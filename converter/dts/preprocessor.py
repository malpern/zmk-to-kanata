"""DTS Preprocessor Module.

This module provides functionality for preprocessing DTS files before parsing.
"""

import os
import subprocess
import re
import tempfile
import shlex
from typing import List, Tuple, Optional
from pathlib import Path


class PreprocessorError(Exception):
    """Exception raised when preprocessing fails."""

    def __init__(
        self,
        message: str,
        file: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        context: Optional[str] = None,
        help_text: Optional[str] = None,
    ):
        """Initialize the error with detailed information.

        Args:
            message: The error message
            file: The file where the error occurred
            line: The line number where the error occurred
            column: The column number where the error occurred
            context: Additional context for the error
            help_text: Help text for fixing the error
        """
        super().__init__(message)
        self.message = message
        self.file = file
        self.line = line
        self.column = column
        self.context = context
        self.help_text = help_text


class DtsPreprocessor:
    """Preprocesses DTS files using the C preprocessor."""

    def __init__(
        self,
        cpp_path: Optional[str] = None,
        include_paths: Optional[List[str]] = None,
    ):
        """Initialize the preprocessor.

        Args:
            cpp_path: Path to the C preprocessor executable
            include_paths: List of paths to search for include files
        """
        if cpp_path is None:
            cpp_path = "/usr/bin/cpp"
        cpp_path = str(cpp_path)
        if not cpp_path.endswith("cpp"):
            raise PreprocessorError(
                "Invalid cpp path",
                help_text="The cpp path must point to a cpp executable",
            )
        self.cpp_path = Path(cpp_path)

        self.include_paths = []
        if include_paths:
            for path in include_paths:
                path_obj = Path(path)
                if not path_obj.exists():
                    msg = f"Include path does not exist: {path}"
                    help_text = "Ensure all include paths exist and are " "accessible"
                    raise PreprocessorError(msg, help_text=help_text)
                self.include_paths.append(str(path_obj))

    @staticmethod
    def _quote_path(path: str) -> str:
        """Quote a path for safe usage in subprocess commands."""
        # Use shlex.quote for POSIX, fallback to double quotes for Windows
        if os.name == "nt":
            # On Windows, wrap in double quotes if needed
            if " " in path or any(c in path for c in "()[]{}&^%$#@!"):
                return f'"{path}"'
            return path
        else:
            return shlex.quote(path)

    def _get_matrix_size(self, content: str) -> Optional[Tuple[int, int]]:
        """Extract matrix dimensions from DTS content.

        Args:
            content: The DTS content to parse

        Returns:
            A tuple of (rows, cols) if found, None otherwise
        """
        # Try to find matrix size from matrix_transform property
        matrix_pattern = (
            r"matrix_transform\s*:\s*[^{]*{[^}]*rows\s*=\s*<(\d+)>"
            r"[^}]*columns\s*=\s*<(\d+)>"
        )
        match = re.search(matrix_pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            rows = int(match.group(1))
            cols = int(match.group(2))
            return rows, cols

        # Fallback: try to find size from RC_MATRIX macro
        rc_pattern = r"RC_MATRIX\s*=\s*<(\d+)\s+(\d+)>"
        match = re.search(rc_pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            rows = int(match.group(1))
            cols = int(match.group(2))
            return rows, cols

        return None

    def preprocess(
        self,
        input_path: str,
        matrix_size: Optional[Tuple[int, int]] = None,
    ) -> str:
        """Preprocess a DTS file.

        Args:
            input_path: Path to the input file
            matrix_size: Optional tuple of (rows, cols) for matrix transform

        Returns:
            The preprocessed content as a string

        Raises:
            PreprocessorError: If preprocessing fails
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise PreprocessorError(
                f"Input file does not exist: {input_path}",
                help_text=(
                    "Ensure the input file exists and has proper " "read permissions"
                ),
            )

        try:
            with open(input_path, "r") as f:
                content_for_cpp = f.read()
        except Exception as e:
            raise PreprocessorError(
                f"Failed to read input file: {str(e)}",
                file=str(input_path),
                help_text=("Ensure the file exists and has proper " "read permissions"),
            )

        # Create a temporary file for the preprocessor input
        tmp_input = tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".dts",
            dir=None,  # Use system default temp dir (usually /tmp)
        )
        tmp_input.write(content_for_cpp)
        tmp_input.close()
        tmp_input_file = Path(tmp_input.name)

        # Debug: print environment and temp file contents
        print("[DtsPreprocessor] ENVIRONMENT:")
        for k, v in os.environ.items():
            if len(v) > 40:
                print(f"  {k}={v[:20]}...{v[-20:]}")
            else:
                print(f"  {k}={v}")
        if len(str(tmp_input_file)) > 70:
            print(f"[DtsPreprocessor] Temp file: " f"{str(tmp_input_file)[:70]}...")
        else:
            print(f"[DtsPreprocessor] Temp file: {tmp_input_file}")
        with open(tmp_input_file, "r") as f:
            print("[DtsPreprocessor] Temp file contents:")
            print(f.read())

        try:
            # Build preprocessor command as a list for shell=False
            if os.uname().sysname == "Darwin":
                # Use clang with assembler-with-cpp for .dts files on macOS
                clang_path = "/usr/bin/clang"
                cpp_cmd = [
                    clang_path,
                    "-E",
                    "-nostdinc",
                    "-undef",
                    "-x",
                    "assembler-with-cpp",
                ]
                for path in self.include_paths:
                    cpp_cmd.extend(["-I", str(path)])
                cpp_cmd.append(str(tmp_input_file))
            else:
                cpp_cmd = [
                    str(self.cpp_path),
                    "-E",
                ]
                for path in self.include_paths:
                    cpp_cmd.extend(["-I", str(path)])
                cpp_cmd.extend(["-x", "c", str(tmp_input_file)])

            # Debug: print the constructed command list
            print("[DtsPreprocessor] cpp command:", cpp_cmd)

            # Run preprocessor with shell=False
            try:
                result = subprocess.run(
                    cpp_cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=False,
                )
            except subprocess.CalledProcessError as e:
                raise PreprocessorError(
                    "Failed to process DTS directives",
                    file=str(input_path),
                    context=str(e),
                    help_text=("Check for malformed DTS directives in " "input file"),
                )

            return result.stdout

        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_input_file)
            except Exception:
                pass

    def _create_matrix_transform_header(
        self,
        rows: int,
        cols: int,
    ) -> Optional[str]:
        """Create a header file with matrix transform definitions.

        Args:
            rows: Number of rows in the matrix
            cols: Number of columns in the matrix

        Returns:
            Path to the created header file, or None if creation fails
        """
        content = f"""
#define RC(row, col) RC(row,col)
#define RC_MATRIX({rows}, {cols})
"""
        try:
            tmp_file = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".h",
                delete=False,
            )
            tmp_file.write(content)
            tmp_file.close()
            return tmp_file.name
        except Exception:
            return None
