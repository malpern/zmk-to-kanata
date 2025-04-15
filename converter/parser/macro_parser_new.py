"""Token-based Macro Parser Module

This module provides a robust, token-based parser for ZMK macro definitions and usages.
It replaces the line-based approach with a token-stream parser that can handle
complex, multi-line macro definitions and nested structures.
"""

import logging
from typing import Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

from converter.parser.zmk_lexer import Token, TokenType, SourceLocation
from converter.parser.zmk_ast import ZMKMacroDefinition, ZMKMacroStep, ZMKDocument, ZMKBinding, ZMKMacrosBlock
from converter.error_handling.error_manager import get_error_manager, ErrorSeverity


logger = logging.getLogger(__name__)


# Define known macro commands and their expected parameter counts
# This helps with validation during parsing
MACRO_COMMANDS = {
    # Command name: (min_params, max_params)
    "kp": (1, 1),                   # &kp KEY
    "macro_tap": (0, 0),            # &macro_tap (begins tap section)
    "macro_press": (0, 0),          # &macro_press (begins press section)
    "macro_release": (0, 0),        # &macro_release (begins release section)
    "macro_wait_time": (1, 1),      # &macro_wait_time MS
    "macro_tap_time": (1, 1),       # &macro_tap_time MS
}


class MacroParserState(Enum):
    """Enum for tracking the state of the macro parser."""
    INITIAL = auto()
    IN_MACROS_BLOCK = auto()
    IN_MACRO_DEFINITION = auto()
    IN_BINDINGS_LIST = auto()
    IN_PARAMS = auto()


class MacroUsageParserState(Enum):
    """
    Enum for tracking the state of macro usage parsing.
    """
    INITIAL = auto()
    IN_MACRO_USAGE = auto()
    IN_PARAMS = auto()


class ZMKMacroKeyActionType(Enum):
    """Enum for macro key action types."""
    TAP = auto()
    PRESS = auto()
    RELEASE = auto()


@dataclass
class MacroDefinition:
    """Represents a complete macro definition with name, steps, and metadata."""
    name: str
    steps: List['MacroStep'] = field(default_factory=list)
    label: Optional[str] = None
    compatible: Optional[str] = None
    binding_cells: int = 0
    location: Optional[SourceLocation] = None
    
    def to_ast(self) -> ZMKMacroDefinition:
        """Convert to AST representation for integration with the rest of the pipeline."""
        ast_macro = ZMKMacroDefinition(self.name)
        ast_macro.label = self.label
        ast_macro.compatible = self.compatible
        
        # Convert steps to AST format
        for step in self.steps:
            ast_step = ZMKMacroStep(step.command, str(step.params) if step.params else None)
            ast_macro.steps.append(ast_step)
        
        return ast_macro
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate that the macro definition is complete and consistent.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check for empty name
        if not self.name:
            errors.append("Macro name cannot be empty")
        
        # Check for empty steps list
        if not self.steps:
            errors.append(f"Macro '{self.name}' has no steps")
        
        # Validate each step
        for i, step in enumerate(self.steps):
            step_valid, step_errors = step.validate()
            if not step_valid:
                for error in step_errors:
                    errors.append(f"Step {i+1}: {error}")
        
        return len(errors) == 0, errors


@dataclass
class MacroStep:
    """
    Represents a step within a macro definition.
    A step consists of a command (&kp, &macro_tap, etc.) with optional parameters.
    """
    # Known macro commands and their expected parameter counts (None means variable number)
    KNOWN_COMMANDS = {
        'kp': 1,           # Key press, e.g., &kp X
        'macro_press': 1,  # Press and hold, e.g., &macro_press LSHIFT
        'macro_release': 1, # Release a held key, e.g., &macro_release LSHIFT
        'macro_tap': 1,    # Tap a key, e.g., &macro_tap X
        'macro_wait_time': 1, # Wait for milliseconds, e.g., &macro_wait_time 50
        'macro_pause_for_release': 0, # Pauses macro until triggering key is released
        'to': None,        # Variable params, e.g., &to 1
    }
    
    def __init__(self, command: str, params: List[str], location: Optional[SourceLocation] = None):
        self.command = command
        self.params = params
        self.location = location
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate this macro step against known commands and parameter counts.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Check if command is known
        if self.command not in self.KNOWN_COMMANDS:
            errors.append(f"Unknown macro command: '{self.command}'")
            return False, errors
        
        # Check parameter count
        expected_param_count = self.KNOWN_COMMANDS[self.command]
        if expected_param_count is not None and len(self.params) != expected_param_count:
            errors.append(f"Command '{self.command}' expects {expected_param_count} parameter(s), but got {len(self.params)}")
        
        return len(errors) == 0, errors

    def __str__(self) -> str:
        params_str = ", ".join(self.params) if self.params else ""
        return f"&{self.command} {params_str}"

    def __repr__(self) -> str:
        return f"MacroStep(command='{self.command}', params={self.params})"


