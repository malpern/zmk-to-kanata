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

# --- Unsupported ZMK features and their Kanata equivalents/limitations ---
UNSUPPORTED_ZMK_FEATURES = {
    "zmk,behavior-bluetooth": (
        "No Kanata equivalent; Bluetooth switching is not supported."
    ),
    "zmk,behavior-bootloader": (
        "No Kanata equivalent; bootloader key is not supported."
    ),
    "zmk,behavior-caps-word": ("No Kanata equivalent; caps word is not supported."),
    # Add more as needed
}


class KanataTransformer:
    """Transforms ZMK keymap configurations to Kanata format.

    Unsupported ZMK features are mapped to Kanata comments inline.
    See UNSUPPORTED_ZMK_FEATURES for details.
    """

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
        """
        Transform the intermediate KeymapConfig into Kanata DSL format.

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
                                        "[KanataTransformer] Skipping hold-tap alias: "
                                        "insufficient params for binding: "
                                        f"{binding}"
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
                                        "[KanataTransformer] Error generating hold-tap alias for "
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
                            "[KanataTransformer] Skipping hold-tap combo: "
                            "insufficient params for binding: "
                            f"{binding}"
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
                    "[KanataTransformer] No behavior found for hold-tap alias: "
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
                    "[KanataTransformer] Error generating hold-tap alias for "
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
                    "[KanataTransformer] Error transforming layer "
                    f"{getattr(layer, 'name', None)}: {e}"
                )
                logging.error(msg)
                self.error_messages.append(msg)
                self.output.append(
                    f"; <err: failed to transform layer "
                    f"{getattr(layer, 'name', None)}: {e}>"
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
            f"[KanataTransformer] Transforming layer: {layer.name} "
            f"with {len(layer.bindings)} bindings"
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
        if behavior_type in (
            "zmk,behavior-transparent",
            "zmk,behavior-none",
            "trans",
        ):
            return "_"

        # Map ZMK key-repeat to Kanata 'rpt'
        if behavior_type == "zmk,behavior-key-repeat":
            return "rpt"

        # Map ZMK sticky-key to Kanata one-shot
        if behavior_type == "zmk,behavior-sticky-key":
            # Use one-shot 500 <key> (timeout 500ms, can be adjusted)
            key = binding.params[0] if binding.params else "?"
            return f"(one-shot 500 {key})"

        # Map ZMK sticky-layer to Kanata one-shot + layer-while-held
        if behavior_type == "zmk,behavior-sticky-layer":
            # Use one-shot 500 (layer-while-held <layer>)
            layer = binding.params[0] if binding.params else "?"
            return f"(one-shot 500 (layer-while-held {layer}))"

        # Handle known unsupported ZMK features
        if behavior_type in UNSUPPORTED_ZMK_FEATURES:
            zmk_syntax = getattr(binding.behavior, "name", behavior_type)
            param_str = " ".join(str(p) for p in binding.params)
            comment = (
                f"; unsupported: {zmk_syntax} {param_str} -- "
                f"{UNSUPPORTED_ZMK_FEATURES[behavior_type]}"
            )
            if len(comment) > 79:
                comment = comment[:76] + "..."
            return comment

        # Handle toggle-layer (to)
        if behavior_type == "zmk,behavior-toggle-layer":
            param = binding.params[0] if binding.params else "?"
            comment = f"; unsupported: toggle-layer to {param} " f"(ZMK: &to {param})"
            if len(comment) > 79:
                comment = comment[:76] + "..."
            return comment

        # Handle hold-tap/tap-dance with only one param
        if behavior_type in (
            "hold-tap",
            "zmk,behavior-hold-tap",
            "zmk,behavior-tap-dance",
        ):
            if len(binding.params) == 1:
                tap = binding.params[0]
                comment = (
                    f"{tap} ; tap only (ZMK: &{getattr(binding.behavior, 'name', 'td')} {tap}) "
                    f"; unsupported: missing hold param"
                )
                if len(comment) > 79:
                    comment = comment[:76] + "..."
                return comment
            elif len(binding.params) == 2:
                pass
            else:
                comment = (
                    f"; unsupported: hold-tap/tap-dance malformed: "
                    f"&{getattr(binding.behavior, 'name', 'td')} "
                    f"{' '.join(str(p) for p in binding.params)}"
                )
                if len(comment) > 79:
                    comment = comment[:76] + "..."
                return comment

        # Existing error handling for missing params
        if (
            behavior_type
            in ("hold-tap", "zmk,behavior-hold-tap", "zmk,behavior-tap-dance")
            and len(binding.params) < 2
        ):
            comment = (
                f"; unsupported: hold-tap/tap-dance missing params: "
                f"&{getattr(binding.behavior, 'name', 'td')} "
                f"{' '.join(str(p) for p in binding.params)}"
            )
            if len(comment) > 79:
                comment = comment[:76] + "..."
            return comment

        # Unknown/unsupported behavior
        if behavior_type and behavior_type.startswith("zmk,behavior-"):
            zmk_syntax = getattr(binding.behavior, "name", behavior_type)
            param_str = " ".join(str(p) for p in binding.params)
            comment = (
                f"; unsupported: {zmk_syntax} {param_str} "
                f"(ZMK: &{zmk_syntax} {param_str})"
            )
            if len(comment) > 79:
                comment = comment[:76] + "..."
            return comment

        # Fallback: try to emit the param or binding as-is
        if binding.params:
            return str(binding.params[0])
        return (
            f"; unsupported: unknown binding: "
            f"&{getattr(binding.behavior, 'name', 'unknown')} "
            f"{' '.join(str(p) for p in binding.params)}"
        )

    def _holdtap_alias_name(self, behavior_type, hold_param, tap_param):
        """Generate a consistent alias name for hold-tap behaviors."""
        hold = self.macro_transformer._convert_key(hold_param)
        tap = self.macro_transformer._convert_key(tap_param)
        if behavior_type == "lt":
            return f"lt_{hold}_{tap}"
        else:
            return f"ht_{hold}_{tap}"
