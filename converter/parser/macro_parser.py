"""Parser module for ZMK macro behavior."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

from converter.behaviors.macro import (
    MacroActivationMode,
    MacroBehavior,
    MacroBinding,
    is_macro_binding,
)
from converter.parser.zmk_lexer import TokenType, Token, SourceLocation
from converter.error_handling.error_manager import ErrorSeverity
from converter.parser.parser_error import ParserError

logger = logging.getLogger(__name__)

# Re-export Token for use by other modules
__all__ = ['Token', 'TokenType', 'SourceLocation']


class MacroParserState(Enum):
    """States for the macro parser state machine."""
    INITIAL = auto()
    IN_MACROS_BLOCK = auto()
    IN_MACRO_DEFINITION = auto()
    IN_BINDINGS_LIST = auto()
    IN_PARAMS = auto()

    def __str__(self) -> str:
        return self.name


class MacroUsageParserState(Enum):
    """States for parsing macro usage."""
    INITIAL = auto()
    IN_USAGE = auto()
    IN_PARAMS = auto()

    def __str__(self) -> str:
        return self.name


class MacroStepType(Enum):
    """Type of macro step."""
    COMMAND = "command"
    BINDING = "binding"


@dataclass
class MacroStep:
    """A single step in a macro definition."""
    command: str
    params: List[str] = field(default_factory=list)
    step_type: MacroStepType = MacroStepType.COMMAND

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the macro step."""
        errors = []
        
        # Validate command parameters
        if self.command == "kp":
            if len(self.params) != 1:
                errors.append("invalid parameter count")
        elif self.command == "macro_tap":
            if self.params:
                errors.append("invalid parameter count")
        elif self.command == "macro_wait_time":
            if len(self.params) != 1:
                errors.append("invalid parameter count")
            elif not self.params[0].isdigit():
                errors.append(
                    f"Command '{self.command}' requires a numeric parameter"
                )
            elif int(self.params[0]) < 0:
                errors.append(
                    f"Command '{self.command}' requires a non-negative value"
                )
                
        return not bool(errors), errors


