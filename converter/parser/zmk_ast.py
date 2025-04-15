"""Module defining Abstract Syntax Tree (AST) structures for ZMK configuration files."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any
from converter.parser.zmk_lexer import SourceLocation


class NodeType(Enum):
    """Enum defining different types of AST nodes."""

    ROOT = auto()
    BEHAVIORS_BLOCK = auto()
    KEYMAP_BLOCK = auto()
    LAYER_DEF = auto()
    BEHAVIOR_DEF = auto()
    BINDING = auto()
    BINDING_PARAM = auto()
    MACRO_DEF = auto()
    MACRO_STEP = auto()
    KEY_PRESS = auto()
    COMBO_DEF = auto()
    CONDITIONAL_LAYER = auto()


@dataclass
class ASTNode:
    """Base class for all AST nodes."""

    node_type: NodeType
    location: Optional[SourceLocation] = None

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f"{self.node_type.name}"


@dataclass
class ZMKParameter:
    """Represents a parameter in ZMK configuration."""

    name: str
    value: Any
    location: Optional[SourceLocation] = None

    def __str__(self) -> str:
        """Return string representation of the parameter."""
        return f"{self.name} = {self.value}"


class ZMKDocument(ASTNode):
    """Root node for a ZMK configuration document."""

    behaviors: Optional["ZMKBehaviorsBlock"] = None
    keymap: Optional["ZMKKeymapBlock"] = None
    macros: Optional["ZMKMacrosBlock"] = None
    combos: Optional["ZMKCombosBlock"] = None
    conditional_layers: Optional["ZMKConditionalLayersBlock"] = None

    def __init__(self):
        """Initialize ZMK document."""
        super().__init__(NodeType.ROOT)

    def __str__(self) -> str:
        """Return string representation of the document."""
        result = "ZMK Document:\n"
        if self.behaviors:
            result += f"  {self.behaviors}\n"
        if self.keymap:
            result += f"  {self.keymap}\n"
        if self.macros:
            result += f"  {self.macros}\n"
        if self.combos:
            result += f"  {self.combos}\n"
        if self.conditional_layers:
            result += f"  {self.conditional_layers}\n"
        return result


class ZMKBehaviorsBlock(ASTNode):
    """Represents a behaviors block in ZMK configuration."""

    behaviors: Dict[str, "ZMKBehaviorDefinition"]

    def __init__(self):
        """Initialize behaviors block."""
        super().__init__(NodeType.BEHAVIORS_BLOCK)
        self.behaviors = {}

    def __str__(self) -> str:
        """Return string representation of the behaviors block."""
        result = "Behaviors:\n"
        for name, behavior in self.behaviors.items():
            result += f"    {name}: {behavior}\n"
        return result


class ZMKBehaviorDefinition(ASTNode):
    """Represents a behavior definition in ZMK configuration."""

    name: str
    behavior_type: str
    parameters: List[ZMKParameter]

    def __init__(self, name: str, behavior_type: str):
        """Initialize behavior definition."""
        super().__init__(NodeType.BEHAVIOR_DEF)
        self.name = name
        self.behavior_type = behavior_type
        self.parameters = []

    def __str__(self) -> str:
        """Return string representation of the behavior definition."""
        param_str = ", ".join(str(p) for p in self.parameters)
        return f"{self.behavior_type} ({param_str})"


class ZMKKeymapBlock(ASTNode):
    """Represents a keymap block in ZMK configuration."""

    layers: Dict[str, "ZMKLayerDefinition"]

    def __init__(self):
        """Initialize keymap block."""
        super().__init__(NodeType.KEYMAP_BLOCK)
        self.layers = {}

    def __str__(self) -> str:
        """Return string representation of the keymap block."""
        result = "Keymap:\n"
        for name, layer in self.layers.items():
            result += f"    {name}: {layer}\n"
        return result


class ZMKLayerDefinition(ASTNode):
    """Represents a layer definition in ZMK configuration."""

    name: str
    bindings: List["ZMKBinding"]

    def __init__(self, name: str):
        """Initialize layer definition."""
        super().__init__(NodeType.LAYER_DEF)
        self.name = name
        self.bindings = []

    def __str__(self) -> str:
        """Return string representation of the layer definition."""
        binding_str = "\n        ".join(str(b) for b in self.bindings)
        return f"Layer {self.name}:\n        {binding_str}"


@dataclass
class ZMKBindingParameter:
    """Represents a parameter to a binding, which can be complex."""

    value: Union[str, "ZMKModifierExpression"]
    location: Optional[SourceLocation] = None

    def __str__(self) -> str:
        """Return string representation of the binding parameter."""
        return str(self.value)


@dataclass
class ZMKModifierExpression:
    """Represents a complex modifier expression like LC(LS(LALT))."""

    modifier: str
    params: List[Union[str, "ZMKModifierExpression"]] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    def __str__(self) -> str:
        """Return string representation of the modifier expression."""
        param_str = ", ".join(str(p) for p in self.params)
        return f"{self.modifier}({param_str})"


class ZMKBinding(ASTNode):
    """Represents a binding in ZMK configuration."""

    behavior: str
    params: List[ZMKBindingParameter]
    # Valid behaviors and expected parameter counts
    VALID_BEHAVIORS = {
        "kp": 1,
        "mt": 2,
        "hm": 2,
        "hs": 2,
        "td": 2,
        "mo": 1,
        "to": 1,
        "tog": 1,
        "trans": 0,
    }

    def __init__(self, behavior: str):
        """Initialize binding."""
        super().__init__(NodeType.BINDING)
        self.behavior = behavior
        self.params = []

    def validate(self) -> bool:
        """Validate the binding: behavior and parameter count."""
        if self.behavior not in self.VALID_BEHAVIORS:
            return False
        expected = self.VALID_BEHAVIORS[self.behavior]
        return len(self.params) == expected

    def __str__(self) -> str:
        """Return string representation of the binding."""
        param_str = " ".join(str(p) for p in self.params)
        return f"&{self.behavior} {param_str}".strip()


class ZMKMacrosBlock(ASTNode):
    """Represents a macros block in ZMK configuration."""

    macros: Dict[str, "ZMKMacroDefinition"]

    def __init__(self):
        """Initialize macros block."""
        super().__init__(NodeType.MACRO_DEF)
        self.macros = {}

    def __str__(self) -> str:
        """Return string representation of the macros block."""
        result = "Macros:\n"
        for name, macro in self.macros.items():
            result += f"    {name}: {macro}\n"
        return result


class ZMKMacroDefinition(ASTNode):
    """Represents a macro definition in ZMK configuration."""

    name: str
    steps: List["ZMKMacroStep"]
    label: Optional[str] = None
    compatible: Optional[str] = None

    def __init__(self, name: str):
        """Initialize macro definition."""
        super().__init__(NodeType.MACRO_DEF)
        self.name = name
        self.steps = []
        self.label = None
        self.compatible = None

    def __str__(self) -> str:
        """Return string representation of the macro definition."""
        parts = []
        if self.label:
            parts.append(f'label="{self.label}"')
        if self.compatible:
            parts.append(f'compatible="{self.compatible}"')
        step_str = ", ".join(str(s) for s in self.steps)
        parts.append(f"steps=[{step_str}]")
        details = ", ".join(parts)
        return f"Macro {self.name}: {details}"


class ZMKMacroStep(ASTNode):
    """Represents a step in a macro definition."""

    action: str
    param: Optional[str]

    def __init__(self, action: str, param: Optional[str] = None):
        """Initialize macro step."""
        super().__init__(NodeType.MACRO_STEP)
        self.action = action
        self.param = param

    def __str__(self) -> str:
        """Return string representation of the macro step."""
        if self.param:
            return f"{self.action}({self.param})"
        return self.action


class ZMKCombosBlock(ASTNode):
    """Represents a combos block in ZMK configuration."""

    combos: Dict[str, "ZMKComboDefinition"]

    def __init__(self):
        """Initialize combos block."""
        super().__init__(NodeType.COMBO_DEF)
        self.combos = {}

    def __str__(self) -> str:
        """Return string representation of the combos block."""
        result = "Combos:\n"
        for name, combo in self.combos.items():
            result += f"    {name}: {combo}\n"
        return result


class ZMKComboDefinition(ASTNode):
    """Represents a combo definition in ZMK configuration."""

    name: str
    timeout_ms: int
    key_positions: List[int]
    bindings: List[ZMKBinding]
    layers: List[int]

    def __init__(self, name: str):
        """Initialize combo definition."""
        super().__init__(NodeType.COMBO_DEF)
        self.name = name
        self.timeout_ms = 0
        self.key_positions = []
        self.bindings = []
        self.layers = []

    def __str__(self) -> str:
        """Return string representation of the combo definition."""
        pos_str = ", ".join(str(p) for p in self.key_positions)
        bind_str = ", ".join(str(b) for b in self.bindings)
        layer_str = ", ".join(str(layer) for layer in self.layers)
        return f"Combo {self.name}: timeout={self.timeout_ms}, pos=[{pos_str}], bindings=[{bind_str}], layers=[{layer_str}]"


class ZMKConditionalLayersBlock(ASTNode):
    """Represents a conditional_layers block in ZMK configuration."""

    conditional_layers: Dict[str, "ZMKConditionalLayerDefinition"]

    def __init__(self):
        """Initialize conditional layers block."""
        super().__init__(NodeType.CONDITIONAL_LAYER)
        self.conditional_layers = {}

    def __str__(self) -> str:
        """Return string representation of the conditional layers block."""
        result = "Conditional Layers:\n"
        for name, cond_layer in self.conditional_layers.items():
            result += f"    {name}: {cond_layer}\n"
        return result


class ZMKConditionalLayerDefinition(ASTNode):
    """Represents a conditional layer definition in ZMK configuration."""

    name: str
    if_layers: List[int]
    then_layer: int

    def __init__(self, name: str):
        """Initialize conditional layer definition."""
        super().__init__(NodeType.CONDITIONAL_LAYER)
        self.name = name
        self.if_layers = []
        self.then_layer = -1

    def __str__(self) -> str:
        """Return string representation of the conditional layer definition."""
        if_str = ", ".join(str(layer) for layer in self.if_layers)
        return f"Conditional Layer {self.name}: if [{if_str}] then {self.then_layer}"
