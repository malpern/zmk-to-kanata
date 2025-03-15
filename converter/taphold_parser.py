import re
from dataclasses import dataclass
from typing import List

@dataclass
class HoldTapBehavior:
    """Represents a ZMK hold-tap behavior configuration."""
    name: str
    label: str
    binding_cells: int
    bindings: List[str]

class HoldTapParser:
    """Parser for ZMK hold-tap behavior definitions."""
    
    def __init__(self):
        # Pattern to match behavior name and label
        self.name_pattern = re.compile(r'(\w+):\s*\w+\s*{')
        # Pattern to match label field
        self.label_pattern = re.compile(r'label\s*=\s*"([^"]+)"')
        # Pattern to match binding cells
        self.cells_pattern = re.compile(r'#binding-cells\s*=\s*<(\d+)>')
        # Pattern to match individual bindings within angle brackets
        self.binding_pattern = re.compile(r'<&(\w+)>')
        # Pattern to verify hold-tap compatibility
        self.compatible_pattern = re.compile(r'compatible\s*=\s*"zmk,behavior-hold-tap"')
    
    def parse_behavior(self, zmk_config: str) -> HoldTapBehavior:
        """Parse a ZMK hold-tap behavior definition.
        
        Args:
            zmk_config: String containing the ZMK behavior definition
            
        Returns:
            HoldTapBehavior object representing the parsed configuration
            
        Raises:
            ValueError: If the behavior is not a hold-tap or required fields are missing
        """
        # Check if this is a hold-tap behavior
        if not self.compatible_pattern.search(zmk_config):
            raise ValueError("Not a hold-tap behavior")
        
        # Extract behavior name
        name_match = self.name_pattern.search(zmk_config)
        if not name_match:
            raise ValueError("Missing behavior name")
        name = name_match.group(1)
        
        # Extract required fields
        label_match = self.label_pattern.search(zmk_config)
        cells_match = self.cells_pattern.search(zmk_config)
        
        # Find bindings line
        bindings_line = re.search(r'bindings\s*=\s*([^;]+);', zmk_config)
        
        if not all([label_match, cells_match, bindings_line]):
            raise ValueError("Missing required fields in hold-tap behavior")
        
        # Parse bindings with debug output
        bindings_str = bindings_line.group(1)
        print(f"Raw bindings string: '{bindings_str}'")
        
        # Find all binding references
        bindings = []
        for match in self.binding_pattern.finditer(bindings_str):
            binding = match.group(1)
            print(f"Found binding: '{binding}'")
            bindings.append(binding)
        
        print(f"Final bindings list: {bindings}")
        
        return HoldTapBehavior(
            name=name,
            label=label_match.group(1),
            binding_cells=int(cells_match.group(1)),
            bindings=bindings
        ) 