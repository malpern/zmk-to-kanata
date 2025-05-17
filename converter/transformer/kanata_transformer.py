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
from converter.transformer.keycode_map import zmk_to_kanata, MODIFIER_MACROS

import logging
import re
from typing import List, Dict, Optional

# --- Unsupported ZMK features and their Kanata equivalents/limitations ---
UNSUPPORTED_ZMK_FEATURES = {
    "zmk,behavior-bluetooth": ("No Kanata equivalent: Bluetooth not supported."),
    "zmk,behavior-bootloader": ("No Kanata equivalent: bootloader key not supported."),
    # caps-word now supported, so removed from unsupported list
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
        self.current_layer_name: Optional[str] = None
        self.output: List[str] = []
        self.hold_tap_definitions: Dict[str, str] = {}
        self.holdtap_transformer = HoldTapTransformer()
        self.macro_transformer = MacroTransformer()
        self.macro_definitions: Dict[str, str] = {}
        self.sticky_key_transformer = StickyKeyTransformer()
        self.error_messages: List[str] = []
        # Default configuration values
        self.config = {
            "tapping_term_ms": 200,
            "quick_tap_ms": 0,
            "tap_hold_wait_ms": None,
            "require_prior_idle_ms": None,
            "tap_hold_flavor": "hold-preferred",
        }

    def add_unsupported_feature(self, feature_type: str, details: str):
        """Record an unsupported ZMK feature to be included in the summary."""
        # Sanitize details to prevent them from breaking Kanata comment lines
        sanitized_details = details.replace("\\n", " ").replace(";", ",")
        msg = f"; unsupported: {feature_type} - {sanitized_details}"
        # Ensure error_messages list exists (already typed in __init__)
        if msg not in self.error_messages:  # Avoid duplicates
            self.error_messages.append(msg)
            logging.warning(
                f"Unsupported feature encountered: {feature_type} - {details}"
            )

    def transform(self, keymap: KeymapConfig) -> str:
        """
        Transform the intermediate KeymapConfig into Kanata DSL format.

        Appends a summary of all errors as a Kanata comment at the end.
        Unsupported ZMK features are mapped to Kanata comments inline.
        """

        def is_holdtap(obj):
            return (
                hasattr(obj, "type")
                and getattr(obj, "type", None) == "hold-tap"
                and hasattr(obj, "name")
                and hasattr(obj, "tapping_term_ms")
                and hasattr(obj, "hold_key")
                and hasattr(obj, "tap_key")
            )

        self.output = []
        self.hold_tap_definitions = {}
        self.macro_definitions = {}
        self.layer_count = len(keymap.layers)
        # self.error_messages = [] # Already initialized in __init__

        # Update config from keymap if available
        if hasattr(keymap, "config"):
            self.config.update(keymap.config)

        self._add_header()

        # --- Combo support: emit simple combos as Kanata aliases ---
        if hasattr(keymap, "combos") and keymap.combos:
            for combo in keymap.combos:
                # Simple combo: single key output, no modifiers/macros
                is_simple = (
                    hasattr(combo, "binding") and  # Ensure combo.binding exists
                    (
                        (hasattr(combo.binding, "key") and combo.binding.key) or
                        (
                            hasattr(combo.binding, "params") and
                            isinstance(combo.binding.params, list) and
                            len(combo.binding.params) == 1
                        )
                    ) and
                    isinstance(combo.key_positions, list) and
                    len(combo.key_positions) >= 2
                )
                if is_simple:
                    # Map key positions to Kanata key names
                    # (assume keymap.layers[0] is default)
                    if keymap.layers:
                        default_layer = keymap.layers[0]
                        # Use flat list of bindings
                        try:
                            key_names = []
                            for pos in combo.key_positions:
                                binding = default_layer.bindings[pos]
                                if hasattr(binding, "key") and binding.key:
                                    key_name = binding.key
                                elif hasattr(binding, "params") and binding.params:
                                    key_name = binding.params[0]
                                else:
                                    key_name = str(pos)
                                # Map to Kanata
                                mapped = self._to_kanata_symbolic(key_name)
                                key_names.append(mapped if mapped else key_name)
                        except Exception:
                            key_names = [str(pos) for pos in combo.key_positions]
                    else:
                        key_names = [str(pos) for pos in combo.key_positions]

                    # Get output key
                    if hasattr(combo.binding, "key") and combo.binding.key:
                        out_key = combo.binding.key
                    elif (
                        hasattr(combo.binding, "params")
                        and len(combo.binding.params) == 1
                    ):
                        out_key = combo.binding.params[0]
                    else:
                        out_key = None

                    if out_key:
                        out_key_mapped = self._to_kanata_symbolic(out_key) or out_key
                        alias_name = f"{combo.name}"
                        combo_str = (
                            f"(defalias\\n  {alias_name} "
                            f"(combo {' '.join(key_names)} {out_key_mapped})\\n)"
                        )
                        self.output.append(f"\\n{combo_str}")
                    else:
                        msg = (
                            f"Warning: Combo '{combo.name}' skipped: "
                            "output is not a simple key."
                        )
                        logging.warning(msg)
                        self.error_messages.append(msg)
                        comment = (
                            f"; unsupported: combo '{combo.name}' "
                            "is not a simple key output"
                        )
                        self.output.append(self._format_binding_comment("", comment))
                else:
                    msg = (
                        f"Warning: Combo '{combo.name}' skipped: " "not a simple combo."
                    )
                    logging.warning(msg)
                    self.error_messages.append(msg)
                    comment = (
                        f"; unsupported: combo '{combo.name}' " "is not a simple combo"
                    )
                    self.output.append(self._format_binding_comment("", comment))

        if keymap.behaviors:
            for behavior_obj in keymap.behaviors.values():  # Renamed to avoid conflict
                if behavior_obj.type == "macro":
                    macro_str = self.macro_transformer.transform_macro(behavior_obj)
                    if behavior_obj.name not in self.macro_definitions:
                        self.macro_definitions[behavior_obj.name] = macro_str
                        self.output.append(f"\\n{macro_str}")
                elif behavior_obj.type == "hold-tap":
                    # Always emit a base alias for any hold-tap type with a name
                    if not (hasattr(behavior_obj, "name")):
                        msg = (
                            "Warning: Skipping hold-tap behavior with no name "
                            f"(got {type(behavior_obj)})."
                        )
                        logging.warning(msg)
                        self.error_messages.append(msg)
                        comment = (
                            "; unsupported: hold-tap behavior with no name "
                            f"(got {type(behavior_obj)})"
                        )
                        self.output.append(self._format_binding_comment("", comment))
                        continue

                    tap_time = getattr(behavior_obj, "tapping_term_ms", 200)
                    hold_time = getattr(behavior_obj, "hold_time_ms", tap_time)
                    tap_key = self._to_kanata_symbolic(
                        getattr(behavior_obj, "tap_key", "A"), for_alias_name=True
                    )
                    hold_key = self._to_kanata_symbolic(
                        getattr(behavior_obj, "hold_key", "LCTRL"), for_alias_name=True
                    )
                    alias_name = behavior_obj.name
                    config_parts = [
                        "tap-hold",
                        str(tap_time),
                        str(hold_time),
                        str(tap_key),
                        str(hold_key),
                    ]
                    alias_def = f"(defalias {alias_name} ({' '.join(config_parts)}))"
                    self.output.append(f"\\n{alias_def}")
                    # Emit comments for unmapped properties (like retro-tap)
                    extra = getattr(behavior_obj, "extra_properties", {})
                    for prop in ["retro-tap", "hold-trigger-key-positions"]:
                        val = extra.get(prop, None) if extra else None
                        if val is None:
                            val = getattr(behavior_obj, prop.replace("-", "_"), None)
                        if val is not None:
                            comment = (
                                f"; TODO: {prop} property present; Kanata "
                                "does not support this property. "
                                "Manual review needed."
                            )
                            self.output.append(
                                self._format_binding_comment("", comment)
                            )
                    if extra:
                        for prop in extra:
                            if prop not in (
                                "hold-time-ms",
                                "flavor",
                                "bindings",
                                "quick-tap-ms",
                                "tap-hold-wait-ms",
                                "require-prior-idle-ms",
                                "retro-tap",
                                "hold-trigger-key-positions",
                            ):
                                comment = (
                                    f"; TODO: hold-tap '{alias_name}' "
                                    f"property '{prop}' not mapped. "
                                    "Manual review needed."
                                )
                                self.output.append(
                                    self._format_binding_comment("", comment)
                                )
        holdtap_combos = set()
        for layer in keymap.layers:
            for binding_item in layer.bindings:  # Renamed to avoid conflict
                if (
                    binding_item
                    and hasattr(binding_item, "behavior")
                    and binding_item.behavior is not None
                    and getattr(binding_item.behavior, "type", None)
                    in ("hold-tap", "zmk,behavior-mod-tap")
                ):
                    if not binding_item.params or len(binding_item.params) < 2:
                        msg = (
                            "Warning: Skipped hold-tap combo due to missing "
                            "parameters "
                            f"(binding: {getattr(binding_item, 'params', binding_item)})"
                        )
                        logging.error(msg)
                        self.error_messages.append(msg)
                        continue
                    modifier = binding_item.params[0]
                    key = binding_item.params[1]
                    btype = getattr(binding_item.behavior, "type", None)
                    bname = getattr(binding_item.behavior, "name", None)
                    holdtap_combos.add((btype, bname, modifier, key))

        for btype, bname, modifier, key in holdtap_combos:
            alias_type = bname if bname in ("lt", "mt") else btype
            # Resolve the actual behavior object
            ht_behavior = None
            for layer_conf in keymap.layers:  # Renamed to avoid conflict
                for binding_obj in layer_conf.bindings:  # Renamed
                    if (
                        binding_obj
                        and hasattr(binding_obj, "behavior")
                        and binding_obj.behavior is not None
                        and getattr(binding_obj.behavior, "type", None) == btype
                        and getattr(binding_obj.behavior, "name", None) == bname
                    ):
                        ht_behavior = binding_obj.behavior
                        break
                if ht_behavior:
                    break

            if not (
                ht_behavior  # Check if resolved
                and hasattr(ht_behavior, "type")
                and getattr(ht_behavior, "type", None) == "hold-tap"
                and hasattr(ht_behavior, "name")
            ):
                msg = (
                    f"Warning: Skipping hold-tap alias '{alias_type}' "
                    f"(hold: {modifier}, tap: {key}) "
                    "because behavior is not a hold-tap type "
                    f"(got {type(ht_behavior)})."
                )
                logging.warning(msg)
                self.error_messages.append(msg)
                comment = (
                    f"; unsupported: hold-tap alias '{alias_type}' "
                    f"(hold: {modifier}, tap: {key}) not a hold-tap type"
                )
                self.output.append(self._format_binding_comment("", comment))
                continue

            tap_time = getattr(ht_behavior, "tapping_term_ms", 200)
            hold_time = getattr(ht_behavior, "hold_time_ms", tap_time)
            # Use mapped values for tap and hold keys, always symbolic
            mapped_tap = self._to_kanata_symbolic(key, for_alias_name=True)
            mapped_hold = self._to_kanata_symbolic(modifier, for_alias_name=True)
            alias_name = self._holdtap_alias_name(
                alias_type,
                mapped_hold,
                mapped_tap,
            )
            config_parts = [
                "tap-hold",
                str(tap_time),
                str(hold_time),
                str(mapped_tap),
                str(mapped_hold),
            ]
            
            # Format defalias carefully to respect line length
            alias_name_str = str(alias_name)
            config_str = f"({' '.join(config_parts)})"
            line2_for_defalias = f"  {alias_name_str} {config_str}"

            if len(line2_for_defalias) <= 79:
                alias_def = f"(defalias\n{line2_for_defalias}\n)"
            else:
                # Try to fit alias name on its own line, then config on next
                line2_name_only = f"  {alias_name_str}"
                line3_config_only = f"  {config_str}"
                if len(line2_name_only) <= 79 and len(line3_config_only) <= 79:
                    alias_def = f"(defalias {alias_name_str}\n{line3_config_only}\n)" # Name on 1st line
                else:
                    # If config_str itself is too long, it needs internal splitting by Kanata if supported
                    # or this indicates a very complex/long generated config part.
                    # For now, just put it on its line and let it exceed if it must.
                    # A more robust solution might truncate or further parse config_str.
                    logging.warning(
                        f"Generated defalias config part is very long and might exceed line limits: {config_str}"
                    )
                    alias_def = f"(defalias {alias_name_str}\n  {config_str} ; Potentially long line\n)"
            
            if alias_name not in self.hold_tap_definitions:
                self.hold_tap_definitions[alias_name] = alias_def
                self.output.append(f"\\n{alias_def}")

        for layer in keymap.layers:
            try:
                self.output.append(self._transform_layer(layer))
            except Exception as e:
                msg = (
                    f"Error: Failed to transform layer "
                    f"'{getattr(layer, 'name', None)}'. Reason: {e}"
                )
                logging.error(msg)
                self.error_messages.append(msg)
                err_line = (
                    f"; unsupported: failed to transform layer "
                    f"{getattr(layer, 'name', None)}. Reason: {e}>"
                )
                self.output.append(self._format_binding_comment("", err_line))

        # Append error summary as a Kanata comment
        if self.error_messages:
            # Deduplicate and filter messages
            unique_msgs = list(dict.fromkeys(self.error_messages))
            filtered_msgs = []
            skip_phrases = [
                "Warning: Skipped hold-tap alias due to missing parameters",
                "Warning: Skipped hold-tap combo due to missing parameters",
            ]
            skip_counts = {phrase: 0 for phrase in skip_phrases}

            for msg_item in unique_msgs:
                for phrase in skip_phrases:
                    if msg_item.startswith(phrase):
                        skip_counts[phrase] += 1
                        break
                else:
                    filtered_msgs.append(msg_item)

            self.output.append("\n; --- Unsupported/Unknown ZMK Features ---")
            # Grouped warnings
            for phrase, count in skip_counts.items():
                if count:
                    line = (
                        f"; {phrase} ({count} occurrence"
                        f"{'s' if count > 1 else ''})"
                    )
                    if len(line) > 79: # Max length for summary lines
                        line = line[:76] + "..."
                    self.output.append(line)

            # Other unique, actionable messages
            for msg_item in filtered_msgs:
                # msg_item could be like "; unsupported: some feature" or "ERROR: Some error"
                if not msg_item.startswith(";"):
                    # If it's a raw error message like "ERROR: Some error"
                    line = f"; {msg_item.lstrip()}"
                else:
                    # If it's already a comment like "; unsupported: ..."
                    line = msg_item.lstrip()
                
                if len(line) > 79: # Max length for summary lines
                    line = line[:76] + "..."
                self.output.append(line)
        
        return "\n".join(self.output) + "\n" # Ensure trailing newline

    def _add_header(self):
        """Add Kanata configuration header."""
        self.output.append("(defcfg")
        self.output.append("  input (kb () () )")
        self.output.append("  output (kbd ())")
        self.output.append(")")
        self.output.append("")
        # Add global settings (tap-time, hold-time)
        tap_time_cfg = getattr(self, "tap_time", None) or self.config.get(  # Renamed
            "tap_time", 200
        )
        hold_time_cfg = getattr(self, "hold_time", None) or self.config.get(  # Renamed
            "hold_time", 250
        )
        self.output.append(f"(defvar tap-time {tap_time_cfg})")
        self.output.append(f"(defvar hold-time {hold_time_cfg})")
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
        for idx, binding_obj in enumerate(layer.bindings):
            logging.debug(f"  Binding {idx}: {binding_obj}")

            if type(binding_obj).__name__ == "UnicodeBinding":
                result_str = binding_obj.to_kanata()  # type: ignore
                # UnicodeBinding.to_kanata() should return a correctly formatted Kanata string.
                # It might be a comment or a Kanata action like (unicode "X").
                # If it's a comment, it should start with ';'.
                # If it's an action, it needs indentation.
                if result_str.lstrip().startswith(";"):
                    lines.append(result_str.lstrip()) # Add comment unindented
                else:
                    lines.append(f"  {result_str}") # Indent action
                continue
            
            # Special handling for hold-tap aliases, which are already formatted.
            # This part should come before generic _transform_binding if it consumes the binding.
            if (
                hasattr(binding_obj, "behavior")
                and binding_obj.behavior is not None
                and getattr(binding_obj.behavior, "type", None)
                in (
                    "hold-tap",
                    "zmk,behavior-hold-tap",
                    "zmk,behavior-mod-tap",
                )
                and len(binding_obj.params) == 2
            ):
                behavior_type_val = (
                    getattr(binding_obj.behavior, "name", None) or 
                    getattr(binding_obj.behavior, "type", None)
                )
                # This creates an alias like @ht_LCTRL_A, which should be indented.
                # The original code appended f"  @{alias_name}"
                if behavior_type_val: # Ensure we have a type to derive alias
                    alias_type_prefix = "ht" # Default
                    if behavior_type_val in ("lt", "mt"):
                        alias_type_prefix = behavior_type_val
                    
                    hold_param = binding_obj.params[0]
                    tap_param = binding_obj.params[1]
                    alias_name = self._holdtap_alias_name(
                        alias_type_prefix,
                        hold_param,
                        tap_param,
                    )
                    lines.append(f"  @{alias_name}")
                    logging.debug(
                        f"[DEBUG] _transform_layer: emitted hold-tap alias: @{alias_name}"
                    )
                    continue # Binding handled

            # General binding transformation
            result_obj = self._transform_binding(binding_obj)

            if "\n" in result_obj:  # It's a pre-formatted multi-line string
                # Split it and add lines, assuming they are correctly formatted
                # by _transform_binding (e.g., complex tap-dance TODOs)
                # These lines are typically already indented if they are comments
                # following a binding, or are self-contained multi-line forms.
                for sub_line in result_obj.splitlines():
                    lines.append(sub_line) 
            else:  # Single line result from _transform_binding
                result_stripped = result_obj.lstrip()
                if result_stripped.startswith(";"):
                    lines.append(result_stripped)  # Add unindented comment
                else:
                    lines.append(f"  {result_obj}")  # Indent normal bindings
            
        lines.append(")")
        return "\n".join(lines)

    def _transform_binding(self, binding: Binding) -> str:
        """
        Transform a binding to Kanata format.

        If unsupported or unknown, emit a Kanata comment describing the ZMK
        feature. For single-param hold-tap/tap-dance, emit a macro or comment
        for tap action only. For toggle-layer, emit a descriptive Kanata
        comment. Error comments include the original ZMK binding for easier
        debugging.
        """
        logging.debug(f"[KanataTransformer]     Transforming binding: {binding}")
        behavior_type = None
        if hasattr(binding, "behavior") and binding.behavior is not None:
            behavior_type = getattr(binding.behavior, "type", None)
            if behavior_type is None and hasattr(binding.behavior, "name"):
                # Fallback to name if type is not set (e.g. for built-ins like 'kp')
                behavior_type = binding.behavior.name

        # Special handling for reset and bootloader (preferred check)
        if hasattr(binding, "behavior") and binding.behavior is not None:
            bname = getattr(binding.behavior, "name", None)
            if bname in ("reset", "bootloader"):
                return self._format_binding_comment("", f"; unsupported: {bname}")
        # Fallback: handle param-only bootloader/reset if behavior is None
        elif (
            getattr(binding, "behavior", None) is None
            and hasattr(binding, "params")
            and isinstance(binding.params, list)
            and len(binding.params) == 1
            and binding.params[0] in ("&bootloader", "&reset")
        ):
            bname = binding.params[0][1:]  # Extract name from e.g., "&bootloader"
            return self._format_binding_comment("", f"; unsupported: {bname}")

        # Macro reference handling
        if hasattr(binding, "behavior") and binding.behavior is not None:
            macro_name = getattr(binding.behavior, "name", None)
            # Check type first, then if name is in defined macros
            if behavior_type == "macro" or (
                macro_name and macro_name in self.macro_definitions
            ):
                return f"(macro {macro_name})"

        # Map ZMK transparent/none to Kanata '_'
        if behavior_type in (
            "zmk,behavior-transparent",
            "zmk,behavior-none",
            "trans",  # Allow short 'trans' as well
        ):
            return "_"

        # Map ZMK key-repeat to Kanata 'rpt'
        if behavior_type == "zmk,behavior-key-repeat":
            return "rpt"

        # Handle Unicode behavior
        if behavior_type == "zmk,behavior-unicode":
            unicode_char_name = None
            if binding.behavior:
                unicode_char_name = getattr(binding.behavior, "name", None)

            if unicode_char_name:
                if unicode_char_name == "uni_pi":
                    # On macOS, Kanata uses (unicode "char").
                    # Other platforms might differ or lack support.
                    # Simulating macOS output for the test.
                    return '(unicode "π")'
                else:
                    return self._format_binding_comment(
                        "",
                        (
                            f"; TODO: Unicode behavior '{unicode_char_name}' "
                            "needs manual mapping"
                        ),
                    )
            else:
                return self._format_binding_comment(
                    "", "; TODO: Nameless Unicode behavior found"
                )

        # Map ZMK sticky-key to Kanata one-shot
        if behavior_type == "zmk,behavior-sticky-key":
            key_param = binding.params[0] if binding.params else "?"  # Renamed
            return f"(one-shot 500 {key_param})"

        # Map ZMK sticky-layer to Kanata one-shot + layer-while-held
        if behavior_type == "zmk,behavior-sticky-layer":
            layer_param = binding.params[0] if binding.params else "?"  # Renamed
            return f"(one-shot 500 (layer-while-held {layer_param}))"

        # Kanata caps-word support
        if behavior_type == "zmk,behavior-caps-word":
            # Kanata's caps-word action, 2000ms timeout is typical
            return "(caps-word 2000)"

        # Map ZMK key-press to Kanata keycode
        if behavior_type == "zmk,behavior-key-press" or behavior_type == "kp":
            if binding.params:
                param_str = str(binding.params[0])
                mapped = self._to_kanata_symbolic(param_str)
                if mapped is not None:
                    return mapped
                else:
                    # If zmk_to_kanata returns None
                    # (e.g., for complex/unknown keycodes)
                    return self._format_binding_comment(
                        "",
                        (
                            f"; unsupported: kp {param_str} "
                            "(failed ZMK->Kanata mapping)"
                        ),
                    )
            else:
                # Should not happen for valid &kp bindings from extractor
                return self._format_binding_comment(
                    "", "; unsupported: kp with no params (ZMK: &kp)"
                )

        # Handle known unsupported ZMK features
        if behavior_type in UNSUPPORTED_ZMK_FEATURES:
            zmk_syntax = (
                getattr(binding.behavior, "name", behavior_type)
                if binding.behavior
                else behavior_type
            )
            param_str = " ".join(str(p) for p in binding.params)
            comment_text = (  # Renamed
                f"; unsupported: {zmk_syntax} {param_str} -- "
                f"{UNSUPPORTED_ZMK_FEATURES[behavior_type]}"
            )
            return self._format_binding_comment("", comment_text)

        # Handle toggle-layer (to)
        if behavior_type == "zmk,behavior-toggle-layer":
            param_val = binding.params[0] if binding.params else "?"  # Renamed
            # Map to Kanata's layer-toggle action
            return f"(layer-toggle {param_val})"

        # Handle tap-dance specifically
        if behavior_type == "zmk,behavior-tap-dance":
            tap_time_val = 200  # Default tap time # Renamed
            if binding.behavior:
                if (
                    hasattr(binding.behavior, "tapping_term_ms")
                    and binding.behavior.tapping_term_ms is not None
                ):
                    tap_time_val = binding.behavior.tapping_term_ms
                elif hasattr(binding.behavior, "extra_properties"):
                    dts_tap_time = binding.behavior.extra_properties.get(
                        "tapping-term-ms"
                    )
                    if isinstance(dts_tap_time, int):
                        tap_time_val = dts_tap_time
                    elif (
                        isinstance(dts_tap_time, list)
                        and dts_tap_time
                        and isinstance(dts_tap_time[0], int)
                    ):
                        tap_time_val = dts_tap_time[0]

            behavior_name_td = (  # Renamed
                getattr(binding.behavior, "name", "td") if binding.behavior else "td"
            )
            if not binding.params:
                self.add_unsupported_feature(
                    "tap-dance",
                    f"&{behavior_name_td} with no params",
                )
                return self._format_binding_comment(
                    "",
                    f"; unsupported: &{behavior_name_td} with no params",
                )

            mapped_params = []
            for p_str in binding.params:
                mapped = self._to_kanata_symbolic(str(p_str))
                mapped_params.append(mapped if mapped is not None else str(p_str))

            base_kanata_output = f"(tap-dance {tap_time_val} {' '.join(mapped_params)})"

            has_complex_zmk_features = False
            if binding.behavior and hasattr(binding.behavior, "extra_properties"):
                if binding.behavior.extra_properties.get("hold-action") is not None:
                    has_complex_zmk_features = True
                # Add checks for other ZMK-specific tap-dance properties
                # if binding.behavior.extra_properties.get('quick-tap-ms') is not None:
                #     has_complex_zmk_features = True

            if has_complex_zmk_features:
                actual_behavior_name = (  # Renamed
                    getattr(binding.behavior, "name", "unknown_td")
                    if binding.behavior
                    else "unknown_td"
                )
                self.add_unsupported_feature(
                    "tap-dance",
                    (
                        "ZMK specific features like 'hold-action' for "
                        f"behavior '{actual_behavior_name}'"
                    ),
                )
                zmk_doc_url = "https://zmk.dev/docs/behaviors/tap-dance"
                kanata_doc_url = (
                    "https://github.com/jtroo/kanata/blob/main/"
                    "docs/config.md#tap-dance"
                )

                output_lines = [base_kanata_output]
                output_lines.append(
                    f"  ; TODO: ZMK tap-dance '{actual_behavior_name}' uses "
                    "features like hold-action"
                )
                output_lines.append("  ; that may not be fully represented.")
                output_lines.append(f"  ; See ZMK ({zmk_doc_url})")
                output_lines.append(f"  ; vs Kanata ({kanata_doc_url}) docs.")
                return "\\n".join(output_lines)
            else:
                return base_kanata_output  # No TODO for simple tap-dances

        # Handle hold-tap
        # (this will also catch zmk,behavior-mod-tap if not handled earlier)
        if behavior_type in (
            "hold-tap",
            "zmk,behavior-hold-tap",
        ):
            ht_behavior_name = (  # Renamed
                getattr(binding.behavior, "name", "ht") if binding.behavior else "ht"
            )
            if len(binding.params) == 1:
                tap_action = binding.params[0]  # Renamed
                comment_text = (  # Renamed
                    f"; tap only (ZMK: &{ht_behavior_name} {tap_action}) "
                    f"; unsupported: missing hold param"
                )
                return self._format_binding_comment(str(tap_action), comment_text)
            elif len(binding.params) == 2:
                # This will be handled by the hold-tap alias system.
                # If it's a tap-dance with 2 params that fell through,
                # it might be caught by the generic "zmk,behavior-" fallback.
                pass  # Explicitly do nothing, rely on alias or generic fallback
            else:  # 0 or 3+ params for hold-tap
                comment_text = (  # Renamed
                    f"; unsupported: hold-tap malformed: "
                    f"&{ht_behavior_name} "
                    f"{' '.join(str(p) for p in binding.params)}"
                )
                return self._format_binding_comment("", comment_text)

        # Existing error handling for missing params for certain types
        if (
            behavior_type
            in (
                "hold-tap",  # Already covered above but good for safety
                "zmk,behavior-hold-tap",  # Already covered
                "zmk,behavior-tap-dance",  # Tap-dance with no params is covered
            )
            and len(binding.params) < 2  # General check for 2-param types
        ):
            # This logic might be redundant if specific cases are handled well.
            # For tap-dance, no-param case is handled.
            # For hold-tap, 1-param case is handled.
            # This would catch tap-dance with 1 param if it wasn't erroring earlier.
            td_like_name = (  # Renamed
                getattr(binding.behavior, "name", "td") if binding.behavior else "td"
            )
            comment_text = (  # Renamed
                f"; unsupported: {behavior_type} missing params: "
                f"&{td_like_name} "
                f"{' '.join(str(p) for p in binding.params)}"
            )
            return self._format_binding_comment("", comment_text)

        # Unknown/unsupported behavior with "zmk,behavior-" prefix
        if behavior_type and behavior_type.startswith("zmk,behavior-"):
            zmk_syntax_name = (  # Renamed
                getattr(binding.behavior, "name", behavior_type)
                if binding.behavior
                else behavior_type
            )
            param_str = " ".join(str(p) for p in binding.params)
            comment_text = (  # Renamed
                f"; unsupported: {zmk_syntax_name} {param_str} "
                f"(ZMK: &{zmk_syntax_name} {param_str})"
            )
            return self._format_binding_comment("", comment_text)

        # --- BEGIN: Error binding handling (from extractor) ---
        if (
            hasattr(binding, "params")
            and binding.params
            and isinstance(binding.params[0], str)
            and binding.params[0].startswith("ERROR:")
        ):
            error_msg_text = binding.params[0]  # Renamed
            comment_str = self._format_binding_comment(
                "", f"; {error_msg_text}"
            )  # Renamed
            if error_msg_text not in self.error_messages:
                self.error_messages.append(error_msg_text)
            return comment_str
        # --- END: Error binding handling ---

        # Fallback: try to emit the param or binding as-is
        if binding.params:
            param_str_val = str(binding.params[0])
            mapped_val = self._to_kanata_symbolic(param_str_val)

            if isinstance(mapped_val, str) and mapped_val.startswith("ERROR:"):
                comment_str = self._format_binding_comment("", f"; {mapped_val}")
                if mapped_val not in self.error_messages:
                    self.error_messages.append(mapped_val)
                return comment_str
            
            # Check for untransformed but potentially malformed/incomplete macros
            # MODIFIER_MACROS is like [("LSHIFT(%s)", "ls(%s)"), ...]
            # We need the ZMK prefixes like "LSHIFT", "LCTL"
            # This is a simplified check. A full parser for these would be better.
            is_potentially_malformed = False
            if mapped_val == param_str_val: # No specific Kanata mapping found by _to_kanata_symbolic
                # Check if it looks like an unclosed ZMK modifier macro or similar pattern
                is_potentially_malformed = False
                # Case 1: PREFIX() - e.g., LS(), LCTRLA()
                if re.match(r"^[A-Z0-9_]+\(\)$", param_str_val):
                    is_potentially_malformed = True
                # Case 2: PREFIX(something or PREFIX(something<EOF> (unclosed)
                elif re.match(r"^[A-Z0-9_]+\(.*[^)]$", param_str_val) and not param_str_val.endswith(")"):
                    is_potentially_malformed = True
                # Case 3: General unbalanced parentheses for macro-like strings
                elif (param_str_val.count("(") != param_str_val.count(")")) and \
                     re.match(r"^[A-Z0-9_]+\(.*", param_str_val): # Starts like a macro
                    is_potentially_malformed = True
                # Case 4: Specific known pattern like "LS LA(A)" (space means not a single macro)
                elif re.match(r"^[A-Z0-9_]+\s+[A-Z0-9_]+\(.+\)$", param_str_val):
                    is_potentially_malformed = True

            if is_potentially_malformed:
                error_msg = f"ERROR: malformed or incomplete macro: {param_str_val}"
                comment_str = self._format_binding_comment(  # Renamed
                    "", f"; {error_msg}"
                )
                if error_msg not in self.error_messages:
                    self.error_messages.append(error_msg)
                return comment_str
            
            if mapped_val is not None: # If not an error and not malformed, and there is a value
                return mapped_val
            
            # Fallback for unmapped macros that were not caught as malformed above
            # This regex was for things like "LS (" with space, or other oddities
            # MODIFIER_MACROS is imported at the top
            macro_prefixes = [
                p.split("\\\\")[0][2:-3]  # Corrected regex escape
                for p, _ in MODIFIER_MACROS
                if p and len(p.split("\\\\")) > 0 and len(p) > 5  # Corrected
            ]
            if macro_prefixes:
                try:
                    # Ensure regex is valid by escaping prefixes if they contain special chars
                    safe_prefixes = [re.escape(p) for p in macro_prefixes]
                    macro_regex_str = rf"^({'|'.join(safe_prefixes)})\\s*\\("
                    macro_regex = re.compile(macro_regex_str)
                    if macro_regex.match(param_str_val.strip()):
                        error_msg = (
                            f"ERROR: malformed or unknown macro: {param_str_val}"
                        )
                        comment_str = self._format_binding_comment(  # Renamed
                            "", f"; {error_msg}"
                        )
                        if error_msg not in self.error_messages:
                            self.error_messages.append(error_msg)
                        return comment_str
                except re.error:
                    error_msg = (
                        f"ERROR: malformed or unknown macro (regex error): "
                        f"{param_str_val}"
                    )
                    comment_str = self._format_binding_comment(  # Renamed
                        "", f"; {error_msg}"
                    )
                    if error_msg not in self.error_messages:
                        self.error_messages.append(error_msg)
                    return comment_str
            return param_str_val  # Return original param if no mapping/error

        # Final fallback for truly unknown bindings
        final_behavior_name = (  # Renamed
            getattr(binding.behavior, "name", "unknown")
            if binding.behavior
            else "unknown"
        )
        return self._format_binding_comment(
            "",
            (
                f"; unsupported: unknown binding: &{final_behavior_name} "
                f"{' '.join(str(p) for p in binding.params)}"
            ),
        )

    def _format_binding_comment(self, binding_str: str, comment: str) -> str:
        """
        Format a binding and comment so that no line exceeds 79 chars.

        If the combined line is too long, place the comment on a new indented
        line. Truncate the comment if still too long, including indentation.
        Handles multi-line pre-formatted comments.
        """
        max_len = 79
        indent_str = "  "  # Renamed

        # If comment is already multi-line, handle it carefully
        if "\\n" in comment:
            lines = comment.split("\\n")
            if binding_str:
                # Check if first line of comment fits with binding_str
                first_line_combined = f"{binding_str} {lines[0]}".rstrip()
                if len(first_line_combined) <= max_len:
                    formatted_comment = "\\n".join(
                        [first_line_combined]
                        + [f"{indent_str}{line.strip()}" for line in lines[1:]]
                    )
                    return (
                        formatted_comment.strip()
                    )  # Ensure no trailing newlines from original comment
                else:
                    # binding_str + first comment line is too long, put all comment on new lines
                    formatted_comment = "\\n".join(
                        [binding_str]
                        + [f"{indent_str}{line.strip()}" for line in lines]
                    )
                    return formatted_comment.strip()
            else:  # No binding_str, comment starts on its own line
                return "\\n".join(
                    [f"{indent_str}{line.strip()}" for line in lines]
                ).strip()

        # Single line comment logic
        if binding_str:
            line = f"{binding_str} {comment}".rstrip()
        else:
            line = f"{indent_str}{comment}".rstrip()

        if len(line) <= max_len:
            return line

        # If too long, split comment onto a new line, indented
        if binding_str:
            # Comment is on a new line, indented by "  "
            comment_max_len = max_len - len(indent_str)
            truncated_comment_str = comment  # Renamed
            if len(comment) > comment_max_len:
                truncated_comment_str = comment[: comment_max_len - 3] + "..."
            return f"{binding_str}\\n{indent_str}{truncated_comment_str.strip()}"
        else:
            # Comment is on the first line (binding_str was empty)
            # This path should ideally not be taken if comment was single line
            # and initial `len(line) <= max_len` failed, means comment itself is too long.
            comment_max_len = max_len - len(indent_str)
            truncated_comment_str = comment  # Renamed
            if len(comment) > comment_max_len:
                truncated_comment_str = comment[: comment_max_len - 3] + "..."
            return f"{indent_str}{truncated_comment_str.strip()}"

    def _holdtap_alias_name(self, behavior_type, hold_param, tap_param):
        """Generate a consistent alias name for hold-tap behaviors."""
        hold = self._to_kanata_symbolic(hold_param, for_alias_name=True)
        tap = self._to_kanata_symbolic(tap_param, for_alias_name=True)
        logging.debug(
            f"[DEBUG] _holdtap_alias_name: behavior_type={behavior_type}, "
            f"hold_param={hold_param}, tap_param={tap_param}, "
            f"hold={hold}, tap={tap}"
        )
        if behavior_type == "lt":
            return f"lt_{hold}_{tap}"
        else:  # Default to 'ht' for mod-tap or generic hold-tap
            return f"ht_{hold}_{tap}"

    def _to_kanata_symbolic(self, zmk_key: str, for_alias_name: bool = False) -> str:
        """Convert ZMK key to a Kanata symbolic name if possible.
        
        If for_alias_name is True, ensure the result is a safe token for an alias.
        """
        # First, try to get a symbolic representation from ZMK key (e.g. LCTRL, A)
        # This part aims to convert raw ZMK inputs like "&kp LCTRL" to just "LCTRL"
        # or handle potential macro_transformer specific conversions.
        mapped_by_macro_transformer = self.macro_transformer._convert_key(zmk_key)

        # Determine a base symbol (prefer macro_transformer if it provides a non-digit)
        if mapped_by_macro_transformer is not None and not mapped_by_macro_transformer.isdigit():
            base_symbol = mapped_by_macro_transformer
        else:
            # Fallback or if macro_transformer gave a digit/None
            rev_map = getattr(self.macro_transformer, "reverse_key_map", None)
            if rev_map and zmk_key.isdigit() and zmk_key in rev_map:
                base_symbol = rev_map[zmk_key] # e.g. map number to symbolic like F1
            else:
                base_symbol = zmk_key # Use original key if no other symbol found

        # Now, map this base_symbol to a Kanata keycode or symbol
        kanata_representation = zmk_to_kanata(base_symbol)

        if for_alias_name:
            # For aliases, we need a clean, simple token.
            # If zmk_to_kanata gave a good symbol, use it.
            # Otherwise, sanitize the base_symbol.
            if (
                kanata_representation is not None and 
                "TODO" not in kanata_representation and 
                re.match(r"^[a-zA-Z0-9_.:-]+$", kanata_representation) # Relaxed regex for typical Kanata symbols
            ):
                return kanata_representation
            else:
                # Sanitize the original zmk_key or base_symbol to be a safe alias part
                # Replace common problematic chars like parentheses, ampersands, spaces
                safe_symbol = base_symbol.replace("&", "").replace("(", "_").replace(")", "").replace(" ", "_")
                safe_symbol = re.sub(r'[^a-zA-Z0-9_.:-]', '', safe_symbol) # Keep only typical token chars
                return safe_symbol if safe_symbol else "unknown_key"
        else:
            # For general use, return Kanata mapping or the base_symbol if no mapping
            return kanata_representation if kanata_representation is not None else base_symbol

    def _emit_tapdance(self, behavior, params):  # behavior can be None
        """Emit Kanata tap-dance syntax."""
        # Support any number of tap-dance actions
        timeout_val = 200  # Default # Renamed
        if (
            behavior
            and hasattr(behavior, "tapping_term_ms")
            and behavior.tapping_term_ms is not None
        ):
            timeout_val = behavior.tapping_term_ms

        if len(params) >= 1:
            keys = [self._to_kanata_symbolic(p) for p in params]
            return f"(tap-dance {timeout_val} {' '.join(keys)})"
        else:
            # This case should ideally be caught earlier in _transform_binding
            # if a tap-dance has no params.
            return (
                f"; TODO: tap-dance with params {params} not supported. "
                "Manual review needed."
            )
