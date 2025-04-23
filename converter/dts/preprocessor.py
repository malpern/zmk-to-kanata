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

    pass


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
            PreprocessorError: If the preprocessor fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file does not exist: {input_file}")

        # Convert input file to absolute path
        input_file = os.path.abspath(input_file)
        input_dir = os.path.dirname(input_file)

        # Read input file to get matrix size and preserve DTS directives
        with open(input_file, "r") as f:
            content = f.read()

        # Preserve DTS directives
        content, directives = self._preserve_dts_directives(content)

        # Get matrix size if available
        matrix_size = self._get_matrix_size(content)
        matrix_header = None

        try:
            # Create matrix transform header if size is available
            if matrix_size:
                rows, cols = matrix_size
                matrix_header = self._create_matrix_transform_header(rows, cols)

            # Build preprocessor command
            if platform.system() == "Windows":
                cmd = [self.cpp_path, "/E", "/C"]
                # Add input directory first
                cmd.extend(["/I", input_dir])
                for path in self.include_paths:
                    cmd.extend(["/I", os.path.abspath(path)])
                cmd.append(input_file)
            else:
                cmd = [
                    self.cpp_path,
                    "-E",  # Preprocess only
                    "-x",
                    "c",  # Treat input as C source
                    "-P",  # Don't include line markers
                    "-D__DTS__",
                ]
                # Add input directory first
                cmd.extend(["-I", input_dir])
                for path in self.include_paths:
                    cmd.extend(["-I", os.path.abspath(path)])
                if matrix_header:
                    cmd.extend(["-include", matrix_header])
                cmd.append(input_file)

            # Write preserved content to temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".dts", delete=False
            ) as f:
                f.write(content)
                temp_input = f.name

            try:
                # Run preprocessor
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    raise PreprocessorError(
                        f"Preprocessor failed with code {result.returncode}:\n"
                        f"Command: {' '.join(cmd)}\n"
                        f"Error: {result.stderr}"
                    )

                # Process output
                output = result.stdout

                # Restore RC macros
                output = self._restore_rc_macros(output)

                # Restore DTS directives
                output = self._restore_dts_directives(output, directives)

                return output

            finally:
                # Clean up temporary files
                os.unlink(temp_input)

        finally:
            # Clean up matrix header if created
            if matrix_header and os.path.exists(matrix_header):
                os.unlink(matrix_header)
