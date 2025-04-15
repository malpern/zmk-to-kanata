"""Module implementing a token-based parser for ZMK configuration files."""

import logging
import os
from typing import List, Optional

from converter.parser.zmk_lexer import ZMKLexer, Token, TokenType, SourceLocation
from converter.parser.zmk_ast import (
    ZMKDocument,
    ZMKBehaviorsBlock,
    ZMKBehaviorDefinition,
    ZMKParameter,
    ZMKKeymapBlock,
    ZMKLayerDefinition,
    ZMKBinding,
    ZMKBindingParameter,
    ZMKModifierExpression,
    ZMKMacrosBlock,
    ZMKMacroDefinition,
    ZMKMacroStep,
    ZMKCombosBlock,
    ZMKComboDefinition,
    ZMKConditionalLayersBlock,
    ZMKConditionalLayerDefinition,
)

# Set logger level from environment variable or default to WARNING
LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.WARNING))
logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Exception raised for parsing errors."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        """Initialize ParseError with a message and optional location."""
        self.message = message
        self.location = location
        super().__init__(self.get_error_message())

    def get_error_message(self) -> str:
        """Get a formatted error message with location information."""
        if self.location:
            return f"{self.message} at {self.location}"
        return self.message


class ZMKParserNew:
    """A token-based parser for ZMK configuration files."""

    def __init__(self, source: str = ""):
        """Initialize the parser."""
        self.source = source
        self.tokens: List[Token] = []
        self.position = 0
        self.errors: List[ParseError] = []
        self.warnings: List[ParseError] = []

    def parse(self, source: str = None) -> ZMKDocument:
        """Parse a ZMK configuration file."""
        if source is not None:
            self.source = source

        # Reset parser state
        self.position = 0
        self.errors = []
        self.warnings = []

        # Tokenize the source
        logger.debug("Starting tokenization")
        lexer = ZMKLexer(self.source)
        self.tokens = lexer.tokenize()
        logger.debug(f"Tokenization complete, got {len(self.tokens)} tokens")

        # Filter out whitespace and comments
        self.tokens = [
            t
            for t in self.tokens
            if t.type not in (TokenType.WHITESPACE, TokenType.COMMENT)
        ]
        logger.debug(f"After filtering, {len(self.tokens)} tokens remain")

        # Build the AST
        try:
            logger.debug("Starting document parsing")
            document = self._parse_document()
            logger.debug("Document parsing complete")
            # Stability check: if a keymap block exists, it must have at least one layer
            if document.keymap is not None:
                logger.debug(
                    f"Parsed keymap block with {len(document.keymap.layers)} layers"
                )
                assert (
                    len(document.keymap.layers) > 0
                ), "Parsed keymap block has no layers (invalid or empty file)"
            return document
        except ParseError as e:
            self.errors.append(e)
            logger.error(f"Parse error: {e}")
            # Return partially constructed document for error recovery
            return ZMKDocument()
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {type(e).__name__}: {e}")
            raise

    def _peek(self, offset: int = 0) -> Token:
        """Peek at a token ahead in the stream."""
        if self.position + offset >= len(self.tokens):
            # Return EOF token if we're at the end
            return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", None)
        return self.tokens[self.position + offset]

    def _consume(self) -> Token:
        """Consume the current token and advance."""
        if self.position >= len(self.tokens):
            raise ParseError("Unexpected end of file")

        token = self.tokens[self.position]
        self.position += 1
        return token

    def _match(self, token_type: TokenType) -> Token:
        """Match the current token against the expected type."""
        token = self._peek()
        if token.type != token_type:
            raise ParseError(
                f"Expected {token_type.name}, got {token.type.name}", token.location
            )
        return self._consume()

    def _match_any(self, token_types: List[TokenType]) -> Token:
        """Match the current token against any of the expected types."""
        token = self._peek()
        if token.type not in token_types:
            expected = ", ".join(t.name for t in token_types)
            raise ParseError(
                f"Expected one of {expected}, got {token.type.name}", token.location
            )
        return self._consume()

    def _try_match(self, token_type: TokenType) -> Optional[Token]:
        """Try to match the current token against the expected type."""
        token = self._peek()
        if token.type != token_type:
            return None
        return self._consume()

    def _parse_document(self) -> ZMKDocument:
        """Parse a ZMK document."""
        document = ZMKDocument()

        # Match the opening / {
        logger.debug("Parsing document start")
        self._match(TokenType.SLASH)
        self._match(TokenType.OPEN_BRACE)

        # Parse blocks until we find the closing brace
        while self._peek().type != TokenType.CLOSE_BRACE:
            # Look ahead to see what kind of block we're parsing
            if self._peek().type == TokenType.KW_BEHAVIORS:
                logger.debug("Found behaviors block")
                document.behaviors = self._parse_behaviors_block()
            elif self._peek().type == TokenType.KW_KEYMAP:
                logger.debug("Found keymap block")
                document.keymap = self._parse_keymap_block()
            elif self._peek().type == TokenType.KW_MACROS:
                logger.debug("Found macros block")
                document.macros = self._parse_macros_block()
            elif (
                self._peek().type == TokenType.IDENTIFIER
                and self._peek().value == "combos"
            ):
                logger.debug("Found combos block")
                document.combos = self._parse_combos_block()
            elif (
                self._peek().type == TokenType.IDENTIFIER
                and self._peek().value == "conditional_layers"
            ):
                logger.debug("Found conditional_layers block")
                document.conditional_layers = self._parse_conditional_layers_block()
            elif self._peek().type == TokenType.EOF:
                raise ParseError("Unexpected end of file, expected closing brace")
            else:
                # Skip unknown block
                token = self._consume()
                self._warning(f"Skipping unknown block: {token.value}", token.location)
                self._skip_until(TokenType.SEMICOLON)

        # Match the closing }
        self._match(TokenType.CLOSE_BRACE)
        logger.debug("Document parsing complete")

        return document

    def _parse_behaviors_block(self) -> ZMKBehaviorsBlock:
        """Parse a behaviors block."""
        behaviors_block = ZMKBehaviorsBlock()

        # Match the behaviors {
        logger.debug("Parsing behaviors block")
        self._match(TokenType.KW_BEHAVIORS)
        self._match(TokenType.OPEN_BRACE)

        # Parse behavior definitions until we find the closing brace
        behavior_count = 0
        while self._peek().type != TokenType.CLOSE_BRACE:
            try:
                logger.debug(f"Parsing behavior definition #{behavior_count + 1}")
                # Parse a behavior definition (name: type { ... };)
                behavior_name = self._match(TokenType.IDENTIFIER).value
                logger.debug(f"Found behavior name: {behavior_name}")
                self._match(TokenType.COLON)

                # Parse behavior type (can be one or more identifiers)
                behavior_type = ""
                while self._peek().type != TokenType.OPEN_BRACE:
                    token = self._peek()
                    if token.type == TokenType.IDENTIFIER:
                        if behavior_type:
                            behavior_type += (
                                "_"  # Join multi-token types with underscore
                            )
                        behavior_type += self._consume().value
                    elif token.type == TokenType.EOF:
                        raise ParseError(
                            "Unexpected EOF while parsing behavior type", token.location
                        )
                    else:
                        # Allow skipping unexpected tokens before the brace, but warn
                        self._warning(
                            f"Unexpected token while parsing behavior type: {token.type.name}",
                            token.location,
                        )
                        self._consume()

                if not behavior_type:
                    raise ParseError(
                        "Missing behavior type before opening brace",
                        self._peek().location,
                    )

                logger.debug(f"Found behavior type: {behavior_type}")

                behavior = ZMKBehaviorDefinition(behavior_name, behavior_type)

                # Parse the behavior parameters block
                self._match(TokenType.OPEN_BRACE)

                # Parse parameters until we find the closing brace
                param_count = 0
                while self._peek().type != TokenType.CLOSE_BRACE:
                    if self._peek().type == TokenType.EOF:
                        raise ParseError(
                            "Unexpected end of file while parsing behavior parameters"
                        )

                    param_token = self._peek()
                    param_name = None
                    param_value = None
                    param_name_parts = []

                    # Check if parameter name is IDENTIFIER, KW_BINDINGS, or potentially other keywords
                    # Allow multi-token IDENTIFIER names joined by SUBTRACT
                    while self._peek().type not in (
                        TokenType.EQUALS,
                        TokenType.EOF,
                        TokenType.OPEN_BRACE,
                        TokenType.CLOSE_BRACE,
                        TokenType.SEMICOLON,
                    ):
                        token = self._consume()
                        if (
                            token.type == TokenType.IDENTIFIER
                            or token.type == TokenType.KW_BINDINGS
                        ):
                            # Use token value directly (works for IDENTIFIER and 'bindings')
                            param_name_parts.append(token.value)
                        elif token.type == TokenType.SUBTRACT:
                            # Keep hyphen if joining identifiers, ignore if leading/trailing/double
                            if (
                                param_name_parts
                                and self._peek().type == TokenType.IDENTIFIER
                            ):
                                param_name_parts.append("-")
                        elif token.type in (TokenType.COMMENT, TokenType.WHITESPACE):
                            pass  # Ignore whitespace/comments between parts
                        else:
                            # Unexpected token within the parameter name part
                            raise ParseError(
                                f"Unexpected token '{token.value}' ({token.type.name}) while parsing parameter name",
                                token.location,
                            )

                    if not param_name_parts:
                        # If we didn't find any name parts but didn't hit EOF/Braces etc.
                        if param_token.type in (
                            TokenType.COMMENT,
                            TokenType.WHITESPACE,
                        ):
                            self._consume()  # Consume the whitespace/comment
                            continue  # Skip to next iteration
                        raise ParseError(
                            f"Expected parameter name, got {param_token.type.name}",
                            param_token.location,
                        )

                    param_name = "".join(param_name_parts)
                    logger.debug(
                        f"Parsing behavior parameter #{param_count + 1}: {param_name}"
                    )

                    self._match(TokenType.EQUALS)

                    # Value parsing logic (remains the same for now)
                    # TODO: Potentially refactor value parsing based on param_name if needed
                    if self._peek().type == TokenType.STRING:
                        param_value = self._match(TokenType.STRING).value
                    elif self._peek().type == TokenType.NUMBER:
                        param_value = self._match(TokenType.NUMBER).value
                    elif self._peek().type == TokenType.OPEN_ANGLE:
                        # Note: _parse_simple_angle_bracket_parameter returns raw string including <>
                        param_value = self._parse_simple_angle_bracket_parameter()
                    else:
                        param_value = self._match(TokenType.IDENTIFIER).value
                    logger.debug(f"Parsed value: {param_value}")

                    # Add the parameter if successfully parsed
                    if param_name is not None and param_value is not None:
                        behavior.parameters.append(
                            ZMKParameter(param_name, param_value)
                        )
                        param_count += 1
                        self._match(TokenType.SEMICOLON)
                    else:
                        # This case should ideally not be reached if error/skip logic is correct
                        self._warning(
                            f"Failed to parse parameter value starting near {param_token.location}"
                        )
                        self._skip_until(TokenType.SEMICOLON)  # Attempt to recover

                # Match the closing brace and semicolon
                self._match(TokenType.CLOSE_BRACE)
                self._match(TokenType.SEMICOLON)

                # Add the behavior to the block
                behaviors_block.behaviors[behavior_name] = behavior
                behavior_count += 1
                logger.debug(f"Successfully parsed behavior: {behavior_name}")

            except ParseError as e:
                self.errors.append(e)
                logger.error(f"Error parsing behavior definition: {e}")
                self._recover_to_next_definition()

        # Match the closing brace
        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.debug(
            f"Behaviors block parsing complete, found {behavior_count} behaviors"
        )

        return behaviors_block

    def _parse_simple_angle_bracket_parameter(self) -> str:
        """Parse a parameter enclosed in angle brackets like <&kp> using a simpler non-recursive approach."""
        start_position = self.position
        logger.debug(
            f"Starting angle bracket parameter parsing at position {start_position}"
        )

        # Match the opening angle bracket
        self._match(TokenType.OPEN_ANGLE)

        # Count angle brackets to handle nesting
        open_count = 1
        close_count = 0

        # Simply capture everything until we find a matching closing bracket
        tokens_captured = []
        tokens_captured.append("<")  # Add the opening bracket

        # Set a max token limit to prevent infinite loops
        max_tokens = 100

        while open_count > close_count and len(tokens_captured) < max_tokens:
            if self._peek().type == TokenType.EOF:
                # Reset position and bail out on EOF
                self.position = start_position
                raise ParseError(
                    "Unexpected end of file while parsing angle bracket parameter"
                )

            token = self._peek()

            if token.type == TokenType.OPEN_ANGLE:
                open_count += 1
            elif token.type == TokenType.CLOSE_ANGLE:
                close_count += 1

            # Consume the token
            tokens_captured.append(self._consume().value)

            # Break if we've matched all opening brackets
            if open_count == close_count:
                break

        # Check if we've hit the token limit
        if len(tokens_captured) >= max_tokens:
            # Reset position and bail out
            self.position = start_position
            logger.error(
                f"Too many tokens ({len(tokens_captured)}) in angle bracket parameter"
            )
            raise ParseError(
                "Too many tokens in angle bracket parameter, possible infinite loop",
                self._peek().location,
            )

        # Join all the token values to form the complete parameter
        param_value = "".join(tokens_captured)

        logger.debug(f"Successfully parsed angle bracket parameter: {param_value}")
        return param_value

    def _parse_keymap_block(self) -> ZMKKeymapBlock:
        """Parse a keymap block."""
        keymap_block = ZMKKeymapBlock()

        # Match the keymap {
        logger.debug("Parsing keymap block")
        self._match(TokenType.KW_KEYMAP)
        self._match(TokenType.OPEN_BRACE)

        # Match the compatible = "zmk,keymap";
        self._match(TokenType.KW_COMPATIBLE)
        self._match(TokenType.EQUALS)
        self._match(TokenType.STRING)
        self._match(TokenType.SEMICOLON)

        # Parse layer definitions until we find the closing brace
        layer_count = 0
        while self._peek().type != TokenType.CLOSE_BRACE:
            try:
                logger.debug(
                    f"Parsing layer definition #{layer_count + 1} at token {self._peek().location}"
                )
                # Parse a layer definition (name_layer { ... };)
                layer_name = ""

                # The layer name can be split across multiple tokens
                while True:
                    token = self._peek()
                    if token.type == TokenType.IDENTIFIER:
                        if layer_name:
                            layer_name += "_"
                        layer_name += self._consume().value
                    elif token.type == TokenType.OPEN_BRACE:
                        break
                    else:
                        raise ParseError(
                            f"Unexpected token in layer name: {token.type.name}",
                            token.location,
                        )

                logger.info(f"Found layer name: {layer_name} at token {token.location}")
                logger.info(f"Starting layer: {layer_name}")
                layer = ZMKLayerDefinition(layer_name)

                # Parse the layer bindings block
                self._match(TokenType.OPEN_BRACE)

                # Parse the bindings = <...>;
                self._match(TokenType.KW_BINDINGS)
                self._match(TokenType.EQUALS)

                # Parse bindings within the angle brackets
                self._match(TokenType.OPEN_ANGLE)  # Consume the opening <

                binding_count = 0
                while self._peek().type != TokenType.CLOSE_ANGLE:
                    if self._peek().type == TokenType.EOF:
                        raise ParseError(
                            "Unexpected end of file while parsing bindings"
                        )

                    # Parse a binding &behavior param1 param2...
                    if self._peek().type == TokenType.AMPERSAND:
                        logger.debug(
                            f"Parsing binding #{binding_count + 1} in layer '{layer_name}' at token {self._peek().location}"
                        )
                        binding = (
                            self._parse_binding()
                        )  # Use self._parse_binding directly
                        if hasattr(binding, "validate") and not binding.validate():
                            msg = f"Skipping invalid binding: {binding} in layer '{layer_name}' at token {self._peek().location}"
                            logger.warning(msg)
                            self.warnings.append(ParseError(msg, self._peek().location))
                        else:
                            layer.bindings.append(binding)
                            logger.info(
                                f"Added binding to layer '{layer_name}': {binding}"
                            )
                            binding_count += 1
                    else:
                        # Skip non-binding tokens (e.g., whitespace, comments) within the < >
                        skipped_token = self._consume()
                        msg = f"Skipped non-binding token '{skipped_token.value}' of type {skipped_token.type.name} in layer '{layer_name}' at {skipped_token.location}"
                        logger.debug(msg)

                self._match(TokenType.CLOSE_ANGLE)  # Consume the closing >

                # Match the semicolon
                self._match(TokenType.SEMICOLON)

                # Match the closing brace and semicolon
                self._match(TokenType.CLOSE_BRACE)
                self._match(TokenType.SEMICOLON)

                # Add the layer to the keymap
                logger.info(
                    f"Finishing layer: {layer_name} with {binding_count} bindings"
                )
                keymap_block.layers[layer_name] = layer
                logger.info(f"Added layer '{layer_name}' to keymap block")
                layer_count += 1
                logger.debug(
                    f"Successfully parsed layer: {layer_name} with {binding_count} bindings"
                )

            except ParseError as e:
                self.errors.append(e)
                logger.error(f"Error parsing layer definition: {e}")
                self._recover_to_next_definition()

        # Match the closing brace and semicolon
        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.info(f"Keymap block parsing complete, found {layer_count} layers")
        logger.info(f"Final list of layers: {list(keymap_block.layers.keys())}")
        for lname, layer in keymap_block.layers.items():
            logger.info(
                f"Layer '{lname}' has {len(layer.bindings)} bindings: {[str(b) for b in layer.bindings]}"
            )

        return keymap_block

    def _parse_binding(self) -> ZMKBinding:
        """Parse a binding like &kp A or &mt LSHFT A."""
        # Match the & prefix and behavior name
        self._match(TokenType.AMPERSAND)
        behavior_name = self._match(TokenType.IDENTIFIER).value
        logger.debug(f"Found binding behavior: {behavior_name}")

        binding = ZMKBinding(behavior_name)

        # Parse parameters until we find another binding or the end
        param_count = 0
        max_params = 20  # Safety limit
        while (
            self._peek().type not in (TokenType.AMPERSAND, TokenType.CLOSE_ANGLE)
            and param_count < max_params
        ):
            if self._peek().type == TokenType.EOF:
                break

            logger.debug(f"Parsing binding parameter #{param_count + 1}")
            binding_param = self._parse_binding_parameter()
            binding.params.append(binding_param)
            param_count += 1

        if param_count >= max_params:
            logger.warning(
                f"Reached maximum parameter limit ({max_params}) for binding {behavior_name}"
            )

        logger.debug(
            f"Successfully parsed binding: {behavior_name} with {param_count} parameters"
        )
        return binding

    def _parse_binding_parameter(self) -> ZMKBindingParameter:
        """Parse a binding parameter, which can be a simple identifier, number, or a complex expression."""
        token = self._peek()

        # Check for a complex expression with parentheses like LC(LS(LALT))
        if (
            token.type == TokenType.IDENTIFIER
            and self._peek(1).type == TokenType.OPEN_PAREN
        ):
            logger.debug(
                f"Parsing complex modifier expression starting with {token.value}"
            )
            modifier_expr = self._parse_modifier_expression()
            return ZMKBindingParameter(modifier_expr, token.location)

        # Check for simple identifier or number parameters
        elif token.type in (TokenType.IDENTIFIER, TokenType.NUMBER):
            value = self._consume().value
            logger.debug(f"Found simple binding parameter: {value} ({token.type.name})")
            return ZMKBindingParameter(value, token.location)

        # Unexpected token type for a parameter
        else:
            raise ParseError(
                f"Unexpected token type for binding parameter: {token.type.name}",
                token.location,
            )

    def _parse_modifier_expression(self) -> ZMKModifierExpression:
        """Parse a complex modifier expression like LC(LS(LALT))."""
        # Parse the modifier name
        modifier = self._match(TokenType.IDENTIFIER).value
        logger.debug(f"Parsing modifier expression with modifier: {modifier}")

        # Match the opening parenthesis
        self._match(TokenType.OPEN_PAREN)

        # Parse the parameters
        params = []

        # Handle empty parameters case
        if self._peek().type == TokenType.CLOSE_PAREN:
            self._match(TokenType.CLOSE_PAREN)
            logger.debug(f"Empty modifier expression: {modifier}()")
            return ZMKModifierExpression(modifier, params)

        # Safety counter
        param_count = 0
        max_params = 10

        while param_count < max_params:
            # Check for nested expression
            if (
                self._peek().type == TokenType.IDENTIFIER
                and self._peek(1).type == TokenType.OPEN_PAREN
            ):
                logger.debug(
                    f"Found nested modifier expression in parameter #{param_count + 1}"
                )
                nested_expr = self._parse_modifier_expression()
                params.append(nested_expr)
            else:
                # Simple parameter
                param = self._consume().value
                logger.debug(f"Found simple parameter: {param}")
                params.append(param)

            param_count += 1

            # Check if we're at the end of the parameters
            if self._peek().type == TokenType.CLOSE_PAREN:
                break

            # Match comma if we expect more parameters
            self._match(TokenType.COMMA)

            # Check for end after comma (trailing comma case)
            if self._peek().type == TokenType.CLOSE_PAREN:
                break

        # Match the closing parenthesis
        self._match(TokenType.CLOSE_PAREN)

        logger.debug(
            f"Successfully parsed modifier expression: {modifier} with {param_count} parameters"
        )
        return ZMKModifierExpression(modifier, params)

    def _parse_macros_block(self) -> ZMKMacrosBlock:
        """Parse a macros block."""
        macros_block = ZMKMacrosBlock()

        # Match the macros {
        logger.debug("Parsing macros block")
        self._match(TokenType.KW_MACROS)
        self._match(TokenType.OPEN_BRACE)

        # Parse macro definitions until we find the closing brace
        macro_count = 0
        while self._peek().type != TokenType.CLOSE_BRACE:
            try:
                logger.debug(f"Parsing macro definition #{macro_count + 1}")
                # Parse a macro definition (name: macro { ... };)
                macro_name = self._match(TokenType.IDENTIFIER).value
                logger.debug(f"Found macro name: {macro_name}")
                self._match(TokenType.COLON)

                # Verify this is a macro
                if (
                    self._peek().type != TokenType.IDENTIFIER
                    or self._peek().value != "macro"
                ):
                    raise ParseError(
                        f"Expected 'macro', got {self._peek().value}",
                        self._peek().location,
                    )
                self._consume()  # Consume 'macro'

                macro = ZMKMacroDefinition(macro_name)

                # Parse the macro definition block
                self._match(TokenType.OPEN_BRACE)

                # Parse parameters until we find the closing brace
                param_parsed_successfully = True
                while self._peek().type != TokenType.CLOSE_BRACE:
                    if not param_parsed_successfully:
                        self._skip_until(TokenType.SEMICOLON)
                        if self._peek().type == TokenType.CLOSE_BRACE:
                            break
                    param_parsed_successfully = False  # Reset

                    if self._peek().type == TokenType.EOF:
                        raise ParseError(
                            "Unexpected end of file while parsing macro definition"
                        )

                    param_token = self._peek()
                    param_handled = False  # Flag to check if parameter was processed

                    # Check parameter name token type
                    # Macro params can be IDENTIFIER, KW_LABEL, KW_COMPATIBLE, or KW_BINDINGS
                    accepted_param_types = (
                        TokenType.IDENTIFIER,
                        TokenType.KW_BINDINGS,
                        TokenType.KW_LABEL,
                        TokenType.KW_COMPATIBLE,
                    )
                    if param_token.type in accepted_param_types:
                        param_name = (
                            self._consume().value
                        )  # Consume IDENTIFIER, 'bindings', 'label', or 'compatible'

                        # Check for EQUALS sign immediately after name
                        if self._peek().type != TokenType.EQUALS:
                            self._warning(
                                f"Expected '=' after macro parameter '{param_name}', got {self._peek().type.name}",
                                self._peek().location,
                            )
                            # Attempt to recover by skipping to semicolon
                            continue  # Let outer loop handle skipping
                        self._match(TokenType.EQUALS)

                        logger.debug(f"Parsing macro parameter: {param_name}")

                        try:
                            # Use the token type to determine the parameter if name is keyword
                            actual_param_name = (
                                param_name
                                if param_token.type == TokenType.IDENTIFIER
                                else param_token.type.name.lower().replace("kw_", "")
                            )

                            if actual_param_name == "label":
                                # Get string value *without* quotes
                                string_token = self._match(TokenType.STRING)
                                macro.label = (
                                    string_token.value[1:-1]
                                    if len(string_token.value) >= 2
                                    else ""
                                )
                                logger.debug(f"Parsed macro label: {macro.label}")
                                param_handled = True
                            elif actual_param_name == "compatible":
                                # Get string value *without* quotes
                                string_token = self._match(TokenType.STRING)
                                macro.compatible = (
                                    string_token.value[1:-1]
                                    if len(string_token.value) >= 2
                                    else ""
                                )
                                logger.debug(
                                    f"Parsed macro compatible: {macro.compatible}"
                                )
                                param_handled = True
                            elif actual_param_name == "bindings":
                                # Parse macro steps directly from token stream
                                self._match(TokenType.OPEN_ANGLE)
                                step_count = 0
                                while self._peek().type != TokenType.CLOSE_ANGLE:
                                    if self._peek().type == TokenType.EOF:
                                        raise ParseError(
                                            "Unexpected end of file while parsing macro steps"
                                        )
                                    if self._peek().type == TokenType.AMPERSAND:
                                        step = self._parse_macro_step()
                                        macro.steps.append(step)
                                        step_count += 1
                                    else:
                                        self._consume()  # Skip non-step tokens
                                self._match(TokenType.CLOSE_ANGLE)
                                logger.debug(f"Found {step_count} macro steps")
                                param_handled = True
                            else:
                                # Unknown IDENTIFIER parameter name
                                self._warning(
                                    f"Skipping unknown parameter in macro: {param_name}",
                                    param_token.location,
                                )
                                # Let outer loop skip value until semicolon
                                pass  # Fall through to param_handled check

                            if param_handled:
                                self._match(TokenType.SEMICOLON)
                                param_parsed_successfully = True

                        except ParseError as e:
                            self.errors.append(
                                ParseError(
                                    f"Error parsing macro parameter '{param_name}': {e.message}",
                                    e.location,
                                )
                            )
                            logger.error(
                                f"Error parsing macro parameter '{param_name}': {e}"
                            )
                            # param_parsed_successfully remains False, outer loop will skip

                    elif param_token.type in (TokenType.WHITESPACE, TokenType.COMMENT):
                        self._consume()  # Skip whitespace/comments
                        param_parsed_successfully = (
                            True  # Still considered successful for skipping
                        )
                        continue  # Go to next token
                    else:
                        # Unexpected token where parameter name was expected
                        expected_names = ", ".join(t.name for t in accepted_param_types)
                        self._warning(
                            f"Skipping unexpected token ({param_token.type.name}) in macro definition, expected {expected_names}",
                            param_token.location,
                        )
                        # param_parsed_successfully remains False, outer loop will skip

                # Match the closing brace and semicolon
                self._match(TokenType.CLOSE_BRACE)
                self._match(TokenType.SEMICOLON)

                # Add the macro to the block
                macros_block.macros[macro_name] = macro
                macro_count += 1
                logger.debug(f"Successfully parsed macro: {macro_name}")

            except ParseError as e:
                self.errors.append(e)
                logger.error(f"Error parsing macro definition: {e}")
                self._recover_to_next_definition()

        # Match the closing brace and semicolon
        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.debug(f"Macros block parsing complete, found {macro_count} macros")

        return macros_block

    def _parse_macro_step(self) -> ZMKMacroStep:
        """Parse a macro step like &kp A."""
        # Match the & prefix
        self._match(TokenType.AMPERSAND)

        # Parse the action (kp, macro_tap, macro_press, macro_release, etc.)
        action = self._match(TokenType.IDENTIFIER).value

        # Parse the parameter if present
        param = None
        if self._peek().type not in (TokenType.AMPERSAND, TokenType.CLOSE_ANGLE):
            param = self._consume().value

        logger.debug(f"Parsed macro step: &{action}{' ' + param if param else ''}")
        return ZMKMacroStep(action, param)

    def _parse_combos_block(self) -> ZMKCombosBlock:
        """Parse a combos block."""
        combos_block = ZMKCombosBlock()

        # Match the combos {
        logger.debug("Parsing combos block")
        start_loc = self._peek().location  # Location for error reporting
        self._match(TokenType.IDENTIFIER)  # 'combos'
        self._match(TokenType.OPEN_BRACE)

        # Match the compatible = "zmk,combos";
        try:
            self._match(TokenType.KW_COMPATIBLE)
            self._match(TokenType.EQUALS)
            # TODO: Maybe validate string content == "zmk,combos"?
            self._match(TokenType.STRING)
            self._match(TokenType.SEMICOLON)
        except ParseError as e:
            # Allow parsing to continue if compatible line is missing/malformed, but log error
            self.errors.append(
                ParseError(
                    f"Error parsing 'compatible' line in combos block: {e.message}",
                    e.location,
                )
            )
            logger.error(f"Error parsing 'compatible' line in combos block: {e}")
            # Attempt recovery: skip until we likely find the start of a combo def or the end brace
            while self._peek().type not in (
                TokenType.IDENTIFIER,
                TokenType.CLOSE_BRACE,
                TokenType.EOF,
            ):
                self._consume()

        # Parse combo definitions until closing brace
        combo_count = 0
        while self._peek().type != TokenType.CLOSE_BRACE:
            if self._peek().type == TokenType.EOF:
                raise ParseError("Unexpected EOF while parsing combos block", start_loc)

            if self._peek().type == TokenType.IDENTIFIER:
                try:
                    logger.debug(f"Parsing combo definition #{combo_count + 1}")
                    combo_def = self._parse_combo_definition()
                    # TODO: Check for duplicate combo names?
                    combos_block.combos[combo_def.name] = combo_def
                    combo_count += 1
                except ParseError as e:
                    self.errors.append(e)
                    logger.error(f"Error parsing combo definition: {e}")
                    self._recover_to_next_definition()  # Reuse recovery logic
            else:
                # Skip unexpected tokens (e.g., comments, extra semicolons) until the next potential definition or end brace
                token = self._consume()
                # Avoid warning for comments/whitespace if they were filtered out
                if token.type not in (TokenType.WHITESPACE, TokenType.COMMENT):
                    self._warning(
                        f"Skipping unexpected token in combos block: {token.value}",
                        token.location,
                    )

        # Match the closing brace and semicolon
        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.debug(f"Combos block parsing complete, found {combo_count} combos")

        return combos_block

    def _parse_combo_definition(self) -> ZMKComboDefinition:
        """Parse a single combo definition like my_combo { ... };"""
        combo_name = self._match(TokenType.IDENTIFIER).value
        start_loc = self._peek().location  # Location for error reporting
        logger.debug(f"Parsing combo definition: {combo_name}")
        self._match(TokenType.OPEN_BRACE)

        # TODO: Update ZMKComboDefinition in zmk_ast.py with these fields
        combo = ZMKComboDefinition(combo_name)
        combo.timeout_ms = 0  # Default values
        combo.key_positions = []
        combo.bindings = []
        combo.layers = []

        # Parse parameters until closing brace
        param_parsed_successfully = (
            True  # Flag to track if the last parameter was parsed/skipped okay
        )
        while self._peek().type != TokenType.CLOSE_BRACE:
            if not param_parsed_successfully:
                # If the last attempt failed, skip until the next likely parameter start or end brace
                self._skip_until(TokenType.SEMICOLON)
                # Now check if we landed on the closing brace after skipping
                if self._peek().type == TokenType.CLOSE_BRACE:
                    break
            param_parsed_successfully = False  # Reset flag for this iteration

            if self._peek().type == TokenType.EOF:
                raise ParseError(
                    "Unexpected EOF while parsing combo definition parameters",
                    start_loc,
                )

            param_name_token = self._peek()
            param_name = None

            # Check if parameter name is IDENTIFIER, KW_BINDINGS, or KW_LAYERS
            accepted_param_types = (
                TokenType.IDENTIFIER,
                TokenType.KW_BINDINGS,
                TokenType.KW_LAYERS,
            )
            if param_name_token.type in accepted_param_types:
                param_name = (
                    self._consume().value
                )  # Consume IDENTIFIER, 'bindings', or 'layers'
            elif param_name_token.type in (TokenType.COMMENT, TokenType.WHITESPACE):
                self._consume()
                param_parsed_successfully = (
                    True  # Skipped comment/whitespace successfully
                )
                continue  # Skip to next token
            else:
                # Unexpected token where parameter name was expected
                expected_names = ", ".join(t.name for t in accepted_param_types)
                self._warning(
                    f"Expected combo parameter name ({expected_names}), got {param_name_token.type.name}",
                    param_name_token.location,
                )
                # No need to raise, attempt recovery by skipping in the next loop iteration
                continue

            # If we got a name, proceed to parse value
            self._match(TokenType.EQUALS)
            logger.debug(f"Parsing combo parameter: {param_name}")

            # Parse specific parameters
            try:
                if param_name == "timeout-ms":
                    combo.timeout_ms = self._parse_angle_bracket_number()
                    logger.debug(f"Parsed timeout-ms: {combo.timeout_ms}")
                elif param_name == "key-positions":
                    combo.key_positions = self._parse_angle_bracket_number_list()
                    logger.debug(f"Parsed key-positions: {combo.key_positions}")
                elif param_name == "bindings":
                    combo.bindings = self._parse_angle_bracket_bindings()
                    logger.debug(f"Parsed bindings: {len(combo.bindings)} binding(s)")
                elif param_name == "layers":
                    combo.layers = self._parse_angle_bracket_number_list()
                    logger.debug(f"Parsed layers: {combo.layers}")
                else:
                    # Unknown parameter, skip its value
                    self._warning(
                        f"Skipping unknown combo parameter: {param_name}",
                        param_name_token.location,
                    )
                    # Assuming value is <...> or simple value; skip until semicolon
                    # Let the outer loop handle skipping via param_parsed_successfully = False
                    pass  # Mark as handled for try/except

                self._match(TokenType.SEMICOLON)
                param_parsed_successfully = True  # Parameter parsed successfully

            except ParseError as e:
                # Log error and attempt recovery in the next loop iteration
                self.errors.append(
                    ParseError(
                        f"Error parsing combo parameter '{param_name}': {e.message}",
                        e.location,
                    )
                )
                logger.error(f"Error parsing combo parameter '{param_name}': {e}")
                # param_parsed_successfully remains False, outer loop will skip

        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.debug(f"Successfully parsed combo: {combo_name}")
        return combo

    # --- Start: Combo Parsing Helpers ---
    def _parse_angle_bracket_number(self) -> int:
        """Parses a single number within angle brackets like <50>."""
        self._match(TokenType.OPEN_ANGLE)
        # TODO: Add check for non-numeric value if needed
        value = int(self._match(TokenType.NUMBER).value)
        self._match(TokenType.CLOSE_ANGLE)
        logger.debug(f"Parsed angle bracket number: {value}")
        return value

    def _parse_angle_bracket_number_list(self) -> List[int]:
        """Parses a list of numbers within angle brackets like <0 1>."""
        self._match(TokenType.OPEN_ANGLE)
        numbers = []
        while self._peek().type != TokenType.CLOSE_ANGLE:
            if self._peek().type == TokenType.NUMBER:
                numbers.append(int(self._consume().value))
            elif self._peek().type == TokenType.EOF:
                raise ParseError(
                    "Unexpected EOF in angle bracket number list", self._peek().location
                )
            else:  # Skip other tokens like whitespace, assuming they are separators
                self._consume()
        self._match(TokenType.CLOSE_ANGLE)
        logger.debug(f"Parsed angle bracket number list: {numbers}")
        return numbers

    def _parse_angle_bracket_bindings(self) -> List[ZMKBinding]:
        """Parses one or more bindings within angle brackets like <&kp ENTER>."""
        self._match(TokenType.OPEN_ANGLE)
        bindings = []
        binding_count = 0
        while self._peek().type != TokenType.CLOSE_ANGLE:
            if self._peek().type == TokenType.AMPERSAND:
                logger.debug(f"Parsing angle bracket binding #{binding_count + 1}")
                bindings.append(self._parse_binding())
                binding_count += 1
            elif self._peek().type == TokenType.EOF:
                raise ParseError(
                    "Unexpected EOF in angle bracket bindings", self._peek().location
                )
            else:  # Skip other tokens like whitespace
                self._consume()
        self._match(TokenType.CLOSE_ANGLE)
        logger.debug(f"Parsed {binding_count} angle bracket bindings: {bindings}")
        return bindings

    # --- End: Combo Parsing Helpers ---

    # --- Start: Conditional Layer Parsing Helper ---
    def _parse_conditional_layer_definition(self) -> ZMKConditionalLayerDefinition:
        """Parse a single conditional layer definition like tri_layer { ... };"""
        layer_name = self._match(TokenType.IDENTIFIER).value
        start_loc = self._peek().location  # Location for error reporting
        logger.debug(f"Parsing conditional layer definition: {layer_name}")
        self._match(TokenType.OPEN_BRACE)

        # TODO: Update ZMKConditionalLayerDefinition in zmk_ast.py with these fields
        cond_layer = ZMKConditionalLayerDefinition(layer_name)
        cond_layer.if_layers = []  # Default values
        cond_layer.then_layer = -1  # Use -1 or similar to indicate not set

        # Parse parameters until closing brace
        while self._peek().type != TokenType.CLOSE_BRACE:
            if self._peek().type == TokenType.EOF:
                raise ParseError(
                    "Unexpected EOF while parsing conditional layer parameters",
                    start_loc,
                )

            param_name_token = self._peek()
            if param_name_token.type != TokenType.IDENTIFIER:
                if param_name_token.type in (TokenType.COMMENT, TokenType.WHITESPACE):
                    self._consume()
                    continue
                raise ParseError(
                    f"Expected conditional layer parameter name (IDENTIFIER), got {param_name_token.type.name}",
                    param_name_token.location,
                )

            param_name = self._consume().value
            self._match(TokenType.EQUALS)

            # Parse specific parameters
            try:
                if param_name == "if-layers":
                    cond_layer.if_layers = self._parse_angle_bracket_number_list()
                    logger.debug(f"Parsed if-layers: {cond_layer.if_layers}")
                elif param_name == "then-layer":
                    # then-layer expects a single number inside < >
                    cond_layer.then_layer = self._parse_angle_bracket_number()
                    logger.debug(f"Parsed then-layer: {cond_layer.then_layer}")
                else:
                    self._warning(
                        f"Skipping unknown conditional layer parameter: {param_name}",
                        param_name_token.location,
                    )
                    self._skip_until(TokenType.SEMICOLON)
                    continue

            except ParseError as e:
                self.errors.append(
                    ParseError(
                        f"Error parsing conditional layer parameter '{param_name}': {e.message}",
                        e.location,
                    )
                )
                logger.error(
                    f"Error parsing conditional layer parameter '{param_name}': {e}"
                )
                self._skip_until(TokenType.SEMICOLON)
                continue

            self._match(TokenType.SEMICOLON)

        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.debug(f"Successfully parsed conditional layer: {layer_name}")
        return cond_layer

    # --- End: Conditional Layer Parsing Helper ---

    def _parse_conditional_layers_block(self) -> ZMKConditionalLayersBlock:
        """Parse a conditional_layers block."""
        conditional_layers_block = ZMKConditionalLayersBlock()

        # Match the conditional_layers {
        logger.debug("Parsing conditional_layers block")
        start_loc = self._peek().location  # Location for error reporting
        self._match(TokenType.IDENTIFIER)  # 'conditional_layers'
        self._match(TokenType.OPEN_BRACE)

        # Match the compatible = "zmk,conditional-layers";
        try:
            self._match(TokenType.KW_COMPATIBLE)
            self._match(TokenType.EQUALS)
            # TODO: Maybe validate string content == "zmk,conditional-layers"?
            self._match(TokenType.STRING)
            self._match(TokenType.SEMICOLON)
        except ParseError as e:
            self.errors.append(
                ParseError(
                    f"Error parsing 'compatible' line in conditional_layers block: {e.message}",
                    e.location,
                )
            )
            logger.error(
                f"Error parsing 'compatible' line in conditional_layers block: {e}"
            )
            while self._peek().type not in (
                TokenType.IDENTIFIER,
                TokenType.CLOSE_BRACE,
                TokenType.EOF,
            ):
                self._consume()

        # Parse conditional layer definitions until closing brace
        layer_count = 0
        while self._peek().type != TokenType.CLOSE_BRACE:
            if self._peek().type == TokenType.EOF:
                raise ParseError(
                    "Unexpected EOF while parsing conditional_layers block", start_loc
                )

            if self._peek().type == TokenType.IDENTIFIER:
                try:
                    logger.debug(
                        f"Parsing conditional layer definition #{layer_count + 1}"
                    )
                    cond_layer_def = self._parse_conditional_layer_definition()
                    # TODO: Check for duplicate names?
                    conditional_layers_block.conditional_layers[cond_layer_def.name] = (
                        cond_layer_def
                    )
                    layer_count += 1
                except ParseError as e:
                    self.errors.append(e)
                    logger.error(f"Error parsing conditional layer definition: {e}")
                    self._recover_to_next_definition()  # Reuse recovery logic
            else:
                token = self._consume()
                if token.type not in (TokenType.WHITESPACE, TokenType.COMMENT):
                    self._warning(
                        f"Skipping unexpected token in conditional_layers block: {token.value}",
                        token.location,
                    )

        # Match the closing brace and semicolon
        self._match(TokenType.CLOSE_BRACE)
        self._match(TokenType.SEMICOLON)
        logger.debug(
            f"Conditional_layers block parsing complete, found {layer_count} conditional layers"
        )

        return conditional_layers_block

    def _skip_until(self, token_type: TokenType) -> None:
        """Skip tokens until we find the specified token type."""
        # Safety counter to prevent infinite loops
        max_tokens = 10000
        tokens_skipped = 0

        logger.debug(f"Skipping tokens until {token_type.name}")

        while (
            self._peek().type != token_type
            and self._peek().type != TokenType.EOF
            and tokens_skipped < max_tokens
        ):
            self._consume()
            tokens_skipped += 1

            if tokens_skipped % 1000 == 0:
                logger.debug(f"Skipped {tokens_skipped} tokens so far")

        if tokens_skipped >= max_tokens:
            logger.warning("Skip limit reached, may indicate an infinite loop")

        # Consume the target token if we found it
        if self._peek().type == token_type:
            self._consume()

        logger.debug(f"Skipped {tokens_skipped} tokens total")

    def _skip_balanced_braces(self) -> None:
        """Skip tokens, keeping track of nested braces, until we find the matching closing brace."""
        depth = 1  # We're already inside a brace

        # Safety counter to prevent infinite loops
        max_tokens = 10000
        tokens_skipped = 0

        logger.debug("Skipping balanced braces")

        while (
            depth > 0
            and self._peek().type != TokenType.EOF
            and tokens_skipped < max_tokens
        ):
            token = self._consume()
            tokens_skipped += 1

            if token.type == TokenType.OPEN_BRACE:
                depth += 1
                logger.debug(f"Found opening brace, depth now {depth}")
            elif token.type == TokenType.CLOSE_BRACE:
                depth -= 1
                logger.debug(f"Found closing brace, depth now {depth}")

            if tokens_skipped % 1000 == 0:
                logger.debug(
                    f"Skipped {tokens_skipped} tokens so far in balanced braces"
                )

        if tokens_skipped >= max_tokens:
            logger.warning(
                "Skip limit reached during balanced brace skipping, may indicate an infinite loop"
            )

        # Consume the semicolon if present
        if self._peek().type == TokenType.SEMICOLON:
            self._consume()

        logger.debug(f"Skipped {tokens_skipped} tokens in balanced braces")

    def _recover_to_next_definition(self) -> None:
        """Recover to the start of the next definition.
        Attempts to find the start of a potential next definition (IDENTIFIER :)
        or the end of the current structure (}) to allow parsing to continue
        after an error within a block.
        """
        max_tokens = 5000
        tokens_skipped = 0

        logger.info(
            "Attempting recovery: Skipping until next definition start (IDENTIFIER :) or block end (}) ..."
        )

        while tokens_skipped < max_tokens:
            current_token = self._peek()

            if current_token.type == TokenType.EOF:
                logger.info("Recovery stopped at EOF.")
                break

            # Check for potential start of next definition (IDENTIFIER :) -> Don't consume
            if (
                current_token.type == TokenType.IDENTIFIER
                and self._peek(1).type == TokenType.COLON
            ):
                logger.info(
                    f"Found potential recovery point at IDENTIFIER COLON; skipped {tokens_skipped} tokens"
                )
                break

            # Check for end of current definition block (}) -> Don't consume
            if current_token.type == TokenType.CLOSE_BRACE:
                logger.info(
                    f"Found potential recovery point at CLOSE_BRACE; skipped {tokens_skipped} tokens"
                )
                break

            # Consume the current token if it's not a recovery point
            skipped_token = self._consume()
            tokens_skipped += 1
            logger.debug(
                f"Recovery: Skipped token '{skipped_token.value}' of type {skipped_token.type.name} at {skipped_token.location}"
            )

            if tokens_skipped % 1000 == 0:
                logger.info(f"Skipped {tokens_skipped} tokens so far during recovery")

        if tokens_skipped >= max_tokens:
            logger.warning("Recovery skip limit reached, may indicate an infinite loop")
        else:
            logger.info("Recovery finished.")

    def _warning(self, message: str, location: Optional[SourceLocation] = None) -> None:
        """Log a warning and add it to the warnings list."""
        warning = ParseError(message, location)
        self.warnings.append(warning)
        logger.warning(str(warning))

    def report_issues(self):
        """
        Print a grouped summary of all errors and warnings collected during parsing.
        Each entry includes context (line number, message, etc.).
        """
        if not self.errors and not self.warnings:
            print("No errors or warnings.")
            return
        if self.errors:
            print("\nERRORS:")
            for err in self.errors:
                print(f"  - {err.get_error_message()}")
        if self.warnings:
            print("\nWARNINGS:")
            for warn in self.warnings:
                print(f"  - {warn.get_error_message()}")
        print()
