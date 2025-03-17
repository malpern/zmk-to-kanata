"""Macro parser module for ZMK keymaps."""
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from .parser_error import ParserError


logger = logging.getLogger(__name__)


@dataclass
class MacroBinding:
    """A single binding in a macro."""
    action: str  # press, release, tap
    behavior: str  # kp, mo, etc.
    param: Optional[str] = None


@dataclass
class Macro:
    """A ZMK macro definition."""
    name: str
    wait_ms: int = 30
    tap_ms: int = 40
    bindings: List[MacroBinding] = None
    param_count: int = 0

    def __post_init__(self):
        """Initialize default values."""
        if self.bindings is None:
            self.bindings = []


class MacroParser:
    """Parser for ZMK macro definitions."""
    
    def __init__(self):
        """Initialize the parser."""
        self.current_macro: Optional[Macro] = None
        self.macros: List[Macro] = []
        self.in_macros_block = False
        self.in_macro_def = False
        self.in_bindings = False
        self.current_setting = None
        self.current_setting_value = None
        self.current_bindings_line = None

    def start_macros_block(self, line: str) -> None:
        """Start parsing a macros block.
        
        Args:
            line: The line containing the macros block start.
            
        Raises:
            ParserError: If already in a macros block.
        """
        if self.in_macros_block:
            raise ParserError("Nested macros blocks are not allowed")
        if "macros {" not in line:
            raise ParserError(f"Invalid macros block start: {line}")
        self.in_macros_block = True
        logger.debug("Started macros block")

    def end_macros_block(self, line: str) -> None:
        """End parsing a macros block.
        
        Args:
            line: The line containing the macros block end.
            
        Raises:
            ParserError: If not in a macros block.
        """
        if not self.in_macros_block:
            raise ParserError("Not in a macros block")
        if "}" not in line:
            raise ParserError(f"Invalid macros block end: {line}")
        self.in_macros_block = False
        logger.debug("Ended macros block")

    def start_macro(self, line: str) -> None:
        """Start parsing a new macro.
        
        Args:
            line: The line containing the macro definition.
            
        Raises:
            ParserError: If already parsing a macro or if the macro name
                is invalid.
        """
        if self.current_macro:
            raise ParserError("Already parsing a macro")
        
        # Match pattern: name: name {
        match = re.match(r'^\s*(\w+)\s*:\s*\w+\s*{', line)
        if not match:
            raise ParserError(f"Invalid macro definition: {line}")
        
        name = match.group(1)
        self.current_macro = Macro(name=name)
        self.in_macro_def = True
        logger.debug("Started macro: %s", name)

    def end_macro(self, line: str) -> None:
        """End parsing the current macro.
        
        Args:
            line: The line containing the macro end.
            
        Raises:
            ParserError: If not parsing a macro.
        """
        if not self.current_macro:
            raise ParserError("No macro being parsed")
        if not self.in_macro_def:
            raise ParserError("Not in a macro definition")
        if "}" not in line:
            raise ParserError(f"Invalid macro end: {line}")
        
        if self.current_setting:
            raise ParserError("Unclosed setting")
        
        self.macros.append(self.current_macro)
        logger.debug(
            "Ended macro %s with %d bindings",
            self.current_macro.name,
            len(self.current_macro.bindings)
        )
        self.current_macro = None
        self.in_macro_def = False
        self.in_bindings = False
        self.current_bindings_line = None

    def parse_binding(self, binding: str) -> List[MacroBinding]:
        """Parse a single binding string which may contain multiple bindings.
        
        Args:
            binding: The binding string to parse.
            
        Returns:
            A list of MacroBinding objects.
            
        Raises:
            ParserError: If the binding is invalid.
        """
        binding = binding.strip()
        if not binding:
            raise ParserError("Empty binding")

        # Remove closing >;
        if binding.endswith('>;'):
            binding = binding[:-2]

        bindings = []
        parts = binding.split('&')
        parts = [p.strip() for p in parts if p.strip()]
        
        if not parts:
            raise ParserError(f"Invalid binding format: {binding}")
            
        current_action = None
        for part in parts:
            # Check if this part defines a new action
            if part.startswith(('macro_press', 'macro_release', 'macro_tap')):
                current_action = part
                continue
            elif part.startswith('macro_param_1to1'):
                # Special case for parameterized macros
                bindings.append(
                    MacroBinding(
                        action='macro_param_1to1',
                        behavior=None,
                        param=None
                    )
                )
                continue
            elif 'MACRO_PLACEHOLDER' in part:
                # Special case for macro placeholder
                match = re.match(r'^(\w+)\s+MACRO_PLACEHOLDER$', part)
                if not match:
                    raise ParserError(f"Invalid placeholder format: {part}")
                bindings.append(
                    MacroBinding(
                        action=match.group(1),
                        behavior='MACRO_PLACEHOLDER',
                        param=None
                    )
                )
                continue
            
            if current_action is None:
                raise ParserError(f"No action specified before: {part}")
                
            match = re.match(r'^(\w+)(?:\s+(\w+))?$', part)
            if not match:
                raise ParserError(f"Invalid behavior format: {part}")
            behavior_name, param = match.groups()
            bindings.append(
                MacroBinding(
                    action=current_action,
                    behavior=behavior_name,
                    param=param
                )
            )
            
        return bindings

    def parse_bindings_line(self, line: str) -> None:
        """Parse a line of bindings.
        
        Args:
            line: The line containing bindings.
            
        Raises:
            ParserError: If the bindings are invalid or no macro is being
                parsed.
        """
        if not self.current_macro:
            raise ParserError("No macro being parsed")

        line = line.strip()
        if not line:
            return

        if line.startswith("bindings = <"):
            # Start of bindings block
            if self.in_bindings:
                raise ParserError("Already in bindings block")
            self.in_bindings = True
            content = line[len("bindings = <"):].strip()
            self.current_bindings_line = content
        elif line.endswith(">;"):
            # End of bindings block
            if not self.in_bindings:
                raise ParserError("Not in bindings block")
            content = line[:-2].strip()
            if self.current_bindings_line:
                content = self.current_bindings_line + " " + content
            self.in_bindings = False
            self.current_bindings_line = None
        elif self.in_bindings:
            # Middle of bindings block
            content = line.rstrip(',')
            if self.current_bindings_line:
                self.current_bindings_line += " " + content
            else:
                self.current_bindings_line = content
            return
        else:
            raise ParserError(f"Invalid bindings line: {line}")

        if not content:
            return

        # Split on commas and parse each binding
        bindings = [b.strip() for b in content.split(',')]
        for binding in bindings:
            if binding:
                self.current_macro.bindings.extend(
                    self.parse_binding(binding)
                )

    def parse_setting(self, line: str) -> None:
        """Parse a macro setting line.
        
        Args:
            line: The line containing the setting.
            
        Raises:
            ParserError: If the setting is invalid or no macro is being
                parsed.
        """
        if not self.current_macro:
            raise ParserError("No macro being parsed")

        line = line.strip().rstrip(';')

        # Handle multi-line settings
        if self.current_setting is not None:
            if not line:
                return
            
            # If we're in a multi-line setting, append this line
            if line.startswith('"') and line.endswith('"'):
                # Single line completion
                value = line.strip('"')
                self._handle_setting_value(self.current_setting, value)
                self.current_setting = None
                self.current_setting_value = None
                return
            elif line.endswith('"'):
                # End of multi-line
                value = line.rstrip('"')
                if self.current_setting_value is None:
                    self.current_setting_value = value.strip()
                else:
                    self.current_setting_value += ' ' + value.strip()
                # Handle the complete setting value
                self._handle_setting_value(
                    self.current_setting,
                    self.current_setting_value
                )
                self.current_setting = None
                self.current_setting_value = None
                return
            else:
                # Middle of multi-line
                if self.current_setting_value is None:
                    self.current_setting_value = line.strip()
                else:
                    self.current_setting_value += ' ' + line.strip()
                return

        # First try to match settings with numeric values in angle brackets
        pattern = (
            r'^([#\w]+(?:-\w+)*)\s*='  # name (allow # in front)
            r'\s*<(-?\d+)>$'           # value with optional negative sign
        )
        numeric_match = re.match(pattern, line)
        if numeric_match:
            setting, value = numeric_match.groups()
            try:
                value_int = int(value)
                if value_int <= 0:
                    msg = f"Setting value must be positive: {line}"
                    raise ParserError(msg)

                if setting == 'wait-ms':
                    self.current_macro.wait_ms = value_int
                elif setting == 'tap-ms':
                    self.current_macro.tap_ms = value_int
                elif setting == '#binding-cells':
                    self.current_macro.param_count = value_int
                else:
                    logger.warning("Unknown setting: %s", setting)
            except ValueError:
                raise ParserError(f"Invalid setting value: {line}")
            return

        # Try to match settings with string values in quotes
        string_match = re.match(
            r'^([#\w]+(?:-\w+)*)\s*=\s*"([^"]+)"$',  # allow # in front
            line
        )
        if string_match:
            setting, value = string_match.groups()
            self._handle_setting_value(setting, value)
            return

        # Check for start of multi-line setting
        setting_start = re.match(
            r'^([#\w]+(?:-\w+)*)\s*=\s*$',  # allow # in front
            line
        )
        if setting_start:
            self.current_setting = setting_start.group(1)
            self.current_setting_value = None
            return

        # If we get here, the setting format is invalid
        raise ParserError(f"Invalid setting format: {line}")

    def _handle_setting_value(self, setting: str, value: str) -> None:
        """Handle a complete setting value.
        
        Args:
            setting: The setting name.
            value: The setting value.
        """
        if setting == 'compatible':
            if 'zmk,behavior-macro-one-param' in value:
                self.current_macro.param_count = 1
            elif 'zmk,behavior-macro-two-param' in value:
                self.current_macro.param_count = 2
        else:
            logger.warning("Unknown setting: %s", setting)

    def process_line(self, line: str) -> None:
        """Process a single line based on current state.
        
        Args:
            line: The line to process.
            
        Raises:
            ParserError: If there are any parsing errors.
        """
        line = line.strip()
        if not line:
            return

        try:
            if line == "/ {":
                # Root node, ignore
                return
            elif "macros {" in line:
                self.start_macros_block(line)
            elif self.in_macros_block and line == "};":
                if self.in_macro_def:
                    self.end_macro(line)
                else:
                    self.end_macros_block(line)
            elif self.in_macros_block and ":" in line and "{" in line:
                self.start_macro(line)
            elif self.in_macro_def and line == "}":
                self.end_macro(line)
            elif (self.in_macro_def and 
                  ("bindings" in line or self.in_bindings)):
                self.parse_bindings_line(line)
            elif (self.in_macro_def and 
                  ("=" in line or self.current_setting)):
                self.parse_setting(line)
            else:
                raise ParserError(f"Unknown line format: {line}")
        except ParserError:
            raise
        except Exception as e:
            raise ParserError(f"Unexpected error: {e}") 