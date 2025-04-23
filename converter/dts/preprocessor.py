import os
import re
import subprocess
import tempfile
from typing import List, Optional, Tuple
import platform


class PreprocessorError(Exception):
    """Exception raised when preprocessing fails."""
    pass


class DtsPreprocessor:
    """Preprocesses DTS files using the C preprocessor."""

    def __init__(
        self,
        cpp_path: Optional[str] = None,
        include_paths: Optional[List[str]] = None
    ):
        """Initialize the preprocessor.

        Args:
            cpp_path: Path to the C preprocessor. If None, uses xcrun cpp on
                     macOS and cpp on other platforms.
            include_paths: List of paths to search for included files.
        """
        self.include_paths = include_paths or []

        # Use clang on macOS, regular cpp on other platforms
        if cpp_path:
            self.cpp_path = cpp_path
        elif platform.system() == 'Darwin':
            try:
                # Try to get clang path from xcrun
                result = subprocess.run(
                    ['xcrun', '--find', 'clang'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.cpp_path = result.stdout.strip()
            except subprocess.CalledProcessError:
                # Fall back to regular cpp if xcrun fails
                self.cpp_path = 'cpp'
        else:
            self.cpp_path = 'cpp'

    def _get_matrix_size(self, content: str) -> Optional[Tuple[int, int]]:
        """Extract matrix dimensions from DTS content."""
        # Try to find matrix size from matrix_transform property
        matrix_pattern = (
            r'matrix_transform\s*:\s*[^{]*{[^}]*rows\s*=\s*<(\d+)>'
            r'[^}]*columns\s*=\s*<(\d+)>'
        )
        match = re.search(matrix_pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Fallback: try to find size from RC_MATRIX macro
        rc_pattern = r'RC_MATRIX\s*=\s*<(\d+)\s+(\d+)>'
        match = re.search(rc_pattern, content)
        
        if match:
            return int(match.group(1)), int(match.group(2))
            
        return None

    def _create_matrix_transform_header(self, rows: int, cols: int) -> str:
        """Create a temporary header file with matrix transform macros."""
        content = f"""
#define RC(row, col) {{ &transform[{rows} * (col) + (row)] }}
#define RC_MATRIX({rows}, {cols})
"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.h',
            delete=False
        ) as f:
            f.write(content)
            return f.name

    def _restore_rc_macros(self, content: str, rows: int, cols: int) -> str:
        """Restore RC macros in preprocessed content.

        Args:
            content: Preprocessed content
            rows: Number of rows in the matrix
            cols: Number of columns in the matrix

        Returns:
            Content with RC macros restored
        """
        # Replace expanded RC macros with original form
        for i in range(cols):
            content = content.replace(str(i), f"RC({i})")
        return content

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

        # Read input file to get matrix size
        with open(input_file, 'r') as f:
            content = f.read()

        # Get matrix size if available
        matrix_size = self._get_matrix_size(content)
        matrix_header = None

        try:
            # Create matrix transform header if size is available
            if matrix_size:
                rows, cols = matrix_size
                matrix_header = self._create_matrix_transform_header(
                    rows,
                    cols
                )

            # Build preprocessor command
            if platform.system() == 'Windows':
                cmd = [self.cpp_path, '/E', '/C']
                # Add input directory first
                cmd.extend(['/I', input_dir])
                for path in self.include_paths:
                    cmd.extend(['/I', os.path.abspath(path)])
                cmd.append(input_file)
            else:
                cmd = [
                    self.cpp_path,
                    '-E',  # Preprocess only
                    '-x', 'c',  # Treat input as C source
                    '-P',  # Don't include line markers
                    '-D__DTS__'
                ]
                # Add input directory first
                cmd.extend(['-I', input_dir])
                for path in self.include_paths:
                    cmd.extend(['-I', os.path.abspath(path)])
                if matrix_header:
                    cmd.extend(['-I', os.path.dirname(matrix_header)])
                cmd.append(input_file)

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                content = result.stdout

                # Restore RC macros if matrix size is available
                if matrix_size:
                    rows, cols = matrix_size
                    content = self._restore_rc_macros(content, rows, cols)

                return content

            except subprocess.CalledProcessError as e:
                raise PreprocessorError(
                    f"Preprocessing failed: {e.stderr}"
                ) from e
            except FileNotFoundError as e:
                raise PreprocessorError(
                    f"C preprocessor not found: {self.cpp_path}"
                ) from e

            finally:
                # Clean up temporary header file
                if matrix_header and os.path.exists(matrix_header):
                    os.unlink(matrix_header)

        except Exception:
            # Clean up temporary header file on any error
            if matrix_header and os.path.exists(matrix_header):
                os.unlink(matrix_header)
            raise 