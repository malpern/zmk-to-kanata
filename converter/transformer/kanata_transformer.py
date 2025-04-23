"""Kanata Transformer Module.

This module provides functionality for transforming ZMK keymap configurations to
Kanata format.
"""

from typing import Dict, List

from converter.behaviors.macro import MacroBehavior
from converter.error_handling.error_manager import get_error_manager
from converter.models import Binding, Layer, KeymapConfig
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor

from converter.behaviors.sticky_key import StickyKeyBinding

from .holdtap_transformer import HoldTapTransformer
from .macro_transformer import MacroTransformer


class KanataTransformer:
    """Transforms ZMK keymap configurations to Kanata format."""

    def __init__(self):
        """Initialize the kanata transformer."""
        self.parser = DtsParser()
        self.extractor = KeymapExtractor()
        self.error_manager = get_error_manager()
        self.layer_count = 0
        self.current_layer_name = None
        self.output = []
        self.hold_tap_definitions = {}
        self.holdtap_transformer = HoldTapTransformer()
        self.macro_transformer = MacroTransformer()
        self.macro_definitions = {}

    def transform(self, keymap: KeymapConfig) -> str:
        """Transform the intermediate KeymapConfig into Kanata DSL format."""
        self.output = []
        self.hold_tap_definitions = {}
        self.macro_definitions = {}
        self.layer_count = len(keymap.layers)

        self._add_header()

        if keymap.behaviors:
            for behavior in keymap.behaviors.values():
                if behavior.type == "macro":
                    macro_str = self.macro_transformer.transform_macro(behavior)
                    if behavior.name not in self.macro_definitions:
                        self.macro_definitions[behavior.name] = macro_str
                        self.output.append(f"\n{macro_str}")
                elif behavior.type == "hold-tap":
                    alias_def, alias_name = self.holdtap_transformer.transform_behavior(
                        behavior
                    )
                    if alias_name not in self.hold_tap_definitions:
                        self.hold_tap_definitions[alias_name] = alias_def
                        self.output.append(f"\n{alias_def}")

        for layer in keymap.layers:
            self._transform_layer(layer)

        return "\n".join(self.output)

    def _add_header(self):
        """Add Kanata configuration header."""
        self.output.append("(defcfg")
        self.output.append("  input (kb () () )")
        self.output.append("  output (kbd ())")
        self.output.append(")")
        self.output.append("")

    def _transform_layer(self, layer: Layer):
        """Transform a single layer into Kanata format."""
        layer_name = layer.name if layer.name else f"layer{layer.index}"
        self.current_layer_name = layer_name
        self.output.append(f"(deflayer {layer_name}")

        bindings_str = " ".join(
            self._transform_binding(binding) if binding else "_"
            for binding in layer.bindings
        )
        self.output.append(f"  {bindings_str}")
        self.output.append(")")
        self.output.append("")

    def _transform_binding(self, binding: Binding) -> str:
        """Transform a single binding object into Kanata format."""
        if binding.behavior and binding.behavior.type == "trans":
            return "_"

        if binding.behavior is None:
            zmk_key = binding.params[0]
            return self.macro_transformer._convert_key(zmk_key)

        behavior_type = binding.behavior.type
        params = binding.params

        if behavior_type == "kp":
            zmk_key = params[0]
            return self.macro_transformer._convert_key(zmk_key)
        elif behavior_type == "trans":
            return "_"
        elif behavior_type in ["mo", "to", "tog"]:
            layer_index_or_name = params[0]
            layer_ref = layer_index_or_name
            if behavior_type == "mo":
                return f"(layer {layer_ref})"
            elif behavior_type == "to":
                return f"(layer-switch {layer_ref})"
            elif behavior_type == "tog":
                return f"(layer-toggle {layer_ref})"
        elif behavior_type == "mt":
            mod = self.macro_transformer._convert_key(params[0])
            key = self.macro_transformer._convert_key(params[1])
            alias_name = f"ht_{mod}_{key}"
            if alias_name in self.hold_tap_definitions:
                return f"@{alias_name}"
            else:
                self.error_manager.add_error(
                    f"Mod-tap alias '{alias_name}' not defined.", binding=str(binding)
                )
                return f"(mt ??? {mod} {key})"
        elif behavior_type == "lt":
            layer_index_or_name = params[0]
            key = self.macro_transformer._convert_key(params[1])
            layer_ref = layer_index_or_name
            alias_name = f"lt_{layer_ref}_{key}"
            if alias_name in self.hold_tap_definitions:
                return f"@{alias_name}"
            else:
                self.error_manager.add_error(
                    f"Layer-tap alias '{alias_name}' not defined.", binding=str(binding)
                )
                return f"(lt ??? {layer_ref} {key})"

        elif behavior_type == "macro":
            macro_name = binding.behavior.name
            if macro_name in self.macro_definitions:
                if len(params) > 0:
                    macro_params = " ".join(
                        self.macro_transformer._convert_key(p) for p in params
                    )
                    return f"(macro {macro_name} {macro_params})"
                else:
                    return f"(macro {macro_name})"
            else:
                self.error_manager.add_error(
                    f"Macro '{macro_name}' not defined.", binding=str(binding)
                )
                return f"<undef_macro:{macro_name}>"

        elif behavior_type == "sk":
            mod = self.macro_transformer._convert_key(params[0])
            return f"(sticky-key {mod})"

        self.error_manager.add_error(
            f"Unsupported behavior type '{behavior_type}' in binding.",
            binding=str(binding),
        )
        return f"<unhandled:{behavior_type}>"
