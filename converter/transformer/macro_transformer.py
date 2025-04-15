"""Macro Transformer Module

This module provides functionality for transforming ZMK macro behaviors to
Kanata format.
"""

from typing import Dict, List, Optional
import logging
import re

from converter.behaviors.macro import (
    MacroBehavior,
    MacroActivationMode
)
from converter.error_handling.error_manager import get_error_manager, ErrorSeverity
from converter.parser.macro_parser_new import MacroDefinition, MacroUsage

# Define constants for macro commands
MACRO_TAP = "&macro_tap"
MACRO_PRESS = "&macro_press"
MACRO_RELEASE = "&macro_release"
MACRO_WAIT_TIME = "&macro_wait_time"
MACRO_TAP_TIME = "&macro_tap_time"


class MacroTransformer:
    """
    Transformer for ZMK macro behaviors to Kanata format.

    Output format matches Kanata S-expression macros:
      - Macro definition: (defmacro name step1 step2 ...)
      - Macro usage: (macro name)
      - Supports timing/delay steps: (delay 30), (tap-hold-ms 200)
      - Supports press/release groups if present in the input
    """

    def __init__(self):
        """Initialize the transformer."""
        # No local errors/warnings; use centralized error manager
        self.key_map: Dict[str, str] = {
            # Letters
            'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e',
            'F': 'f', 'G': 'g', 'H': 'h', 'I': 'i', 'J': 'j',
            'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'O': 'o',
            'P': 'p', 'Q': 'q', 'R': 'r', 'S': 's', 'T': 't',
            'U': 'u', 'V': 'v', 'W': 'w', 'X': 'x', 'Y': 'y',
            'Z': 'z',

            # Numbers
            'N0': '0', 'N1': '1', 'N2': '2', 'N3': '3', 'N4': '4',
            'N5': '5', 'N6': '6', 'N7': '7', 'N8': '8', 'N9': '9',

            # Function keys
            'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4',
            'F5': 'f5', 'F6': 'f6', 'F7': 'f7', 'F8': 'f8',
            'F9': 'f9', 'F10': 'f10', 'F11': 'f11', 'F12': 'f12',

            # Navigation
            'LEFT': 'left', 'RIGHT': 'right', 'UP': 'up', 'DOWN': 'down',
            'HOME': 'home', 'END': 'end', 'PG_UP': 'pg_up', 'PG_DN': 'pg_dn',

            # Editing
            'ENTER': 'ret', 'RET': 'ret', 'ESC': 'esc', 'BSPC': 'bspc',
            'DEL': 'del', 'TAB': 'tab', 'SPACE': 'spc', 'SPC': 'spc',
            'CAPS': 'caps',

            # Modifiers
            'LSHIFT': 'lsft', 'RSHIFT': 'rsft',
            'LCTRL': 'lctl', 'RCTRL': 'rctl',
            'LALT': 'lalt', 'RALT': 'ralt',
            'LGUI': 'lmet', 'RGUI': 'rmet',

            # Punctuation
            'GRAVE': 'grv', 'MINUS': 'minus', 'EQUAL': 'equal',
            'LBKT': 'lbrc', 'RBKT': 'rbrc', 'BSLH': 'bslh',
            'SEMI': 'semi', 'APOS': 'apos', 'COMMA': 'comma',
            'DOT': 'dot', 'FSLH': 'fslh',
        }

    def _validate_timing(self, value: Optional[int], name: str) -> None:
        """Validate a timing value."""
        if value is not None:
            if not isinstance(value, int):
                msg = f"{name} value must be an integer"
                get_error_manager().add_error(
                    message=msg,
                    source="macro_transformer",
                    severity=ErrorSeverity.ERROR
                )
                raise ValueError(msg)
            if value < 0:
                msg = f"Negative {name} value: {value}"
                get_error_manager().add_error(
                    message=msg,
                    source="macro_transformer",
                    severity=ErrorSeverity.ERROR
                )
                raise ValueError(msg)
            if value == 0:
                 # Allow zero for potentially disabling a default? Needs clarification.
                 pass
            # Add reasonable upper bound check? e.g., 60000ms
            # if value > 60000:
            #     raise ValueError(f"{name} value too large: {value}")

    def _parse_macro_step(self, step: str) -> str:
        """Parse a single step in a ZMK macro binding list."""
        if step.startswith(MACRO_WAIT_TIME):
            try:
                value = int(step.split()[-1])
                self._validate_timing(value, "wait-time")
                return f"(delay {value})"
            except (IndexError, ValueError) as e:
                msg = f"Invalid wait-time format: {step}"
                get_error_manager().add_error(
                    message=msg,
                    source="macro_transformer",
                    severity=ErrorSeverity.ERROR
                )
                return f"<unknown:{step}>"
        elif step.startswith(MACRO_TAP_TIME):
            try:
                value = int(step.split()[-1])
                self._validate_timing(value, "tap-time")
                return f"(tap-hold-ms {value})" # Kanata uses tap-hold-ms for tap time
            except (IndexError, ValueError) as e:
                msg = f"Invalid tap-time format: {step}"
                get_error_manager().add_error(
                    message=msg,
                    source="macro_transformer",
                    severity=ErrorSeverity.ERROR
                )
                return f"<unknown:{step}>"
        elif step == MACRO_PRESS:
            return "press"
        elif step == MACRO_RELEASE:
            return "release"
        elif step.startswith("&kp"):
            key = step.split()[-1].lower()
            # Basic key mapping (needs enhancement for modifiers, etc.)
            key_map = {
                "lshift": "lsft", "rshift": "rsft",
                "lctrl": "lctl", "rctrl": "rctl",
                "lalt": "lalt", "ralt": "ralt",
                "lgui": "lmet", "rgui": "rmet"
            }
            return key_map.get(key, key)
        else:
            msg = f"Unknown macro step: {step}"
            get_error_manager().add_error(
                message=msg,
                source="macro_transformer",
                severity=ErrorSeverity.WARNING
            )
            return f"<unknown:{step}>"

    def transform_behavior(self, behavior):
        """
        Deprecated. Use transform_definition(MacroDefinition) instead.
        """
        raise NotImplementedError(
            "transform_behavior is deprecated. Use transform_definition(MacroDefinition) instead."
        )

    def transform_binding(self, usage):
        """
        Deprecated. Use transform_usage(MacroUsage) instead.
        """
        raise NotImplementedError(
            "transform_binding is deprecated. Use transform_usage(MacroUsage) instead."
        )

    def _convert_key(self, key: str) -> str:
        """Convert a ZMK key name to its Kanata equivalent.

        Args:
            key: The ZMK key name

        Returns:
            The Kanata key name
        """
        return self.key_map.get(key, key.lower())

    def report_issues(self):
        """
        Print a grouped summary of all errors and warnings collected during macro transformation.
        Each entry includes context (message, macro name, etc.).
        """
        error_mgr = get_error_manager()
        errors = error_mgr.get_errors()
        if not errors:
            print("No errors or warnings.")
            return
        print("\nERRORS AND WARNINGS:")
        for err in errors:
            print(f"  - {err}")
        print()

    def transform_definition(self, macro_def: MacroDefinition) -> str:
        """
        Transform a MacroDefinition object to Kanata format.
        Args:
            macro_def: The MacroDefinition to transform
        Returns:
            The Kanata macro definition string
        """
        logger = logging.getLogger(__name__)
        kanata_steps = []
        for step in macro_def.steps:
            # Each step is a MacroStep with command and params
            if step.command == 'kp' and step.params:
                key = step.params[0].lower()
                kanata_steps.append(self.key_map.get(key, key))
            elif step.command == 'macro_wait_time' and step.params:
                try:
                    value = int(step.params[0])
                    self._validate_timing(value, "wait-time")
                    kanata_steps.append(f"(delay {value})")
                except Exception as e:
                    msg = f"Invalid wait-time in macro {macro_def.name}: {step.params}"
                    get_error_manager().add_error(
                        message=msg,
                        source="macro_transformer",
                        severity=ErrorSeverity.ERROR
                    )
            elif step.command == 'macro_tap_time' and step.params:
                try:
                    value = int(step.params[0])
                    self._validate_timing(value, "tap-time")
                    kanata_steps.append(f"(tap-hold-ms {value})")
                except Exception as e:
                    msg = f"Invalid tap-time in macro {macro_def.name}: {step.params}"
                    get_error_manager().add_error(
                        message=msg,
                        source="macro_transformer",
                        severity=ErrorSeverity.ERROR
                    )
            elif step.command == 'macro_press':
                kanata_steps.append("press")
            elif step.command == 'macro_release':
                kanata_steps.append("release")
            else:
                msg = f"Unknown macro step in {macro_def.name}: {step.command} {step.params}"
                get_error_manager().add_error(
                    message=msg,
                    source="macro_transformer",
                    severity=ErrorSeverity.WARNING
                )
                kanata_steps.append(f"<unknown:{step.command}>")
        macro_str = f"(defmacro {macro_def.name} {' '.join(kanata_steps)})"
        # Output validation
        if not (macro_str.startswith("(defmacro ") and macro_str.endswith(")")):
            msg = f"Macro output does not match expected format: {macro_str}"
            logger.warning(msg)
            get_error_manager().add_error(
                message=msg,
                source="macro_transformer",
                severity=ErrorSeverity.WARNING
            )
        else:
            logger.debug(f"Macro transformed successfully: {macro_str}")
        return macro_str

    def transform_usage(self, usage: MacroUsage) -> str:
        """
        Transform a MacroUsage object to Kanata macro usage format.
        Args:
            usage: The MacroUsage to transform
        Returns:
            The Kanata macro usage string
        """
        if not usage.name:
            msg = "Macro usage missing macro name"
            get_error_manager().add_error(
                message=msg,
                source="macro_transformer",
                severity=ErrorSeverity.ERROR
            )
            return "(macro <invalid>)"
        # If parameters are present, include them in the usage
        if usage.params:
            params_str = ' '.join(usage.params)
            return f"(macro {usage.name} {params_str})"
        else:
            return f"(macro {usage.name})"
