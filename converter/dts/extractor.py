"""AST extractor for mapping DTS nodes to keymap model."""

from typing import Dict, List, Optional, Any
from .ast import DtsNode, DtsRoot, DtsProperty
from ..models import (
    KeymapConfig,
    Layer,
    Binding,
    Behavior,
    HoldTap,
    MacroBehavior,
    Combo,
    ConditionalLayer,
)
import logging


class KeymapExtractor:
    """Extracts keymap information from DTS AST."""

    def __init__(self):
        """Initialize the extractor."""
        self.behaviors: Dict[str, Behavior] = {}
        self.layers: Dict[str, Layer] = {}
        self.combos: List[Combo] = []
        self.conditional_layers: List[ConditionalLayer] = []
        # Store nodes for second pass behavior processing
        self._behavior_nodes_to_process: List[tuple[str, DtsNode]] = []

    def extract(self, ast: DtsRoot) -> KeymapConfig:
        """Extract keymap configuration from DTS AST.

        Args:
            ast: The DTS AST root node

        Returns:
            KeymapConfig instance with extracted information
        """
        logging.info(
            f"[extract] ast.children.keys() at start: {list(ast.children.keys())}"
        )
        # Reset state for potentially multiple calls
        self.behaviors = {}
        self.layers = {}
        self.combos = []
        self.conditional_layers = []
        self._behavior_nodes_to_process = []

        # The 'ast' (DtsRoot) object itself represents the root '/' node.
        # Its children are directly ast.children.
        # root_node = ast.root.children.get("/") # Old incorrect access
        # if not root_node: # This check is now on 'ast' itself
        #     print("Warning: No root node '/' found in AST or ast.children is empty.")
        #     return KeymapConfig(layers=[], behaviors={})

        # Directly access children of the DtsRoot object (ast)
        behaviors_node = ast.children.get("behaviors")
        combos_node = ast.children.get("combos")
        conditional_layers_node = ast.children.get("conditional_layers")
        keymap_node = ast.children.get("keymap")
        # If not found, check for nested '/' child and look for keymap, behaviors, combos, conditional_layers there
        if "/" in ast.children:
            nested_root = ast.children["/"]
            if isinstance(nested_root, DtsNode):
                if not keymap_node:
                    keymap_node = nested_root.children.get("keymap")
                    if keymap_node:
                        logging.info(
                            "Found keymap node under nested '/' child of root."
                        )
                if not behaviors_node:
                    behaviors_node = nested_root.children.get("behaviors")
                    if behaviors_node:
                        logging.info(
                            "Found behaviors node under nested '/' child of root."
                        )
                if not combos_node:
                    combos_node = nested_root.children.get("combos")
                    if combos_node:
                        logging.info(
                            "Found combos node under nested '/' child of root."
                        )
                if not conditional_layers_node:
                    conditional_layers_node = nested_root.children.get(
                        "conditional_layers"
                    )
                    if conditional_layers_node:
                        logging.info(
                            "Found conditional_layers node under nested '/' child of root."
                        )
        else:
            if keymap_node:
                logging.info("Found keymap node directly under root.")
            if behaviors_node:
                logging.info("Found behaviors node directly under root.")
            if combos_node:
                logging.info("Found combos node directly under root.")
            if conditional_layers_node:
                logging.info("Found conditional_layers node directly under root.")

        # Merge behaviors, combos, and conditional_layers from both root and nested '/' if both exist
        behaviors_nodes = []
        combos_nodes = []
        conditional_layers_nodes = []
        if behaviors_node:
            behaviors_nodes.append(behaviors_node)
        if "/" in ast.children:
            nested_root = ast.children["/"]
            if isinstance(nested_root, DtsNode):
                nested_behaviors = nested_root.children.get("behaviors")
                if nested_behaviors and nested_behaviors is not behaviors_node:
                    behaviors_nodes.append(nested_behaviors)
        if combos_node:
            combos_nodes.append(combos_node)
        if "/" in ast.children:
            nested_root = ast.children["/"]
            if isinstance(nested_root, DtsNode):
                nested_combos = nested_root.children.get("combos")
                if nested_combos and nested_combos is not combos_node:
                    combos_nodes.append(nested_combos)
        if conditional_layers_node:
            conditional_layers_nodes.append(conditional_layers_node)
        if "/" in ast.children:
            nested_root = ast.children["/"]
            if isinstance(nested_root, DtsNode):
                nested_conditional_layers = nested_root.children.get(
                    "conditional_layers"
                )
                if (
                    nested_conditional_layers
                    and nested_conditional_layers is not conditional_layers_node
                ):
                    conditional_layers_nodes.append(nested_conditional_layers)
        # Extract all behaviors, combos, conditional_layers, with nested '/' taking precedence
        for node in behaviors_nodes:
            self._extract_behaviors_pass1(node)
        logging.debug(
            f"[extract] behaviors keys after extraction: {list(self.behaviors.keys())}"
        )
        for node in combos_nodes:
            self._extract_combos(node)
        for node in conditional_layers_nodes:
            self._extract_conditional_layers(node)

        # Pass 2: Process deferred behavior details (like macro bindings)
        self._extract_behaviors_pass2()

        # Pass 3: Extract layers (which can now reference fully defined behaviors)
        if keymap_node:
            self._extract_layers(keymap_node)
        else:
            print("Warning: No 'keymap' node found under root '/'.")

        logging.info(
            f"[extract] ast.children.keys() before layers: {list(ast.children.keys())}"
        )
        # Create and return keymap config
        return KeymapConfig(
            layers=list(self.layers.values()),
            behaviors=self.behaviors,  # Keep as dictionary
            combos=self.combos,
            conditional_layers=self.conditional_layers,
        )

    def _extract_behaviors_pass1(self, behaviors_node: DtsNode) -> None:
        """Pass 1: Create behavior objects, register labels, defer nested parsing."""
        for name, child_node in behaviors_node.children.items():
            if "compatible" in child_node.properties:
                compatible_prop = child_node.properties["compatible"]
                if compatible_prop.type != "string":
                    continue

                compatible = compatible_prop.value
                behavior_object = None
                behavior_type = "unknown"

                # Determine behavior type and create basic object
                if compatible == "zmk,behavior-hold-tap":
                    behavior_object = self._create_hold_tap_behavior(child_node)
                    behavior_type = "hold-tap"
                elif compatible == "zmk,behavior-macro":
                    # Defer binding parsing
                    behavior_object = MacroBehavior(name="", bindings=[])
                    behavior_type = "macro"
                    # Store node for pass 2
                    label_key = next(iter(child_node.labels.keys()), name)
                    self._behavior_nodes_to_process.append((label_key, child_node))
                elif compatible == "zmk,behavior-unicode":
                    behavior_object = Behavior(name="", type="unicode")
                    behavior_type = "unicode"
                elif compatible == "zmk,behavior-unicode-string":
                    behavior_object = Behavior(name="", type="unicode_string")
                    behavior_type = "unicode_string"
                else:
                    # Register all other behaviors as generic
                    behavior_object = Behavior(name="", type=compatible)
                    behavior_type = compatible

                if behavior_object:
                    # Use the first label found as the primary key
                    label_key = next(iter(child_node.labels.keys()), None)
                    behavior_key = label_key if label_key else name
                    behavior_object.name = behavior_key  # Assign name
                    behavior_object.type = behavior_type  # Ensure type is set

                    if behavior_key in self.behaviors:
                        print(
                            "Warning: Duplicate behavior key "
                            f"{behavior_key}. Overwriting."
                        )
                    self.behaviors[behavior_key] = behavior_object

    def _extract_behaviors_pass2(self) -> None:
        """Pass 2: Process deferred behavior details, parse macro bindings."""
        for behavior_key, node in self._behavior_nodes_to_process:
            behavior = self.behaviors.get(behavior_key)
            if not behavior:
                print(
                    f"Warning: Behavior '{behavior_key}' not found "
                    "during pass 2 processing."
                )
                continue

            if isinstance(behavior, MacroBehavior):
                bindings_prop = node.properties.get("bindings")
                if bindings_prop and bindings_prop.type == "array":
                    # For macro behaviors, parse as Bindings, not just strings
                    behavior.bindings = self._parse_bindings(bindings_prop.value)
                else:
                    print(
                        f"Warning: Macro behavior '{behavior_key}' missing "
                        "valid bindings property."
                    )
            # Add processing for other behaviors needing a second pass here...

    def _extract_combos(self, combos_node: DtsNode) -> None:
        """Extract combo definitions from the 'combos' node."""
        for name, child in combos_node.children.items():
            # Skip the compatible property if present
            if name == "compatible" and "compatible" in child.properties:
                continue

            timeout_prop = child.properties.get("timeout-ms")
            positions_prop = child.properties.get("key-positions")
            bindings_prop = child.properties.get("bindings")

            # Ensure properties exist and have expected types
            if not (
                timeout_prop
                and timeout_prop.type in ["integer", "array"]
                and positions_prop
                and positions_prop.type == "array"
                and bindings_prop
                and bindings_prop.type == "array"
            ):
                print(
                    f"Warning: Skipping combo '{name}' due to "
                    f"missing/invalid properties."
                )
                continue

            # Parse timeout (handle single int or array)
            timeout_ms = self._parse_integer_prop(timeout_prop)
            if timeout_ms is None:
                print(
                    f"Warning: Skipping combo '{name}' due to " f"invalid timeout-ms."
                )
                continue

            # Parse positions
            try:
                key_positions = [int(p) for p in positions_prop.value]
            except (ValueError, TypeError):
                print(
                    f"Warning: Skipping combo '{name}' due to "
                    f"invalid key-positions."
                )
                continue

            # Parse bindings (expecting a single binding for the combo)
            # This parsing happens *after* behaviors pass 1
            parsed_bindings = self._parse_bindings(bindings_prop.value)
            if not parsed_bindings:
                print(f"Warning: Skipping combo '{name}' due to invalid bindings.")
                continue
            # Combos expect a single resulting binding
            if len(parsed_bindings) != 1:
                print(
                    f"Warning: Skipping combo '{name}' - expected 1 binding, "
                    f"found {len(parsed_bindings)}."
                )
                continue
            binding = parsed_bindings[0]

            combo = Combo(
                name=name,
                timeout_ms=timeout_ms,
                key_positions=key_positions,
                binding=binding,
            )
            self.combos.append(combo)
            print(f"Added combo {name}: {combo}")

    def _extract_conditional_layers(self, cond_layers_node: DtsNode) -> None:
        """Extract conditional layers from 'conditional_layers' node."""
        for name, child in cond_layers_node.children.items():
            # Skip the compatible property if present
            if name == "compatible" and "compatible" in child.properties:
                continue

            if_layers_prop = child.properties.get("if-layers")
            then_layer_prop = child.properties.get("then-layer")

            if not (
                if_layers_prop
                and if_layers_prop.type == "array"
                and then_layer_prop
                and then_layer_prop.type in ["integer", "array"]
            ):
                print(
                    f"Warning: Skipping conditional layer '{name}' due to "
                    f"missing/invalid properties."
                )
                continue

            # Parse if-layers
            try:
                if_layer_nums = [int(layer_num) for layer_num in if_layers_prop.value]
            except (ValueError, TypeError):
                print(
                    f"Warning: Skipping conditional layer '{name}' due to "
                    f"invalid if-layers."
                )
                continue

            # Parse then-layer (handle single int or array)
            then_layer_num = self._parse_integer_prop(then_layer_prop)
            if then_layer_num is None:
                print(
                    f"Warning: Skipping conditional layer '{name}' due to "
                    f"invalid then-layer."
                )
                continue

            cond_layer = ConditionalLayer(
                name=name, if_layers=if_layer_nums, then_layer=then_layer_num
            )
            self.conditional_layers.append(cond_layer)
            print(f"Added conditional layer {name}: {cond_layer}")

    def _create_hold_tap_behavior(self, node: DtsNode) -> Optional[HoldTap]:
        """Create a hold-tap behavior instance (called in Pass 1)."""
        tapping_term_prop = node.properties.get("tapping-term-ms")
        if not tapping_term_prop:
            print(
                f"Warning: Hold-tap behavior '{node.name}' missing " f"tapping-term-ms."
            )
            return None

        tapping_term_ms = self._parse_integer_prop(tapping_term_prop)
        if tapping_term_ms is None:
            print(
                f"Warning: Hold-tap behavior '{node.name}' has invalid "
                f"tapping-term-ms."
            )
            return None

        # Create object, name/type set by caller (_extract_behaviors_pass1)
        return HoldTap(name="", tapping_term_ms=tapping_term_ms)

    def _extract_layers(self, keymap_node: DtsNode) -> None:
        """Extract layer definitions from the 'keymap' node (Pass 3)."""
        # Skip compatible property if present
        for idx, (name, child) in enumerate(keymap_node.children.items()):
            if name == "compatible" and "compatible" in child.properties:
                continue

            # Assume direct children of keymap are layers
            layer = self._create_layer(child, idx)
            if layer:
                if layer.name in self.layers:
                    print(
                        f"Warning: Duplicate layer name {layer.name}. " f"Overwriting."
                    )
                self.layers[layer.name] = layer
                print(f"Added layer {layer.name}: {layer}")
            else:
                print(f"Warning: Could not create layer from node '{name}'.")

    def _create_layer(self, node: DtsNode, index: int) -> Optional[Layer]:
        """Create a layer instance from a node (called in Pass 3)."""
        bindings_prop = node.properties.get("bindings")
        if not bindings_prop or bindings_prop.type != "array":
            print(f"Warning: Layer '{node.name}' missing valid bindings property.")
            return None

        # Parse bindings now, all behaviors should be available
        parsed_bindings = self._parse_bindings(bindings_prop.value)
        return Layer(name=node.name, index=index, bindings=parsed_bindings)

    def _parse_bindings(self, value: List[Any]) -> List[Binding]:
        """Parse bindings from a list value provided by the parser."""
        if not isinstance(value, list):
            raise ValueError("Invalid binding value type, expected list")

        # Built-in ZMK behaviors that may not be defined in user config
        BUILTIN_BEHAVIORS = {
            # Key behaviors
            "kp": "zmk,behavior-key-press",
            "mt": "zmk,behavior-mod-tap",
            "lt": "zmk,behavior-layer-tap",
            "mo": "zmk,behavior-momentary-layer",
            "to": "zmk,behavior-toggle-layer",
            "sl": "zmk,behavior-sticky-layer",
            "sk": "zmk,behavior-sticky-key",
            "td": "zmk,behavior-tap-dance",
            "bt": "zmk,behavior-bluetooth",
            "mkp": "zmk,behavior-mouse-key-press",
            "trans": "zmk,behavior-transparent",
            "none": "zmk,behavior-none",
            "reset": "zmk,behavior-reset",
            "bootloader": "zmk,behavior-bootloader",
            "unicode": "zmk,behavior-unicode",
            "unicode_string": "zmk,behavior-unicode-string",
            # Add more as needed
        }

        bindings = []
        i = 0
        while i < len(value):
            token = value[i]

            if isinstance(token, str) and token.startswith("&"):
                behavior_name = token[1:]  # Remove &
                params = []
                num_params_expected = 0

                # Determine expected parameters
                if behavior_name in ("kp", "mo", "to", "sl", "sk", "td", "bt", "mkp"):
                    num_params_expected = 1
                elif behavior_name in self.behaviors:
                    b_type = getattr(self.behaviors[behavior_name], "type", None)
                    if b_type == "hold-tap":
                        num_params_expected = 2
                    elif b_type == "macro":
                        num_params_expected = 0
                # Add other known behaviors here...

                # When resolving a binding, only allow behaviors explicitly defined by the user
                def get_or_create_behavior(name, type_str):
                    if name in self.behaviors:
                        return self.behaviors[name]
                    if name in BUILTIN_BEHAVIORS:
                        b = Behavior(name=name, type=BUILTIN_BEHAVIORS[name])
                        self.behaviors[name] = b
                        return b
                    raise ValueError(
                        f"Unknown behavior referenced during binding creation: {name}"
                    )

                # Consume expected parameters
                param_start_index = i + 1
                param_end_index = min(i + 1 + num_params_expected, len(value))
                actual_params_consumed = 0
                for j in range(param_start_index, param_end_index):
                    next_token = value[j]
                    if isinstance(next_token, str) and next_token.startswith("&"):
                        break
                    params.append(str(next_token))
                    actual_params_consumed += 1

                behavior = get_or_create_behavior(behavior_name, behavior_name)
                if behavior:
                    bindings.append(self._create_binding([behavior_name] + params))
                i += 1 + actual_params_consumed
            else:
                bindings.append(self._create_binding(str(token)))
                i += 1
        return bindings

    def _create_binding(self, value: str | List[str]) -> Binding:
        """Create a binding instance from a value."""
        # NOTE: Parameterless 'mo' (and similar) is valid only in the context of a behavior
        # definition (e.g., in a behavior's 'bindings' property), not in a keymap binding.
        # If a parameterless 'mo' is created in a keymap binding, this likely indicates a
        # malformed keymap or a bug in the extractor. All real-world keymap bindings should
        # provide a parameter for 'mo' (e.g., '&mo 1').
        if isinstance(value, list):
            # Handle list format [behavior_name, param1, ...]
            if not value:
                raise ValueError("Empty binding list value")
            behavior_name = value[0]
            params = value[1:]

            if behavior_name == "kp":
                if len(params) != 1:
                    raise ValueError(
                        f"kp behavior expects 1 parameter, "
                        f"got {len(params)}: {params}"
                    )
                # Ensure params is always a list
                return Binding(behavior=None, params=[params[0]])  # Wrap param

            # Look up custom behavior - should exist now
            behavior = self.behaviors.get(behavior_name)
            if behavior:
                # TODO: Validate params against behavior definition if needed
                return Binding(behavior=behavior, params=params)
            else:
                # This shouldn't happen if pass logic is correct
                raise ValueError(
                    f"Unknown behavior referenced during binding creation: "
                    f"{behavior_name}"
                )

        elif isinstance(value, str):
            # Handle simple binding ('A') or parameterless behavior ('&macro')
            if value.startswith("&"):
                behavior_name = value[1:]
                if behavior_name == "kp":
                    raise ValueError("&kp behavior requires a parameter")
                behavior = self.behaviors.get(behavior_name)
                if behavior:
                    # Parameterless, use empty list for params
                    return Binding(behavior=behavior, params=[])
                else:
                    raise ValueError(
                        f"Unknown parameterless behavior reference: {value}"
                    )
            else:
                # Simple value binding, treat param as list
                return Binding(behavior=None, params=[value])  # Wrap param
        else:
            raise ValueError(f"Invalid type for _create_binding: {type(value)}")

    def _parse_integer_prop(self, prop: DtsProperty) -> Optional[int]:
        """Safely parse an integer value from a property."""
        # print(f"DEBUG _parse_integer_prop: Received prop type='{prop.type}', value={repr(prop.value)}") # DEBUG
        # Handle direct integer/scalar types from parser simplification
        if prop.type in ["integer", "scalar"]:
            try:
                result = int(prop.value)
                # print(f"DEBUG _parse_integer_prop: Parsed type '{prop.type}' to {result}") # DEBUG
                return result
            except (ValueError, TypeError):
                # print(f"DEBUG _parse_integer_prop: Failed int(prop.value) for type '{prop.type}': {e}") # DEBUG
                return None
        # Handle case where parser left it as a single-element array
        elif prop.type == "array" and len(prop.value) == 1:
            try:
                result = int(prop.value[0])
                # print(f"DEBUG _parse_integer_prop: Parsed type 'array[1]' to {result}") # DEBUG
                return result
            except (ValueError, TypeError):
                # print(f"DEBUG _parse_integer_prop: Failed int(prop.value[0]) for type 'array[1]': {e}") # DEBUG
                return None
        # print(f"DEBUG _parse_integer_prop: Property type '{prop.type}' not handled or array length != 1.") # DEBUG
        return None
