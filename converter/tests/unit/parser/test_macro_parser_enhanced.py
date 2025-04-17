"""Tests for enhanced macro parser features."""

import pytest

from converter.error_handling.error_manager import get_error_manager
from converter.parser.macro_parser import (
    MacroDefinition,
    MacroParser,
    MacroParserState,
    MacroStep,
    Token,
    TokenType,
)
from converter.parser.parser_error import ParserError
from converter.parser.zmk_lexer import SourceLocation


@pytest.fixture
def macro_parser():
    """Create a MacroParser instance."""
    # Clear any existing errors
    error_manager = get_error_manager()
    error_manager.clear()

    parser = MacroParser()
    parser.tokens = []  # Initialize tokens list
    parser.position = 0  # Initialize position
    return parser


def test_validate_macro_command_parameters():
    """Test validation of macro command parameters."""
    # Test valid command with correct parameters
    macro = MacroDefinition(
        name="test_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
            MacroStep(command="macro_wait_time", params=["50"]),
        ],
    )
    is_valid, errors = macro.validate()
    assert is_valid
    assert not errors

    # Test command with too few parameters
    macro.steps.append(MacroStep(command="kp", params=[]))
    is_valid, errors = macro.validate()
    assert not is_valid
    assert "invalid parameter count" in errors[0]

    # Test command with too many parameters
    macro.steps.append(MacroStep(command="macro_tap", params=["extra"]))
    is_valid, errors = macro.validate()
    assert not is_valid
    assert "invalid parameter count" in errors[1]


def test_validate_timing_parameters():
    """Test validation of timing parameters."""
    # Test valid timing values
    macro = MacroDefinition(
        name="test_macro",
        wait_ms=50,
        tap_ms=100,
        steps=[MacroStep(command="kp", params=["A"])],
    )
    is_valid, errors = macro.validate()
    assert is_valid
    assert not errors

    # Test invalid wait_ms
    macro.wait_ms = -1
    is_valid, errors = macro.validate()
    assert not is_valid
    assert "invalid wait_ms value" in errors[0]

    # Test invalid tap_ms
    macro.wait_ms = 50
    macro.tap_ms = -1
    is_valid, errors = macro.validate()
    assert not is_valid
    assert "invalid tap_ms value" in errors[0]


def test_error_recovery_with_context(macro_parser):
    """Test error recovery with context logging."""
    tokens = [
        Token(TokenType.SLASH, "/", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 3, 2)),
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(2, 5, 8)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 7, 10)),
        Token(TokenType.IDENTIFIER, "test_macro", SourceLocation(3, 9, 19)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(3, 11, 21)),
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(4, 13, 34)),
        Token(TokenType.EQUALS, "=", SourceLocation(4, 15, 36)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(4, 17, 38)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(4, 18, 39)),
        Token(
            TokenType.IDENTIFIER, "invalid_command", SourceLocation(4, 19, 40)
        ),
        Token(TokenType.CLOSE_ANGLE, ">", SourceLocation(4, 33, 54)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 34, 55)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(5, 9, 64)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 10, 65)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(6, 5, 70)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(6, 6, 71)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(7, 1, 72)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(7, 2, 73)),
    ]

    # Initialize the parser with the tokens and state
    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    # Parse the macros block
    with pytest.raises(ParserError) as exc_info:
        macro_parser.parse_macros_block()

    error_message = str(exc_info.value)
    assert "invalid_command" in error_message
    assert "Line " in error_message  # Check for line number format "Line X:"


def test_state_transition_validation(macro_parser):
    """Test validation of state transitions."""
    # Initialize tokens and position
    macro_parser.tokens = [Token(TokenType.EOF, "", SourceLocation(1, 1, 0))]
    macro_parser.position = 0

    # Test valid transition
    macro_parser._transition_state(MacroParserState.IN_MACROS_BLOCK)
    assert macro_parser.state == MacroParserState.IN_MACROS_BLOCK

    # Test invalid transition
    # Invalid from IN_MACROS_BLOCK
    macro_parser._transition_state(MacroParserState.IN_PARAMS)
    # State still changes
    assert macro_parser.state == MacroParserState.IN_PARAMS
    # Error should be logged but not prevent the transition