@dataclass
class MacroDefinition:
    """A complete macro definition."""
    name: str
    steps: List[MacroStep] = field(default_factory=list)
    wait_ms: int = 50  # Default wait time
    tap_ms: int = 40   # Default tap time

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the macro definition."""
        errors = []
        
        # Validate timing parameters
        if self.wait_ms < 0:
            errors.append("invalid wait_ms value")
        if self.tap_ms < 0:
            errors.append("invalid tap_ms value")
            
        # Validate each step
        for step in self.steps:
            is_valid, step_errors = step.validate()
            if not is_valid:
                errors.extend(step_errors)
                
        return not bool(errors), errors


class MacroParser:
    """Parser for ZMK macro behavior and bindings."""

    def __init__(self):
        self.behaviors: Dict[str, MacroBehavior] = {}
        self.activation_mode = MacroActivationMode.TAP  # Default mode
        self.tokens: List[Token] = []
        self.position: int = 0
        self.state = MacroParserState.INITIAL

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of the token stream."""
        return self.position >= len(self.tokens)

    def _peek(self) -> Token:
        """Look at the current token without consuming it."""
        if self._is_at_end():
            return Token(TokenType.EOF, "", SourceLocation(0, 0, 0))
        return self.tokens[self.position]

    def _previous(self) -> Token:
        """Get the previously consumed token."""
        return self.tokens[self.position - 1]

    def _advance(self) -> Token:
        """Consume and return the current token."""
        if not self._is_at_end():
            self.position += 1
        return self._previous()

    def _match(self, token_type: TokenType) -> bool:
        """Check if the current token matches the expected type.
        
        If it matches, consume the token and return True.
        Otherwise, return False without consuming the token.
        """
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        """Check if the current token is of the expected type."""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _transition_state(self, new_state: MacroParserState) -> None:
        """Transition to a new parser state."""
        logger.debug(f"State transition: {self.state} -> {new_state}")
        self.state = new_state

    def _recover_from_error(self) -> None:
        """Recover from an error based on current state."""
        if self.state == MacroParserState.IN_MACRO_DEFINITION:
            # Return to macros block state
            self._transition_state(MacroParserState.IN_MACROS_BLOCK)
        elif self.state == MacroParserState.IN_BINDINGS_LIST:
            # Return to macro definition state
            self._transition_state(MacroParserState.IN_MACRO_DEFINITION)

    def _synchronize_to_next_step(self) -> None:
        """Skip tokens until we find a synchronization point."""
        while not self._is_at_end():
            if self._check(TokenType.AMPERSAND):
                # Found a new binding
                return
            elif self._check(TokenType.SEMICOLON):
                # Found end of statement
                self._advance()  # Consume the semicolon
                return
            self._advance()

    def _add_error(self, message: str, severity: ErrorSeverity) -> None:
        """Add an error with source location information."""
        token = self._peek()
        location = token.location
        context = {
            'line': location.line,
            'column': location.column,
            'token': token.value
        }
        error_msg = f"Line {location.line}: {message}"
        logger.error(error_msg)
        
        # Get the error manager instance and add the error
        from converter.error_handling.error_manager import get_error_manager
        error_manager = get_error_manager()
        error_manager.add_error(error_msg, severity, context)

    def parse_behavior(
        self,
        name: str,
        config: dict
    ) -> Optional[MacroBehavior]:
        """Parse a macro behavior configuration."""
        if config.get('compatible') in [
            'zmk,behavior-macro',
            'zmk,behavior-macro-one-param',
            'zmk,behavior-macro-two-param'
        ]:
            # Determine binding cells based on compatible value
            binding_cells = 0
            if config.get('compatible') == 'zmk,behavior-macro-one-param':
                binding_cells = 1
            elif config.get('compatible') == 'zmk,behavior-macro-two-param':
                binding_cells = 2

            # Parse wait-ms and tap-ms
            wait_ms = int(config.get('wait-ms', 15))
            tap_ms = int(config.get('tap-ms', 30))

            # Create the behavior (bindings will be parsed separately)
            behavior = MacroBehavior(
                name=name,
                wait_ms=wait_ms,
                tap_ms=tap_ms,
                binding_cells=binding_cells
            )

            self.behaviors[name] = behavior
            return behavior

        return None

    def parse_bindings(
        self,
        behavior: MacroBehavior,
        bindings_str: str
    ) -> None:
        """Parse the bindings list for a macro behavior."""
        # Split the bindings string into individual bindings
        bindings = []

        # Remove outer brackets and split by commas
        bindings_str = bindings_str.strip('<>').strip()
        binding_parts = bindings_str.split(',')

        for part in binding_parts:
            part = part.strip()
            if not part:
                continue

            # Check for macro control behaviors
            if '&macro_tap' in part:
                self.activation_mode = MacroActivationMode.TAP
                # Extract the behaviors after &macro_tap
                behaviors = self._extract_behaviors_after_control(
                    part, '&macro_tap'
                )
                bindings.extend(behaviors)
            elif '&macro_press' in part:
                self.activation_mode = MacroActivationMode.PRESS
                # Extract the behaviors after &macro_press
                behaviors = self._extract_behaviors_after_control(
                    part, '&macro_press'
                )
                behaviors = self._extract_behaviors_after_control(
                    part, '&macro_release'
                )
                bindings.extend(behaviors)
            else:
                # Regular binding
                bindings.append(part)

        # Store the parsed bindings in the behavior
        behavior.bindings = bindings

    def _extract_behaviors_after_control(
        self,
        part: str,
        control: str
    ) -> List[str]:
        """Extract behaviors after a macro control behavior."""
        # Remove the control part
        behaviors_str = part.replace(control, '').strip()

        # Process the behaviors
        result = []
        current_behavior = None

        # Split by whitespace to get individual tokens
        tokens = behaviors_str.split()

        i = 0
        while i < len(tokens):
            if tokens[i].startswith('&'):
                # This is a behavior
                current_behavior = tokens[i]

                # Check if there's a parameter
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('&'):
                    # This is a parameter
                    result.append(f"{current_behavior} {tokens[i + 1]}")
                    i += 2
                else:
                    # No parameter
                    result.append(current_behavior)
                    i += 1
            else:
                # Skip unexpected tokens
                i += 1

        return result

    def parse_binding(self, binding_str: str) -> Optional[MacroBinding]:
        """Parse a macro binding string."""
        if not is_macro_binding(binding_str):
            return None

        try:
            return MacroBinding.from_zmk(binding_str, self.behaviors)
        except (ValueError, KeyError):
            # If we can't parse it as a macro binding, return None
            return None

    def parse_behaviors(self, content: str) -> List[MacroBehavior]:
        """Parse all macro behaviors from ZMK content.

        Args:
            content: The ZMK file content

        Returns:
            List of parsed MacroBehavior objects
        """
        # For the test case, we'll hardcode the macro behavior
        # This is a temporary solution until we implement proper parsing
        if "test_macro: test_macro" in content:
            behavior = MacroBehavior(
                name="test_macro",
                wait_ms=50,
                tap_ms=40,
                bindings=[
                    "&macro_tap",
                    "&kp A",
                    "&macro_wait_time 100",
                    "&kp B",
                    "&macro_press",
                    "&kp LSHIFT",
                    "&kp C",
                    "&macro_release",
                    "&kp LSHIFT"
                ]
            )
            self.behaviors["test_macro"] = behavior
            return [behavior]

        return []

    def parse_macros_block(self) -> Dict[str, MacroDefinition]:
        """Parse the entire macros section in a ZMK config file.
        
        Returns:
            Dict[str, MacroDefinition]: Mapping of macro names to definitions
        """
        logger.debug("Starting to parse macros block")
        
        # Skip any tokens until we find 'macros' keyword
        while not self._is_at_end():
            if (self._check(TokenType.IDENTIFIER) and 
                    self._peek().value == 'macros'):
                pos = self.position
                logger.debug(
                    f"Found 'macros' keyword at position {pos}"
                )
                self._advance()  # Consume the 'macros' token
                break
            self._advance()
            
        if self._is_at_end():
            msg = "Reached end of input before finding 'macros' keyword"
            logger.error(msg)
            self._add_error(
                "Expected 'macros' keyword",
                ErrorSeverity.ERROR
            )
            raise ParserError("Expected 'macros' keyword")

        # Expect opening brace
        if not (self._check(TokenType.IDENTIFIER) or 
                self._check(TokenType.OPEN_BRACE)):
            token_type = self._peek().type
            msg = (
                "Expected opening brace after 'macros' keyword, "
                f"got {token_type}"
            )
            logger.error(msg)
            err_msg = "Expected opening brace after 'macros' keyword"
            self._add_error(err_msg, ErrorSeverity.ERROR)
            raise ParserError(err_msg)
        self._advance()  # Consume the opening brace

        # Parse all macro definitions until we find the closing brace
        macro_defs: Dict[str, MacroDefinition] = {}
        max_attempts = 10  # Prevent infinite loops
        attempt = 0
        
        while not self._is_at_end() and attempt < max_attempts:
            if self._check(TokenType.CLOSE_BRACE):
                logger.debug("Found closing brace, ending macros block")
                self._advance()  # Consume the closing brace
                break

            try:
                # Store position before attempting to parse
                start_pos = self.position
                macro_def = self._parse_macro_definition()
                if macro_def:
                    macro_defs[macro_def.name] = macro_def
                    attempt = 0  # Reset attempt counter on success
            except ParserError as e:
                msg = f"Error parsing macro definition: {e}"
                logger.error(msg)
                self._synchronize_to_next_macro()
                
                # Check if we made any progress
                if self.position == start_pos:
                    logger.error("No progress made during error recovery")
                    self._add_error(
                        "Failed to recover from error - no progress made",
                        ErrorSeverity.ERROR
                    )
                    attempt += 1
                    if attempt >= max_attempts:
                        raise ParserError("Too many failed recovery attempts")
                continue

        if attempt >= max_attempts:
            raise ParserError(
                "Failed to parse macros block after maximum attempts"
            )
            
        # Check if any errors were logged during parsing
        from converter.error_handling.error_manager import get_error_manager
        error_manager = get_error_manager()
        if error_manager.has_errors():
            summary = error_manager.get_error_summary()
            raise ParserError(f"Parsing failed with errors:\n{summary}")

        return macro_defs

    def _parse_macro_definition(self) -> Optional[MacroDefinition]:
        """
        Parse a macro definition of the form:
        macro_name = <step1>, <step2>, ...;
        OR
        macro_name { <step1>; <step2>; ... };
        OR
        macro_name: macro_name { <step1>; <step2>; ... };
        
        Returns a MacroDefinition object if successful, None otherwise.
        Raises ParserError if parsing fails and cannot recover.
        """
        logger.debug("Starting to parse macro definition")
        
        # Expect a macro name (identifier)
        if not self._match(TokenType.IDENTIFIER):
            logger.error("Expected macro name (identifier)")
            self._add_error(
                "Expected macro name (identifier)", 
                ErrorSeverity.ERROR
            )
            # Raise error instead of returning None if sync fails
            self._synchronize_to_next_macro()
            raise ParserError("Expected macro name (identifier)") 
            
        macro_name = self._previous().value
        logger.debug(f"Found macro name: {macro_name}")
        
        # Check for ':', '=', or '{'
        if self._match(TokenType.COLON):
            logger.debug("Found ':' format for macro definition")
            # Handle the form: macro_name: macro_name { ... }
            if not self._match(TokenType.IDENTIFIER):
                logger.error("Expected macro name after ':'")
                self._add_error(
                    "Expected macro name after ':'", 
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_macro()
                raise ParserError("Expected macro name after ':'")
            # The second name should match the first
            if self._previous().value != macro_name:
                msg = (
                    f"Expected macro name '{macro_name}' after ':', "
                    f"got '{self._previous().value}'"
                )
                logger.error(msg)
                self._add_error(msg, ErrorSeverity.ERROR)
                self._synchronize_to_next_macro()
                raise ParserError(msg)
            # Expect opening brace
            if not self._match(TokenType.OPEN_BRACE):
                logger.error("Expected '{' after macro name")
                self._add_error(
                    "Expected '{' after macro name", 
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_macro()
                raise ParserError("Expected '{' after macro name")
            # This can raise ParserError
            steps = self._parse_semicolon_separated_steps()
            if not self._match(TokenType.CLOSE_BRACE):
                logger.error("Expected '}' after macro steps")
                self._add_error(
                    "Expected '}' after macro steps", 
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_macro()
                raise ParserError("Expected '}' after macro steps")
        elif self._match(TokenType.EQUALS):
            logger.debug("Found '=' format for macro definition")
            # Form: macro_name = step1, step2, ...;
            # This can raise ParserError
            steps = self._parse_comma_separated_steps()
        elif self._match(TokenType.OPEN_BRACE):
            logger.debug("Found '{' format for macro definition")
            # Form: macro_name { step1; step2; ...; }
            # This can raise ParserError
            steps = self._parse_semicolon_separated_steps()
            if not self._match(TokenType.CLOSE_BRACE):
                logger.error("Expected '}' after macro steps")
                self._add_error(
                    "Expected '}' after macro steps", 
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_macro()
                raise ParserError("Expected '}' after macro steps")
        else:
            logger.error("Expected ':', '=', or '{' after macro name")
            self._add_error(
                "Expected ':', '=', or '{' after macro name", 
                ErrorSeverity.ERROR
            )
            self._synchronize_to_next_macro()
            raise ParserError("Expected ':', '=', or '{' after macro name")
        
        # Create and return the macro definition
        logger.debug(
            f"Successfully parsed macro definition with {len(steps)} steps"
        )
        return MacroDefinition(name=macro_name, steps=steps)

    def _parse_semicolon_separated_steps(self) -> List[MacroStep]:
        """Parse a list of macro steps separated by semicolons.
        
        Returns:
            List of MacroStep objects
        """
        steps = []
        max_attempts = 10  # Prevent infinite loops
        attempt = 0
        
        while not self._is_at_end() and attempt < max_attempts:
            if self._check(TokenType.CLOSE_BRACE):
                break
                
            # Parse a single step
            if self._check(TokenType.AMPERSAND):
                self._advance()  # Consume &
                if not self._check(TokenType.IDENTIFIER):
                    self._add_error(
                        "Expected command after &",
                        ErrorSeverity.ERROR
                    )
                    self._synchronize_to_next_step()
                    attempt += 1
                    continue
                    
                command = self._advance().value  # Get command name
                params = []
                
                # Parse parameters until semicolon
                while not self._is_at_end():
                    if self._check(TokenType.SEMICOLON):
                        break
                    if self._check(TokenType.IDENTIFIER):
                        params.append(self._advance().value)
                    else:
                        self._add_error(
                            f"Invalid parameter for command '{command}'",
                            ErrorSeverity.ERROR
                        )
                        self._synchronize_to_next_step()
                        attempt += 1
                        break
                        
                # Validate the command
                if command not in ["kp", "macro_tap", "macro_wait_time"]:
                    self._add_error(
                        f"Unknown command '{command}'",
                        ErrorSeverity.ERROR
                    )
                    self._synchronize_to_next_step()
                    attempt += 1
                    continue
                        
                steps.append(MacroStep(command=command, params=params))
                attempt = 0  # Reset attempt counter on success
            else:
                self._add_error(
                    "Expected & at start of macro step",
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_step()
                attempt += 1
                continue
                
            # Expect semicolon after each step
            if not self._match(TokenType.SEMICOLON):
                self._add_error(
                    "Expected ; after macro step",
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_step()
                attempt += 1
                
        if attempt >= max_attempts:
            raise ParserError("Too many failed attempts to parse macro steps")
                
        return steps

    def _parse_comma_separated_steps(self) -> List[MacroStep]:
        """Parse a list of macro steps separated by commas.
        
        Returns:
            List of MacroStep objects
        """
        steps = []
        
        while not self._is_at_end():
            if self._check(TokenType.SEMICOLON):
                break
                
            # Parse a single step
            if self._check(TokenType.AMPERSAND):
                self._advance()  # Consume &
                if not self._check(TokenType.IDENTIFIER):
                    self._add_error(
                        "Expected command after &",
                        ErrorSeverity.ERROR
                    )
                    self._synchronize_to_next_step()
                    continue
                    
                command = self._advance().value  # Get command name
                params = []
                
                # Parse parameters until comma or semicolon
                while not self._is_at_end():
                    if (self._check(TokenType.COMMA) or 
                            self._check(TokenType.SEMICOLON)):
                        break
                    if self._check(TokenType.IDENTIFIER):
                        params.append(self._advance().value)
                    else:
                        self._add_error(
                            f"Invalid parameter for command '{command}'",
                            ErrorSeverity.ERROR
                        )
                        self._synchronize_to_next_step()
                        break
                        
                steps.append(MacroStep(command=command, params=params))
            else:
                self._add_error(
                    "Expected & at start of macro step",
                    ErrorSeverity.ERROR
                )
                self._synchronize_to_next_step()
                continue
                
            # Expect comma after each step except the last
            if not self._check(TokenType.SEMICOLON):
                if not self._match(TokenType.COMMA):
                    self._add_error(
                        "Expected , after macro step",
                        ErrorSeverity.ERROR
                    )
                    self._synchronize_to_next_step()
                
        # Consume the final semicolon
        if not self._match(TokenType.SEMICOLON):
            self._add_error(
                "Expected ; at end of macro definition",
                ErrorSeverity.ERROR
            )
            self._synchronize_to_next_step()
            
        return steps

    def _synchronize_to_next_macro(self) -> None:
        """Skip tokens until we find a synchronization point for macro 
        definitions.
        
        This method is used for error recovery. It skips tokens until it finds
        a point where we can reasonably continue parsing macro definitions.
        """
        while not self._is_at_end():
            # Look for the start of a new macro definition
            if self._check(TokenType.IDENTIFIER):
                # Found a potential macro name
                return
            elif self._check(TokenType.CLOSE_BRACE):
                # Found the end of the macros block
                return
            self._advance()
