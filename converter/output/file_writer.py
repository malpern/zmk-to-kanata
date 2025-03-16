"""File Writer Module

This module is responsible for writing the Kanata configuration to a file.
"""
from pathlib import Path
import os


class KanataFileWriter:
    """Writes Kanata configuration to a file.

    This class provides functionality to write Kanata configuration strings
    to files, with proper error handling for common file operations.
    """

    def write(self, content: str, output_path: Path) -> None:
        """Write the Kanata configuration to the specified file.

        Args:
            content: The Kanata configuration string to write.
            output_path: The path where to write the configuration file.

        Raises:
            OSError: If there are permission issues or directory doesn't exist.
            TypeError: If content is not a string or output_path not a Path.
        """
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        if not isinstance(output_path, Path):
            raise TypeError("Output path must be a Path object")

        # Ensure the parent directory exists
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(content)
