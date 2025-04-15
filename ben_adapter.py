#!/usr/bin/env python
"""Adapter script to convert Ben Vallack's ZMK config to Kanata."""

import sys
import tempfile
from pathlib import Path

# Write Ben's config to a temporary file
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

# Create a modified ZMKParser that can handle this config
from converter.parser.zmk_parser import ZMKParser

# Monkey patch the ZMKParser's parse method to accept string content
original_parse = ZMKParser.parse


def patched_parse(self, content_or_path):
    """Handle both file paths and string content."""
    if isinstance(content_or_path, (str, Path)) and "\n" in str(content_or_path):
        # This is content, not a path
        lines = content_or_path.splitlines()

        # Initialize parser state
        self.layers = []
        self.current_layer = None
        self.state = self.ParserState.INITIAL
        self.errors = []
        self.global_settings_parser = self.GlobalSettingsParser()

        # Process each line
        for i, line in enumerate(lines):
            try:
                self._parse_line(line.rstrip())
            except Exception as e:
                self.errors.append((i + 1, str(e)))

        # Finish parsing and create the keymap config
        if self.current_layer is not None:
            self._finish_current_layer()

        global_settings = self.global_settings_parser.finish()
        return self.KeymapConfig(layers=self.layers, global_settings=global_settings)
    else:
        # This is a path, use the original method
        if isinstance(content_or_path, str):
            content_or_path = Path(content_or_path)
        with open(content_or_path, "r") as f:
            content = f.read()
        return patched_parse(self, content)


# Apply the monkey patch
ZMKParser.parse = patched_parse

# Convert the config
from converter.zmk_to_kanata import convert_zmk_to_kanata
from converter.error_handling import ErrorManager

error_manager = ErrorManager(verbose=True)
kanata_config, metadata = convert_zmk_to_kanata(
    zmk_content=ben_config,
    output_path="ben_vallack_output.kbd",
    error_manager=error_manager,
    is_mac=True,  # Use Mac-specific modifiers
)

print("Conversion complete! Output saved to ben_vallack_output.kbd")
