"""ZMK Parser Module

This module is responsible for parsing ZMK keymap files into our intermediate
representation.
"""
import logging
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set

from converter.model.keymap_model import (
    GlobalSettings,
    Layer,
    KeymapConfig,
)
from .parser_error import ParserError
from .layer_parser import LayerParser
from .global_settings_parser import GlobalSettingsParser
from converter.error_recovery import ErrorRecoveryManager
from converter.parser.parser_base import ParserBase
from converter.parser.binding_parser import BindingParser, BindingParseError


logger = logging.getLogger(__name__)


class ParserState(Enum):
    """Parser states."""
    INITIAL = auto()
    IN_KEYMAP = auto()
    IN_LAYER = auto()
    IN_BEHAVIORS = auto()
    IN_CONDITIONAL_LAYER = auto()


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


class ZMKParser(ParserBase):
    """Parser for ZMK keymap files."""

    # Define valid state transitions
    VALID_TRANSITIONS: Dict[ParserState, Set[ParserState]] = {
        ParserState.INITIAL: {ParserState.IN_KEYMAP},
        ParserState.IN_KEYMAP: {ParserState.IN_LAYER},
        ParserState.IN_LAYER: {
            ParserState.IN_BEHAVIORS,
            ParserState.IN_CONDITIONAL_LAYER
        },
        ParserState.IN_BEHAVIORS: {ParserState.IN_LAYER},
        ParserState.IN_CONDITIONAL_LAYER: {ParserState.IN_LAYER},
    }

    def __init__(self):
        """Initialize the parser."""
        self.state = ParserState.INITIAL
        self.layer_parser = LayerParser()
        self.global_settings_parser = GlobalSettingsParser()
        self.layers: List[Layer] = []
        self.current_layer: Optional[Layer] = None
        self.current_layer_content = ""
        self.global_settings = GlobalSettings()
        self.settings_parser = GlobalSettingsParser()
        self.error_manager = ErrorRecoveryManager()
        self.current_line = 0
        self.logger = logging.getLogger(__name__)
        self.binding_parser = BindingParser()

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

            # Process file line by line
            for line in content.split('\n'):
                self.current_line += 1
                line = line.strip()

                if not line or line.startswith('//'):
                    continue

                self._parse_line(line)

            if not self.layers:
                raise ValueError("No layers found in ZMK file")

            return KeymapConfig(
                global_settings=self.global_settings_parser.finish(),
                layers=self.layers
            )
        except ParserError as e:
            raise e
        except Exception as e:
            raise ParserError(f"Failed to parse ZMK file: {e}") from e

    def _parse_line(self, line: str) -> None:
        """Parse a single line.

        Args:
            line: The line to parse
        """
        try:
            if self.state == ParserState.INITIAL:
                if 'keymap {' in line:
                    self._transition_to(ParserState.IN_KEYMAP)

            elif self.state == ParserState.IN_KEYMAP:
                if '_layer {' in line:
                    name = self._extract_layer_name(line)
                    self._start_new_layer(name)
                    self._transition_to(ParserState.IN_LAYER)

            elif self.state in (
                ParserState.IN_LAYER,
                ParserState.IN_BEHAVIORS,
                ParserState.IN_CONDITIONAL_LAYER
            ):
                if '_layer {' in line:
                    raise ParserError("Nested layers are not supported")
                elif 'bindings = <' in line:
                    self._parse_bindings_start(line)
                elif '};' in line:
                    self._finish_current_layer()
                elif self.state == ParserState.IN_BEHAVIORS:
                    if '>' in line:
                        self._transition_to(ParserState.IN_LAYER)
                    else:
                        self._parse_binding_line(line)
        except Exception as e:
            self.logger.error(
                f"Error parsing line {self.current_line}: {line}"
            )
            raise ParserError(f"Line {self.current_line}: {str(e)}")

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
            bindings_count = len(layer.bindings)
            logger.debug("Layer %s: %d bindings", layer.name, bindings_count)
            logger.debug("Adding layer to list: %s", layer.name)
            self.layers.append(layer)
            logger.debug("Total layers: %d", len(self.layers))
            self._transition_to(ParserState.IN_KEYMAP)
        except ValueError as e:
            raise ParserError(str(e)) from e

    def _parse_bindings_start(self, line: str) -> None:
        """Parse the start of a bindings section.

        Args:
            line: The line containing bindings start
        """
        if '=' not in line:
            raise ValueError("Invalid bindings format")

        # Check if bindings are on the same line
        if line.endswith('>;'):
            bindings = line.split('<')[1].rstrip('>;').strip()
            if bindings:
                self._parse_binding_line(bindings)

    def _parse_binding_line(self, line: str) -> None:
        """Parse a binding line.

        Args:
            line: The binding line to parse
        """
        if not line or line.startswith('//'):
            return

        # Remove trailing comma if present
        line = line.rstrip(',')

        # Split multiple bindings on the same line
        bindings = line.strip().split()

        for binding in bindings:
            if not binding:
                continue

            try:
                key_mapping = self.binding_parser.parse(binding)
                if self.current_layer:
                    self.current_layer.bindings.append(key_mapping)
            except BindingParseError as e:
                if self.error_manager:
                    context = {
                        "binding": binding,
                        "error": str(e)
                    }
                    if "nested" in str(e):
                        context["nested_error"] = str(e)
                    elif "behavior" in str(e):
                        context["behavior_error"] = str(e)
                    elif "parameter" in str(e):
                        context["param_error"] = str(e)

                    key_mapping = self.error_manager.handle_invalid_binding(
                        binding,
                        self.current_line,
                        context
                    )
                    if self.current_layer:
                        self.current_layer.bindings.append(key_mapping)
                else:
                    raise ValueError(f"Invalid binding: {binding}")

    def get_error_summary(self) -> str:
        """Get a summary of all errors that occurred during parsing.

        Returns:
            str: A formatted error summary
        """
        return self.error_manager.get_error_summary()

    def has_errors(self) -> bool:
        """Check if any errors occurred during parsing.

        Returns:
            bool: True if errors occurred, False otherwise
        """
        return self.error_manager.has_errors()
