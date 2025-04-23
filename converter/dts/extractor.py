"""AST extractor for mapping DTS nodes to keymap model."""

from typing import Dict, List, Optional
from .ast import DtsNode, DtsRoot
from ..models import (
    KeymapConfig,
    Layer,
    Binding,
    Behavior,
    HoldTap,
    MacroBehavior,
    Combo,
    ConditionalLayer
)


class KeymapExtractor:
    """Extracts keymap information from DTS AST."""

    def __init__(self):
        """Initialize the extractor."""
        self.behaviors: Dict[str, Behavior] = {}
        self.layers: Dict[str, Layer] = {}
        self.combos: List[Combo] = []
        self.conditional_layers: List[ConditionalLayer] = []

    def extract(self, ast: DtsRoot) -> KeymapConfig:
        """Extract keymap configuration from DTS AST.
        
        Args:
            ast: The DTS AST root node
            
        Returns:
            KeymapConfig instance with extracted information
        """
        # First extract behaviors
        self._extract_behaviors(ast.root)
        
        # Then extract combos
        self._extract_combos(ast.root)
        
        # Then extract conditional layers
        self._extract_conditional_layers(ast.root)
        
        # Finally extract layers
        self._extract_layers(ast.root)
        
        # Create and return keymap config
        return KeymapConfig(
            layers=list(self.layers.values()),
            behaviors=list(self.behaviors.values()),
            combos=self.combos,
            conditional_layers=self.conditional_layers
        )

    def _extract_behaviors(self, node: DtsNode) -> None:
        """Extract behavior definitions from node.
        
        Args:
            node: Current node to process
        """
        if node.name == "behaviors":
            for name, child in node.children.items():
                if "compatible" in child.properties:
                    behavior = self._create_behavior(child)
                    if behavior:
                        # Find the label for this node
                        for label, node_name in child.labels.items():
                            if node_name == child.name:
                                behavior.name = label
                                self.behaviors[label] = behavior
                                print(f"Added behavior {label}: {behavior}")
                                break
                        # If no label found, use the node name
                        if not behavior.name:
                            behavior.name = name
                            self.behaviors[name] = behavior
                            print(f"Added behavior {name}: {behavior}")
        
        # Recursively process children
        for child in node.children.values():
            self._extract_behaviors(child)

    def _extract_combos(self, node: DtsNode) -> None:
        """Extract combo definitions from node.
        
        Args:
            node: Current node to process
        """
        if node.name == "combos":
            for name, child in node.children.items():
                if name != "compatible":
                    timeout = child.properties.get("timeout-ms")
                    positions = child.properties.get("key-positions")
                    bindings = child.properties.get("bindings")
                    
                    if timeout and positions and bindings:
                        timeout_ms = int(timeout.value[1:-1])
                        key_positions = [
                            int(p) for p in positions.value[1:-1].split()
                        ]
                        binding = self._parse_bindings(bindings.value)[0]
                        
                        combo = Combo(
                            name=name,
                            timeout_ms=timeout_ms,
                            key_positions=key_positions,
                            binding=binding
                        )
                        self.combos.append(combo)
                        print(f"Added combo {name}: {combo}")
        
        # Recursively process children
        for child in node.children.values():
            self._extract_combos(child)

    def _extract_conditional_layers(self, node: DtsNode) -> None:
        """Extract conditional layer definitions from node.
        
        Args:
            node: Current node to process
        """
        if node.name == "conditional_layers":
            for name, child in node.children.items():
                if name != "compatible":
                    if_layers = child.properties.get("if-layers")
                    then_layer = child.properties.get("then-layer")
                    
                    if if_layers and then_layer:
                        if_layer_nums = [
                            int(layer_num) for layer_num in if_layers.value[1:-1].split()
                        ]
                        then_layer_num = int(then_layer.value[1:-1])
                        
                        cond_layer = ConditionalLayer(
                            name=name,
                            if_layers=if_layer_nums,
                            then_layer=then_layer_num
                        )
                        self.conditional_layers.append(cond_layer)
                        print(f"Added conditional layer {name}: {cond_layer}")
        
        # Recursively process children
        for child in node.children.values():
            self._extract_conditional_layers(child)

    def _create_behavior(self, node: DtsNode) -> Optional[Behavior]:
        """Create a behavior instance from a node.
        
        Args:
            node: Node containing behavior definition
            
        Returns:
            Behavior instance or None if invalid
        """
        compatible = node.properties.get("compatible")
        if not compatible or compatible.type != "string":
            return None
            
        # Create appropriate behavior type based on compatible string
        if compatible.value == "zmk,behavior-hold-tap":
            return self._create_hold_tap_behavior(node)
        elif compatible.value == "zmk,behavior-macro":
            return self._create_macro_behavior(node)
        elif compatible.value == "zmk,behavior-unicode":
            return self._create_unicode_behavior(node)
        elif compatible.value == "zmk,behavior-unicode-string":
            return self._create_unicode_string_behavior(node)
        # Add other behavior types as needed
            
        return None

    def _create_hold_tap_behavior(self, node: DtsNode) -> Optional[HoldTap]:
        """Create a hold-tap behavior instance.
        
        Args:
            node: Node containing hold-tap behavior definition
            
        Returns:
            HoldTap behavior instance or None if invalid
        """
        # Extract required properties
        tapping_term = node.properties.get("tapping-term-ms")
        if not tapping_term or tapping_term.type != "array":
            return None
            
        # Parse array value
        value = tapping_term.value[1:-1].strip()  # Strip < and >
        if not value:
            return None
        try:
            tapping_term_ms = int(value)
        except ValueError:
            return None
            
        return HoldTap(
            name="",  # Will be set by caller
            tapping_term_ms=tapping_term_ms,
            # Add other properties as needed
        )

    def _create_macro_behavior(self, node: DtsNode) -> Optional[MacroBehavior]:
        """Create a macro behavior instance.
        
        Args:
            node: Node containing macro behavior definition
            
        Returns:
            MacroBehavior instance or None if invalid
        """
        # Extract required properties
        bindings = node.properties.get("bindings")
        if not bindings or bindings.type != "array":
            return None
            
        return MacroBehavior(
            name="",  # Will be set by caller
            bindings=self._parse_bindings(bindings.value)
        )

    def _create_unicode_behavior(self, node: DtsNode) -> Optional[Behavior]:
        """Create a unicode behavior instance.
        
        Args:
            node: Node containing unicode behavior definition
            
        Returns:
            Behavior instance or None if invalid
        """
        return Behavior(
            name="",  # Will be set by caller
            type="unicode"
        )

    def _create_unicode_string_behavior(
        self, node: DtsNode
    ) -> Optional[Behavior]:
        """Create a unicode string behavior instance.
        
        Args:
            node: Node containing unicode string behavior definition
            
        Returns:
            Behavior instance or None if invalid
        """
        return Behavior(
            name="",  # Will be set by caller
            type="unicode_string"
        )

    def _extract_layers(self, node: DtsNode) -> None:
        """Extract layer definitions from node.
        
        Args:
            node: Current node to process
        """
        if node.name == "keymap":
            for name, child in node.children.items():
                if name.endswith("_layer"):
                    layer = self._create_layer(child)
                    if layer:
                        self.layers[name] = layer
                        print(f"Added layer {name}: {layer}")
        
        # Recursively process children
        for child in node.children.values():
            self._extract_layers(child)

    def _create_layer(self, node: DtsNode) -> Optional[Layer]:
        """Create a layer instance from a node.
        
        Args:
            node: Node containing layer definition
            
        Returns:
            Layer instance or None if invalid
        """
        bindings = node.properties.get("bindings")
        if not bindings or bindings.type != "array":
            return None
            
        return Layer(
            name=node.name,
            bindings=self._parse_bindings(bindings.value)
        )

    def _parse_bindings(self, value: str) -> List[Binding]:
        """Parse bindings from property value.
        
        Args:
            value: Property value containing bindings
            
        Returns:
            List of Binding instances
            
        Raises:
            ValueError: If binding format is invalid
        """
        if not value.startswith('<') or not value.endswith('>'):
            raise ValueError("Invalid binding format: must be enclosed in < >")
            
        # Parse array of bindings
        content = value[1:-1].strip()
        if not content:
            return []
            
        bindings = []
        for binding in content.split('&')[1:]:  # Skip empty first element
            binding = binding.strip()
            if not binding:
                continue
                
            # Validate binding format
            valid_prefixes = [
                "kp", "mt", "lt", "macro", "unicode", "uc_string",
                "reset", "bootloader", "none"
            ]
            if not any(
                binding.startswith(prefix) 
                for prefix in valid_prefixes
            ):
                raise ValueError(f"Invalid binding format: {binding}")
                
            bindings.append(self._create_binding(binding))
                
        return bindings

    def _create_binding(self, value: str) -> Binding:
        """Create a binding instance from string value.
        
        Args:
            value: String representation of binding
            
        Returns:
            Binding instance
            
        Raises:
            ValueError: If binding format is invalid
        """
        parts = value.split()
        if not parts:
            raise ValueError("Invalid binding format: empty binding")
            
        behavior_name = parts[0]
        params = parts[1:]
        
        # Validate behavior name
        valid_prefixes = [
            "kp", "mt", "lt", "macro", "unicode", "uc_string",
            "reset", "bootloader", "none"
        ]
        if not any(
            behavior_name.startswith(prefix) 
            for prefix in valid_prefixes
        ):
            raise ValueError(f"Invalid binding format: {value}")
        
        # Look up behavior
        behavior = self.behaviors.get(behavior_name)
        
        # Handle built-in behaviors
        if behavior_name in ["kp", "reset", "bootloader", "none"]:
            behavior = None  # These are built-in
            
        return Binding(behavior=behavior, params=params) 