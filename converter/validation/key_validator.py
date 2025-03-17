"""Key validation module for ZMK to Kanata conversion."""

from typing import Dict, Optional
import re

# Define valid key categories
LETTERS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
NUMBERS = {f'N{i}' for i in range(10)}
FUNCTION_KEYS = {f'F{i}' for i in range(1, 25)}  # F1 to F24

# Navigation keys
NAVIGATION_KEYS = {
    'LEFT', 'RIGHT', 'UP', 'DOWN',
    'HOME', 'END', 'PG_UP', 'PG_DN',
    'INS', 'DEL'
}

# Editing keys
EDITING_KEYS = {
    'ENTER', 'RET', 'ESC', 'BSPC',
    'DEL', 'TAB', 'SPACE', 'SPC',
    'CAPS'
}

# Modifier keys
MODIFIER_KEYS = {
    'LSHIFT', 'RSHIFT', 'LCTRL', 'RCTRL',
    'LALT', 'RALT', 'LGUI', 'RGUI',
    'LWIN', 'RWIN'  # Windows-specific aliases
}

# Punctuation keys
PUNCTUATION_KEYS = {
    'GRAVE', 'MINUS', 'EQUAL', 'LBKT', 'RBKT',
    'BSLH', 'SEMI', 'APOS', 'COMMA', 'DOT',
    'FSLH', 'NUBS'  # Non-US backslash
}

# Symbol keys
SYMBOL_KEYS = {
    'EXCL', 'AT', 'HASH', 'DLLR', 'PRCNT',
    'CARET', 'AMPS', 'STAR', 'LPAR', 'RPAR',
    'PLUS', 'UNDER', 'PIPE', 'TILDE'
}

# Media keys
MEDIA_KEYS = {
    'C_MUTE', 'C_VOL_UP', 'C_VOL_DN',
    'C_PP', 'C_NEXT', 'C_PREV',
    'C_STOP', 'C_EJECT'
}

# Numpad keys
NUMPAD_KEYS = {
    'KP_SLASH', 'KP_MULTIPLY', 'KP_MINUS',
    'KP_PLUS', 'KP_ENTER', 'KP_DOT'
} | {f'KP_N{i}' for i in range(10)}

# International keys
INTERNATIONAL_KEYS = {
    'INT1', 'INT2', 'INT3', 'INT4',
    'INT5', 'INT6', 'INT7', 'INT8', 'INT9'
}

# Language keys
LANGUAGE_KEYS = {
    'LANG1', 'LANG2', 'LANG3',
    'LANG4', 'LANG5', 'LANG6',
    'LANG7', 'LANG8', 'LANG9'
}

# All valid keys
VALID_KEYS = (
    LETTERS | NUMBERS | FUNCTION_KEYS |
    NAVIGATION_KEYS | EDITING_KEYS | MODIFIER_KEYS |
    PUNCTUATION_KEYS | SYMBOL_KEYS | MEDIA_KEYS |
    NUMPAD_KEYS | INTERNATIONAL_KEYS | LANGUAGE_KEYS
)

# Special behavior keys
SPECIAL_KEYS = {
    'NONE',  # No-op
    'TRANS'  # Transparent key
}

