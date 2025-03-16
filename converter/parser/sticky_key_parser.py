"""Parser module for ZMK sticky key behavior."""

from typing import Dict, Optional

from converter.behaviors.sticky_key import (
    StickyKeyBehavior,
    StickyKeyBinding,
    is_sticky_key_binding,
)


class StickyKeyParser:
    """Parser for ZMK sticky key behavior and bindings."""

    def __init__(self):
        self.behaviors: Dict[str, StickyKeyBehavior] = {}

    def parse_behavior(
        self,
        name: str,
        config: dict
    ) -> Optional[StickyKeyBehavior]:
        """Parse a sticky key behavior configuration."""
        if config.get('compatible') == '"zmk,behavior-sticky-key"':
            # Extract release-after-ms if present
            release_after_ms = None
            if 'release-after-ms' in config:
                release_after_ms = int(config['release-after-ms'])

            # Create the behavior
            behavior = StickyKeyBehavior(
                name=name,
                release_after_ms=release_after_ms
            )
            
            self.behaviors[name] = behavior
            return behavior
        
        return None

    def parse_binding(self, binding_str: str) -> Optional[StickyKeyBinding]:
        """Parse a sticky key binding string."""
        if not is_sticky_key_binding(binding_str):
            return None

        try:
            # Extract the key from the binding string
            key = binding_str.replace('&sk', '').strip()
            
            # Check if the key is valid
            if not key or key.isdigit() or key == 'INVALID':
                return None
            
            # Create the binding
            return StickyKeyBinding(key=key)
        except ValueError:
            # If we can't parse it as a sticky key binding, return None
            return None
