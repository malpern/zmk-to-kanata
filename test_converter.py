#!/usr/bin/env python
"""Test script for testing the converter directly."""

import os
import sys

# Add the parent directory to the path so we can import converter modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from converter.model.keymap_model import GlobalSettings, KeymapConfig, Layer, KeyMapping
from converter.transformer.kanata_transformer import KanataTransformer

# Create a sample keymap config with KeyMapping objects
layers = []


# Helper function to convert strings to KeyMapping objects
def create_key_row(keys):
    return [KeyMapping(key=k) for k in keys]


# Default layer
default_layer = Layer(
    name="default",
    bindings=[
        KeyMapping(key="TAB"),
        KeyMapping(key="C"),
        KeyMapping(key="L"),
        KeyMapping(key="M"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="F"),
        KeyMapping(key="U"),
        KeyMapping(key="Z"),
        KeyMapping(key="BSPC"),
        KeyMapping(key="I"),
        KeyMapping(key="S"),
        KeyMapping(key="R"),
        KeyMapping(key="T"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="N"),
        KeyMapping(key="K"),
        KeyMapping(key="A"),
        KeyMapping(key="O"),
        KeyMapping(key="Q"),
        KeyMapping(key="V"),
        KeyMapping(key="W"),
        KeyMapping(key="D"),
        KeyMapping(key="SPACE"),
        KeyMapping(key="E"),
        KeyMapping(key="H"),
        KeyMapping(key="Y"),
        KeyMapping(key="DOT"),
        KeyMapping(key="X"),
    ],
)
layers.append(default_layer)

# Left layer
left_layer = Layer(
    name="left",
    bindings=[
        KeyMapping(key="TRANS"),
        KeyMapping(key="AT"),
        KeyMapping(key="HASH"),
        KeyMapping(key="DLLR"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="NONE"),
        KeyMapping(key="NONE"),
        KeyMapping(key="CARET"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TAB"),
        KeyMapping(key="EQUAL"),
        KeyMapping(key="LBKT"),
        KeyMapping(key="RBKT"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="NONE"),
        KeyMapping(key="NONE"),
        KeyMapping(key="PIPE"),
        KeyMapping(key="AMPS"),
        KeyMapping(key="TILDE"),
        KeyMapping(key="GRAVE"),
        KeyMapping(key="LPAR"),
        KeyMapping(key="RPAR"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="LPAR"),
        KeyMapping(key="RPAR"),
        KeyMapping(key="RBKT"),
        KeyMapping(key="RSHIFT"),
    ],
)
layers.append(left_layer)

# Right layer
right_layer = Layer(
    name="right",
    bindings=[
        KeyMapping(key="TRANS"),
        KeyMapping(key="C_PP"),
        KeyMapping(key="C_PREV"),
        KeyMapping(key="C_NEXT"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="N7"),
        KeyMapping(key="N8"),
        KeyMapping(key="N9"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TAB"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="C_VOL_DN"),
        KeyMapping(key="C_VOL_UP"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="N4"),
        KeyMapping(key="N5"),
        KeyMapping(key="N6"),
        KeyMapping(key="EQUAL"),
        KeyMapping(key="PRCNT"),
        KeyMapping(key="PRCNT"),
        KeyMapping(key="FSLH"),
        KeyMapping(key="STAR"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="TRANS"),
        KeyMapping(key="N1"),
        KeyMapping(key="N2"),
        KeyMapping(key="N3"),
        KeyMapping(key="MINUS"),
    ],
)
layers.append(right_layer)

# Create global settings
global_settings = GlobalSettings(tap_time=200, hold_time=250)

# Create keymap config
keymap_config = KeymapConfig(layers=layers, global_settings=global_settings)

# Transform to Kanata
transformer = KanataTransformer()
kanata_config = transformer.transform(keymap_config)

# Write to file
output_file = "test_output.kbd"
with open(output_file, "w") as f:
    f.write(kanata_config)

print(f"Successfully wrote Kanata config to {output_file}")

# Display the beginning of the output
with open(output_file, "r") as f:
    lines = f.readlines()
    preview = "".join(lines[:20])
    print("\nPreview of the converted file:")
    print("=" * 40)
    print(preview)
    print("=" * 40)
    print(f"Total lines: {len(lines)}")
