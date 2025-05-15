# -*- coding: utf-8 -*-
"""
Hold-tap data models and contracts for ZMK to Kanata conversion.
Implements HoldTap, HoldTapBinding, and HoldTapBehavior as per the new architecture.
"""
from dataclasses import dataclass
from typing import List, Optional

# TODO: Import the centralized error manager when available
# from converter.error_handling import get_error_manager

# HoldTap and HoldTapBinding classes removed to avoid duplication.


@dataclass
class HoldTapBehavior:
    """Represents a ZMK hold-tap behavior configuration (for a whole behavior, not just a single key)."""

    name: str
    label: str
    binding_cells: int
    bindings: List[str]
    tapping_term_ms: Optional[int] = None
    quick_tap_ms: Optional[int] = None
    require_prior_idle_ms: Optional[int] = None
    flavor: Optional[str] = None  # tap-preferred, hold-preferred, or balanced
    hold_trigger_key_positions: Optional[List[int]] = None
    hold_trigger_on_release: bool = False
    retro_tap: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str):
            # TODO: Log error via error manager
            raise TypeError("name must be a string")
        if not isinstance(self.label, str):
            # TODO: Log error via error manager
            raise TypeError("label must be a string")
        if not isinstance(self.binding_cells, int):
            # TODO: Log error via error manager
            raise TypeError("binding_cells must be an int")
        if not isinstance(self.bindings, list):
            # TODO: Log error via error manager
            raise TypeError("bindings must be a list of strings")
        for b in self.bindings:
            if not isinstance(b, str):
                # TODO: Log error via error manager
                raise TypeError("Each binding must be a string")
        if self.tapping_term_ms is not None and not isinstance(
            self.tapping_term_ms, int
        ):
            # TODO: Log error via error manager
            raise TypeError("tapping_term_ms must be int or None")
        if self.quick_tap_ms is not None and not isinstance(self.quick_tap_ms, int):
            # TODO: Log error via error manager
            raise TypeError("quick_tap_ms must be int or None")
        if self.require_prior_idle_ms is not None and not isinstance(
            self.require_prior_idle_ms, int
        ):
            # TODO: Log error via error manager
            raise TypeError("require_prior_idle_ms must be int or None")
        if self.flavor is not None and not isinstance(self.flavor, str):
            # TODO: Log error via error manager
            raise TypeError("flavor must be str or None")
        if self.hold_trigger_key_positions is not None and not isinstance(
            self.hold_trigger_key_positions, list
        ):
            # TODO: Log error via error manager
            raise TypeError("hold_trigger_key_positions must be a list of ints or None")
        if self.hold_trigger_key_positions:
            for pos in self.hold_trigger_key_positions:
                if not isinstance(pos, int):
                    # TODO: Log error via error manager
                    raise TypeError("Each hold_trigger_key_position must be an int")
        if not isinstance(self.hold_trigger_on_release, bool):
            # TODO: Log error via error manager
            raise TypeError("hold_trigger_on_release must be a bool")
        if not isinstance(self.retro_tap, bool):
            # TODO: Log error via error manager
            raise TypeError("retro_tap must be a bool")

    # Optionally, add a to_kanata() method if needed for the whole behavior
    def to_kanata(self) -> str:
        # TODO: Implement actual conversion logic for the full behavior
        return f"(holdtap-behavior {self.name} {self.label} {self.binding_cells} {self.bindings})"


# TODO: Integrate with centralized error manager for logging and validation
# TODO: Add any additional methods or integration points as required by the new architecture
