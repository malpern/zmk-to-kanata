"""End-to-end tests for ZMK sticky key behavior conversion."""

from pathlib import Path

from converter.cli import main


def test_sticky_key_basic(temp_test_dir):
    """Test basic sticky key conversion with modifiers."""
    zmk_content = """#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    behaviors {
        sk: sticky_key {
            compatible = "zmk,behavior-sticky-key";
            #binding-cells = <1>;
            bindings = <&kp>;
            release-after-ms = <1000>;
        };
    };

    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &sk LSHIFT  &sk LCTRL   &sk LALT
                &sk LGUI    &kp A       &kp B
            >;
        };
    };
};"""

    zmk_file = temp_test_dir / "sticky_basic.dtsi"
    zmk_file.write_text(zmk_content)

    kanata_file = temp_test_dir / "sticky_basic.kbd"

    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0

    content = kanata_file.read_text().lower()

    # Verify sticky modifiers are converted correctly
    assert "sticky-lsft" in content
    assert "sticky-lctl" in content
    assert "sticky-lalt" in content
    assert "sticky-lmet" in content

    # Verify regular keys remain unchanged
    assert "a" in content
    assert "b" in content


def test_sticky_key_advanced(temp_test_dir):
    """Test advanced sticky key features."""
    # Load the test fixture
    fixture_dir = Path(__file__).parent.parent / "fixtures" / "zmk"
    fixture_path = fixture_dir / "test_sticky_keys.dtsi"
    kanata_file = temp_test_dir / "sticky_advanced.kbd"

    exit_code = main([str(fixture_path), str(kanata_file)])
    assert exit_code == 0

    content = kanata_file.read_text().lower()

    # Verify sticky modifiers
    assert "sticky-lsft" in content
    assert "sticky-lctl" in content
    assert "sticky-lalt" in content
    assert "sticky-lmet" in content

    # Verify sticky function keys
    assert "sticky-f1" in content
    assert "sticky-f2" in content
    assert "sticky-f3" in content

    # Verify layer structure
    assert "(deflayer default" in content
    assert "(deflayer function" in content

    # Verify transparent keys
    assert "_" in content  # Kanata uses _ for transparent keys


def test_sticky_key_errors(temp_test_dir):
    """Test error handling for invalid sticky key configurations."""
    zmk_content = """#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    behaviors {
        sk: sticky_key {
            compatible = "zmk,behavior-sticky-key";
            #binding-cells = <1>;
            bindings = <&invalid_behavior>;  # Invalid binding
            release-after-ms = <1000>;
        };
    };

    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &sk INVALID  &sk 123456   &sk
            >;
        };
    };
};"""

    zmk_file = temp_test_dir / "sticky_errors.dtsi"
    zmk_file.write_text(zmk_content)

    kanata_file = temp_test_dir / "sticky_errors.kbd"

    # Should return non-zero exit code for invalid configuration
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code != 0
