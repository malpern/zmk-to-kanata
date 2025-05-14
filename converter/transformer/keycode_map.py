"""
Centralized keycode mapping utility for ZMK-to-Kanata conversion.
Handles symbolic names, numeric codes, and recursive modifier macros.
"""

import re
from typing import Optional

# Main mapping table: ZMK symbolic name -> Kanata name
ZMK_TO_KANATA = {
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
    # ZMK-specific/extra
    "SQT": "sqt",
    "DQT": "dqt",
    "LBRC": "lbrc",
    "RBRC": "rbrc",
    "LPRN": "lpar",
    "RPRN": "rpar",
    "COLON": "colon",
    "ATSN": "atsn",
}

# Modifier macro patterns
MODIFIER_MACROS = [
    (r"^LS\((.+)\)$", "ls"),
    (r"^LA\((.+)\)$", "la"),
    (r"^LG\((.+)\)$", "lg"),
    (r"^RC\((.+)\)$", "rc"),
    (r"^RS\((.+)\)$", "rs"),
    (r"^RA\((.+)\)$", "ra"),
    (r"^RG\((.+)\)$", "rg"),
    (r"^LC\((.+)\)$", "lc"),
]


def zmk_to_kanata(key: str) -> Optional[str]:
    """
    Convert a ZMK key name, numeric code, or modifier macro to Kanata equivalent.
    Handles nested modifier macros recursively.
    """
    key = key.strip()
    # Direct mapping
    if key in ZMK_TO_KANATA:
        return ZMK_TO_KANATA[key]
    # Numeric code (decimal or hex)
    if re.match(r"^(0x[0-9A-Fa-f]+|\d+)$", key):
        return key.lower()
    # Modifier macro (possibly nested)
    for pattern, kanata_mod in MODIFIER_MACROS:
        m = re.match(pattern, key)
        if m:
            inner = m.group(1).strip()
            if not inner:
                return f"ERROR: malformed or unknown macro: {key}"
            inner_mapped = zmk_to_kanata(inner)
            if inner_mapped and not inner_mapped.startswith("ERROR:"):
                return f"{kanata_mod}({inner_mapped})"
            else:
                return f"ERROR: malformed or unknown macro: {key}"
    # If it looks like a macro but is not supported, emit error
    if re.match(r"^[A-Z]{2,}\(.*\)$", key):
        return f"ERROR: malformed or unknown macro: {key}"
    # If it starts with a known macro prefix and contains '(', but does not end with ')', emit error
    macro_prefixes = [
        p.split("\\")[0][2:-3] for p, _ in MODIFIER_MACROS
    ]  # e.g., 'LS', 'LA', ...
    if any(
        key.startswith(f"{prefix}(") or key.startswith(f"{prefix} (")
        for prefix in macro_prefixes
    ):
        if "(" in key and not key.rstrip().endswith(")"):
            return f"ERROR: malformed or unknown macro: {key}"
    # Fallback: unmapped
    return None


# For testability: expose the mapping table
ALL_MAPPED_KEYS = set(ZMK_TO_KANATA.keys())
