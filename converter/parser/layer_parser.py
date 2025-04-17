"""Layer parser module for ZMK keymaps."""

import logging
from typing import List, Optional
import re

from converter.model.keymap_model import KeyMapping, Layer
from converter.parser.sticky_key_parser import StickyKeyParser

logger = logging.getLogger(__name__)


class LayerParser:
    """Parser for ZMK layer definitions."""

    def __init__(self):
        """Initialize the layer parser."""
        self.current_layer: Optional[str] = None
        self.current_rows: List[List[KeyMapping]] = []  # Each line is a row
        self.has_bindings_declaration: bool = False
        self.sticky_key_parser = StickyKeyParser()
        self.collecting_bindings: bool = False
        # Add macro and unicode parsers as attributes
        from converter.parser.macro_parser import MacroParser
        from converter.parser.unicode_parser import UnicodeParser

        self.macro_parser = MacroParser()
        self.unicode_parser = UnicodeParser()

    def start_layer(self, line: str) -> str:
        """Start parsing a new layer.

        Args:
            line: The line containing the layer definition.

        Returns:
            The name of the layer.

        Raises:
            ValueError: If the layer name cannot be extracted.
        """
        try:
            layer_name = line.split("_layer")[0].strip()
            if not layer_name:
                raise ValueError("Empty layer name")
            self.current_layer = layer_name
            self.current_rows = []
            self.has_bindings_declaration = False
            self.collecting_bindings = False
            return layer_name
        except Exception as e:
            raise ValueError(f"Failed to parse layer name from line: {line}") from e

    def finish_layer(self) -> Layer:
        """Finish parsing the current layer.

        Returns:
            The completed Layer object.

        Raises:
            ValueError: If no layer is being parsed, or if the layer has no
                bindings declaration.
        """
        if not self.current_layer:
            raise ValueError("No layer currently being parsed")

        # Check if we've seen a bindings declaration
        if not self.has_bindings_declaration:
            raise ValueError("Layer must have a bindings declaration")

        logger.debug(
            f"finish_layer: current_rows (len={len(self.current_rows)}): "
            f"{self.current_rows}"
        )

        layer = Layer(name=self.current_layer, keys=self.current_rows)
        self.current_layer = None
        self.current_rows = []
        self.has_bindings_declaration = False
        self.collecting_bindings = False
        return layer

    def parse_binding(self, binding: str) -> KeyMapping:
        """Parse a single key binding.

        Args:
            binding: The binding string to parse.

        Returns:
            A KeyMapping or specialized Binding object representing the
            binding.

        Raises:
            ValueError: If the binding is invalid.
        """
        binding = binding.strip()
        if not binding:
            raise ValueError("Empty binding")

        # Handle unicode bindings
        from converter.behaviors.unicode import is_unicode_binding
        if is_unicode_binding(binding):
            unicode_parser = getattr(self, "unicode_parser", None)
            if unicode_parser is not None:
                unicode_binding = unicode_parser.parse_binding(binding)
                if unicode_binding is not None:
                    return unicode_binding

        # Handle sticky key bindings
        if binding.startswith("&"):
            tokens = binding[1:].strip().split()
            if not tokens:
                raise ValueError("Invalid binding: missing command")
            command = tokens[0]
            # Hold-tap and tap-dance (including custom behaviors like &hm, &hs, &td)
            hold_tap_prefixes = [
                "mt", "ht", "td", "hm", "hs"
            ]
            if (
                command in hold_tap_prefixes
                or command in self._get_custom_hold_tap_behaviors()
            ):
                # Use the hold-tap parser if available
                hold_tap_parser = getattr(self, "hold_tap_parser", None)
                if hold_tap_parser is not None:
                    hold_tap_binding = hold_tap_parser.parse_binding(binding)
                    if hold_tap_binding is not None:
                        return hold_tap_binding
            if command == "kp" and len(tokens) > 1:
                key = tokens[1]
                return KeyMapping(key=key)
            elif command == "trans":
                return KeyMapping(key="trans")
            elif command.startswith("sk"):
                # Use the sticky key parser for validation
                try:
                    sticky_binding = self.sticky_key_parser.parse_binding(
                        binding
                    )
                    if sticky_binding is None:
                        raise ValueError(
                            f"Invalid sticky key binding: {binding}"
                        )
                    return sticky_binding
                except ValueError as e:
                    raise ValueError(str(e))
            else:
                # Fallback: treat as a generic key mapping
                key_str = (
                    " ".join(tokens[1:]) if len(tokens) > 1 else command
                )
                return KeyMapping(key=key_str)

        # Handle macro bindings (only if not a known hold-tap/tap-dance)
        from converter.behaviors.macro import is_macro_binding
        if is_macro_binding(binding):
            macro_parser = getattr(self, "macro_parser", None)
            if macro_parser is not None:
                macro_binding = macro_parser.parse_binding(binding)
                if macro_binding is not None:
                    return macro_binding

        # Fallback for legacy or direct key names
        if binding == "trans":
            return KeyMapping(key="trans")
        if binding.startswith("sk "):
            try:
                sticky_binding = self.sticky_key_parser.parse_binding(
                    f"&{binding}"
                )
                if sticky_binding is None:
                    raise ValueError(
                        f"Invalid sticky key binding: {binding}"
                    )
                return sticky_binding
            except ValueError as e:
                raise ValueError(str(e))
        if binding.startswith("kp "):
            key = binding[3:].strip()
            if not key:
                raise ValueError("Empty key press binding")
            return KeyMapping(key=key)
        return KeyMapping(key=binding)

    def _get_custom_hold_tap_behaviors(self):
        """Return a set of custom hold-tap/tap-dance behavior names if available."""
        # This can be extended to dynamically collect custom behaviors from config
        # For now, return an empty set or hardcode known custom behaviors
        return set([
            "hm", "hs"
        ])  # Add more as needed

    def parse_bindings_line(self, line: str) -> List[KeyMapping]:
        """Parse a line of bindings into a list of KeyMappings.

        Args:
            line: The line containing bindings.

        Returns:
            A list of KeyMapping objects.

        Raises:
            ValueError: If the line contains invalid bindings.
        """
        logger.debug("Raw binding line: %s", line)

        # Skip binding declaration lines without content
        if line.strip() == "bindings = <":
            return []

        # Skip binding end lines
        if line.strip() == ">;":
            return []

        # Extract content between < and >
        if "<" in line and ">" in line:
            content = line.split("<")[1].split(">")[0].strip()
            logger.debug("Extracted binding content: %s", content)
            if not content:  # Empty bindings block
                return []
            line = content

        # Also handle lines like '<&kp A;'
        if line.startswith("<") and line.endswith(";"):
            content = line[1:-1].strip()
            if not content:
                return []
            line = content

        line = line.rstrip(";").strip()
        if not line:
            return []

        # Use a token-based approach to split on each '&' and include the
        # following command and parameter(s)
        pattern = r"&[^&]+"
        tokens = re.findall(pattern, line)
        bindings = [t.strip() for t in tokens if t.strip()]
        logger.debug("Parsed bindings: %s", bindings)
        if not bindings:
            return []

        try:
            result = [self.parse_binding(b) for b in bindings]
            logger.debug("Created bindings: %s", result)
            return result
        except ValueError as e:
            raise ValueError(f"Invalid binding in line: {line}") from e

    def add_bindings_line(self, line: str) -> None:
        """Add a line of bindings to the current layer.

        Args:
            line: The line containing bindings.

        Raises:
            ValueError: If the bindings are invalid or no layer is being
                parsed.
        """
        if not self.current_layer:
            raise ValueError("No layer currently being parsed")

        logger.debug(f"add_bindings_line: line='{line}'")

        if "bindings = <" in line and ">;" in line:
            # Single-line bindings block
            self.has_bindings_declaration = True
            bindings = self.parse_bindings_line(line)
            logger.debug(f"add_bindings_line: parsed single-line row={bindings}")
            if bindings:
                self.current_rows.append(bindings)
            return  # Don't process further

        if "bindings = <" in line:
            self.has_bindings_declaration = True
            self.collecting_bindings = True
            return  # Don't add this line as a binding

        if ">;" in line:
            self.collecting_bindings = False
            return  # Don't add this line as a binding

        if self.collecting_bindings:
            bindings = self.parse_bindings_line(line)
            logger.debug(f"add_bindings_line: parsed row={bindings}")
            if bindings:
                self.current_rows.append(bindings)
