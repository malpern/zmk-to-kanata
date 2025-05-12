"""AST node definitions for DTS parsing."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


@dataclass
class DtsProperty:
    """Represents a property in a DTS node.

    Properties can have different types of values:
    - Strings: "value"
    - Integers: <1 2 3>
    - References: &label
    - Boolean: property-present;
    """

    name: str
    value: Union[str, List[str], int, List[int], bool]
    type: str  # "string", "integer", "reference", "boolean", "array"


@dataclass
class DtsNode:
    """Represents a node in the DTS AST.

    Nodes can have:
    - Properties (key-value pairs)
    - Children (nested nodes)
    - Labels (for references)
    - Parent node (for tree traversal)
    """

    name: str
    parent: Optional["DtsNode"] = None
    children: Dict[str, "DtsNode"] = field(default_factory=dict)
    properties: Dict[str, DtsProperty] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

    def add_child(self, child: "DtsNode") -> None:
        """Add a child node to this node."""
        child.parent = self
        self.children[child.name] = child

    def add_property(self, prop: DtsProperty) -> None:
        """Add a property to this node."""
        self.properties[prop.name] = prop

    def add_label(self, label: str) -> None:
        """Add a label to this node."""
        self.labels[label] = self.name

    def find_node(self, path: str) -> Optional["DtsNode"]:
        """Find a node by its path.

        Args:
            path: Node path (e.g., "/keymap/default_layer")

        Returns:
            The node if found, None otherwise
        """
        if not path or path == "/":
            return self

        parts = [p for p in path.split("/") if p]
        current = self

        for part in parts:
            if part in current.children:
                current = current.children[part]
            elif part in current.labels:
                label_name = current.labels[part]
                if label_name in current.children:
                    current = current.children[label_name]
                else:
                    return None
            else:
                return None

        return current


@dataclass
class DtsRoot(DtsNode):
    """Root of the DTS AST.

    Contains the root node and maintains a mapping of labels to nodes
    for efficient reference resolution.
    """

    label_to_node: Dict[str, DtsNode] = field(default_factory=dict)

    def __init__(self, root: DtsNode):
        """Initialize the root node.

        Args:
            root: The root node to wrap
        """
        super().__init__(
            name="/",
            parent=None,
            children=root.children,
            properties=root.properties,
            labels=root.labels,
        )
        self.label_to_node = dict()  # Explicitly initialize the field
        self._build_label_map(self)

    def _build_label_map(self, node: DtsNode) -> None:
        """Build the label-to-node mapping by traversing the tree."""
        for label in node.labels:
            self.label_to_node[label] = node
        for child in node.children.values():
            self._build_label_map(child)

    def resolve_reference(self, ref: str) -> Optional[DtsNode]:
        """Resolve a reference to a node.

        Args:
            ref: Reference string (e.g., "&kp")

        Returns:
            The referenced node if found, None otherwise
        """
        if not ref.startswith("&"):
            return None
        label = ref[1:]  # Remove the & prefix
        return self.label_to_node.get(label)
