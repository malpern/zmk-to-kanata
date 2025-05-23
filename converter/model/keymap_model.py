"""Keymap Model Module.

This module contains the intermediate representation classes for our keymap
converter.

This file is the single source of truth for keymap models. It contains
all the model classes and conversion logic for the keymap converter.
"""

from dataclasses import dataclass, field, KW_ONLY
from typing import List, Optional, Union, Dict, Any
from converter.transformer.keycode_map import zmk_to_kanata


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
class Behavior:
    """Represents a ZMK behavior, serving as a base for specific types."""

    name: str
    _: KW_ONLY
    type: Optional[str] = None  # E.g., "hold-tap", "macro", etc.
    extra_properties: Dict[str, Any] = field(
        default_factory=dict
    )  # Store other DTS properties like 'tapping-term-ms'


@dataclass
class HoldTap(Behavior):
    """Represents a hold-tap behavior in ZMK."""

    name: str
    hold_key: str
    tap_key: str
    tapping_term_ms: int
    hold_time_ms: Optional[int] = None
    quick_tap_ms: Optional[int] = None
    flavor: Optional[str] = None
    tap_hold_wait_ms: Optional[int] = None
    require_prior_idle_ms: Optional[int] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if not isinstance(self.hold_key, str):
            raise TypeError("hold_key must be a string")
        if not isinstance(self.tap_key, str):
            raise TypeError("tap_key must be a string")
        if not isinstance(self.tapping_term_ms, int):
            raise TypeError("tapping_term_ms must be an int")
        if self.hold_time_ms is not None and not isinstance(self.hold_time_ms, int):
            raise TypeError("hold_time_ms must be int or None")
        if self.quick_tap_ms is not None and not isinstance(self.quick_tap_ms, int):
            raise TypeError("quick_tap_ms must be int or None")
        if self.flavor is not None and not isinstance(self.flavor, str):
            raise TypeError("flavor must be str or None")
        if self.tap_hold_wait_ms is not None and not isinstance(
            self.tap_hold_wait_ms, int
        ):
            raise TypeError("tap_hold_wait_ms must be int or None")
        if self.require_prior_idle_ms is not None and not isinstance(
            self.require_prior_idle_ms, int
        ):
            raise TypeError("require_prior_idle_ms must be int or None")

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

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this hold-tap behavior."""
        return {
            "name": self.name,
            "hold_key": self.hold_key,
            "tap_key": self.tap_key,
            "tapping_term_ms": self.tapping_term_ms,
            "hold_time_ms": self.hold_time_ms,
            "quick_tap_ms": self.quick_tap_ms,
            "flavor": self.flavor,
            "tap_hold_wait_ms": self.tap_hold_wait_ms,
            "require_prior_idle_ms": self.require_prior_idle_ms,
        }


@dataclass(frozen=True)
class HoldTapBinding:
    """Represents a hold-tap binding with additional parameters."""

    key: str
    hold_tap: HoldTap
    tap: str
    hold: str
    params: Dict[str, Union[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.key, str):
            raise TypeError("key must be a string")
        if not isinstance(self.hold_tap, HoldTap):
            raise TypeError("hold_tap must be a HoldTap instance")
        if not isinstance(self.tap, str):
            raise TypeError("tap must be a string")
        if not isinstance(self.hold, str):
            raise TypeError("hold must be a string")
        if not isinstance(self.params, dict):
            raise TypeError("params must be a dict")
        for k, v in self.params.items():
            if not isinstance(k, str):
                raise TypeError("params keys must be strings")
            if not (isinstance(v, str) or isinstance(v, int)):
                raise TypeError("params values must be str or int")

    def __eq__(self, other: object) -> bool:
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
    behavior: Optional[Behavior] = None
    params: List[str] = field(default_factory=list)
    hold_tap: Optional[Union[HoldTap, HoldTapBinding]] = None
    sticky: bool = False

    def __eq__(self, other: object) -> bool:
        """Compare two KeyMapping instances for equality."""
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key

    def to_kanata(self) -> str:
        """Convert the key mapping to Kanata format using the central mapping utility."""
        ht = self.hold_tap
        if (
            ht
            and hasattr(ht, "hold_tap")
            and hasattr(ht.hold_tap, "name")
            and hasattr(ht, "hold")
            and hasattr(ht, "tap")
        ):
            return f"@{ht.hold_tap.name}_{ht.hold}_{ht.tap}"
        if (
            ht
            and hasattr(ht, "name")
            and hasattr(ht, "hold_key")
            and hasattr(ht, "tap_key")
        ):
            return f"@{ht.name}_{ht.hold_key}_{ht.tap_key}"
        if ht and hasattr(ht, "to_kanata") and callable(ht.to_kanata):
            return ht.to_kanata()
        key = zmk_to_kanata(self.key)
        if self.key.startswith("mo "):
            layer_num = self.key.split()[1]
            return f"(layer-while-held {layer_num})"
        elif self.key == "trans":
            return "_"
        elif self.sticky:
            if self.key.startswith("F") and self.key[1:].isdigit():
                return f"sticky-{self.key}"
            k = key if key is not None else self.key
            return f"sticky-{k if k is not None else ''}"
        else:
            if self.key.startswith("n") and self.key[1:].isdigit():
                return self.key[1:]
            if (
                self.key.startswith("kp_n")
                and len(self.key) > 4
                and self.key[4:].isdigit()
            ):
                return "kp" + self.key[4:]
            return (
                key if key is not None else (self.key if self.key is not None else "")
            )

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
                params={
                    "tapping_term_ms": tap_time,
                    "hold_time_ms": hold_time,
                },
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
    behaviors: Dict[str, Behavior] = field(default_factory=dict)
