"""ZMK Parser Module.

This module is responsible for parsing ZMK keymap files into our intermediate
representation.
"""

import logging
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Set
import re

from converter.model.keymap_model import (
    KeymapConfig,
    Layer,
)
from converter.parser.sticky_key_parser import StickyKeyParser

from .global_settings_parser import GlobalSettingsParser
from .layer_parser import LayerParser
from .parser_error import ParserError

logger = logging.getLogger(__name__)


class ParserState(Enum):
    """States for the ZMK parser state machine."""

    INITIAL = auto()
    IN_ROOT = auto()
    IN_KEYMAP = auto()
    IN_LAYER = auto()
    IN_BINDINGS = auto()

    def __str__(self) -> str:
        """Return the name of the state as a string."""
        return self.name


class InvalidStateTransitionError(ParserError):
    """Error raised when an invalid state transition is attempted."""

    def __init__(self, from_state: ParserState, to_state: ParserState) -> None:
        """Initialize the error with the from and to states."""
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"Invalid state transition from {from_state} to {to_state}")


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

    # For test/debug compatibility
    bindings_pattern = re.compile(r"&[^&]+")
    global_pattern = re.compile(r"tap-time|hold-time")

    def __init__(self):
        """Initialize the parser."""
        self.state = ParserState.INITIAL
        self.layer_parser = LayerParser()
        self.global_settings_parser = GlobalSettingsParser()
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
        logger.debug("State transition: %s -> %s", self.state, new_state)
        self.state = new_state

    def _parse_global_settings(self, line: str) -> None:
        """Parse global settings.

        Args:
            line: The line containing global settings.

        Raises:
            ParserError: If the setting is invalid or malformed.
        """
        try:
            self.global_settings_parser.parse_setting(line)
        except ValueError as e:
            raise ParserError(str(e)) from e

    def parse(self, file_path: Path) -> KeymapConfig:
        """Parse a ZMK keymap file.

        Args:
            file_path: Path to the keymap file.

        Returns:
            A KeymapConfig object containing the parsed keymap.

        Raises:
            ParserError: If there are any parsing errors.
        """
        try:
            # Read and process file
            content = file_path.read_text()

            # Populate unicode mappings before parsing layers
            self.layer_parser.unicode_parser.parse_unicode_mappings(content)

            # Process file line by line
            for line in content.split("\n"):
                self._process_line(line.strip())

            if not self.layers:
                raise ValueError("No layers found in ZMK file")

            return KeymapConfig(
                global_settings=self.global_settings_parser.finish(),
                layers=self.layers,
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

        logger.debug("State %s: %s", self.state, line)
        try:
            if self.state == ParserState.INITIAL:
                if "/ {" in line:
                    self._transition_to(ParserState.IN_ROOT)

            elif self.state == ParserState.IN_ROOT:
                if "keymap {" in line:
                    self._transition_to(ParserState.IN_KEYMAP)
                elif "tap-time" in line or "hold-time" in line:
                    self._parse_global_settings(line)

            elif self.state == ParserState.IN_KEYMAP:
                if "_layer {" in line:
                    logger.debug("Found layer: %s", line)
                    self._start_new_layer(line)
                elif "}" in line and self.layer_parser.current_layer:
                    layer_name = self.layer_parser.current_layer
                    logger.debug("Finishing layer: %s", layer_name)
                    self._finish_current_layer()

            elif self.state in (ParserState.IN_LAYER, ParserState.IN_BINDINGS):
                if "_layer {" in line:
                    raise ParserError("Nested layers are not supported")
                elif "bindings = <" in line:
                    logger.debug("Found bindings: %s", line)
                    # Handle single-line bindings
                    if ">;" in line:
                        self._add_bindings_line(line)
                    else:
                        self._add_bindings_line(line)
                        self._transition_to(ParserState.IN_BINDINGS)
                elif "};" in line:
                    logger.debug("Layer end: %s", line)
                    self._finish_current_layer()
                elif self.state == ParserState.IN_BINDINGS:
                    if ">" in line:
                        logger.debug("Bindings end: %s", line)
                        self._add_bindings_line(line)
                        self._transition_to(ParserState.IN_LAYER)
                    elif "&" in line or "trans" in line:
                        logger.debug("Found binding: %s", line)
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
            logger.debug("Started layer: %s", layer_name)
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
            bindings_count = sum(len(row) for row in layer.keys)
            logger.debug("Layer %s: %d bindings", layer.name, bindings_count)
            logger.debug("Adding layer to list: %s", layer.name)
            self.layers.append(layer)
            logger.debug("Total layers: %d", len(self.layers))
            self._transition_to(ParserState.IN_KEYMAP)
        except ValueError as e:
            raise ParserError(str(e)) from e

    def _add_bindings_line(self, line: str) -> None:
        """Add a line of bindings to the current layer.

        Args:
            line: The line containing bindings.

        Raises:
            ParserError: If the bindings are invalid.
        """
        try:
            self.layer_parser.add_bindings_line(line)
            logger.debug("Added bindings: %s", line)
        except ValueError as e:
            raise ParserError(f"Invalid bindings: {line}") from e

    def _parse_bindings(self, binding_text: str):
        """
        Parse bindings for test/debug utilities.

        Returns a list of lists of KeyMapping.
        """
        parser = LayerParser()
        rows = []
        for line in binding_text.strip().splitlines():
            bindings = parser.parse_bindings_line(line.strip())
            if bindings:
                rows.append(bindings)
        return rows
