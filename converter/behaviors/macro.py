"""Module for ZMK macro behavior and bindings."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from ..model.keymap_model import Binding


class MacroActivationMode(Enum):
    """Activation mode for macro bindings."""
    TAP = "tap"
    PRESS = "press"
    RELEASE = "release"


@dataclass
class MacroBehavior:
    """Represents a ZMK macro behavior configuration."""
    name: str
    wait_ms: int = 15  # Default from ZMK CONFIG_ZMK_MACRO_DEFAULT_WAIT_MS
    tap_ms: int = 30   # Default from ZMK CONFIG_ZMK_MACRO_DEFAULT_TAP_MS
    bindings: List[Binding] = field(default_factory=list)
    binding_cells: int = 0  # For non-parameterized macros


@dataclass
class MacroBinding(Binding):
    """Represents a macro binding in the keymap."""
    behavior: MacroBehavior
    param: Optional[int] = None  # For parameterized macros

    def to_kanata(self) -> str:
        """Convert the binding to Kanata format.

        Returns:
            String containing the Kanata binding
        """
        # For now, just return a simple macro reference
        # This will be expanded in the future to use the MacroTransformer
        return f"(macro {self.behavior.name})"

    @classmethod
    def from_zmk(
        cls,
        zmk_binding: str,
        behaviors: Dict[str, MacroBehavior]
    ) -> 'MacroBinding':
        """Create a MacroBinding from a ZMK binding string."""
        # Extract behavior name and optional parameter
        parts = zmk_binding.replace('&', '').strip().split()
        behavior_name = parts[0]

        # Look up the behavior
        if behavior_name not in behaviors:
            raise ValueError(f"Unknown macro behavior: {behavior_name}")

        behavior = behaviors[behavior_name]

        # Check for parameter
        param = None
        if len(parts) > 1 and behavior.binding_cells > 0:
            param = int(parts[1])

        return cls(behavior=behavior, param=param)


def is_macro_binding(binding_str: str) -> bool:
    """Check if a binding string is a macro binding."""
    # Macro bindings start with & followed by a behavior name
    # We'll need to check against known macro behaviors
    excluded_prefixes = [
        '&kp', '&mo', '&lt', '&to', '&sk', '&key_sequence'
    ]
    return binding_str.startswith('&') and not any(
        binding_str.startswith(prefix) for prefix in excluded_prefixes
    )
