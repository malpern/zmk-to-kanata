"""Module for handling ZMK key sequence behavior conversion."""

from dataclasses import dataclass
from typing import List, Optional

from converter.model.keymap_model import Binding


@dataclass
class KeySequenceBehavior:
    """Model for ZMK key sequence behavior.

    Attributes:
        wait_ms: Delay between key presses in milliseconds
        tap_ms: Duration of key press in milliseconds
        bindings: List of keys in the sequence
    """

    wait_ms: int = 30
    tap_ms: int = 30
    bindings: List[str] = None

    def __post_init__(self):
        """Validate the behavior configuration."""
        if self.wait_ms < 0:
            raise ValueError("wait_ms must be non-negative")
        if self.tap_ms < 0:
            raise ValueError("tap_ms must be non-negative")
        # Initialize empty bindings list if None
        if self.bindings is None:
            self.bindings = []
        # Validate that bindings list is not empty when explicitly provided
        elif not self.bindings:
            raise ValueError("bindings list cannot be empty")


class KeySequenceBinding(Binding):
    """Represents a key sequence binding in the keymap."""

    # Map ZMK key names to Kanata format
    key_mapping = {
        "LSHIFT": "lsft",
        "RSHIFT": "rsft",
        "LCTRL": "lctl",
        "RCTRL": "rctl",
        "LALT": "lalt",
        "RALT": "ralt",
        "LGUI": "lmet",
        "RGUI": "rmet",
        "ENTER": "ret",
        "SPACE": "spc",
        "TAB": "tab",
        "ESCAPE": "esc",
        "BACKSPACE": "bspc",
        "DELETE": "del",
    }

    def __init__(
        self, keys: List[str], behavior: Optional[KeySequenceBehavior] = None
    ):
        self.keys = keys
        self.behavior = behavior or KeySequenceBehavior()

    def to_kanata(self) -> str:
        """Convert the key sequence binding to Kanata format."""
        # Kanata uses (chord ...) for key sequences
        # Convert each key using the mapping or lowercase
        key_str = " ".join(
            self.key_mapping.get(k, k.lower()) for k in self.keys
        )
        return f"(chord {key_str})"

    @classmethod
    def from_zmk(
        cls, zmk_binding: str, behavior: Optional[KeySequenceBehavior] = None
    ) -> "KeySequenceBinding":
        """Create a KeySequenceBinding from a ZMK binding string."""
        # Remove &key_sequence prefix and any whitespace
        keys_str = zmk_binding.replace("&key_sequence", "").strip()

        # Split into individual keys and clean up
        keys = [k.strip() for k in keys_str.split()]

        # Convert ZMK key names to Kanata format
        keys = [cls.key_mapping.get(k, k.lower()) for k in keys]
        return cls(keys, behavior)


def is_key_sequence_binding(binding_str: str) -> bool:
    """Check if a binding string represents a key sequence."""
    return binding_str.strip().startswith("&key_sequence")


def parse_key_sequence_behavior(config: dict) -> KeySequenceBehavior:
    """Parse ZMK key sequence behavior configuration."""
    wait_ms = int(config.get("wait-ms", 30))
    tap_ms = int(config.get("tap-ms", 30))

    # Parse bindings if present
    bindings = []
    if "bindings" in config:
        bindings_str = config["bindings"].strip("<>").strip()
        # Split by comma and clean up each binding
        bindings = [
            b.strip().replace("&", "").strip() for b in bindings_str.split(",")
        ]

    return KeySequenceBehavior(
        wait_ms=wait_ms, tap_ms=tap_ms, bindings=bindings
    )
