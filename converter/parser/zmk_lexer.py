"""ZMK Lexer module for tokenizing ZMK config files."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types for ZMK lexer."""

    IDENTIFIER = auto()
    NUMBER = auto()  # For numeric literals
    STRING = auto()  # For string literals
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_ANGLE = auto()
    CLOSE_ANGLE = auto()
    AMPERSAND = auto()
    EQUALS = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()  # For separating items in lists
    SLASH = auto()
    EOF = auto()


@dataclass
class SourceLocation:
    """Source location information for tokens."""

    line: int
    column: int
    offset: int


@dataclass
class Token:
    """Token class for ZMK lexer."""

    type: TokenType
    value: str
    location: SourceLocation
