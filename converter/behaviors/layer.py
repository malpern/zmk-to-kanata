# -*- coding: utf-8 -*-
"""
Layer behavior data model for ZMK to Kanata conversion.
Implements LayerBehavior as per the new architecture and data contracts.
"""
from dataclasses import dataclass
from typing import Optional

# TODO: Import the centralized error manager when available
# from converter.error_handling import get_error_manager

@dataclass
class LayerBehavior:
    """Represents a layer-switching behavior (e.g., momentary, toggle, to-layer)."""
    name: str
    layer_num: int
    behavior_type: str  # e.g., 'mo', 'to', 'tog'
    label: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.name, str):
            # TODO: Log error via error manager
            raise TypeError("name must be a string")
        if not isinstance(self.layer_num, int):
            # TODO: Log error via error manager
            raise TypeError("layer_num must be an int")
        if not isinstance(self.behavior_type, str):
            # TODO: Log error via error manager
            raise TypeError("behavior_type must be a string")
        if self.label is not None and not isinstance(self.label, str):
            # TODO: Log error via error manager
            raise TypeError("label must be a string or None")

    def to_kanata(self) -> str:
        """Convert to Kanata S-expression format for layer switching."""
        # TODO: Implement actual conversion logic based on behavior_type
        if self.behavior_type == 'mo':
            return f"(layer-while-held {self.layer_num})"
        elif self.behavior_type == 'to':
            return f"(layer-switch {self.layer_num})"
        elif self.behavior_type == 'tog':
            return f"(layer-toggle {self.layer_num})"
        else:
            # TODO: Log error via error manager
            return f"(unknown-layer-behavior {self.behavior_type} {self.layer_num})"

# TODO: Integrate with centralized error manager for logging and validation
# TODO: Add any additional methods or integration points as required by the new architecture 