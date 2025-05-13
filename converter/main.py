"""Main module for the ZMK to Kanata converter."""

import argparse
import os
import sys
import logging
import json
from typing import List

from converter.transformer.kanata_transformer import KanataTransformer
from converter.dts.preprocessor import DtsPreprocessor
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor


def setup_logging(debug=False, verbose=0, log_level=None):
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    elif debug:
        level = logging.DEBUG
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def dump_output(data, dest, default=None):
    if dest is True or dest is None:
        print(data)
    else:
        with open(dest, "w") as f:
            f.write(data)


def convert_zmk_to_kanata(
    zmk_file: str,
    include_paths: List[str] = None,
    dump_preprocessed=None,
    dump_ast=None,
    dump_extracted=None,
) -> str:
    """Convert a ZMK keymap file to Kanata configuration, with optional dumps."""
    default_include_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dts", "include"
    )
    all_include_paths = [default_include_path]
    if include_paths:
        all_include_paths.extend(include_paths)
    preprocessor = DtsPreprocessor(include_paths=all_include_paths)
    parser = DtsParser()
    extractor = KeymapExtractor()
    transformer = KanataTransformer()
    try:
        preprocessed_content = preprocessor.preprocess(zmk_file)
        if dump_preprocessed is not None:
            dump_output(preprocessed_content, dump_preprocessed)
        ast = parser.parse(preprocessed_content)
        if dump_ast is not None:
            # Use JSON for AST dump
            ast_json = json.dumps(ast, default=lambda o: o.__dict__, indent=2)
            dump_output(ast_json, dump_ast)
        keymap_config = extractor.extract(ast)
        if dump_extracted is not None:
            # Use JSON for extracted model
            model_json = json.dumps(
                keymap_config, default=lambda o: o.__dict__, indent=2
            )
            dump_output(model_json, dump_extracted)
        return transformer.transform(keymap_config)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input file not found: {zmk_file}") from e
    except Exception as e:
        raise ValueError(f"Failed to convert keymap: {str(e)}") from e


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Convert ZMK keymap files to Kanata configuration"
    )
    parser.add_argument("input_file", help="Path to the ZMK keymap file")
    parser.add_argument("output_file", help="Path to the output file (Kanata config)")
    parser.add_argument(
        "--dump-preprocessed",
        nargs="?",
        const=True,
        help="Output preprocessed DTS to stdout or file",
    )
    parser.add_argument(
        "--dump-ast",
        nargs="?",
        const=True,
        help="Output parsed AST (as JSON) to stdout or file",
    )
    parser.add_argument(
        "--dump-extracted",
        nargs="?",
        const=True,
        help="Output extracted keymap model (as JSON) to stdout or file",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity"
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help="Set logging level (e.g., info, debug, warning)",
    )
    parser.add_argument(
        "-I",
        "--include",
        action="append",
        help="Additional include paths for preprocessing",
        default=[],
    )
    parsed_args = parser.parse_args(args)
    setup_logging(parsed_args.debug, parsed_args.verbose, parsed_args.log_level)
    try:
        kanata_config = convert_zmk_to_kanata(
            parsed_args.input_file,
            include_paths=parsed_args.include,
            dump_preprocessed=parsed_args.dump_preprocessed,
            dump_ast=parsed_args.dump_ast,
            dump_extracted=parsed_args.dump_extracted,
        )
        with open(parsed_args.output_file, "w") as f:
            f.write(kanata_config)
        logging.info(
            f"Successfully converted {parsed_args.input_file} to {parsed_args.output_file}"
        )
        return 0
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