# ZMK to Kanata key mapping
ZMK_TO_KANATA: Dict[str, str] = {
    # Modifiers
    'LSHIFT': 'lsft',
    'RSHIFT': 'rsft',
    'LCTRL': 'lctl',
    'RCTRL': 'rctl',
    'LALT': 'lalt',
    'RALT': 'ralt',
    'LGUI': 'lmet',
    'RGUI': 'rmet',
    'LWIN': 'lmet',
    'RWIN': 'rmet',

    # Editing
    'ENTER': 'ret',
    'RET': 'ret',
    'ESC': 'esc',
    'BSPC': 'bspc',
    'DEL': 'del',
    'TAB': 'tab',
    'SPACE': 'spc',
    'SPC': 'spc',

    # Navigation
    'LEFT': 'left',
    'RIGHT': 'right',
    'UP': 'up',
    'DOWN': 'down',
    'HOME': 'home',
    'END': 'end',
    'PG_UP': 'pgup',
    'PG_DN': 'pgdn',

    # Punctuation
    'GRAVE': 'grv',
    'MINUS': 'minus',
    'EQUAL': 'equal',
    'LBKT': 'lbrc',
    'RBKT': 'rbrc',
    'BSLH': 'bslh',
    'SEMI': 'semi',
    'APOS': 'apos',
    'COMMA': 'comma',
    'DOT': 'dot',
    'FSLH': 'fslh',

    # Symbols
    'EXCL': 'excl',
    'AT': 'at',
    'HASH': 'hash',
    'DLLR': 'dollar',
    'PRCNT': 'percent',
    'CARET': 'caret',
    'AMPS': 'amp',
    'STAR': 'astrk',
    'LPAR': 'lprn',
    'RPAR': 'rprn',
    'PLUS': 'plus',
    'UNDER': 'under',
    'PIPE': 'pipe',
    'TILDE': 'tilde'
}


class KeyValidationError(Exception):
    """Exception raised for key validation errors."""

    def __init__(self, message: str, key: str, details: Optional[str] = None):
        """Initialize the error.

        Args:
            message: The error message
            key: The invalid key
            details: Optional additional details about the error
        """
        self.key = key
        self.details = details
        super().__init__(message)


def validate_key(key: str) -> bool:
    """Validate a ZMK key.

    Args:
        key: The key to validate

    Returns:
        bool: True if the key is valid

    Raises:
        KeyValidationError: If the key is invalid
    """
    if not key:
        raise KeyValidationError(
            "Empty key",
            key,
            "Key cannot be empty"
        )

    # Handle special keys
    if key in SPECIAL_KEYS:
        return True

    # Handle layer keys
    if key.startswith(('mo ', 'to ')):
        try:
            layer_num = int(key.split()[1])
            if layer_num < 0:
                raise KeyValidationError(
                    f"Invalid layer number in key: {key}",
                    key,
                    "Layer numbers must be non-negative"
                )
            return True
        except (IndexError, ValueError):
            raise KeyValidationError(
                f"Invalid layer key format: {key}",
                key,
                "Layer keys must be in format 'mo N' or 'to N' "
                "where N is a number"
            )

    # Handle regular keys
    if key in VALID_KEYS:
        return True

    # Handle number keys without N prefix
    if key.isdigit():
        return True

    # Handle function keys without F prefix
    if key.startswith('F') and key[1:].isdigit():
        fn_num = int(key[1:])
        if 1 <= fn_num <= 24:
            return True
        raise KeyValidationError(
            f"Invalid function key number: {key}",
            key,
            "Function key numbers must be between 1 and 24"
        )

    # Handle key sequences
    if is_key_sequence(key):
        validate_key_sequence(key)
        return True

    # If we get here, the key is invalid
    category = suggest_key_category(key)
    suggestion = suggest_similar_key(key)
    details = []

    if category:
        details.append(f"Did you mean to use a {category} key?")
    if suggestion:
        details.append(f"Did you mean '{suggestion}'?")

    raise KeyValidationError(
        f"Invalid key: {key}",
        key,
        " ".join(details) if details else None
    )


def is_key_sequence(key: str) -> bool:
    """Check if a key is a key sequence.

    Args:
        key: The key to check

    Returns:
        bool: True if the key is a sequence
    """
    return bool(re.match(r'^[A-Z0-9_]+(\s+[A-Z0-9_]+)+$', key))


def validate_key_sequence(sequence: str) -> None:
    """Validate a key sequence.

    Args:
        sequence: The key sequence to validate

    Raises:
        KeyValidationError: If the sequence is invalid
    """
    keys = sequence.split()
    for key in keys:
        if key not in VALID_KEYS and not key.isdigit():
            msg = "Each key in the sequence must be valid."
            details = f"'{key}' is not valid."
            raise KeyValidationError(
                f"Invalid key in sequence: {key}",
                sequence,
                f"{msg} {details}"
            )