@dataclass
class MacroUsage:
    """Represents a macro usage/reference in a binding."""
    name: str  # Reference to the macro by name
    params: Optional[List[str]] = None  # Optional parameters for parameterized macros
    location: Optional[SourceLocation] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.params is None:
            self.params = []
    
    def validate(self, known_macros: Set[str]) -> Tuple[bool, List[str]]:
        """
        Validate that the macro usage references a known macro and has valid parameters.
        
        Args:
            known_macros: Set of known macro names
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if the macro exists
        if self.name not in known_macros:
            errors.append(f"Referenced macro '{self.name}' is not defined")
        
        # TODO: Add parameter validation when we have macro parameter definitions
        
        return len(errors) == 0, errors


class ZMKMacroParser:
    """
    Token-based parser for ZMK macro definitions and usages.
    
    This parser processes a token stream (rather than lines) to robustly handle
    macro definitions and usages, including complex nested structures and
    multi-line definitions.
    """
    
    def __init__(self):
        """Initialize the parser with empty state."""
        self.state = MacroParserState.INITIAL
        self.current_macro: Optional[MacroDefinition] = None
        self.macros: Dict[str, MacroDefinition] = {}
        self.tokens: List[Token] = []
        self.position = 0
        self.error_manager = get_error_manager()
        
        # Set up for recovery after errors
        self.recovery_tokens = {
            TokenType.SEMICOLON,
            TokenType.CLOSE_BRACE,
            TokenType.CLOSE_ANGLE
        }
    
    def parse_macros_block(self) -> Dict[str, MacroDefinition]:
        """
        Parse the entire macros section in a ZMK config file.
        Expected format:
        
        macros {
            <macro_definition_1>
            <macro_definition_2>
            ...
        };
        
        Returns a dictionary mapping macro names to their MacroDefinition objects.
        """
        # Expect 'macros' keyword
        if not self._match(TokenType.IDENTIFIER) or self._previous().value != 'macros':
            logger.error(f"Expected 'macros' keyword to start macros block, got {self._peek().type}")
            return {}
            
        # Expect opening brace
        if not self._match(TokenType.LEFT_BRACE):
            logger.error(f"Expected '{{' after 'macros' keyword, got {self._peek().type}")
            return {}
            
        # Parse all macro definitions
        macros = {}
        
        # Continue parsing macro definitions until we reach the closing brace
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            # Parse a single macro definition
            macro_name, macro_def = self.parse_macro_definition()
            
            if macro_name and macro_def:
                # Check for duplicate macro names
                if macro_name in macros:
                    logger.warning(f"Duplicate macro name '{macro_name}'. Previous definition will be overwritten.")
                
                macros[macro_name] = macro_def
            else:
                # Error recovery: skip tokens until we find a semicolon or right brace
                self._error_recovery()
                
        # Expect closing brace
        if not self._match(TokenType.RIGHT_BRACE):
            logger.error(f"Expected '}}' at end of macros block, got {self._peek().type}")
            return macros
            
        # Expect semicolon after closing brace
        if not self._match(TokenType.SEMICOLON):
            logger.warning(f"Expected ';' after macros block, got {self._peek().type}")
            
        return macros
    
    def parse_macro_definition(self) -> Optional[MacroDefinition]:
        """
        Parse a macro definition of the form:
        macro_name = <step1>, <step2>, ...;
        OR
        macro_name { <step1>; <step2>; ... };
        
        Returns a MacroDefinition object if successful, None otherwise.
        """
        # Expect a macro name (identifier)
        if not self._match(TokenType.IDENTIFIER):
            self._add_error("Expected macro name (identifier)", ErrorSeverity.ERROR)
            return None
            
        macro_name = self._previous().text
        
        # Check for either '=' or '{'
        if not (self._check(TokenType.EQUAL) or self._check(TokenType.LEFT_BRACE)):
            self._add_error(f"Expected '=' or '{{' after macro name '{macro_name}'", ErrorSeverity.ERROR)
            return None
            
        # Create a new macro definition
        macro_def = MacroDefinition(macro_name)
        
        # Handle the two different syntax forms
        if self._match(TokenType.EQUAL):
            # Form: macro_name = step1, step2, ...;
            steps = self._parse_comma_separated_steps()
            if not steps:
                self._add_error(f"Empty macro definition for '{macro_name}'", ErrorSeverity.WARNING)
            else:
                for step in steps:
                    macro_def.add_step(step)
                    
            # Expect semicolon
            if not self._match(TokenType.SEMICOLON):
                self._add_error(f"Expected ';' after macro definition for '{macro_name}'", ErrorSeverity.ERROR)
                
        elif self._match(TokenType.LEFT_BRACE):
            # Form: macro_name { step1; step2; ... };
            steps = self._parse_semicolon_separated_steps()
            if not steps:
                self._add_error(f"Empty macro definition for '{macro_name}'", ErrorSeverity.WARNING)
            else:
                for step in steps:
                    macro_def.add_step(step)
                    
            # Expect closing brace
            if not self._match(TokenType.RIGHT_BRACE):
                self._add_error(f"Expected '}}' to close macro definition for '{macro_name}'", ErrorSeverity.ERROR)
                
            # Expect semicolon after closing brace
            if not self._match(TokenType.SEMICOLON):
                self._add_error(f"Expected ';' after macro definition for '{macro_name}'", ErrorSeverity.ERROR)
        
        return macro_def
    
    def _synchronize_to_macro_end(self):
        """
        Advance tokens until a right brace is found or end of file.
        Used for error recovery when parsing macro definitions.
        """
        while not self._is_at_end():
            if self._match(TokenType.RIGHT_BRACE):
                return
            self._advance()
    
    def parse_macro_steps(self) -> List[MacroStep]:
        """
        Parse the sequence of macro steps inside a macro definition.
        
        Returns:
            List of MacroStep objects
        """
        steps = []
        
        # Parse macro steps until we hit a closing brace
        while not self._check(TokenType.CLOSING_BRACE) and not self._is_at_end():
            # Parse a binding or wait command
            if self._check(TokenType.LESS_THAN):
                # This is a wait command: <wait-ms>X</wait-ms>
                wait_step = self.parse_wait_step()
                if wait_step:
                    steps.append(wait_step)
            else:
                # This is a key binding
                binding = self.parse_binding()
                if binding:
                    steps.append(MacroStep(binding=binding))
                else:
                    # If we failed to parse a binding, skip to the next valid token
                    self._synchronize_to_next_step()
                    continue
            
            # Expect a comma or semicolon after each step
            if self._match([TokenType.COMMA, TokenType.SEMICOLON]):
                # Skip the separator and continue
                pass
            elif not self._check(TokenType.CLOSING_BRACE):
                # If there's no separator and we're not at the end, report an error
                self._add_error("Expected ',' or ';' after macro step", ErrorSeverity.ERROR)
                # Skip the current token and continue
                self._advance()
        
        return steps
    
    def parse_wait_step(self) -> Optional[MacroStep]:
        """
        Parse a wait step in a macro.
        Format: <wait-ms>X</wait-ms> where X is an integer.
        
        Returns:
            MacroStep with wait_ms set, or None if parsing fails
        """
        # Record the starting position for error reporting
        start_position = self._current_position()
        
        # Expect opening tag
        if not self._consume(TokenType.LESS_THAN, "Expected '<' to start wait tag"):
            return None
        
        # Expect wait-ms identifier
        if not self._consume(TokenType.IDENTIFIER, "Expected 'wait-ms' after '<'"):
            return None
        
        wait_tag = self._previous_token()
        if wait_tag.value != 'wait-ms':
            self._add_error(f"Expected 'wait-ms' but got '{wait_tag.value}'", ErrorSeverity.ERROR)
            return None
        
        # Expect closing angle bracket
        if not self._consume(TokenType.GREATER_THAN, "Expected '>' after 'wait-ms'"):
            return None
        
        # Expect an integer for ms value
        if not self._consume(TokenType.INTEGER, "Expected integer for wait duration"):
            return None
        
        wait_ms = int(self._previous_token().value)
        
        # Expect opening tag for closing wait-ms
        if not self._consume(TokenType.LESS_THAN, "Expected '<' to start closing wait tag"):
            # Return what we have even with error
            return MacroStep(wait_ms=wait_ms)
        
        # Expect slash
        if not self._consume(TokenType.FORWARD_SLASH, "Expected '/' after '<' in closing wait tag"):
            # Return what we have even with error
            return MacroStep(wait_ms=wait_ms)
        
        # Expect wait-ms identifier
        if not self._consume(TokenType.IDENTIFIER, "Expected 'wait-ms' after '</' in closing wait tag"):
            # Return what we have even with error
            return MacroStep(wait_ms=wait_ms)
        
        close_wait_tag = self._previous_token()
        if close_wait_tag.value != 'wait-ms':
            self._add_error(f"Expected 'wait-ms' but got '{close_wait_tag.value}'", ErrorSeverity.ERROR)
            # Return what we have even with error
            return MacroStep(wait_ms=wait_ms)
        
        # Expect closing angle bracket
        if not self._consume(TokenType.GREATER_THAN, "Expected '>' to end closing wait tag"):
            # Return what we have even with error
            return MacroStep(wait_ms=wait_ms)
        
        return MacroStep(wait_ms=wait_ms)
    
    def extract_parameters(self, tokens: List[Token]) -> List[str]:
        """
        Extract parameters for a macro usage from a list of tokens.
        Handles identifiers, numbers, and strings robustly.

        Args:
            tokens: List of tokens representing the macro usage (excluding the macro name)
        Returns:
            List of parameter values as strings
        """
        params = []
        for token in tokens:
            if token.type in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING):
                params.append(token.value)
        return params

    def parse_macro_usage(self, tokens: List[Token], known_macros: Optional[Set[str]] = None) -> Optional[MacroUsage]:
        """
        Parse a macro usage/reference from a token stream, with state management and validation.

        Args:
            tokens: List of tokens representing the macro usage
            known_macros: Optional set of known macro names for validation
        Returns:
            MacroUsage if successful, None if parsing failed
        """
        if not tokens:
            self._add_error("Empty token list for macro usage", ErrorSeverity.ERROR)
            return None
        self._transition_usage_state(MacroUsageParserState.INITIAL)
        macro_name = None
        param_tokens = []
        location = tokens[0].location if tokens else None
        for i, token in enumerate(tokens):
            if self.usage_state == MacroUsageParserState.INITIAL:
                if token.type == TokenType.IDENTIFIER:
                    macro_name = token.value
                    self._transition_usage_state(MacroUsageParserState.IN_MACRO_USAGE)
            elif self.usage_state == MacroUsageParserState.IN_MACRO_USAGE:
                if token.type in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING):
                    param_tokens.append(token)
                    self._transition_usage_state(MacroUsageParserState.IN_PARAMS)
            elif self.usage_state == MacroUsageParserState.IN_PARAMS:
                if token.type in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING):
                    param_tokens.append(token)
                elif token.type in (TokenType.SEMICOLON, TokenType.COMMA, TokenType.RIGHT_BRACE):
                    self._transition_usage_state(MacroUsageParserState.INITIAL)
                    break
        if macro_name is None:
            self._add_error("No macro name found in macro usage", ErrorSeverity.ERROR, location)
            return None
        params = self.extract_parameters(param_tokens)
        usage = MacroUsage(name=macro_name, params=params, location=location)
        # Validation: check macro existence and parameter count if possible
        if known_macros is not None:
            valid, errors = usage.validate(known_macros)
            for err in errors:
                self._add_error(err, ErrorSeverity.ERROR, location)
            if not valid:
                return None
        self._transition_usage_state(MacroUsageParserState.INITIAL)
        return usage
    
    def validate_all_macros(self) -> bool:
        """
        Validate all parsed macro definitions.
        
        Returns:
            True if all macros are valid, False otherwise
        """
        all_valid = True
        
        for name, macro in self.macros.items():
            valid, errors = macro.validate()
            if not valid:
                all_valid = False
                for error in errors:
                    self._add_error(
                        f"Macro '{name}' validation error: {error}",
                        ErrorSeverity.ERROR,
                        macro.location
                    )
        
        return all_valid
    
    def _recover_from_error(self):
        """
        Skip tokens until a statement boundary to recover from an error.
        This helps continue parsing even after encountering errors.
        """
        self._synchronize_to_semicolon()
    
    def _peek(self, offset: int = 0) -> Token:
        """Peek at a token ahead in the stream."""
        if self.position + offset >= len(self.tokens):
            # Return EOF token if we're at the end
            return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", None)
        return self.tokens[self.position + offset]
    
    def _consume(self, expected_type: TokenType, error_message: str) -> Token:
        """Consume the current token and advance."""
        if self.position >= len(self.tokens):
            self._add_error(error_message, ErrorSeverity.ERROR)
            # Return EOF token
            return Token(TokenType.EOF, "", None)
        
        token = self.tokens[self.position]
        if token.type != expected_type:
            self._add_error(error_message, ErrorSeverity.ERROR, token.location)
            # Return EOF token
            return Token(TokenType.EOF, "", None)
        
        self.position += 1
        return token
    
    def _match(self, token_type: TokenType, expected_value: Optional[str] = None) -> Optional[Token]:
        """Match the current token against the expected type and value."""
        token = self._peek()
        if token.type != token_type:
            self._add_error(
                f"Expected {token_type.name}, got {token.type.name}",
                ErrorSeverity.ERROR,
                token.location
            )
            return None
        if expected_value and token.value != expected_value:
            self._add_error(
                f"Expected '{expected_value}', got '{token.value}'",
                ErrorSeverity.ERROR,
                token.location
            )
            return None
        return self._consume(token_type, f"Expected {token_type.name}")
    
    def _try_match(self, token_type: TokenType) -> Optional[Token]:
        """Try to match the current token against the expected type."""
        token = self._peek()
        if token.type != token_type:
            return None
        return self._consume(token.type, f"Expected {token.type.name}")
    
    def _match_any(self, token_types: List[TokenType]) -> Optional[Token]:
        """Match the current token against any of the expected types."""
        token = self._peek()
        if token.type not in token_types:
            expected = ", ".join(t.name for t in token_types)
            self._add_error(
                f"Expected one of {expected}, got {token.type.name}",
                ErrorSeverity.ERROR,
                token.location
            )
            return None
        return self._consume(token.type, f"Expected one of {', '.join(t.name for t in token_types)}")
    
    def _add_error(self, message, severity=ErrorSeverity.ERROR, location=None):
        """
        Add an error to the error manager.
        Args:
            message: The error message
            severity: Error severity (ERROR, WARNING, INFO)
            location: Source location for the error (optional, can be None)
        """
        line_number = getattr(location, 'line', None) if location else None
        column = getattr(location, 'column', None) if location else None
        get_error_manager().add_error(
            message=message,
            severity=severity,
            source="macro_parser",
            line_number=line_number,
            column=column
        )
    
    def _transition_to(self, new_state: MacroParserState):
        """Transition to a new parser state."""
        old_state = self.state
        self.state = new_state
        logger.debug(f"State transition: {old_state.name} -> {new_state.name}")
    
    def log_parse_summary(self):
        """Log a summary of the parsing results."""
        logger.info(f"Parsing complete. Found {len(self.macros)} macro definitions.")
        for name, macro in self.macros.items():
            logger.info(f"  - Macro '{name}': {len(macro.steps)} steps")
    
    def _process_macro_steps(self) -> List[MacroStep]:
        """
        Process all steps in a macro definition until we encounter a closing brace.
        This method parses multiple macro steps, handles commas between steps,
        and returns a list of MacroStep objects.
        
        Returns:
            List[MacroStep]: A list of parsed macro steps
        """
        steps = []
        
        # Continue until we find a closing brace, semicolon, or EOF
        while (not self._check(TokenType.RIGHT_BRACE) and 
               not self._check(TokenType.SEMICOLON) and 
               not self._is_at_end()):
            
            # Parse a single macro step
            step = self._parse_macro_step()
            if step:
                steps.append(step)
            else:
                # Error already reported in _parse_macro_step
                # Synchronize to the next step or end of macro definition
                self._synchronize_to_next_step()
                continue
            
            # Check for a comma between steps (required except before closing brace)
            if (not self._check(TokenType.RIGHT_BRACE) and 
                not self._check(TokenType.SEMICOLON)):
                if not self._match(TokenType.COMMA):
                    self._add_error("Expected ',' between macro steps", ErrorSeverity.ERROR)
                    # Try to recover by synchronizing to the next step
                    self._synchronize_to_next_step()
        
        return steps

    def _parse_macro_step(self) -> Optional[MacroStep]:
        """
        Parse a single macro step, which can be one of:
        - wait-ms: time delay in milliseconds
        - tap: key press followed by immediate release
        - press: key press without release
        - release: key release without preceding press
        
        Returns:
            Optional[MacroStep]: A MacroStep object if parsing succeeds, None otherwise
        """
        # Handle wait-ms step
        if self._match(TokenType.IDENTIFIER) and self._previous().text.lower() == "wait-ms":
            return self._parse_wait_ms_step()
            
        # Handle tap step
        elif self._match(TokenType.IDENTIFIER) and self._previous().text.lower() == "tap":
            return self._parse_key_action_step("tap")
            
        # Handle press step
        elif self._match(TokenType.IDENTIFIER) and self._previous().text.lower() == "press":
            return self._parse_key_action_step("press")
            
        # Handle release step
        elif self._match(TokenType.IDENTIFIER) and self._previous().text.lower() == "release":
            return self._parse_key_action_step("release")
            
        # Unknown step type
        elif self._match(TokenType.IDENTIFIER):
            self._add_error(f"Unknown macro step type: '{self._previous().text}'", ErrorSeverity.ERROR)
            return None
            
        # Not a valid step beginning
        else:
            self._add_error("Expected a macro step (wait-ms, tap, press, or release)", ErrorSeverity.ERROR)
            return None
            
    def _synchronize_to_next_step(self):
        """
        Skip tokens until we find a comma, closing brace, or semicolon.
        This helps recover from errors by finding the start of the next step.
        """
        while (not self._is_at_end() and 
               not self._check(TokenType.COMMA) and 
               not self._check(TokenType.RIGHT_BRACE) and 
               not self._check(TokenType.SEMICOLON)):
            self._advance()
            
    def _parse_wait_ms_step(self) -> Optional[MacroStep]:
        """
        Parse a wait-ms step, which specifies a time delay in milliseconds.
        Format: wait-ms <integer>
        
        Returns:
            Optional[MacroStep]: A MacroStep object if parsing succeeds, None otherwise
        """
        # Expect an integer value for milliseconds
        if not self._match(TokenType.INTEGER):
            self._add_error("Expected integer value after 'wait-ms'", ErrorSeverity.ERROR)
            return None
            
        # Get the milliseconds value
        ms_value = int(self._previous().text)
        
        # Create and return a MacroStep for wait-ms
        return MacroStep(step_type="wait-ms", params={"ms": ms_value})
        
    def _parse_key_action_step(self, action_type: str) -> Optional[MacroStep]:
        """
        Parse a key action step (tap, press, or release).
        Format: <action_type> <key>
        
        Args:
            action_type: The type of key action ("tap", "press", or "release")
            
        Returns:
            Optional[MacroStep]: A MacroStep object if parsing succeeds, None otherwise
        """
        # Expect a key code
        if not self._match(TokenType.IDENTIFIER):
            self._add_error(f"Expected key code after '{action_type}'", ErrorSeverity.ERROR)
            return None
            
        # Get the key code
        key_code = self._previous().text
        
        # Create and return a MacroStep for the key action
        return MacroStep(step_type=action_type, params={"key": key_code})

    def parse_key_action_type(self) -> Optional[ZMKMacroKeyActionType]:
        """
        Parse a key action type: &kp, &down, or &up
        
        Returns:
            ZMKMacroKeyActionType enum value if successful, None otherwise
        """
        if not self._consume(TokenType.AMPERSAND, "Expected '&' at start of key action"):
            return None
        
        if not self._consume(TokenType.IDENTIFIER, "Expected key action type after '&'"):
            return None
        
        action_type_str = self._previous_token().value.lower()
        
        if action_type_str == "kp":
            return ZMKMacroKeyActionType.TAP
        elif action_type_str == "down":
            return ZMKMacroKeyActionType.PRESS
        elif action_type_str == "up":
            return ZMKMacroKeyActionType.RELEASE
        else:
            self._add_error(f"Invalid key action type: '{action_type_str}'. Expected 'kp', 'down', or 'up'", ErrorSeverity.ERROR)
            return None
    
    def parse_wait_time(self) -> Optional[int]:
        """
        Parse a wait time value
        
        Returns:
            Integer wait time in milliseconds if successful, None otherwise
        """
        if not self._consume(TokenType.NUMBER, "Expected number for wait time"):
            return None
        
        try:
            wait_ms = int(self._previous_token().value)
            
            if wait_ms < 0:
                self._add_error(f"Wait time must be non-negative, got {wait_ms}", ErrorSeverity.ERROR)
                return None
            
            return wait_ms
        except ValueError:
            self._add_error(f"Invalid number format for wait time: '{self._previous_token().value}'", ErrorSeverity.ERROR)
            return None

    def parse_macro_block(self) -> Optional[ZMKMacrosBlock]:
        """
        Parse an entire macros block with multiple macro definitions.
        
        Returns a ZMKMacrosBlock object containing all parsed macro definitions.
        """
        # Ensure we're at the start of a macros block
        if not self._check(TokenType.IDENTIFIER) or self._peek().text != "macros":
            return None
            
        self._advance()  # consume 'macros'
        
        # Expect opening brace
        if not self._match(TokenType.LEFT_BRACE):
            self._add_error("Expected '{' after 'macros'", ErrorSeverity.ERROR)
            return None
            
        macros_block = ZMKMacrosBlock()
        
        # Parse macro definitions until we reach the closing brace
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            # Parse a macro definition
            macro_def = self.parse_macro_definition()
            
            if macro_def:
                # Add the macro definition to the block
                macros_block.add_definition(macro_def)
            else:
                # If parsing the definition failed, skip to the next semicolon or brace
                self._synchronize([TokenType.SEMICOLON, TokenType.RIGHT_BRACE])
                
        # Expect closing brace
        if not self._match(TokenType.RIGHT_BRACE):
            self._add_error("Expected '}' to close macros block", ErrorSeverity.ERROR)
            # Continue anyway to return what we've parsed
            
        return macros_block

    def _synchronize_to_next_macro(self):
        """
        Advance tokens until we find a semicolon (end of current macro)
        or an identifier at the start of a line (potential start of next macro).
        Used for error recovery when parsing macro definitions.
        """
        while not self._is_at_end():
            # If we see a semicolon, we're at the end of a macro definition
            if self._match(TokenType.SEMICOLON):
                return
                
            # If we're at the start of a new line and see an identifier,
            # it might be the start of a new macro definition
            current_token = self._peek()
            if (current_token.column == 0 or current_token.column == 1) and current_token.type == TokenType.IDENTIFIER:
                return
                
            # If we see a closing brace, we're at the end of the macros block
            if self._check(TokenType.RIGHT_BRACE):
                return
                
            self._advance() 

    def _parse_wait_step(self) -> Optional[MacroStep]:
        """
        Parse a wait step in a macro definition, which has the format: wait <milliseconds>
        
        Returns a MacroStep object if successful, None otherwise.
        """
        # Expect a number for milliseconds
        if not self._match(TokenType.NUMBER):
            self._add_error("Expected number of milliseconds after 'wait'", ErrorSeverity.ERROR)
            return None
            
        try:
            ms_value = int(self._previous().text)
            if ms_value < 0:
                self._add_error(f"Wait time cannot be negative: {ms_value}", ErrorSeverity.ERROR)
                return None
                
            return MacroStep(MacroStepType.WAIT, str(ms_value))
        except ValueError:
            self._add_error(f"Invalid millisecond value: {self._previous().text}", ErrorSeverity.ERROR)
            return None 

    def _parse_comma_separated_steps(self) -> List[MacroStep]:
        """
        Parse macro steps separated by commas.
        macro_name = step1, step2, ..., stepN;
        """
        steps = []
        
        # Parse first step
        step = self._parse_macro_step()
        if step:
            steps.append(step)
        else:
            return steps  # Return empty list if no valid first step
            
        # Parse additional steps separated by commas
        while self._match(TokenType.COMMA):
            step = self._parse_macro_step()
            if step:
                steps.append(step)
            else:
                self._add_error("Expected valid macro step after ','", ErrorSeverity.ERROR)
                # Continue parsing to recover from error
        
        return steps
        
    def _parse_semicolon_separated_steps(self) -> List[MacroStep]:
        """
        Parse macro steps separated by semicolons.
        macro_name { step1; step2; ...; stepN }
        """
        steps = []
        
        # Continue parsing steps until we reach the closing brace
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            step = self._parse_macro_step()
            if step:
                steps.append(step)
            else:
                # Error already reported in _parse_macro_step
                # Synchronize to next step to recover from error
                self._synchronize_to_next_step()
                continue
                
            # Expect semicolon after each step except the last one
            if not self._match(TokenType.SEMICOLON):
                if not self._check(TokenType.RIGHT_BRACE):
                    self._add_error("Expected ';' after macro step", ErrorSeverity.ERROR)
                    self._synchronize_to_next_step()
        
        return steps
        
    def _synchronize_to_next_step(self):
        """
        Skip tokens until we reach a token that could start a new macro step
        or a token that would end the current macro definition.
        """
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
                
            if self._peek().type in [TokenType.RIGHT_BRACE, TokenType.SEMICOLON]:
                return
                
            self._advance()
            
    def _parse_macro_step(self) -> Optional[MacroStep]:
        """
        Parse a single macro step, which can be either:
        - A binding behavior (tap, press, release)
        - A timing parameter (wait-ms, tap-ms, press-ms, release-ms)
        
        Returns a MacroStep object or None on error.
        """
        if self._is_at_end():
            self._add_error("Unexpected end of input while parsing macro step", ErrorSeverity.ERROR)
            return None
            
        # Check the type of macro step
        token = self._peek()
        
        # Binding behaviors
        if token.text in ["tap", "press", "release"]:
            return self._parse_binding_step()
            
        # Timing parameters
        elif token.text in ["wait-ms", "tap-ms", "press-ms", "release-ms"]:
            return self._parse_timing_step()
            
        else:
            self._add_error(f"Unknown macro step: {token.text}", ErrorSeverity.ERROR)
            return None

    def _parse_binding_step(self) -> Optional[MacroStep]:
        """
        Parse a binding step like: tap KEY, press KEY, or release KEY.
        Returns a MacroStep with the appropriate action and key.
        """
        # Get the action type (tap, press, or release)
        action = self._advance().text
        
        # Expect a key name after the action
        if not self._check(TokenType.IDENTIFIER) and not self._check(TokenType.STRING):
            self._add_error(f"Expected key name after '{action}'", ErrorSeverity.ERROR)
            return None
            
        # Parse the key
        key = self._advance().text
        
        # Create and return the macro step
        return MacroStep(action=action, key=key)
        
    def _parse_timing_step(self) -> Optional[MacroStep]:
        """
        Parse a timing step like: wait-ms N, tap-ms N, press-ms N, or release-ms N.
        Returns a MacroStep with the appropriate timing parameter and value.
        """
        # Get the timing parameter type
        timing_type = self._advance().text
        
        # Expect a numeric value after the timing parameter
        if not self._check(TokenType.NUMBER):
            self._add_error(f"Expected numeric value after '{timing_type}'", ErrorSeverity.ERROR)
            return None
            
        # Parse the numeric value
        try:
            value = int(self._advance().text)
            if value < 0:
                self._add_error(f"Timing value must be non-negative, got {value}", ErrorSeverity.ERROR)
                return None
        except ValueError:
            self._add_error(f"Invalid numeric value for '{timing_type}'", ErrorSeverity.ERROR)
            return None
            
        # Create and return the macro step
        return MacroStep(action=timing_type, value=value) 

    def _transition_usage_state(self, new_state):
        """
        Transition the macro usage parser state to a new state.
        Args:
            new_state: The new MacroUsageParserState value
        """
        old_state = getattr(self, 'usage_state', None)
        self.usage_state = new_state
        logger.debug(f"Macro usage state transition: {old_state} -> {new_state}") 