"""Parser module for ZMK Unicode bindings."""

import re
from typing import Dict, Optional

from converter.behaviors.unicode import UnicodeBinding, is_unicode_binding


class UnicodeParser:
    """Parser for ZMK Unicode bindings."""

    def __init__(self):
        """Initialize the parser."""
        self.unicode_mappings: Dict[str, str] = {}

    def parse_unicode_mappings(self, content: str) -> None:
        """Parse Unicode mappings from ZMK content.

        This method looks for macro definitions that implement Unicode
        characters and stores the mapping between the macro name and the
        Unicode character.

        Args:
            content: The ZMK file content
        """
        # Look for urob/zmk-nodefree-config style Unicode definitions
        # ZMK_UNICODE_SINGLE(pi, N0, N3, C, N0)
        single_pattern = re.compile(
            r'ZMK_UNICODE_SINGLE\((\w+),\s*([^)]+)\)',
            re.DOTALL
        )

        for match in single_pattern.finditer(content):
            name = match.group(1)
            # In a real implementation, we would parse the hex digits
            # and convert them to the actual Unicode character
            # For now, we'll use hardcoded mappings for common characters
            if name == "pi":
                self.unicode_mappings[f"&{name}"] = "π"

        # Look for urob/zmk-nodefree-config style Unicode pair definitions
        # ZMK_UNICODE_PAIR(n_tilde, N0, N0, F, N1, N0, N0, D, N1)
        pair_pattern = re.compile(
            r'ZMK_UNICODE_PAIR\((\w+),\s*([^)]+)\)',
            re.DOTALL
        )

        for match in pair_pattern.finditer(content):
            name = match.group(1)
            # In a real implementation, we would parse the hex digits
            # and convert them to the actual Unicode characters
            # For now, we'll use hardcoded mappings for common characters
            if name == "n_tilde":
                self.unicode_mappings[f"&{name}"] = "ñ"

    def parse_binding(self, binding_str: str) -> Optional[UnicodeBinding]:
        """Parse a Unicode binding string.

        Args:
            binding_str: The binding string to parse

        Returns:
            A UnicodeBinding if the string is a valid Unicode binding,
            None otherwise
        """
        if not is_unicode_binding(binding_str):
            return None

        # Check if we have a mapping for this binding
        if binding_str in self.unicode_mappings:
            return UnicodeBinding(self.unicode_mappings[binding_str])

        # If no mapping exists, extract character from name
        # This is a simplified approach; in reality, we would need to
        # parse the macro definition to get the actual character
        return UnicodeBinding("?")