def suggest_key_category(key: str) -> Optional[str]:
    """Suggest a key category based on the invalid key.

    Args:
        key: The invalid key

    Returns:
        Optional[str]: The suggested category or None
    """
    if re.match(r'^[A-Z]$', key):
        return "letter"
    if re.match(r'^[0-9]+$', key) or key.startswith('N'):
        return "number"
    if key.startswith('F'):
        return "function"
    if key in {'UP', 'DOWN', 'LEFT', 'RIGHT'}:
        return "navigation"
    if key in {'SHIFT', 'CTRL', 'ALT', 'GUI', 'WIN'}:
        return "modifier"
    if key.startswith('KP'):
        return "numpad"
    return None


def suggest_similar_key(key: str) -> Optional[str]:
    """Suggest a similar valid key.

    Args:
        key: The invalid key

    Returns:
        Optional[str]: The suggested key or None
    """
    # Check for common mistakes
    if key.startswith('SHIFT'):
        return 'LSHIFT' if 'L' in key else 'RSHIFT'
    if key.startswith('CTRL'):
        return 'LCTRL' if 'L' in key else 'RCTRL'
    if key.startswith('ALT'):
        return 'LALT' if 'L' in key else 'RALT'
    if key.startswith('GUI') or key.startswith('WIN'):
        return 'LGUI' if 'L' in key else 'RGUI'

    # Find the closest match by Levenshtein distance
    best_match = None
    best_distance = float('inf')

    for valid_key in VALID_KEYS:
        distance = levenshtein_distance(key, valid_key)
        if distance < best_distance and distance <= 2:
            best_match = valid_key
            best_distance = distance

    return best_match


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        int: The Levenshtein distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if not s2:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def convert_to_kanata(key: str) -> str:
    """Convert a ZMK key to Kanata format.

    Args:
        key: The ZMK key to convert

    Returns:
        str: The key in Kanata format

    Raises:
        KeyValidationError: If the key cannot be converted
    """
    # Validate the key first
    validate_key(key)

    # Handle special keys
    if key == 'TRANS':
        return '_'
    if key == 'NONE':
        return 'none'

    # Handle layer keys
    if key.startswith('mo '):
        layer_num = key.split()[1]
        return f"(layer-while-held {layer_num})"
    if key.startswith('to '):
        layer_num = key.split()[1]
        return f"(layer-switch {layer_num})"

    # Use mapping table for special conversions
    if key in ZMK_TO_KANATA:
        return ZMK_TO_KANATA[key]

    # Handle number keys
    if key.startswith('N') and key[1:].isdigit():
        return key[1:]  # Remove N prefix
    if key.isdigit():
        return key

    # Handle function keys
    if key in FUNCTION_KEYS or (
        key.startswith('F') and key[1:].isdigit()
    ):
        return key.lower()

    # Handle key sequences
    if is_key_sequence(key):
        keys = key.split()
        converted_keys = [
            ZMK_TO_KANATA.get(k, k.lower())
            for k in keys
        ]
        return f"(chord {' '.join(converted_keys)})"

    # Default to lowercase for regular keys
    return key.lower()


def get_key_category(key: str) -> Optional[str]:
    """Get the category of a key.

    Args:
        key: The key to categorize

    Returns:
        Optional[str]: The category name, or None if unknown
    """
    if key in LETTERS:
        return 'letter'
    if key in NUMBERS or key.isdigit():
        return 'number'
    if key in FUNCTION_KEYS:
        return 'function'
    if key in NAVIGATION_KEYS:
        return 'navigation'
    if key in EDITING_KEYS:
        return 'editing'
    if key in MODIFIER_KEYS:
        return 'modifier'
    if key in PUNCTUATION_KEYS:
        return 'punctuation'
    if key in SYMBOL_KEYS:
        return 'symbol'
    if key in MEDIA_KEYS:
        return 'media'
    if key in NUMPAD_KEYS:
        return 'numpad'
    if key in INTERNATIONAL_KEYS:
        return 'international'
    if key in LANGUAGE_KEYS:
        return 'language'
    if key in SPECIAL_KEYS:
        return 'special'
    if key.startswith(('mo ', 'to ')):
        return 'layer'
    if is_key_sequence(key):
        return 'sequence'
    return None
