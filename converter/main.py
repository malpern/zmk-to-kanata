"""Main module for the ZMK to Kanata converter."""

import argparse
import sys
from pathlib import Path
from typing import List

from .layer_transformer import KanataLayer
from .parser.zmk_parser import ZMKParser
from converter.error_handling import ErrorManager, ErrorSeverity
from converter.zmk_to_kanata import convert_zmk_to_kanata


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


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert ZMK keymap to Kanata format"
    )
    parser.add_argument(
        "input_file",
        help="Path to the input ZMK keymap file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output Kanata file (default: stdout)",
        default=None
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    parser.add_argument(
        "--mac",
        help="Use Mac-specific modifiers (GUI becomes CMD)",
        action="store_true"
    )
    parser.add_argument(
        "--version",
        help="Show version information",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("ZMK to Kanata Converter v1.0.0")
        sys.exit(0)
    
    # Set up error manager
    error_manager = ErrorManager(verbose=args.verbose)
    
    try:
        # Read input file
        with open(args.input_file, 'r') as f:
            zmk_content = f.read()
        
        # Convert ZMK to Kanata
        kanata_config, metadata = convert_zmk_to_kanata(
            zmk_content=zmk_content,
            output_path=args.output,
            error_manager=error_manager,
            is_mac=args.mac
        )
        
        # If no output file is specified, print to stdout
        if not args.output:
            print(kanata_config)
        
        # Print any errors or warnings
        if error_manager.has_errors(ErrorSeverity.WARNING):
            for error in error_manager.get_errors(ErrorSeverity.WARNING):
                print(f"WARNING: {error}", file=sys.stderr)
        
        if error_manager.has_errors(ErrorSeverity.ERROR):
            for error in error_manager.get_errors(ErrorSeverity.ERROR):
                print(f"ERROR: {error}", file=sys.stderr)
            sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())

# Implementation will be added in subsequent tasks
