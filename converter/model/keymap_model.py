"""Keymap Model Module

This module contains the intermediate representation classes for our keymap
converter.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class GlobalSettings:
    """Global keymap settings."""
    tap_time: int
    hold_time: int


@dataclass(frozen=True)
class HoldTapBinding:
    """Represents a hold-tap binding with its behavior and parameters."""
    behavior_name: str  # e.g., "lh_hm", "rh_hm"
    hold_key: str      # e.g., "LGUI", "LALT"
    tap_key: str       # e.g., "A", "S"
    # Key positions that trigger hold
    hold_trigger_key_positions: Optional[Tuple[int, ...]] = None
    # Whether to trigger hold on key release
    hold_trigger_on_release: bool = False
    # Whether to allow tap on release after hold timeout
    retro_tap: bool = False


@dataclass
class KeyMapping:
    """Represents a single key mapping."""
    key: str  # For basic key press (e.g., "A", "B")
    hold_tap: Optional[HoldTapBinding] = None  # For hold-tap behavior

    def __eq__(self, other):
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key


@dataclass
class Layer:
    """Represents a layer with its name and key bindings."""
    name: str
    keys: List[List[KeyMapping]]


@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""
    global_settings: GlobalSettings
    layers: List[Layer]