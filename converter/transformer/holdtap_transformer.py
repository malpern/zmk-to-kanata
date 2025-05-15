"""Module for transforming ZMK hold-tap behaviors into Kanata format."""

from typing import Dict, Optional

from ..model.keymap_model import HoldTapBinding, HoldTap


class HoldTapTransformer:
    """Transformer for converting ZMK hold-tap behaviors to Kanata format."""

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

        # Default configuration values
        self.config = {
            "tapping_term_ms": 200,
            "quick_tap_ms": 0,
            "tap_hold_wait_ms": None,
            "require_prior_idle_ms": None,
            "tap_hold_flavor": "hold-preferred",
        }

    def transform_binding(
        self,
        binding: HoldTapBinding,
        tap_time: Optional[int] = None,
        hold_time: Optional[int] = None,
        quick_tap_ms: Optional[int] = None,
        tap_hold_wait_ms: Optional[int] = None,
        require_prior_idle_ms: Optional[int] = None,
        flavor: Optional[str] = None,
    ) -> str:
        """Transform a hold-tap binding to Kanata format.

        Args:
            binding: The hold-tap binding to transform
            tap_time: The tap time in milliseconds (default: from config)
            hold_time: The hold time in milliseconds (default: same as tap_time)
            quick_tap_ms: Optional quick tap time in ms
            tap_hold_wait_ms: Optional tap-hold wait time in ms
            require_prior_idle_ms: Optional prior idle time in ms
            flavor: Optional tap-hold flavor (e.g., "hold-preferred")

        Returns:
            The Kanata format string for the hold-tap binding
        """
        if not binding.hold_tap:
            raise ValueError("HoldTapBinding must have a hold_tap configuration")

        # Use provided values or fall back to binding values then config defaults
        tap_time = (
            tap_time
            if tap_time is not None
            else (
                binding.hold_tap.tapping_term_ms
                if binding.hold_tap.tapping_term_ms is not None
                else self.config["tapping_term_ms"]
            )
        )
        hold_time = (
            hold_time
            if hold_time is not None
            else (
                binding.hold_tap.hold_time_ms
                if binding.hold_tap.hold_time_ms is not None
                else tap_time
            )
        )
        quick_tap_ms = (
            quick_tap_ms
            if quick_tap_ms is not None
            else (
                binding.hold_tap.quick_tap_ms
                if binding.hold_tap.quick_tap_ms is not None
                else self.config["quick_tap_ms"]
            )
        )
        tap_hold_wait_ms = (
            tap_hold_wait_ms
            if tap_hold_wait_ms is not None
            else (
                binding.hold_tap.tap_hold_wait_ms
                if binding.hold_tap.tap_hold_wait_ms is not None
                else self.config["tap_hold_wait_ms"]
            )
        )
        require_prior_idle_ms = (
            require_prior_idle_ms
            if require_prior_idle_ms is not None
            else (
                binding.hold_tap.require_prior_idle_ms
                if binding.hold_tap.require_prior_idle_ms is not None
                else self.config["require_prior_idle_ms"]
            )
        )
        flavor = (
            flavor
            if flavor is not None
            else (
                binding.hold_tap.flavor
                if binding.hold_tap.flavor is not None
                else self.config["tap_hold_flavor"]
            )
        )

        # Convert the hold and tap keys to Kanata format
        hold_key = (
            self.modifier_map.get(binding.hold.upper(), binding.hold.lower())
            if binding.hold
            else None
        )
        tap_key = binding.tap.lower() if binding.tap else None

        if not hold_key or not tap_key:
            raise ValueError("Both hold and tap keys must be specified")

        # Determine the tap-hold variant
        tap_hold_type = self.flavor_map.get(flavor, "tap-hold")

        # Build the tap-hold configuration
        config_parts = [
            tap_hold_type,
            str(tap_time),
            str(hold_time),
            tap_key,
            hold_key,
        ]

        # Add optional parameters if present
        if quick_tap_ms is not None and quick_tap_ms > 0:
            config_parts.append(str(quick_tap_ms))
        if tap_hold_wait_ms is not None:
            if len(config_parts) == 5:  # Add quick_tap_ms if not present
                config_parts.append("0")
            config_parts.append(str(tap_hold_wait_ms))
        if require_prior_idle_ms is not None:
            while len(config_parts) < 7:  # Add missing params if needed
                config_parts.append("0")
            config_parts.append(str(require_prior_idle_ms))

        # Create and return the configuration string
        return f"({' '.join(config_parts)})"

    def transform_behavior(
        self, behavior: HoldTap, hold_param: str, tap_param: str
    ) -> tuple[str, str]:
        """Transform a HoldTap behavior into a Kanata alias definition.

        Args:
            behavior: The HoldTap behavior to transform
            hold_param: The hold key/action (e.g., 'LCTRL', '1' for layer)
            tap_param: The tap key/action

        Returns:
            A tuple of (alias_definition, alias_name) where:
            - alias_definition is the full Kanata alias definition string
            - alias_name is the name of the alias for reference
        """
        # Convert the hold and tap params to Kanata format
        hold_key = self.modifier_map.get(hold_param.upper(), hold_param.lower())
        tap_key = tap_param.lower()

        # Determine the tap-hold variant based on behavior properties
        tap_hold_type = self.flavor_map.get(behavior.flavor, "tap-hold")

        # Build the tap-hold configuration
        config_parts = [
            tap_hold_type,
            str(behavior.tapping_term_ms),
            str(behavior.hold_time_ms or behavior.tapping_term_ms),
            tap_key,
            hold_key,
        ]

        # Add optional parameters if present
        if behavior.quick_tap_ms is not None and behavior.quick_tap_ms > 0:
            config_parts.append(str(behavior.quick_tap_ms))
        if behavior.tap_hold_wait_ms is not None:
            if len(config_parts) == 5:  # Add quick_tap_ms if not present
                config_parts.append("0")
            config_parts.append(str(behavior.tap_hold_wait_ms))
        if behavior.require_prior_idle_ms is not None:
            while len(config_parts) < 7:  # Add missing params if needed
                config_parts.append("0")
            config_parts.append(str(behavior.require_prior_idle_ms))

        # Create the configuration string
        config = f"({' '.join(config_parts)})"

        # Create the full alias definition
        alias_def = f"(defalias {behavior.name} {config})"

        return alias_def, behavior.name
