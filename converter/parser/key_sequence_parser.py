"""Parser module for ZMK key sequence behavior."""

from typing import Dict, Optional

from converter.behaviors.key_sequence import KeySequenceBinding


class KeySequenceParser:
    """Parser for ZMK key sequence behavior and bindings."""

    def __init__(self):
        self.behaviors: Dict[str, str] = {}

    def parse_behavior(
        self,
        name: str,
        config: dict
    ) -> None:
        """Parse a key sequence behavior configuration."""
        if config.get('compatible') == '"zmk,behavior-key-sequence"':
            # Store the behavior name for later reference
            self.behaviors[name] = name

    def parse_binding(self, binding_str: str) -> Optional[KeySequenceBinding]:
        """Parse a key sequence binding string."""
        if not binding_str.startswith('&key_sequence'):
            return None

        try:
            return KeySequenceBinding.from_zmk(binding_str)
        except ValueError:
            # If we can't parse it as a key sequence binding, return None
            return None 