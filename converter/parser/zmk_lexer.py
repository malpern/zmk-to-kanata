"""Module for lexical analysis of ZMK configuration files."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Tuple


class TokenType(Enum):
    """Enum representing the types of tokens in a ZMK configuration file."""
    # Structural tokens
    OPEN_BRACE = auto()      # {
    CLOSE_BRACE = auto()     # }
    OPEN_ANGLE = auto()      # <
    CLOSE_ANGLE = auto()     # >
    OPEN_PAREN = auto()      # (
    CLOSE_PAREN = auto()     # )
    SEMICOLON = auto()       # ;
    COMMA = auto()           # ,
    COLON = auto()           # :
    EQUALS = auto()          # =
    AT_SIGN = auto()         # @
    AMPERSAND = auto()       # &
    SLASH = auto()           # /
    
    # Identifier and values
    IDENTIFIER = auto()      # Letters, numbers, underscores, hyphen
    NUMBER = auto()          # Integer or decimal number
    STRING = auto()          # Quoted string
    
    # Special tokens
    COMMENT = auto()         # // or /* */
    WHITESPACE = auto()      # Spaces, tabs, newlines
    EOF = auto()             # End of file
    
    # Keyword tokens
    KW_COMPATIBLE = auto()   # compatible
    KW_BINDINGS = auto()     # bindings
    KW_LABEL = auto()        # label
    KW_LAYERS = auto()       # layers
    KW_KEYMAP = auto()       # keymap
    KW_GLOBAL = auto()       # global
    KW_BEHAVIORS = auto()    # behaviors
    KW_MACROS = auto()       # macros
    
    # Unknown token (for error recovery)
    UNKNOWN = auto()


@dataclass
class SourceLocation:
    """Class to represent the location of a token in the source file."""
    line: int               # 1-based line number
    column: int             # 1-based column number
    offset: int             # 0-based character offset from the start of the file
    length: int = 1         # Length of the token in characters
    
    def __str__(self) -> str:
        """Return a string representation of the source location."""
        return f"line {self.line}, column {self.column}"


@dataclass
class Token:
    """Class to represent a token in a ZMK configuration file."""
    type: TokenType         # Type of the token
    value: str              # Actual text of the token
    location: SourceLocation  # Location of the token in the source
    
    def __str__(self) -> str:
        """Return a string representation of the token."""
        return f"{self.type.name}('{self.value}') at {self.location}"


class ZMKLexer:
    """Lexer for ZMK configuration files."""
    
    # Map of keywords to token types
    KEYWORDS = {
        "compatible": TokenType.KW_COMPATIBLE,
        "bindings": TokenType.KW_BINDINGS,
        "label": TokenType.KW_LABEL,
        "layers": TokenType.KW_LAYERS,
        "keymap": TokenType.KW_KEYMAP,
        "global": TokenType.KW_GLOBAL,
        "behaviors": TokenType.KW_BEHAVIORS,
        "macros": TokenType.KW_MACROS,
    }
    
    def __init__(self, source: str):
        """Initialize the lexer with the source code."""
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.error_tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        while self.position < len(self.source):
            # Skip whitespace
            if self.source[self.position].isspace():
                self._consume_whitespace()
                continue
            
            # Check for comments
            if self.position + 1 < len(self.source) and self.source[self.position:self.position+2] == "//":
                self._consume_line_comment()
                continue
            
            if self.position + 1 < len(self.source) and self.source[self.position:self.position+2] == "/*":
                self._consume_block_comment()
                continue
            
            # Check for structural tokens
            if self._try_consume_structural_token():
                continue
            
            # Check for identifiers and keywords
            if self.source[self.position].isalpha() or self.source[self.position] == '_':
                self._consume_identifier()
                continue
            
            # Check for numbers
            if self.source[self.position].isdigit() or self.source[self.position] == '-':
                self._consume_number()
                continue
            
            # Check for string literals
            if self.source[self.position] == '"':
                self._consume_string()
                continue
            
            # Unknown token (for error recovery)
            self._add_token(TokenType.UNKNOWN, self.source[self.position])
            self._advance()
        
        # Add EOF token
        self._add_token(TokenType.EOF, "")
        
        return self.tokens
    
    def _advance(self) -> None:
        """Advance the position and update line and column."""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def _peek(self, ahead: int = 0) -> Optional[str]:
        """Peek at a character ahead of the current position."""
        index = self.position + ahead
        if index >= len(self.source):
            return None
        return self.source[index]
    
    def _add_token(self, token_type: TokenType, value: str, length: int = None) -> None:
        """Add a token to the list of tokens."""
        if length is None:
            length = len(value)
        
        location = SourceLocation(
            line=self.line,
            column=self.column - length,
            offset=self.position - length,
            length=length
        )
        
        token = Token(type=token_type, value=value, location=location)
        
        if token_type == TokenType.UNKNOWN:
            self.error_tokens.append(token)
        
        self.tokens.append(token)
    
    def _try_consume_structural_token(self) -> bool:
        """Try to consume a structural token."""
        char = self.source[self.position]
        
        if char == '{':
            self._add_token(TokenType.OPEN_BRACE, char)
        elif char == '}':
            self._add_token(TokenType.CLOSE_BRACE, char)
        elif char == '<':
            self._add_token(TokenType.OPEN_ANGLE, char)
        elif char == '>':
            self._add_token(TokenType.CLOSE_ANGLE, char)
        elif char == '(':
            self._add_token(TokenType.OPEN_PAREN, char)
        elif char == ')':
            self._add_token(TokenType.CLOSE_PAREN, char)
        elif char == ';':
            self._add_token(TokenType.SEMICOLON, char)
        elif char == ',':
            self._add_token(TokenType.COMMA, char)
        elif char == ':':
            self._add_token(TokenType.COLON, char)
        elif char == '=':
            self._add_token(TokenType.EQUALS, char)
        elif char == '@':
            self._add_token(TokenType.AT_SIGN, char)
        elif char == '&':
            self._add_token(TokenType.AMPERSAND, char)
        elif char == '/':
            self._add_token(TokenType.SLASH, char)
        else:
            return False
        
        self._advance()
        return True
    
    def _consume_whitespace(self) -> None:
        """Consume whitespace characters."""
        start_pos = self.position
        
        while self.position < len(self.source) and self.source[self.position].isspace():
            self._advance()
        
        whitespace = self.source[start_pos:self.position]
        
        # Add whitespace token (typically filtered out in parsing phase)
        self._add_token(
            TokenType.WHITESPACE, 
            whitespace, 
            length=len(whitespace)
        )
    
    def _consume_line_comment(self) -> None:
        """Consume a line comment."""
        start_pos = self.position
        
        # Skip the initial //
        self._advance()
        self._advance()
        
        while self.position < len(self.source) and self.source[self.position] != '\n':
            self._advance()
        
        comment = self.source[start_pos:self.position]
        
        # Add comment token (typically filtered out in parsing phase)
        self._add_token(
            TokenType.COMMENT, 
            comment, 
            length=len(comment)
        )
    
    def _consume_block_comment(self) -> None:
        """Consume a block comment."""
        start_pos = self.position
        
        # Skip the initial /*
        self._advance()
        self._advance()
        
        nesting_level = 1
        while self.position < len(self.source) and nesting_level > 0:
            if self.position + 1 < len(self.source) and self.source[self.position:self.position+2] == "/*":
                nesting_level += 1
                self._advance()
                self._advance()
            elif self.position + 1 < len(self.source) and self.source[self.position:self.position+2] == "*/":
                nesting_level -= 1
                self._advance()
                self._advance()
            else:
                self._advance()
        
        comment = self.source[start_pos:self.position]
        
        # Add comment token (typically filtered out in parsing phase)
        self._add_token(
            TokenType.COMMENT, 
            comment, 
            length=len(comment)
        )
    
    def _consume_identifier(self) -> None:
        """Consume an identifier."""
        start_pos = self.position
        
        while (
            self.position < len(self.source) and 
            (self.source[self.position].isalnum() or 
             self.source[self.position] in "_-#")
        ):
            self._advance()
        
        identifier = self.source[start_pos:self.position]
        
        # Check if the identifier is a keyword
        token_type = self.KEYWORDS.get(identifier, TokenType.IDENTIFIER)
        
        self._add_token(
            token_type, 
            identifier, 
            length=len(identifier)
        )
    
    def _consume_number(self) -> None:
        """Consume a number."""
        start_pos = self.position
        
        # Handle negative numbers
        if self.source[self.position] == '-':
            self._advance()
        
        # Consume the first part of the number
        while self.position < len(self.source) and self.source[self.position].isdigit():
            self._advance()
        
        # Handle decimal part if present
        if (
            self.position < len(self.source) and 
            self.source[self.position] == '.' and 
            self.position + 1 < len(self.source) and 
            self.source[self.position + 1].isdigit()
        ):
            self._advance()  # consume the '.'
            
            while self.position < len(self.source) and self.source[self.position].isdigit():
                self._advance()
        
        number = self.source[start_pos:self.position]
        
        self._add_token(
            TokenType.NUMBER, 
            number, 
            length=len(number)
        )
    
    def _consume_string(self) -> None:
        """Consume a string literal."""
        start_pos = self.position
        
        # Skip the opening quote
        self._advance()
        
        while self.position < len(self.source) and self.source[self.position] != '"':
            # Handle escape sequences
            if (
                self.source[self.position] == '\\' and 
                self.position + 1 < len(self.source)
            ):
                self._advance()  # Skip the backslash
            
            self._advance()
        
        # Skip the closing quote if present
        if self.position < len(self.source) and self.source[self.position] == '"':
            self._advance()
        
        string = self.source[start_pos:self.position]
        
        self._add_token(
            TokenType.STRING, 
            string, 
            length=len(string)
        )
    
    def get_errors(self) -> List[Tuple[str, SourceLocation]]:
        """Get a list of lexical errors."""
        return [(token.value, token.location) for token in self.error_tokens] 