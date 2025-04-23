"""Kanata Transformer Module.

This module provides functionality for transforming ZMK keymap
configurations to Kanata format.
"""

from converter.error_handling.error_manager import get_error_manager
from converter.models import Binding, Layer, KeymapConfig, HoldTapBinding
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor

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
        # Default configuration values
        self.config = {
            "tapping_term_ms": 200,
            "quick_tap_ms": 0,
            "tap_hold_wait_ms": None,
            "require_prior_idle_ms": None,
            "tap_hold_flavor": "hold-preferred",
        }

    def transform(self, keymap: KeymapConfig) -> str:
        """Transform the intermediate KeymapConfig into Kanata DSL format."""
        self.output = []
        self.hold_tap_definitions = {}
        self.macro_definitions = {}
        self.layer_count = len(keymap.layers)

        # Update config from keymap if available
        if hasattr(keymap, "config"):
            self.config.update(keymap.config)

        self._add_header()

        if keymap.behaviors:
            for behavior in keymap.behaviors.values():
                if behavior.type == "macro":
                    macro_str = self.macro_transformer.transform_macro(behavior)
                    if behavior.name not in self.macro_definitions:
                        self.macro_definitions[behavior.name] = macro_str
                        self.output.append(f"\n{macro_str}")
                elif behavior.type == "hold-tap":
                    # Find a binding that uses this behavior to get params
                    for layer in keymap.layers:
                        for binding in layer.bindings:
                            if binding and binding.behavior == behavior:
                                hold_param = binding.params[0]
                                tap_param = binding.params[1]
                                alias_def, alias_name = (
                                    self.holdtap_transformer.transform_behavior(
                                        behavior,
                                        hold_param,
                                        tap_param,
                                    )
                                )
                                if alias_name not in self.hold_tap_definitions:
                                    self.hold_tap_definitions[alias_name] = alias_def
                                    self.output.append(f"\n{alias_def}")
                                break

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
        """Transform a binding to Kanata format.

        Args:
            binding: The binding to transform

        Returns:
            The Kanata format string for the binding
        """
        if isinstance(binding, HoldTapBinding):
            # Get the global tap-hold configuration parameters
            tap_time = self.config["tapping_term_ms"]
            hold_time = self.config["quick_tap_ms"]
            quick_tap_ms = self.config.get("quick_tap_ms")
            tap_hold_wait_ms = self.config.get("tap_hold_wait_ms")
            require_prior_idle_ms = self.config.get("require_prior_idle_ms")
            flavor = self.config.get("tap_hold_flavor")

            # Transform the hold-tap binding with all configuration parameters
            return self.holdtap_transformer.transform_binding(
                binding,
                tap_time=tap_time,
                hold_time=hold_time,
                quick_tap_ms=quick_tap_ms,
                tap_hold_wait_ms=tap_hold_wait_ms,
                require_prior_idle_ms=require_prior_idle_ms,
                flavor=flavor,
            )
        elif binding.behavior and binding.behavior.type == "trans":
            return "_"
        elif binding.behavior is None:
            zmk_key = binding.params[0]
            return self.macro_transformer._convert_key(zmk_key)
        elif binding.behavior.type == "kp":
            zmk_key = binding.params[0]
            return self.macro_transformer._convert_key(zmk_key)
        elif binding.behavior.type == "trans":
            return "_"
        elif binding.behavior.type in ["mo", "to", "tog"]:
            layer_index_or_name = binding.params[0]
            layer_ref = layer_index_or_name
            if binding.behavior.type == "mo":
                return f"(layer {layer_ref})"
            elif binding.behavior.type == "to":
                return f"(layer-switch {layer_ref})"
            elif binding.behavior.type == "tog":
                return f"(layer-toggle {layer_ref})"
        elif binding.behavior.type == "mt":
            mod = self.macro_transformer._convert_key(binding.params[0])
            key = self.macro_transformer._convert_key(binding.params[1])
            alias_name = f"ht_{mod}_{key}"
            if alias_name in self.hold_tap_definitions:
                return f"@{alias_name}"
            else:
                err_msg = f"Mod-tap alias '{alias_name}' not defined."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return f"(mt ??? {mod} {key})"
        elif binding.behavior.type == "lt":
            layer_index_or_name = binding.params[0]
            key = self.macro_transformer._convert_key(binding.params[1])
            layer_ref = layer_index_or_name
            alias_name = f"lt_{layer_ref}_{key}"
            if alias_name in self.hold_tap_definitions:
                return f"@{alias_name}"
            else:
                err_msg = f"Layer-tap alias '{alias_name}' not defined."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return f"(lt ??? {layer_ref} {key})"
        elif binding.behavior.type == "hold-tap":
            # Get the hold and tap parameters
            hold_param = binding.params[0]
            tap_param = binding.params[1]
            # Generate alias name based on whether it's layer-tap or mod-tap
            if hold_param.isdigit():
                alias_name = f"lt_{hold_param}_{tap_param.lower()}"
            else:
                mod_key = self.holdtap_transformer.modifier_map.get(
                    hold_param, hold_param.lower()
                )
                alias_name = f"ht_{mod_key}_{tap_param.lower()}"
            # Return the alias reference
            if alias_name in self.hold_tap_definitions:
                return f"@{alias_name}"
            else:
                err_msg = f"Hold-tap alias '{alias_name}' not defined."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return f"<undef_holdtap:{alias_name}>"
        elif binding.behavior.type == "macro":
            macro_name = binding.behavior.name
            if macro_name in self.macro_definitions:
                if len(binding.params) > 0:
                    macro_params = " ".join(
                        self.macro_transformer._convert_key(p) for p in binding.params
                    )
                    return f"(macro {macro_name} {macro_params})"
                else:
                    return f"(macro {macro_name})"
            else:
                err_msg = f"Macro '{macro_name}' not defined."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return f"<undef_macro:{macro_name}>"
        else:
            err_msg = f"Unknown binding type: {binding.behavior.type}"
            self.error_manager.add_error(err_msg, context={"binding": str(binding)})
            return f"<unknown:{binding.behavior.type}>"
