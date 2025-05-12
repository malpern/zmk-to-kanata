"""DTS parser for converting DTS to keymap configuration."""

from typing import List, Any, Tuple, Optional
from .ast import DtsNode, DtsProperty, DtsRoot
from .error_handler import DtsParseError, format_error_context


class DtsParser:
    """Parser for DTS content."""

    def __init__(self):
        """Initialize parser."""
        self.tokens: List[str] = []
        self.pos = 0
        self.content: str = ""
        self.line_map: List[Tuple[int, int]] = []  # (line, column) for each token

    def parse(self, content: str, file: Optional[str] = None) -> DtsRoot:
        """Parse DTS content into an AST.

        Args:
            content: DTS content string
            file: Optional file path for error reporting

        Returns:
            DtsRoot object representing the parsed AST

        Raises:
            DtsParseError: If the content is not valid DTS
        """
        self.content = content
        self.tokens = []
        self.line_map = []
        self._tokenize(content)
        self.pos = 0

        # Check for root node token '/'
        if not self.tokens or self.tokens[0] != "/":
            raise DtsParseError(
                "DTS must start with root node '/'",
                file=file,
                line=1,
                column=1,
                context=format_error_context(content, 1, 1),
            )

        # The DtsParser will build up the tree starting from a DtsNode.
        # This node will represent the root of the DTS structure (e.g., '/').
        parsed_root_node = DtsNode(name="/")
        self.pos += 1  # Consume the '/' token

        # Expect '{' after root node '/'
        if self.pos >= len(self.tokens) or self.tokens[self.pos] != "{":
            line, col = self._get_pos_info(self.pos)
            raise DtsParseError(
                "Expected '{' after root node '/'",
                file=file,
                line=line,
                column=col,
                context=format_error_context(content, line, col),
            )
        self.pos += 1  # Consume '{'

        try:
            # Parse the body of the DTS, populating the parsed_root_node
            self._parse_node_body(parsed_root_node)

            # Once the DtsNode tree is built, create the DtsRoot wrapper.
            # DtsRoot's __init__ will handle copying necessary fields and
            # building the label map.
            ast_root = DtsRoot(root=parsed_root_node)

        except DtsParseError as e:
            if not e.file:
                e.file = file  # Ensure file is set on error
            raise

        return ast_root

    def _tokenize(self, content: str) -> None:
        """Tokenize DTS content and build line/column map.

        Args:
            content: DTS content string

        Raises:
            DtsParseError: If string or array is unterminated
        """
        # Remove comments first
        try:
            content = self._remove_comments(content)
        except Exception as e:
            raise DtsParseError(
                f"Failed to process comments: {str(e)}",
                context=format_error_context(content, 1, 1),
            )

        # Split on whitespace, but keep strings and arrays intact
        current = ""
        in_string = False
        array_stack = []  # Stack to track nested arrays
        line = 1
        column = 1

        i = 0
        while i < len(content):
            char = content[i]

            # Track line and column
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1

            if char == '"' and not array_stack:
                if not in_string:
                    if current.strip():
                        tokens = current.strip().split()
                        self.tokens.extend(tokens)
                        for _ in tokens:
                            self.line_map.append((line, column - len(current)))
                    current = char
                else:
                    current += char
                    self.tokens.append(current)
                    self.line_map.append((line, column - len(current)))
                    current = ""
                in_string = not in_string
                i += 1
            elif char == "<" and not in_string:
                if not array_stack:
                    if current.strip():
                        tokens = current.strip().split()
                        self.tokens.extend(tokens)
                        for _ in tokens:
                            self.line_map.append((line, column - len(current)))
                    current = ""
                array_stack.append((i, line, column))
                i += 1
            elif char == ">" and not in_string:
                if not array_stack:
                    raise DtsParseError(
                        "Unexpected '>'",
                        line=line,
                        column=column,
                        context=format_error_context(content, line, column),
                    )

                start_pos, start_line, start_col = array_stack.pop()
                if not array_stack:  # Only add token if this is the outermost array
                    array_content = content[start_pos : i + 1]
                    self.tokens.append(array_content)
                    self.line_map.append((start_line, start_col))
                i += 1
            elif char in "{};=:" and not (in_string or array_stack):
                if current.strip():
                    tokens = current.strip().split()
                    self.tokens.extend(tokens)
                    for _ in tokens:
                        self.line_map.append((line, column - len(current)))
                self.tokens.append(char)
                self.line_map.append((line, column))
                current = ""
                i += 1
            else:
                if not array_stack:
                    current += char
                i += 1

        if in_string:
            raise DtsParseError(
                "Unterminated string",
                line=line,
                column=column,
                context=format_error_context(content, line, column),
            )

        if array_stack:
            start_line, start_col = array_stack[-1][1:]
            raise DtsParseError(
                "Unterminated array",
                line=start_line,
                column=start_col,
                context=format_error_context(content, start_line, start_col),
            )

        if current.strip():
            tokens = current.strip().split()
            self.tokens.extend(tokens)
            for _ in tokens:
                self.line_map.append((line, column - len(current)))
        # print(f"Generated tokens: {self.tokens}") # Temporary debug print (Reverted)

    def _get_pos_info(self, pos: int) -> Tuple[int, int]:
        """Get line and column information for a token position."""
        if pos < len(self.line_map):
            return self.line_map[pos]
        return self.line_map[-1] if self.line_map else (1, 1)

    def _remove_comments(self, content: str) -> str:
        """Remove comments from DTS content.

        Handles C-style block (/* ... */) and line (// ...) comments.

        Args:
            content: DTS content string

        Returns:
            Content with comments removed
        """
        # Simple state machine approach for comment removal
        result = []
        in_block_comment = False
        in_line_comment = False
        in_string = False
        prev_char = ""

        for char in content:
            if in_block_comment:
                if char == "/" and prev_char == "*":
                    in_block_comment = False
                    # Skip the trailing '/'
                # Keep prev_char up-to-date within comment
                prev_char = char
                continue

            if in_line_comment:
                if char == "\n":
                    in_line_comment = False
                    result.append(char)  # Keep newlines
                continue

            if char == "/" and prev_char == "/":
                in_line_comment = True
                result.pop()  # Remove the first '/'
                continue

            if char == "*" and prev_char == "/":
                in_block_comment = True
                result.pop()  # Remove the '/'
                continue

            if char == '"' and not in_block_comment and not in_line_comment:
                in_string = not in_string

            result.append(char)
            prev_char = char

        return "".join(result)

    def _parse_array_value(self, value: str) -> List[Any]:
        """Parse array value (e.g., '<&kp A 1 0x10>').

        Args:
            value: Array value string to parse

        Returns:
            List of parsed values (integers, strings keeping & prefix)

        Raises:
            DtsParseError: If array format is invalid
        """
        # Remove angle brackets
        if not value.startswith("<") or not value.endswith(">"):
            line, col = self._get_pos_info(self.pos)
            raise DtsParseError(
                "Invalid array value format",
                line=line,
                column=col,
                context=format_error_context(self.content, line, col),
                help_text="Array values must be enclosed in angle brackets: <value1 value2>",
            )
        value = value[1:-1].strip()

        # Handle empty array
        if not value:
            return []

        # Split on whitespace, but handle nested arrays
        values = []
        current = ""
        array_stack = []

        i = 0
        while i < len(value):
            char = value[i]

            if char == "<":
                array_stack.append(i)
                current += char
            elif char == ">":
                if not array_stack:
                    line, col = self._get_pos_info(self.pos)
                    raise DtsParseError(
                        "Unexpected '>' in array value",
                        line=line,
                        column=col + i,
                        context=format_error_context(self.content, line, col + i),
                    )
                array_stack.pop()
                current += char
                if not array_stack:  # End of nested array
                    if current.strip():
                        values.append(current.strip())
                    current = ""
            elif char.isspace() and not array_stack:
                if current.strip():
                    values.append(current.strip())
                current = ""
            else:
                current += char
            i += 1

        if array_stack:
            line, col = self._get_pos_info(self.pos)
            raise DtsParseError(
                "Unterminated nested array",
                line=line,
                column=col,
                context=format_error_context(self.content, line, col),
            )

        if current.strip():
            values.append(current.strip())

        # Convert values to appropriate types
        result = []
        for val in values:
            if val.startswith("0x"):
                try:
                    result.append(int(val, 16))
                except ValueError:
                    line, col = self._get_pos_info(self.pos)
                    raise DtsParseError(
                        f"Invalid hexadecimal value: {val}",
                        line=line,
                        column=col,
                        context=format_error_context(self.content, line, col),
                        help_text="Hexadecimal values must start with '0x' followed by valid hex digits",
                    )
            elif val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
                result.append(int(val))
            else:
                result.append(val)

        return result

    def _parse_property_value(self, name: str, value: str) -> DtsProperty:
        """Parse a property value into a DtsProperty object.

        Args:
            name: Property name
            value: Property value string

        Returns:
            DtsProperty object

        Raises:
            DtsParseError: If property value format is invalid
        """
        if value.startswith("<"):
            try:
                values = self._parse_array_value(value)
                return DtsProperty(name=name, value=values, type="array")
            except DtsParseError as e:
                if not e.help_text:
                    e.help_text = "Array values must be enclosed in angle brackets and contain valid elements"
                raise
        elif value.startswith('"') and value.endswith('"'):
            return DtsProperty(name=name, value=value[1:-1], type="string")
        elif value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            return DtsProperty(name=name, value=int(value), type="integer")
        elif value.startswith("0x"):
            try:
                return DtsProperty(name=name, value=int(value, 16), type="integer")
            except ValueError:
                line, col = self._get_pos_info(self.pos)
                raise DtsParseError(
                    f"Invalid hexadecimal value: {value}",
                    line=line,
                    column=col,
                    context=format_error_context(self.content, line, col),
                    help_text="Hexadecimal values must start with '0x' followed by valid hex digits",
                )
        elif value == "true":
            return DtsProperty(name=name, value=True, type="boolean")
        elif value == "false":
            return DtsProperty(name=name, value=False, type="boolean")
        elif value.startswith("&"):
            return DtsProperty(name=name, value=value, type="reference")
        else:
            line, col = self._get_pos_info(self.pos)
            raise DtsParseError(
                f"Invalid property value: {value}",
                line=line,
                column=col,
                context=format_error_context(self.content, line, col),
                help_text="Property values must be strings, integers, arrays, or booleans",
            )

    def _parse_node_body(self, node: DtsNode) -> None:
        """Parse the body of a DTS node.

        Args:
            node: DtsNode to parse body into

        Raises:
            DtsParseError: If node body format is invalid
        """
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token == "}":
                self.pos += 1
                return
            elif token == "{":
                line, col = self._get_pos_info(self.pos)
                raise DtsParseError(
                    "Unexpected '{' in node body",
                    line=line,
                    column=col,
                    context=format_error_context(self.content, line, col),
                    help_text="Node definitions must have a label or reference",
                )

            if token == ";":  # Handle empty statements
                self.pos += 1
                continue

            # Handle boolean properties (e.g., "prop_name;")
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1] == ";":
                name = token
                # Basic check for valid property name (alphanumeric, _, -)
                # This helps distinguish from stray semicolons or other constructs.
                # The tokenizer should ideally guarantee 'token' is a potential identifier here.
                if (
                    name
                    and all(c.isalnum() or c in ("_", "-") for c in name)
                    and name[0] != "-"
                ):  # Ensure it's a valid C-style identifier
                    prop = DtsProperty(name=name, value=True, type="boolean")
                    node.add_property(prop)
                    self.pos += 2  # Consume name and ';'
                    continue

            # Handle properties with assignment (e.g. "prop_name = value;")
            if self.pos + 2 < len(self.tokens) and self.tokens[self.pos + 1] == "=":
                name = token
                value_token = self.tokens[self.pos + 2]
                try:
                    prop = self._parse_property_value(name, value_token)
                    node.add_property(prop)
                    self.pos += 3

                    # Check for additional comma-separated array cells
                    if prop.type == "array":
                        while (
                            self.pos < len(self.tokens) and self.tokens[self.pos] == ","
                        ):
                            self.pos += 1
                            if self.pos >= len(self.tokens):
                                line, col = self._get_pos_info(self.pos - 1)
                                raise DtsParseError(
                                    "Unexpected end of file after ',' in property value",
                                    line=line,
                                    column=col,
                                    context=format_error_context(
                                        self.content, line, col
                                    ),
                                )
                            next_value_token = self.tokens[self.pos]
                            # Parse the next array cell. We expect it to be an array itself.
                            # _parse_property_value will return a DtsProperty, we need its value.
                            additional_prop_part = self._parse_property_value(
                                "_{temp}", next_value_token
                            )
                            if additional_prop_part.type == "array":
                                if isinstance(prop.value, list) and isinstance(
                                    additional_prop_part.value, list
                                ):
                                    prop.value.extend(additional_prop_part.value)
                                else:
                                    # This case should ideally not happen if tokens are well-formed <...>
                                    line, col = self._get_pos_info(self.pos)
                                    raise DtsParseError(
                                        f"Expected array type for subsequent part of property '{name}'",
                                        line=line,
                                        column=col,
                                        context=format_error_context(
                                            self.content, line, col
                                        ),
                                    )
                            else:
                                line, col = self._get_pos_info(self.pos)
                                raise DtsParseError(
                                    f"Expected array for subsequent part of property '{name}', got {additional_prop_part.type}",
                                    line=line,
                                    column=col,
                                    context=format_error_context(
                                        self.content, line, col
                                    ),
                                )
                            self.pos += 1
                except DtsParseError as e:
                    if not e.help_text:
                        e.help_text = f"Invalid value for property '{name}'"
                    raise
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != ";":
                    line, col = self._get_pos_info(self.pos)
                    raise DtsParseError(
                        "Expected ';' after property value",
                        line=line,
                        column=col,
                        context=format_error_context(self.content, line, col),
                        help_text="Property definitions must end with a semicolon",
                    )
                self.pos += 1
                continue

            # Handle child nodes. At this point, 'token' is either a node name or a label.
            current_labels_for_node: List[str] = []
            current_token = token  # Start with the first token we haven't processed as property/etc.

            # Loop to gather all labels: label1: label2: ... node_name
            while self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1] == ":":
                # Current token is a label
                current_labels_for_node.append(current_token)
                self.pos += 2  # Consume label and ':'
                if self.pos >= len(self.tokens):
                    line, col = self._get_pos_info(self.pos - 1)
                    raise DtsParseError(
                        "Unexpected end of file after label expecting node name or another label",
                        line=line,
                        column=col,
                        context=format_error_context(self.content, line, col),
                    )
                current_token = self.tokens[
                    self.pos
                ]  # This is the next potential label or the actual node name

            # After the loop, current_token is the actual node name
            actual_node_name = current_token
            self.pos += 1  # Consume the actual_node_name token

            child = DtsNode(name=actual_node_name)
            for lbl in current_labels_for_node:
                child.add_label(lbl)

            if self.pos >= len(self.tokens) or self.tokens[self.pos] != "{":
                line, col = self._get_pos_info(self.pos)
                # Provide more context in error: what token did we actually find?
                found_token_msg = (
                    f"Found '{self.tokens[self.pos]}' instead."
                    if self.pos < len(self.tokens)
                    else "Found end of input."
                )
                raise DtsParseError(
                    f"Expected '{{ ' after node '{actual_node_name}'. {found_token_msg}",
                    line=line,
                    column=col,
                    context=format_error_context(self.content, line, col),
                    help_text="Node definitions must be enclosed in curly braces and start with '{'.",
                )
            self.pos += 1  # Consume '{'

            self._parse_node_body(child)
            node.add_child(child)

        line, col = self._get_pos_info(self.pos - 1)
        raise DtsParseError(
            "Unexpected end of file",
            line=line,
            column=col,
            context=format_error_context(self.content, line, col),
            help_text="Node body is not properly closed with '}'",
        )
