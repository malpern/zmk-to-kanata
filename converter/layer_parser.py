"""Parser for ZMK layer configurations."""

import re
from typing import List

from .behaviors.key_sequence import is_key_sequence_binding
from .behaviors.macro import is_macro_binding
from .behaviors.sticky_key import is_sticky_key_binding
from .behaviors.unicode import is_unicode_binding
from .model.keymap_model import Binding, Layer
from .parser.key_sequence_parser import KeySequenceParser
from .parser.macro_parser import MacroParser
from .parser.sticky_key_parser import StickyKeyParser
from .parser.unicode_parser import UnicodeParser
from .taphold_parser import TapHoldParser, is_hold_tap_binding


class LayerParser:
    """Parser for ZMK layer configurations."""

    def __init__(self):
        self.sticky_key_parser = StickyKeyParser()
        self.key_sequence_parser = KeySequenceParser()
        self.macro_parser = MacroParser()
        self.unicode_parser = UnicodeParser()
        self.taphold_parser = TapHoldParser()

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

                # Check for hold-tap behaviors
                if config.get('compatible') == '"zmk,behavior-hold-tap"':
                    # Parse the hold-tap behavior
                    behavior_text = block.group(0)
                    try:
                        self.taphold_parser.parse_behavior(behavior_text)
                    except ValueError:
                        # If we can't parse it, just continue
                        pass
                    continue

                # Check for sticky key behaviors
                if config.get('compatible') == '"zmk,behavior-sticky-key"':
                    self.sticky_key_parser.parse_behavior(name, config)
                    continue

                # Check for key sequence behaviors
                if config.get('compatible') == '"zmk,behavior-key-sequence"':
                    self.key_sequence_parser.parse_behavior(name, config)
                    continue

                # Check for macro behaviors
                if config.get('compatible') == '"zmk,behavior-macro"':
                    if 'bindings' in config:
                        behavior = name
                        self.macro_parser.parse_bindings(
                            behavior,
                            config['bindings']
                        )
                    continue

                # Parse Unicode mappings
                self.unicode_parser.parse_unicode_mappings(config_str)

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
        if is_macro_binding(binding_str):
            binding = self.macro_parser.parse_binding(binding_str)
            if binding:
                return binding

        # Try parsing as a Unicode binding
        if is_unicode_binding(binding_str):
            binding = self.unicode_parser.parse_binding(binding_str)
            if binding:
                return binding

        # Try parsing as a hold-tap binding
        if is_hold_tap_binding(binding_str):
            # Extract the behavior name from the binding string
            behavior_name = binding_str.split()[0][1:]  # Remove & prefix
            
            # Check if this is a registered custom behavior
            if self.taphold_parser.is_registered_behavior(behavior_name):
                # Default to a regular key binding that will be processed
                # by the KeyMapping.from_zmk method
                from .model.keymap_model import KeyMapping
                return KeyMapping.from_zmk(binding_str)

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
            
            # Split the bindings string by & to get individual bindings
            # First, remove extra whitespace
            bindings_str = re.sub(r'\s+', ' ', bindings_str.strip())
            
            # Then split by & but keep the & with each binding
            binding_parts = []
            for part in bindings_str.split('&'):
                if part.strip():  # Skip empty parts
                    binding_parts.append('&' + part.strip())
            
            # Process each binding
            for binding_str in binding_parts:
                try:
                    binding = self.parse_binding(binding_str)
                    bindings.append(binding)
                except ValueError:
                    # If we can't parse it, just continue
                    pass

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
            
            # Split the bindings string by & to get individual bindings
            # First, remove extra whitespace
            bindings_str = re.sub(r'\s+', ' ', bindings_str.strip())
            
            # Then split by & but keep the & with each binding
            binding_parts = []
            for part in bindings_str.split('&'):
                if part.strip():  # Skip empty parts
                    binding_parts.append('&' + part.strip())
            
            # Process each binding
            for binding_str in binding_parts:
                try:
                    binding = self.parse_binding(binding_str)
                    bindings.append(binding)
                except ValueError:
                    # If we can't parse it, just continue
                    pass

            # Create layer
            layer = Layer(name=layer_name, bindings=bindings)
            layers.append(layer)

        return layers
