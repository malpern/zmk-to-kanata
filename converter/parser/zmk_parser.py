"""ZMK Parser Module

This module is responsible for parsing ZMK keymap files into our intermediate
representation.
"""
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

from converter.model.keymap_model import (
    GlobalSettings,
    KeyMapping,
    Layer,
    KeymapConfig,
)
from converter.behaviors.sticky_key import StickyKeyBinding


class ParserState(Enum):
    """States for the ZMK parser state machine."""
    INITIAL = auto()
    IN_ROOT = auto()
    IN_KEYMAP = auto()
    IN_LAYER = auto()
    IN_BINDINGS = auto()


class LayerParser:
    """Parser for ZMK layer definitions."""
    
    def parse_binding(self, binding: str) -> KeyMapping:
        """Parse a single key binding."""
        binding = binding.strip()
        if binding == 'trans':
            return KeyMapping(key='trans')
        elif binding.startswith('sk '):
            key = binding[3:].strip()  # Remove 'sk ' prefix
            return StickyKeyBinding(key=key)
        elif binding.startswith('kp '):
            key = binding[3:].strip()  # Remove 'kp ' prefix
            return KeyMapping(key=key)
        else:
            return KeyMapping(key=binding.strip())

    def parse_bindings_line(self, line: str) -> List[KeyMapping]:
        """Parse a line of bindings into a list of KeyMappings."""
        # Remove any trailing characters and split by &
        line = line.rstrip(';').rstrip('>').strip()
        bindings = [b.strip() for b in line.split('&') if b.strip()]
        return [self.parse_binding(b) for b in bindings]


class ZMKParser:
    """Parser for ZMK keymap files."""

    def __init__(self):
        """Initialize the parser."""
        self.layer_parser = LayerParser()
        self.state = ParserState.INITIAL
        self.current_layer: Optional[str] = None
        self.current_bindings: List[List[KeyMapping]] = []
        self.layers: List[Layer] = []

    def parse(self, file_path: Path) -> KeymapConfig:
        """Parse a ZMK keymap file into a KeymapConfig object."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Use default global settings for now
        global_settings = GlobalSettings(tap_time=200, hold_time=250)
        
        # Process file line by line
        for line in content.split('\n'):
            self._process_line(line.strip())

        if not self.layers:
            raise ValueError("Could not find any layers in ZMK file")

        return KeymapConfig(
            global_settings=global_settings,
            layers=self.layers
        )

    def _process_line(self, line: str) -> None:
        """Process a single line based on current state."""
        if not line:
            return

        if self.state == ParserState.INITIAL:
            if '/ {' in line:
                self.state = ParserState.IN_ROOT
        
        elif self.state == ParserState.IN_ROOT:
            if 'keymap {' in line:
                self.state = ParserState.IN_KEYMAP
        
        elif self.state == ParserState.IN_KEYMAP:
            if '_layer {' in line:
                self._start_new_layer(line)
            elif '}' in line and self.current_layer:
                self._finish_current_layer()
        
        elif self.state == ParserState.IN_LAYER:
            if 'bindings = <' in line:
                self.state = ParserState.IN_BINDINGS
            elif '};' in line:
                self._finish_current_layer()
        
        elif self.state == ParserState.IN_BINDINGS:
            if ('&' in line or 'trans' in line) and not line.endswith('>'):
                self._add_bindings_line(line)
            elif '>' in line:
                self._add_bindings_line(line)
                self.state = ParserState.IN_LAYER

    def _start_new_layer(self, line: str) -> None:
        """Start parsing a new layer."""
        if self.current_layer:
            self._finish_current_layer()
        
        self.current_layer = line.split('_layer')[0].strip()
        self.current_bindings = []
        self.state = ParserState.IN_LAYER

    def _finish_current_layer(self) -> None:
        """Finish parsing the current layer."""
        if self.current_layer and self.current_bindings:
            self.layers.append(Layer(
                name=self.current_layer,
                keys=self.current_bindings
            ))
        self.current_layer = None
        self.current_bindings = []
        self.state = ParserState.IN_KEYMAP

    def _add_bindings_line(self, line: str) -> None:
        """Add a line of bindings to the current layer."""
        if self.current_layer is None:
            return
        
        bindings = self.layer_parser.parse_bindings_line(line)
        if bindings:
            self.current_bindings.append(bindings)
