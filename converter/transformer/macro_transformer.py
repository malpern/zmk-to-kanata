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
        # Reverse mapping from numeric codes to ZMK symbolic names
        self.reverse_key_map: Dict[str, str] = {
            # Letters
            "0x04": "A",
            "4": "A",
            "0x05": "B",
            "5": "B",
            "0x06": "C",
            "6": "C",
            "0x07": "D",
            "7": "D",
            "0x08": "E",
            "8": "E",
            "0x09": "F",
            "9": "F",
            "0x0A": "G",
            "10": "G",
            "0x0B": "H",
            "11": "H",
            "0x0C": "I",
            "12": "I",
            "0x0D": "J",
            "13": "J",
            "0x0E": "K",
            "14": "K",
            "0x0F": "L",
            "15": "L",
            "0x10": "M",
            "16": "M",
            "0x11": "N",
            "17": "N",
            "0x12": "O",
            "18": "O",
            "0x13": "P",
            "19": "P",
            "0x14": "Q",
            "20": "Q",
            "0x15": "R",
            "21": "R",
            "0x16": "S",
            "22": "S",
            "0x17": "T",
            "23": "T",
            "0x18": "U",
            "24": "U",
            "0x19": "V",
            "25": "V",
            "0x1A": "W",
            "26": "W",
            "0x1B": "X",
            "27": "X",
            "0x1C": "Y",
            "28": "Y",
            "0x1D": "Z",
            "29": "Z",
            # Numbers (row)
            "0x1E": "N1",
            "30": "N1",
            "0x1F": "N2",
            "31": "N2",
            "0x20": "N3",
            "32": "N3",
            "0x21": "N4",
            "33": "N4",
            "0x22": "N5",
            "34": "N5",
            "0x23": "N6",
            "35": "N6",
            "0x24": "N7",
            "36": "N7",
            "0x25": "N8",
            "37": "N8",
            "0x26": "N9",
            "38": "N9",
            "0x27": "N0",
            "39": "N0",
            # Modifiers
            "0xE0": "LCTRL",
            "224": "LCTRL",
            "0xE1": "LSHIFT",
            "225": "LSHIFT",
            "0xE2": "LALT",
            "226": "LALT",
            "0xE3": "LGUI",
            "227": "LGUI",
            "0xE4": "RCTRL",
            "228": "RCTRL",
            "0xE5": "RSHIFT",
            "229": "RSHIFT",
            "0xE6": "RALT",
            "230": "RALT",
            "0xE7": "RGUI",
            "231": "RGUI",
            # Function keys
            "0x3A": "F1",
            "58": "F1",
            "0x3B": "F2",
            "59": "F2",
            "0x3C": "F3",
            "60": "F3",
            "0x3D": "F4",
            "61": "F4",
            "0x3E": "F5",
            "62": "F5",
            "0x3F": "F6",
            "63": "F6",
            "0x40": "F7",
            "64": "F7",
            "0x41": "F8",
            "65": "F8",
            "0x42": "F9",
            "66": "F9",
            "0x43": "F10",
            "67": "F10",
            "0x44": "F11",
            "68": "F11",
            "0x45": "F12",
            "69": "F12",
            # Other keys
            "0x28": "ENTER",
            "40": "ENTER",
            "0x29": "ESC",
            "41": "ESC",
            "0x2A": "BSPC",
            "42": "BSPC",
            "0x2B": "TAB",
            "43": "TAB",
            "0x2C": "SPC",
            "44": "SPC",
            "0x2D": "MINUS",
            "45": "MINUS",
            "0x2E": "EQUAL",
            "46": "EQUAL",
            "0x2F": "LBKT",
            "47": "LBKT",
            "0x30": "RBKT",
            "48": "RBKT",
            "0x31": "BSLH",
            "49": "BSLH",
            "0x33": "SEMI",
            "51": "SEMI",
            "0x34": "APOS",
            "52": "APOS",
            "0x35": "GRAVE",
            "53": "GRAVE",
            "0x36": "COMMA",
            "54": "COMMA",
            "0x37": "DOT",
            "55": "DOT",
            "0x38": "SLASH",
            "56": "SLASH",
            "0x39": "CAPS",
            "57": "CAPS",
            # Navigation
            "0x4A": "HOME",
            "74": "HOME",
            "0x4B": "PG_UP",
            "75": "PG_UP",
            "0x4C": "DELETE",
            "76": "DELETE",
            "0x4D": "END",
            "77": "END",
            "0x4E": "PG_DN",
            "78": "PG_DN",
            "0x4F": "RIGHT",
            "79": "RIGHT",
            "0x50": "LEFT",
            "80": "LEFT",
            "0x51": "DOWN",
            "81": "DOWN",
            "0x52": "UP",
            "82": "UP",
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
        """Convert a ZMK key name or code to Kanata key name."""
        # Try symbolic name first
        if zmk_key in self.key_map:
            return self.key_map[zmk_key]
        # Try reverse mapping if input is a numeric code
        if zmk_key in self.reverse_key_map:
            symbolic = self.reverse_key_map[zmk_key]
            return self.key_map.get(symbolic, symbolic.lower())
        # Fallback: lowercase
        return zmk_key.lower()
