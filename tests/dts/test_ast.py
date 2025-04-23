"""Tests for DTS AST node definitions."""

from converter.dts.ast import DtsNode, DtsProperty, DtsRoot


def test_dts_property_creation():
    """Test creating DTS properties with different types."""
    # String property
    str_prop = DtsProperty("name", "value", "string")
    assert str_prop.name == "name"
    assert str_prop.value == "value"
    assert str_prop.type == "string"

    # Integer property
    int_prop = DtsProperty("size", 42, "integer")
    assert int_prop.name == "size"
    assert int_prop.value == 42
    assert int_prop.type == "integer"

    # Array property
    array_prop = DtsProperty("values", [1, 2, 3], "array")
    assert array_prop.name == "values"
    assert array_prop.value == [1, 2, 3]
    assert array_prop.type == "array"


def test_dts_node_creation():
    """Test creating and manipulating DTS nodes."""
    # Create root node
    root = DtsNode("/")
    assert root.name == "/"
    assert not root.parent
    assert not root.children
    assert not root.properties
    assert not root.labels

    # Add child node
    child = DtsNode("child")
    root.add_child(child)
    assert child in root.children.values()
    assert child.parent == root

    # Add property
    prop = DtsProperty("test", "value", "string")
    root.add_property(prop)
    assert prop in root.properties.values()

    # Add label
    root.add_label("test_label")
    assert "test_label" in root.labels


def test_dts_node_find():
    """Test finding nodes by path."""
    # Create a simple tree
    root = DtsNode("/")
    keymap = DtsNode("keymap")
    default_layer = DtsNode("default_layer")

    root.add_child(keymap)
    keymap.add_child(default_layer)

    # Test finding nodes
    assert root.find_node("/") == root
    assert root.find_node("/keymap") == keymap
    assert root.find_node("/keymap/default_layer") == default_layer
    assert root.find_node("/nonexistent") is None


def test_dts_root_creation():
    """Test creating and using DTS root."""
    # Create a simple tree
    root_node = DtsNode("/")
    keymap = DtsNode("keymap")
    kp = DtsNode("key_press")

    root_node.add_child(keymap)
    root_node.add_child(kp)
    kp.add_label("kp")

    # Create root
    root = DtsRoot(root_node)

    # Test finding nodes
    assert root.find_node("/keymap") == keymap
    assert root.find_node("/key_press") == kp

    # Test resolving references
    assert root.resolve_reference("&kp") == kp
    assert root.resolve_reference("&nonexistent") is None


def test_dts_root_label_map():
    """Test label mapping in DTS root."""
    # Create a tree with labeled nodes
    root_node = DtsNode("/")
    kp = DtsNode("key_press")
    mt = DtsNode("mod_tap")

    root_node.add_child(kp)
    root_node.add_child(mt)
    kp.add_label("kp")
    mt.add_label("mt")

    # Create root and verify label map
    root = DtsRoot(root_node)
    assert root.label_to_node["kp"] == kp
    assert root.label_to_node["mt"] == mt
    assert len(root.label_to_node) == 2
