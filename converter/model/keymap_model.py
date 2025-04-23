"""Keymap Model Module.

This module contains the intermediate representation classes for our keymap
converter.

This file is the single source of truth for keymap models. It contains
all the model classes and conversion logic for the keymap converter.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Union, Dict, Any

if TYPE_CHECKING:
    # These imports are only used for type checking
    from .behaviors import Behavior


@dataclass
class Binding:
    """Base class for all key bindings."""

    behavior: Optional["Behavior"] = None
    params: List[str] = field(default_factory=list)

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

    name: str
    hold_key: str
    tap_key: str
    tapping_term_ms: int
    hold_time_ms: Optional[int] = None
    quick_tap_ms: Optional[int] = None
    flavor: Optional[str] = None

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

        # Determine tap-hold variant based on flavor
        tap_hold_type = "tap-hold"
        if self.flavor == "balanced":
            tap_hold_type = "tap-hold-release"
        elif self.flavor == "hold-preferred":
            tap_hold_type = "tap-hold-press"

        # Build tap-hold configuration
        config = [
            tap_hold_type,
            str(self.tapping_term_ms),
            str(self.hold_time_ms or self.tapping_term_ms),
            hold_key.lower(),
            tap_key.lower(),
        ]

        # Add quick-tap timing if specified
        if self.quick_tap_ms:
            config.append(str(self.quick_tap_ms))

        return f"({' '.join(config)})"


@dataclass(frozen=True)
class HoldTapBinding:
    """Represents a hold-tap binding with additional parameters."""

    key: str
    hold_tap: HoldTap
    tap: str
    hold: str
    params: Dict[str, Any] = field(default_factory=dict)

    def __eq__(self, other: Any) -> bool:
        """Compare two HoldTapBindings for equality."""
        if not isinstance(other, HoldTapBinding):
            return False
        return (
            self.key == other.key
            and self.hold_tap == other.hold_tap
            and self.params == other.params
            and self.tap == other.tap
            and self.hold == other.hold
        )

    def to_kanata(self) -> str:
        """Convert the hold-tap binding to Kanata format."""
        return self.hold_tap.to_kanata()


@dataclass
class KeyMapping:
    """Represents a key mapping in the keymap."""

    key: str
    behavior: Optional["Behavior"] = None
    params: List[str] = field(default_factory=list)
    hold_tap: Optional[Union[HoldTap, HoldTapBinding]] = None
    sticky: bool = False

    def __eq__(self, other):
        """Compare two KeyMapping instances for equality."""
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key

    def to_kanata(self) -> str:
        """Convert the key mapping to Kanata format."""
        if self.hold_tap:
            # Use the alias we created for this hold-tap binding
            if hasattr(self.hold_tap, "name"):
                binding_id = (
                    f"{self.hold_tap.name}_"
                    f"{self.hold_tap.hold}_"
                    f"{self.hold_tap.tap}"
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
    def from_zmk(
        cls, binding_str: str, tap_time: int = 200, hold_time: int = 200
    ) -> "KeyMapping":
        """Create a KeyMapping from a ZMK binding string.

        Args:
            binding_str: The ZMK binding string
            tap_time: The tapping term in milliseconds
            hold_time: The hold term in milliseconds

        Returns:
            A KeyMapping object

        Raises:
            ValueError: If the binding string is invalid
        """
        # Handle empty binding
        if binding_str == "&none":
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
        hold_tap_prefixes = ["&mt", "&lh_hm", "&rh_hm", "&ht", "&hm", "&hs", "&td"]
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

            # Create HoldTap instance with proper timing parameters
            hold_tap = HoldTap(
                name=behavior_name,
                hold_key=hold_key,
                tap_key=tap_key,
                tapping_term_ms=tap_time,
                hold_time_ms=hold_time,  # Set hold_time_ms explicitly
                quick_tap_ms=None,  # Can be set via params if needed
                flavor="balanced",  # Default to balanced flavor
            )

            # Create HoldTapBinding with the hold-tap configuration
            hold_tap_binding = HoldTapBinding(
                key=tap_key,
                hold_tap=hold_tap,
                tap=tap_key,
                hold=hold_key,
                params={"tapping_term_ms": tap_time, "hold_time_ms": hold_time},
            )

            # Return KeyMapping with both behavior and hold_tap set
            return cls(
                key=tap_key,
                behavior=hold_tap,  # Set behavior to HoldTap instance
                # Convert timing params to strings
                params=[str(tap_time), str(hold_time)],
                hold_tap=hold_tap_binding,
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
    """Represents a layer in the keymap."""

    name: str
    index: int
    bindings: List[Binding] = field(default_factory=list)


@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""

    layers: List[Layer]
    behaviors: Dict[str, "Behavior"] = field(default_factory=dict)
