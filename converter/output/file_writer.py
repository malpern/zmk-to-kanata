"""File Writer Module

This module is responsible for writing the Kanata configuration to a file.
"""
from pathlib import Path


class KanataFileWriter:
    """Writes Kanata configuration to a file."""

    def write(self, content: str, output_path: Path) -> None:
        """Write the Kanata configuration to the specified file.

        Args:
            content: The Kanata configuration string to write.
            output_path: The path where to write the configuration file.
        """
        with open(output_path, 'w') as f:
            f.write(content)