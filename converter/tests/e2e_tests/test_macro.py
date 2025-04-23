"""End-to-end tests for macro support."""

import pytest
from click.testing import CliRunner
from converter.cli import main as cli_main


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.e2e
def test_basic_macro_conversion(runner, tmp_path):
    """Test converting a ZMK file with basic macros."""
    zmk_content = """
    #include <behaviors.dtsi>
    #include <dt-bindings/zmk/keys.h>
    / {
        behaviors {
            macro_test: macro_test {
                compatible = "zmk,behavior-macro";
                label = "MACRO_TEST";
                #binding-cells = <0>;
                wait-ms = <30>;
                tap-ms = <30>;
                bindings = <&macro_tap &kp A &kp B>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&macro_test>;
            };
        };
    };
    """
    zmk_file = tmp_path / "basic_macro.dtsi"
    zmk_file.write_text(zmk_content)
    kanata_file = tmp_path / "basic_macro.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(defmacro macro_test" in content
    assert "tap a" in content
    assert "tap b" in content
    assert "(deflayer default_layer" in content
    assert "(macro macro_test)" in content


@pytest.mark.e2e
def test_complex_macro_conversion(runner, tmp_path):
    """Test converting a ZMK file with complex macros (press/release/wait)."""
    zmk_content = """
    #include <behaviors.dtsi>
    #include <dt-bindings/zmk/keys.h>
    / {
        behaviors {
            complex_macro: complex_macro {
                compatible = "zmk,behavior-macro";
                label = "COMPLEX_MACRO";
                #binding-cells = <0>;
                bindings = <&macro_press &kp LCTRL &macro_tap &kp C &macro_release &kp LCTRL &macro_wait_time 100 &macro_tap &kp V>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&complex_macro>;
            };
        };
    };
    """
    zmk_file = tmp_path / "complex_macro.dtsi"
    zmk_file.write_text(zmk_content)
    kanata_file = tmp_path / "complex_macro.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(defmacro complex_macro" in content
    assert "press lctl" in content
    assert "tap c" in content
    assert "release lctl" in content
    assert "delay 100" in content
    assert "tap v" in content
    assert "(deflayer default_layer" in content
    assert "(macro complex_macro)" in content


@pytest.mark.e2e
def test_parameterized_macro_conversion(runner, tmp_path):
    """Test converting a ZMK file with parameterized macros."""
    # Note: Parameterized macros in ZMK often rely on C preprocessor.
    # This test uses a basic DTS definition for simplicity.
    zmk_content = """
    #include <behaviors.dtsi>
    #include <dt-bindings/zmk/keys.h>
    / {
        macros {
            // Example from ZMK docs, actual implementation might vary
            param_macro: param_macro {
                compatible = "zmk,behavior-macro-two-param";
                label = "PARAM_MACRO";
                #binding-cells = <2>; // Expects two parameters
                bindings = <&macro_tap &kp MACRO_PLACEHOLDER_1 &macro_tap &kp MACRO_PLACEHOLDER_2>;
                param1-transform = <&kp MACRO_PLACEHOLDER_1>;
                param2-transform = <&kp MACRO_PLACEHOLDER_2>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&param_macro(A B)>; // Using the macro with params
            };
        };
    };
    """
    zmk_file = tmp_path / "param_macro.dtsi"
    zmk_file.write_text(zmk_content)
    kanata_file = tmp_path / "param_macro.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    # Check for macro definition and usage with parameters
    # Actual Kanata syntax for parameterized macros might need specific handling.
    # This is a basic check assuming simple transformation.
    assert "(defmacro param_macro" in content  # Check definition (name might vary)
    # Check usage with parameters passed
    assert "(macro param_macro a b)" in content
