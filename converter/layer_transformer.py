"""Module for transforming ZMK layers to Kanata format."""

from typing import Dict, List

from converter.behaviors.key_sequence import KeySequenceBinding
from converter.model.keymap_model import Binding, KeyMapping, Layer


class KanataLayer:
    """Represents a layer in Kanata format."""

    def __init__(self, name: str, keys: List[List[str]]):
        """Initialize a Kanata layer.

        Args:
            name: The name of the layer
            keys: A 2D list of key bindings in Kanata format
        """
        self.name = name
        self.keys = keys
        # Add bindings attribute for compatibility with new architecture
        self.bindings = []
        for row in keys:
            self.bindings.extend(row)


class LayerTransformer:
    """Transformer for ZMK layers to Kanata format."""

    def __init__(self):
        """Initialize the transformer."""
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
            # Symbols
            "EXCL": "excl",
            "AT": "at",
            "HASH": "hash",
            "DLLR": "dollar",
            "PRCNT": "percent",
            "CARET": "caret",
            "AMPS": "amp",
            "STAR": "astrk",
            "LPAR": "lpar",
            "RPAR": "rpar",
            "UNDER": "under",
            "PLUS": "plus",
            "PIPE": "pipe",
            "TILDE": "tilde",
            # Numpad
            "KP_N0": "kp0",
            "KP_N1": "kp1",
            "KP_N2": "kp2",
            "KP_N3": "kp3",
            "KP_N4": "kp4",
            "KP_N5": "kp5",
            "KP_N6": "kp6",
            "KP_N7": "kp7",
            "KP_N8": "kp8",
            "KP_N9": "kp9",
            "KP_DOT": "kp_dot",
            "KP_PLUS": "kp_plus",
            "KP_MINUS": "kp_minus",
            "KP_MULTIPLY": "kp_multiply",
            "KP_DIVIDE": "kp_divide",
            "KP_ENTER": "kp_enter",
            # Media
            "C_MUTE": "c_mute",
            "C_VOL_UP": "c_vol_up",
            "C_VOL_DN": "c_vol_dn",
            "C_PP": "c_pp",
            "C_NEXT": "c_next",
            "C_PREV": "c_prev",
            # Special
            "PSCRN": "prnt",
            "SLCK": "slck",
            "PAUSE": "pause",
            "INS": "ins",
            "MENU": "menu",
        }

    def transform_binding(self, binding: Binding) -> str:
        """Transform a binding to Kanata format.

        Args:
            binding: The binding to transform

        Returns:
            The binding in Kanata format
        """
        # Handle transparent key
        if isinstance(binding, str) and binding == "trans":
            return "_"

        # Handle key sequence bindings
        if isinstance(binding, KeySequenceBinding):
            # Convert each key in the sequence
            kanata_keys = []
            for key in binding.keys:
                # Look up the key in the key map
                kanata_key = self.key_map.get(key, key.lower())
                kanata_keys.append(kanata_key)

            # Format as a chord
            return f"(chord {' '.join(kanata_keys)})"

        # Handle sticky key bindings
        from converter.behaviors.sticky_key import StickyKeyBinding

        if isinstance(binding, StickyKeyBinding):
            # Get the modifier key from the binding
            mod_key = binding.key.upper()
            # Map to shorter form if needed
            mod_map = {
                "LSHIFT": "lsft",
                "RSHIFT": "rsft",
                "LCTRL": "lctl",
                "RCTRL": "rctl",
                "LALT": "lalt",
                "RALT": "ralt",
                "LGUI": "lmet",
                "RGUI": "rmet",
            }
            mod_short = mod_map.get(mod_key, mod_key.lower())
            return f"sticky-{mod_short}"

        # Handle regular key mappings
        if isinstance(binding, KeyMapping):
            # Special case for layer switching
            if binding.key.startswith("mo "):
                layer_num = binding.key.split()[1]
                return f"@layer{layer_num}"
            return binding.to_kanata()

        # Handle any binding with to_kanata()
        if hasattr(binding, "to_kanata") and callable(binding.to_kanata):
            try:
                return binding.to_kanata()
            except Exception as e:
                print(f"[DEBUG] Exception in to_kanata: {e}")
                pass

        # Default case
        return str(binding)

    def transform_bindings_matrix(self, matrix: List[List[Binding]]) -> List[List[str]]:
        """Transform a matrix of bindings to Kanata format.

        Args:
            matrix: A 2D list of bindings

        Returns:
            A 2D list of strings in Kanata format
        """
        result = []
        for row in matrix:
            kanata_row = []
            for binding in row:
                kanata_row.append(self.transform_binding(binding))
            result.append(kanata_row)
        return result

    def transform_layer(self, layer: Layer) -> str:
        """Transform a ZMK layer to Kanata format.

        Args:
            layer: The ZMK layer to transform

        Returns:
            A string representing the layer in Kanata format
        """
        # Convert bindings to Kanata format
        kanata_bindings = []
        for row in layer.keys:
            for binding in row:
                kanata_bindings.append(self.transform_binding(binding))

        # For simplicity, we're putting all keys in a single row
        # In a real implementation, we would respect the original layout
        keys = [kanata_bindings]

        # Create a KanataLayer for backward compatibility
        kanata_layer = KanataLayer(layer.name, keys)

        # Format as a string
        result = f"(deflayer {layer.name}\n"
        for row in kanata_layer.keys:
            result += "  " + " ".join(row) + "\n"
        result += ")"

        return result

    def transform_layers(self, zmk_layers: List[Layer]) -> str:
        """Transform ZMK layers to Kanata format.

        Args:
            zmk_layers: List of ZMK Layer objects

        Returns:
            String containing the complete Kanata keymap configuration
        """
        # Define the source keys
        source_keys = self._get_source_keys()

        # Transform each layer
        kanata_layers = []
        for layer in zmk_layers:
            kanata_layers.append(self.transform_layer(layer))

        # Combine everything
        kanata_content = f"(defsrc\n  {source_keys}\n)\n\n"

        # Add each layer definition - kanata_layers now contains strings, not KanataLayer objects
        for layer_str in kanata_layers:
            kanata_content += layer_str + "\n\n"

        return kanata_content.rstrip()

    def _get_source_keys(self) -> str:
        """Get the source keys for the Kanata keymap."""
        # This is a simplified version; in a real implementation,
        # we would derive this from the actual keyboard layout
        return "a b c d e f g h i j k l m n o p q r s t u v w x y z"
