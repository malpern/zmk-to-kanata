"""Macro Transformer Module

This module provides functionality for transforming ZMK macro behaviors to 
Kanata format.
"""

from typing import Dict

from converter.behaviors.macro import (
    MacroBehavior,
    MacroActivationMode
)


class MacroTransformer:
    """Transformer for ZMK macro behaviors to Kanata format."""

    def __init__(self):
        """Initialize the transformer."""
        # Mapping of ZMK key names to Kanata key names
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

    def transform_behavior(self, behavior: MacroBehavior) -> str:
        """Transform a ZMK macro behavior to Kanata format.

        Args:
            behavior: The ZMK macro behavior to transform.

        Returns:
            The Kanata macro definition string.
        """
        lines = [f"(defsrc {behavior.name})"]
        
        # Add the macro bindings
        binding_lines = []
        for binding in behavior.bindings:
            binding_str = binding.to_kanata()
            if binding_str:
                binding_lines.append(binding_str)
        
        if binding_lines:
            lines.append(f"(deflayer {behavior.name}")
            lines.append("  " + " ".join(binding_lines))
            lines.append(")")
        
        return "\n".join(lines)

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
            
            # Handle mode changes
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
            
            # Handle wait times
            elif binding.startswith("&macro_wait_time "):
                wait_time = binding.split(" ")[1]
                macro_def += f"  delay {wait_time}\n"
                i += 1
                continue
            
            # Extract the key from the binding string
            if binding.startswith("&kp "):
                key = binding[4:]
                kanata_key = self._convert_key(key)
                
                # Special case for the first key after &macro_press
                # In ZMK, this is the modifier key that should be pressed
                if current_mode == MacroActivationMode.PRESS and key in [
                    "LSHIFT", "RSHIFT", "LCTRL", "RCTRL", 
                    "LALT", "RALT", "LGUI", "RGUI"
                ]:
                    pressed_keys.add(kanata_key)
                    macro_def += f"  press {kanata_key}\n"
                # For other keys in PRESS mode, we tap them
                elif current_mode == MacroActivationMode.PRESS:
                    macro_def += f"  tap {kanata_key}\n"
                elif current_mode == MacroActivationMode.TAP:
                    macro_def += f"  tap {kanata_key}\n"
                elif current_mode == MacroActivationMode.RELEASE:
                    if kanata_key in pressed_keys:
                        pressed_keys.remove(kanata_key)
                    macro_def += f"  release {kanata_key}\n"
            
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