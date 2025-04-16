"""Unicode Behavior Module

This module provides classes for representing ZMK Unicode behaviors and
bindings.
"""

from typing import Optional

from converter.model.keymap_model import Binding


class UnicodeBinding(Binding):
    """Represents a Unicode binding in ZMK."""

    def __init__(self, character: str):
        """Initialize a Unicode binding.

        Args:
            character: The Unicode character to output
        """
        self.character = character

    def to_kanata(self) -> str:
        """Convert the binding to Kanata format.

        Returns:
            The Kanata representation of the binding
        """
        # Return a properly formatted unicode character reference
        return f"(unicode {self.character})"

    @classmethod
    def from_zmk(cls, zmk_binding: str) -> Optional["UnicodeBinding"]:
        """Create a UnicodeBinding from a ZMK binding string.

        Args:
            zmk_binding: The ZMK binding string

        Returns:
            A UnicodeBinding if the string is a valid Unicode binding,
            None otherwise
        """
        # ZMK doesn't have native Unicode support yet, but we can handle
        # the workaround using macros that output Unicode characters
        if zmk_binding.startswith("&unicode_"):
            # Extract the character from the binding name
            # This is a simplified approach; in reality, we would need to
            # parse the macro definition to get the actual character
            # For now, we'll just use a placeholder
            return cls("?")

        # Handle the urob/zmk-nodefree-config approach
        if zmk_binding.startswith("&pi") or zmk_binding.startswith("&n_tilde"):
            # These are examples from the urob/zmk-nodefree-config approach
            # In reality, we would need to parse the macro definition
            if zmk_binding.startswith("&pi"):
                return cls("π")
            elif zmk_binding.startswith("&n_tilde"):
                return cls("ñ")

        return None


def is_unicode_binding(binding_str: str) -> bool:
    """Check if a binding string is a Unicode binding.

    Args:
        binding_str: The binding string to check

    Returns:
        True if the binding string is a Unicode binding, False otherwise
    """
    return (
        binding_str.startswith("&unicode_")
        or binding_str.startswith("&pi")
        or binding_str.startswith("&n_tilde")
    )
