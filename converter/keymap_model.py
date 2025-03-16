"""Data models for keyboard mapping."""

from dataclasses import dataclass
from typing import List, Optional


class Binding:
    """Base class for all key bindings."""
    def to_kanata(self) -> str:
        """Convert the binding to Kanata format."""
        raise NotImplementedError


@dataclass
class HoldTap:
    """Represents a hold-tap key binding."""
    def __init__(self, behavior_name: str, hold_key: str, tap_key: str):
        self.behavior_name = behavior_name
        self.hold_key = hold_key
        self.tap_key = tap_key

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
    """Represents a key mapping."""
    def __init__(self, key: str = None, hold_tap: HoldTap = None):
        self.key = key
        self.hold_tap = hold_tap

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
            if mod == 'lshift':
                mod = 'lsft'
            elif mod == 'rshift':
                mod = 'rsft'
            elif mod == 'lcontrol':
                mod = 'lctl'
            elif mod == 'rcontrol':
                mod = 'rctl'
            elif mod == 'lctrl':
                mod = 'lctl'
            elif mod == 'rctrl':
                mod = 'rctl'
            elif mod == 'lgui':
                mod = 'lmet'
            elif mod == 'rgui':
                mod = 'rmet'
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
class Layer:
    """Represents a keyboard layer with its bindings."""
    name: str
    keys: List[List[Optional[Binding]]]

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