"""Main module for the ZMK to Kanata converter."""

import argparse
import sys
from pathlib import Path
from typing import List

from .layer_parser import LayerParser
from .layer_transformer import LayerTransformer, KanataLayer


def generate_kanata_keymap(layers: List[KanataLayer]) -> str:
    """Generate a Kanata keymap configuration from a list of layers.

    Args:
        layers: List of KanataLayer objects

    Returns:
        String containing the complete Kanata keymap configuration
    """
    kanata_config = []

    # Add header comments
    kanata_config.extend([
        ";; ZMK to Kanata Configuration",
        ";; Generated automatically - DO NOT EDIT",
        "",
        ";; Global settings",
        "(defvar tap-time 200)",
        "(defvar hold-time 250)",
        ""
    ])

    # Add layers
    for i, layer in enumerate(layers):
        # Add layer definition
        kanata_config.append(f"(deflayer {layer.name}")
        # Add key rows with proper spacing
        for row in layer.keys:
            kanata_config.append("  " + " ".join(row))
        kanata_config.append(")")
        # Add empty line between layers, but not after the last one
        if i < len(layers) - 1:
            kanata_config.append("")

    # Ensure file ends with a newline
    kanata_config.append("")

    return "\n".join(kanata_config)


def convert_keymap(input_file: Path, output_file: Path) -> None:
    """Convert a ZMK keymap file to Kanata format.

    Args:
        input_file: Path to the input ZMK keymap file
        output_file: Path where the Kanata config will be written

    Raises:
        FileNotFoundError: If input_file doesn't exist
        ValueError: If input file format is invalid
        OSError: If output file cannot be written
        Exception: For other unexpected errors
    """
    try:
        content = input_file.read_text()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")

    layer_parser = LayerParser()
    try:
        layers = layer_parser.parse_zmk_file(content)
    except ValueError as e:
        raise ValueError(f"Invalid input file format: {e}")

    transformer = LayerTransformer()
    kanata_layers = [
        transformer.transform_layer(layer)
        for layer in layers
    ]

    output = generate_kanata_keymap(kanata_layers)
    try:
        output_file.write_text(output)
    except OSError as e:
        raise OSError(f"Error writing output file: {e}")
    except Exception as e:
        raise Exception(f"Error writing output file: {e}")


def main():
    """Main entry point for the converter."""
    parser = argparse.ArgumentParser(
        description='Convert ZMK keymap to Kanata keymap'
    )
    parser.add_argument(
        'input_file',
        help='Path to input ZMK keymap file'
    )
    parser.add_argument(
        'output_file',
        help='Path to output Kanata keymap file'
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            content = f.read()

        layer_parser = LayerParser()
        try:
            layers = layer_parser.parse_zmk_file(content)
        except ValueError as e:
            print(f"Error parsing input file: {e}", file=sys.stderr)
            return 2

        # Create a keymap config with the parsed layers
        from .model.keymap_model import GlobalSettings, KeymapConfig
        config = KeymapConfig(
            global_settings=GlobalSettings(tap_time=200, hold_time=250),
            layers=layers
        )

        # Use the KanataTransformer to transform the config
        from .transformer.kanata_transformer import KanataTransformer
        transformer = KanataTransformer()
        output = transformer.transform(config)
        
        with open(args.output_file, 'w') as f:
            f.write(output)

        return 0

    except FileNotFoundError:
        print(f"Input file not found: {args.input_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())

# Implementation will be added in subsequent tasks
