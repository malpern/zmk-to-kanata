"""Module for transforming ZMK layer bindings into Kanata format."""

from dataclasses import dataclass
from typing import Dict, List

from .layer_parser import Layer
from converter.model.keymap_model import KeyMapping
from .behaviors.sticky_key import StickyKeyBinding
from .behaviors.key_sequence import KeySequenceBinding


@dataclass
class KanataLayer:
    """Represents a layer in Kanata format."""
    name: str
    keys: List[List[str]]  # Matrix of key bindings


class LayerTransformer:
    """Transforms ZMK layers into Kanata format."""
    
    def __init__(self):
        """Initialize the transformer with ZMK to Kanata mapping."""
        # Basic key mapping from ZMK to Kanata
        self.key_map: Dict[str, str] = {
            # Letters
            "A": "a", "B": "b", "C": "c", "D": "d", "E": "e",
            "F": "f", "G": "g", "H": "h", "I": "i", "J": "j",
            "K": "k", "L": "l", "M": "m", "N": "n", "O": "o",
            "P": "p", "Q": "q", "R": "r", "S": "s", "T": "t",
            "U": "u", "V": "v", "W": "w", "X": "x", "Y": "y",
            "Z": "z",
            
            # Numbers (both number row and numpad)
            "N0": "0", "N1": "1", "N2": "2", "N3": "3", "N4": "4",
            "N5": "5", "N6": "6", "N7": "7", "N8": "8", "N9": "9",
            "KP_N0": "kp0", "KP_N1": "kp1", "KP_N2": "kp2", "KP_N3": "kp3",
            "KP_N4": "kp4", "KP_N5": "kp5", "KP_N6": "kp6", "KP_N7": "kp7",
            "KP_N8": "kp8", "KP_N9": "kp9",
            
            # Symbols and Punctuation
            "EXCL": "excl",           # !
            "AT": "at",               # @
            "HASH": "hash",           # #
            "DLLR": "dollar",         # $
            "PRCNT": "percent",       # %
            "CARET": "caret",         # ^
            "AMPS": "amp",            # &
            "STAR": "asterisk",       # *
            "LPAR": "lpar",           # (
            "RPAR": "rpar",           # )
            "MINUS": "minus",         # -
            "UNDER": "underscore",    # _
            "PLUS": "plus",           # +
            "EQUAL": "equal",         # =
            "LBRC": "lbrc",           # {
            "RBRC": "rbrc",           # }
            "LBKT": "lbkt",           # [
            "RBKT": "rbkt",           # ]
            "PIPE": "pipe",           # |
            "BSLH": "bslh",           # \
            "COLON": "colon",         # :
            "SEMI": "semi",           # ;
            "DQT": "dqt",             # "
            "SQT": "sqt",             # '
            "LT": "lt",               # <
            "GT": "gt",               # >
            "COMMA": "comma",         # ,
            "DOT": "dot",             # .
            "FSLH": "fslh",           # /
            "QMARK": "qmark",         # ?
            "GRAVE": "grave",         # `
            "TILDE": "tilde",         # ~
            
            # Function keys
            "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
            "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8",
            "F9": "f9", "F10": "f10", "F11": "f11", "F12": "f12",
            
            # Navigation and editing
            "ENTER": "enter",
            "SPACE": "space",
            "TAB": "tab",
            "ESC": "esc",
            "BSPC": "bspc",
            "DEL": "del",
            "INS": "ins",
            "HOME": "home",
            "END": "end",
            "PG_UP": "pg_up",
            "PG_DN": "pg_dn",
            "LEFT": "left",
            "RIGHT": "right",
            "UP": "up",
            "DOWN": "down",
            
            # Modifiers
            "LSHIFT": "lshift",
            "RSHIFT": "rshift",
            "LCTRL": "lctrl",
            "RCTRL": "rctrl",
            "LALT": "lalt",
            "RALT": "ralt",
            "LGUI": "lgui",
            "RGUI": "rgui",
            
            # System and media keys
            "CAPS": "caps",
            "PSCRN": "pscrn",
            "SLCK": "slck",
            "PAUSE_BREAK": "pause",
            "C_MUTE": "c_mute",
            "C_VOL_UP": "c_vol_up",
            "C_VOL_DN": "c_vol_dn",
            "C_PP": "c_pp",
            "C_NEXT": "c_next",
            "C_PREV": "c_prev",
            
            # Numpad special keys
            "KP_PLUS": "kp_plus",
            "KP_MINUS": "kp_minus",
            "KP_MULTIPLY": "kp_multiply",
            "KP_DIVIDE": "kp_divide",
            "KP_ENTER": "kp_enter",
            "KP_DOT": "kp_dot",
            "KP_EQUAL": "kp_equal",
            
            # International characters
            "NON_US_HASH": "non_us_hash",
            "NON_US_BSLH": "non_us_bslh",
        }
    
    def transform_binding(self, key_mapping: KeyMapping) -> str:
        """Transform a ZMK key binding into Kanata format.
        
        Args:
            key_mapping: KeyMapping object to transform
            
        Returns:
            Kanata key binding string
        """
        # Handle sticky key binding
        if isinstance(key_mapping, StickyKeyBinding):
            return key_mapping.to_kanata()
            
        # Handle key sequence binding
        if isinstance(key_mapping, KeySequenceBinding):
            return key_mapping.to_kanata()
            
        # Handle hold-tap binding
        if key_mapping.hold_tap:
            hold_key = key_mapping.hold_tap.hold_key
            tap_key = key_mapping.hold_tap.tap_key
            
            # Transform the keys using the key map
            hold_key = self.key_map.get(hold_key) or hold_key.lower()
            tap_key = self.key_map.get(tap_key) or tap_key.lower()
            
            return f"tap-hold {hold_key} {tap_key}"
        
        # Handle sticky key format from parser
        if key_mapping.key.startswith('sk '):
            key = key_mapping.key.replace('sk ', '')
            sticky_binding = StickyKeyBinding(key)
            return sticky_binding.to_kanata()
            
        # Handle layer momentary switch
        if key_mapping.key.startswith("mo "):
            layer_num = key_mapping.key.split(" ")[1]
            return f"@layer{layer_num}"
        
        # Handle transparent key
        if key_mapping.key == "trans":
            return "_"
        
        # Handle basic key press using key map
        mapped_key = self.key_map.get(key_mapping.key)
        if mapped_key:
            return mapped_key
        
        # Special case for KP_N keys
        if (key_mapping.key.startswith("KP_N") and 
                key_mapping.key[4:].isdigit()):
            num = key_mapping.key[4:]
            return f"kp{num}"
        
        # Handle unknown keys by lowercasing
        return key_mapping.key.lower()
    
    def parse_binding_matrix(self, zmk_bindings: str) -> List[List[str]]:
        """Parse ZMK bindings string into a matrix of bindings.
        
        Args:
            zmk_bindings: Raw ZMK bindings string
            
        Returns:
            Matrix of bindings (rows and columns)
        """
        # Split into rows and clean up whitespace
        rows = [row.strip() for row in zmk_bindings.strip().split("\n")]
        
        # Parse each row into individual bindings
        matrix = []
        for row in rows:
            if not row:  # Skip empty rows
                continue
            # Split row into individual bindings and transform each
            bindings = [b.strip() for b in row.split("&") if b.strip()]
            transformed = []
            for binding in bindings:
                result = self.transform_binding(binding)
                if result:
                    transformed.append(result)
            if transformed:  # Only add non-empty rows
                matrix.append(transformed)
        
        return matrix
    
    def transform_bindings_matrix(
        self, matrix: List[List[KeyMapping]]
    ) -> List[List[str]]:
        """Transform a matrix of KeyMapping objects into Kanata key strings."""
        if not matrix:
            return []

        result = []
        for row in matrix:
            transformed_row = []
            for binding in row:
                if binding is None:
                    transformed_row.append("trans")
                else:
                    transformed_row.append(self.transform_binding(binding))
            result.append(transformed_row)
        return result
    
    def transform_layer(self, layer: Layer) -> KanataLayer:
        """Transform a ZMK layer into a Kanata layer."""
        # Remove _layer suffix if present
        name = layer.name.replace("_layer", "")
        
        # Transform the bindings matrix
        transformed_matrix = self.transform_bindings_matrix(layer.keys)
        
        return KanataLayer(name=name, keys=transformed_matrix)
    
    def transform_layers(self, zmk_layers: List[Layer]) -> List[KanataLayer]:
        """Transform multiple ZMK layers into Kanata format.
        
        Args:
            zmk_layers: List of ZMK Layer objects
            
        Returns:
            List of transformed KanataLayer objects
        """
        return [self.transform_layer(layer) for layer in zmk_layers]