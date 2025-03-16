"""Parser for ZMK layer configurations."""

import re
from typing import List

from .behaviors.key_sequence import is_key_sequence_binding
from .behaviors.sticky_key import is_sticky_key_binding
from .model.keymap_model import Binding, Layer
from .parser.sticky_key_parser import StickyKeyParser
from .parser.key_sequence_parser import KeySequenceParser
from .parser.macro_parser import MacroParser


class LayerParser:
    """Parser for ZMK layer configurations."""

    def __init__(self):
        self.sticky_key_parser = StickyKeyParser()
        self.key_sequence_parser = KeySequenceParser()
        self.macro_parser = MacroParser()

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
                    continue

                # Try parsing as key sequence behavior
                is_key_sequence = (
                    'compatible' in config and
                    config['compatible'] == '"zmk,behavior-key-sequence"'
                )
                if is_key_sequence:
                    self.key_sequence_parser.parse_behavior(name, config)
                    continue

                # Try parsing as macro behavior
                is_macro = (
                    'compatible' in config and
                    config['compatible'].startswith('"zmk,behavior-macro')
                )
                if is_macro:
                    behavior = self.macro_parser.parse_behavior(name, config)

                    # Parse bindings if present
                    if behavior and 'bindings' in config:
                        self.macro_parser.parse_bindings(
                            behavior,
                            config['bindings']
                        )
                    continue

    def parse_binding(self, binding_str: str) -> Binding:
        """Parse a binding string into a Binding object."""
        # Try parsing as a sticky key binding
        if is_sticky_key_binding(binding_str):
            binding = self.sticky_key_parser.parse_binding(binding_str)
            if binding:
                return binding

        # Try parsing as a key sequence binding
        if is_key_sequence_binding(binding_str):
            binding = self.key_sequence_parser.parse_binding(binding_str)
            if binding:
                return binding

        # Try parsing as a macro binding
        from .behaviors.macro import is_macro_binding
        if is_macro_binding(binding_str):
            binding = self.macro_parser.parse_binding(binding_str)
            if binding:
                return binding

        # Default to a regular key binding
        from .model.keymap_model import KeyMapping
        return KeyMapping.from_zmk(binding_str)

    def extract_layers(self, keymap_content: str) -> List[Layer]:
        """Extract layers from a ZMK keymap content."""
        layers = []
        # Updated pattern to be more flexible with whitespace
        layer_pattern = (
            r'(\w+)_layer\s*{\s*'
            r'bindings\s*=\s*<([^>]*)>'
            r'[^}]*}\s*;'
        )

        for match in re.finditer(layer_pattern, keymap_content):
            layer_name = match.group(1)
            bindings_str = match.group(2)

            # Parse bindings
            bindings = []

            # Process all bindings using a single regex pattern
            binding_pattern = r'&(\w+)(?:\s+([A-Z0-9_]+)(?:\s+([A-Z0-9_]+))?)?'
            for binding_match in re.finditer(binding_pattern, bindings_str):
                behavior = binding_match.group(1)
                param1 = binding_match.group(2)
                param2 = binding_match.group(3)

                if param2:  # Hold-tap binding
                    binding_str = f"&{behavior} {param1} {param2}"
                elif param1:  # Regular binding
                    binding_str = f"&{behavior} {param1}"
                else:  # Simple binding like &none
                    binding_str = f"&{behavior}"

                binding = self.parse_binding(binding_str)
                bindings.append(binding)

            # Create layer
            layer = Layer(name=layer_name, bindings=bindings)
            layers.append(layer)

        return layers

    def parse_zmk_file(self, content: str) -> List[Layer]:
        """Parse a ZMK file and extract layers."""
        # First parse behaviors
        self.parse_behaviors(content)

        # Extract keymap section - simplified pattern
        keymap_pattern = (
            r'keymap\s*{\s*compatible\s*=\s*"zmk,keymap";\s*'
            r'([\s\S]*?)}\s*;'
        )
        match = re.search(keymap_pattern, content)
        if not match:
            raise ValueError("No valid keymap section found in ZMK file")

        # Extract layers directly from the content
        layers = []
        layer_pattern = (
            r'(\w+)_layer\s*{\s*'
            r'bindings\s*=\s*<([^>]*)>'
            r'[^}]*}\s*;'
        )

        for match in re.finditer(layer_pattern, content):
            layer_name = match.group(1)
            bindings_str = match.group(2)

            # Parse bindings
            bindings = []

            # Process all bindings using a single regex pattern
            binding_pattern = r'&(\w+)(?:\s+([A-Z0-9_]+)(?:\s+([A-Z0-9_]+))?)?'
            for binding_match in re.finditer(binding_pattern, bindings_str):
                behavior = binding_match.group(1)
                param1 = binding_match.group(2)
                param2 = binding_match.group(3)

                if param2:  # Hold-tap binding
                    binding_str = f"&{behavior} {param1} {param2}"
                elif param1:  # Regular binding
                    binding_str = f"&{behavior} {param1}"
                else:  # Simple binding like &none
                    binding_str = f"&{behavior}"

                binding = self.parse_binding(binding_str)
                bindings.append(binding)

            # Create layer
            layer = Layer(name=layer_name, bindings=bindings)
            layers.append(layer)

        return layers
