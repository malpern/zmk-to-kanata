"""Module for parsing ZMK layer definitions into Kanata format."""

import re
from dataclasses import dataclass
from typing import List, Optional

from .model.keymap_model import Layer, KeyMapping, HoldTapBinding


@dataclass
class Layer:
    """Represents a layer with its name and key bindings."""
    name: str
    bindings: str


class LayerParser:
    """Parser for extracting and processing ZMK layers."""
    
    def __init__(self):
        """Initialize the parser with regex patterns."""
        # Pattern to match the entire keymap section
        keymap_parts = [
            r'(?:(?:#include\s+<[^>]+>\s*)*)',  # Optional includes at start
            r'/\s*{\s*',  # Root node
            r'(?:global\s*{\s*[^}]*}\s*;\s*)*',  # Optional global section
            r'keymap\s*{\s*',  # Keymap section
            r'compatible\s*=\s*"zmk,keymap";\s*',  # Compatible property
            r'([\s\S]*?',  # Capture all layer content (including newlines)
            r'}\s*;)\s*',  # Close keymap (included in capture)
            r'}\s*;',  # Close root
        ]
        self.keymap_pattern = re.compile(''.join(keymap_parts), re.DOTALL)
        
        # Pattern to match individual layers
        self.layer_pattern = re.compile(
            r'(\w+)_layer\s*{\s*'  # Layer name
            r'bindings\s*=\s*<\s*'  # Bindings start
            r'([\s\S]*?)'  # Capture bindings (non-greedy)
            r'>\s*;\s*'  # Bindings end
            r'}\s*;',  # Layer end
            re.DOTALL
        )

        # Pattern to match hold-tap bindings
        self.holdtap_pattern = re.compile(
            r'&(\w+)\s+(\w+)\s+(\w+)'  # behavior, hold key, tap key
        )

        # Pattern to match basic key press
        self.keypress_pattern = re.compile(r'&kp\s+(\w+)')
        
        # Pattern to match layer momentary switch
        self.momentary_pattern = re.compile(r'&mo\s+(\d+)')
        
        # Pattern to match transparent key
        self.transparent_pattern = re.compile(r'&trans\b')
    
    def extract_keymap(self, content: str) -> Optional[str]:
        """Extract the keymap section from ZMK content.
        
        Args:
            content: The full ZMK file content
            
        Returns:
            The keymap section content if found, None otherwise
        """
        match = self.keymap_pattern.search(content)
        return match.group(1) if match else None
    
    def extract_layers(self, keymap_content: str) -> List[Layer]:
        """Extract all layers from a keymap section.
        
        Args:
            keymap_content: The content of the keymap section
            
        Returns:
            List of Layer objects containing name and bindings
        """
        layers = []
        for match in self.layer_pattern.finditer(keymap_content):
            name, bindings = match.groups()
            layers.append(Layer(name=name, bindings=bindings.strip()))
        return layers
    
    def parse_binding(self, binding: str) -> KeyMapping:
        """Parse a single binding into a KeyMapping object.
        
        Args:
            binding: The binding string (e.g., "&kp A", "&lh_hm LGUI A")
            
        Returns:
            KeyMapping object representing the binding
        """
        binding = binding.strip()
        
        # Check for hold-tap binding
        holdtap_match = self.holdtap_pattern.match(binding)
        if holdtap_match:
            behavior, hold_key, tap_key = holdtap_match.groups()
            return KeyMapping(
                key=tap_key,  # Use tap key as the base key
                hold_tap=HoldTapBinding(
                    behavior_name=behavior,
                    hold_key=hold_key,
                    tap_key=tap_key
                )
            )
        
        # Check for basic key press
        keypress_match = self.keypress_pattern.match(binding)
        if keypress_match:
            return KeyMapping(key=keypress_match.group(1))
        
        # Check for layer momentary switch
        momentary_match = self.momentary_pattern.match(binding)
        if momentary_match:
            return KeyMapping(key=f"mo {momentary_match.group(1)}")
        
        # Check for transparent key
        if self.transparent_pattern.match(binding):
            return KeyMapping(key="trans")
        
        # Default to raw key if no pattern matches
        return KeyMapping(key=binding)
    
    def parse_bindings_matrix(self, bindings_str: str) -> List[List[KeyMapping]]:
        """Parse a bindings string into a matrix of KeyMapping objects.
        
        Args:
            bindings_str: The raw bindings string from the ZMK file
            
        Returns:
            A matrix (list of lists) of KeyMapping objects
        """
        # Split into rows and clean up whitespace
        rows = [row.strip() for row in bindings_str.strip().split('\n')]
        
        matrix = []
        for row in rows:
            if not row:  # Skip empty rows
                continue
                
            # Split the row into individual bindings
            # First split by '&' to get each binding, then recombine with '&'
            bindings = ['&' + b.strip() for b in row.split('&') if b.strip()]
            
            # Parse each binding
            row_bindings = [self.parse_binding(b) for b in bindings]
            if row_bindings:  # Only add non-empty rows
                matrix.append(row_bindings)
        
        return matrix
    
    def parse_zmk_file(self, content: str) -> List[Layer]:
        """Parse a complete ZMK file and extract all layers.
        
        Args:
            content: The full content of a ZMK file
            
        Returns:
            List of Layer objects containing name and bindings
        
        Raises:
            ValueError: If no valid keymap section is found
        """
        keymap = self.extract_keymap(content)
        if not keymap:
            raise ValueError("No valid keymap section found in ZMK file")
        
        return self.extract_layers(keymap) 