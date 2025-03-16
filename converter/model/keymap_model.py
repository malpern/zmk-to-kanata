"""Keymap Model Module

This module contains the intermediate representation classes for our keymap
converter.

TODO(tech-debt): This file will become the single source of truth for keymap
models. Currently, there is duplicate functionality in 
converter/keymap_model.py which will eventually be merged into this file. 
The plan is to:

1. Move all conversion logic (to_kanata methods) here
2. Update the root keymap_model.py to re-export from this file
3. Eventually remove the root version

This file contains the more complete model with GlobalSettings and
KeymapConfig, while the root version has the conversion logic. These will be
unified here.

See plan.md Task 26 for full details.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple


class Binding:
    """Base class for all key bindings."""
    def to_kanata(self) -> str:
        """Convert the binding to Kanata format."""
        raise NotImplementedError


@dataclass
class GlobalSettings:
    """Global keymap settings."""
    tap_time: int
    hold_time: int


@dataclass
class HoldTap:
    """Hold-tap key binding."""
    behavior_name: str
    hold_key: str
    tap_key: str

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        # Convert hold key to short form
        hold_key = self.hold_key.lower()
        # Map modifier keys to their short forms
        mod_map = {
            'lshift': 'lsft',
            'rshift': 'rsft',
            'lcontrol': 'lctl',
            'rcontrol': 'rctl',
            'lctrl': 'lctl',
            'rctrl': 'rctl',
            'lgui': 'lmet',
            'rgui': 'rmet'
        }
        if hold_key in mod_map:
            hold_key = mod_map[hold_key]

        # Convert tap key
        tap_key = self.tap_key.lower()
        if tap_key.startswith('n') and tap_key[1:].isdigit():
            tap_key = tap_key[1:]  # Remove 'n' prefix for number keys

        return f"tap-hold {hold_key} {tap_key}"


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

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        # Convert hold key to short form
        hold_key = self.hold_key.lower()
        if hold_key == 'lshift':
            hold_key = 'lsft'
        elif hold_key == 'rshift':
            hold_key = 'rsft'
        elif hold_key == 'lcontrol':
            hold_key = 'lctl'
        elif hold_key == 'rcontrol':
            hold_key = 'rctl'
        elif hold_key == 'lctrl':
            hold_key = 'lctl'
        elif hold_key == 'rctrl':
            hold_key = 'rctl'
        elif hold_key == 'lgui':
            hold_key = 'lmet'
        elif hold_key == 'rgui':
            hold_key = 'rmet'

        # Convert tap key
        tap_key = self.tap_key.lower()
        if tap_key.startswith('n') and tap_key[1:].isdigit():
            tap_key = tap_key[1:]  # Remove 'n' prefix for number keys

        return f"tap-hold {hold_key} {tap_key}"


@dataclass
class KeyMapping(Binding):
    """Represents a single key mapping."""
    key: str  # For basic key press (e.g., "A", "B")
    hold_tap: Optional[HoldTap] = None  # For hold-tap behavior

    def __eq__(self, other):
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        if self.hold_tap:
            return self.hold_tap.to_kanata()

        if not self.key:
            return "_"  # Use _ for transparent keys

        key = self.key.lower()

        # Handle sticky keys
        if key.startswith('sk '):
            mod = key[3:]  # Remove 'sk ' prefix
            # Map modifier keys to their short forms
            mod_map = {
                'lshift': 'lsft',
                'rshift': 'rsft',
                'lcontrol': 'lctl',
                'rcontrol': 'rctl',
                'lctrl': 'lctl',
                'rctrl': 'rctl',
                'lgui': 'lmet',
                'rgui': 'rmet'
            }
            if mod in mod_map:
                mod = mod_map[mod]
            return f"sticky-{mod}"

        # Handle layer switches
        if key.startswith('mo '):
            layer_num = key[3:]  # Remove 'mo ' prefix
            return f"@layer{layer_num}"

        # Handle number keys
        if key.startswith('n') and key[1:].isdigit():
            return key[1:]  # Remove 'n' prefix

        # Handle transparent keys
        if key == 'trans':
            return "_"

        return key


@dataclass
class Layer(Binding):
    """Represents a layer with its name and key bindings."""
    name: str
    keys: List[List[KeyMapping]]

    def to_kanata(self) -> str:
        """Convert the layer to Kanata format."""
        # Convert bindings to Kanata format
        kanata_rows = []
        for row in self.keys:
            kanata_row = []
            for binding in row:
                if binding is None:
                    kanata_row.append('_')  # Transparent key
                else:
                    kanata_row.append(binding.to_kanata())
            kanata_rows.append('  ' + ' '.join(kanata_row))

        # Format the layer definition
        return (
            f"(deflayer {self.name}\n"
            f"{chr(10).join(kanata_rows)}\n"
            ")"
        )


@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""
    global_settings: GlobalSettings
    layers: List[Layer]