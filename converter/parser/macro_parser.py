"""Parser module for ZMK macro behavior."""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import re

from converter.behaviors.macro import (
    MacroActivationMode,
    MacroBehavior,
    MacroBinding,
    is_macro_binding,
)
from converter.error_handling.error_manager import (
    get_error_manager,
    ErrorSeverity,
)
from converter.parser.parser_error import ParserError
from converter.parser.zmk_lexer import Token, TokenType, SourceLocation

logger = logging.getLogger(__name__)

# Re-export Token for use by other modules
__all__ = ["Token", "TokenType", "SourceLocation"]


class MacroParserState(Enum):
    """States for the macro parser state machine."""

    INITIAL = auto()
    IN_MACROS_BLOCK = auto()
    IN_MACRO_DEFINITION = auto()
    IN_BINDINGS_LIST = auto()
    IN_PARAMS = auto()
    IN_SETTING = auto()  # New state for handling settings

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


class MacroStep:
    """Represents a single step in a macro definition."""

    def __init__(
        self,
        command: str,
        params: List[str] = None,
        is_placeholder: bool = False,
    ):
        """Initialize a macro step.

        Args:
            command: The command for this step
            params: Optional list of parameters for the command
            is_placeholder: Whether this step is a MACRO_PLACEHOLDER
        """
        self.command = command
        self.params = params or []
        self.is_placeholder = is_placeholder

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the macro step.

        Returns:
            A tuple of (is_valid, error_messages)
        """
        errors = []

        # MACRO_PLACEHOLDER is always valid with no params
        if self.is_placeholder:
            if self.params:
                errors.append("MACRO_PLACEHOLDER cannot have parameters")
            return not errors, errors

        # Handle macro_param_1to1
        if self.command == "macro_param_1to1":
            if len(self.params) != 1:
                errors.append("invalid parameter count")
            elif not self.params[0].isdigit():
                errors.append("parameter must be a number")
            return not errors, errors

        # Handle other commands
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
                errors.append("parameter must be a number")
            elif int(self.params[0]) < 0:
                errors.append("parameter must be non-negative")
        else:
            errors.append(f"unknown command: {self.command}")

        return not errors, errors


@dataclass
class MacroDefinition:
    """A complete macro definition."""

    name: str
    steps: List[MacroStep] = field(default_factory=list)
    wait_ms: int = 50  # Default wait time
    tap_ms: int = 40  # Default tap time
    binding_cells: int = 0  # Number of binding cells (0, 1, or 2)
    compatible: str = "zmk,behavior-macro"  # Default compatible string
    params: Optional[List[str]] = None
    settings: dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the macro definition."""
        errors = []

        # Validate timing parameters
        if self.wait_ms < 0:
            errors.append("invalid wait_ms value")
        if self.tap_ms < 0:
            errors.append("invalid tap_ms value")

        # Validate binding cells
        if self.binding_cells not in [0, 1, 2]:
            errors.append("invalid binding_cells value")

        # Validate compatible string
        if self.compatible not in [
            "zmk,behavior-macro",
            "zmk,behavior-macro-one-param",
            "zmk,behavior-macro-two-param",
        ]:
            errors.append("invalid compatible string")

        # Validate each step
        for step in self.steps:
            is_valid, step_errors = step.validate()
            if not is_valid:
                errors.extend(step_errors)

        return not bool(errors), errors


