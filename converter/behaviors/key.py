# -*- coding: utf-8 -*-
"""
Key mapping data model for ZMK to Kanata conversion.
Implements KeyMapping as per the new architecture and data contracts.
"""
from dataclasses import dataclass
from typing import Optional

# TODO: Import the centralized error manager when available
# from converter.error_handling import get_error_manager

@dataclass
class KeyMapping:
    """Represents a key mapping in the keymap."""
    key: str
    sticky: bool = False
    label: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.key, str):
            # TODO: Log error via error manager
            raise TypeError("key must be a string")
        if not isinstance(self.sticky, bool):
            # TODO: Log error via error manager
            raise TypeError("sticky must be a bool")
        if self.label is not None and not isinstance(self.label, str):
            # TODO: Log error via error manager
            raise TypeError("label must be a string or None")

    def to_kanata(self) -> str:
        """Convert the key mapping to Kanata format."""
        # TODO: Implement actual conversion logic
        if self.sticky:
            return f"sticky-{self.key.lower()}"
        return self.key.lower()

# TODO: Integrate with centralized error manager for logging and validation
# TODO: Add any additional methods or integration points as required by the new architecture 