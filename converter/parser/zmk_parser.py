"""ZMK Parser Module

This module is responsible for parsing ZMK keymap files into our intermediate
representation.
"""
import re
from pathlib import Path
from typing import List

from converter.model.keymap_model import (
    GlobalSettings,
    KeyMapping,
    Layer,
    KeymapConfig
)


class ZMKParser:
    """Parser for ZMK keymap files."""

    def __init__(self):
        """Initialize the parser."""
        # Regular expressions for parsing
        self.global_pattern = re.compile(
            r'global\s*{\s*'
            r'tap-time\s*=\s*<(\d+)>;\s*'
            r'hold-time\s*=\s*<(\d+)>;\s*'
            r'}'
        )
        self.bindings_pattern = re.compile(
            r'bindings\s*=\s*<([^>]+)>'
        )

    def parse(self, file_path: Path) -> KeymapConfig:
        """Parse a ZMK keymap file into a KeymapConfig object."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Parse global settings
        global_match = self.global_pattern.search(content)
        if not global_match:
            raise ValueError("Could not find global settings in ZMK file")
        
        global_settings = GlobalSettings(
            tap_time=int(global_match.group(1)),
            hold_time=int(global_match.group(2))
        )

        # Parse default layer
        bindings_match = self.bindings_pattern.search(content)
        if not bindings_match:
            raise ValueError("Could not find key bindings in ZMK file")

        # Process key bindings
        bindings_text = bindings_match.group(1)
        keys = self._parse_bindings(bindings_text)

        default_layer = Layer(name="default", keys=keys)

        return KeymapConfig(
            global_settings=global_settings,
            layers=[default_layer]
        )

    def _parse_bindings(self, bindings_text: str) -> List[List[KeyMapping]]:
        """Parse the bindings text into a 2D array of KeyMappings."""
        # Split into rows (assuming they're separated by newlines)
        rows = [
            row.strip() for row in bindings_text.split('\n')
            if row.strip()
        ]
        
        result = []
        for row in rows:
            # Split the row into individual key bindings
            key_bindings = [
                kb.strip() for kb in row.split('&kp')
                if kb.strip()
            ]
            # Convert each binding to a KeyMapping
            row_mappings = [
                KeyMapping(key=key.strip()) for key in key_bindings
            ]
            result.append(row_mappings)
        
        return result