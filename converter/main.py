"""Main module for the ZMK to Kanata converter."""

import argparse
import os
import sys
from typing import List

from converter.transformer.kanata_transformer import KanataTransformer
from converter.dts.preprocessor import DtsPreprocessor
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor


def convert_zmk_to_kanata(zmk_file: str, include_paths: List[str] = None) -> str:
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
    # Get the default include path from the package
    default_include_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dts", "include"
    )

    # Combine user-provided include paths with the default one
    all_include_paths = [default_include_path]
    if include_paths:
        all_include_paths.extend(include_paths)

    # Initialize components
    preprocessor = DtsPreprocessor(include_paths=all_include_paths)
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
        # Directly return the transformed output
        return transformer.transform(keymap_config)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input file not found: {zmk_file}") from e
    except Exception as e:
        # Consider more specific error handling/logging here
        raise ValueError(f"Failed to convert keymap: {str(e)}") from e


def main(args=None):
    """Main entry point for the converter."""
    parser = argparse.ArgumentParser(
        description="Convert ZMK keymap files to Kanata configuration"
    )
    parser.add_argument("input_file", help="Path to the ZMK keymap file")
    parser.add_argument(
        "-o", "--output", help="Path to the output file (default: stdout)"
    )
    parser.add_argument(
        "-I",
        "--include",
        action="append",
        help="Additional include paths for preprocessing",
        default=[],  # Add default value
    )

    parsed_args = parser.parse_args(args)

    try:
        # Convert the keymap
        kanata_config = convert_zmk_to_kanata(
            parsed_args.input_file, include_paths=parsed_args.include
        )

        # Write output
        if parsed_args.output:
            with open(parsed_args.output, "w") as f:
                f.write(kanata_config)
            print(
                f"Successfully converted {parsed_args.input_file} to {parsed_args.output}"
            )  # Add success message
        else:
            print(kanata_config)

        return 0  # Return success code

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        # Potentially return different codes for different errors
        return 1  # Return error code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
