"""DTS parser for converting DTS to keymap configuration."""

from typing import List, Any
from .ast import DtsNode, DtsProperty, DtsRoot


class DtsParser:
    """Parser for DTS content."""

    def __init__(self):
        """Initialize parser."""
        self.tokens: List[str] = []
        self.pos = 0

    def parse(self, content: str) -> DtsRoot:
        """Parse DTS content into an AST.

        Args:
            content: DTS content string

        Returns:
            DtsRoot object representing the parsed AST

        Raises:
            ValueError: If the content is not valid DTS
        """
        self.tokens = self._tokenize(content)
        self.pos = 0

        # Parse root node
        if not self.tokens or self.tokens[0] != "/":
            raise ValueError("DTS must start with root node '/'")

        root = DtsRoot()  # Create DtsRoot instance directly
        self.pos += 1  # Skip root node

        # Parse root node body
        if self.pos >= len(self.tokens) or self.tokens[self.pos] != "{":
            raise ValueError("Expected '{' after root node")
        self.pos += 1

        self._parse_node_body(root)
        root._build_label_map()  # Build label map after parsing

        return root

    def _tokenize(self, content: str) -> List[str]:
        """Tokenize DTS content.

        Args:
            content: DTS content string

        Returns:
            List of tokens

        Raises:
            ValueError: If string or array is unterminated
        """
        # Remove comments first
        content = self._remove_comments(content)

        # Split on whitespace, but keep strings and arrays intact
        tokens = []
        current = ""
        in_string = False
        array_stack = []  # Stack to track nested arrays

        i = 0
        while i < len(content):
            char = content[i]

            if char == '"' and not array_stack:
                if not in_string:
                    if current.strip():
                        tokens.extend(current.strip().split())
                    current = char
                else:
                    current += char
                    tokens.append(current)
                    current = ""
                in_string = not in_string
                i += 1
            elif char == "<" and not in_string:
                if not array_stack:
                    if current.strip():
                        tokens.extend(current.strip().split())
                    current = ""
                array_stack.append(i)
                i += 1
            elif char == ">" and not in_string:
                if not array_stack:
                    current += char
                    i += 1
                    continue

                start = array_stack.pop()
                if not array_stack:  # Only add token if this is the outermost array
                    array_content = content[start : i + 1]
                    tokens.append(array_content)
                i += 1
            elif char in "{};=:" and not (in_string or array_stack):
                if current.strip():
                    tokens.extend(current.strip().split())
                tokens.append(char)
                current = ""
                i += 1
            else:
                if not array_stack:
                    current += char
                i += 1

        if in_string:
            raise ValueError("Unterminated string")

        if array_stack:
            raise ValueError("Unterminated array")

        if current.strip():
            tokens.extend(current.strip().split())

        # Filter out any potential empty strings from splitting
        return [t for t in tokens if t.strip()]

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
        """
        # Remove angle brackets
        if not value.startswith("<") or not value.endswith(">"):
            raise ValueError("Invalid array value format")
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
                    raise ValueError("Unmatched '>' in array")
                array_stack.pop()
                current += char
                if not array_stack:  # Only split if this is the outermost array
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

        if current.strip():
            values.append(current.strip())

        # Parse each value
        result = []
        for val in values:
            if val.startswith("<") and val.endswith(">"):
                # Nested array
                result.append(self._parse_array_value(val))
            elif val.startswith("&"):
                # Keep reference value including & prefix
                result.append(val)
            elif val.startswith("0x"):
                # Hex value
                try:
                    result.append(int(val, 16))
                except ValueError:
                    result.append(val)  # Keep as string if invalid hex
            else:
                try:
                    # Try to convert to integer
                    result.append(int(val))
                except ValueError:
                    # Keep as string if not a number
                    result.append(val)

        return result

    def _parse_property_value(self, name: str, value: str) -> DtsProperty:
        """Parse property value into appropriate type.

        Args:
            name: Property name
            value: Property value string

        Returns:
            DtsProperty with parsed value and type
        """
        value = value.strip()
        if value.startswith("<") and value.endswith(">"):
            # Array value
            parsed_array = self._parse_array_value(value)
            # Check if parser should simplify single-element non-reference arrays
            simplify_to_scalar = len(parsed_array) == 1 and not (
                isinstance(parsed_array[0], str) and parsed_array[0].startswith("&")
            )

            if simplify_to_scalar:
                # Determine if it's an integer or needs to stay string/bool
                single_val = parsed_array[0]
                if isinstance(single_val, int):
                    return DtsProperty(name=name, value=single_val, type="integer")
                # Add checks for boolean if needed, though less common in ZMK arrays
                # Otherwise, treat as scalar string? Or keep as single-elem array?
                # Let's keep as single element array for now unless explicitly int.
                # Revisit if ZMK spec requires scalar conversion for other types.
                # return DtsProperty(name=name, value=single_val, type="scalar")

            # Default to array type
            return DtsProperty(name=name, value=parsed_array, type="array")
        elif value.startswith('"') and value.endswith('"'):
            # String value
            return DtsProperty(name=name, value=value[1:-1], type="string")
        elif value.startswith("&"):
            # Reference outside an array
            return DtsProperty(name=name, value=value[1:], type="reference")
        elif value.lower() in ("true", "false"):
            # Boolean value
            return DtsProperty(name=name, value=value.lower() == "true", type="boolean")
        else:
            # Try to parse as number (integer)
            try:
                # Handle hex directly if needed, though parser usually handles it
                int_val = int(value, 16) if value.startswith("0x") else int(value)
                return DtsProperty(name=name, value=int_val, type="integer")
            except ValueError:
                # Default to string if not recognized as anything else
                return DtsProperty(name=name, value=value, type="string")

    def _parse_node_body(self, node: DtsNode) -> None:
        """Parse node body.

        Args:
            node: Node to parse body for
        """
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token == "}":
                self.pos += 1
                return

            if token == ";":
                self.pos += 1
                continue

            # Handle labels
            labels = []
            while self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1] == ":":
                labels.append(token)
                self.pos += 2  # Skip label and colon
                if self.pos >= len(self.tokens):
                    raise ValueError("Unexpected end of input after label")
                token = self.tokens[self.pos]

            # Add labels to node
            for label in labels:
                node.add_label(label)

            # Handle property assignments
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1] == "=":
                prop_name = token
                self.pos += 2  # Skip name and =
                if self.pos >= len(self.tokens):
                    raise ValueError("Unexpected end of input after =")

                value_token = self.tokens[self.pos]
                self.pos += 1

                # Create property
                prop = self._parse_property_value(prop_name, value_token)
                node.add_property(prop)

                # Handle array concatenation (e.g., bindings = <...>, <...>;)
                while self.pos < len(self.tokens) and self.tokens[self.pos] == ",":
                    self.pos += 1  # Skip comma
                    if self.pos >= len(self.tokens):
                        raise ValueError("Unexpected end of input after comma")
                    value_token = self.tokens[self.pos]
                    self.pos += 1
                    array_prop = self._parse_property_value(prop_name, value_token)
                    if prop.type != "array" or array_prop.type != "array":
                        raise ValueError("Can only concatenate array values")
                    prop.value.extend(array_prop.value)

                # Expect semicolon after property value
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != ";":
                    raise ValueError("Expected ';' after property value")
                self.pos += 1

            # Handle child nodes
            else:
                node_name = token
                self.pos += 1

                # Handle node type after name
                if self.pos < len(self.tokens) and self.tokens[self.pos] != "{":
                    node_type = self.tokens[self.pos]
                    if node_type != "{":
                        self.pos += 1

                # Expect opening brace
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != "{":
                    raise ValueError("Expected '{' after node name")
                self.pos += 1

                # Create and parse child node
                child = DtsNode(node_name)
                node.add_child(child)
                self._parse_node_body(child)
