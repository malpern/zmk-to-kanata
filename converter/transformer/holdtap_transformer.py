"""Module for transforming ZMK hold-tap behaviors into Kanata format."""

from typing import Dict, Optional

from ..model.keymap_model import HoldTapBinding


class HoldTapTransformer:
    """Transforms ZMK hold-tap behaviors into Kanata format."""

    def __init__(self):
        """Initialize the transformer with behavior mappings."""
        # Map ZMK hold-tap flavors to Kanata tap-hold variants
        self.flavor_map: Dict[str, str] = {
            # Default ZMK behavior
            "hold-preferred": "tap-hold",
            # Balanced behavior maps to default
            "balanced": "tap-hold",
            # Release variant for tap preference
            "tap-preferred": "tap-hold-release",
            # Press variant for interruption
            "tap-unless-interrupted": "tap-hold-press",
            # Press with timeout for tap-then-hold
            "tap-then-hold": "tap-hold-press-timeout",
        }

        # Map ZMK modifiers to Kanata format
        self.modifier_map: Dict[str, str] = {
            "LSHIFT": "lsft",
            "RSHIFT": "rsft",
            "LCTRL": "lctl",
            "RCTRL": "rctl",
            "LALT": "lalt",
            "RALT": "ralt",
            "LGUI": "lmet",
            "RGUI": "rmet",
        }

    def transform_binding(
        self,
        binding: HoldTapBinding,
        tap_time: int,
        hold_time: int
    ) -> Optional[str]:
        """Transform a ZMK hold-tap binding into Kanata format.

        Args:
            binding: The hold-tap binding to transform
            tap_time: Global tap timeout in milliseconds
            hold_time: Global hold timeout in milliseconds

        Returns:
            Kanata tap-hold configuration string or None if invalid
        """
        # Get the appropriate tap-hold variant
        tap_hold_type = "tap-hold"  # Default to basic tap-hold

        # Handle advanced features
        if binding.hold_trigger_key_positions:
            # Use tap-hold-release-keys for hold-trigger-key-positions
            tap_hold_type = "tap-hold-release-keys"
        elif binding.hold_trigger_on_release:
            # Use tap-hold-release for hold-trigger-on-release
            tap_hold_type = "tap-hold-release"
        elif binding.retro_tap:
            # Use tap-hold-press-timeout for retro-tap
            tap_hold_type = "tap-hold-press-timeout"

        # Map the hold key (usually a modifier)
        hold_key = self.modifier_map.get(
            binding.hold_key,
            binding.hold_key.lower()
        )

        # Map the tap key
        tap_key = binding.tap_key.lower()

        # Basic tap-hold configuration
        config = (
            f"({tap_hold_type} {tap_time} {hold_time} {tap_key} {hold_key}"
        )

        # Add extra parameters for advanced features
        if tap_hold_type == "tap-hold-release-keys":
            # Convert key positions to a list
            positions = " ".join(
                str(pos) for pos in binding.hold_trigger_key_positions
            )
            config += f" ({positions})"
        elif tap_hold_type == "tap-hold-press-timeout" and binding.retro_tap:
            # Add tap key as timeout action for retro-tap
            config += f" {tap_key}"

        # Close the configuration
        config += ")"

        return config
