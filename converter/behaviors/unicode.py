"""Unicode Behavior Module.

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
        # Normalize the binding string
        binding = zmk_binding.strip().rstrip(";")
        # ZMK doesn't have native Unicode support yet, but we can handle
        # the workaround using macros that output Unicode characters
        if binding.startswith("&unicode_"):
            return cls("?")
        if binding == "&pi":
            return cls("π")
        if binding == "&n_tilde":
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
