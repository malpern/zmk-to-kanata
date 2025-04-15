#!/usr/bin/env python
"""Adapter script to convert Ben Vallack's ZMK config to Kanata."""

from pathlib import Path
import tempfile
import os

# Import and patch GlobalSettings to have default values
from converter.model.keymap_model import GlobalSettings

# Store original GlobalSettings class
OriginalGlobalSettings = GlobalSettings


# Create a new GlobalSettings class with default values
class PatchedGlobalSettings:
    def __new__(cls, tap_time=200, hold_time=250):
        return OriginalGlobalSettings(tap_time=tap_time, hold_time=hold_time)


# Patch the GlobalSettings class
from converter.model import keymap_model

keymap_model.GlobalSettings = PatchedGlobalSettings

# Ben's config
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
                &trans &kp F  &kp U    &kp Z  &kp BKSP
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

# Create a temporary file with Ben's config
temp_dir = tempfile.mkdtemp()
input_file = os.path.join(temp_dir, "ben_vallack_config.dtsi")
with open(input_file, "w") as f:
    f.write(ben_config)

# Run the converter
output_file = "ben_vallack_output.kbd"
from converter.main import main
import sys

# Override sys.argv
original_argv = sys.argv
sys.argv = [
    "converter",
    input_file,
    "-o",
    output_file,
    "--mac",  # Use Mac-specific modifiers
]

try:
    main()
    print(f"Conversion complete! Output saved to {output_file}")
except Exception as e:
    print(f"Error during conversion: {e}")
finally:
    # Restore sys.argv
    sys.argv = original_argv
