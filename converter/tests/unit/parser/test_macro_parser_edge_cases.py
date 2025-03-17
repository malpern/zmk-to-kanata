"""Tests for edge cases in the macro parser."""
import pytest
from converter.parser.macro_parser_v2 import ParserError


def test_complex_binding_formats(macro_parser):
    """Test parsing complex binding formats."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")
    macro_parser.process_line("        complex: complex {")
    macro_parser.process_line("            bindings = <")
    macro_parser.process_line("                &macro_press &kp LSHIFT,")
    macro_parser.process_line("                &macro_tap &kp A &kp B &kp C,")
    macro_parser.process_line("                &macro_release &kp LSHIFT,")
    macro_parser.process_line(
        "                &macro_tap &kp EXCL &kp AT &kp HASH,"
    )
    macro_parser.process_line("                &macro_press &kp LCTRL,")
    macro_parser.process_line(
        "                &macro_tap &kp N1 &kp N2 &kp N3,"
    )
    macro_parser.process_line("                &macro_release &kp LCTRL")
    macro_parser.process_line("            >;")
    macro_parser.process_line("        };")
    macro_parser.process_line("    };")

    assert len(macro_parser.macros) == 1
    macro = macro_parser.macros[0]
    assert len(macro.bindings) == 13

    # Check modifier press/release pairs
    assert macro.bindings[0].action == "macro_press"
    assert macro.bindings[0].behavior == "kp"
    assert macro.bindings[0].param == "LSHIFT"

    # Check multiple taps after press
    for i, key in enumerate(["A", "B", "C"]):
        binding = macro.bindings[i + 1]
        assert binding.action == "macro_tap"
        assert binding.behavior == "kp"
        assert binding.param == key

    # Check special characters
    for i, key in enumerate(["EXCL", "AT", "HASH"]):
        binding = macro.bindings[i + 5]  # Start index for special chars
        assert binding.action == "macro_tap"
        assert binding.behavior == "kp"
        assert binding.param == key


def test_error_recovery(macro_parser):
    """Test error recovery scenarios."""
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")

    # Test recovery from incomplete macro
    with pytest.raises(ParserError) as exc_info:
        macro_parser.process_line("        test: test {")
        macro_parser.process_line("            bindings = <")
        macro_parser.process_line("                &macro_tap &kp A")  # No comma
        macro_parser.process_line("            >;")  # Force binding end
    assert "Invalid binding format" in str(exc_info.value)

    # Test recovery from missing semicolon
    with pytest.raises(ParserError) as exc_info:
        macro_parser.process_line("            wait-ms = <30>")  # No semicolon
    assert "Invalid setting format" in str(exc_info.value)

    # Test recovery from unclosed setting
    with pytest.raises(ParserError) as exc_info:
        macro_parser.process_line("            bindings = ")  # Unclosed
        macro_parser.process_line("        };")
    assert "Unclosed setting" in str(exc_info.value)

    # Verify parser state is clean after errors
    assert macro_parser.current_macro is None
    assert macro_parser.in_bindings is False
    assert macro_parser.current_setting is None
    assert macro_parser.current_setting_value is None


def test_state_transitions(macro_parser):
    """Test state transitions and edge cases."""
    # Test transitioning between different macro types
    macro_parser.process_line("/ {")
    macro_parser.process_line("    macros {")

    # Regular macro
    macro_parser.process_line("        basic: basic {")
    macro_parser.process_line("            bindings = <&macro_tap &kp A>;")
    macro_parser.process_line("        };")

    # Parameterized macro
    macro_parser.process_line("        param: param {")
    macro_parser.process_line(
        '            compatible = "zmk,behavior-macro-one-param";'
    )
    macro_parser.process_line("            #binding-cells = <1>;")
    macro_parser.process_line("            bindings = <&macro_param_1to1>;")
    macro_parser.process_line("        };")

    # Complex macro with nested settings
    macro_parser.process_line("        complex: complex {")
    macro_parser.process_line("            bindings = <")
    macro_parser.process_line("                &macro_tap &kp A,")
    macro_parser.process_line("                &macro_press &kp LSHIFT")
    macro_parser.process_line("            >;")
    macro_parser.process_line("            wait-ms = <30>;")  # After bindings
    macro_parser.process_line("        };")

    macro_parser.process_line("    };")

    # Verify all macros were parsed correctly
    assert len(macro_parser.macros) == 3

    # Check basic macro
    assert macro_parser.macros[0].name == "basic"
    assert len(macro_parser.macros[0].bindings) == 1

    # Check parameterized macro
    assert macro_parser.macros[1].name == "param"
    assert macro_parser.macros[1].param_count == 1
    assert len(macro_parser.macros[1].bindings) == 1
    assert macro_parser.macros[1].bindings[0].action == "macro_param_1to1"

    # Check complex macro
    assert macro_parser.macros[2].name == "complex"
    assert len(macro_parser.macros[2].bindings) == 2
    assert macro_parser.macros[2].wait_ms == 30


@pytest.mark.parametrize("invalid_state,error_msg", [
    ("test: test {", "No macros block"),
    ("inner: inner {", "Already parsing a macro"),
    ("bindings = <&macro_tap &kp A>;", "No macro being parsed"),
    ("wait-ms = <30>;", "No macro being parsed"),
])
def test_invalid_state_transitions(macro_parser, invalid_state, error_msg):
    """Test invalid state transitions."""
    # Setup initial state if needed
    if "Already parsing a macro" in error_msg:
        macro_parser.process_line("/ {")
        macro_parser.process_line("    macros {")
        macro_parser.process_line("        outer: outer {")

    with pytest.raises(ParserError) as exc_info:
        macro_parser.process_line(f"        {invalid_state}")
    assert error_msg in str(exc_info.value)
