"""Macro parser module for ZMK keymaps."""
from dataclasses import dataclass
from typing import List, Optional

from converter.parser.parser_error import ParserError
from converter.parser.macro_binding import MacroBinding


@dataclass
class Macro:
    """A macro definition."""
    name: str
    wait_ms: int = 30
    tap_ms: int = 40
    bindings: List[MacroBinding] = None
    param_count: int = 0
    compatible: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.bindings is None:
            self.bindings = []

    def add_binding(self, binding: MacroBinding):
        """Add a binding to the macro."""
        self.bindings.append(binding)


class MacroParser:
    """Parser for ZMK macro definitions."""
    def __init__(self):
        self.macros = []
        self.current_macro = None
        self.in_bindings = False
        self.current_binding = ""
        self.in_macros_block = False

    def process_line(self, line: str) -> None:
        """Process a single line of input."""
        if not line:
            return

        stripped_line = line.strip()
        if not stripped_line:
            return

        # Handle block endings
        if stripped_line == "};":
            if self.current_macro:
                if self.in_bindings:
                    raise ParserError("Unclosed bindings block")
                self.macros.append(self.current_macro)
                self.current_macro = None
            else:
                self.in_macros_block = False
            return

        # Handle block beginnings
        if stripped_line == "/ {":
            return

        if stripped_line == "macros {":
            self.in_macros_block = True
            return

        # Check if we're in a macros block
        if not self.in_macros_block and not stripped_line == "/ {":
            raise ParserError("Not in macros block")

        # Handle macro definitions
        if stripped_line.endswith("{"):
            if ":" in stripped_line:
                if self.current_macro:
                    raise ParserError("Already parsing a macro")
                name = stripped_line.split(":")[0].strip()
                self.current_macro = Macro(name)
            return

        # Handle settings and bindings
        if not self.current_macro:
            raise ParserError("No macro being parsed")

        if "=" in stripped_line:
            self._handle_setting(stripped_line)
        elif self.in_bindings:
            self._handle_binding(stripped_line)
        else:
            raise ParserError("Unexpected line outside of bindings block")

    def _handle_setting(self, line: str) -> None:
        """Handle a setting line."""
        if not line.endswith(";") and not line.endswith("{"):
            raise ParserError("Invalid setting format")

        parts = line.split("=", 1)
        if len(parts) != 2:
            raise ParserError("Invalid setting format")

        key = parts[0].strip()
        value = parts[1].strip()

        if key == "bindings":
            if value.startswith("<"):
                self.in_bindings = True
                if value.endswith(">;"):
                    # Complete binding on one line
                    value = value[1:-2]  # Remove < and >; from start/end
                    self._handle_complete_binding(value)
                    self.in_bindings = False
                else:
                    # Start of multi-line binding
                    value = value[1:]  # Remove < from start
                    if value:  # Only process if there's content after <
                        self._handle_binding(value)
            else:
                raise ParserError("Invalid bindings format")
        elif key == "#binding-cells":
            if not value.startswith("<") or not value.endswith(">;"):
                raise ParserError("Invalid binding cells format")
            try:
                self.current_macro.param_count = int(value[1:-2])
            except ValueError:
                raise ParserError("Invalid binding cells value")
        elif key == "compatible":
            if not value.startswith('"') or not value.endswith('";'):
                raise ParserError("Invalid compatible value")
            self.current_macro.compatible = value[1:-2]
        elif key == "wait-ms":
            if not value.startswith("<") or not value.endswith(">;"):
                raise ParserError("Invalid wait-ms value")
            try:
                self.current_macro.wait_ms = int(value[1:-2])
            except ValueError:
                raise ParserError("Invalid wait-ms value")
        elif key == "tap-ms":
            if not value.startswith("<") or not value.endswith(">;"):
                raise ParserError("Invalid tap-ms value")
            try:
                self.current_macro.tap_ms = int(value[1:-2])
            except ValueError:
                raise ParserError("Invalid tap-ms value")

    def _handle_binding(self, line: str) -> None:
        """Handle a binding line."""
        if not line.strip():
            return

        # Handle line endings
        if line.endswith(">;"):
            line = line[:-2]  # Remove >; from end
            if self.current_binding:
                line = self.current_binding + " " + line
                self.current_binding = ""
            self._handle_complete_binding(line)
            self.in_bindings = False
        elif line.endswith(","):
            line = line[:-1]  # Remove trailing comma
            if self.current_binding:
                line = self.current_binding + " " + line
                self.current_binding = ""
            self._handle_complete_binding(line)
        else:
            # Accumulate the line into current_binding
            if self.current_binding:
                self.current_binding += " " + line.strip()
            else:
                self.current_binding = line.strip()

    def _handle_complete_binding(self, line: str) -> None:
        """Handle a complete binding (between < and >; or comma-separated)."""
        line = line.strip()
        if not line:
            raise ParserError("Empty binding")

        # Split on commas and process each group
        for part in line.split(","):
            part = part.strip()
            if part:
                self._parse_binding_group(part)

    def _parse_binding_group(self, group: str) -> None:
        """Parse a group of bindings (e.g., '&macro_tap &kp A &kp B')."""
        parts = group.strip().split()
        if not parts:
            raise ParserError("Empty binding")

        if not parts[0].startswith("&macro_"):
            raise ParserError(f"Invalid binding format: {group}")

        action = parts[0][1:]  # Remove &
        current_binding = []

        for i, part in enumerate(parts[1:], 1):
            if part.startswith("&"):
                if current_binding:
                    self._create_binding(action, current_binding)
                current_binding = [part]
            else:
                current_binding.append(part)

        if current_binding:
            self._create_binding(action, current_binding)

    def _create_binding(self, action: str, parts: List[str]) -> None:
        """Create a MacroBinding from action and parts."""
        if not parts:
            raise ParserError("Empty binding")

        if parts[0].startswith("&"):
            behavior = parts[0][1:]  # Remove &
            param = " ".join(parts[1:]) if len(parts) > 1 else None
        else:
            behavior = None
            param = " ".join(parts)

        if self.current_macro:
            self.current_macro.add_binding(
                MacroBinding(action=action, behavior=behavior, param=param)
            )
