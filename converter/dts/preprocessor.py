"""DTS Preprocessor Module.

This module provides functionality for preprocessing DTS files before parsing.
"""

import os
import platform
import subprocess
import re
import tempfile
from typing import List, Tuple, Optional


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
            context: Additional context about the error
            help_text: Helpful text for fixing the error
        """
        self.file = file
        self.line = line
        self.column = column
        self.context = context
        self.help_text = help_text

        # Build the full error message
        full_message = message
        if file:
            full_message = f"{file}: {full_message}"
        if line:
            full_message = f"{full_message} at line {line}"
            if column:
                full_message = f"{full_message}, column {column}"

        if context:
            full_message = f"{full_message}\n\n{context}"
        if help_text:
            full_message = f"{full_message}\n\nHelp: {help_text}"

        super().__init__(full_message)


class DtsPreprocessor:
    """Preprocesses DTS files using the C preprocessor."""

    def __init__(
        self, cpp_path: Optional[str] = None, include_paths: Optional[List[str]] = None
    ):
        """Initialize the preprocessor.

        Args:
            cpp_path: Path to the C preprocessor. If None, uses xcrun cpp on
                     macOS and cpp on other platforms.
            include_paths: List of paths to search for included files.
        """
        # Get the path to our local header files
        module_dir = os.path.dirname(os.path.abspath(__file__))
        local_include_path = os.path.join(module_dir, "include")

        # Combine with user-provided paths, ensuring local path is first
        self.include_paths = [local_include_path]
        if include_paths:
            self.include_paths.extend(include_paths)

        # Use clang on macOS, regular cpp on other platforms
        if cpp_path:
            self.cpp_path = cpp_path
        elif platform.system() == "Darwin":
            try:
                # Try to get clang path from xcrun
                result = subprocess.run(
                    ["xcrun", "--find", "clang"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.cpp_path = result.stdout.strip()
            except subprocess.CalledProcessError:
                # Fall back to regular cpp if xcrun fails
                self.cpp_path = "cpp"
        else:
            self.cpp_path = "cpp"

    def _get_matrix_size(self, content: str) -> Optional[Tuple[int, int]]:
        """Extract matrix dimensions from DTS content."""
        # Try to find matrix size from matrix_transform property
        matrix_pattern = (
            r"matrix_transform\s*:\s*[^{]*{[^}]*rows\s*=\s*<(\d+)>"
            r"[^}]*columns\s*=\s*<(\d+)>"
        )
        match = re.search(matrix_pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            return int(match.group(1)), int(match.group(2))

        # Fallback: try to find size from RC_MATRIX macro
        rc_pattern = r"RC_MATRIX\s*=\s*<(\d+)\s+(\d+)>"
        match = re.search(rc_pattern, content)

        if match:
            return int(match.group(1)), int(match.group(2))

        return None

    def _create_matrix_transform_header(self, rows: int, cols: int) -> str:
        """Create a temporary header file with matrix transform macros."""
        content = f"""
