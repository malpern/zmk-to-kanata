"""Module for handling key behaviors in ZMK.

This module provides classes for representing key behaviors in ZMK.
"""

from dataclasses import dataclass

from converter.model.binding import Binding


@dataclass
class KeyMapping(Binding):
    """Represents a key mapping in the keymap."""

    key: str
    sticky: bool = False

    def to_kanata(self) -> str:
        """Convert the key mapping to Kanata format."""
        # Map ZMK modifier names to Kanata format
        mod_map = {
            "LSHIFT": "lsft",
            "RSHIFT": "rsft",
            "LCTRL": "lctl",
            "RCTRL": "rctl",
            "LALT": "lalt",
            "RALT": "ralt",
            "LGUI": "lmet",
            "RGUI": "rmet",
        }

        key = mod_map.get(self.key, self.key.lower())
        return key
