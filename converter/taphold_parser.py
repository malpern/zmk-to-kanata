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
        'tap-preferred',
        'hold-preferred',
        'balanced',
        'tap-unless-interrupted'
    }

    def __init__(self):
        # Basic property patterns
        self.name_pattern = re.compile(r'(\w+):\s*\w+\s*{')
        self.label_pattern = re.compile(r'label\s*=\s*"([^"]+)"')
        self.cells_pattern = re.compile(r'#binding-cells\s*=\s*<(\d+)>')
        self.binding_pattern = re.compile(r'<&(\w+)>')
        self.compatible_pattern = re.compile(
            r'compatible\s*=\s*"zmk,behavior-hold-tap"'
        )

        # Configuration patterns
        self.tapping_term_pattern = re.compile(
            r'tapping-term-ms\s*=\s*<(\d+)>'
        )
        self.quick_tap_pattern = re.compile(
            r'quick-tap-ms\s*=\s*<(\d+)>'
        )
        self.prior_idle_pattern = re.compile(
            r'require-prior-idle-ms\s*=\s*<(\d+)>'
        )
        self.flavor_pattern = re.compile(r'flavor\s*=\s*"([^"]+)"')

        # Advanced feature patterns
        self.key_positions_pattern = re.compile(
            r'hold-trigger-key-positions\s*=\s*<([^>]+)>'
        )
        self.hold_trigger_release_pattern = re.compile(
            r'hold-trigger-on-release\s*;'
        )
        self.retro_tap_pattern = re.compile(r'retro-tap\s*;')

    def parse_behavior(self, zmk_config: str) -> HoldTapBehavior:
        """Parse a ZMK hold-tap behavior definition."""
        # Check if this is a hold-tap behavior
        if not self.compatible_pattern.search(zmk_config):
            raise ValueError("Not a hold-tap behavior")

        # Extract behavior name
        name_match = self.name_pattern.search(zmk_config)
        if not name_match:
            raise ValueError("Missing behavior name")
        name = name_match.group(1)

        # Extract required fields
        label_match = self.label_pattern.search(zmk_config)
        cells_match = self.cells_pattern.search(zmk_config)

        # Find bindings line
        bindings_line = re.search(r'bindings\s*=\s*([^;]+);', zmk_config)

        if not all([label_match, cells_match, bindings_line]):
            raise ValueError("Missing required fields in hold-tap behavior")

        # Parse bindings
        bindings_str = bindings_line.group(1)
        bindings = []
        for match in self.binding_pattern.finditer(bindings_str):
            binding = match.group(1)
            bindings.append(binding)

        # Parse configuration parameters
        tapping_term = self._parse_int_param(
            self.tapping_term_pattern, zmk_config
        )
        quick_tap = self._parse_int_param(
            self.quick_tap_pattern, zmk_config
        )
        prior_idle = self._parse_int_param(
            self.prior_idle_pattern, zmk_config
        )

        # Parse and validate flavor
        flavor = None
        flavor_match = self.flavor_pattern.search(zmk_config)
        if flavor_match:
            flavor = flavor_match.group(1)
            if flavor not in self.VALID_FLAVORS:
                raise ValueError(
                    f"Invalid flavor '{flavor}'. "
                    f"Must be one of: {', '.join(self.VALID_FLAVORS)}"
                )

        # Parse advanced features
        key_positions = self._parse_key_positions(zmk_config)
        hold_trigger_on_release = bool(
            self.hold_trigger_release_pattern.search(zmk_config)
        )
        retro_tap = bool(self.retro_tap_pattern.search(zmk_config))

        return HoldTapBehavior(
            name=name,
            label=label_match.group(1),
            binding_cells=int(cells_match.group(1)),
            bindings=bindings,
            tapping_term_ms=tapping_term,
            quick_tap_ms=quick_tap,
            require_prior_idle_ms=prior_idle,
            flavor=flavor,
            hold_trigger_key_positions=key_positions,
            hold_trigger_on_release=hold_trigger_on_release,
            retro_tap=retro_tap
        )

    def _parse_int_param(
        self, pattern: re.Pattern, config: str
    ) -> Optional[int]:
        """Helper method to parse integer parameters from config."""
        match = pattern.search(config)
        return int(match.group(1)) if match else None

    def _parse_key_positions(self, config: str) -> Optional[List[int]]:
        """Parse hold-trigger-key-positions array."""
        match = self.key_positions_pattern.search(config)
        if not match:
            return None

        try:
            # Split on whitespace and filter out empty strings
            positions = [pos for pos in match.group(1).split() if pos]
            # Convert to integers, removing any trailing commas
            return [int(pos.rstrip(',')) for pos in positions]
        except ValueError as e:
            raise ValueError(
                f"Invalid key position value in "
                f"hold-trigger-key-positions: {e}"
            )

    @staticmethod
    def parse_tap_hold_behavior(behavior_text: str) -> Dict:
        """Parse a tap-hold behavior definition from ZMK config.

        Args:
            behavior_text: String containing the behavior definition

        Returns:
            Dictionary with parsed behavior properties
        """

# Alias for backward compatibility
HoldTapParser = TapHoldParser

def is_hold_tap_binding(binding_str: str) -> bool:
    """Check if a binding string is a hold-tap binding."""
    return binding_str.startswith("&ht") or binding_str.startswith("&lt") or binding_str.startswith("&mt")
