"""Data models for keymap configuration."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Union


@dataclass
class GlobalSettings:
    """Global keymap settings."""

    tap_time: int
    hold_time: int

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of global settings."""
        return {
            "tap_time": self.tap_time,
            "hold_time": self.hold_time,
        }


@dataclass
class Binding:
    """Represents a key binding."""

    behavior: Optional["Behavior"]
    params: List[str]

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this binding."""
        return {
            "behavior": self.behavior.to_dict() if self.behavior else None,
            "params": list(self.params),
        }


@dataclass
class KeyMapping(Binding):
    """Represents a key mapping in the keymap."""

    key: str
    hold_tap: Optional[Union["HoldTap", "HoldTapBinding"]] = None
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

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this key mapping."""
        base = super().to_dict()
        base.update(
            {
                "key": self.key,
                "hold_tap": (
                    self.hold_tap.to_dict()
                    if self.hold_tap and hasattr(self.hold_tap, "to_dict")
                    else self.hold_tap
                ),
                "sticky": self.sticky,
            }
        )
        return base


@dataclass
class Behavior:
    """Base class for behaviors."""

    name: str
    type: str = ""

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this behavior."""
        return {
            "name": self.name,
            "type": self.type,
        }


class HoldTap(Behavior):
    """Hold-tap behavior."""

    def __init__(
        self,
        name: str,
        tapping_term_ms: int,
        hold_time_ms: Optional[int] = None,
        quick_tap_ms: Optional[int] = None,
        flavor: Optional[str] = None,
        tap_hold_wait_ms: Optional[int] = None,
        require_prior_idle_ms: Optional[int] = None,
    ):
        """Initialize a hold-tap behavior.

        Args:
            name: Name of the behavior
            tapping_term_ms: Tap timeout in milliseconds
            hold_time_ms: Hold timeout in milliseconds (defaults to tapping_term_ms)
            quick_tap_ms: Optional quick tap timeout in milliseconds
            flavor: Optional hold-tap flavor (e.g. 'tap-preferred')
            tap_hold_wait_ms: Optional tap-hold wait time in ms
            require_prior_idle_ms: Optional prior idle time in ms
        """
        super().__init__(name=name, type="hold-tap")
        self.tapping_term_ms = tapping_term_ms
        self.hold_time_ms = (
            hold_time_ms if hold_time_ms is not None else tapping_term_ms
        )
        self.quick_tap_ms = quick_tap_ms
        self.flavor = flavor
        self.tap_hold_wait_ms = tap_hold_wait_ms
        self.require_prior_idle_ms = require_prior_idle_ms

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this hold-tap behavior."""
        return {
            "name": self.name,
            "type": self.type,
            "tapping_term_ms": self.tapping_term_ms,
            "hold_time_ms": self.hold_time_ms,
            "quick_tap_ms": self.quick_tap_ms,
            "flavor": self.flavor,
            "tap_hold_wait_ms": self.tap_hold_wait_ms,
            "require_prior_idle_ms": self.require_prior_idle_ms,
        }


@dataclass
class HoldTapBinding:
    """Represents a hold-tap binding configuration."""

    behavior_name: str
    hold_key: str
    tap_key: str
    hold_trigger_key_positions: Optional[Tuple[int, ...]] = None
    hold_trigger_on_release: bool = False
    retro_tap: bool = False

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this hold-tap binding."""
        return {
            "behavior_name": self.behavior_name,
            "hold_key": self.hold_key,
            "tap_key": self.tap_key,
            "hold_trigger_key_positions": self.hold_trigger_key_positions,
            "hold_trigger_on_release": self.hold_trigger_on_release,
            "retro_tap": self.retro_tap,
        }


class MacroBehavior(Behavior):
    """Macro behavior."""

    def __init__(self, name: str, bindings: List[Binding]):
        """Initialize a macro behavior.

        Args:
            name: Name of the macro behavior
            bindings: List of key bindings in the macro
        """
        super().__init__(name=name, type="macro")
        self.bindings = bindings

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this macro behavior."""
        return {
            "name": self.name,
            "type": self.type,
            "bindings": [b.to_dict() for b in self.bindings],
        }


@dataclass
class Layer:
    """Represents a keymap layer."""

    name: str
    bindings: List[Binding]
    index: int

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this layer."""
        return {
            "name": self.name,
            "bindings": [b.to_dict() for b in self.bindings],
            "index": self.index,
        }


@dataclass
class Combo:
    """Represents a key combo."""

    name: str
    timeout_ms: int
    key_positions: List[int]
    binding: Binding

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this combo."""
        return {
            "name": self.name,
            "timeout_ms": self.timeout_ms,
            "key_positions": list(self.key_positions),
            "binding": self.binding.to_dict(),
        }


@dataclass
class ConditionalLayer:
    """Represents a conditional layer activation."""

    name: str
    if_layers: List[int]
    then_layer: int

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this conditional layer."""
        return {
            "name": self.name,
            "if_layers": list(self.if_layers),
            "then_layer": self.then_layer,
        }


@dataclass
class KeymapConfig:
    """Top-level keymap configuration."""

    layers: List[Layer]
    behaviors: Dict[str, Behavior] = field(default_factory=dict)
    combos: List[Combo] = field(default_factory=list)
    conditional_layers: List[ConditionalLayer] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of the keymap config."""
        return {
            "layers": [layer.to_dict() for layer in self.layers],
            "behaviors": {k: v.to_dict() for k, v in self.behaviors.items()},
            "combos": [c.to_dict() for c in self.combos],
            "conditional_layers": [cl.to_dict() for cl in self.conditional_layers],
        }


@dataclass
class KanataConfig:
    """Configuration for Kanata output."""

    tapping_term_ms: int = 200
    quick_tap_ms: int = 0
    permissive_hold: bool = False
    hold_on_other_key_press: bool = False
    retro_tapping: bool = False

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of the Kanata config."""
        return {
            "tapping_term_ms": self.tapping_term_ms,
            "quick_tap_ms": self.quick_tap_ms,
            "permissive_hold": self.permissive_hold,
            "hold_on_other_key_press": self.hold_on_other_key_press,
            "retro_tapping": self.retro_tapping,
        }
