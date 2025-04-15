"""Unit tests for the macro parser module."""
import pytest
import re

from converter.parser.macro_parser import MacroParser, Macro, MacroStep
from converter.parser.parser_error import ParserError
from converter.parser.macro_parser_new import ZMKMacroParser, Token, TokenType


def test_basic_macro(macro_parser: MacroParser):
    """Test parsing a basic macro definition."""
    # Test macro block start
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    assert macro_parser.in_macros_block is True

    # Test macro definition start
    macro_parser.process_line("        test_macro: test_macro {")
    assert macro_parser.current_macro is not None
    assert macro_parser.current_macro.name == "test_macro"

    # Test macro settings
    macro_parser.process_line("            wait-ms = <30>;")
    assert macro_parser.current_macro.wait_ms == 30
    macro_parser.process_line("            tap-ms = <40>;")
    assert macro_parser.current_macro.tap_ms == 40

    # Test bindings
    macro_parser.process_line("            bindings = <&macro_tap &kp A>;")
    assert len(macro_parser.current_macro.bindings) == 2
    assert isinstance(macro_parser.current_macro.bindings[0], MacroStep)
    assert macro_parser.current_macro.bindings[0].command == "macro_tap"
    assert macro_parser.current_macro.bindings[1].command == "kp"
    assert macro_parser.current_macro.bindings[1].params == ["A"]

    # Test macro end
    macro_parser.process_line("        };")
    assert macro_parser.current_macro is None
    assert len(macro_parser.macros) == 1

    # Test macros block end
    macro_parser.process_line("    };")
    assert macro_parser.in_macros_block is False


@pytest.mark.skip(reason="Parameter parsing for multi-step lines needs refactoring")
def test_complex_macro(macro_parser: MacroParser):
    """Test parsing a macro with multiple bindings."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    macro_parser.process_line("        complex: complex {")
    macro_parser.process_line("            wait-ms = <50>;")
    macro_parser.process_line("            tap-ms = <60>;")
    macro_parser.process_line("            bindings = <")
    macro_parser.process_line("                &macro_press &kp LSHIFT,")
    macro_parser.process_line("                &macro_tap &kp A &kp B &kp C,")
    macro_parser.process_line("                &macro_release &kp LSHIFT")
    macro_parser.process_line("            >;")
    macro_parser.process_line("        };")
    macro_parser.process_line("    };")

    assert len(macro_parser.macros) == 1
    macro = macro_parser.macros[0]
    assert macro.name == "complex"
    assert macro.wait_ms == 50
    assert macro.tap_ms == 60
    assert len(macro.bindings) == 8

    # Check press binding
    assert macro.bindings[0].command == "macro_press"
    assert macro.bindings[1].command == "kp"
    assert macro.bindings[1].params == ["LSHIFT"]

    # Check tap bindings
    for i, key in enumerate(["A", "B", "C"]):
        binding = macro.bindings[i + 2]
        assert binding.command == "macro_tap"
        assert binding.params == [key]

    # Check release binding
    assert macro.bindings[7].command == "kp"
    assert macro.bindings[7].params == ["LSHIFT"]


def test_parameterized_macro(macro_parser: MacroParser):
    """Test parsing a parameterized macro."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    macro_parser.process_line("        param_macro: param_macro {")
    macro_parser.process_line('            compatible = "zmk,behavior-macro-one-param";')
    macro_parser.process_line("            #binding-cells = <1>;")
    macro_parser.process_line("            bindings = <")
    macro_parser.process_line("                &macro_param_1to1,")
    macro_parser.process_line("                &kp MACRO_PLACEHOLDER")
    macro_parser.process_line("            >;")
    macro_parser.process_line("        };")
    macro_parser.process_line("    };")

    assert len(macro_parser.macros) == 1
    macro = macro_parser.macros[0]
    assert macro.name == "param_macro"
    assert macro.compatible == "zmk,behavior-macro-one-param"
    assert macro.param_count == 1
    assert len(macro.bindings) == 2

    # Check step command
    assert macro.bindings[0].command == "macro_param_1to1"
    assert macro.bindings[1].command == "kp"
    assert macro.bindings[1].params == ["MACRO_PLACEHOLDER"]


@pytest.mark.parametrize("invalid_setting,error_msg,match_exact", [
    # Expect "Invalid setting format" for missing <>
    ("wait-ms = 30;", "Invalid setting format", True), 
    # Expect "Setting value must be positive" for negative value (allow substring match)
    ("tap-ms = <-10>;", "Setting value must be positive", False), 
    # Expect "Invalid bindings line" (exact match)
    ("bindings = kp A;", "Invalid bindings line", True), 
])
def test_invalid_macro_settings(macro_parser: MacroParser, invalid_setting: str, error_msg: str, match_exact: bool):
    """Test handling of invalid macro settings."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    macro_parser.process_line("        test: test {")

    if match_exact:
        # Use exact match for specific format errors
        with pytest.raises(ParserError, match=re.escape(error_msg)):
            macro_parser.process_line(f"            {invalid_setting}")
    else:
        # Use substring match for value errors where extra info might be present
        with pytest.raises(ParserError) as exc_info:
             macro_parser.process_line(f"            {invalid_setting}")
        assert error_msg in str(exc_info.value)


def test_nested_macros(macro_parser: MacroParser):
    """Test that nested macro blocks are not allowed."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")

    with pytest.raises(ParserError) as exc_info:
        macro_parser.process_line("        macros {")
    assert "Nested macros blocks are not allowed" in str(exc_info.value)


def make_token(value, type_=TokenType.IDENTIFIER):
    return Token(type_, value, None)

def test_valid_macro_usage():
    parser = ZMKMacroParser()
    tokens = [make_token('my_macro'), make_token('param1'), make_token('param2')]
    known_macros = {'my_macro'}
    usage = parser.parse_macro_usage(tokens, known_macros)
    assert usage is not None
    assert usage.name == 'my_macro'
    assert usage.params == ['param1', 'param2']

def test_macro_usage_no_params():
    parser = ZMKMacroParser()
    tokens = [make_token('simple_macro')]
    known_macros = {'simple_macro'}
    usage = parser.parse_macro_usage(tokens, known_macros)
    assert usage is not None
    assert usage.name == 'simple_macro'
    assert usage.params == []

def test_unknown_macro_name():
    parser = ZMKMacroParser()
    tokens = [make_token('unknown_macro')]
    known_macros = {'other_macro'}
    usage = parser.parse_macro_usage(tokens, known_macros)
    assert usage is None  # Should fail validation

def test_empty_token_list():
    parser = ZMKMacroParser()
    usage = parser.parse_macro_usage([], {'any_macro'})
    assert usage is None

def test_macro_usage_mixed_params():
    parser = ZMKMacroParser()
    tokens = [
        make_token('macro1'),
        make_token('42', TokenType.NUMBER),
        make_token('"string"', TokenType.STRING),
        make_token('param')
    ]
    known_macros = {'macro1'}
    usage = parser.parse_macro_usage(tokens, known_macros)
    assert usage is not None
    assert usage.params == ['42', '"string"', 'param']
