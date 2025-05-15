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
    "SLASH": "fslh",
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

# Add numeric HID usage codes for standard keys (based on ZMK/QMK HID usage tables)
NUMERIC_TO_SYMBOLIC = {
    # Letters
    "4": "A",
    "5": "B",
    "6": "C",
    "7": "D",
    "8": "E",
    "9": "F",
    "10": "G",
    "11": "H",
    "12": "I",
    "13": "J",
    "14": "K",
    "15": "L",
    "16": "M",
    "17": "N",
    "18": "O",
    "19": "P",
    "20": "Q",
    "21": "R",
    "22": "S",
    "23": "T",
    "24": "U",
    "25": "V",
    "26": "W",
    "27": "X",
    "28": "Y",
    "29": "Z",
    # Numbers
    "30": "N1",
    "31": "N2",
    "32": "N3",
    "33": "N4",
    "34": "N5",
    "35": "N6",
    "36": "N7",
    "37": "N8",
    "38": "N9",
    "39": "N0",
    # Enter, Escape, Backspace, Tab, Space
    "40": "ENTER",
    "41": "ESC",
    "42": "BSPC",
    "43": "TAB",
    "44": "SPACE",
    # Punctuation
    "45": "MINUS",
    "46": "EQUAL",
    "47": "LBKT",
    "48": "RBKT",
    "49": "BSLH",
    "51": "SEMI",
    "52": "APOS",
    "53": "GRAVE",
    "54": "COMMA",
    "55": "DOT",
    "56": "FSLH",
    # Caps Lock
    "57": "CAPS",
    # Function keys
    "58": "F1",
    "59": "F2",
    "60": "F3",
    "61": "F4",
    "62": "F5",
    "63": "F6",
    "64": "F7",
    "65": "F8",
    "66": "F9",
    "67": "F10",
    "68": "F11",
    "69": "F12",
    # Print, Scroll, Pause
    "70": "PSCRN",
    "71": "SLCK",
    "72": "PAUSE",
    # Insert, Home, Page Up, Delete, End, Page Down
    "73": "INS",
    "74": "HOME",
    "75": "PG_UP",
    "76": "DEL",
    "77": "END",
    "78": "PG_DN",
    # Arrows
    "79": "RIGHT",
    "80": "LEFT",
    "81": "DOWN",
    "82": "UP",
    # Numpad
    "83": "NUMLOCK",
    "84": "KP_SLASH",
    "85": "KP_ASTERISK",
    "86": "KP_MINUS",
    "87": "KP_PLUS",
    "88": "KP_ENTER",
    "89": "KP_N1",
    "90": "KP_N2",
    "91": "KP_N3",
    "92": "KP_N4",
    "93": "KP_N5",
    "94": "KP_N6",
    "95": "KP_N7",
    "96": "KP_N8",
    "97": "KP_N9",
    "98": "KP_N0",
    "99": "KP_DOT",
    # Modifiers
    "224": "LCTRL",
    "225": "LSHIFT",
    "226": "LALT",
    "227": "LGUI",
    "228": "RCTRL",
    "229": "RSHIFT",
    "230": "RALT",
    "231": "RGUI",
}

# Update ZMK_TO_KANATA to include numeric keys for all mapped symbolic keys
for num, sym in NUMERIC_TO_SYMBOLIC.items():
    if sym in ZMK_TO_KANATA:
        ZMK_TO_KANATA[num] = ZMK_TO_KANATA[sym]

# Reverse mapping for numeric to symbolic
REVERSE_KEY_MAP = {num: sym for num, sym in NUMERIC_TO_SYMBOLIC.items()}


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
        # Try to map numeric to symbolic, then to Kanata
        sym = REVERSE_KEY_MAP.get(key)
        if sym and sym in ZMK_TO_KANATA:
            return ZMK_TO_KANATA[sym]
        return f"; TODO: Unknown numeric keycode: {key}"
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


def zmk_binding_to_kanata(
    binding_str: str,
    hold_tap: Optional[object] = None,
    sticky: bool = False,
) -> Optional[str]:
    """
    Convert a ZMK binding string (e.g., '&kp A', '&mo 1', '&sk LSHIFT', '&trans').
    Handles all special cases. Optionally, pass hold_tap or sticky flags for advanced cases.
    """
    binding_str = binding_str.strip()
    # Handle empty or none
    if not binding_str or binding_str == "&none":
        return "none"
    # Transparent
    if binding_str == "&trans" or binding_str == "trans":
        return "_"
    # Sticky key
    if binding_str.startswith("&sk") or sticky:
        parts = binding_str.split()
        key = (
            parts[1] if len(parts) > 1 else (parts[0][3:] if len(parts[0]) > 3 else "")
        )
        k = zmk_to_kanata(key) if key else key
        if k and k.startswith("f") and k[1:].isdigit():
            return f"sticky-{k}"
        return f"sticky-{k if k else ''}"
    # Hold-tap (emit alias if hold_tap info is present)
    if hold_tap:
        if (
            hasattr(hold_tap, "hold_tap")
            and hasattr(hold_tap.hold_tap, "name")
            and hasattr(hold_tap, "hold")
            and hasattr(hold_tap, "tap")
        ):
            return f"@{hold_tap.hold_tap.name}_{hold_tap.hold}_{hold_tap.tap}"
        elif (
            hasattr(hold_tap, "name")
            and hasattr(hold_tap, "hold_key")
            and hasattr(hold_tap, "tap_key")
        ):
            return f"@{hold_tap.name}_{hold_tap.hold_key}_{hold_tap.tap_key}"
    # Layer switch
    if binding_str.startswith("&mo") or binding_str.startswith("mo "):
        parts = binding_str.split()
        layer_num = parts[1] if len(parts) > 1 else "?"
        return f"(layer-while-held {layer_num})"
    if binding_str.startswith("&to") or binding_str.startswith("to "):
        parts = binding_str.split()
        layer_num = parts[1] if len(parts) > 1 else "?"
        return f"(layer-switch {layer_num})"
    # Regular key binding
    if binding_str.startswith("&kp"):
        parts = binding_str.split()
        key = parts[1] if len(parts) > 1 else ""
        return zmk_to_kanata(key) if key else key
    # Fallback: try direct mapping
    mapped = zmk_to_kanata(binding_str)
    if mapped is not None:
        return mapped
    # Unknown binding
    if binding_str.startswith("&"):
        return f"; TODO: Unknown binding: {binding_str}"
    return binding_str
