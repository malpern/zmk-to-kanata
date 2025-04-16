"""Tests for enhanced macro parser features."""
import pytest
from converter.parser.macro_parser import (
    MacroParser,
    MacroDefinition,
    MacroStep,
    MacroParserState,
    Token,
    TokenType,
)
from converter.parser.parser_error import ParserError
from converter.parser.zmk_lexer import SourceLocation


@pytest.fixture
def macro_parser():
    """Create a MacroParser instance."""
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
            MacroStep(command="macro_wait_time", params=["50"])
        ]
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
        steps=[MacroStep(command="kp", params=["A"])]
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
            TokenType.IDENTIFIER, 
            "invalid_command", 
            SourceLocation(4, 19, 40)
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
    macro_parser._transition_state(MacroParserState.IN_PARAMS)  # Invalid from IN_MACROS_BLOCK
    assert macro_parser.state == MacroParserState.IN_PARAMS  # State still changes
    # Error should be logged but not prevent the transition


def test_error_recovery_state_specific(macro_parser):
    """Test state-specific error recovery strategies."""
    # Test recovery in IN_MACRO_DEFINITION state
    macro_parser.state = MacroParserState.IN_MACRO_DEFINITION
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(1, 2, 1))
    ]
    macro_parser.position = 0
    macro_parser._recover_from_error()
    assert macro_parser.state == MacroParserState.IN_MACROS_BLOCK

    # Test recovery in IN_BINDINGS_LIST state
    macro_parser.state = MacroParserState.IN_BINDINGS_LIST
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        Token(TokenType.CLOSE_BRACE, "}", SourceLocation(1, 2, 1))
    ]
    macro_parser.position = 0
    macro_parser._recover_from_error()
    assert macro_parser.state == MacroParserState.IN_MACRO_DEFINITION


def test_synchronization_points(macro_parser):
    """Test synchronization points for error recovery."""
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        Token(TokenType.AMPERSAND, "&", SourceLocation(1, 2, 1)),  # Should be a sync point
        Token(TokenType.SEMICOLON, ";", SourceLocation(1, 3, 2))   # Should be a sync point
    ]
    macro_parser.position = 0
    macro_parser._synchronize_to_next_step()
    assert macro_parser.position == 1  # Should stop at ampersand

    macro_parser.position = 0
    macro_parser.tokens = [
        Token(TokenType.IDENTIFIER, "invalid", SourceLocation(1, 1, 0)),
        Token(TokenType.SEMICOLON, ";", SourceLocation(1, 2, 1))   # Should be a sync point
    ]
    macro_parser._synchronize_to_next_step()
    assert macro_parser.position == 2  # Should consume the semicolon 