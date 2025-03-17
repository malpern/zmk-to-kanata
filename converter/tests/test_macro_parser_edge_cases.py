"""Tests for edge cases in the macro parser."""
import pytest

from converter.parser.macro_parser_v2 import MacroParser, ParserError


def test_complex_binding_formats():
    """Test parsing complex binding formats."""
    parser = MacroParser()

    parser.process_line("/ {")
    parser.process_line("    macros {")
    parser.process_line("        complex: complex {")
    parser.process_line("            bindings = <")
    parser.process_line("                &macro_press &kp LSHIFT,")
    parser.process_line("                &macro_tap &kp A &kp B &kp C,")
    parser.process_line("                &macro_release &kp LSHIFT,")
    parser.process_line(
        "                &macro_tap &kp EXCL &kp AT &kp HASH,"
    )
    parser.process_line("                &macro_press &kp LCTRL,")
    parser.process_line("                &macro_tap &kp N1 &kp N2 &kp N3,")
    parser.process_line("                &macro_release &kp LCTRL")
    parser.process_line("            >;")
    parser.process_line("        };")
    parser.process_line("    };")

    assert len(parser.macros) == 1
    macro = parser.macros[0]
    assert len(macro.bindings) == 13

    # Check modifier press/release pairs
    assert macro.bindings[0].action == "macro_press"
    assert macro.bindings[0].behavior == "kp"
    assert macro.bindings[0].param == "LSHIFT"

    # Check multiple taps after press
    for i, key in enumerate(["A", "B", "C"]):
        assert macro.bindings[i + 1].action == "macro_tap"
        assert macro.bindings[i + 1].behavior == "kp"
        assert macro.bindings[i + 1].param == key

    # Check special characters
    for i, key in enumerate(["EXCL", "AT", "HASH"]):
        # Start index for special chars
        idx = i + 5
        assert macro.bindings[idx].action == "macro_tap"
        assert macro.bindings[idx].behavior == "kp"
        assert macro.bindings[idx].param == key


def test_error_recovery():
    """Test error recovery scenarios."""
    parser = MacroParser()

    parser.process_line("/ {")
    parser.process_line("    macros {")

    # Test recovery from incomplete macro
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("        test: test {")
        parser.process_line("            bindings = <")
        parser.process_line("                &macro_tap &kp A")  # Missing comma
        parser.process_line("            >;")  # Force binding end
    assert "Invalid binding format" in str(exc_info.value)

    # Test recovery from missing semicolon
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            wait-ms = <30>")  # No semicolon
    assert "Invalid setting format" in str(exc_info.value)

    # Test recovery from unclosed setting
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            bindings = ")  # Unclosed
        parser.process_line("        };")
    assert "Unclosed setting" in str(exc_info.value)

    # Verify parser state is clean after errors
    assert parser.current_macro is None
    assert parser.in_bindings is False
    assert parser.current_setting is None
    assert parser.current_setting_value is None


def test_state_transitions():
    """Test state transitions and edge cases."""
    parser = MacroParser()

    # Test transitioning between different macro types
    parser.process_line("/ {")
    parser.process_line("    macros {")

    # Regular macro
    parser.process_line("        basic: basic {")
    parser.process_line("            bindings = <&macro_tap &kp A>;")
    parser.process_line("        };")

    # Parameterized macro
    parser.process_line("        param: param {")
    parser.process_line(
        '            compatible = "zmk,behavior-macro-one-param";'
    )
    parser.process_line("            #binding-cells = <1>;")
    parser.process_line("            bindings = <&macro_param_1to1>;")
    parser.process_line("        };")

    # Complex macro with nested settings
    parser.process_line("        complex: complex {")
    parser.process_line("            bindings = <")
    parser.process_line("                &macro_tap &kp A,")
    parser.process_line("                &macro_press &kp LSHIFT")
    parser.process_line("            >;")
    parser.process_line("            wait-ms = <30>;")  # Setting after bindings
    parser.process_line("        };")

    parser.process_line("    };")

    # Verify all macros were parsed correctly
    assert len(parser.macros) == 3

    # Check basic macro
    assert parser.macros[0].name == "basic"
    assert len(parser.macros[0].bindings) == 1

    # Check parameterized macro
    assert parser.macros[1].name == "param"
    assert parser.macros[1].param_count == 1
    assert len(parser.macros[1].bindings) == 1
    assert parser.macros[1].bindings[0].action == "macro_param_1to1"

    # Check complex macro
    assert parser.macros[2].name == "complex"
    assert len(parser.macros[2].bindings) == 2
    assert parser.macros[2].wait_ms == 30


def test_invalid_state_transitions():
    """Test invalid state transitions."""
    parser = MacroParser()

    # Test starting macro without macros block
    with pytest.raises(ParserError):
        parser.process_line("        test: test {")

    parser.process_line("/ {")
    parser.process_line("    macros {")

    # Test nested macro definitions
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("        outer: outer {")
        parser.process_line("            inner: inner {")
    assert "Already parsing a macro" in str(exc_info.value)

    # Test bindings without macro
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            bindings = <&macro_tap &kp A>;")
        parser.process_line("        };")  # Force end of block
    assert "No macro being parsed" in str(exc_info.value)

    # Test settings without macro
    with pytest.raises(ParserError) as exc_info:
        parser.process_line("            wait-ms = <30>;")
    assert "No macro being parsed" in str(exc_info.value)
