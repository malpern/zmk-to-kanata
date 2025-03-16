"""Main module for the ZMK to Kanata converter."""

import argparse
import os
import sys
from pathlib import Path
from typing import List

from .layer_transformer import KanataLayer
from .parser.zmk_parser import ZMKParser


def generate_kanata_keymap(layers: List[KanataLayer]) -> str:
    """Generate a Kanata keymap configuration from a list of layers.

    Args:
        layers: List of KanataLayer objects or strings

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
        # Handle both KanataLayer objects and strings
        if isinstance(layer, str):
            kanata_config.append(layer)
        else:
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


def main(args=None):
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
    
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    try:
        # Parse ZMK file
        zmk_parser = ZMKParser()
        try:
            config = zmk_parser.parse(Path(args.input_file))
        except FileNotFoundError:
            print(f"Input file not found: {args.input_file}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error parsing ZMK file: {e}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Error during parsing: {e}", file=sys.stderr)
            return 3

        # Transform to Kanata format
        from .transformer.kanata_transformer import KanataTransformer
        transformer = KanataTransformer()
        try:
            output = transformer.transform(config)
        except ValueError as e:
            print(f"Error transforming keymap: {e}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Error during transformation: {e}", file=sys.stderr)
            return 3
        
        # Write output file
        try:
            with open(args.output_file, 'w') as f:
                f.write(output)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 3

        return 0

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())

# Implementation will be added in subsequent tasks
