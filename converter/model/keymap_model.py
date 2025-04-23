"""Keymap Model Module

This module contains the intermediate representation classes for our keymap
converter.

This file is the single source of truth for keymap models. It contains
all the model classes and conversion logic for the keymap converter.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

if TYPE_CHECKING:
    # These imports are only used for type checking
    pass


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
    # Add missing attributes to match HoldTapBinding
    hold_trigger_key_positions: Optional[Tuple[int, ...]] = None
    hold_trigger_on_release: bool = False
    retro_tap: bool = False

    def to_kanata(self) -> str:
        """Convert the hold-tap to Kanata format."""
        # Convert hold_key to short form if needed
        hold_key = self.hold_key
        if hold_key == "LSHIFT":
            hold_key = "lsft"
        elif hold_key == "RSHIFT":
            hold_key = "rsft"
        elif hold_key == "LCTRL":
            hold_key = "lctl"
        elif hold_key == "RCTRL":
            hold_key = "rctl"
        elif hold_key == "LALT":
            hold_key = "lalt"
        elif hold_key == "RALT":
            hold_key = "ralt"
        elif hold_key == "LGUI":
            hold_key = "lmet"
        elif hold_key == "RGUI":
            hold_key = "rmet"

        # Convert tap_key if needed
        tap_key = self.tap_key
        # Remove leading 'n' from number keys if followed by digits
        if tap_key.startswith("N") and tap_key[1:].isdigit():
            tap_key = tap_key[1:]

        return f"tap-hold {hold_key} {tap_key.lower()}"


@dataclass(frozen=True)
class HoldTapBinding:
    """Represents a hold-tap binding with its behavior and parameters."""

    behavior_name: str  # e.g., "lh_hm", "rh_hm"
    hold_key: str  # e.g., "LGUI", "LALT"
    tap_key: str  # e.g., "A", "S"
    # Key positions that trigger hold
    hold_trigger_key_positions: Optional[Tuple[int, ...]] = None
    # Whether to trigger hold on key release
    hold_trigger_on_release: bool = False
    # Whether to allow tap on release after hold timeout
    retro_tap: bool = False

    def __eq__(self, other) -> bool:
        """Compare two HoldTapBinding instances for equality."""
        if not isinstance(other, HoldTapBinding):
            return False
        return (
            self.behavior_name == other.behavior_name
            and self.hold_key == other.hold_key
            and self.tap_key == other.tap_key
            and self.hold_trigger_key_positions == other.hold_trigger_key_positions
            and self.hold_trigger_on_release == other.hold_trigger_on_release
            and self.retro_tap == other.retro_tap
        )

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        # Convert hold key to short form
        hold_key = self.hold_key.lower()
        if hold_key == "lshift":
            hold_key = "lsft"
        elif hold_key == "rshift":
            hold_key = "rsft"
        elif hold_key == "lcontrol":
            hold_key = "lctl"
        elif hold_key == "rcontrol":
            hold_key = "rctl"
        elif hold_key == "lctrl":
            hold_key = "lctl"
        elif hold_key == "rctrl":
            hold_key = "rctl"
        elif hold_key == "lgui":
            hold_key = "lmet"
        elif hold_key == "rgui":
            hold_key = "rmet"

        # Convert tap key
        tap_key = self.tap_key.lower()
        if tap_key.startswith("n") and tap_key[1:].isdigit():
            tap_key = tap_key[1:]  # Remove 'n' prefix for number keys

        # Determine tap-hold variant based on binding properties
        tap_hold_type = "tap-hold"  # Default to basic tap-hold

        if self.hold_trigger_key_positions:
            tap_hold_type = "tap-hold-release-keys"
        elif self.hold_trigger_on_release:
            tap_hold_type = "tap-hold-release"
        elif self.retro_tap:
            tap_hold_type = "tap-hold-press-timeout"

        # Build the tap-hold configuration
        config = f"({tap_hold_type} 200 200 {tap_key} {hold_key}"

        # Add extra parameters for advanced features
        if tap_hold_type == "tap-hold-release-keys":
            positions = " ".join(str(pos) for pos in self.hold_trigger_key_positions)
            config += f" ({positions})"
        elif tap_hold_type == "tap-hold-press-timeout" and self.retro_tap:
            config += f" {tap_key}"

        config += ")"
        return config


@dataclass
class KeyMapping(Binding):
    """Represents a key mapping in the keymap."""

    key: str
    hold_tap: Optional[Union[HoldTap, HoldTapBinding]] = None
    sticky: bool = False

    def __eq__(self, other):
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key

    def to_kanata(self) -> str:
        """Convert the key mapping to Kanata format."""
        if self.hold_tap:
            # Use the alias we created for this hold-tap binding
            if hasattr(self.hold_tap, "behavior_name"):
                binding_id = (
                    f"{self.hold_tap.behavior_name}_"
                    f"{self.hold_tap.hold_key}_"
                    f"{self.hold_tap.tap_key}"
                )
                return f"@{binding_id}"
            else:
                # Fall back to direct conversion
                return self.hold_tap.to_kanata()

        if self.key.startswith("mo "):
            # Handle momentary layer switch
            layer_num = self.key.split()[1]
            return f"(layer-while-held {layer_num})"
        elif self.key == "trans":
            # Handle transparent key
            return "_"
        elif self.sticky:
            # Handle sticky key with proper modifier conversion
            key = self.key
            # For function keys, preserve the case
            if key.startswith("F") and key[1:].isdigit():
                return f"sticky-{key}"
            # For other keys, convert to lowercase and map modifiers
            key = key.lower()
            key_map = {
                "lshift": "lsft",
                "rshift": "rsft",
                "lctrl": "lctl",
                "rctrl": "rctl",
                "lgui": "lmet",
                "rgui": "rmet",
            }
            if key in key_map:
                key = key_map[key]
            return f"sticky-{key}"
        else:
            # Handle regular key
            key = self.key.lower()
            # Convert number keys by removing 'n' prefix if followed by digits
            if key.startswith("n") and len(key) > 1 and key[1:].isdigit():
                key = key[1:]
            # Convert numpad keys by removing 'n' from KP_N prefix
            elif key.startswith("kp_n") and len(key) > 4 and key[4:].isdigit():
                key = "kp" + key[4:]
            return key

    @classmethod
    def from_zmk(cls, binding_str: str) -> "KeyMapping":
        """Create a KeyMapping from a ZMK binding string.

        Args:
            binding_str: The ZMK binding string

        Returns:
            A KeyMapping object

        Raises:
            ValueError: If the binding string is invalid
        """
        # Handle empty binding
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
            "&mt",
            "&lh_hm",
            "&rh_hm",
            "&ht",
            "&hm",
            "&hs",
            "&td",
        ]
        has_hold_tap_prefix = any(
            binding_str.startswith(prefix) for prefix in hold_tap_prefixes
        )
        if has_hold_tap_prefix:
            parts = binding_str.split(maxsplit=2)
            if len(parts) != 3:
                raise ValueError(f"Invalid hold-tap binding: {binding_str}")

            behavior_name = parts[0][1:]  # Remove & prefix
            hold_key = parts[1]
            tap_key = parts[2]

            return cls(
                key=tap_key,
                hold_tap=HoldTap(
                    behavior_name=behavior_name,
                    hold_key=hold_key,
                    tap_key=tap_key,
                ),
            )

        # Handle layer switch bindings
        if binding_str.startswith("&mo"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid layer switch binding: {binding_str}")
            layer_num = parts[1]
            return cls(key=f"mo {layer_num}")

        # Handle layer toggle bindings
        if binding_str.startswith("&to"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid layer toggle binding: {binding_str}")
            layer_num = parts[1]
            return cls(key=f"to {layer_num}")

        # Handle regular key bindings
        if binding_str.startswith("&kp"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid key binding: {binding_str}")
            key = parts[1]
            return cls(key=key)

        # Special case for test files that don't use &kp prefix
        if binding_str.startswith("&"):
            # This is some other binding type we don't support yet
            raise ValueError(f"Unknown binding: {binding_str}")
        else:
            # Assume this is a direct key reference (for test files)
            return cls(key=binding_str)


@dataclass
class Layer:
    """Represents a layer in the keymap.

    Now stores the keys matrix as a 2D list (rows x columns).
    The 'bindings' attribute is deprecated; use 'keys' instead.
    """

    name: str
    keys: List[List[Binding]] = field(default_factory=list)

    def __init__(
        self,
        name: str,
        bindings: List[Binding] = None,
        keys: List[List[Binding]] = None,
    ):
        """Initialize a Layer with a keys matrix (preferred) or flat bindings list (deprecated).

        Args:
            name: The name of the layer
            bindings: (Deprecated) List of bindings (flat)
            keys: Matrix of keys (rows x columns, preferred)
        """
        self.name = name
        if keys is not None:
            self.keys = keys
        elif bindings is not None:
            # For backward compatibility, treat as a single row
            self.keys = [bindings]
        else:
            self.keys = []

    def to_kanata(self) -> str:
        """Convert the layer to Kanata format."""
        kanata_bindings = []
        for row in self.keys:
            kanata_bindings.append(
                "  " + "  ".join(binding.to_kanata() for binding in row)
            )
        layer_def = f"(deflayer {self.name}\n"
        layer_def += "\n".join(kanata_bindings) + "\n"
        layer_def += ")"
        return layer_def


@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""

    global_settings: GlobalSettings
    layers: List[Layer]
