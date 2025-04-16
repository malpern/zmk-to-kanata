import logging
from typing import Any
from converter.behaviors.sticky_key import StickyKeyBinding
from converter.error_handling import get_error_manager, ErrorSeverity

class StickyKeyTransformer:
    """Transformer for ZMK sticky key behaviors to Kanata format."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_manager = get_error_manager()

    def transform_binding(self, binding: Any) -> str:
        """
        Transform a sticky key binding to Kanata S-expression.
        Args:
            binding: StickyKeyBinding, StickyKeyBehavior, or similar
        Returns:
            str: Kanata S-expression for the sticky key
        """
        # Accept both StickyKeyBinding and StickyKeyBehavior (with .key)
        key = None
        timeout = None
        # Handle StickyKeyBinding
        if isinstance(binding, StickyKeyBinding):
            key = binding.key
            behavior = binding.behavior
            timeout = getattr(behavior, 'release_after_ms', None)
        # Handle StickyKeyBehavior (from edge case tests)
        elif hasattr(binding, 'key'):
            key_obj = getattr(binding, 'key')
            if hasattr(key_obj, 'key'):
                key = getattr(key_obj, 'key')
            else:
                key = key_obj
            timeout = getattr(binding, 'timeout', None)
        else:
            self.error_manager.add_error(
                message=f"Invalid binding type for sticky key: {type(binding)}",
                source="sticky_key_transformer",
                severity=ErrorSeverity.ERROR
            )
            self.logger.error(f"Invalid binding type: {type(binding)}")
            return "sticky-unknown"

        # Validate key
        if not key or (isinstance(key, str) and not key.strip()):
            self.error_manager.add_error(
                message="Sticky key binding is empty or None.",
                source="sticky_key_transformer",
                severity=ErrorSeverity.WARNING
            )
            self.logger.warning("Sticky key binding is empty or None.")
            return "sticky-_"

        # Map modifiers to Kanata short form
        mod_map = {
            'LSHIFT': 'lsft', 'RSHIFT': 'rsft',
            'LCTRL': 'lctl', 'RCTRL': 'rctl',
            'LALT': 'lalt', 'RALT': 'ralt',
            'LGUI': 'lmet', 'RGUI': 'rmet',
            'lshift': 'lsft', 'rshift': 'rsft',
            'lctrl': 'lctl', 'rctrl': 'rctl',
            'lalt': 'lalt', 'ralt': 'ralt',
            'lgui': 'lmet', 'rgui': 'rmet',
        }
        # Handle function keys
        if isinstance(key, str) and key.startswith('F') and key[1:].isdigit():
            expr = f"sticky-{key.lower()}"
        # Handle known modifiers
        elif isinstance(key, str) and key.upper() in mod_map:
            expr = f"sticky-{mod_map.get(key.upper(), key.lower())}"
        # Handle layer switches
        elif isinstance(key, str) and key.startswith("mo "):
            try:
                layer_num = key.split()[1]
                expr = f"sticky-@layer{layer_num}"
            except Exception as e:
                self.error_manager.add_error(
                    message=f"Invalid layer switch in sticky key: {key}",
                    source="sticky_key_transformer",
                    severity=ErrorSeverity.ERROR,
                    exception=e
                )
                self.logger.error(f"Invalid layer switch in sticky key: {key}")
                expr = f"sticky-unknown {key}"
        # Handle regular keys (letters, numbers, etc.)
        elif isinstance(key, str) and key.isalnum():
            expr = f"sticky-{key.lower()}"
        # Handle special keys (e.g., PG_UP, KP_N7)
        elif isinstance(key, str) and key.replace('_', '').isalnum():
            expr = f"sticky-{key.lower()}"
        # Handle unknown or special cases
        elif isinstance(key, str):
            self.error_manager.add_error(
                message=f"Unknown or special sticky key: {key}",
                source="sticky_key_transformer",
                severity=ErrorSeverity.WARNING
            )
            self.logger.warning(f"Unknown or special sticky key: {key}")
            expr = f"sticky-unknown {key}"
        else:
            self.error_manager.add_error(
                message=f"Sticky key binding is not a string: {key}",
                source="sticky_key_transformer",
                severity=ErrorSeverity.ERROR
            )
            self.logger.error(f"Sticky key binding is not a string: {key}")
            expr = "sticky-unknown"

        # Handle timing/timeout if present and valid
        if timeout is not None:
            try:
                timeout_val = int(timeout)
                if timeout_val > 0 and timeout_val < 100000000:
                    expr = f"{expr}-{timeout_val}"
            except Exception as e:
                self.error_manager.add_error(
                    message=f"Invalid timeout value for sticky key: {timeout}",
                    source="sticky_key_transformer",
                    severity=ErrorSeverity.WARNING,
                    exception=e
                )
                self.logger.warning(f"Invalid timeout value for sticky key: {timeout}")

        return expr 