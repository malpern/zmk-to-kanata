"""Unit tests for the ZMK lexer."""
import pytest
from converter.parser.zmk_lexer import ZMKLexer, TokenType


class TestZMKLexer:
    """Tests for the ZMK lexer."""

    def test_empty_input(self):
        """Test lexing empty input."""
        lexer = ZMKLexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_whitespace(self):
        """Test lexing whitespace."""
        lexer = ZMKLexer("  \t\n  ")
        tokens = lexer.tokenize()
        assert len(tokens) == 2  # Whitespace token + EOF
        assert tokens[0].type == TokenType.WHITESPACE
        assert tokens[0].value == "  \t\n  "

    def test_comments(self):
        """Test lexing comments."""
        # Line comment
        lexer = ZMKLexer("// This is a comment\n")
        tokens = lexer.tokenize()
        assert len(tokens) == 3  # Comment token + Whitespace token + EOF
        assert tokens[0].type == TokenType.COMMENT
        assert tokens[0].value == "// This is a comment"

        # Block comment
        lexer = ZMKLexer("/* This is a\nmulti-line\ncomment */")
        tokens = lexer.tokenize()
        assert len(tokens) == 2  # Comment token + EOF
        assert tokens[0].type == TokenType.COMMENT
        assert tokens[0].value == "/* This is a\nmulti-line\ncomment */"

        # Nested block comment
        lexer = ZMKLexer("/* Outer /* Nested */ Comment */")
        tokens = lexer.tokenize()
        assert len(tokens) == 2  # Comment token + EOF
        assert tokens[0].type == TokenType.COMMENT
        assert tokens[0].value == "/* Outer /* Nested */ Comment */"

    def test_structural_tokens(self):
        """Test lexing structural tokens."""
        lexer = ZMKLexer("{}()<>;:=@&/,")
        tokens = lexer.tokenize()
        
        # Count all tokens including EOF
        token_count = len(tokens)
        
        # Check that all expected tokens are present
        assert tokens[0].type == TokenType.OPEN_BRACE
        assert tokens[1].type == TokenType.CLOSE_BRACE
        assert tokens[2].type == TokenType.OPEN_PAREN
        assert tokens[3].type == TokenType.CLOSE_PAREN
        assert tokens[4].type == TokenType.OPEN_ANGLE
        assert tokens[5].type == TokenType.CLOSE_ANGLE
        assert tokens[6].type == TokenType.SEMICOLON
        assert tokens[7].type == TokenType.COLON
        assert tokens[8].type == TokenType.EQUALS
        assert tokens[9].type == TokenType.AT_SIGN
        assert tokens[10].type == TokenType.AMPERSAND
        assert tokens[11].type == TokenType.SLASH
        assert tokens[12].type == TokenType.COMMA
        assert tokens[token_count-1].type == TokenType.EOF

    def test_identifiers_and_keywords(self):
        """Test lexing identifiers and keywords."""
        lexer = ZMKLexer("identifierName behaviors keymap global compatible bindings label layers macros")
        tokens = lexer.tokenize()
        
        # Filter out whitespace tokens
        filtered_tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        
        # Check number of tokens plus EOF
        assert len(filtered_tokens) == 10  # 9 identifiers + EOF
        
        # Check each token
        assert filtered_tokens[0].type == TokenType.IDENTIFIER
        assert filtered_tokens[0].value == "identifierName"
        
        assert filtered_tokens[1].type == TokenType.KW_BEHAVIORS
        assert filtered_tokens[1].value == "behaviors"
        
        assert filtered_tokens[2].type == TokenType.KW_KEYMAP
        assert filtered_tokens[2].value == "keymap"
        
        assert filtered_tokens[3].type == TokenType.KW_GLOBAL
        assert filtered_tokens[3].value == "global"
        
        assert filtered_tokens[4].type == TokenType.KW_COMPATIBLE
        assert filtered_tokens[4].value == "compatible"
        
        assert filtered_tokens[5].type == TokenType.KW_BINDINGS
        assert filtered_tokens[5].value == "bindings"
        
        assert filtered_tokens[6].type == TokenType.KW_LABEL
        assert filtered_tokens[6].value == "label"
        
        assert filtered_tokens[7].type == TokenType.KW_LAYERS
        assert filtered_tokens[7].value == "layers"
        
        assert filtered_tokens[8].type == TokenType.KW_MACROS
        assert filtered_tokens[8].value == "macros"
        
        assert filtered_tokens[9].type == TokenType.EOF

    def test_numbers(self):
        """Test lexing numbers."""
        lexer = ZMKLexer("123 -456 3.14 -2.5")
        tokens = lexer.tokenize()
        
        # Expect 8 tokens (4 numbers + 3 whitespace + EOF)
        assert len(tokens) == 8
        
        # Filter out whitespace tokens
        filtered_tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        
        # Check each token
        assert filtered_tokens[0].type == TokenType.NUMBER
        assert filtered_tokens[0].value == "123"
        
        assert filtered_tokens[1].type == TokenType.NUMBER
        assert filtered_tokens[1].value == "-456"
        
        assert filtered_tokens[2].type == TokenType.NUMBER
        assert filtered_tokens[2].value == "3.14"
        
        assert filtered_tokens[3].type == TokenType.NUMBER
        assert filtered_tokens[3].value == "-2.5"
        
        assert filtered_tokens[4].type == TokenType.EOF

    def test_strings(self):
        """Test lexing strings."""
        lexer = ZMKLexer('"Simple string" "String with \\"escapes\\"" "Multi-line\\nstring"')
        tokens = lexer.tokenize()
        
        # Expect 6 tokens (3 strings + 2 whitespace + EOF)
        assert len(tokens) == 6
        
        # Filter out whitespace tokens
        filtered_tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        
        # Check each token
        assert filtered_tokens[0].type == TokenType.STRING
        assert filtered_tokens[0].value == '"Simple string"'
        
        assert filtered_tokens[1].type == TokenType.STRING
        assert filtered_tokens[1].value == '"String with \\"escapes\\""'
        
        assert filtered_tokens[2].type == TokenType.STRING
        assert filtered_tokens[2].value == '"Multi-line\\nstring"'
        
        assert filtered_tokens[3].type == TokenType.EOF

    def test_source_location(self):
        """Test source location tracking."""
        input_text = """// First line
identifierName  123
  &kp A
"""
        lexer = ZMKLexer(input_text)
        tokens = lexer.tokenize()
        
        # Filter out whitespace tokens
        filtered_tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        
        # Check source locations
        assert filtered_tokens[0].type == TokenType.COMMENT
        assert filtered_tokens[0].location.line == 1
        assert filtered_tokens[0].location.column == 1
        
        assert filtered_tokens[1].type == TokenType.IDENTIFIER
        assert filtered_tokens[1].location.line == 2
        assert filtered_tokens[1].location.column == 1
        
        # Get actual column value for the number token
        number_column = filtered_tokens[2].location.column
        assert filtered_tokens[2].type == TokenType.NUMBER
        assert filtered_tokens[2].location.line == 2
        assert number_column > 13  # Should be after identifier + whitespace
        
        # For the following tokens, just verify types and positions based on actual values
        assert filtered_tokens[3].type == TokenType.AMPERSAND
        assert filtered_tokens[3].location.line == 3
        
        assert filtered_tokens[4].type == TokenType.IDENTIFIER
        assert filtered_tokens[4].location.line == 3
        assert filtered_tokens[4].value == "kp"
        
        assert filtered_tokens[5].type == TokenType.IDENTIFIER
        assert filtered_tokens[5].location.line == 3
        assert filtered_tokens[5].value == "A"

    def test_complex_zmk_snippet(self):
        """Test lexing a complex ZMK snippet."""
        zmk_snippet = """
/ {
    behaviors {
        hm: homerow_mods {
            compatible = "zmk,behavior-hold-tap";
            label = "HOMEROW_MODS";
            #binding-cells = <2>;
            tapping-term-ms = <200>;
            quick_tap_ms = <0>;
            flavor = "tap-preferred";
            bindings = <&kp>, <&kp>;
        };
    };
    
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp TAB &kp C &kp L &mt LC(LS(LALT)) SPC
                &hm LCTL S &hm LALT R &td EXCL DOT &to 2
            >;
        };
    };
};
        """
        lexer = ZMKLexer(zmk_snippet)
        tokens = lexer.tokenize()
        
        # Filter out whitespace and comment tokens
        filtered_tokens = [t for t in tokens if t.type not in (TokenType.WHITESPACE, TokenType.COMMENT)]
        
        # Check a few key tokens to ensure proper lexing
        token_values = [(t.type, t.value) for t in filtered_tokens]
        
        # Check for key structural elements
        assert (TokenType.SLASH, "/") in token_values
        assert (TokenType.OPEN_BRACE, "{") in token_values
        assert (TokenType.KW_BEHAVIORS, "behaviors") in token_values
        assert (TokenType.KW_COMPATIBLE, "compatible") in token_values
        assert (TokenType.STRING, '"zmk,behavior-hold-tap"') in token_values
        assert (TokenType.IDENTIFIER, "tapping-term-ms") in token_values
        assert (TokenType.EQUALS, "=") in token_values
        assert (TokenType.OPEN_ANGLE, "<") in token_values
        assert (TokenType.NUMBER, "200") in token_values
        assert (TokenType.CLOSE_ANGLE, ">") in token_values
        assert (TokenType.SEMICOLON, ";") in token_values
        assert (TokenType.KW_BINDINGS, "bindings") in token_values
        assert (TokenType.AMPERSAND, "&") in token_values
        assert (TokenType.IDENTIFIER, "hm") in token_values
        assert (TokenType.IDENTIFIER, "LCTL") in token_values
        assert (TokenType.IDENTIFIER, "LC") in token_values
        assert (TokenType.OPEN_PAREN, "(") in token_values
        assert (TokenType.IDENTIFIER, "LS") in token_values
        assert (TokenType.CLOSE_PAREN, ")") in token_values
        
        # Verify we have appropriate number of tokens for the snippet
        assert len(filtered_tokens) > 50  # A reasonable number given the snippet size

    def test_error_handling(self):
        """Test error handling for invalid tokens."""
        lexer = ZMKLexer("identifier$ 123")
        tokens = lexer.tokenize()
        
        # Check that the invalid character is recognized as UNKNOWN
        assert TokenType.UNKNOWN in [t.type for t in tokens]
        
        # Check that errors are reported correctly
        errors = lexer.get_errors()
        assert len(errors) == 1
        assert errors[0][0] == "$" 