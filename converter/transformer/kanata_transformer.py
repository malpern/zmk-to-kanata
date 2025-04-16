"""Kanata Transformer Module

This module converts our intermediate representation into Kanata DSL format.
"""

from typing import Dict, List

from converter.behaviors.macro import MacroBehavior, MacroBinding
from converter.behaviors.sticky_key import StickyKeyBinding
from converter.behaviors.unicode import UnicodeBinding
from converter.model.keymap_model import KeymapConfig, KeyMapping

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
        """Transform the config into Kanata DSL format.

        Args:
            config: The keymap configuration.

        Returns:
            The Kanata DSL format as a string.
        """
        output = []
        output.extend(self._transform_header())
        output.extend(self._transform_global_settings(config))
        output.append("")

        # Add hold-tap aliases if there are any
        aliases = self._generate_hold_tap_aliases(config)
        if aliases:
            output.append(";; Hold-tap aliases")
            output.append("(defalias")
            for alias in aliases:
                output.append(f"  {alias}")
            output.append(")")
            output.append("")

        # Add macros if there are any
        macros = self._generate_macros(config)
        if macros:
            output.append(";; Macro definitions")
            for macro in macros:
                output.extend(macro)
                output.append("")
            output.append("")

        # Add layers
        output.extend(self._transform_layers(config))

        return "\n".join(output)

    def _transform_header(self) -> List[str]:
        """Transform the configuration header.

        Returns:
            A list of header lines.
        """
        return [
            ";; ZMK to Kanata Configuration",
            ";; Generated automatically - DO NOT EDIT",
            "",
            ";; Global settings",
        ]

    def _transform_global_settings(self, config: KeymapConfig) -> List[str]:
        """Transform global settings into Kanata format.

        Args:
            config: The keymap configuration.

        Returns:
            A list of global settings lines.
        """
        return [
            f"(defvar tap-time {config.global_settings.tap_time})",
            f"(defvar hold-time {config.global_settings.hold_time})",
        ]

    def _transform_layers(self, config: KeymapConfig) -> List[str]:
        """Transform layers into Kanata format.

        Args:
            config: The keymap configuration.

        Returns:
            A list of layer definition lines.
        """
        lines = []
        for layer in config.layers:
            # If layer is already a string (already transformed), just add it
            if isinstance(layer, str):
                lines.append(layer)
                lines.append("")
                continue

            # Remove _layer suffix from layer name if present
            layer_name = layer.name.replace("_layer", "")
            lines.append(f"(deflayer {layer_name}")
            # Transform each row of bindings
            for row in layer.keys:
                binding_line = "  " + "  ".join(
                    self._transform_key(binding) for binding in row
                )
                lines.append(binding_line)
            lines.append(")")
            lines.append("")

        # Remove the last empty line if it exists
        if lines and not lines[-1]:
            lines.pop()

        return lines

    def _transform_key(self, key_mapping: KeyMapping) -> str:
        """Transform a key mapping to its Kanata representation.

        Args:
            key_mapping: The key mapping to transform.

        Returns:
            The Kanata key representation as a string.
        """
        # Handle sticky key bindings first
        if isinstance(key_mapping, StickyKeyBinding):
            # Get the key from the binding
            key = key_mapping.key
            # Map modifiers to their shorter form
            mod_map = {
                "LSHIFT": "lsft",
                "RSHIFT": "rsft",
                "LCTRL": "lctl",
                "RCTRL": "rctl",
                "LALT": "lalt",
                "RALT": "ralt",
                "LGUI": "lmet",
                "RGUI": "rmet",
            }
            # For function keys, keep the case
            if key.startswith("F") and key[1:].isdigit():
                return f"sticky-{key}"
            # For modifiers, use the mapping
            return f"sticky-{mod_map.get(key, key.lower())}"

        # Handle transparent keys
        if key_mapping.key == "trans":
            return "_"

        # Handle layer switch keys
        if key_mapping.key.startswith("mo "):
            layer_num = key_mapping.key.split(" ")[1]
            # Return using @layer format for momentary layer switch
            return f"@layer{layer_num}"

        # Handle hold-tap bindings
        if hasattr(key_mapping, "hold_tap") and key_mapping.hold_tap:
            alias_name = self._generate_hold_tap_alias_name(
                key_mapping.hold_tap.behavior_name,
                key_mapping.hold_tap.hold_key,
                key_mapping.hold_tap.tap_key,
            )
            return f"@{alias_name}"

        # Handle Unicode bindings
        if isinstance(key_mapping, UnicodeBinding):
            return key_mapping.to_kanata()

        # Handle macro bindings
        if isinstance(key_mapping, MacroBinding):
            return key_mapping.to_kanata()

        # Handle regular key bindings
        key = key_mapping.key
        # For function keys, keep the case
        if key.startswith("F") and key[1:].isdigit():
            return key
        return key.lower()

    def _generate_hold_tap_alias_name(
        self, behavior_name: str, hold_key: str, tap_key: str
    ) -> str:
        """Generate a consistent name for a hold-tap alias.

        Args:
            behavior_name: The name of the hold-tap behavior.
            hold_key: The key to activate when held.
            tap_key: The key to activate when tapped.

        Returns:
            A consistent name for the hold-tap alias.
        """
        return f"{behavior_name}_{hold_key}_{tap_key}"

    def _generate_hold_tap_aliases(self, config: KeymapConfig) -> List[str]:
        """Generate aliases for all hold-tap bindings in the config.

        Args:
            config: The keymap configuration.

        Returns:
            A list of hold-tap alias definitions.
        """
        aliases = []
        # Collect unique hold-tap bindings
        seen_bindings = set()

        # Scan all layers and keys for hold-tap bindings
        for layer in config.layers:
            # Skip if layer is a string (already transformed)
            if isinstance(layer, str):
                continue

            for row in layer.keys:
                for key in row:
                    # Skip sticky key bindings
                    if isinstance(key, StickyKeyBinding):
                        continue

                    if key.hold_tap:
                        ht = key.hold_tap
                        alias_name = self._generate_hold_tap_alias_name(
                            ht.behavior_name, ht.hold_key, ht.tap_key
                        )

                        # Only process each unique binding once
                        binding_key = (
                            ht.behavior_name,
                            ht.hold_key,
                            ht.tap_key,
                            str(ht.hold_trigger_key_positions),
                            ht.hold_trigger_on_release,
                            ht.retro_tap,
                        )

                        if binding_key in seen_bindings:
                            continue

                        seen_bindings.add(binding_key)

                        # Format the hold-tap alias based on its properties
                        hold_key = ht.hold_key.lower()
                        tap_key = ht.tap_key.lower()

                        # Map modifiers to their kanata representation
                        mod_map = {
                            "lshift": "lsft",
                            "rshift": "rsft",
                            "lctrl": "lctl",
                            "rctrl": "rctl",
                            "lalt": "lalt",
                            "ralt": "ralt",
                            "lgui": "lmet",
                            "rgui": "rmet",
                        }

                        hold_key = mod_map.get(hold_key, hold_key)

                        # Basic tap-hold format
                        tap_time = config.global_settings.tap_time
                        hold_time = config.global_settings.hold_time
                        # Base format for simple tap-hold
                        alias_def = (
                            f"{alias_name} (tap-hold {tap_time} {hold_time} "
                            f"{tap_key} {hold_key})"
                        )

                        # Add key positions if specified
                        if ht.hold_trigger_key_positions:
                            pos_str = " ".join(
                                str(p) for p in ht.hold_trigger_key_positions
                            )
                            alias_def = (
                                f"{alias_name} (tap-hold-release-keys "
                                f"{tap_time} {hold_time} {tap_key} {hold_key} "
                                f"({pos_str}))"
                            )
                        # Add release trigger if specified
                        elif ht.hold_trigger_on_release:
                            alias_def = (
                                f"{alias_name} (tap-hold-release "
                                f"{tap_time} {hold_time} {tap_key} {hold_key})"
                            )

                        aliases.append(alias_def)

        return aliases

    def _generate_macros(self, config: KeymapConfig) -> List[List[str]]:
        """Generate macro definitions for all macros in the config.

        Args:
            config: The keymap configuration.

        Returns:
            A list of macro definitions.
        """
        # This would need access to the MacroBehavior objects
        # For now, we'll return an empty list as a placeholder
        # This should be implemented later to properly support macros
        return []

    def register_macro_behavior(self, behavior: MacroBehavior) -> None:
        """Register a macro behavior for later transformation.

        Args:
            behavior: The macro behavior to register.
        """
        self.macro_behaviors[behavior.name] = behavior
