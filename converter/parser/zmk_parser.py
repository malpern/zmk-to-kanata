"""ZMK Parser Module

This module is responsible for parsing ZMK keymap files into our intermediate
representation.
"""
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set

from converter.model.keymap_model import (
    GlobalSettings,
    KeyMapping,
    Layer,
    KeymapConfig,
)
from converter.parser.sticky_key_parser import StickyKeyParser


class ParserState(Enum):
    """States for the ZMK parser state machine."""
    INITIAL = auto()
    IN_ROOT = auto()
    IN_KEYMAP = auto()
    IN_LAYER = auto()
    IN_BINDINGS = auto()

    def __str__(self) -> str:
        return self.name


class ParserError(Exception):
    """Base class for parser errors."""
    pass


class InvalidStateTransitionError(ParserError):
    """Error raised when an invalid state transition is attempted."""
    def __init__(
        self,
        from_state: ParserState,
        to_state: ParserState
    ) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid state transition from {from_state} to {to_state}"
        )


class LayerParser:
    """Parser for ZMK layer definitions."""
    
    def __init__(self):
        """Initialize the layer parser."""
        self.current_layer: Optional[str] = None
        self.current_bindings: List[List[KeyMapping]] = []
        self.sticky_key_parser = StickyKeyParser()

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
            layer_name = line.split('_layer')[0].strip()
            if not layer_name:
                raise ValueError("Empty layer name")
            self.current_layer = layer_name
            self.current_bindings = []
            return layer_name
        except Exception as e:
            raise ValueError(
                f"Failed to parse layer name from line: {line}"
            ) from e

    def finish_layer(self) -> Layer:
        """Finish parsing the current layer.
        
        Returns:
            The completed Layer object.
            
        Raises:
            ValueError: If no layer is currently being parsed.
        """
        if not self.current_layer or not self.current_bindings:
            raise ValueError("No layer currently being parsed")
        
        # Flatten the bindings list into a single list
        bindings = [
            binding for row in self.current_bindings 
            for binding in row
        ]
        
        layer = Layer(
            name=self.current_layer,
            bindings=bindings
        )
        self.current_layer = None
        self.current_bindings = []
        return layer

    def parse_binding(self, binding: str) -> KeyMapping:
        """Parse a single key binding.
        
        Args:
            binding: The binding string to parse.
            
        Returns:
            A KeyMapping object representing the binding.
            
        Raises:
            ValueError: If the binding is invalid.
        """
        binding = binding.strip()
        if not binding:
            raise ValueError("Empty binding")

        if binding == 'trans':
            return KeyMapping(key='trans')
        
        if binding.startswith('sk '):
            # Use the sticky key parser for validation
            try:
                sticky_binding = self.sticky_key_parser.parse_binding(
                    f"&{binding}"
                )
                if sticky_binding is None:
                    raise ValueError(f"Invalid sticky key binding: {binding}")
                return sticky_binding
            except ValueError as e:
                raise ValueError(str(e))
        
        if binding.startswith('kp '):
            key = binding[3:].strip()
            if not key:
                raise ValueError("Empty key press binding")
            return KeyMapping(key=key)
        
        return KeyMapping(key=binding)

    def parse_bindings_line(self, line: str) -> List[KeyMapping]:
        """Parse a line of bindings into a list of KeyMappings.
        
        Args:
            line: The line containing bindings.
            
        Returns:
            A list of KeyMapping objects.
            
        Raises:
            ValueError: If the line contains invalid bindings.
        """
        print(f"Raw binding line: {line}")  # Debug
        # Extract content between < and >
        if '<' in line and '>' in line:
            line = line.split('<')[1].split('>')[0].strip()
            print(f"Extracted binding content: {line}")  # Debug
        
        line = line.rstrip(';').strip()
        if not line:
            return []

        bindings = [b.strip() for b in line.split('&') if b.strip()]
        print(f"Parsed bindings: {bindings}")  # Debug
        if not bindings:
            return []

        try:
            result = [self.parse_binding(b) for b in bindings]
            print(f"Created bindings: {result}")  # Debug
            return result
        except ValueError as e:
            raise ValueError(
                f"Invalid binding in line: {line}"
            ) from e

    def add_bindings_line(self, line: str) -> None:
        """Add a line of bindings to the current layer.
        
        Args:
            line: The line containing bindings.
            
        Raises:
            ValueError: If no layer is currently being parsed or if the 
                bindings are invalid.
        """
        if self.current_layer is None:
            raise ValueError("No layer currently being parsed")
        
        bindings = self.parse_bindings_line(line)
        if bindings:
            self.current_bindings.append(bindings)


