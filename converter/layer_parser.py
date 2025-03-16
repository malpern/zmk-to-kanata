"""Parser for ZMK layer configurations."""

import re
from typing import List, Optional

from converter.model.keymap_model import KeyMapping, Layer, HoldTap
from .parser.sticky_key_parser import StickyKeyParser
from .behaviors.key_sequence import KeySequenceBinding, is_key_sequence_binding


class LayerParser:
    """Parser for ZMK layer configurations."""

    def __init__(self):
        self.sticky_key_parser = StickyKeyParser()

    def extract_keymap(self, content: str) -> Optional[str]:
        """Extract the keymap section from ZMK content."""
        keymap_pattern = (
            r'(?:(?:\s*#include\s+<[^>]+>\s*)*)'  # Include statements
            r'/\s*{\s*'                            # Root object start
            r'(?:[^}]*}\s*;\s*)*'                 # Optional other blocks
            r'keymap\s*{\s*'                      # Keymap block start
            r'compatible\s*=\s*"zmk,keymap";\s*'  # Keymap compatibility
            r'([\s\S]*?}\s*;)\s*}\s*;'           # Layer contents
        )
        match = re.search(keymap_pattern, content)
        return match.group(1) if match else None

    def parse_behaviors(self, content: str) -> None:
        """Parse behavior configurations from ZMK content."""
        behaviors_pattern = r'behaviors\s*{\s*([^}]*?)}\s*;'
        behaviors_match = re.search(behaviors_pattern, content)
        
        if behaviors_match:
            behaviors_content = behaviors_match.group(1)
            behavior_pattern = (
                r'(\w+):\s*\w+\s*{\s*'
                r'([^}]*?)}\s*;'
            )
            behavior_blocks = re.finditer(
                behavior_pattern,
                behaviors_content
            )
            
            for block in behavior_blocks:
                name = block.group(1)
                config_str = block.group(2)
                
                # Parse config into dict
                config = {}
                for line in config_str.split('\n'):
                    line = line.strip()
                    if '=' in line:
                        key, val = line.split('=', 1)
                        config[key.strip()] = val.strip().rstrip(';')
                    elif line and not line.startswith('//'):
                        config[line] = True
                
                # Try parsing as sticky key behavior
                is_sticky = (
                    'compatible' in config and
                    config['compatible'] == '"zmk,behavior-sticky-key"'
                )
                if is_sticky:
                    self.sticky_key_parser.parse_behavior(name, config)

    def parse_binding(self, binding_str: str) -> Optional[KeyMapping]:
        """Parse a single binding string into a KeyMapping object."""
        if not binding_str or binding_str == '&none':
            return None

        if binding_str == '&trans':
            return KeyMapping(key='trans')

        # Handle sticky key binding
        if binding_str.startswith('&sk'):
            if (binding_str == '&sk' or 
                    not binding_str.replace('&sk', '').strip()):
                raise ValueError("Invalid sticky key binding: missing key")
            key = binding_str.replace('&sk', '').strip()
            if key.isdigit() or key == 'INVALID':
                msg = f"Invalid sticky key binding: invalid key '{key}'"
                raise ValueError(msg)
            return KeyMapping(key=f"sk {key}")

        # Handle key sequence binding
        if is_key_sequence_binding(binding_str):
            return KeySequenceBinding.from_zmk(binding_str)

        # Handle hold-tap bindings
        hold_tap_prefixes = [
            '&mt', '&lh_hm', '&rh_hm', '&ht'
        ]
        has_hold_tap_prefix = any(
            binding_str.startswith(prefix)
            for prefix in hold_tap_prefixes
        )
        if has_hold_tap_prefix:
            parts = binding_str.split()
            if len(parts) != 3:
                raise ValueError(
                    f"Invalid hold-tap binding: {binding_str}"
                )

            behavior_name = parts[0][1:]  # Remove & prefix
            hold_key = parts[1]
            tap_key = parts[2]

            return KeyMapping(
                key=tap_key,
                hold_tap=HoldTap(
                    behavior_name=behavior_name,
                    hold_key=hold_key,
                    tap_key=tap_key
                )
            )

        # Handle regular key binding
        if binding_str.startswith('&kp'):
            key = binding_str.replace('&kp', '').strip()
            return KeyMapping(key=key)

        # Handle layer switch binding
        if binding_str.startswith('&mo'):
            layer_num = binding_str.replace('&mo', '').strip()
            return KeyMapping(key=f"mo {layer_num}")

        # Handle invalid input
        if not binding_str.startswith('&'):
            raise ValueError(f"Invalid binding: {binding_str}")

        raise ValueError(f"Unknown binding: {binding_str}")

    def parse_bindings_matrix(
        self, bindings_text: str
    ) -> List[List[KeyMapping]]:
        """Parse bindings text into a matrix of KeyMapping objects.

        Args:
            bindings_text: String containing the bindings matrix

        Returns:
            List of lists of KeyMapping objects
        """
        # Clean up the text
        bindings_text = bindings_text.strip()
        if not bindings_text:
            return []

        # Split into rows
        rows = [row.strip() for row in bindings_text.split('\n')]
        rows = [row for row in rows if row]  # Remove empty rows

        # Parse each row
        matrix = []
        for row in rows:
            # Split row into individual bindings
            bindings = [b.strip() for b in row.split('&') if b.strip()]
            # Parse each binding in the row
            row_mappings = []
            for binding in bindings:
                mapping = self.parse_binding(f"&{binding}")
                row_mappings.append(mapping)
            matrix.append(row_mappings)

        return matrix

    def extract_layers(self, keymap_content: str) -> List[Layer]:
        """Extract layers from keymap content.

        Args:
            keymap_content: String containing keymap content

        Returns:
            List of Layer objects
        """
        layers = []
        layer_pattern = (
            # Layer name with optional _layer suffix
            r'(\w+?)(?:_layer)?\s*{\s*'
            r'bindings\s*=\s*<\s*'  # Bindings start
            r'([^;]*)'  # Bindings content (non-greedy)
            r'>\s*;\s*'  # Bindings end
        )
        matches = re.finditer(layer_pattern, keymap_content)

        for match in matches:
            name = match.group(1)
            bindings_text = match.group(2)

            # Clean up bindings text by removing comments
            bindings_text = re.sub(r'//[^\n]*', '', bindings_text)
            bindings_text = re.sub(
                r'/\*.*?\*/', 
                '', 
                bindings_text, 
                flags=re.DOTALL
            )
            bindings_text = bindings_text.strip()

            # Parse the bindings matrix
            matrix = self.parse_bindings_matrix(bindings_text)
            layers.append(Layer(name=name, keys=matrix))

        return layers

    def parse_zmk_file(self, content: str) -> List[Layer]:
        """Parse a ZMK file and extract layers."""
        # First parse behaviors
        self.parse_behaviors(content)
        
        # Extract keymap section
        keymap_pattern = (
            r'/\s*{\s*'                            # Root object start
            r'(?:[^}]*}\s*;\s*)*'                 # Optional other blocks
            r'keymap\s*{\s*'                      # Keymap block start
            r'compatible\s*=\s*"zmk,keymap";\s*'  # Keymap compatibility
            r'([\s\S]*?)\s*}\s*;\s*}\s*;'        # Layer contents
        )
        
        match = re.search(keymap_pattern, content)
        if not match:
            raise ValueError("No valid keymap section found in ZMK file")
        
        keymap = match.group(1)
        return self.extract_layers(keymap)