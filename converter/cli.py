"""Command-line interface for the ZMK to Kanata converter."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .main import main as convert_main

__version__ = "0.1.0"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert ZMK keymap files to Kanata format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input ZMK keymap file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path where the Kanata config will be written (default: stdout)",
        default=None,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit",
    )

    # Add debug and dump flags
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

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: List of command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Build argument list for converter.main.main
    main_args = [str(args.input_file)]
    if args.output is not None:
        main_args.extend(["-o", str(args.output)])
    if args.include:
        for inc in args.include:
            main_args.extend(["-I", inc])
    if args.dump_preprocessed is not None:
        main_args.append(
            f"--dump-preprocessed{'' if args.dump_preprocessed == '-' else f'={args.dump_preprocessed}' }"
        )
    if args.dump_ast is not None:
        main_args.append(
            f"--dump-ast{'' if args.dump_ast == '-' else f'={args.dump_ast}' }"
        )
    if args.dump_extracted is not None:
        main_args.append(
            f"--dump-extracted{'' if args.dump_extracted == '-' else f'={args.dump_extracted}' }"
        )
    if args.debug:
        main_args.append("--debug")
    if args.verbose:
        main_args.extend(["-v"] * args.verbose)
    if args.log_level:
        main_args.extend(["--log-level", args.log_level])

    return convert_main(main_args)


if __name__ == "__main__":
    sys.exit(main())
