"""Kanata Transformer Module

This module converts our intermediate representation into Kanata DSL format.
"""
from converter.model.keymap_model import KeymapConfig


class KanataTransformer:
    """Transforms the intermediate representation into Kanata DSL format."""

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

    def _transform_layers(self, config: KeymapConfig) -> list[str]:
        """Transform layers into Kanata format.

        Args:
            config: The keymap configuration.

        Returns:
            A list of layer definition lines.
        """
        lines = []
        for layer in config.layers:
            lines.append(f"(deflayer {layer.name}")
            # Transform each row of keys
            for row in layer.keys:
                # Convert keys to lowercase for Kanata format
                key_line = "  " + "  ".join(k.key.lower() for k in row)
                lines.append(key_line)
            lines.append(")")
        return lines