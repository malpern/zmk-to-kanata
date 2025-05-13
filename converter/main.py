"""Main module for the ZMK to Kanata converter."""

import argparse
import os
import sys
from typing import List
import logging
import json
import yaml

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
        default=[],
    )
    parser.add_argument(
        "--dump-preprocessed",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Dump preprocessed DTS to FILE (or stdout if not specified)",
    )
    parser.add_argument(
        "--dump-ast",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Dump parsed AST as JSON to FILE (or stdout if not specified)",
    )
    parser.add_argument(
        "--dump-extracted",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Dump extracted keymap model as JSON to FILE (or stdout if not specified)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging output",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times)",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help="Set logging level (e.g., info, debug, warning)",
    )

    parsed_args = parser.parse_args(args)

    # Set up logging configuration
    log_level = logging.WARNING
    if parsed_args.debug:
        log_level = logging.DEBUG
    elif parsed_args.verbose == 1:
        log_level = logging.INFO
    elif parsed_args.verbose >= 2:
        log_level = logging.DEBUG
    if parsed_args.log_level:
        log_level = getattr(logging, parsed_args.log_level.upper(), log_level)
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(message)s",
    )

    try:
        # Get the default include path from the package
        default_include_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "dts", "include"
        )
        all_include_paths = [default_include_path]
        if parsed_args.include:
            all_include_paths.extend(parsed_args.include)

        # Initialize components
        preprocessor = DtsPreprocessor(include_paths=all_include_paths)
        parser_ = DtsParser()
        extractor = KeymapExtractor()
        transformer = KanataTransformer()

        # Preprocess the input file
        logging.info("Preprocessing input file: %s", parsed_args.input_file)
        preprocessed_content = preprocessor.preprocess(parsed_args.input_file)
        if parsed_args.dump_preprocessed is not None:
            out = parsed_args.dump_preprocessed
            if out == "-":
                print(preprocessed_content)
            else:
                with open(out, "w") as f:
                    f.write(preprocessed_content)
            logging.info("Preprocessed DTS dumped to %s", out)

        # Parse the preprocessed content
        logging.info("Parsing preprocessed DTS content")
        ast = parser_.parse(preprocessed_content)
        if parsed_args.dump_ast is not None:
            out = parsed_args.dump_ast
            ast_dict = ast.to_dict() if hasattr(ast, "to_dict") else ast.__dict__
            ast_json = json.dumps(ast_dict, indent=2)
            if out == "-":
                print(ast_json)
            else:
                with open(out, "w") as f:
                    f.write(ast_json)
            logging.info("AST dumped to %s", out)

        # Extract keymap configuration
        logging.info("Extracting keymap configuration from AST")
        keymap_config = extractor.extract(ast)
        if parsed_args.dump_extracted is not None:
            out = parsed_args.dump_extracted
            # Try YAML, fallback to JSON
            try:
                extracted_dict = (
                    keymap_config.to_dict()
                    if hasattr(keymap_config, "to_dict")
                    else keymap_config.__dict__
                )
                extracted_yaml = yaml.safe_dump(extracted_dict, sort_keys=False)
                if out == "-":
                    print(extracted_yaml)
                else:
                    with open(out, "w") as f:
                        f.write(extracted_yaml)
                logging.info("Extracted keymap model dumped to %s (YAML)", out)
            except Exception as e:
                logging.warning("Failed to dump extracted model as YAML: %s", e)
                extracted_json = json.dumps(extracted_dict, indent=2)
                if out == "-":
                    print(extracted_json)
                else:
                    with open(out, "w") as f:
                        f.write(extracted_json)
                logging.info("Extracted keymap model dumped to %s (JSON)", out)

        # Transform to Kanata format
        logging.info("Transforming keymap to Kanata format")
        kanata_config = transformer.transform(keymap_config)

        # Write output
        if parsed_args.output:
            with open(parsed_args.output, "w") as f:
                f.write(kanata_config)
            logging.info(
                "Successfully converted %s to %s",
                parsed_args.input_file,
                parsed_args.output,
            )
        else:
            print(kanata_config)

        return 0  # Return success code

    except Exception as e:
        logging.error("Error: %s", str(e))
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1  # Return error code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
