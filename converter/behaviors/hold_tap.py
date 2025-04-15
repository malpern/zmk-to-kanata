"""Module for handling hold-tap behaviors in ZMK.

This module provides classes for representing hold-tap behaviors in ZMK.
"""

from dataclasses import dataclass
from typing import Optional

from converter.model.binding import Binding  # Using a relative import to avoid circular imports


@dataclass
class HoldTapBinding(Binding):
    """Represents a hold-tap binding in ZMK."""
    
    behavior_name: str  # e.g., "mt", "lt", "ht", "hm", etc.
    hold_key: str  # The key to activate when held
    tap_key: str  # The key to activate when tapped
    
    def to_kanata(self) -> str:
        """Convert the hold-tap binding to Kanata format."""
        # Map different hold-tap behaviors to Kanata formats
        if self.behavior_name == "mt":  # mod-tap
            # Convert ZMK modifier to Kanata modifier
            mod_map = {
                "LSHIFT": "lsft", "RSHIFT": "rsft",
                "LCTRL": "lctl", "RCTRL": "rctl",
                "LALT": "lalt", "RALT": "ralt",
                "LGUI": "lmet", "RGUI": "rmet"
            }
            mod = mod_map.get(self.hold_key, self.hold_key.lower())
            return f"(tap-hold 200 200 {self.tap_key.lower()} {mod})"
        
        elif self.behavior_name == "lt":  # layer-tap
            return f"(layer-while-held {self.hold_key} {self.tap_key.lower()})"
        
        # Generic hold-tap format for other behaviors
        return f"(tap-hold 200 200 {self.tap_key.lower()} {self.hold_key.lower()})"


@dataclass
class HoldTap:
    """Factory class for creating hold-tap bindings."""
    
    behavior_name: str
    hold_key: str
    tap_key: str
    timing_ms: Optional[int] = 200
    
    def create_binding(self) -> HoldTapBinding:
        """Create a hold-tap binding with the specified parameters."""
        return HoldTapBinding(
            behavior_name=self.behavior_name,
            hold_key=self.hold_key,
            tap_key=self.tap_key
        ) 