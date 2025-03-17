"""Module for transforming ZMK hold-tap behaviors to Kanata format."""

from typing import Union
from converter.behaviors.holdtap import HoldTapBehavior
from converter.behaviors.key import KeyMapping
from converter.behaviors.layer import LayerBehavior
from converter.behaviors.macro import MacroBehavior
from converter.behaviors.sticky_key import StickyKeyBehavior
from converter.behaviors.key_sequence import KeySequenceBehavior


class HoldTapTransformer:
    """Transformer for ZMK hold-tap behaviors."""

    def __init__(self):
        """Initialize the transformer."""
        self.layer_transformer = None
        self.macro_transformer = None
        self.sticky_key_transformer = None
        self.key_sequence_transformer = None

    def set_layer_transformer(self, transformer) -> None:
        """Set the layer transformer."""
        self.layer_transformer = transformer

    def set_macro_transformer(self, transformer) -> None:
        """Set the macro transformer."""
        self.macro_transformer = transformer

    def set_sticky_key_transformer(self, transformer) -> None:
        """Set the sticky key transformer."""
        self.sticky_key_transformer = transformer

    def set_key_sequence_transformer(self, transformer) -> None:
        """Set the key sequence transformer."""
        self.key_sequence_transformer = transformer

    def _validate_nested_behavior(
        self,
        behavior: Union[
            KeyMapping,
            LayerBehavior,
            MacroBehavior,
            StickyKeyBehavior,
            KeySequenceBehavior,
            HoldTapBehavior
        ]
    ) -> bool:
        """Validate a nested behavior.

        Args:
            behavior: The behavior to validate

        Returns:
            bool: True if the behavior is valid for nesting
        """
        # HoldTap behaviors cannot be nested
        if isinstance(behavior, HoldTapBehavior):
            return False

        # Layer behaviors are allowed in hold position only
        if isinstance(behavior, LayerBehavior):
            return True

        # Macro behaviors are not allowed to be nested
        if isinstance(behavior, MacroBehavior):
            return False

        # Sticky key behaviors are not allowed to be nested
        if isinstance(behavior, StickyKeyBehavior):
            return False

        # Key sequence behaviors are not allowed to be nested
        if isinstance(behavior, KeySequenceBehavior):
            return False

        # KeyMapping is always allowed
        if isinstance(behavior, KeyMapping):
            return True

        return False

    def _transform_nested_behavior(
        self,
        behavior: Union[
            KeyMapping,
            LayerBehavior,
            MacroBehavior,
            StickyKeyBehavior,
            KeySequenceBehavior,
            HoldTapBehavior
        ]
    ) -> str:
        """Transform a nested behavior.

        Args:
            behavior: The behavior to transform

        Returns:
            str: The transformed behavior in Kanata format
        """
        if isinstance(behavior, KeyMapping):
            return behavior.to_kanata()

        if isinstance(behavior, LayerBehavior) and self.layer_transformer:
            return self.layer_transformer.transform_binding(behavior)

        # For unsupported nested behaviors, return "unknown"
        return "unknown"

    def transform_binding(self, behavior: HoldTapBehavior) -> str:
        """Transform a hold-tap binding to Kanata format.

        Args:
            behavior: The hold-tap behavior to transform

        Returns:
            str: The transformed binding in Kanata format
        """
        # Validate hold behavior
        if not self._validate_nested_behavior(behavior.hold):
            return "(tap-hold _ unknown)"

        # Validate tap behavior
        if not self._validate_nested_behavior(behavior.tap):
            return "(tap-hold unknown _)"

        # Transform hold and tap behaviors
        hold_str = self._transform_nested_behavior(behavior.hold)
        tap_str = self._transform_nested_behavior(behavior.tap)

        # Construct the tap-hold binding
        return f"(tap-hold {tap_str} {hold_str})"

    def transform_behavior(self, behavior: HoldTapBehavior) -> str:
        """Transform a hold-tap behavior to Kanata format.

        Args:
            behavior: The hold-tap behavior to transform

        Returns:
            str: The transformed behavior in Kanata format
        """
        # For now, just transform the binding
        # In the future, we can add behavior-specific transformations
        return self.transform_binding(behavior)
