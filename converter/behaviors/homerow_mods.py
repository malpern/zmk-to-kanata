"""Module for handling homerow mods conversion from ZMK to Kanata.

This module provides support for converting ZMK homerow mods (&hm) to Kanata's
tap-hold functionality, including special handling for Mac-specific modifiers.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class HomeRowModBehavior:
    """Represents a ZMK homerow mod behavior configuration."""
    mod: str  # The modifier (LGUI, LALT, LCTL, LSFT, etc.)
    key: str  # The key to tap (A, S, D, F, etc.)
    tap_time: int = 200  # Default tap time in ms
    hold_time: int = 200  # Default hold time in ms
    is_mac: bool = False  # Whether to use Mac-specific modifiers

    @property
    def kanata_mod(self) -> str:
        """Convert ZMK modifier to Kanata modifier."""
        # Map of ZMK modifiers to Kanata modifiers
        zmk_to_kanata = {
            # Left modifiers
            "LGUI": "lmet" if self.is_mac else "lmet",
            "LALT": "lalt",
            "LCTL": "lctl",
            "LSHFT": "lsft",
            # Right modifiers
            "RGUI": "rmet" if self.is_mac else "rmet",
            "RALT": "ralt",
            "RCTL": "rctl",
            "RSHFT": "rsft",
            # Aliases
            "GUI": "lmet" if self.is_mac else "lmet",
            "ALT": "lalt",
            "CTRL": "lctl",
            "SHIFT": "lsft",
        }
        return zmk_to_kanata.get(self.mod, "lmet")  # Default to lmet if unknown

    def to_kanata(self) -> str:
        """Convert to Kanata tap-hold configuration."""
        return f"(tap-hold {self.tap_time} {self.hold_time} {self.key.lower()} {self.kanata_mod})"


class HomeRowModParser:
    """Parser for ZMK homerow mod bindings."""

    def __init__(self, is_mac: bool = False):
        """Initialize the parser.
        
        Args:
            is_mac: Whether to use Mac-specific modifiers
        """
        self.is_mac = is_mac

    def parse(self, binding_str: str) -> Optional[HomeRowModBehavior]:
        """Parse a ZMK homerow mod binding string.
        
        Args:
            binding_str: The binding string to parse (e.g., "&hm LCTL A")
            
        Returns:
            A HomeRowModBehavior object if the binding is a valid homerow mod,
            None otherwise.
        """
        if not binding_str.startswith("&hm "):
            return None
            
        parts = binding_str.split(maxsplit=2)
        if len(parts) != 3:
            return None
            
        _, mod, key = parts
        return HomeRowModBehavior(
            mod=mod,
            key=key,
            is_mac=self.is_mac
        )


def is_homerow_mod_binding(binding_str: str) -> bool:
    """Check if a binding string is a homerow mod binding.
    
    Args:
        binding_str: The binding string to check
        
    Returns:
        True if the binding string is a homerow mod binding, False otherwise
    """
    return binding_str.startswith("&hm ") 