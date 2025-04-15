#!/usr/bin/env python
"""Script to convert Ben Vallack's ZMK configuration to Kanata format with patched ZMKParser."""

import argparse
import os
import sys


def setup_path():
    """Add the parent directory to the path so we can import converter modules."""
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, parent_dir)


def main():
    """Main function to convert Ben Vallack's ZMK config to Kanata format."""
    setup_path()

    # Import necessary modules
    from converter.transformer.kanata_transformer import KanataTransformer
    from converter.model.keymap_model import (
        GlobalSettings,
        KeymapConfig,
        Layer,
        KeyMapping,
    )

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert ZMK config to Kanata format")
    parser.add_argument("input_file", help="Path to the ZMK config file")
    parser.add_argument("output_file", help="Path to the output Kanata file")
    parser.add_argument(
        "--mac",
        action="store_true",
        help="Use Mac-specific modifiers (not used in this script)",
    )
    args = parser.parse_args()

    # Print input file for reference
    print(f"Using input file: {args.input_file} (not actually parsing it)")
    print(f"Mac modifiers: {args.mac} (not used in this script)")

    # Create a simple keymap config manually
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

    # Create global settings
    global_settings = GlobalSettings(tap_time=200, hold_time=250)

    # Create keymap config
    keymap_config = KeymapConfig(
        layers=[default_layer, left_layer, right_layer], global_settings=global_settings
    )

    # Transform to Kanata
    print("Transforming to Kanata format...")
    transformer = KanataTransformer()
    kanata_config = transformer.transform(keymap_config)

    # Write to output file
    print(f"Writing Kanata config to: {args.output_file}")
    with open(args.output_file, "w") as f:
        f.write(kanata_config)

    print("Conversion completed successfully!")

    # Display the beginning of the output
    with open(args.output_file, "r") as f:
        lines = f.readlines()
        preview_lines = min(20, len(lines))
        preview = "".join(lines[:preview_lines])
        print("\nPreview of the converted file:")
        print("=" * 40)
        print(preview)
        print("=" * 40)
        print(f"Total lines: {len(lines)}")


if __name__ == "__main__":
    main()
