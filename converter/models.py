from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Behavior:
    """Base class for all behaviors."""
    name: str


@dataclass
class HoldTap(Behavior):
    """Hold-tap behavior configuration."""
    tapping_term_ms: int
    quick_tap_ms: Optional[int] = None
    flavor: Optional[str] = None
    hold_triggered: Optional[bool] = None


@dataclass
class MacroBehavior(Behavior):
    """Macro behavior configuration."""
    bindings: List['Binding'] = field(default_factory=list)


@dataclass
class Binding:
    """Key binding configuration."""
    behavior: Optional[Behavior] = None
    params: List[str] = field(default_factory=list)


@dataclass
class Layer:
    """Layer configuration."""
    name: str
    bindings: List[Binding] = field(default_factory=list)


@dataclass
class KeymapConfig:
    """Complete keymap configuration."""
    layers: List[Layer] = field(default_factory=list)
    behaviors: List[Behavior] = field(default_factory=list)


@dataclass
class KanataConfig:
    """Configuration for Kanata output."""
    tapping_term_ms: int = 200
    quick_tap_ms: int = 0
    permissive_hold: bool = False
    hold_on_other_key_press: bool = False
    retro_tapping: bool = False 