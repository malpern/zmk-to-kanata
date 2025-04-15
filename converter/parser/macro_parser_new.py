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
from converter.parser.zmk_ast import ZMKMacroDefinition, ZMKMacroStep, ZMKDocument
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
    """Represents a single step or command within a macro definition."""
    command: str  # e.g., 'kp', 'macro_wait_time', 'macro_tap', 'macro_press', 'macro_release'
    params: Optional[List[str]] = None  # Parameters for the command
    location: Optional[SourceLocation] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.params is None:
            self.params = []
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate that the macro step has a valid command and correct number of parameters.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if the command is known
        if self.command not in MACRO_COMMANDS:
            errors.append(f"Unknown macro command: '{self.command}'")
            return False, errors
        
        # Check parameter count
        min_params, max_params = MACRO_COMMANDS[self.command]
        param_count = len(self.params) if self.params else 0
        
        if param_count < min_params:
            errors.append(f"Command '{self.command}' requires at least {min_params} parameter(s), got {param_count}")
        
        if max_params != -1 and param_count > max_params:
            errors.append(f"Command '{self.command}' accepts at most {max_params} parameter(s), got {param_count}")
        
        return len(errors) == 0, errors


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
    
    def parse_macro_block(self, tokens: List[Token]) -> Dict[str, MacroDefinition]:
        """
        Parse a complete macros block from a token stream.
        
        Args:
            tokens: List of tokens representing the macro block
            
        Returns:
            Dictionary of macro definitions keyed by name
        """
        self.tokens = tokens
        self.position = 0
        self.state = MacroParserState.INITIAL
        self.macros = {}
        
        # Start parsing the macros block
        logger.debug("Starting to parse macros block")
        
        # TODO: Implement the parsing logic
        # This will involve:
        # 1. Finding the macros { token
        # 2. Iterating through tokens to find macro definitions
        # 3. For each definition, calling parse_macro_definition()
        # 4. Building and returning the dictionary of macro definitions
        
        return self.macros
    
    def parse_macro_definition(self) -> Optional[MacroDefinition]:
        """
        Parse a single macro definition.
        
        Returns:
            MacroDefinition if successful, None if parsing failed
        """
        # TODO: Implement macro definition parsing
        # This will involve:
        # 1. Extracting the macro name
        # 2. Processing parameters (label, compatible, etc.)
        # 3. Parsing the bindings list of macro steps
        # 4. Validating the macro and returning it
        
        return None
    
    def parse_macro_step(self) -> Optional[MacroStep]:
        """
        Parse a single macro step.
        
        Returns:
            MacroStep if successful, None if parsing failed
        """
        # TODO: Implement macro step parsing
        # This will involve:
        # 1. Identifying the command (e.g., macro_tap, kp)
        # 2. Extracting parameters
        # 3. Handling nested commands if present
        # 4. Validating and returning the macro step
        
        return None
    
    def parse_macro_usage(self, tokens: List[Token]) -> Optional[MacroUsage]:
        """
        Parse a macro usage/reference from a token stream.
        
        Args:
            tokens: List of tokens representing the macro usage
            
        Returns:
            MacroUsage if successful, None if parsing failed
        """
        # TODO: Implement macro usage parsing
        # This will involve:
        # 1. Extracting the macro name being referenced
        # 2. Processing any parameters
        # 3. Validating against known macros
        # 4. Returning the MacroUsage object
        
        return None
    
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
        Recover from a parsing error by advancing to a recovery point.
        
        Recovery points are tokens like semicolons, closing braces, etc.
        """
        logger.debug("Attempting to recover from parsing error")
        
        # Skip tokens until we find a recovery token or reach the end
        while (self.position < len(self.tokens) and 
               self._peek().type not in self.recovery_tokens):
            token = self._consume()
            logger.debug(f"Skipping token during recovery: {token.type.name} '{token.value}'")
        
        # Consume the recovery token if we found one
        if self.position < len(self.tokens) and self._peek().type in self.recovery_tokens:
            token = self._consume()
            logger.debug(f"Recovered at token: {token.type.name} '{token.value}'")
    
    def _peek(self, offset: int = 0) -> Token:
        """Peek at a token ahead in the stream."""
        if self.position + offset >= len(self.tokens):
            # Return EOF token if we're at the end
            return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", None)
        return self.tokens[self.position + offset]
    
    def _consume(self) -> Token:
        """Consume the current token and advance."""
        if self.position >= len(self.tokens):
            self._add_error("Unexpected end of file", ErrorSeverity.ERROR)
            # Return EOF token
            return Token(TokenType.EOF, "", None)
        
        token = self.tokens[self.position]
        self.position += 1
        return token
    
    def _match(self, token_type: TokenType) -> Optional[Token]:
        """Match the current token against the expected type."""
        token = self._peek()
        if token.type != token_type:
            self._add_error(
                f"Expected {token_type.name}, got {token.type.name}",
                ErrorSeverity.ERROR,
                token.location
            )
            return None
        return self._consume()
    
    def _try_match(self, token_type: TokenType) -> Optional[Token]:
        """Try to match the current token against the expected type."""
        token = self._peek()
        if token.type != token_type:
            return None
        return self._consume()
    
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
        return self._consume()
    
    def _add_error(self, message: str, severity: ErrorSeverity, location: Optional[SourceLocation] = None):
        """Add an error to the error manager."""
        self.error_manager.add_error(
            message=message,
            source="macro_parser",
            severity=severity,
            line_number=location.line if location else None,
            column=location.column if location else None
        )
        logger.log(
            logging.ERROR if severity == ErrorSeverity.ERROR else logging.WARNING,
            f"{severity.name}: {message} at {location}" if location else f"{severity.name}: {message}"
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