#define RC(row, col) RC(row,col)
#define RC_MATRIX({rows}, {cols})
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".h", delete=False) as f:
            f.write(content)
            return f.name

    def _restore_rc_macros(self, content: str) -> str:
        """Restore RC macros in preprocessed content."""
        # Replace expanded RC macro with original format
        pattern = r"\(\((\d+)\)\s*<<\s*8\s*\|\s*\((\d+)\)\)"
        content = re.sub(pattern, r"RC(\1,\2)", content)
        return content

    def _preserve_dts_directives(self, content: str) -> Tuple[str, List[str]]:
        """Preserve DTS-specific directives before preprocessing.

        Args:
            content: The original DTS content

        Returns:
            A tuple containing:
            - The content with DTS directives replaced by placeholders
            - A list of the preserved directives
        """
        # Pattern to match DTS-specific directives with their full context
        dts_directive_patterns = [
            # binding-cells directive with optional value
            r"(#binding-cells\s*=\s*<[^>]*>)",
            # include directive with path
            r'(#include\s+[<"][^>"}]*[>"])',
            # define directive with value
            r"(#define\s+[^\n]*)",
            # General DTS directives that might span multiple lines
            r"(#[a-zA-Z-]+\s*[^;]*?;)",
        ]

        directives = []
        modified_content = content

        # Process each pattern
        for pattern in dts_directive_patterns:
            matches = list(re.finditer(pattern, modified_content, re.MULTILINE))

            # Process matches in reverse to preserve positions
            for match in reversed(matches):
                directive = match.group(1)
                placeholder = f"__DTS_DIRECTIVE_{len(directives)}__"
                directives.append(directive)

                # Replace the directive with placeholder, preserving surrounding whitespace
                start, end = match.span(1)
                modified_content = (
                    modified_content[:start] + placeholder + modified_content[end:]
                )

        return modified_content, list(reversed(directives))

    def _restore_dts_directives(self, content: str, directives: List[str]) -> str:
        """Restore DTS-specific directives after preprocessing.

        Args:
            content: The preprocessed content
            directives: List of preserved directives

        Returns:
            Content with DTS directives restored
        """
        modified_content = content

        # Process each directive
        for i, directive in enumerate(directives):
            placeholder = f"__DTS_DIRECTIVE_{i}__"

            # Handle multi-line directives
            if "\n" in directive:
                # Ensure proper line endings
                directive = directive.rstrip() + "\n"

            modified_content = modified_content.replace(placeholder, directive)

        return modified_content

    def preprocess(self, input_file: str) -> str:
        """Preprocess a DTS file using the C preprocessor.

        Args:
            input_file: Path to the input DTS file

        Returns:
            The preprocessed file contents as a string

        Raises:
            FileNotFoundError: If the input file does not exist
            PreprocessorError: If the preprocessor fails with detailed context
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file does not exist: {input_file}")

        # Convert input file to absolute path
        input_file = os.path.abspath(input_file)
        input_dir = os.path.dirname(input_file)

        try:
            # Read input file to get matrix size and preserve DTS directives
            with open(input_file, "r") as f:
                content = f.read()
        except Exception as e:
            raise PreprocessorError(
                f"Failed to read input file: {str(e)}",
                file=input_file,
                help_text="Ensure the file exists and has proper read permissions.",
            )

        try:
            # Preserve DTS directives
            content, directives = self._preserve_dts_directives(content)
        except Exception as e:
            raise PreprocessorError(
                "Failed to process DTS directives",
                file=input_file,
                context=str(e),
                help_text="Check for malformed DTS directives in the input file.",
            )

        # Get matrix size if available
        matrix_size = self._get_matrix_size(content)
        matrix_header = None

        try:
            # Create matrix transform header if size is available
            if matrix_size:
                rows, cols = matrix_size
                matrix_header = self._create_matrix_transform_header(rows, cols)
                self.include_paths.insert(0, os.path.dirname(matrix_header))

            # Build cpp command
            cpp_args = [
                self.cpp_path,
                "-E",  # Preprocess only
                "-x",
                "c",  # Treat as C source
                "-P",  # No line markers
            ]

            # Add include paths
            for path in self.include_paths:
                cpp_args.extend(["-I", path])

            # Add input file
            cpp_args.append(input_file)

            # Run preprocessor
            result = subprocess.run(
                cpp_args, capture_output=True, text=True, cwd=input_dir
            )

            if result.returncode != 0:
                # Parse error message for line/column info
                error_pattern = r"([^:]+):(\d+):(\d+):\s*(.+)"
                match = re.search(error_pattern, result.stderr)

                if match:
                    err_file, line, col, msg = match.groups()
                    # Get the problematic line for context
                    with open(err_file, "r") as f:
                        lines = f.readlines()
                        context_line = lines[int(line) - 1].strip()
                        pointer = " " * (int(col) - 1) + "^"
                        context = f"  |\n{line}| {context_line}\n  | {pointer}"

                    raise PreprocessorError(
                        msg,
                        file=err_file,
                        line=int(line),
                        column=int(col),
                        context=context,
                        help_text=self._get_help_text(msg),
                    )
                else:
                    raise PreprocessorError(
                        "Preprocessing failed",
                        file=input_file,
                        context=result.stderr,
                        help_text="Check the error message above for details.",
                    )

            # Process the output
            output = result.stdout

            # Restore RC macros and DTS directives
            output = self._restore_rc_macros(output)
            output = self._restore_dts_directives(output, directives)

            return output

        finally:
            # Clean up temporary matrix header
            if matrix_header and os.path.exists(matrix_header):
                os.unlink(matrix_header)

    def _get_help_text(self, error_msg: str) -> str:
        """Get helpful text based on the error message.

        Args:
            error_msg: The error message from the preprocessor

        Returns:
            A helpful message for fixing the error
        """
        help_texts = {
            "file not found": "Make sure the file exists and the path is correct.",
            "'dt-bindings/zmk/keys.h' file not found": (
                "The ZMK header files are missing. Check that the include paths "
                "are set correctly and the required headers are present."
            ),
            "unterminated conditional directive": (
                "There's an unclosed #if/#ifdef/#ifndef directive. "
                "Make sure all conditional directives are properly closed with #endif."
            ),
            "expected expression": (
                "The preprocessor expected a valid C expression. "
                "Check for syntax errors in macro definitions or conditional directives."
            ),
        }

        # Find the most relevant help text
        for key, text in help_texts.items():
            if key.lower() in error_msg.lower():
                return text

        return "Check the syntax and ensure all required files are present."
