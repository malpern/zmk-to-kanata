"""End-to-end test for Ben Vallack's ZMK configuration."""

import os
from pathlib import Path

import pytest

from converter.zmk_to_kanata import convert_zmk_to_kanata


def get_test_file_path(filename):
    """Get the absolute path to a test file."""
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    return current_dir / ".." / "test_data" / filename


def test_ben_vallack_config_conversion():
    """Test converting Ben Vallack's ZMK configuration."""
    # Load Ben's config from file
    ben_config_path = Path("ben_vallack_config.dtsi")

    # If the file doesn't exist in the current directory, try to find it in the test data
    if not ben_config_path.exists():
        try:
            ben_config_path = get_test_file_path("ben_vallack_config.dtsi")
        except (FileNotFoundError, OSError):
            # If still not found, create a sample for testing
            ben_config = """
/ {
    global {
        tap-time = <200>;
        hold-time = <250>;
    };

    behaviors {
        hm: homerow_mods {
            compatible = "zmk,behavior-hold-tap";
            label = "HOMEROW_MODS";
            #binding-cells = <2>;
            tapping-term-ms = <200>;
            quick_tap_ms = <0>;
            flavor = "tap-preferred";
            bindings = <&kp>, <&kp>;
        };
        hs: homerow_shifts {
            compatible = "zmk,behavior-hold-tap";
            label = "HOMEROW_SHIFTS";
            #binding-cells = <2>;
            tapping-term-ms = <150>;
            quick_tap_ms = <0>;
            flavor = "balanced";
            bindings = <&kp>, <&kp>;
        };
        td: tapdance {
            compatible = "zmk,behavior-hold-tap";
            label = "TAPDANCE";
            #binding-cells = <2>;
            tapping-term-ms = <150>;
            quick_tap_ms = <0>;
            flavor = "tap-preferred";
            bindings = <&kp>, <&kp>;
        };
    };

    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp TAB &kp C &kp L &kp M &trans
                &trans &kp F  &kp U    &kp Z  &kp BSPC
                &kp I &hm LCTL S &hm LALT R &hm LGUI T &trans
                &trans  &hm RGUI N &hm RALT K &hm RCTL A &kp O
                &hs LSHIFT Q &kp V &kp W &kp D &mt LC(LS(LALT)) SPC
                &kp E &kp H  &kp Y &td EXCL DOT &hs RSHIFT X
                                &mt LC(LS(LALT)) SPC &trans
                                &trans &kp E
            >;
        };

        left_layer {
            bindings = <
                &trans  &kp ATSN   &td LC(LG(LS(N4))) LS(N3) &kp DLLR &trans
                &trans &kp LS(COMMA) &kp LS(DOT) &kp CARET &trans
                &kp TAB &hm LCTL EQUAL &hm LALT LA(RBKT) &hm LGUI LA(LS(RBKT)) &trans
                &trans &hm RGUI LBRC &hm RALT RBRC &hm RCTL PIPE &kp AMPS
                &hs LSHIFT TILDE &kp GRAVE &kp LA(LBKT) &kp LA(LS(LBKT)) &to 0
                &to 2 &kp LPRN &kp RPRN &kp RBKT &kp RSHIFT
                                &to 0 &trans
                                &trans &to 2
            >;
        };

        right_layer {
            bindings = <
                &trans &kp C_PP &kp C_PREV &kp C_NEXT &trans
                &trans &kp N7 &kp N8 &kp N9 &trans
                &kp TAB &trans &hm LALT C_VOL_DN &hm LGUI C_VOL_UP &trans
                &trans &hm RGUI N4 &kp N5 &kp N6 &kp EQUAL
                &hs LSHIFT PRCNT &kp PRCNT &kp SLASH &kp STAR &to 0
                &trans &kp N1 &kp N2 &td DOT N3 &kp MINUS
                                &to 0 &trans
                                &trans &trans
            >;
        };
    };
};
            """
        else:
            with open(ben_config_path, "r") as f:
                ben_config = f.read()
    else:
        with open(ben_config_path, "r") as f:
            ben_config = f.read()

    # Convert to Kanata format
    kanata_config, metadata = convert_zmk_to_kanata(zmk_content=ben_config, is_mac=True)

    # Verify the conversion was successful
    assert kanata_config, "Conversion should produce non-empty result"
    assert metadata["layer_count"] == 3, "Should have 3 layers"

    # Check for specific elements in the output
    assert "deflayer default" in kanata_config, "Default layer should be present"
    assert "deflayer left" in kanata_config, "Left layer should be present"
    assert "deflayer right" in kanata_config, "Right layer should be present"

    # Specific keys that should be present
    assert "tab" in kanata_config.lower(), "TAB key should be present"
    assert "bspc" in kanata_config.lower(), "Backspace key should be present"

    # Verify tap-hold behavior for homerow mods
    # This may need to be adjusted based on your actual implementation
    assert (
        "tap-hold" in kanata_config.lower() or "@tap_hold" in kanata_config.lower()
    ), "Tap-hold behavior should be present"
