"""Data models for keymap configuration."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union
from .transformer.keycode_map import zmk_binding_to_kanata
from converter.model.keymap_model import HoldTap, HoldTapBinding, Behavior
import logging


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

    def to_kanata(self) -> str:
        """Convert the binding to Kanata format. Base implementation raises error."""
        # This method should be overridden by subclasses like KeyMapping or UnicodeBinding.
        # If a plain Binding object somehow needs transformation, it indicates an
        # issue upstream (e.g., in the extractor) or requires specific handling here.
        logging.error(
            f"to_kanata() called on a base Binding object: {self}. "
            f"This typically means it wasn't fully processed into a specific type."
        )
        # Fallback to a generic comment if direct transformation is not possible.
        behavior_name = (
            getattr(self.behavior, "name", "unknown_behavior")
            if self.behavior
            else "no_behavior"
        )
        param_str = " ".join(self.params)
        return f"; unsupported: base_binding ({behavior_name} {param_str})"

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this binding."""
        # Debug: Assert behavior is None or Behavior
        if self.behavior is not None and not hasattr(self.behavior, "to_dict"):
            print(
                f"[ERROR] Binding.behavior is not a Behavior: {type(self.behavior)} value: {repr(self.behavior)}"
            )
            assert False, "Binding.behavior must be None or Behavior"
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
        """Convert the key mapping to Kanata format using the centralized mapping utility."""
        result = zmk_binding_to_kanata(
            self.key, hold_tap=self.hold_tap, sticky=self.sticky
        )
        return result if result is not None else ""

    @classmethod
    def from_zmk(cls, binding_str: str) -> "KeyMapping":
        """Create a KeyMapping from a ZMK binding string."""
        # Handle empty binding
        if not binding_str or binding_str == "&none":
            return cls(key="none", behavior=None, params=[])
        # Handle transparent binding
        if binding_str == "&trans":
            return cls(key="trans", behavior=None, params=[])
        # Handle sticky key bindings
        if binding_str.startswith("&sk"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid sticky key binding: {binding_str}")
            key = parts[1]
            return cls(key=key, sticky=True, behavior=None, params=[])
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
            tap_key = parts[2]
            return cls(key=tap_key, behavior=None, params=[])
        # Handle layer switch bindings
        if binding_str.startswith("&mo"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid layer switch binding: {binding_str}")
            layer_num = parts[1]
            return cls(key=f"mo {layer_num}", behavior=None, params=[])
        # Handle layer toggle bindings
        if binding_str.startswith("&to"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid layer toggle binding: {binding_str}")
            layer_num = parts[1]
            return cls(key=f"to {layer_num}", behavior=None, params=[])
        # Handle regular key bindings
        if binding_str.startswith("&kp"):
            parts = binding_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid key binding: {binding_str}")
            key = parts[1]
            return cls(key=key, behavior=None, params=[])
        # Special case for test files that don't use &kp prefix
        if binding_str.startswith("&"):
            raise ValueError(f"Unknown binding: {binding_str}")
        else:
            return cls(key=binding_str, behavior=None, params=[])

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
class Layer:
    """Represents a keymap layer."""

    name: str
    bindings: List[Binding]
    index: int

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this layer."""
        # Debug: Assert all bindings are Binding
        for b in self.bindings:
            if not hasattr(b, "to_dict"):
                print(
                    f"[ERROR] Layer.bindings contains non-Binding: {type(b)} value: {repr(b)}"
                )
                assert False, "Layer.bindings must be Binding instances"
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
        # Debug: Assert binding is Binding
        if not hasattr(self.binding, "to_dict"):
            print(
                f"[ERROR] Combo.binding is not a Binding: {type(self.binding)} value: {repr(self.binding)}"
            )
            assert False, "Combo.binding must be a Binding instance"
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
        # Debug: Assert all if_layers are int, then_layer is int
        for if_layer in self.if_layers:
            if not isinstance(if_layer, int):
                print(
                    f"[ERROR] ConditionalLayer.if_layers contains non-int: {type(if_layer)} value: {repr(if_layer)}"
                )
                assert False, "ConditionalLayer.if_layers must be int"
        if not isinstance(self.then_layer, int):
            print(
                f"[ERROR] ConditionalLayer.then_layer is not int: {type(self.then_layer)} value: {repr(self.then_layer)}"
            )
            assert False, "ConditionalLayer.then_layer must be int"
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
        # Debug: Assert all layers are Layer, behaviors are Behavior, combos are Combo, conditional_layers are ConditionalLayer
        for layer in self.layers:
            if not hasattr(layer, "to_dict"):
                print(
                    f"[ERROR] KeymapConfig.layers contains non-Layer: {type(layer)} value: {repr(layer)}"
                )
                assert False, "KeymapConfig.layers must be Layer"
        for k, v in self.behaviors.items():
            if not hasattr(v, "to_dict"):
                print(
                    f"[ERROR] KeymapConfig.behaviors['{k}'] is not a Behavior: {type(v)} value: {repr(v)}"
                )
                assert False, "KeymapConfig.behaviors values must be Behavior instances"
        for c in self.combos:
            if not hasattr(c, "to_dict"):
                print(
                    f"[ERROR] KeymapConfig.combos contains non-Combo: {type(c)} value: {repr(c)}"
                )
                assert False, "KeymapConfig.combos must be Combo instances"
        for cl in self.conditional_layers:
            if not hasattr(cl, "to_dict"):
                print(
                    f"[ERROR] KeymapConfig.conditional_layers contains non-ConditionalLayer: {type(cl)} value: {repr(cl)}"
                )
                assert (
                    False
                ), "KeymapConfig.conditional_layers must be ConditionalLayer instances"
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


class MacroBehavior(Behavior):
    """Macro behavior."""

    def __init__(self, name: str, bindings: list):
        """Initialize a macro behavior.

        Args:
            name: Name of the macro behavior
            bindings: List of key bindings in the macro
        """
        super().__init__(name=name)
        self.type = "macro"
        self.bindings = bindings

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this macro behavior."""
        for b in self.bindings:
            if not hasattr(b, "to_dict"):
                print(
                    f"[ERROR] MacroBehavior.bindings contains non-Binding: {type(b)} value: {repr(b)}"
                )
                assert False, "MacroBehavior.bindings must be Binding instances"
        return {
            "name": self.name,
            "type": self.type,
            "bindings": [b.to_dict() for b in self.bindings],
        }
