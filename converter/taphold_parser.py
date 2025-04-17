"""Parser for ZMK tap-hold behavior configurations."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class HoldTapBehavior:
    """Represents a ZMK hold-tap behavior configuration."""

    name: str
    label: str
    binding_cells: int
    bindings: List[str]
    # Basic configuration parameters
    tapping_term_ms: Optional[int] = None
    quick_tap_ms: Optional[int] = None
    require_prior_idle_ms: Optional[int] = None
    flavor: Optional[str] = None  # tap-preferred, hold-preferred, or balanced
    # Advanced features
    hold_trigger_key_positions: Optional[List[int]] = None
    hold_trigger_on_release: bool = False
    retro_tap: bool = False


class TapHoldParser:
    """Parser for ZMK tap-hold behavior configurations."""

    VALID_FLAVORS = {
        "tap-preferred",
        "hold-preferred",
        "balanced",
        "tap-unless-interrupted",
    }

    # Known custom hold-tap behaviors
    CUSTOM_BEHAVIORS = {
        "hm": "homerow_mods",  # Ben Vallack's homerow mods
        "hs": "homerow_shifts",  # Ben Vallack's homerow shifts
        "td": "tapdance",  # Ben Vallack's tapdance
    }

    def __init__(self):
        # Basic property patterns
        self.name_pattern = re.compile(r"(\w+):\s*\w+\s*{")
        self.label_pattern = re.compile(r'label\s*=\s*"([^"]+)"')
        self.cells_pattern = re.compile(r"#binding-cells\s*=\s*<(\d+)>")
        self.binding_pattern = re.compile(r"<&(\w+)>")
        self.compatible_pattern = re.compile(
            r'compatible\s*=\s*"zmk,behavior-hold-tap"'
        )

        # Configuration patterns
        self.tapping_term_pattern = re.compile(r"tapping-term-ms\s*=\s*<(\d+)>")
        self.quick_tap_pattern = re.compile(r"quick-tap-ms\s*=\s*<(\d+)>")
        self.require_prior_idle_pattern = re.compile(
            r"require-prior-idle-ms\s*=\s*<(\d+)>"
        )
        self.flavor_pattern = re.compile(r'flavor\s*=\s*"([^"]+)"')
        self.hold_trigger_positions_pattern = re.compile(
            r"hold-trigger-key-positions\s*=\s*<([^>]+)>"
        )
        self.hold_trigger_on_release_pattern = re.compile(r"hold-trigger-on-release")
        self.retro_tap_pattern = re.compile(r"retro-tap")

        # Registry for custom behaviors
        self.behavior_registry: Dict[str, HoldTapBehavior] = {}

    def register_behavior(self, behavior: HoldTapBehavior) -> None:
        """Register a behavior in the registry.

        Args:
            behavior: The behavior to register
        """
        self.behavior_registry[behavior.name] = behavior

        # Also register any known aliases for this behavior
        for alias, full_name in self.CUSTOM_BEHAVIORS.items():
            if behavior.name == full_name:
                self.behavior_registry[alias] = behavior

    def get_behavior(self, name: str) -> Optional[HoldTapBehavior]:
        """Get a behavior from the registry by name.

        Args:
            name: The name of the behavior to get

        Returns:
            The behavior if found, None otherwise
        """
        return self.behavior_registry.get(name)

    def is_registered_behavior(self, name: str) -> bool:
        """Check if a behavior is registered.

        Args:
            name: The name of the behavior to check

        Returns:
            True if the behavior is registered, False otherwise
        """
        return name in self.behavior_registry

    def parse_behavior(self, zmk_config: str) -> HoldTapBehavior:
        """Parse a ZMK hold-tap behavior configuration.

        Args:
            zmk_config: The ZMK configuration string

        Returns:
            A HoldTapBehavior object

        Raises:
            ValueError: If the configuration is invalid
        """
        # Check if this is a hold-tap behavior
        if not self.compatible_pattern.search(zmk_config):
            raise ValueError("Not a hold-tap behavior: missing compatible string")

        # Extract basic properties
        name_match = self.name_pattern.search(zmk_config)
        if not name_match:
            raise ValueError("Invalid behavior: missing name")
        name = name_match.group(1)

        label_match = self.label_pattern.search(zmk_config)
        label = label_match.group(1) if label_match else name

        cells_match = self.cells_pattern.search(zmk_config)
        if not cells_match:
            raise ValueError("Invalid behavior: missing binding-cells")
        binding_cells = int(cells_match.group(1))

        # Extract bindings
        bindings = []
        for match in self.binding_pattern.finditer(zmk_config):
            bindings.append(match.group(1))

        # Extract configuration parameters
        tapping_term = self._parse_int_param(self.tapping_term_pattern, zmk_config)
        quick_tap = self._parse_int_param(self.quick_tap_pattern, zmk_config)
        prior_idle = self._parse_int_param(self.require_prior_idle_pattern, zmk_config)

        flavor_match = self.flavor_pattern.search(zmk_config)
        flavor = flavor_match.group(1) if flavor_match else None

        if flavor and flavor not in self.VALID_FLAVORS:
            raise ValueError(f"Invalid flavor: {flavor}")

        # Extract advanced features
        key_positions = self._parse_key_positions(zmk_config)
        hold_trigger_on_release = bool(
            self.hold_trigger_on_release_pattern.search(zmk_config)
        )
        retro_tap = bool(self.retro_tap_pattern.search(zmk_config))

        # Create and register the behavior
        behavior = HoldTapBehavior(
            name=name,
            label=label,
            binding_cells=binding_cells,
            bindings=bindings,
            tapping_term_ms=tapping_term,
            quick_tap_ms=quick_tap,
            require_prior_idle_ms=prior_idle,
            flavor=flavor,
            hold_trigger_key_positions=key_positions,
            hold_trigger_on_release=hold_trigger_on_release,
            retro_tap=retro_tap,
        )

        # Register the behavior in the registry
        self.register_behavior(behavior)

        return behavior

    def _parse_int_param(self, pattern: re.Pattern, config: str) -> Optional[int]:
        """Helper method to parse integer parameters from config."""
        match = pattern.search(config)
        return int(match.group(1)) if match else None

    def _parse_key_positions(self, config: str) -> Optional[List[int]]:
        """Parse hold-trigger-key-positions array."""
        match = self.hold_trigger_positions_pattern.search(config)
        if not match:
            return None

        try:
            # Split on whitespace and filter out empty strings
            positions = [pos for pos in match.group(1).split() if pos]
            # Convert to integers, removing any trailing commas
            return [int(pos.rstrip(",")) for pos in positions]
        except ValueError as e:
            raise ValueError(
                f"Invalid key position value in " f"hold-trigger-key-positions: {e}"
            )

    @staticmethod
    def parse_tap_hold_behavior(behavior_text: str) -> Dict:
        """Parse a tap-hold behavior definition from ZMK config.

        Args:
            behavior_text: String containing the behavior definition

        Returns:
            Dictionary with parsed behavior properties
        """
        pass  # Implementation to be added


# Alias for backward compatibility
HoldTapParser = TapHoldParser


def is_hold_tap_binding(binding_str: str) -> bool:
    """Check if a binding string is a hold-tap binding.

    Args:
        binding_str: The binding string to check

    Returns:
        True if the binding string is a hold-tap binding, False otherwise
    """
    # Standard hold-tap prefixes
    standard_prefixes = ["&ht", "&lt", "&mt"]

    # Custom hold-tap prefixes from Ben Vallack's keymap
    custom_prefixes = ["&hm", "&hs", "&td"]

    # Check if the binding starts with any of the prefixes
    for prefix in standard_prefixes + custom_prefixes:
        if binding_str.startswith(prefix):
            return True

    return False
