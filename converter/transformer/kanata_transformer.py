"""Kanata Transformer Module.

This module provides functionality for transforming ZMK keymap
configurations to Kanata format.
"""

from converter.error_handling.error_manager import get_error_manager
from converter.models import Binding, Layer, KeymapConfig
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor

from .holdtap_transformer import HoldTapTransformer
from .macro_transformer import MacroTransformer

import logging


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
                                # Use the correct type string for alias naming
                                if hasattr(behavior, "name") and behavior.name in (
                                    "lt",
                                    "mt",
                                ):
                                    alias_type = behavior.name
                                else:
                                    alias_type = behavior.type
                                alias_name = self._holdtap_alias_name(
                                    alias_type,
                                    hold_param,
                                    tap_param,
                                )
                                (
                                    alias_def,
                                    _alias_name,
                                ) = self.holdtap_transformer.transform_behavior(
                                    behavior,
                                    hold_param,
                                    tap_param,
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
        # Map ZMK layer names to Kanata conventions
        layer_name = layer.name if layer.name else f"layer{layer.index}"
        if layer_name == "default_layer":
            layer_name = "default"
        self.current_layer_name = layer_name
        logging.debug(
            f"[KanataTransformer] Transforming layer: {layer_name} "
            f"with {len(layer.bindings)} bindings"
        )
        self.output.append(f"(deflayer {layer_name}")

        for idx, binding in enumerate(layer.bindings):
            logging.debug(f"[KanataTransformer]   Binding {idx}: {binding}")
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
        # Map ZMK built-in compatible types to Kanata actions
        BUILTIN_TYPE_MAP = {
            "zmk,behavior-transparent": "trans",
            "zmk,behavior-momentary-layer": "mo",
            "zmk,behavior-toggle-layer": "to",
            "zmk,behavior-sticky-layer": "sl",
            # Add more as needed
        }
        # If the behavior type is a known compatible string, map to short type
        behavior_type = None
        if binding.behavior:
            btype = binding.behavior.type
            if btype in BUILTIN_TYPE_MAP:
                behavior_type = BUILTIN_TYPE_MAP[btype]
            else:
                behavior_type = btype
        # Transform the hold-tap binding with all configuration parameters
        if (
            hasattr(binding, "behavior")
            and binding.behavior is not None
            and getattr(binding.behavior, "__class__", None)
            and binding.behavior.__class__.__name__ == "HoldTap"
        ):
            if hasattr(binding.behavior, "name"):
                if binding.behavior.name == "mt" and "mt" in self.hold_tap_definitions:
                    return "@mt"
                elif (
                    binding.behavior.name == "lt" and "lt" in self.hold_tap_definitions
                ):
                    return "@lt"
            alias_name = self._holdtap_alias_name(
                (
                    binding.behavior.name
                    if hasattr(binding.behavior, "name")
                    else binding.behavior.type
                ),
                binding.params[0],
                binding.params[1],
            )
            if alias_name in self.hold_tap_definitions:
                return f"@{alias_name}"
            else:
                err_msg = f"Hold-tap alias '{alias_name}' not defined."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return f"<undef_holdtap:{alias_name}>"
        elif behavior_type == "trans":
            return "_"
        elif binding.behavior is None:
            if not binding.params or len(binding.params) < 1:
                err_msg = "Binding with no parameters."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return "<missing_param>"
            zmk_key = binding.params[0]
            return self.macro_transformer._convert_key(zmk_key)
        elif behavior_type == "kp":
            if not binding.params or len(binding.params) < 1:
                err_msg = "KP binding with no parameters."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return "<missing_param>"
            zmk_key = binding.params[0]
            return self.macro_transformer._convert_key(zmk_key)
        elif behavior_type in ["mo", "to", "tog"]:
            if not binding.params or len(binding.params) < 1:
                err_msg = f"{behavior_type} binding with no layer parameter."
                self.error_manager.add_error(err_msg, context={"binding": str(binding)})
                return f"<{behavior_type}_missing_layer>"
            layer_index_or_name = binding.params[0]
            layer_ref = layer_index_or_name
            if behavior_type == "mo":
                return f"(layer {layer_ref})"
            elif behavior_type == "to":
                return f"(layer-switch {layer_ref})"
            elif behavior_type == "tog":
                return f"(layer-toggle {layer_ref})"
        elif behavior_type == "macro":
            macro_name = binding.behavior.name
            if len(binding.params) > 0:
                macro_params = " ".join(
                    self.macro_transformer._convert_key(p) for p in binding.params
                )
                return f"(macro {macro_name} {macro_params})"
            else:
                return f"(macro {macro_name})"
        else:
            err_msg = f"Unknown binding type: {behavior_type}"
            self.error_manager.add_error(err_msg, context={"binding": str(binding)})
            return f"<unknown:{behavior_type}>"
        return None

    def _holdtap_alias_name(self, behavior_type, hold_param, tap_param):
        """Generate a consistent alias name for hold-tap behaviors."""
        hold = self.macro_transformer._convert_key(hold_param)
        tap = self.macro_transformer._convert_key(tap_param)
        if behavior_type == "lt":
            return f"lt_{hold}_{tap}"
        else:
            return f"ht_{hold}_{tap}"