def test_error_recovery_state_specific(macro_parser):
    """Test state-specific error recovery strategies."""
    # Test recovery in IN_MACRO_DEFINITION state
    macro_parser.state = MacroParserState.IN_MACRO_DEFINITION
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(1, 2, 1)),
    ]
    macro_parser.position = 0
    macro_parser._recover_from_error()
    assert macro_parser.state == MacroParserState.IN_MACROS_BLOCK

    # Test recovery in IN_BINDINGS_LIST state
    macro_parser.state = MacroParserState.IN_BINDINGS_LIST
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(1, 2, 1)),
    ]
    macro_parser.position = 0
    macro_parser._recover_from_error()
    assert macro_parser.state == MacroParserState.IN_MACRO_DEFINITION


def test_synchronization_points(macro_parser):
    """Test synchronization points for error recovery."""
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        # Should be a sync point
        Token(TokenType.AMPERSAND, "&", SourceLocation(1, 2, 1)),
        # Should be a sync point
        Token(TokenType.SEMICOLON, ";", SourceLocation(1, 3, 2)),
    ]
    macro_parser.position = 0
    macro_parser._synchronize_to_next_step()
    assert macro_parser.position == 1  # Should stop at ampersand

    macro_parser.position = 0
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        # Should be a sync point
        Token(TokenType.SEMICOLON, ";", SourceLocation(1, 2, 1)),
    ]
    macro_parser._synchronize_to_next_step()
    # Should consume the semicolon
    assert macro_parser.position == 2


def test_basic_macro(macro_parser):
    """Test parsing of a basic macro with simple commands."""
    tokens = [
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 7, 6)),
        Token(TokenType.IDENTIFIER, "test_macro", SourceLocation(2, 4, 11)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 14, 21)),
        Token(TokenType.IDENTIFIER, "compatible", SourceLocation(3, 8, 30)),
        Token(TokenType.EQUALS, "=", SourceLocation(3, 18, 40)),
        Token(
            TokenType.IDENTIFIER,
            "zmk,behavior-macro",
            SourceLocation(3, 20, 42),
        ),
        Token(TokenType.SEMICOLON, ";", SourceLocation(3, 39, 61)),
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(4, 8, 70)),
        Token(TokenType.EQUALS, "=", SourceLocation(4, 16, 78)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(4, 18, 80)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(4, 19, 81)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(4, 20, 82)),
        Token(TokenType.IDENTIFIER, "A", SourceLocation(4, 23, 85)),
        Token(TokenType.COMMA, ",", SourceLocation(4, 24, 86)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(4, 26, 88)),
        Token(
            TokenType.IDENTIFIER, "macro_wait_time", SourceLocation(4, 27, 89)
        ),
        Token(TokenType.IDENTIFIER, "50", SourceLocation(4, 42, 104)),
        Token(TokenType.CLOSE_ANGLE, ">", SourceLocation(4, 44, 106)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 45, 107)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(5, 4, 112)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 5, 113)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(6, 1, 115)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(6, 2, 116)),
    ]

    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    macro_defs = macro_parser.parse_macros_block()
    assert "test_macro" in macro_defs

    macro = macro_defs["test_macro"]
    assert macro.name == "test_macro"
    assert macro.compatible == "zmk,behavior-macro"
    assert len(macro.steps) == 2

    # Verify first step (kp A)
    assert macro.steps[0].command == "kp"
    assert macro.steps[0].params == ["A"]

    # Verify second step (macro_wait_time 50)
    assert macro.steps[1].command == "macro_wait_time"
    assert macro.steps[1].params == ["50"]


