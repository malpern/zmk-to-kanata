"""Module for handling layer behaviors in ZMK.

This module provides classes for representing layer behaviors in ZMK.
"""

from dataclasses import dataclass


@dataclass
class LayerBehavior:
    """Represents a layer behavior in ZMK."""

    behavior_name: str  # e.g., "mo", "to", "tog", etc.
    layer_index: int  # The layer index

    def to_kanata(self) -> str:
        """Convert the layer behavior to Kanata format."""
        if self.behavior_name == "mo":  # momentary layer
            return f"(layer-while-held {self.layer_index})"
        elif self.behavior_name == "to":  # switch to layer
            return f"(layer-switch {self.layer_index})"
        elif self.behavior_name == "tog":  # toggle layer
            return f"(layer-toggle {self.layer_index})"

        # Default case
        return f"({self.behavior_name} {self.layer_index})"
