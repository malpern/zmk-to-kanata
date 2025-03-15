"""Module for parsing ZMK layer definitions into Kanata format."""

import re
from dataclasses import dataclass
from typing import List, Optional


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
        self.keymap_pattern = re.compile(
            r'/\s*{\s*'  # Root node
            r'keymap\s*{\s*'  # Keymap section
            r'compatible\s*=\s*"zmk,keymap";\s*'  # Compatible property
            r'([\s\S]*?'  # Capture all layer content (including newlines)
            r'}\s*;)\s*'  # Close keymap (included in capture)
            r'}\s*;',  # Close root
            re.DOTALL
        )
        
        # Pattern to match individual layers
        self.layer_pattern = re.compile(
            r'(\w+)_layer\s*{\s*'  # Layer name
            r'bindings\s*=\s*<\s*'  # Bindings start
            r'([\s\S]*?)'  # Capture bindings (non-greedy)
            r'>\s*;\s*'  # Bindings end
            r'}\s*;',  # Layer end
            re.DOTALL
        )
    
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