def test_complex_macro(macro_parser):
    """Test parsing of a complex macro with multiple commands and settings."""
    tokens = [
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 7, 6)),
        Token(TokenType.IDENTIFIER, "complex_macro", SourceLocation(2, 4, 11)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 17, 24)),
        # Settings
        Token(TokenType.IDENTIFIER, "compatible", SourceLocation(3, 8, 33)),
        Token(TokenType.EQUALS, "=", SourceLocation(3, 18, 43)),
        Token(
            TokenType.IDENTIFIER,
            "zmk,behavior-macro-two-param",
            SourceLocation(3, 20, 45),
        ),
        Token(TokenType.SEMICOLON, ";", SourceLocation(3, 48, 73)),
        Token(TokenType.IDENTIFIER, "wait-ms", SourceLocation(4, 8, 82)),
        Token(TokenType.EQUALS, "=", SourceLocation(4, 16, 90)),
        Token(TokenType.IDENTIFIER, "30", SourceLocation(4, 18, 92)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 20, 94)),
        Token(TokenType.IDENTIFIER, "tap-ms", SourceLocation(5, 8, 103)),
        Token(TokenType.EQUALS, "=", SourceLocation(5, 15, 110)),
        Token(TokenType.IDENTIFIER, "20", SourceLocation(5, 17, 112)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 19, 114)),
        Token(
            TokenType.IDENTIFIER, "#binding-cells", SourceLocation(6, 8, 123)
        ),
        Token(TokenType.EQUALS, "=", SourceLocation(6, 22, 137)),
        Token(TokenType.IDENTIFIER, "2", SourceLocation(6, 24, 139)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(6, 25, 140)),
        # Bindings
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(7, 8, 149)),
        Token(TokenType.EQUALS, "=", SourceLocation(7, 16, 157)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(7, 18, 159)),
        # First sequence
        Token(TokenType.AMPERSAND, "&", SourceLocation(8, 12, 172)),
        Token(TokenType.IDENTIFIER, "macro_tap", SourceLocation(8, 13, 173)),
        Token(TokenType.COMMA, ",", SourceLocation(8, 22, 182)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(8, 24, 184)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(8, 25, 185)),
        Token(TokenType.IDENTIFIER, "LSHIFT", SourceLocation(8, 28, 188)),
        Token(TokenType.COMMA, ",", SourceLocation(8, 34, 194)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(8, 36, 196)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(8, 37, 197)),
        Token(TokenType.IDENTIFIER, "A", SourceLocation(8, 40, 200)),
        Token(TokenType.COMMA, ",", SourceLocation(8, 41, 201)),
        # Second sequence
        Token(TokenType.AMPERSAND, "&", SourceLocation(9, 12, 214)),
        Token(
            TokenType.IDENTIFIER, "macro_wait_time", SourceLocation(9, 13, 215)
        ),
        Token(TokenType.IDENTIFIER, "100", SourceLocation(9, 28, 230)),
        Token(TokenType.COMMA, ",", SourceLocation(9, 31, 233)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(9, 33, 235)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(9, 34, 236)),
        Token(TokenType.IDENTIFIER, "B", SourceLocation(9, 37, 239)),
        Token(TokenType.CLOSE_ANGLE, ">", SourceLocation(10, 8, 248)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(10, 9, 249)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(11, 4, 254)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(11, 5, 255)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(12, 1, 257)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(12, 2, 258)),
    ]

    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    macro_defs = macro_parser.parse_macros_block()
    assert "complex_macro" in macro_defs

    macro = macro_defs["complex_macro"]
    assert macro.name == "complex_macro"
    assert macro.compatible == "zmk,behavior-macro-two-param"
    assert macro.wait_ms == 30
    assert macro.tap_ms == 20
    assert macro.binding_cells == 2
    assert len(macro.steps) == 5

    # Verify macro_tap step
    assert macro.steps[0].command == "macro_tap"
    assert not macro.steps[0].params

    # Verify first kp step
    assert macro.steps[1].command == "kp"
    assert macro.steps[1].params == ["LSHIFT"]

    # Verify second kp step
    assert macro.steps[2].command == "kp"
    assert macro.steps[2].params == ["A"]

    # Verify macro_wait_time step
    assert macro.steps[3].command == "macro_wait_time"
    assert macro.steps[3].params == ["100"]

    # Verify final kp step
    assert macro.steps[4].command == "kp"
    assert macro.steps[4].params == ["B"]


def test_error_recovery_missing_semicolon(macro_parser):
    """Test error recovery when a semicolon is missing after a macro step."""
    tokens = [
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 7, 6)),
        Token(TokenType.IDENTIFIER, "test_macro", SourceLocation(2, 4, 11)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 14, 21)),
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(3, 8, 30)),
        Token(TokenType.EQUALS, "=", SourceLocation(3, 16, 38)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(3, 18, 40)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(3, 19, 41)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(3, 20, 42)),
        Token(TokenType.IDENTIFIER, "A", SourceLocation(3, 23, 45)),
        # Missing semicolon here
        Token(TokenType.CLOSE_ANGLE, ">", SourceLocation(3, 24, 46)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(3, 25, 47)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(4, 4, 51)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 5, 52)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(5, 1, 53)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 2, 54)),
    ]

    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    with pytest.raises(ParserError) as exc_info:
        macro_parser.parse_macros_block()

    error_message = str(exc_info.value)
    assert "Expected ," in error_message or "Expected ;" in error_message
    assert "Line " in error_message


