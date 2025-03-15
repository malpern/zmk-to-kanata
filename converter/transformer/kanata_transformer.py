"""Kanata Transformer Module

This module converts our intermediate representation into Kanata DSL format.
"""
from typing import List

from converter.model.keymap_model import (
    KeymapConfig,
    KeyMapping
)
from .holdtap_transformer import HoldTapTransformer


class KanataTransformer:
    """Transforms the intermediate representation into Kanata DSL format."""

    def __init__(self):
        """Initialize the transformer."""
        self.holdtap_transformer = HoldTapTransformer()

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
        # Collect all unique hold-tap bindings
        holdtap_bindings = set()
        for layer in config.layers:
            for row in layer.keys:
                for key in row:
                    if key.hold_tap:
                        # Create a unique identifier for this hold-tap binding
                        binding_id = (
                            f"{key.hold_tap.behavior_name}_"
                            f"{key.hold_tap.hold_key}_"
                            f"{key.hold_tap.tap_key}"
                        )
                        holdtap_bindings.add((binding_id, key.hold_tap))
        
        if not holdtap_bindings:
            return []
        
        # Transform bindings into aliases
        lines = [";; Hold-tap aliases", "(defalias"]
        for binding_id, binding in sorted(holdtap_bindings):
            # Transform the binding
            kanata_binding = self.holdtap_transformer.transform_binding(
                binding,
                config.global_settings.tap_time,
                config.global_settings.hold_time
            )
            if kanata_binding:
                # Add the alias definition
                lines.append(f"  {binding_id} {kanata_binding}")
        lines.append(")")
        
        return lines

    def _transform_key(self, key: KeyMapping) -> str:
        """Transform a single key mapping to Kanata format.

        Args:
            key: The key mapping to transform.

        Returns:
            The Kanata key representation.
        """
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