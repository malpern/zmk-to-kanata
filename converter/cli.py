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
        "output_file",
        type=Path,
        help="Path where the Kanata config will be written",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit",
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

    # Convert the args to a list for the main function
    main_args = [str(args.input_file), str(args.output_file)]
    return convert_main(main_args)


if __name__ == "__main__":
    sys.exit(main())
