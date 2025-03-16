"""Keymap Model Module

This module contains the intermediate representation classes for our keymap
converter.

This file is the single source of truth for keymap models. It contains
all the model classes and conversion logic for the keymap converter.
"""

from dataclasses import dataclass, field
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
    """Represents a hold-tap behavior in ZMK."""
    behavior_name: str
    hold_key: str
    tap_key: str

    def to_kanata(self) -> str:
        """Convert the hold-tap to Kanata format."""
        # Convert hold_key to short form if needed
        hold_key = self.hold_key
        if hold_key == 'LSHIFT':
            hold_key = 'lsft'
        elif hold_key == 'RSHIFT':
            hold_key = 'rsft'
        elif hold_key == 'LCTRL':
            hold_key = 'lctl'
        elif hold_key == 'RCTRL':
            hold_key = 'rctl'
        elif hold_key == 'LALT':
            hold_key = 'lalt'
        elif hold_key == 'RALT':
            hold_key = 'ralt'
        elif hold_key == 'LGUI':
            hold_key = 'lmet'
        elif hold_key == 'RGUI':
            hold_key = 'rmet'

        # Convert tap_key if needed
        tap_key = self.tap_key
        # Remove leading 'n' from number keys if followed by digits
        if tap_key.startswith('N') and tap_key[1:].isdigit():
            tap_key = tap_key[1:]

        return f"tap-hold {hold_key} {tap_key.lower()}"


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
    """Represents a key mapping in the keymap."""
    key: str
    hold_tap: Optional[HoldTap] = None
    sticky: bool = False

    def __eq__(self, other):
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key

    def to_kanata(self) -> str:
        """Convert the key mapping to Kanata format."""
        if self.hold_tap:
            # Use the alias we created for this hold-tap binding
            binding_id = (
                f"{self.hold_tap.behavior_name}_"
                f"{self.hold_tap.hold_key}_"
                f"{self.hold_tap.tap_key}"
            )
            return f"@{binding_id}"

        if self.key.startswith("mo "):
            # Handle momentary layer switch
            layer_num = self.key.split()[1]
            return f"(layer-while-held {layer_num})"
        elif self.key == "trans":
            # Handle transparent key
            return "_"
        elif self.sticky:
            # Handle sticky key
            return f"(sticky-key {self.key.lower()})"
        else:
            # Handle regular key
            return self.key.lower()

    @classmethod
    def from_zmk(cls, binding_str: str) -> 'KeyMapping':
        """Create a KeyMapping from a ZMK binding string."""
        # Handle empty binding or &none
        if not binding_str or binding_str == "&none":
            return cls(key="none")

        # Handle transparent binding
        if binding_str == "&trans":
            return cls(key="trans")

        # Handle sticky key bindings
        if binding_str.startswith("&sk"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid sticky key binding: {binding_str}")
            key = parts[1]
            return cls(key=key, sticky=True)

        # Handle hold-tap bindings
        hold_tap_prefixes = [
            '&mt', '&lh_hm', '&rh_hm', '&ht'
        ]
        has_hold_tap_prefix = any(
            binding_str.startswith(prefix)
            for prefix in hold_tap_prefixes
        )
        if has_hold_tap_prefix:
            parts = binding_str.split()
            if len(parts) != 3:
                raise ValueError(
                    f"Invalid hold-tap binding: {binding_str}"
                )

            behavior_name = parts[0][1:]  # Remove & prefix
            hold_key = parts[1]
            tap_key = parts[2]

            return cls(
                key=tap_key,
                hold_tap=HoldTap(
                    behavior_name=behavior_name,
                    hold_key=hold_key,
                    tap_key=tap_key
                )
            )

        # Handle layer switch bindings
        if binding_str.startswith("&mo"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid layer switch binding: {binding_str}"
                )
            layer_num = parts[1]
            return cls(key=f"mo {layer_num}")

        # Handle Unicode bindings
        unicode_prefixes = ["&unicode_", "&pi", "&n_tilde"]
        is_unicode = any(binding_str.startswith(prefix)
                         for prefix in unicode_prefixes)
        if is_unicode:
            # For now, we'll use a placeholder for the Unicode character
            # In a real implementation, we would parse the macro definition
            # to get the actual character
            if binding_str.startswith("&pi"):
                return cls(key="(unicode π)")
            elif binding_str.startswith("&n_tilde"):
                return cls(key="(unicode ñ)")
            else:
                return cls(key="(unicode ?)")

        # Handle regular key bindings
        if binding_str.startswith("&kp"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid key binding: {binding_str}")
            key = parts[1]
            return cls(key=key)

        # Special case for test files that don't use the &kp prefix
        if not binding_str.startswith("&"):
            return cls(key=binding_str)

        # Handle macro bindings (any other binding starting with &)
        if binding_str.startswith("&"):
            # Extract the macro name (remove the & prefix)
            macro_name = binding_str[1:].split()[0]
            return cls(key=f"(macro {macro_name})")

        # Unknown binding
        raise ValueError(f"Unknown binding: {binding_str}")


@dataclass
class Layer:
    """Represents a layer in the keymap."""
    name: str
    bindings: List[Binding] = field(default_factory=list)

    def to_kanata(self) -> str:
        """Convert the layer to Kanata format."""
        # Convert bindings to Kanata format
        kanata_bindings = []
        for binding in self.bindings:
            kanata_bindings.append(binding.to_kanata())

        # Format the layer definition
        layer_def = f"(deflayer {self.name}\n"
        layer_def += "  " + " ".join(kanata_bindings) + "\n"
        layer_def += ")"

        return layer_def


@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""
    global_settings: GlobalSettings
    layers: List[Layer]
