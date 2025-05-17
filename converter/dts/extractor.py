"""AST extractor for mapping DTS nodes to keymap model."""

from typing import Dict, List, Optional, Any
from .ast import DtsNode, DtsRoot, DtsProperty
from ..models import (
    KeymapConfig,
    Layer,
    Binding,
    Behavior,
    MacroBehavior,
    Combo,
    ConditionalLayer,
)
from converter.model.keymap_model import HoldTap
import logging
from converter.behaviors.unicode import is_unicode_binding, UnicodeBinding


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
                behavior_type = compatible  # Always set to compatible string

                # Determine behavior type and create basic object
                if compatible == "zmk,behavior-hold-tap":
                    behavior_object = self._create_hold_tap_behavior(child_node)
                    behavior_type = "hold-tap"
                elif compatible == "zmk,behavior-macro":
                    behavior_object = MacroBehavior(name="", bindings=[])
                    behavior_type = "macro"
                    label_key = next(iter(child_node.labels.keys()), name)
                    self._behavior_nodes_to_process.append((label_key, child_node))
                elif compatible == "zmk,behavior-unicode":
                    behavior_object = Behavior(name="")
                    behavior_object.type = "unicode"
                elif compatible == "zmk,behavior-unicode-string":
                    behavior_object = Behavior(name="")
                    behavior_object.type = "unicode_string"
                else:
                    behavior_object = Behavior(name="")
                    behavior_object.type = compatible

                if behavior_object:
                    label_key = next(iter(child_node.labels.keys()), None)
                    behavior_key = label_key if label_key else name
                    behavior_object.name = behavior_key
                    behavior_object.type = behavior_type

                    # Populate extra_properties with all DTS properties for this behavior node
                    if hasattr(behavior_object, "extra_properties"):
                        for prop_name, prop_obj in child_node.properties.items():
                            behavior_object.extra_properties[prop_name] = prop_obj.value

                    # Special handling for tapping-term-ms for tap-dance if not already in extra_properties as int
                    if behavior_object.type == "zmk,behavior-tap-dance":
                        tapping_term_prop = child_node.properties.get("tapping-term-ms")
                        if tapping_term_prop and isinstance(
                            tapping_term_prop.value, int
                        ):
                            setattr(
                                behavior_object,
                                "tapping_term_ms",
                                tapping_term_prop.value,
                            )
                        elif (
                            tapping_term_prop
                            and isinstance(tapping_term_prop.value, list)
                            and tapping_term_prop.value
                        ):
                            # Handle cases where tapping-term-ms might be an array <200>
                            try:
                                val = int(tapping_term_prop.value[0])
                                setattr(behavior_object, "tapping_term_ms", val)
                            except (ValueError, TypeError, IndexError):
                                logging.warning(
                                    f"Could not parse tapping-term-ms for {behavior_key}: {tapping_term_prop.value}"
                                )

                    if behavior_key in self.behaviors:
                        print(
                            "Warning: Duplicate behavior key "
                            f"{behavior_key}. Overwriting."
                        )
                    self.behaviors[behavior_key] = behavior_object

        # --- Ensure built-in behaviors like reset and bootloader are always present if referenced ---
        for builtin in ["reset", "bootloader"]:
            if builtin not in self.behaviors:
                self.behaviors[builtin] = Behavior(name=builtin)

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
                key_positions = [
                    int(p)
                    for p in positions_prop.value
                    if isinstance(positions_prop.value, list)
                ]
            except (ValueError, TypeError):
                print(
                    f"Warning: Skipping combo '{name}' due to "
                    f"invalid key-positions."
                )
                continue

            # Parse bindings (expecting a single binding for the combo)
            # This parsing happens *after* behaviors pass 1
            parsed_bindings = self._parse_bindings(
                bindings_prop.value if isinstance(bindings_prop.value, list) else []
            )
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
                if_layer_nums = [
                    int(layer_num)
                    for layer_num in if_layers_prop.value
                    if isinstance(if_layers_prop.value, list)
                ]
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
        ht = HoldTap(name="", hold_key="", tap_key="", tapping_term_ms=tapping_term_ms)
        # Store all extra properties for best-effort mapping
        ht.extra_properties = {}
        # Explicitly parse and store all relevant hold-tap properties
        for prop_name, prop in node.properties.items():
            if prop_name not in ("compatible", "tapping-term-ms"):
                ht.extra_properties[prop_name] = prop.value
        # Ensure all known properties are present (even if missing)
        for known in [
            "quick-tap-ms",
            "hold-trigger-key-positions",
            "retro-tap",
            "tap-hold-wait-ms",
            "require-prior-idle-ms",
            "flavor",
            "bindings",
        ]:
            if known not in ht.extra_properties:
                ht.extra_properties[known] = None
        return ht

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
        parsed_bindings = self._parse_bindings(
            bindings_prop.value if isinstance(bindings_prop.value, list) else []
        )
        return Layer(name=node.name, index=index, bindings=parsed_bindings)

    def _parse_bindings(self, value: List[Any]) -> List[Binding]:
        """Parse bindings from a list value provided by the parser."""
        if not isinstance(value, list):
            # This case should ideally be caught before calling _parse_bindings
            # or handled by ensuring `value` is always a list.
            # If it still happens, log an error and return an empty list.
            logging.error(
                "Invalid binding value type, expected list, got %s", type(value)
            )
            return []

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
            "caps_word": "zmk,behavior-caps-word",
            "key_repeat": "zmk,behavior-key-repeat",
            # Add more as needed
        }

        bindings: list[Binding] = []  # Initialize with correct type
        i = 0
        while i < len(value):
            token = value[i]
            binding_str = str(token)
            # Always check for Unicode macro first
            if is_unicode_binding(binding_str):
                unicode_binding = UnicodeBinding.from_zmk(binding_str)
                if unicode_binding is not None:
                    bindings.append(unicode_binding)
                i += 1
                continue
            if isinstance(token, str) and token.startswith("&"):
                behavior_name = token[1:]
                # Special handling for reset and bootloader
                if behavior_name in ("reset", "bootloader"):
                    behavior = self.behaviors.get(behavior_name)
                    if not behavior:
                        behavior = Behavior(name=behavior_name)
                        self.behaviors[behavior_name] = behavior
                    bindings.append(Binding(behavior=behavior, params=[]))
                    i += 1
                    continue
                params = []
                num_params_expected = 0
                actual_params_consumed = 0

                # Determine expected parameters and consume them
                if behavior_name == "td":
                    param_idx = i + 1
                    while param_idx < len(value) and not str(
                        value[param_idx]
                    ).startswith("&"):
                        params.append(str(value[param_idx]))
                        param_idx += 1
                    actual_params_consumed = len(params)

                    # Ensure 'td' behavior object exists and is correctly typed
                    td_behavior = self.behaviors.get(behavior_name)
                    if not td_behavior:  # If not found, create and store
                        td_behavior = Behavior(name=behavior_name)
                        td_behavior.type = (
                            "zmk,behavior-tap-dance"  # Set type after creation
                        )
                        self.behaviors[behavior_name] = td_behavior  # Store it

                    bindings.append(Binding(behavior=td_behavior, params=params))
                    i += 1 + actual_params_consumed
                    continue  # Crucial: skip the generic param logic below

                elif behavior_name in ("kp", "mo", "to", "sl", "sk", "bt", "mkp"):
                    num_params_expected = 1
                elif behavior_name in (
                    "mt",
                    "hold-tap",
                    "mod-tap",
                ):  # recognize mt as hold-tap
                    num_params_expected = 2
                elif behavior_name in self.behaviors:
                    b_type = getattr(self.behaviors[behavior_name], "type", None)
                    if b_type == "hold-tap":
                        num_params_expected = 2
                    elif b_type == "macro":
                        num_params_expected = 0
                    # Add other known behaviors here...

                logging.debug(
                    f"[extractor] Token: {token}, behavior: {behavior_name}, expected params: {num_params_expected}"
                )

                # When resolving a binding, only allow behaviors explicitly defined by the user
                def get_or_create_behavior(name, type_str=None):
                    if name in self.behaviors:
                        return self.behaviors[name]

                    effective_name_for_lookup = type_str or name
                    mapped_type = BUILTIN_BEHAVIORS.get(effective_name_for_lookup)

                    if mapped_type:
                        b = Behavior(
                            name=name
                        )  # Use actual name for the behavior object
                        if effective_name_for_lookup in ("mt", "hold-tap", "mod-tap"):
                            b.type = "hold-tap"  # Canonical internal type
                        elif effective_name_for_lookup == "sk":
                            b.type = (
                                "zmk,behavior-sticky-key"  # Use ZMK compatible string
                            )
                        else:
                            b.type = mapped_type
                        self.behaviors[name] = b
                        return b

                    logging.error(
                        f"Unknown behavior referenced or failed to map: {name} "
                        f"(type_str hint: {type_str}). Creating as 'unknown-behavior'."
                    )
                    b = Behavior(name=name)
                    b.type = "unknown-behavior"  # Mark as unknown instead of crashing
                    self.behaviors[name] = b
                    return b

                # Enhanced parameter extraction for nested macros
                param_start_index = i + 1
                # actual_params_consumed = 0 # Already init above
                # params = [] # Already init above

                temp_params_for_non_td = []  # Use a temporary list here
                j = param_start_index
                while actual_params_consumed < num_params_expected and j < len(value):
                    next_token = value[j]
                    if (
                        isinstance(next_token, str)
                        and next_token.startswith("&")
                        # and actual_params_consumed < num_params_expected # This part of condition seems redundant with loop head
                    ):
                        break  # Stop if we hit another behavior token prematurely
                    # Detect nested macro/parenthesis
                    if isinstance(next_token, str) and (
                        "(" in next_token or ")" in next_token
                    ):
                        # Group tokens until parentheses are balanced
                        paren_count = 0
                        param_tokens = []
                        temp_j = j  # Use temp_j for this inner loop
                        while temp_j < len(value):
                            t = value[temp_j]
                            param_tokens.append(str(t))
                            paren_count += str(t).count("(")
                            paren_count -= str(t).count(")")
                            if paren_count <= 0 and ("(" in param_tokens[0]):
                                break
                            temp_j += 1
                        temp_params_for_non_td.append(" ".join(param_tokens))
                        actual_params_consumed += 1
                        j = temp_j + 1
                    else:
                        temp_params_for_non_td.append(str(next_token))
                        actual_params_consumed += 1
                        j += 1

                params = temp_params_for_non_td  # Assign collected params back

                logging.debug(
                    f"[extractor]   Params consumed for {behavior_name}: {params} (actual: {actual_params_consumed})"
                )
                behavior = get_or_create_behavior(behavior_name, behavior_name)
                bindings.append(Binding(behavior=behavior, params=params))
                i += 1 + actual_params_consumed
            else:
                # Unicode macro detection
                if is_unicode_binding(str(token)):
                    unicode_binding = UnicodeBinding.from_zmk(str(token))
                    bindings.append(unicode_binding)
                    continue
                bindings.append(self._create_binding(str(token)))
                i += 1

        # After main loop, patch any fallback bootloader/reset bindings
        for idx, b in enumerate(bindings):
            if (
                getattr(b, "behavior", None) is None
                and isinstance(getattr(b, "params", None), list)
                and len(b.params) == 1
                and b.params[0] in ("&bootloader", "&reset")
            ):
                behavior_name = b.params[0][1:]
                behavior = self.behaviors.get(behavior_name)
                if not behavior:
                    behavior = Behavior(name=behavior_name)
                    self.behaviors[behavior_name] = behavior
                bindings[idx] = Binding(behavior=behavior, params=[])
        return bindings

    def _create_binding(self, value: str | list[str]) -> Binding:
        """Create a binding instance from a value."""
        # Special handling for bootloader/reset as string or first list param
        behavior_name_to_check = None
        if isinstance(value, str) and value in ("&bootloader", "&reset"):
            behavior_name_to_check = value[1:]
        elif (
            isinstance(value, list)
            and value
            and isinstance(value[0], str)
            and value[0] in ("&bootloader", "&reset")
        ):
            behavior_name_to_check = value[0][1:]

        if behavior_name_to_check:
            behavior = self.behaviors.get(behavior_name_to_check)
            if not behavior:
                behavior = Behavior(name=behavior_name_to_check)
                self.behaviors[behavior_name_to_check] = behavior
            return Binding(behavior=behavior, params=[])

        if isinstance(value, list):
            if not value:
                msg = "Empty binding list value"
                logging.error(msg)
                return Binding(behavior=None, params=[f"ERROR: {msg}"])
            behavior_name = value[0]
            params = value[1:]
            hold_tap_names = {"mt", "hold-tap", "mod-tap", "hm", "hl", "sr", "td"}
            behavior = self.behaviors.get(behavior_name)
            is_hold_tap = False
            if behavior and hasattr(behavior, "type") and behavior.type == "hold-tap":
                is_hold_tap = True
            if behavior_name in hold_tap_names:
                is_hold_tap = True
            if is_hold_tap:
                if len(params) == 2 and all(params):
                    hold_key, tap_key = params
                    # Use the canonical behavior object if available
                    if (
                        behavior
                        and hasattr(behavior, "type")
                        and behavior.type == "hold-tap"
                    ):
                        behavior.hold_key = hold_key
                        behavior.tap_key = tap_key
                        return Binding(behavior=behavior, params=[hold_key, tap_key])
                    else:
                        tapping_term_ms = 200
                        flavor = "balanced"
                        if behavior and hasattr(behavior, "tapping_term_ms"):
                            tapping_term_ms = getattr(behavior, "tapping_term_ms")
                        if behavior and hasattr(behavior, "flavor"):
                            flavor = getattr(behavior, "flavor")
                        ht = HoldTap(
                            name=behavior_name,
                            hold_key=hold_key,
                            tap_key=tap_key,
                            tapping_term_ms=tapping_term_ms,
                            flavor=flavor,
                        )
                        ht.type = "hold-tap"
                        logging.debug(f"[extractor] Created HoldTap: {ht}")
                        return Binding(behavior=ht, params=[hold_key, tap_key])
                else:
                    msg = (
                        f"[extractor] Invalid hold-tap binding for '{behavior_name}': "
                        f"params={params}. Creating error binding."
                    )
                    logging.warning(msg)
                    return Binding(behavior=None, params=[f"ERROR: {msg}"])
            if behavior_name == "kp":
                if len(params) != 1:
                    msg = (
                        f"kp behavior expects 1 parameter, got {len(params)}: "
                        f"{params}"
                    )
                    logging.error(msg)
                    return Binding(behavior=None, params=[f"ERROR: {msg}"])
                return Binding(behavior=None, params=[params[0]])
            # Handle &sk LSHIFT case specifically before generic behavior handling
            if behavior_name == "sk" and len(params) == 1:
                behavior = self.behaviors.get(behavior_name)
                if not behavior:
                    behavior = Behavior(name=behavior_name)
                    behavior.type = (
                        "zmk,behavior-sticky-key"  # Ensure correct type for &sk
                    )
                    self.behaviors[behavior_name] = behavior
                return Binding(behavior=behavior, params=params)
            # Generic behavior handling using self.behaviors (populated by _parse_bindings)
            behavior = self.behaviors.get(behavior_name)
            if behavior:
                return Binding(behavior=behavior, params=params)
            else:
                msg = f"Unknown behavior referenced during binding creation: {behavior_name}"
                logging.error(msg)
                return Binding(behavior=None, params=[f"ERROR: {msg}"])
        elif isinstance(value, str):
            if value.startswith("&"):
                behavior_name = value[1:]
                if behavior_name == "kp":
                    msg = "&kp behavior requires a parameter"
                    logging.error(msg)
                    return Binding(behavior=None, params=[f"ERROR: {msg}"])
                behavior = self.behaviors.get(behavior_name)
                if behavior:
                    return Binding(behavior=behavior, params=[])
                else:
                    msg = f"Unknown parameterless behavior reference: {value}"
                    logging.error(msg)
                    return Binding(behavior=None, params=[f"ERROR: {msg}"])
            else:
                return Binding(behavior=None, params=[value])
        else:
            msg = f"Invalid type for _create_binding: {type(value)}"
            logging.error(msg)
            return Binding(behavior=None, params=[f"ERROR: {msg}"])

    def _parse_integer_prop(self, prop: DtsProperty) -> Optional[int]:
        """Safely parse an integer value from a property."""
        # Handle direct integer/scalar types from parser simplification
        if prop.type in ["integer", "scalar"]:
            try:
                return int(prop.value)
            except (ValueError, TypeError):
                return None
        # Handle case where parser left it as a single-element array
        elif (
            prop.type == "array"
            and isinstance(prop.value, list)
            and len(prop.value) == 1
        ):
            try:
                return int(prop.value[0])
            except (ValueError, TypeError):
                return None
        return None
