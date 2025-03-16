"""Parser module for ZMK sticky key behavior."""

import re
from typing import Dict, Optional

from ..behaviors.sticky_key import (
    StickyKeyBehavior,
    StickyKeyBinding,
    is_sticky_key_binding,
    parse_sticky_key_behavior,
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
        if config.get('compatible') == 'zmk,behavior-sticky-key':
            behavior = parse_sticky_key_behavior(config)
            self.behaviors[name] = behavior
            return behavior
        return None

    def parse_binding(self, binding_str: str) -> Optional[StickyKeyBinding]:
        """Parse a sticky key binding string."""
        if not is_sticky_key_binding(binding_str):
            return None

        # Extract behavior name if present
        behavior_match = re.match(r'&(\w+)\s+(\w+)', binding_str)
        if behavior_match:
            behavior_name = behavior_match.group(1)
            behavior = self.behaviors.get(behavior_name)
            return StickyKeyBinding.from_zmk(binding_str, behavior)

        return StickyKeyBinding.from_zmk(binding_str) 