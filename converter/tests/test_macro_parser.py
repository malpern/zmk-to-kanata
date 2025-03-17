"""Tests for the ZMK macro parser."""
import pytest

from converter.parser.macro_parser_v2 import MacroParser, ParserError


def test_basic_macro():
    """Test parsing a basic macro definition."""
    parser = MacroParser()

    # Test macro block start
    parser.process_line("/ {")
    parser.process_line("    macros {")
    assert parser.in_macros_block is True

    # Test macro definition start
    parser.process_line("        test_macro: test_macro {")
    assert parser.current_macro is not None
    assert parser.current_macro.name == "test_macro"

    # Test macro settings
    parser.process_line("            wait-ms = <30>;")
    assert parser.current_macro.wait_ms == 30
    parser.process_line("            tap-ms = <40>;")
    assert parser.current_macro.tap_ms == 40

    # Test bindings
    parser.process_line("            bindings = <&macro_tap &kp A>;")
    assert len(parser.current_macro.bindings) == 1
    binding = parser.current_macro.bindings[0]
    assert binding.action == "macro_tap"
    assert binding.behavior == "kp"
    assert binding.param == "A"

    # Test macro end
    parser.process_line("        };")
    assert parser.current_macro is None
    assert len(parser.macros) == 1

    # Test macros block end
    parser.process_line("    };")
    assert parser.in_macros_block is False


def test_complex_macro():
    """Test parsing a macro with multiple bindings."""
    parser = MacroParser()

    parser.process_line("/ {")
    parser.process_line("    macros {")
    parser.process_line("        complex: complex {")
    parser.process_line("            wait-ms = <50>;")
    parser.process_line("            tap-ms = <60>;")
    parser.process_line("            bindings = <")
    parser.process_line("                &macro_press &kp LSHIFT,")
    parser.process_line("                &macro_tap &kp A &kp B &kp C,")
    parser.process_line("                &macro_release &kp LSHIFT")
    parser.process_line("            >;")
    parser.process_line("        };")
    parser.process_line("    };")

    assert len(parser.macros) == 1
    macro = parser.macros[0]
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
        assert macro.bindings[i + 1].action == "macro_tap"
        assert macro.bindings[i + 1].behavior == "kp"
        assert macro.bindings[i + 1].param == key

    # Check release binding
    assert macro.bindings[4].action == "macro_release"
    assert macro.bindings[4].behavior == "kp"
    assert macro.bindings[4].param == "LSHIFT"


def test_invalid_macro_settings():
    """Test handling of invalid macro settings."""
    parser = MacroParser()

    parser.process_line("/ {")
    parser.process_line("    macros {")
    parser.process_line("        test: test {")

    # Test invalid wait-ms format
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            wait-ms = 30;")
    assert "Invalid setting format" in str(exc_info.value)

    # Test invalid tap-ms value
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            tap-ms = <-10>;")
    assert "Setting value must be positive" in str(exc_info.value)

    # Test invalid binding format
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            bindings = kp A;")
    assert "Invalid bindings line" in str(exc_info.value)


def test_nested_macros():
    """Test that nested macro blocks are not allowed."""
    parser = MacroParser()

    parser.process_line("/ {")
    parser.process_line("    macros {")

    with pytest.raises(ParserError) as exc_info:
        parser.process_line("        macros {")
    assert "Nested macros blocks are not allowed" in str(exc_info.value)


def test_parameterized_macro():
    """Test parsing a parameterized macro."""
    parser = MacroParser()

    parser.process_line("/ {")
    parser.process_line("    macros {")
    parser.process_line("        param_macro: param_macro {")
    parser.process_line("            compatible = ")
    parser.process_line("                \"zmk,behavior-macro-one-param\";")
    parser.process_line("            #binding-cells = <1>;")
    parser.process_line("            bindings = <")
    parser.process_line("                &macro_param_1to1,")
    parser.process_line("                &kp MACRO_PLACEHOLDER")
    parser.process_line("            >;")
    parser.process_line("        };")
    parser.process_line("    };")

    assert len(parser.macros) == 1
    macro = parser.macros[0]
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
