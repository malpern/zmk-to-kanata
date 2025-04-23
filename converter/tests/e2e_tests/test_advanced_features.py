"""End-to-end tests for advanced ZMK features."""

import pytest
from click.testing import CliRunner
from converter.cli import main as cli_main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.e2e
def test_multi_layer_with_hold_tap(runner, tmp_path):
    """Test a multi-layer keymap with hold-tap behaviors."""
    zmk_content = """
    #include <behaviors.dtsi>
    #include <dt-bindings/zmk/keys.h>
    / {
        behaviors {
            hm_l: homerow_mods_left {
                compatible = "zmk,behavior-hold-tap";
                #binding-cells = <2>;
                tapping-term-ms = <200>;
                flavor = "tap-preferred";
                bindings = <&kp>, <&kp>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            base_layer {
                bindings = <&kp Q &hm_l LCTRL A &mo 1>;
            };
            nav_layer {
                bindings = <&kp HOME &trans &trans>;
            };
        };
    };
    """
    zmk_file = tmp_path / "multilayer_ht.dtsi"
    zmk_file.write_text(zmk_content)
    kanata_file = tmp_path / "multilayer_ht.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    # Check for hold-tap alias definition
    assert "(defalias hm_l_lctl_a" in content
    # Check for base layer content
    assert "(deflayer base_layer" in content
    assert "q @hm_l_lctl_a (layer nav_layer)" in content
    # Check for nav layer content
    assert "(deflayer nav_layer" in content
    assert "home _ _" in content


@pytest.mark.e2e
def test_multi_layer_with_custom_behaviors(runner, tmp_path):
    """Test keymap with multiple layers and custom behaviors (macros)."""
    zmk_content = """
    #include <behaviors.dtsi>
    #include <dt-bindings/zmk/keys.h>
    / {
        behaviors {
            my_macro: my_macro {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <&macro_tap &kp X &kp Y>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default {
                bindings = <&kp A &my_macro &mo 1>;
            };
            layer_1 {
                bindings = <&kp N1 &kp N2 &trans>;
            };
        };
    };
    """
    zmk_file = tmp_path / "multilayer_macro.dtsi"
    zmk_file.write_text(zmk_content)
    kanata_file = tmp_path / "multilayer_macro.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    # Check for macro definition
    assert "(defmacro my_macro" in content
    assert "tap x" in content
    assert "tap y" in content
    # Check for default layer content
    assert "(deflayer default" in content
    assert "a (macro my_macro) (layer layer_1)" in content
    # Check for layer_1 content
    assert "(deflayer layer_1" in content
    assert "1 2 _" in content
