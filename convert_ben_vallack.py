#!/usr/bin/env python
"""Script to convert Ben Vallack's ZMK configuration to Kanata format."""

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

    # Import converter modules after path setup
    from converter.zmk_to_kanata import convert_zmk_to_kanata

    parser = argparse.ArgumentParser(description="Convert ZMK config to Kanata format")
    parser.add_argument("input_file", help="Path to the ZMK config file")
    parser.add_argument("output_file", help="Path to the output Kanata file")
    parser.add_argument("--mac", action="store_true", help="Use Mac-specific modifiers")
    args = parser.parse_args()

    # Read the ZMK config file
    print(f"Reading ZMK config file: {args.input_file}")
    with open(args.input_file, "r") as f:
        zmk_content = f.read()

    # Convert ZMK to Kanata
    print("Converting to Kanata format...")
    kanata_config, _ = convert_zmk_to_kanata(zmk_content=zmk_content, is_mac=args.mac)

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
