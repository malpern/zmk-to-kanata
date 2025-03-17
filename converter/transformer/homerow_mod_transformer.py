"""Module for transforming ZMK homerow mods to Kanata format."""

from typing import Optional
from converter.behaviors.homerow_mods import HomeRowModBehavior


class HomeRowModTransformer:
    """Transformer for ZMK homerow mods."""

    def __init__(self, is_mac: bool = False):
        """Initialize the transformer.
        
        Args:
            is_mac: Whether to use Mac-specific modifiers
        """
        self.is_mac = is_mac
        self.tap_time = 200  # Default tap time in ms
        self.hold_time = 200  # Default hold time in ms

    def set_timing_parameters(self, tap_time: int, hold_time: int) -> None:
        """Set the timing parameters for the transformer.
        
        Args:
            tap_time: The tap time in ms
            hold_time: The hold time in ms
        """
        self.tap_time = tap_time
        self.hold_time = hold_time

    def transform_binding(self, behavior: HomeRowModBehavior) -> str:
        """Transform a homerow mod behavior to Kanata format.
        
        Args:
            behavior: The homerow mod behavior to transform
            
        Returns:
            The Kanata representation of the homerow mod
        """
        # Update the behavior's timing parameters
        behavior.tap_time = self.tap_time
        behavior.hold_time = self.hold_time
        behavior.is_mac = self.is_mac
        
        return behavior.to_kanata() 