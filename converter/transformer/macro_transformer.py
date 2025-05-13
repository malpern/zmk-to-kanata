"""Macro Transformer Module.

This module provides functionality for transforming ZMK macro behaviors to
Kanata format.
"""

from typing import Dict

from converter.behaviors.macro import MacroActivationMode, MacroBehavior
from converter.error_handling.error_manager import (
    get_error_manager,
)


class MacroTransformer:
    """Transforms ZMK macro behaviors to Kanata format."""

    def __init__(self):
        """Initialize the macro transformer."""
        self.error_manager = get_error_manager()
        # Mapping of ZMK key names to Kanata key names
        self.key_map: Dict[str, str] = {
            # Letters
            "A": "a",
            "B": "b",
            "C": "c",
            "D": "d",
            "E": "e",
            "F": "f",
            "G": "g",
            "H": "h",
            "I": "i",
            "J": "j",
            "K": "k",
            "L": "l",
            "M": "m",
            "N": "n",
            "O": "o",
            "P": "p",
            "Q": "q",
            "R": "r",
            "S": "s",
            "T": "t",
            "U": "u",
            "V": "v",
            "W": "w",
            "X": "x",
            "Y": "y",
            "Z": "z",
            # Numbers
            "N0": "0",
            "N1": "1",
            "N2": "2",
            "N3": "3",
            "N4": "4",
            "N5": "5",
            "N6": "6",
            "N7": "7",
            "N8": "8",
            "N9": "9",
            # Function keys
            "F1": "f1",
            "F2": "f2",
            "F3": "f3",
            "F4": "f4",
            "F5": "f5",
            "F6": "f6",
            "F7": "f7",
            "F8": "f8",
            "F9": "f9",
            "F10": "f10",
            "F11": "f11",
            "F12": "f12",
            # Navigation
            "LEFT": "left",
            "RIGHT": "right",
            "UP": "up",
            "DOWN": "down",
            "HOME": "home",
            "END": "end",
            "PG_UP": "pg_up",
            "PG_DN": "pg_dn",
            # Editing
            "ENTER": "ret",
            "RET": "ret",
            "ESC": "esc",
            "BSPC": "bspc",
            "DEL": "del",
            "TAB": "tab",
            "SPACE": "spc",
            "SPC": "spc",
            "CAPS": "caps",
            # Modifiers
            "LSHIFT": "lsft",
            "RSHIFT": "rsft",
            "LCTRL": "lctl",
            "RCTRL": "rctl",
            "LALT": "lalt",
            "RALT": "ralt",
            "LGUI": "lmet",
            "RGUI": "rmet",
            # Punctuation
            "GRAVE": "grv",
            "MINUS": "minus",
            "EQUAL": "equal",
            "LBKT": "lbrc",
            "RBKT": "rbrc",
            "BSLH": "bslh",
            "SEMI": "semi",
            "APOS": "apos",
            "COMMA": "comma",
            "DOT": "dot",
            "FSLH": "fslh",
        }

    def transform_macro(self, behavior: MacroBehavior) -> str:
        """Transform a ZMK macro behavior to Kanata format.

        Args:
            behavior: The ZMK macro behavior to transform

        Returns:
            String containing the Kanata macro definition
        """
        # Start building the macro definition
        macro_def = f"(defmacro {behavior.name}\n"

        # Process each binding in the macro
        current_mode = MacroActivationMode.TAP
        pressed_keys = set()

        i = 0
        while i < len(behavior.bindings):
            binding = behavior.bindings[i]

            # Handle macro control actions
            if isinstance(binding, str):
                if binding == "&macro_tap":
                    current_mode = MacroActivationMode.TAP
                    i += 1
                    continue
                elif binding == "&macro_press":
                    current_mode = MacroActivationMode.PRESS
                    i += 1
                    continue
                elif binding == "&macro_release":
                    current_mode = MacroActivationMode.RELEASE
                    i += 1
                    continue
                elif binding.startswith("&macro_wait_time "):
                    # Extract wait time
                    wait_time = binding.split(" ", 1)[1]
                    macro_def += f"  (wait {wait_time})\n"
                    i += 1
                    continue
                # Extract the key from the binding string
                if binding.startswith("&kp "):
                    key = binding.split(" ", 1)[1]
                    macro_def += f"  ({current_mode.value} {key})\n"
                    i += 1
                    continue
            elif hasattr(binding, "behavior") and binding.behavior:
                bname = binding.behavior.name
                if bname == "macro_tap":
                    current_mode = MacroActivationMode.TAP
                    i += 1
                    continue
                elif bname == "macro_press":
                    current_mode = MacroActivationMode.PRESS
                    i += 1
                    continue
                elif bname == "macro_release":
                    current_mode = MacroActivationMode.RELEASE
                    i += 1
                    continue
                elif bname == "macro_wait_time":
                    # Wait time is in params[0]
                    if binding.params and len(binding.params) > 0:
                        wait_time = binding.params[0]
                        macro_def += f"  (wait {wait_time})\n"
                    i += 1
                    continue
                elif bname == "kp":
                    # Key press
                    if binding.params and len(binding.params) > 0:
                        key = binding.params[0]
                        macro_def += f"  ({current_mode.value} {key})\n"
                    i += 1
                    continue
            # If binding is not recognized, skip
            i += 1

        # Make sure all pressed keys are released at the end of the macro
        # Only if they haven't been explicitly released
        for key in pressed_keys:
            macro_def += f"  release {key}\n"

        # Close the macro definition
        macro_def += ")"

        return macro_def

    def _convert_key(self, zmk_key: str) -> str:
        """Convert a ZMK key name to Kanata key name.

        Args:
            zmk_key: The ZMK key name

        Returns:
            The corresponding Kanata key name
        """
        return self.key_map.get(zmk_key, zmk_key.lower())
