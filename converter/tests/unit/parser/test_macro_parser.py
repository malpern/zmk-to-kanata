"""Unit tests for the macro parser module."""
import pytest
from converter.parser.macro_parser_v2 import ParserError


def test_basic_macro(macro_parser):
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
    assert len(macro_parser.current_macro.bindings) == 1
    binding = macro_parser.current_macro.bindings[0]
    assert binding.action == "macro_tap"
    assert binding.behavior == "kp"
    assert binding.param == "A"

    # Test macro end
    macro_parser.process_line("        };")
    assert macro_parser.current_macro is None
    assert len(macro_parser.macros) == 1

    # Test macros block end
    macro_parser.process_line("    };")
    assert macro_parser.in_macros_block is False


def test_complex_macro(macro_parser):
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
    assert len(macro.bindings) == 5

    # Check press binding
    assert macro.bindings[0].action == "macro_press"
    assert macro.bindings[0].behavior == "kp"
    assert macro.bindings[0].param == "LSHIFT"

    # Check tap bindings
    for i, key in enumerate(["A", "B", "C"]):
        binding = macro.bindings[i + 1]
        assert binding.action == "macro_tap"
        assert binding.behavior == "kp"
        assert binding.param == key

    # Check release binding
    assert macro.bindings[4].action == "macro_release"
    assert macro.bindings[4].behavior == "kp"
    assert macro.bindings[4].param == "LSHIFT"


def test_parameterized_macro(macro_parser):
    """Test parsing a parameterized macro."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    macro_parser.process_line("        param_macro: param_macro {")
    macro_parser.process_line("            compatible = ")
    macro_parser.process_line('                "zmk,behavior-macro-one-param";')
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
    assert macro.param_count == 1
    assert len(macro.bindings) == 2

    # Check parameter binding
    assert macro.bindings[0].action == "macro_param_1to1"
    assert macro.bindings[0].behavior is None
    assert macro.bindings[0].param is None

    # Check placeholder binding
    assert macro.bindings[1].action == "kp"
    assert macro.bindings[1].behavior == "MACRO_PLACEHOLDER"
    assert macro.bindings[1].param is None


@pytest.mark.parametrize("invalid_setting,error_msg", [
    ("wait-ms = 30;", "Invalid setting format"),
    ("tap-ms = <-10>;", "Setting value must be positive"),
    ("bindings = kp A;", "Invalid bindings line"),
])
def test_invalid_macro_settings(macro_parser, invalid_setting, error_msg):
    """Test handling of invalid macro settings."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    macro_parser.process_line("        test: test {")

    with pytest.raises(ParserError, match=error_msg):
        macro_parser.process_line(f"            {invalid_setting}")


def test_nested_macros(macro_parser):
    """Test that nested macro blocks are not allowed."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")

    with pytest.raises(ParserError) as exc_info:
        macro_parser.process_line("        macros {")
    assert "Nested macros blocks are not allowed" in str(exc_info.value)
