"""Module for handling ZMK sticky key behavior conversion."""

from dataclasses import dataclass
from typing import Optional

from converter.model.keymap_model import Binding


@dataclass
class StickyKeyBehavior:
    """Represents a ZMK sticky key behavior configuration."""
    release_after_ms: int
    quick_release: bool = False
    ignore_modifiers: bool = False


class StickyKeyBinding(Binding):
    """Represents a sticky key binding in the keymap."""
    def __init__(self, key: str, behavior: Optional[StickyKeyBehavior] = None):
        self.key = key
        self.behavior = behavior or StickyKeyBehavior(
            release_after_ms=1000,
            quick_release=False,
            ignore_modifiers=False
        )

    def to_kanata(self) -> str:
        """Convert the sticky key binding to Kanata format."""
        # Use the key mapping for consistent key names
        key_mapping = {
            'LSHIFT': 'lsft',
            'RSHIFT': 'rsft',
            'LCTRL': 'lctl',
            'RCTRL': 'rctl',
            'LALT': 'lalt',
            'RALT': 'ralt',
            'LGUI': 'lmet',
            'RGUI': 'rmet',
        }
        key = key_mapping.get(self.key, self.key.lower())
        return f"sticky-{key}"

    @classmethod
    def from_zmk(
        cls,
        zmk_binding: str,
        behavior: Optional[StickyKeyBehavior] = None
    ) -> 'StickyKeyBinding':
        """Create a StickyKeyBinding from a ZMK binding string."""
        # Remove &sk prefix and any whitespace
        key = zmk_binding.replace('&sk', '').strip()

        # Convert ZMK key names to Kanata format
        key_mapping = {
            'LSHIFT': 'lsft',
            'RSHIFT': 'rsft',
            'LCTRL': 'lctl',
            'RCTRL': 'rctl',
            'LALT': 'lalt',
            'RALT': 'ralt',
            'LGUI': 'lmet',
            'RGUI': 'rmet',
        }

        key = key_mapping.get(key, key.lower())
        return cls(key, behavior)


def parse_sticky_key_behavior(config: dict) -> StickyKeyBehavior:
    """Parse ZMK sticky key behavior configuration."""
    return StickyKeyBehavior(
        release_after_ms=config.get('release-after-ms', 1000),
        quick_release='quick-release' in config,
        ignore_modifiers='ignore-modifiers' in config
    )


def is_sticky_key_binding(binding: str) -> bool:
    """Check if a binding string represents a sticky key."""
    return binding.strip().startswith('&sk')
