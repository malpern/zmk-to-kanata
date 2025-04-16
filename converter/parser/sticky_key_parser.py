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
        self, name: str, config: dict
    ) -> Optional[StickyKeyBehavior]:
        """Parse a sticky key behavior configuration."""
        if config.get("compatible") == '"zmk,behavior-sticky-key"':
            # Check for invalid bindings
            if (
                "bindings" in config
                and "<&invalid_behavior>" in config["bindings"]
            ):
                raise ValueError(
                    f"Invalid binding in sticky key behavior: {name}"
                )

            # Extract release-after-ms if present
            release_after_ms = None
            if "release-after-ms" in config:
                release_after_ms = int(config["release-after-ms"])

            # Create the behavior
            behavior = StickyKeyBehavior(
                name=name, release_after_ms=release_after_ms
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
            key = binding_str.replace("&sk", "").strip()

            # Check if the key is valid
            if not key or key.isdigit() or key == "INVALID":
                raise ValueError(f"Invalid sticky key: {key}")

            # For function keys, preserve the name
            if key.startswith("F") and key[1:].isdigit():
                # Keep function keys as is (F1, F2, etc.)
                pass
            else:
                # Map modifiers to their Kanata representation
                key_mapping = {
                    "LSHIFT": "lsft",
                    "RSHIFT": "rsft",
                    "LCTRL": "lctl",
                    "RCTRL": "rctl",
                    "LALT": "lalt",
                    "RALT": "ralt",
                    "LGUI": "lmet",
                    "RGUI": "rmet",
                }
                key = key_mapping.get(key, key.lower())

            # Create the binding
            return StickyKeyBinding(key=key)
        except ValueError as e:
            # Propagate the error
            raise ValueError(f"Invalid sticky key binding: {e}")