class ZMKParser:
    """Parser for ZMK keymap files."""

    # Define valid state transitions
    VALID_TRANSITIONS: Dict[ParserState, Set[ParserState]] = {
        ParserState.INITIAL: {ParserState.IN_ROOT},
        ParserState.IN_ROOT: {ParserState.IN_KEYMAP},
        ParserState.IN_KEYMAP: {ParserState.IN_LAYER},
        ParserState.IN_LAYER: {ParserState.IN_BINDINGS, ParserState.IN_KEYMAP},
        ParserState.IN_BINDINGS: {ParserState.IN_LAYER, ParserState.IN_KEYMAP},
    }

    def __init__(self):
        """Initialize the parser."""
        self.layer_parser = LayerParser()
        self.state = ParserState.INITIAL
        self.layers: List[Layer] = []
        self.tap_time: int = 200  # Default tap time
        self.hold_time: int = 250  # Default hold time

    def _transition_to(self, new_state: ParserState) -> None:
        """Transition to a new state.
        
        Args:
            new_state: The state to transition to.
            
        Raises:
            InvalidStateTransitionError: If the transition is not valid.
        """
        if new_state not in self.VALID_TRANSITIONS[self.state]:
            raise InvalidStateTransitionError(self.state, new_state)
        print(f"State transition: {self.state} -> {new_state}")  # Debug
        self.state = new_state

    def _parse_global_settings(self, line: str) -> None:
        """Parse global settings from a line.
        
        Args:
            line: The line to parse.
            
        Raises:
            ParserError: If the setting is invalid or malformed.
        """
        line = line.strip()
        try:
            if 'tap-time' in line:
                # Extract number from line like "tap-time = <200>;"
                if '<' not in line or '>' not in line:
                    raise ParserError(f"Invalid tap-time setting: {line}")
                value = line.split('<')[1].split('>')[0].strip()
                try:
                    self.tap_time = int(value)
                except ValueError:
                    raise ParserError(f"Invalid tap-time setting: {line}")
            elif 'hold-time' in line:
                # Extract number from line like "hold-time = <250>;"
                if '<' not in line or '>' not in line:
                    raise ParserError(f"Invalid hold-time setting: {line}")
                value = line.split('<')[1].split('>')[0].strip()
                try:
                    self.hold_time = int(value)
                except ValueError:
                    raise ParserError(f"Invalid hold-time setting: {line}")
        except IndexError:
            raise ParserError(f"Invalid setting format: {line}")

    def parse(self, file_path: Path) -> KeymapConfig:
        """Parse a ZMK keymap file into a KeymapConfig object.
        
        Args:
            file_path: Path to the ZMK keymap file.
            
        Returns:
            A KeymapConfig object representing the parsed keymap.
            
        Raises:
            ValueError: If the file cannot be parsed or no layers are found.
            ParserError: If there are any parsing errors.
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file {file_path}") from e

        try:
            # Process file line by line
            for line in content.split('\n'):
                self._process_line(line.strip())

            if not self.layers:
                raise ValueError("No layers found in ZMK file")

            return KeymapConfig(
                global_settings=GlobalSettings(
                    tap_time=self.tap_time,
                    hold_time=self.hold_time
                ),
                layers=self.layers
            )
        except ParserError as e:
            raise e
        except Exception as e:
            raise ParserError(f"Failed to parse ZMK file: {e}") from e

    def _process_line(self, line: str) -> None:
        """Process a single line based on current state.
        
        Args:
            line: The line to process.
            
        Raises:
            ParserError: If there are any parsing errors.
        """
        if not line:
            return

        print(f"State {self.state}: {line}")  # Debug
        try:
            if self.state == ParserState.INITIAL:
                if '/ {' in line:
                    self._transition_to(ParserState.IN_ROOT)
            
            elif self.state == ParserState.IN_ROOT:
                if 'keymap {' in line:
                    self._transition_to(ParserState.IN_KEYMAP)
                elif 'tap-time' in line or 'hold-time' in line:
                    self._parse_global_settings(line)
            
            elif self.state == ParserState.IN_KEYMAP:
                if '_layer {' in line:
                    print(f"Found layer: {line}")  # Debug
                    self._start_new_layer(line)
                elif '}' in line and self.layer_parser.current_layer:
                    layer_name = self.layer_parser.current_layer
                    print(f"Finishing layer: {layer_name}")  # Debug
                    self._finish_current_layer()
            
            elif self.state == ParserState.IN_LAYER:
                if 'bindings = <' in line:
                    print(f"Found bindings: {line}")  # Debug
                    self._add_bindings_line(line)
                    self._transition_to(ParserState.IN_BINDINGS)
                elif '};' in line:
                    print(f"Layer end: {line}")  # Debug
                    self._finish_current_layer()
            
            elif self.state == ParserState.IN_BINDINGS:
                if '};' in line:
                    print(f"Layer end in bindings: {line}")  # Debug
                    self._finish_current_layer()
                elif '>' in line:
                    print(f"Bindings end: {line}")  # Debug
                    self._add_bindings_line(line)
                    self._transition_to(ParserState.IN_LAYER)
                elif ('&' in line or 'trans' in line):
                    print(f"Found binding: {line}")  # Debug
                    self._add_bindings_line(line)

        except ParserError as e:
            raise e
        except Exception as e:
            raise ParserError(
                f"Error processing line in state {self.state}: {line}"
            ) from e

    def _start_new_layer(self, line: str) -> None:
        """Start parsing a new layer.
        
        Args:
            line: The line containing the layer definition.
            
        Raises:
            ParserError: If the layer name cannot be extracted.
        """
        try:
            self.layer_parser.start_layer(line)
            layer_name = self.layer_parser.current_layer
            print(f"Started layer: {layer_name}")  # Debug
            self._transition_to(ParserState.IN_LAYER)
        except ValueError as e:
            raise ParserError(f"Invalid layer definition: {line}") from e

    def _finish_current_layer(self) -> None:
        """Finish parsing the current layer and add it to the list.
        
        Raises:
            ParserError: If no layer is currently being parsed.
        """
        try:
            layer = self.layer_parser.finish_layer()
            bindings_count = len(layer.bindings)
            print(f"Layer {layer.name}: {bindings_count} bindings")  # Debug
            print(f"Adding layer to list: {layer.name}")  # Debug
            self.layers.append(layer)
            print(f"Total layers: {len(self.layers)}")  # Debug
            self._transition_to(ParserState.IN_KEYMAP)
        except ValueError as e:
            raise ParserError("No layer currently being parsed") from e

    def _add_bindings_line(self, line: str) -> None:
        """Add a line of bindings to the current layer.
        
        Args:
            line: The line containing bindings.
            
        Raises:
            ParserError: If the bindings are invalid.
        """
        try:
            self.layer_parser.add_bindings_line(line)
            print(f"Added bindings: {line}")  # Debug
        except ValueError as e:
            raise ParserError(f"Invalid bindings: {line}") from e
