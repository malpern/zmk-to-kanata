"""Utility functions for tests, primarily for parsing and transforming ZMK content."""

from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.transformer.kanata_transformer import KanataTransformer


def parse_and_transform(zmk_content: str) -> str:
    """Parse ZMK DTS string and transform it into Kanata output format."""
    parser = DtsParser()
    # Ensure raise_on_error is explicitly True for these tests
    # The DtsParser itself handles errors by raising DtsParseError if issues occur.
    ast = parser.parse(zmk_content)  # Removed raise_on_error=True
    extractor = KeymapExtractor()
    keymap_config = extractor.extract(ast)
    transformer = KanataTransformer()
    return transformer.transform(keymap_config)
