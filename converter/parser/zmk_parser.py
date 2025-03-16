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
        
        layer = Layer(
            name=self.current_layer,
            keys=self.current_bindings
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
        line = line.rstrip(';').rstrip('>').strip()
        if not line:
            return []

        bindings = [b.strip() for b in line.split('&') if b.strip()]
        if not bindings:
            return []

        try:
            return [self.parse_binding(b) for b in bindings]
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
        ParserState.IN_BINDINGS: {ParserState.IN_LAYER},
    }

    def __init__(self):
        """Initialize the parser."""
        self.layer_parser = LayerParser()
        self.state = ParserState.INITIAL
        self.layers: List[Layer] = []

    def _transition_to(self, new_state: ParserState) -> None:
        """Transition to a new state.
        
        Args:
            new_state: The state to transition to.
            
        Raises:
            InvalidStateTransitionError: If the transition is not valid.
        """
        if new_state not in self.VALID_TRANSITIONS[self.state]:
            raise InvalidStateTransitionError(self.state, new_state)
        self.state = new_state

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

        # Use default global settings for now
        # TODO: Parse global settings from file
        global_settings = GlobalSettings(tap_time=200, hold_time=250)
        
        try:
            # Process file line by line
            for line in content.split('\n'):
                self._process_line(line.strip())

            if not self.layers:
                raise ValueError("No layers found in ZMK file")

            return KeymapConfig(
                global_settings=global_settings,
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

        try:
            if self.state == ParserState.INITIAL:
                if '/ {' in line:
                    self._transition_to(ParserState.IN_ROOT)
            
            elif self.state == ParserState.IN_ROOT:
                if 'keymap {' in line:
                    self._transition_to(ParserState.IN_KEYMAP)
            
            elif self.state == ParserState.IN_KEYMAP:
                if '_layer {' in line:
                    self._start_new_layer(line)
                elif '}' in line and self.layer_parser.current_layer:
                    self._finish_current_layer()
            
            elif self.state == ParserState.IN_LAYER:
                if 'bindings = <' in line:
                    self._transition_to(ParserState.IN_BINDINGS)
                elif '};' in line:
                    self._finish_current_layer()
            
            elif self.state == ParserState.IN_BINDINGS:
                if ('&' in line or 'trans' in line) and not line.endswith('>'):
                    self._add_bindings_line(line)
                elif '>' in line:
                    self._add_bindings_line(line)
                    self._transition_to(ParserState.IN_LAYER)

        except Exception as e:
            raise ParserError(
                f"Error processing line in state {self.state}: {line}"
            ) from e

    def _start_new_layer(self, line: str) -> None:
        """Start parsing a new layer.
        
        Args:
            line: The line containing the layer definition.
            
        Raises:
            ParserError: If there are any parsing errors.
        """
        try:
            if self.layer_parser.current_layer:
                self._finish_current_layer()
            
            self.layer_parser.start_layer(line)
            self._transition_to(ParserState.IN_LAYER)
        except Exception as e:
            raise ParserError(f"Failed to start new layer: {e}") from e

    def _finish_current_layer(self) -> None:
        """Finish parsing the current layer.
        
        Raises:
            ParserError: If there are any parsing errors.
        """
        try:
            layer = self.layer_parser.finish_layer()
            self.layers.append(layer)
            self._transition_to(ParserState.IN_KEYMAP)
        except Exception as e:
            raise ParserError(f"Failed to finish current layer: {e}") from e

    def _add_bindings_line(self, line: str) -> None:
        """Add a line of bindings to the current layer.
        
        Args:
            line: The line containing bindings.
            
        Raises:
            ParserError: If there are any parsing errors.
        """
        try:
            self.layer_parser.add_bindings_line(line)
        except Exception as e:
            raise ParserError(f"Failed to add bindings line: {e}") from e
