"""Module for transforming ZMK layer bindings into Kanata format."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .layer_parser import Layer


@dataclass
class KanataLayer:
    """Represents a layer in Kanata format."""
    name: str
    bindings: List[List[str]]  # Matrix of key bindings


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
            "LBKT": "lbracket",       # [
            "RBKT": "rbracket",       # ]
            "LBRC": "lbrace",         # {
            "RBRC": "rbrace",         # }
            "BSLH": "bslash",         # \
            "PIPE": "pipe",           # |
            "SEMI": "semicolon",      # ;
            "COLON": "colon",         # :
            "SQT": "quote",           # '
            "DQT": "dquote",          # "
            "COMMA": "comma",         # ,
            "DOT": "dot",            # .
            "FSLH": "slash",         # /
            "QMARK": "question",      # ?
            "GRAVE": "grave",         # `
            "TILDE": "tilde",        # ~
            
            # Function Keys
            "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
            "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8",
            "F9": "f9", "F10": "f10", "F11": "f11", "F12": "f12",
            
            # Navigation and Editing
            "ENTER": "ret",
            "ESC": "esc",
            "BSPC": "bspc",
            "TAB": "tab",
            "SPACE": "spc",
            "DEL": "del",
            "HOME": "home",
            "END": "end",
            "PG_UP": "pgup",
            "PG_DN": "pgdn",
            "RIGHT": "right",
            "LEFT": "left",
            "DOWN": "down",
            "UP": "up",
            
            # Modifiers
            "LSHIFT": "lshift",
            "RSHIFT": "rshift",
            "LCTRL": "lctrl",
            "RCTRL": "rctrl",
            "LALT": "lalt",
            "RALT": "ralt",
            "LGUI": "lmeta",
            "RGUI": "rmeta",
            
            # System and Media
            "CAPS": "caps",
            "INS": "ins",
            "PSCRN": "prtsc",
            "SLCK": "slck",
            "PAUSE_BREAK": "pause",
            "C_MUTE": "mute",
            "C_VOL_UP": "volu",
            "C_VOL_DN": "vold",
            "C_PP": "pp",             # Play/Pause
            "C_NEXT": "next",
            "C_PREV": "prev",
            
            # Numpad Special Keys
            "KP_PLUS": "kp_plus",
            "KP_MINUS": "kp_minus",
            "KP_MULTIPLY": "kp_multiply",
            "KP_DIVIDE": "kp_divide",
            "KP_ENTER": "kp_enter",
            "KP_DOT": "kp_dot",
            "KP_EQUAL": "kp_equal",
            
            # International and Special Characters
            "NON_US_BSLH": "iso_bslash",
            "NON_US_HASH": "iso_hash",
        }
    
    def transform_binding(self, zmk_binding: str) -> Optional[str]:
        """Transform a single ZMK binding to Kanata format.
        
        Args:
            zmk_binding: ZMK binding (e.g., "&kp A", "&mo 1")
            
        Returns:
            Kanata binding or None if binding should be skipped
        """
        binding = zmk_binding.strip()
        
        # Handle layer momentary switch
        if binding.startswith("&mo "):
            layer_num = binding.split(" ")[1]
            return f"@layer{layer_num}"
        
        # Handle transparent key
        if binding == "&trans":
            return "_"
        
        # Handle basic key press
        if binding.startswith("&kp "):
            key = binding.split(" ")[1]
            if key in self.key_map:
                return self.key_map[key]
        
        # Skip or log unhandled bindings for now
        return None
    
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
                result = self.transform_binding("&" + binding)
                if result:
                    transformed.append(result)
            if transformed:  # Only add non-empty rows
                matrix.append(transformed)
        
        return matrix
    
    def transform_layer(self, zmk_layer: Layer) -> KanataLayer:
        """Transform a ZMK layer into Kanata format.
        
        Args:
            zmk_layer: Layer object containing ZMK layer data
            
        Returns:
            KanataLayer object with transformed bindings
        """
        # Transform the bindings matrix
        kanata_bindings = self.parse_binding_matrix(zmk_layer.bindings)
        
        # Create Kanata layer name (strip _layer suffix if present)
        name = zmk_layer.name
        if name.endswith("_layer"):
            name = name[:-6]
        
        return KanataLayer(name=name, bindings=kanata_bindings)
    
    def transform_layers(self, zmk_layers: List[Layer]) -> List[KanataLayer]:
        """Transform multiple ZMK layers into Kanata format.
        
        Args:
            zmk_layers: List of ZMK Layer objects
            
        Returns:
            List of transformed KanataLayer objects
        """
        return [self.transform_layer(layer) for layer in zmk_layers] 