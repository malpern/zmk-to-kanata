"""Layer parser module for ZMK keymaps."""
import logging
from typing import List, Optional

from converter.model.keymap_model import KeyMapping, Layer
from converter.parser.sticky_key_parser import StickyKeyParser


logger = logging.getLogger(__name__)


class LayerParser:
    """Parser for ZMK layer definitions."""
    
    def __init__(self):
        """Initialize the layer parser."""
        self.current_layer: Optional[str] = None
        self.current_bindings: List[List[KeyMapping]] = []
        self.has_bindings_declaration: bool = False
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
            self.has_bindings_declaration = False
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
            ValueError: If no layer is being parsed, or if the layer has no
                bindings declaration.
        """
        if not self.current_layer:
            raise ValueError("No layer currently being parsed")
        
        # Check if we've seen a bindings declaration
        if not self.has_bindings_declaration:
            raise ValueError("Layer must have a bindings declaration")
        
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
        self.has_bindings_declaration = False
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
        logger.debug("Raw binding line: %s", line)
        
        # Skip binding declaration lines without content
        if line.strip() == 'bindings = <':
            return []
        
        # Skip binding end lines
        if line.strip() == '>;':
            return []
        
        # Extract content between < and >
        if '<' in line and '>' in line:
            content = line.split('<')[1].split('>')[0].strip()
            logger.debug("Extracted binding content: %s", content)
            if not content:  # Empty bindings block
                return []
            line = content
        
        line = line.rstrip(';').strip()
        if not line:
            return []

        bindings = [b.strip() for b in line.split('&') if b.strip()]
        logger.debug("Parsed bindings: %s", bindings)
        if not bindings:
            return []

        try:
            result = [self.parse_binding(b) for b in bindings]
            logger.debug("Created bindings: %s", result)
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
            ValueError: If the bindings are invalid or no layer is being
                parsed.
        """
        if not self.current_layer:
            raise ValueError("No layer currently being parsed")
        
        if 'bindings = <' in line:
            self.has_bindings_declaration = True
        
        bindings = self.parse_bindings_line(line)
        if bindings:
            self.current_bindings.append(bindings) 