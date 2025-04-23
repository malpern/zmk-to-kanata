"""End-to-end tests for ZMK sticky key behavior conversion."""

import pytest
from converter.cli import main as cli_main  # Use cli_main for direct arg list passing


@pytest.mark.e2e
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

    # Call cli_main which handles arg list directly
    args = [str(zmk_file), "-o", str(kanata_file)]
    exit_code = cli_main(args)

    assert exit_code == 0
    assert kanata_file.exists()
    # TODO: Add specific assertions for sticky key output once format is finalized


@pytest.mark.e2e
def test_sticky_key_advanced(temp_test_dir):
    """Test advanced sticky key features."""
    # Load the test fixture
    # Use a known good fixture if available, otherwise create minimal one
    zmk_content = """#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
/ {
    behaviors { /* ... complex sticky key setup ... */ };
    keymap { /* ... bindings using complex sticky keys ... */ };
};"""  # Placeholder: Replace with actual fixture content or creation
    zmk_file = temp_test_dir / "sticky_advanced.dtsi"
    # If using real fixture: fixture_dir = Path(__file__).parent.parent / "fixtures" / "zmk"; zmk_file = fixture_dir / "test_sticky_keys.dtsi"
    zmk_file.write_text(zmk_content)  # Remove if using real fixture

    kanata_file = temp_test_dir / "sticky_advanced.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    exit_code = cli_main(args)

    assert exit_code == 0
    assert kanata_file.exists()
    # Add assertions specific to the expected advanced sticky key output


@pytest.mark.e2e
def test_sticky_key_errors(temp_test_dir):
    """Test error handling for invalid sticky key configurations."""
    zmk_content = """#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    behaviors {
        sk: sticky_key {
            compatible = "zmk,behavior-sticky-key";
            #binding-cells = <1>;
            bindings = <&kp>; # Correct basic binding needed for behavior definition
            release-after-ms = <1000>;
        };
    };

    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &sk INVALID  &sk LALT   &sk # Should cause error during extraction/transform
            >;
        };
    };
};"""

    zmk_file = temp_test_dir / "sticky_errors.dtsi"
    zmk_file.write_text(zmk_content)

    kanata_file = temp_test_dir / "sticky_errors.kbd"

    # Expect a non-zero exit code due to conversion error
    args = [str(zmk_file), "-o", str(kanata_file)]
    exit_code = cli_main(args)
    assert exit_code != 0
    # Optionally check stderr for specific error message
