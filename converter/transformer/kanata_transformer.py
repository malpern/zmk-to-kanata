"""Kanata Transformer Module

This module converts our intermediate representation into Kanata DSL format.
"""
from typing import Dict, List

from converter.behaviors.macro import MacroBehavior
from converter.model.keymap_model import (
    KeymapConfig,
    KeyMapping
)
from .holdtap_transformer import HoldTapTransformer
from .macro_transformer import MacroTransformer


class KanataTransformer:
    """Transforms the intermediate representation into Kanata DSL format."""

    def __init__(self):
        """Initialize the transformer."""
        self.holdtap_transformer = HoldTapTransformer()
        self.macro_transformer = MacroTransformer()
        self.macro_behaviors: Dict[str, MacroBehavior] = {}

    def transform(self, config: KeymapConfig) -> str:
        """Transform the keymap configuration into Kanata DSL format.

        Args:
            config: The keymap configuration to transform.

        Returns:
            A string containing the Kanata configuration.
        """
        lines = []

        # Add header
        lines.extend(self._transform_header())

        # Add global settings
        lines.extend(self._transform_global_settings(config))

        # Add hold-tap aliases if needed
        holdtap_aliases = self._transform_holdtap_aliases(config)
        if holdtap_aliases:
            lines.append("")  # Add spacing
            lines.extend(holdtap_aliases)

        # Add macro definitions if needed
        macro_defs = self._transform_macro_definitions()
        if macro_defs:
            lines.append("")  # Add spacing
            lines.extend(macro_defs)

        # Add layers
        if config.layers:
            lines.append("")  # Add spacing
            lines.extend(self._transform_layers(config))

        return "\n".join(lines)

    def _transform_header(self) -> list[str]:
        """Transform the configuration header.

        Returns:
            A list of header lines.
        """
        return [
            ";; ZMK to Kanata Configuration",
            ";; Generated automatically - DO NOT EDIT",
            "",
            ";; Global settings"
        ]

    def _transform_global_settings(self, config: KeymapConfig) -> list[str]:
        """Transform global settings into Kanata format.

        Args:
            config: The keymap configuration.

        Returns:
            A list of global settings lines.
        """
        return [
            f"(defvar tap-time {config.global_settings.tap_time})",
            f"(defvar hold-time {config.global_settings.hold_time})"
        ]

    def _transform_holdtap_aliases(self, config: KeymapConfig) -> List[str]:
        """Transform hold-tap behaviors into Kanata aliases.

        Args:
            config: The keymap configuration.

        Returns:
            A list of alias definitions.
        """
        # For now, we don't extract hold-tap bindings from KanataLayer objects
        # This would require changes to the Layer and KanataLayer classes
        # to preserve the hold-tap information
        return []

    def _transform_key(self, key: KeyMapping) -> str:
        """Transform a single key mapping to Kanata format.

        Args:
            key: The key mapping to transform.

        Returns:
            The Kanata key representation.
        """
        # If key is already a string, just return it
        if isinstance(key, str):
            return key

        if key.hold_tap:
            # Use the alias we created for this hold-tap binding
            binding_id = (
                f"{key.hold_tap.behavior_name}_"
                f"{key.hold_tap.hold_key}_"
                f"{key.hold_tap.tap_key}"
            )
            return f"@{binding_id}"

        if key.key.startswith("mo "):
            # Handle momentary layer switch
            layer_num = key.key.split()[1]
            return f"(layer-while-held {layer_num})"
        elif key.key == "trans":
            # Handle transparent key
            return "_"
        else:
            # Handle regular key
            return key.key.lower()

    def _transform_layers(self, config: KeymapConfig) -> list[str]:
        """Transform layers into Kanata format.

        Args:
            config: The keymap configuration.

        Returns:
            A list of layer definition lines.
        """
        lines = []
        for i, layer in enumerate(config.layers):
            lines.append(f"(deflayer {layer.name}")
            # Transform each row of keys
            for row in layer.keys:
                key_line = "  " + "  ".join(
                    self._transform_key(k) for k in row
                )
                lines.append(key_line)
            lines.append(")")
            # Add spacing between layers, but not after the last one
            if i < len(config.layers) - 1:
                lines.append("")

        return lines

    def _transform_macro_definitions(self) -> List[str]:
        """Transform macro behaviors into Kanata macro definitions.

        Returns:
            A list of macro definition lines.
        """
        if not self.macro_behaviors:
            return []

        lines = [";; Macro definitions"]
        for name, behavior in self.macro_behaviors.items():
            macro_def = self.macro_transformer.transform_macro(behavior)
            lines.append(macro_def)
            lines.append("")  # Add spacing between macros

        return lines

    def register_macro_behavior(self, behavior: MacroBehavior) -> None:
        """Register a macro behavior for later transformation.

        Args:
            behavior: The macro behavior to register.
        """
        self.macro_behaviors[behavior.name] = behavior
