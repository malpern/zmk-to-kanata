"""Main module for the ZMK to Kanata converter."""

import argparse
import sys
from pathlib import Path
from typing import List, Union, Dict, Any, Optional

from .layer_transformer import KanataLayer
from .models import Keymap, Layer, KanataConfig
from .transformer.kanata_transformer import KanataTransformer
from .dts.preprocessor import DtsPreprocessor
from .dts.parser import DtsParser
from .dts.extractor import KeymapExtractor


def generate_kanata_keymap(layers: List[KanataLayer]) -> str:
    """Generate a Kanata keymap configuration from a list of layers.

    Args:
        layers: List of KanataLayer objects or strings

    Returns:
        String containing the complete Kanata keymap configuration
    """
    kanata_config = []

    # Add header comments
    kanata_config.extend(
        [
            ";; ZMK to Kanata Configuration",
            ";; Generated automatically - DO NOT EDIT",
            "",
            ";; Global settings",
            "(defvar tap-time 200)",
            "(defvar hold-time 250)",
            "",
        ]
    )

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

    return "\n".join(kanata_config)


def convert_zmk_to_kanata(
    zmk_file: str, 
    include_paths: List[str] = None
) -> str:
    """Convert a ZMK keymap file to Kanata configuration.

    Args:
        zmk_file: Path to the ZMK keymap file
        include_paths: Optional list of paths to search for included files

    Returns:
        String containing the Kanata configuration

    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If the input file is invalid
    """
    # Initialize components
    preprocessor = DtsPreprocessor(include_paths=include_paths)
    parser = DtsParser()
    extractor = KeymapExtractor()
    transformer = KanataTransformer()

    try:
        # Preprocess the input file
        preprocessed_content = preprocessor.preprocess(zmk_file)
        
        # Parse the preprocessed content
        ast = parser.parse(preprocessed_content)
        
        # Extract keymap configuration
        keymap_config = extractor.extract(ast)
        
        # Transform to Kanata format
        kanata_layers = transformer.transform(keymap_config)
        
        # Generate final configuration
        return generate_kanata_keymap(kanata_layers)
        
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input file not found: {zmk_file}") from e
    except Exception as e:
        raise ValueError(f"Failed to convert keymap: {str(e)}") from e


def main(args=None):
    """Main entry point for the converter."""
    parser = argparse.ArgumentParser(
        description="Convert ZMK keymap files to Kanata configuration"
    )
    parser.add_argument(
        "input_file",
        help="Path to the ZMK keymap file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output file (default: stdout)"
    )
    parser.add_argument(
        "-I", "--include",
        action="append",
        help="Additional include paths for preprocessing"
    )

    args = parser.parse_args(args)

    try:
        # Convert the keymap
        kanata_config = convert_zmk_to_kanata(
            args.input_file,
            include_paths=args.include
        )

        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(kanata_config)
        else:
            print(kanata_config)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Implementation will be added in subsequent tasks
