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
        For single-param hold-tap/tap-dance, emit a macro or comment for tap action only.
        For toggle-layer, emit a descriptive Kanata comment.
        Error comments include the original ZMK binding for easier debugging.
        """
        logging.debug(f"[KanataTransformer]     Transforming binding: {binding}")
        behavior_type = None
        if hasattr(binding, "behavior") and binding.behavior is not None:
            behavior_type = getattr(binding.behavior, "type", None)
            if behavior_type is None and hasattr(binding.behavior, "name"):
                behavior_type = binding.behavior.name

        # Map ZMK transparent/none to Kanata '_'
        if behavior_type in ("zmk,behavior-transparent", "zmk,behavior-none", "trans"):
            return "_"

        # Handle toggle-layer (to)
        if behavior_type == "zmk,behavior-toggle-layer":
            param = binding.params[0] if binding.params else "?"
            return f"; unsupported: toggle-layer to {param} (ZMK: {binding})"

        # Handle hold-tap/tap-dance with only one param
        if behavior_type in (
            "hold-tap",
            "zmk,behavior-hold-tap",
            "zmk,behavior-tap-dance",
        ):
            if len(binding.params) == 1:
                tap = binding.params[0]
                return (
                    f"{tap} ; tap only (ZMK: {binding}) "
                    f"; unsupported: missing hold param"
                )
            elif len(binding.params) == 2:
                # Normal case, handled as before
                pass
            else:
                return f"; unsupported: hold-tap/tap-dance malformed: {binding}"

        # Existing error handling for missing params
        if (
            behavior_type
            in ("hold-tap", "zmk,behavior-hold-tap", "zmk,behavior-tap-dance")
            and len(binding.params) < 2
        ):
            return f"; unsupported: hold-tap/tap-dance missing params: {binding}"

        # Unknown/unsupported behavior
        if behavior_type and behavior_type.startswith("zmk,behavior-"):
            return f"; unsupported: {behavior_type} binding: {binding}"

        # Fallback: try to emit the param or binding as-is
        if binding.params:
            return str(binding.params[0])
        return f"; unsupported: unknown binding: {binding}"

    def _holdtap_alias_name(self, behavior_type, hold_param, tap_param):
        """Generate a consistent alias name for hold-tap behaviors."""
        hold = self.macro_transformer._convert_key(hold_param)
        tap = self.macro_transformer._convert_key(tap_param)
        if behavior_type == "lt":
            return f"lt_{hold}_{tap}"
        else:
            return f"ht_{hold}_{tap}"
