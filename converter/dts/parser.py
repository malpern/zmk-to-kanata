"""DTS parser for converting DTS to keymap configuration."""

from typing import List, Any, Tuple, Optional
from .ast import DtsNode, DtsProperty, DtsRoot
from .error_handler import DtsParseError, format_error_context
import logging


class DtsParser:
    """Parser for DTS content.

    All debug and trace output is handled via the logging module.
    Use the CLI's --debug, --verbose, or --log-level flags to control visibility.
    """

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
        logging.info("Starting tokenization of DTS content")
        logging.debug(f"First 100 chars of content: {repr(content[:100])}")
        logging.debug(
            f"First 10 chars and ordinals: {[ (c, ord(c)) for c in content[:10] ]}"
        )
        # Print first 10 lines before filtering
        lines = content.splitlines()
        for idx, line in enumerate(lines[:10]):
            logging.debug(f"PRE-FILTER line {idx}: {repr(line)}")
        # Remove preprocessor line markers (lines starting with '#'),
        # but keep property assignments like '#binding-cells = ...;'
        filtered_lines = [
            line
            for line in lines
            if not (line.lstrip().startswith("#") and "=" not in line)
        ]
        # Trim leading and trailing empty lines
        while filtered_lines and not filtered_lines[0].strip():
            filtered_lines.pop(0)
        while filtered_lines and not filtered_lines[-1].strip():
            filtered_lines.pop()
        # Debug: print first 10 non-empty lines after trimming
        non_empty = [line for line in filtered_lines if line.strip()][:10]
        for idx, line in enumerate(non_empty):
            logging.debug(f"TRIMMED line {idx}: {repr(line)}")
        content = "\n".join(filtered_lines)
        self.content = content
        self.tokens = []
        self.line_map = []
        self._tokenize(content)
        logging.info(f"Tokenization complete: {len(self.tokens)} tokens")
        logging.debug(f"First 20 tokens: {self.tokens[:20]}")
        logging.debug(f"Last 20 tokens: {self.tokens[-20:]}")
        logging.debug(f"Full token stream: {self.tokens}")
        self.pos = 0

        # Check for root node token '/'
        if not self.tokens or self.tokens[0] != "/":
            logging.error(
                "DTS must start with root node '/' (first token: %r)",
                self.tokens[0] if self.tokens else None,
            )
            raise DtsParseError(
                "DTS must start with root node '/'",
                file=file,
                line=1,
                column=1,
                context=format_error_context(content, 1, 1),
            )

        logging.info("Parsing root node '/'")
        parsed_root_node = DtsNode(name="/")
        self.pos += 1  # Consume the '/' token

        # Expect '{' after root node '/'
        if self.pos >= len(self.tokens) or self.tokens[self.pos] != "{":
            line, col = self._get_pos_info(self.pos)
            logging.error(
                "Expected '{' after root node '/', found '%s'",
                self.tokens[self.pos] if self.pos < len(self.tokens) else None,
            )
            raise DtsParseError(
                "Expected '{' after root node '/'",
                file=file,
                line=line,
                column=col,
                context=format_error_context(content, line, col),
            )
        self.pos += 1  # Consume '{'

        try:
            logging.debug(
                "Entering node body for root node '/' at token position %d", self.pos
            )
            self._parse_node_body(parsed_root_node)
            logging.debug(
                "Finished parsing node body for root node '/' at token position %d",
                self.pos,
            )
            ast_root = DtsRoot(root=parsed_root_node)
            # Robustness: skip any additional root nodes or stray blocks
            logging.debug(
                f"Tokens after first root node: {self.tokens[self.pos:self.pos+20]}"
            )
            while self.pos < len(self.tokens):
                if self.tokens[self.pos] == "/":
                    logging.warning(
                        f"Merging extra root node at token position {self.pos} into main root node"
                    )
                    self.pos += 1
                    if self.pos < len(self.tokens) and self.tokens[self.pos] == "{":
                        self.pos += 1
                        temp_node = DtsNode(name="/")
                        self._parse_node_body(temp_node)
                        # Merge children into the main root node (not as a nested '/')
                        for k, v in temp_node.children.items():
                            if k in parsed_root_node.children:
                                logging.warning(
                                    f"Duplicate top-level node '{k}' found in extra root node; overwriting."
                                )
                            parsed_root_node.children[k] = v
                        # Also merge properties if needed (optional, for completeness)
                        for pk, pv in temp_node.properties.items():
                            if pk in parsed_root_node.properties:
                                logging.warning(
                                    f"Duplicate property '{pk}' found in extra root node; overwriting."
                                )
                            parsed_root_node.properties[pk] = pv
                        # Do NOT add temp_node itself as a child
                    continue
                elif self.tokens[self.pos] == "{":
                    # If a stray '{' is found at the top level, treat it as a root node block
                    logging.warning(
                        f"Merging stray root-level block at token position {self.pos} into main root node"
                    )
                    self.pos += 1
                    temp_node = DtsNode(name="/")
                    self._parse_node_body(temp_node)
                    for k, v in temp_node.children.items():
                        if k in parsed_root_node.children:
                            logging.warning(
                                f"Duplicate top-level node '{k}' found in stray root-level block; overwriting."
                            )
                        parsed_root_node.children[k] = v
                else:
                    self.pos += 1
            logging.info(
                f"AST root children at return: {list(ast_root.children.keys())}"
            )
            return ast_root
        except DtsParseError as e:
            logging.error("Parse error: %s", str(e))
            if not e.file:
                e.file = file  # Ensure file is set on error
            raise

    def _tokenize(self, content: str) -> None:
        """Tokenize DTS content and build line/column map.

        Args:
            content: DTS content string

        Raises:
            DtsParseError: If string or array is unterminated
        """
        logging.debug("Starting tokenization")
        # Remove comments first
        try:
            content = self._remove_comments(content)
        except Exception as e:
            logging.error("Failed to process comments: %s", str(e))
            raise DtsParseError(
                f"Failed to process comments: {str(e)}",
                context=format_error_context(content, 1, 1),
            )

        current = ""
        in_string = False
        line = 1
        column = 1
        i = 0
        safety_counter = 0
        while i < len(content):
            safety_counter += 1
            if safety_counter % 1000 == 0:
                logging.debug(
                    f"[tokenize] i={i}, char={repr(content[i]) if i < len(content) else None}, in_string={in_string}, line={line}, column={column}, safety_counter={safety_counter}"
                )
            if safety_counter > 1_000_000:
                logging.error(
                    "Tokenization exceeded 1,000,000 iterations. Aborting to prevent infinite loop."
                )
                raise RuntimeError(
                    "Tokenization exceeded 1,000,000 iterations. Possible infinite loop."
                )
            char = content[i]
            # Track line and column
            if char == "\n":
                line += 1
                column = 1
                i += 1  # Ensure we always advance on newline
            else:
                column += 1

            if char == '"':
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
                    logging.debug(f"STRING TOKEN: {repr(current)} at i={i}")
                    current = ""
                in_string = not in_string
                i += 1
            elif char == "<" and not in_string:
                if current.strip():
                    tokens = current.strip().split()
                    self.tokens.extend(tokens)
                    for _ in tokens:
                        self.line_map.append((line, column - len(current)))
                current = ""
                # Check for '<<' (bitshift) and treat as part of token, not array delimiter
                if i + 1 < len(content) and content[i + 1] == "<":
                    current += "<<"
                    i += 2
                    continue
                # Start collecting the array as a single token
                start_i = i
                start_line = line
                start_col = column
                depth = 1
                i += 1
                while i < len(content) and depth > 0:
                    c = content[i]
                    # Check for '<<' and '>>' and treat as part of token
                    if c == "<" and i + 1 < len(content) and content[i + 1] == "<":
                        i += 2
                        continue
                    if c == ">" and i + 1 < len(content) and content[i + 1] == ">":
                        i += 2
                        continue
                    # Use logging for debug output
                    if i - start_i < 100:
                        logging.debug(
                            f"[tokenize] i={i}, char={repr(c)}, depth={depth}, snippet={content[start_i:i+1]}"
                        )
                    if c == "<":
                        depth += 1
                    elif c == ">":
                        depth -= 1
                    if c == "\n":
                        line += 1
                        column = 1
                    else:
                        column += 1
                    i += 1
                if depth != 0:
                    logging.error(
                        "Unterminated array starting at line %d, col %d",
                        start_line,
                        start_col,
                    )
                    raise DtsParseError(
                        "Unterminated array",
                        line=start_line,
                        column=start_col,
                        context=format_error_context(content, start_line, start_col),
                    )
                array_content = content[start_i:i]
                self.tokens.append(array_content)
                self.line_map.append((start_line, start_col))
            elif char in "{};=:" and not in_string:
                if current.strip():
                    tokens = current.strip().split()
                    self.tokens.extend(tokens)
                    for _ in tokens:
                        self.line_map.append((line, column - len(current)))
                # Only append the char if it's not whitespace
                if char == "{":
                    logging.debug(
                        f"EMIT '{{' at i={i}, line={line}, col={column}, snippet={repr(content[max(0, i-10):i+10])}"
                    )
                self.tokens.append(char)
                self.line_map.append((line, column))
                current = ""
                i += 1
            else:
                current += char
                i += 1
        logging.debug("Tokenization finished. Total tokens: %d", len(self.tokens))

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

        # Split on whitespace at the top level; do not track parens or arrays
        values = [v.strip() for v in value.split() if v.strip()]

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
        logging.debug(
            f"Entering node body for '{node.name}' at token position {self.pos}"
        )
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            # Skip over extra semicolons and blank/empty tokens
            if token == ";" or (isinstance(token, str) and token.strip() == ""):
                self.pos += 1
                continue

            if token == "}":
                logging.debug(
                    f"Closing node '{node.name}' at token position {self.pos}"
                )
                self.pos += 1
                # Debug: print the next 10 tokens after closing a node
                logging.debug(
                    f"Tokens after closing node: {self.tokens[self.pos:self.pos+10]}"
                )
                # Skip over any stray semicolons or blank tokens (but not braces)
                while self.pos < len(self.tokens) and self.tokens[self.pos] in [
                    ";",
                    "",
                ]:
                    logging.debug(
                        f"Skipping stray token after node close: {self.tokens[self.pos]}"
                    )
                    self.pos += 1
                return
            elif token == "{":
                # If at the root node, treat stray '{' as a block of child nodes
                if node.name == "/":
                    logging.warning(
                        f"Parsing stray '{{' block as child nodes of root at token position {self.pos}"
                    )
                    self.pos += 1
                    temp_node = DtsNode(name="/")
                    self._parse_node_body(temp_node)
                    for k, v in temp_node.children.items():
                        if k in node.children:
                            logging.warning(
                                f"Duplicate top-level node '{k}' found in stray root-level block; overwriting."
                            )
                        node.children[k] = v
                    continue
                # Otherwise, skip as before
                logging.debug(
                    f"Previous tokens: {self.tokens[max(0, self.pos-5):self.pos]}"
                )
                logging.debug(
                    f"Token sequence at error: {self.tokens[self.pos:self.pos+5]}"
                )
                logging.warning(
                    f"Skipping stray '{{' block in node body for '{node.name}' at token position {self.pos}"
                )
                depth = 1
                self.pos += 1
                while self.pos < len(self.tokens) and depth > 0:
                    if self.tokens[self.pos] == "{":
                        depth += 1
                    elif self.tokens[self.pos] == "}":
                        depth -= 1
                    self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos] == "}":
                    logging.debug(
                        f"Closing node '{node.name}' after skipping stray block at token position {self.pos}"
                    )
                    self.pos += 1
                    return
                continue

            if token == ";":  # Handle empty statements
                self.pos += 1
                continue

            # Handle boolean properties (e.g., "prop_name;")
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1] == ";":
                name = token
                if (
                    name
                    and all(c.isalnum() or c in ("_", "-", "#") for c in name)
                    and (name[0].isalpha() or name[0] == "#" or name[0] == "_")
                ):
                    prop = DtsProperty(name=name, value=True, type="boolean")
                    node.add_property(prop)
                    logging.debug(
                        f"Parsed boolean property: {name} = True (type: boolean) in node '{node.name}'"
                    )
                    self.pos += 2  # Consume name and ';'
                    continue

            # Handle properties with assignment (e.g. "prop_name = value;")
            if self.pos + 2 < len(self.tokens) and self.tokens[self.pos + 1] == "=":
                name = token
                value_token = self.tokens[self.pos + 2]
                try:
                    prop = self._parse_property_value(name, value_token)
                    node.add_property(prop)
                    logging.debug(
                        f"Parsed property: {name} = {prop.value} (type: {prop.type}) in node '{node.name}'"
                    )
                    self.pos += 3

                    # Check for additional comma-separated array cells
                    if prop.type == "array":
                        while (
                            self.pos < len(self.tokens) and self.tokens[self.pos] == ","
                        ):
                            self.pos += 1
                            if self.pos >= len(self.tokens):
                                line, col = self._get_pos_info(self.pos - 1)
                                logging.error(
                                    f"Unexpected end of file after ',' in property value for '{name}'"
                                )
                                raise DtsParseError(
                                    "Unexpected end of file after ',' in property value",
                                    line=line,
                                    column=col,
                                    context=format_error_context(
                                        self.content, line, col
                                    ),
                                )
                            next_value_token = self.tokens[self.pos]
                            additional_prop_part = self._parse_property_value(
                                "_{temp}", next_value_token
                            )
                            if additional_prop_part.type == "array":
                                if isinstance(prop.value, list) and isinstance(
                                    additional_prop_part.value, list
                                ):
                                    prop.value.extend(additional_prop_part.value)
                                else:
                                    line, col = self._get_pos_info(self.pos)
                                    logging.error(
                                        f"Expected array type for subsequent part of property '{name}'"
                                    )
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
                                logging.error(
                                    f"Expected array for subsequent part of property '{name}', got {additional_prop_part.type}"
                                )
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
                    logging.error(f"Parse error for property '{name}': {e}")
                    raise
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != ";":
                    line, col = self._get_pos_info(self.pos)
                    logging.error(f"Expected ';' after property value for '{name}'")
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
                    logging.error(
                        "Unexpected end of file after label expecting node name or another label"
                    )
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
                logging.debug(f"Attached label '{lbl}' to node '{actual_node_name}'")

            if self.pos >= len(self.tokens) or self.tokens[self.pos] != "{":
                line, col = self._get_pos_info(self.pos)
                found_token_msg = (
                    f"Found '{self.tokens[self.pos]}' instead."
                    if self.pos < len(self.tokens)
                    else "Found end of input."
                )
                logging.error(
                    f"Expected '{{' after node '{actual_node_name}'. {found_token_msg}"
                )
                raise DtsParseError(
                    f"Expected '{{ ' after node '{actual_node_name}'. {found_token_msg}",
                    line=line,
                    column=col,
                    context=format_error_context(self.content, line, col),
                    help_text="Node definitions must be enclosed in curly braces and start with '{'.",
                )
            self.pos += 1  # Consume '{'

            logging.debug(
                f"Parsing child node '{actual_node_name}' under parent '{node.name}' at token position {self.pos}"
            )
            self._parse_node_body(child)
            node.add_child(child)
            logging.debug(f"Added child node '{child.name}' to parent '{node.name}'")

        # Instead of raising an error on unexpected end of file, just return
        logging.debug(
            f"End of token stream reached in node body for '{node.name}' at token position {self.pos}"
        )
        return