def test_error_recovery_invalid_parameter(macro_parser):
    """Test error recovery when an invalid parameter is encountered."""
    tokens = [
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 7, 6)),
        Token(TokenType.IDENTIFIER, "test_macro", SourceLocation(2, 4, 11)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 14, 21)),
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(3, 8, 30)),
        Token(TokenType.EQUALS, "=", SourceLocation(3, 16, 38)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(3, 18, 40)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(3, 19, 41)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(3, 20, 42)),
        # Invalid parameter (number where string expected)
        Token(TokenType.IDENTIFIER, "123", SourceLocation(3, 23, 45)),
        Token(TokenType.CLOSE_ANGLE, ">", SourceLocation(3, 26, 48)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(3, 27, 49)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(4, 4, 53)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 5, 54)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(5, 1, 55)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 2, 56)),
    ]

    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    with pytest.raises(ParserError) as exc_info:
        macro_parser.parse_macros_block()

    error_message = str(exc_info.value)
    assert "Invalid parameter" in error_message
    assert "Line " in error_message
    assert "123" in error_message


def test_error_recovery_unclosed_bindings(macro_parser):
    """Test error recovery when bindings list is not properly closed."""
    tokens = [
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 7, 6)),
        Token(TokenType.IDENTIFIER, "test_macro", SourceLocation(2, 4, 11)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 14, 21)),
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(3, 8, 30)),
        Token(TokenType.EQUALS, "=", SourceLocation(3, 16, 38)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(3, 18, 40)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(3, 19, 41)),
        Token(TokenType.IDENTIFIER, "kp", SourceLocation(3, 20, 42)),
        Token(TokenType.IDENTIFIER, "A", SourceLocation(3, 23, 45)),
        Token(TokenType.COMMA, ",", SourceLocation(3, 24, 46)),
        # Missing closing angle bracket
        Token(TokenType.SEMICOLON, ";", SourceLocation(3, 25, 47)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(4, 4, 51)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 5, 52)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(5, 1, 53)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 2, 54)),
    ]

    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    with pytest.raises(ParserError) as exc_info:
        macro_parser.parse_macros_block()

    error_message = str(exc_info.value)
    assert "Expected >" in error_message
    assert "Line " in error_message


def test_error_recovery_multiple_errors(macro_parser):
    """Test error recovery when multiple errors occur in sequence."""
    tokens = [
        Token(TokenType.IDENTIFIER, "macros", SourceLocation(1, 1, 0)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(1, 7, 6)),
        Token(TokenType.IDENTIFIER, "test_macro", SourceLocation(2, 4, 11)),
        Token(TokenType.OPEN_BRACE, "{", SourceLocation(2, 14, 21)),
        # First error: missing equals
        Token(TokenType.IDENTIFIER, "bindings", SourceLocation(3, 8, 30)),
        Token(TokenType.OPEN_ANGLE, "<", SourceLocation(3, 18, 40)),
        # Second error: invalid command
        Token(TokenType.AMPERSAND, "&", SourceLocation(3, 19, 41)),
        Token(TokenType.IDENTIFIER, "invalid_cmd", SourceLocation(3, 20, 42)),
        # Third error: missing closing angle bracket
        Token(TokenType.SEMICOLON, ";", SourceLocation(3, 30, 52)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(4, 4, 56)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(4, 5, 57)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(5, 1, 58)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(5, 2, 59)),
    ]

    macro_parser.tokens = tokens
    macro_parser.position = 0
    macro_parser.state = MacroParserState.INITIAL

    with pytest.raises(ParserError) as exc_info:
        macro_parser.parse_macros_block()

    error_message = str(exc_info.value)
    # Check that multiple errors were detected
    assert "Expected =" in error_message
    assert "Unknown command" in error_message
    assert "Line " in error_message