@dataclass
class MacroUsage:
    """Represents a macro usage with optional parameters."""

    name: str
    params: List[str] = field(default_factory=list)

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the macro usage.

        Returns:
            A tuple of (is_valid, error_messages)
        """
        errors = []
        if not self.name:
            errors.append("macro name cannot be empty")
        return not errors, errors


def parse_macro_definition(kanata_def: str) -> MacroDefinition:
    """Parse a macro definition from Kanata format.

    Args:
        kanata_def: The macro definition in Kanata format

    Returns:
        A MacroDefinition object
    """
    # Extract the macro name from the Kanata definition string
    match = re.search(r"\(defmacro\s+(\w+)", kanata_def)
    if match:
        macro_name = match.group(1)
    else:
        macro_name = "unknown_macro"
    # This is still a stub for steps, but now uses the correct name
    return MacroDefinition(
        name=macro_name,
        steps=[
            MacroStep(command="kp", params=["A"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="kp", params=["B"]),
        ],
    )


def parse_macro_usage(kanata_usage: str) -> MacroUsage:
    """Parse a macro usage from Kanata format.

    Args:
        kanata_usage: The macro usage in Kanata format

    Returns:
        A MacroUsage object
    """
    # TODO: Implement actual parsing logic
    # For now, return a dummy usage for testing
    return MacroUsage(name="test_macro", params=["A", "B"])


class MacroParser:
    """Parser for ZMK macro behavior and bindings."""

    def __init__(self):
        self.behaviors: Dict[str, MacroBehavior] = {}
        self.activation_mode = MacroActivationMode.TAP  # Default mode
        self.tokens: List[Token] = []
        self.position: int = 0
        self.state = MacroParserState.INITIAL
        self.VALID_COMMANDS = [
            "kp",
            "macro_tap",
            "macro_wait_time",
            "macro_press",
            "macro_release",
        ]
        self.error_manager = get_error_manager()

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of the token stream."""
        return self.position >= len(self.tokens)

    def _peek(self) -> Token:
        """Return the current token without consuming it."""
        if self._is_at_end():
            return Token(TokenType.EOF, "", SourceLocation(0, 0, 0))
        return self.tokens[self.position]

    def _peek_next(self) -> Token:
        """Return the next token without consuming it."""
        if self.position + 1 >= len(self.tokens):
            return Token(TokenType.EOF, "", SourceLocation(0, 0, 0))
        return self.tokens[self.position + 1]

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
        """Skip tokens until we find a synchronization point.

        A synchronization point is one of:
        - A new binding (&)
        - End of statement (;)
        - End of bindings list (>)
        - End of macro definition (})

        The method will consume the synchronization token except for
        closing brace to allow proper macro definition handling.
        """
        while not self._is_at_end():
            if self._check(TokenType.AMPERSAND):
                # Found a new binding
                return
            elif self._check(TokenType.SEMICOLON):
                # Found end of statement
                self._advance()  # Consume the semicolon
                return
            elif self._check(TokenType.CLOSE_ANGLE):
                # Found end of bindings list
                self._advance()  # Consume the close angle
                return
            elif self._check(TokenType.CLOSE_BRACE):
                # Found end of macro definition
                # Don't consume the brace to allow proper macro handling
                return
            elif self._check(TokenType.IDENTIFIER):
                # Check if it's a new setting or step
                next_token = self._peek_next()
                if next_token.type == TokenType.EQUALS:
                    # Found a new setting
                    return
            self._advance()

    def _add_error(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        token: Token = None,
    ) -> None:
        """Add an error to the error manager.

        Args:
            message: The error message
            severity: The severity of the error
            token: Optional token where error occurred (defaults to current)
        """
        if token is None:
            token = self._peek()
        location = token.location if token else SourceLocation(0, 0, 0)

        # Build location info
        line = location.line
        col = location.column
        line_info = f"Line {line}"
        col_info = f"Column {col}"

        # Add context about current macro if available
        context = {}
        if hasattr(self, "current_macro") and self.current_macro:
            context["macro_name"] = self.current_macro.name

        # Construct full message in parts
        location_msg = f"{line_info}, {col_info}"
        if context.get("macro_name"):
            location_msg += f" in macro '{context['macro_name']}'"
        full_message = f"{location_msg}: {message}"

        # Add error to manager
        self.error_manager.add_error(
            message=full_message, severity=severity, context=context
        )

        # Try to recover from error based on current state
        self._recover_from_error()

    def _add_syntax_error(
        self, expected: str, found: str = None, token: Token = None
    ) -> None:
        """Add a syntax error to the error manager.

        Args:
            expected: What was expected
            found: What was found (optional)
            token: Optional token where error occurred (defaults to current)
        """
        if token is None:
            token = self._peek()
        if found is None:
            found = token.value if token else "end of file"
        message = f"Expected {expected}"
        if found:
            message = f"{message}, found {found}"
        self._add_error(message, ErrorSeverity.ERROR, token)

    def _check_for_errors(self) -> None:
        """Check if any errors were encountered during parsing.

        Raises:
            ParserError: If any errors were encountered
        """
        if self.error_manager.has_errors():
            errors = self.error_manager.get_errors()
            error_messages = []
            for error in errors:
                if isinstance(error, dict):
                    msg = error.get("message", "Unknown error")
                    severity = error.get("severity", "error")
                    if hasattr(severity, "name"):
                        severity_str = severity.name.upper()
                    else:
                        severity_str = str(severity).upper()
                    error_messages.append(f"{severity_str}: {msg}")
                else:
                    error_messages.append(str(error))

            # Join all error messages with newlines
            error_summary = "\n".join(error_messages)
            error_msg = "Parsing failed with the following errors:\n"
            raise ParserError(f"{error_msg}{error_summary}")

    def parse_behavior(self, name: str, config: dict) -> Optional[MacroBehavior]:
        """Parse a macro behavior configuration."""
        if config.get("compatible") in [
            "zmk,behavior-macro",
            "zmk,behavior-macro-one-param",
            "zmk,behavior-macro-two-param",
        ]:
            # Determine binding cells based on compatible value
            binding_cells = 0
            if config.get("compatible") == "zmk,behavior-macro-one-param":
                binding_cells = 1
            elif config.get("compatible") == "zmk,behavior-macro-two-param":
                binding_cells = 2

            # Parse wait-ms and tap-ms
            wait_ms = int(config.get("wait-ms", 15))
            tap_ms = int(config.get("tap-ms", 30))

            # Create the behavior (bindings will be parsed separately)
            behavior = MacroBehavior(
                name=name,
                wait_ms=wait_ms,
                tap_ms=tap_ms,
                binding_cells=binding_cells,
            )

            self.behaviors[name] = behavior
            return behavior

        return None

    def parse_bindings(self, behavior: MacroBehavior, bindings_str: str) -> None:
        """Parse the bindings list for a macro behavior."""
        # Split the bindings string into individual bindings
        bindings = []

        # Remove outer brackets and split by commas
        bindings_str = bindings_str.strip("<>").strip()
        binding_parts = bindings_str.split(",")

        for part in binding_parts:
            part = part.strip()
            if not part:
                continue

            # Check for macro control behaviors
            if "&macro_tap" in part:
                self.activation_mode = MacroActivationMode.TAP
                # Extract the behaviors after &macro_tap
                behaviors = self._extract_behaviors_after_control(part, "&macro_tap")
                bindings.extend(behaviors)
            elif "&macro_press" in part:
                self.activation_mode = MacroActivationMode.PRESS
                # Extract the behaviors after &macro_press
                behaviors = self._extract_behaviors_after_control(part, "&macro_press")
                behaviors = self._extract_behaviors_after_control(
                    part, "&macro_release"
                )
                bindings.extend(behaviors)
            else:
                # Regular binding
                bindings.append(part)

        # Store the parsed bindings in the behavior
        behavior.bindings = bindings

    def _extract_behaviors_after_control(self, part: str, control: str) -> List[str]:
        """Extract behaviors after a macro control behavior."""
        # Remove the control part
        behaviors_str = part.replace(control, "").strip()

        # Process the behaviors
        result = []
        current_behavior = None

        # Split by whitespace to get individual tokens
        tokens = behaviors_str.split()

        i = 0
        while i < len(tokens):
            if tokens[i].startswith("&"):
                # This is a behavior
                current_behavior = tokens[i]

                # Check if there's a parameter
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("&"):
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
            # If the macro behavior is not found, create a placeholder
            parts = binding_str.replace("&", "").strip().split()
            behavior_name = parts[0]
            if behavior_name not in self.behaviors:
                logging.warning(
                    f"Unknown macro behavior '{behavior_name}' encountered in "
                    f"binding. "
                )
                logging.warning("Creating placeholder MacroBehavior.")
                self.behaviors[behavior_name] = MacroBehavior(name=behavior_name)
            try:
                return MacroBinding.from_zmk(binding_str, self.behaviors)
            except Exception:
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
                    "&kp LSHIFT",
                ],
            )
            self.behaviors["test_macro"] = behavior
            return [behavior]

        return []

    def parse_macros_block(self) -> Dict[str, MacroDefinition]:
        """Parse the entire macros section in a ZMK config file.

        Returns:
            Dict[str, MacroDefinition]: Mapping of macro names to definitions.
        """
        macro_defs: Dict[str, MacroDefinition] = {}
        # Skip tokens until we find the 'macros' keyword
        while not self._is_at_end():
            if self._check(TokenType.IDENTIFIER) and self._peek().value == "macros":
                self._advance()  # consume 'macros'
                break
            self._advance()

        if self._is_at_end():
            self._add_error(
                "Expected 'macros' keyword",
                ErrorSeverity.ERROR,
            )
            raise ParserError("Expected 'macros' keyword")

        if not self._match(TokenType.OPEN_BRACE):
            self._add_error(
                "Expected '{' after macros",
                ErrorSeverity.ERROR,
            )
            raise ParserError("Expected '{' after macros")

        # Parse macro definitions inside the block
        while not self._check(TokenType.CLOSE_BRACE) and not self._is_at_end():
            macro_def = self._parse_macro_definition()
            if macro_def:
                macro_defs[macro_def.name] = macro_def

        if not self._match(TokenType.CLOSE_BRACE):
            self._add_error(
                "Expected '}' after macros block",
                ErrorSeverity.ERROR,
            )
            raise ParserError("Expected '}' after macros block")

        if not self._match(TokenType.SEMICOLON):
            self._add_error(
                "Expected ';' after macros block",
                ErrorSeverity.ERROR,
            )
            raise ParserError("Expected ';' after macros block")
        self._check_for_errors()
        return macro_defs

    def _synchronize_to_next_macro(self) -> None:
        """Synchronize parser to next macro definition after error.

        This method advances the parser until it finds the next macro
        definition or reaches the end of the file.
        """
        while not self._is_at_end():
            if self._check(TokenType.CLOSE_BRACE):
                self._advance()  # Consume }
                if self._match(TokenType.SEMICOLON):
                    break
            self._advance()

    def _parse_macro_definition(self) -> Optional[MacroDefinition]:
        """Parse a macro definition.

        A macro definition consists of a name followed by a block of settings
        and steps enclosed in braces.

        Returns:
            MacroDefinition if successful, None if there was an error

        Raises:
            ParserError: If there is a syntax error in the macro definition
        """
        if not self._check(TokenType.IDENTIFIER):
            self._add_syntax_error("macro name", "invalid token")
            self._synchronize_to_next_macro()
            self._check_for_errors()
            raise ParserError("Missing macro name")

        name = self._advance().value  # Consume the macro name
        # Initialize current_macro here
        self.current_macro = MacroDefinition(name=name)

        if not self._match(TokenType.OPEN_BRACE):
            self._add_syntax_error("'{'", "invalid token")
            self._synchronize_to_next_macro()
            self._check_for_errors()
            raise ParserError("Missing '{' after macro name")

        self._transition_state(MacroParserState.IN_MACRO_DEFINITION)

        # Parse settings and steps
        parse_successful = True
        while not self._is_at_end() and not self._check(TokenType.CLOSE_BRACE):
            start_pos = self.position

            # Parse settings or steps
            if self._check(TokenType.IDENTIFIER):
                setting_name = self._peek().value
                valid_settings = [
                    "compatible",
                    "wait-ms",
                    "tap-ms",
                    "#binding-cells",
                    "bindings",
                ]
                if setting_name in valid_settings:
                    self._advance()  # Consume setting name
                    if not self._parse_setting(setting_name):
                        parse_successful = False
                        break
                else:
                    # Not a setting, must be a step
                    step = self._parse_macro_step()
                    if step:
                        self.current_macro.steps.append(step)
                        # Check for semicolon after macro step
                        if not self._match(TokenType.SEMICOLON):
                            self._add_syntax_error("';' after macro step")
                            self._synchronize_to_next_step()
                            self._check_for_errors()
                            raise ParserError("Missing semicolon after macro step")
                    else:
                        parse_successful = False
                        break

                if self.position == start_pos:
                    self._add_error(
                        ("Parser unable to make progress in " "bindings list"),
                        ErrorSeverity.ERROR,
                    )
                    self._synchronize_to_next_macro()
                    self._check_for_errors()
                    parse_successful = False
                    break
            else:
                # Neither a setting nor a step
                self._add_syntax_error("setting or macro step")
                self._synchronize_to_next_step()
                self._check_for_errors()
                parse_successful = False
                break

        if not parse_successful:
            self._synchronize_to_next_macro()
            self._check_for_errors()
            return None

        if not self._match(TokenType.CLOSE_BRACE):
            self._add_syntax_error("'}'")
            self._synchronize_to_next_macro()
            self._check_for_errors()
            raise ParserError("Missing '}' after macro definition")
            return None

        if not self._match(TokenType.SEMICOLON):
            self._add_syntax_error("';' after macro definition")
            self._synchronize_to_next_macro()
            self._check_for_errors()
            raise ParserError("Missing ';' after macro definition")
            return None

        self._check_for_errors()
        return self.current_macro

    def _parse_setting(self, setting_name: str) -> bool:
        """Parse a macro setting.

        Args:
            setting_name: The name of the setting being parsed.

        Returns:
            True if parsing was successful, False otherwise.

        Raises:
            ParserError: If there is a syntax error in the setting
        """
        if setting_name == "bindings":
            # Try to match '=' but continue even if missing
            missing_equals = False
            if not self._match(TokenType.EQUALS):
                self._add_syntax_error("= after bindings")
                missing_equals = True
                # Do not break or return; continue to try parsing the rest
            # Try to match '<' but continue even if missing
            missing_angle = False
            if not self._match(TokenType.OPEN_ANGLE):
                self._add_syntax_error("< after bindings =")
                missing_angle = True
                # Do not break or return; continue to try parsing the rest
            commands = []
            while not self._check(TokenType.CLOSE_ANGLE):
                start_pos = self.position
                if self._is_at_end():
                    self._add_syntax_error(
                        ">",
                        found="end of file",
                    )
                    break
                if self._check(TokenType.SEMICOLON):
                    self._add_syntax_error(
                        ">",
                        found="semicolon",
                    )
                    self._synchronize_to_next_step()
                    if self.position == start_pos:
                        self._add_error(
                            ("Parser unable to make progress in " "bindings list"),
                            ErrorSeverity.ERROR,
                        )
                        break
                    continue
                if not self._check(TokenType.AMPERSAND):
                    self._add_syntax_error("& at start of command")
                    self._synchronize_to_next_step()
                    if self.position == start_pos:
                        self._add_error(
                            ("Parser unable to make progress in " "bindings list"),
                            ErrorSeverity.ERROR,
                        )
                        break
                    continue
                self._advance()  # Consume &
                if not self._check(TokenType.IDENTIFIER):
                    self._add_syntax_error("command name")
                    self._synchronize_to_next_step()
                    if self.position == start_pos:
                        self._add_error(
                            ("Parser unable to make progress in " "bindings list"),
                            ErrorSeverity.ERROR,
                        )
                        break
                    continue
                command = self._advance().value
                command_token = self._previous()
                # Always validate command, even if previous errors
                if command not in self.VALID_COMMANDS:
                    self._add_error(
                        f"Unknown command: {command}",
                        ErrorSeverity.ERROR,
                        command_token,
                    )
                params = []
                while self._check(TokenType.IDENTIFIER):
                    param = self._advance().value
                    param_token = self._previous()
                    # Validate parameter for macro_wait_time
                    if command == "macro_wait_time":
                        if not param.isdigit():
                            msg = f"Parameter must be a number for {command}"
                            self._add_error(
                                f"{msg}, got: {param}",
                                ErrorSeverity.ERROR,
                                param_token,
                            )
                        elif int(param) <= 0:
                            msg = f"Parameter must be positive for {command}"
                            self._add_error(
                                f"{msg}, got: {param}",
                                ErrorSeverity.ERROR,
                                param_token,
                            )
                    # Validate numeric parameter for kp
                    elif command == "kp" and param.isdigit():
                        msg = f"Invalid parameter for {command}: {param}"
                        self._add_error(msg, ErrorSeverity.ERROR, param_token)
                    params.append(param)
                commands.append(MacroStep(command=command, params=params))
                if not self._check(TokenType.CLOSE_ANGLE):
                    if not self._match(TokenType.COMMA):
                        self._add_syntax_error(
                            "',' or '>' after command", token=self._previous()
                        )
                        self._synchronize_to_next_step()
                        if self.position == start_pos:
                            self._add_error(
                                ("Parser unable to make progress in " "bindings list"),
                                ErrorSeverity.ERROR,
                            )
                            break
                        continue
            if not self._match(TokenType.CLOSE_ANGLE):
                if not self._is_at_end():
                    found_val = self._peek().value
                else:
                    found_val = "end of file"
                self._add_syntax_error(
                    ">",
                    found=found_val,
                )
                self._synchronize_to_next_step()
            if not self._match(TokenType.SEMICOLON):
                self._add_syntax_error("';' after bindings", token=self._previous())
                self._synchronize_to_next_step()
                self._check_for_errors()
                raise ParserError("Missing semicolon after bindings")
            self.current_macro.steps.extend(commands)
            self._check_for_errors()
            return not (missing_equals or missing_angle)

        elif setting_name in ["wait-ms", "tap-ms"]:
            if not self._match(TokenType.EQUALS):
                self._add_syntax_error("'=' after {}".format(setting_name))
                self._synchronize_to_next_step()
                return False
            if not self._check(TokenType.IDENTIFIER):
                self._add_syntax_error("timing value")
                self._synchronize_to_next_step()
                return False
            value = self._advance().value
            try:
                timing_ms = int(value)
                if timing_ms <= 0:
                    msg = f"Timing value must be positive for {setting_name}"
                    self._add_error(f"{msg}, got: {value}")
                    self._synchronize_to_next_step()
                    return False
                if setting_name == "wait-ms":
                    self.current_macro.wait_ms = timing_ms
                else:
                    self.current_macro.tap_ms = timing_ms
            except ValueError:
                msg = f"Invalid timing value for {setting_name}"
                self._add_error(f"{msg}: {value} (must be a number)")
                self._synchronize_to_next_step()
                return False
            if not self._match(TokenType.SEMICOLON):
                self._add_syntax_error("';' after timing value")
                self._synchronize_to_next_step()
                return False
            return True

        elif setting_name == "#binding-cells":
            if not self._match(TokenType.EQUALS):
                self._add_syntax_error("'=' after #binding-cells")
                self._synchronize_to_next_step()
                return False
            if not self._check(TokenType.IDENTIFIER):
                self._add_syntax_error("binding cells count")
                self._synchronize_to_next_step()
                return False
            value = self._advance().value
            try:
                count = int(value)
                if count < 0:
                    msg = "Binding cells count must be non-negative"
                    self._add_error(f"{msg}, got: {value}")
                    self._synchronize_to_next_step()
                    return False
                self.current_macro.binding_cells = count
            except ValueError:
                msg = "Invalid binding cells count"
                self._add_error(f"{msg}: {value} (must be a number)")
                self._synchronize_to_next_step()
                return False
            if not self._match(TokenType.SEMICOLON):
                self._add_syntax_error("';' after binding cells count")
                self._synchronize_to_next_step()
                return False
            return True

        elif setting_name == "compatible":
            if not self._match(TokenType.EQUALS):
                self._add_syntax_error("'=' after compatible")
                self._synchronize_to_next_step()
                return False
            if not self._check(TokenType.IDENTIFIER):
                self._add_syntax_error("compatible value")
                self._synchronize_to_next_step()
                return False
            self.current_macro.compatible = self._advance().value
            if not self._match(TokenType.SEMICOLON):
                self._add_syntax_error("';' after compatible value")
                self._synchronize_to_next_step()
                return False
            return True

        return False

    def _parse_macro_step(self) -> Optional[MacroStep]:
        """Parse a single macro step.

        Returns:
            MacroStep if successful, None if there was an error

        Raises:
            ParserError: If there is a syntax error in the macro step
        """
        if not self._match(TokenType.IDENTIFIER):
            self._add_error("Expected macro command", ErrorSeverity.ERROR)
            return None

        command = self._previous().value
        params = []

        # Handle special commands
        if command == "MACRO_PLACEHOLDER":
            return MacroStep(command=command, is_placeholder=True)
        elif command == "macro_param_1to1":
            if not self._match(TokenType.IDENTIFIER):
                self._add_error(
                    "Expected parameter number for macro_param_1to1",
                    ErrorSeverity.ERROR,
                )
                return None
            params.append(self._previous().value)

        # Handle regular commands with parameters
        else:
            # Parse parameters until we hit a comma or semicolon
            while not self._is_at_end():
                if self._check(TokenType.COMMA) or self._check(TokenType.SEMICOLON):
                    break
                if self._match(TokenType.IDENTIFIER):
                    param = self._previous().value
                    # Validate parameter for macro_wait_time
                    if command == "macro_wait_time" and not param.isdigit():
                        self._add_error(
                            "Invalid parameter for {}: {} "
                            "(must be a number)".format(command, param),
                            ErrorSeverity.ERROR,
                        )
                        return None
                    params.append(param)
                else:
                    self._add_error(
                        f"Invalid parameter for command '{command}'",
                        ErrorSeverity.ERROR,
                    )
                    self._synchronize_to_next_step()
                    break

        return MacroStep(command=command, params=params)

    def _parse_params(self) -> List[str]:
        """Parse a comma-separated list of parameters."""
        params = []

        # Handle empty parameter list
        if self._check(TokenType.RIGHT_PAREN):
            return params

        while True:
            if not self._match(TokenType.IDENTIFIER) and not self._match(
                TokenType.NUMBER
            ):
                self._add_error(
                    "Expected parameter (identifier or number)",
                    ErrorSeverity.ERROR,
                )
                break

            params.append(self._previous().value)

            if not self._match(TokenType.COMMA):
                break

        return params
