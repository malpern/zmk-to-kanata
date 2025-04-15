#!/usr/bin/env python
"""Script to convert Ben Vallack's ZMK config to Kanata format."""

import os
import sys
import tempfile

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

# Now patch the ZMKParser for string input
from converter.parser.zmk_parser import ZMKParser
from pathlib import Path

# Store original parse method
original_parse = ZMKParser.parse


def patched_parse(self, file_path):
    """Patched parser that can handle string content."""
    # If a Path object is provided, convert it to a string
    if isinstance(file_path, Path):
        file_path = str(file_path)

    # If file_path is a string and exists as a file, read it
    if isinstance(file_path, str):
        try:
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
            else:
                # Assume it's already content
                content = file_path
        except Exception:
            # If any error occurs, assume it's content
            content = file_path
    else:
        # Should not happen, but just in case
        content = str(file_path)

    # Initialize the state
    self.layers = []
    self.current_layer = None
    self.state = self.ParserState.INITIAL
    self.errors = []
    self.global_settings_parser = self.GlobalSettingsParser()
    self.binding_parser = self.BindingParser()

    # Process each line
    for i, line in enumerate(content.splitlines()):
        try:
            self._parse_line(line.rstrip())
        except Exception as e:
            self.errors.append((i + 1, str(e)))

    # Finish parsing
    if self.current_layer is not None:
        self._finish_current_layer()

    # Create global settings
    global_settings = self.global_settings_parser.finish()

    # Create and return keymap config
    return self.KeymapConfig(layers=self.layers, global_settings=global_settings)


# Apply the monkey patch
ZMKParser.parse = patched_parse

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

# Now also patch the convert_zmk_to_kanata function
from converter.zmk_to_kanata import convert_zmk_to_kanata
from typing import Dict, Any, Optional, Tuple

# Store original function
original_convert = convert_zmk_to_kanata


def patched_convert(
    zmk_content: str,
    output_path: Optional[str] = None,
    error_manager=None,
    is_mac: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """Patched conversion function that works with string content."""
    try:
        # Set up error manager
        from converter.error_handling import (
            ErrorManager,
            ErrorSeverity,
            get_error_manager,
            set_error_manager,
        )

        if error_manager:
            set_error_manager(error_manager)
        else:
            set_error_manager(ErrorManager())

        error_mgr = get_error_manager()

        try:
            # Parse ZMK keymap directly from content
            parser = ZMKParser()
            keymap_config = parser.parse(zmk_content)

            # Transform to Kanata format
            from converter.transformer.kanata_transformer import KanataTransformer

            transformer = KanataTransformer(is_mac=is_mac)
            kanata_layers = []

            for layer in keymap_config.layers:
                kanata_layer = transformer.transform_layer(layer)
                kanata_layers.append(kanata_layer)

            # Generate Kanata keymap
            source_keys = transformer.get_source_keys(keymap_config.layers)
            kanata_config = transformer.generate_kanata_keymap(
                source_keys, kanata_layers
            )

            # Write to file if output path is provided
            if output_path:
                with open(output_path, "w") as f:
                    f.write(kanata_config)
                output_msg = f"Successfully wrote Kanata config to {output_path}"
                error_mgr.add_error(
                    message=output_msg, source="converter", severity=ErrorSeverity.INFO
                )

            # Return the Kanata config and metadata
            metadata = {
                "layer_count": len(keymap_config.layers),
                "global_settings": keymap_config.global_settings,
                "errors": error_mgr.get_error_report(),
            }

            return kanata_config, metadata

        except Exception as e:
            error_mgr.add_error(
                message=f"Error during conversion: {str(e)}",
                source="converter",
                severity=ErrorSeverity.ERROR,
                exception=e,
                raise_immediately=True,
            )
            # This will never be reached due to raise_immediately=True
            return "", {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return "", {}


# Apply the second monkey patch
from converter.zmk_to_kanata import convert_zmk_to_kanata

convert_zmk_to_kanata = patched_convert

# Now run the conversion
try:
    # Set up output file
    output_file = "ben_vallack_output.kbd"

    # Convert directly
    kanata_config, metadata = convert_zmk_to_kanata(
        zmk_content=ben_config,
        output_path=output_file,
        is_mac=True,  # Use Mac-specific modifiers
    )

    print(f"Conversion complete! Output saved to {output_file}")

    # Display the beginning of the output
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            lines = f.readlines()
            preview = "".join(lines[:20])
            print("\nPreview of the converted file:")
            print("=" * 40)
            print(preview)
            print("=" * 40)
            print(f"Total lines: {len(lines)}")

except Exception as e:
    print(f"Error during conversion: {e}")
    if os.path.exists(output_file):
        print("\nPartial output:")
        with open(output_file, "r") as f:
            print(f.read())
