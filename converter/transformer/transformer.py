"""Main Transformer Module.

This module provides the main transformer class that orchestrates the transformation
of ZMK keymap configurations to various output formats.
"""

from typing import Dict

from converter.error_handling.error_manager import (
    ErrorSeverity,
    get_error_manager,
)
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.transformer.kanata_transformer import KanataTransformer
from converter.transformer.macro_transformer import MacroTransformer


class Transformer:
    """Main transformer class that orchestrates the transformation process."""

    def __init__(self):
        """Initialize the transformer."""
        self.parser = DtsParser()
        self.extractor = KeymapExtractor()
        self.kanata_transformer = KanataTransformer()
        self.macro_transformer = MacroTransformer()
        self.error_manager = get_error_manager()

    def transform(self, dts_content: str) -> Dict[str, str]:
        """Transform the DTS content to various output formats.

        Args:
            dts_content: The DTS content to transform.

        Returns:
            A dictionary mapping output format names to their transformed content.
        """
        try:
            # Parse the DTS content
            root_node = self.parser.parse(dts_content)

            # Extract the keymap configuration
            keymap_config = self.extractor.extract(root_node)

            # Transform to various formats
            outputs = {}

            # Transform to Kanata format
            kanata_config = self.kanata_transformer.transform(keymap_config)
            outputs["kanata"] = kanata_config.to_string()

            # Transform macros
            macro_config = self.macro_transformer.transform(keymap_config)
            outputs["macros"] = macro_config.to_string()

            return outputs

        except Exception as e:
            self.error_manager.add_error(
                "Transformation failed", str(e), ErrorSeverity.ERROR
            )
            raise
