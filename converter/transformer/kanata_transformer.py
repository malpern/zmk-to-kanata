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
from .sticky_key_transformer import StickyKeyTransformer

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
        self.sticky_key_transformer = StickyKeyTransformer()
        # Default configuration values
        self.config = {
            "tapping_term_ms": 200,
            "quick_tap_ms": 0,
            "tap_hold_wait_ms": None,
            "require_prior_idle_ms": None,
            "tap_hold_flavor": "hold-preferred",
        }

    def transform(self, keymap: KeymapConfig) -> str:
        """Transform the intermediate KeymapConfig into Kanata DSL format.
        Appends a summary of all errors as a Kanata comment at the end.
        Unsupported ZMK features are mapped to Kanata comments inline.
        """
        self.output = []
        self.hold_tap_definitions = {}
        self.macro_definitions = {}
        self.layer_count = len(keymap.layers)
        self.error_messages = []  # Collect error messages for summary

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
                    for layer in keymap.layers:
                        for binding in layer.bindings:
                            if binding and binding.behavior == behavior:
                                if not binding.params or len(binding.params) < 2:
                                    msg = (
                                        f"[KanataTransformer] Skipping hold-tap alias: "
                                        f"insufficient params for binding: {binding}"
                                    )
                                    logging.error(msg)
                                    self.error_messages.append(msg)
                                    continue
                                hold_param = binding.params[0]
                                tap_param = binding.params[1]
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
                                try:
                                    (
                                        alias_def,
                                        _alias_name,
                                    ) = self.holdtap_transformer.transform_behavior(
                                        behavior,
                                        hold_param,
                                        tap_param,
                                    )
                                except Exception as e:
                                    msg = (
                                        f"[KanataTransformer] Error generating hold-tap alias for "
                                        f"{alias_type}, {hold_param}, {tap_param}: {e}"
                                    )
                                    logging.error(msg)
                                    self.error_messages.append(msg)
                                    continue
                                if alias_name not in self.hold_tap_definitions:
                                    self.hold_tap_definitions[alias_name] = alias_def
                                    self.output.append(f"\n{alias_def}")
                                break
        holdtap_combos = set()
        for layer in keymap.layers:
            for binding in layer.bindings:
                if (
                    binding
                    and hasattr(binding, "behavior")
                    and binding.behavior is not None
                    and getattr(binding.behavior, "type", None)
                    in ("hold-tap", "zmk,behavior-mod-tap")
                ):
                    if not binding.params or len(binding.params) < 2:
                        msg = (
                            f"[KanataTransformer] Skipping hold-tap combo: "
                            f"insufficient params for binding: {binding}"
                        )
                        logging.error(msg)
                        self.error_messages.append(msg)
                        continue
                    modifier = binding.params[0]
                    key = binding.params[1]
                    btype = getattr(binding.behavior, "type", None)
                    bname = getattr(binding.behavior, "name", None)
                    holdtap_combos.add((btype, bname, modifier, key))
        for btype, bname, modifier, key in holdtap_combos:
            alias_type = bname if bname in ("lt", "mt") else btype
            behavior = None
            for layer in keymap.layers:
                for binding in layer.bindings:
                    if (
                        binding
                        and hasattr(binding, "behavior")
                        and binding.behavior is not None
                        and getattr(binding.behavior, "type", None) == btype
                        and getattr(binding.behavior, "name", None) == bname
                    ):
                        behavior = binding.behavior
                        break
                if behavior:
                    break
            if behavior is None:
                msg = (
                    f"[KanataTransformer] No behavior found for hold-tap alias: "
                    f"{alias_type}, {modifier}, {key}"
                )
                logging.warning(msg)
                self.error_messages.append(msg)
                continue
            alias_name = self._holdtap_alias_name(alias_type, modifier, key)
            try:
                alias_def, _alias_name = self.holdtap_transformer.transform_behavior(
                    behavior, modifier, key
                )
            except Exception as e:
                msg = (
                    f"[KanataTransformer] Error generating hold-tap alias for "
                    f"{alias_type}, {modifier}, {key}: {e}"
                )
                logging.error(msg)
                self.error_messages.append(msg)
                continue
            if alias_name not in self.hold_tap_definitions:
                self.hold_tap_definitions[alias_name] = alias_def
                self.output.append(f"\n{alias_def}")
        for layer in keymap.layers:
            try:
                self.output.append(self._transform_layer(layer))
            except Exception as e:
                msg = (
                    f"[KanataTransformer] Error transforming layer "
                    f"{getattr(layer, 'name', None)}: {e}"
                )
                logging.error(msg)
                self.error_messages.append(msg)
                self.output.append(
                    f"; <err: failed to transform layer {getattr(layer, 'name', None)}: {e}>"
                )
        # Append error summary as a Kanata comment
        if self.error_messages:
            self.output.append("\n; --- Unsupported/Unknown ZMK Features ---")
            for msg in self.error_messages:
                self.output.append(msg)
        return "\n".join(self.output)

    def _add_header(self):
        """Add Kanata configuration header."""
        self.output.append("(defcfg")
        self.output.append("  input (kb () () )")
        self.output.append("  output (kbd ())")
        self.output.append(")")
        self.output.append("")
        # Add global settings (tap-time, hold-time)
        tap_time = getattr(self, "tap_time", None) or self.config.get("tap_time", 200)
        hold_time = getattr(self, "hold_time", None) or self.config.get(
            "hold_time", 250
        )
        self.output.append(f"(defvar tap-time {tap_time})")
        self.output.append(f"(defvar hold-time {hold_time})")
        self.output.append("")

    def _transform_layer(self, layer: Layer) -> str:
        """
        Transform a single layer to Kanata format.
        Unsupported or malformed bindings are output as Kanata comments inline.
        """
        logging.debug(
            f"[KanataTransformer] Transforming layer: {layer.name} with {len(layer.bindings)} bindings"
        )
        lines = [f"(deflayer {layer.name}"]
        for idx, binding in enumerate(layer.bindings):
            logging.debug(f"  Binding {idx}: {binding}")
            result = self._transform_binding(binding)
            if result.startswith(";"):
                # Output comment as a separate line in the layer block
                lines.append(f"  {result}")
            else:
                lines.append(f"  {result}")
        lines.append(")")
        return "\n".join(lines)

    def _transform_binding(self, binding: Binding) -> str:
        """
        Transform a binding to Kanata format.
        If unsupported or unknown, emit a Kanata comment describing the ZMK feature.
        Replaces error markers with Kanata comments in layer output.
        """
        logging.debug(f"[KanataTransformer]     Transforming binding: {binding}")
        behavior_type = None
        if hasattr(binding, "behavior") and binding.behavior is not None:
            behavior_type = getattr(binding.behavior, "type", None)
            if behavior_type is None and hasattr(binding.behavior, "name"):
                behavior_type = binding.behavior.name

        # Map ZMK transparent/none to Kanata '_'
        if behavior_type in [
            "zmk,behavior-none",
            "zmk,behavior-transparent",
            "trans",
        ]:
            return "_"

        # Defensive: check params length for known behaviors
        try:
            # Treat zmk,behavior-mod-tap as hold-tap
            if (
                hasattr(binding, "behavior")
                and binding.behavior is not None
                and getattr(binding.behavior, "__class__", None)
                and (
                    binding.behavior.__class__.__name__ == "HoldTap"
                    or getattr(binding.behavior, "type", None)
                    in ("hold-tap", "zmk,behavior-mod-tap")
                )
            ):
                if not binding.params or len(binding.params) < 2:
                    msg = (
                        f"Hold-tap/mod-tap binding missing params: {binding}. "
                        f"This may be due to incomplete extraction or preprocessing."
                    )
                    logging.error(msg)
                    self.error_messages.append(msg)
                    self.error_manager.add_error(msg, context={"binding": str(binding)})
                    return "<err:missing_holdtap_params>"
                try:
                    hold_param = binding.params[0]
                except Exception:
                    hold_param = "<missing>"
                try:
                    tap_param = binding.params[1]
                except Exception:
                    tap_param = "<missing>"
                logging.debug(
                    f"[KanataTransformer] Accessing binding.params[0]: {hold_param}"
                )
                logging.debug(
                    f"[KanataTransformer] Accessing binding.params[1]: {tap_param}"
                )
                if hasattr(binding.behavior, "name"):
                    if (
                        binding.behavior.name == "mt"
                        and "mt" in self.hold_tap_definitions
                    ):
                        return "@mt"
                    elif (
                        binding.behavior.name == "lt"
                        and "lt" in self.hold_tap_definitions
                    ):
                        return "@lt"
                alias_name = self._holdtap_alias_name(
                    (
                        binding.behavior.name
                        if hasattr(binding.behavior, "name")
                        else binding.behavior.type
                    ),
                    hold_param,
                    tap_param,
                )
                if alias_name in self.hold_tap_definitions:
                    return f"@{alias_name}"
                else:
                    msg = f"Hold-tap alias '{alias_name}' not defined."
                    logging.error(msg)
                    self.error_messages.append(msg)
                    self.error_manager.add_error(msg, context={"binding": str(binding)})
                    return "<err:undef_holdtap>"
            elif binding.behavior is None:
                if not binding.params or len(binding.params) < 1:
                    msg = f"Binding with no parameters: {binding}"
                    logging.error(msg)
                    self.error_messages.append(msg)
                    self.error_manager.add_error(msg, context={"binding": str(binding)})
                    return "<err:missing_param>"
                try:
                    zmk_key = binding.params[0]
                except Exception:
                    zmk_key = "<missing>"
                logging.debug(
                    f"[KanataTransformer] Accessing binding.params[0]: {zmk_key}"
                )
                return self.macro_transformer._convert_key(zmk_key)
            elif behavior_type == "kp":
                if not binding.params or len(binding.params) < 1:
                    msg = f"KP binding with no parameters: {binding}"
                    logging.error(msg)
                    self.error_messages.append(msg)
                    self.error_manager.add_error(msg, context={"binding": str(binding)})
                    return "<err:missing_param>"
                try:
                    zmk_key = binding.params[0]
                except Exception:
                    zmk_key = "<missing>"
                logging.debug(
                    f"[KanataTransformer] Accessing binding.params[0]: {zmk_key}"
                )
                return self.macro_transformer._convert_key(zmk_key)
            elif behavior_type in ["mo", "to", "tog"]:
                if not binding.params or len(binding.params) < 1:
                    msg = f"{behavior_type} binding with no layer parameter: {binding}"
                    logging.error(msg)
                    self.error_messages.append(msg)
                    self.error_manager.add_error(msg, context={"binding": str(binding)})
                    return f"<err:{behavior_type}_missing_layer>"
                try:
                    layer_index_or_name = binding.params[0]
                except Exception:
                    layer_index_or_name = "<missing>"
                logging.debug(
                    f"[KanataTransformer] Accessing binding.params[0]: {layer_index_or_name}"
                )
                layer_ref = layer_index_or_name
                if behavior_type == "mo":
                    return f"(layer {layer_ref})"
                elif behavior_type == "to":
                    return f"(layer-switch {layer_ref})"
                elif behavior_type == "tog":
                    return f"(layer-toggle {layer_ref})"
            elif behavior_type == "macro":
                macro_name = binding.behavior.name
                if binding.params and len(binding.params) > 0:
                    macro_params = []
                    for i, p in enumerate(binding.params):
                        try:
                            macro_params.append(self.macro_transformer._convert_key(p))
                        except Exception as e:
                            msg = f"Error converting macro param {i}: {e}"
                            logging.error(msg)
                            self.error_messages.append(msg)
                            macro_params.append(f"<err:{e}>")
                    return f"(macro {macro_name} {' '.join(macro_params)})"
                else:
                    return f"(macro {macro_name})"
            elif (
                hasattr(binding, "behavior")
                and binding.behavior is not None
                and (
                    getattr(binding.behavior, "type", None) == "zmk,behavior-sticky-key"
                    or getattr(binding.behavior, "name", None) == "sk"
                )
            ):
                try:
                    return self.sticky_key_transformer.transform_binding(binding)
                except Exception as e:
                    msg = f"Error transforming sticky key: {e}"
                    logging.error(msg)
                    self.error_messages.append(msg)
                    self.error_manager.add_error(msg, context={"binding": str(binding)})
                    return "<err:sticky_key>"
            else:
                msg = f"Unknown binding type: {behavior_type} for binding: {binding}"
                logging.error(msg)
                self.error_messages.append(msg)
                self.error_manager.add_error(msg, context={"binding": str(binding)})
                return f"<err:unknown:{behavior_type}>"
        except Exception as e:
            # If a known behavior fails, emit a Kanata comment
            msg = f"; unsupported: {behavior_type} binding: {binding} (err: {e})"
            msg = msg[:79]  # Ensure line length
            self.error_messages.append(msg)
            return msg

        # Handle missing hold-tap/mod-tap params
        if behavior_type in ["hold-tap", "mod-tap"] and (
            not hasattr(binding, "params") or len(binding.params) < 2
        ):
            msg = f"; unsupported: hold-tap missing params: {binding.params}"
            msg = msg[:79]
            self.error_messages.append(msg)
            return msg

        # Unknown/unsupported behavior: emit Kanata comment
        err_msg = f"; unsupported: {behavior_type} binding: {binding.params}"
        err_msg = err_msg[:79]
        self.error_messages.append(err_msg)
        return err_msg

    def _holdtap_alias_name(self, behavior_type, hold_param, tap_param):
        """Generate a consistent alias name for hold-tap behaviors."""
        hold = self.macro_transformer._convert_key(hold_param)
        tap = self.macro_transformer._convert_key(tap_param)
        if behavior_type == "lt":
            return f"lt_{hold}_{tap}"
        else:
            return f"ht_{hold}_{tap}"
