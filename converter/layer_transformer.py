"""Module for transforming ZMK layer bindings into Kanata format."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .layer_parser import Layer


@dataclass
class KanataLayer:
    """Represents a layer in Kanata format."""
    name: str
    bindings: List[List[str]]  # Matrix of key bindings


class LayerTransformer:
    """Transforms ZMK layers into Kanata format."""
    
    def __init__(self):
        """Initialize the transformer with ZMK to Kanata mapping."""
        # Basic key mapping from ZMK to Kanata
        self.key_map: Dict[str, str] = {
            "A": "a",
            "B": "b",
            "C": "c",
            # ... more letters will be added
            "N1": "1",
            "N2": "2",
            # ... more numbers will be added
            "EXCL": "excl",
            "AT": "at",
            # ... more symbols will be added
        }
    
    def transform_binding(self, zmk_binding: str) -> Optional[str]:
        """Transform a single ZMK binding to Kanata format.
        
        Args:
            zmk_binding: ZMK binding (e.g., "&kp A", "&mo 1")
            
        Returns:
            Kanata binding or None if binding should be skipped
        """
        binding = zmk_binding.strip()
        
        # Handle layer momentary switch
        if binding.startswith("&mo "):
            layer_num = binding.split(" ")[1]
            return f"@layer{layer_num}"
        
        # Handle transparent key
        if binding == "&trans":
            return "_"
        
        # Handle basic key press
        if binding.startswith("&kp "):
            key = binding.split(" ")[1]
            if key in self.key_map:
                return self.key_map[key]
        
        # Skip or log unhandled bindings for now
        return None
    
    def parse_binding_matrix(self, zmk_bindings: str) -> List[List[str]]:
        """Parse ZMK bindings string into a matrix of bindings.
        
        Args:
            zmk_bindings: Raw ZMK bindings string
            
        Returns:
            Matrix of bindings (rows and columns)
        """
        # Split into rows and clean up whitespace
        rows = [row.strip() for row in zmk_bindings.strip().split("\n")]
        
        # Parse each row into individual bindings
        matrix = []
        for row in rows:
            if not row:  # Skip empty rows
                continue
            # Split row into individual bindings and transform each
            bindings = [b.strip() for b in row.split("&") if b.strip()]
            transformed = []
            for binding in bindings:
                result = self.transform_binding("&" + binding)
                if result:
                    transformed.append(result)
            if transformed:  # Only add non-empty rows
                matrix.append(transformed)
        
        return matrix
    
    def transform_layer(self, zmk_layer: Layer) -> KanataLayer:
        """Transform a ZMK layer into Kanata format.
        
        Args:
            zmk_layer: Layer object containing ZMK layer data
            
        Returns:
            KanataLayer object with transformed bindings
        """
        # Transform the bindings matrix
        kanata_bindings = self.parse_binding_matrix(zmk_layer.bindings)
        
        # Create Kanata layer name (strip _layer suffix if present)
        name = zmk_layer.name
        if name.endswith("_layer"):
            name = name[:-6]
        
        return KanataLayer(name=name, bindings=kanata_bindings)
    
    def transform_layers(self, zmk_layers: List[Layer]) -> List[KanataLayer]:
        """Transform multiple ZMK layers into Kanata format.
        
        Args:
            zmk_layers: List of ZMK Layer objects
            
        Returns:
            List of transformed KanataLayer objects
        """
        return [self.transform_layer(layer) for layer in zmk_layers] 