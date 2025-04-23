"""Tests for the DTS parser."""

import pytest
from converter.dts.parser import DtsParser, DtsNode, DtsProperty


def test_parse_simple_dts():
    """Test parsing a simple DTS file."""
    content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&kp A &kp B &kp C>;
            };
        };
    };
    """
    
    parser = DtsParser()
    ast = parser.parse(content)
    
    assert isinstance(ast.root, DtsNode)
    assert ast.root.name == "/"
    
    # Check keymap node
    assert "keymap" in ast.root.children
    keymap = ast.root.children["keymap"]
    assert isinstance(keymap, DtsNode)
    assert keymap.name == "keymap"
    
    # Check compatible property
    assert "compatible" in keymap.properties
    compatible = keymap.properties["compatible"]
    assert isinstance(compatible, DtsProperty)
    assert compatible.type == "string"
    assert compatible.value == "zmk,keymap"
    
    # Check default_layer node
    assert "default_layer" in keymap.children
    layer = keymap.children["default_layer"]
    assert isinstance(layer, DtsNode)
    assert layer.name == "default_layer"
    
    # Check bindings property
    assert "bindings" in layer.properties
    bindings = layer.properties["bindings"]
    assert isinstance(bindings, DtsProperty)
    assert bindings.type == "array"
    assert bindings.value == "<&kp A &kp B &kp C>"


def test_parse_with_labels():
    """Test parsing DTS with labels."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
        };
    };
    """
    
    parser = DtsParser()
    ast = parser.parse(content)
    
    # Check behaviors node
    assert "behaviors" in ast.root.children
    behaviors = ast.root.children["behaviors"]
    
    # Check mod_tap node
    assert "mod_tap" in behaviors.children
    mod_tap = behaviors.children["mod_tap"]
    assert isinstance(mod_tap, DtsNode)
    assert mod_tap.name == "mod_tap"
    assert "mt" in mod_tap.labels
    
    # Check properties
    assert "compatible" in mod_tap.properties
    compatible = mod_tap.properties["compatible"]
    assert compatible.type == "string"
    assert compatible.value == "zmk,behavior-hold-tap"
    
    assert "tapping-term-ms" in mod_tap.properties
    tapping_term = mod_tap.properties["tapping-term-ms"]
    assert tapping_term.type == "array"
    assert tapping_term.value == "<200>"


def test_parse_with_references():
    """Test parsing DTS with references."""
    content = """
    / {
        node1 {
            prop1 = &label1;
        };
        label1: node2 {
            prop2 = "value2";
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Check reference property
    node1 = root.root.children["node1"]
    assert node1.properties["prop1"].value == "label1"
    assert node1.properties["prop1"].type == "reference"
    
    # Check referenced node
    assert "label1" in root.label_to_node
    node2 = root.label_to_node["label1"]
    assert node2.name == "node2"
    assert node2.properties["prop2"].value == "value2"


def test_parse_error_handling():
    """Test error handling in DTS parsing."""
    parser = DtsParser()
    
    # Test missing root node
    with pytest.raises(ValueError, match="DTS must start with root node '/'"):
        parser.parse("node1 { };")
        
    # Test unterminated string
    with pytest.raises(ValueError, match="Unterminated string"):
        parser.parse('/ { prop1 = "value1; };')
        
    # Test unterminated array
    with pytest.raises(ValueError, match="Unterminated array"):
        parser.parse('/ { prop1 = <1 2 3; };')
        
    # Test invalid property assignment
    with pytest.raises(ValueError, match="Expected ';' after property value"):
        parser.parse('/ { prop1 = value1 };')
        
    # Test invalid node
    with pytest.raises(ValueError, match="Expected '{' after node name"):
        parser.parse('/ { node1; };')


def test_parse_complex_dts():
    """Test parsing a complex DTS file."""
    content = """
    / {
        node1 {
            prop1 = "value1";
            prop2 = <1 2 3>;
            node2 {
                prop3 = 42;
            };
        };
        node3: node3 {
            prop4 = &node1;
            node4 {
                prop5 = "value5";
            };
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Check root structure
    assert root.root.name == "/"
    assert "node1" in root.root.children
    assert "node3" in root.root.children
    
    # Check node1 and its children
    node1 = root.root.children["node1"]
    assert node1.properties["prop1"].value == "value1"
    assert node1.properties["prop2"].value == [1, 2, 3]
    assert "node2" in node1.children
    assert node1.children["node2"].properties["prop3"].value == 42
    
    # Check node3 and its children
    node3 = root.root.children["node3"]
    assert node3.properties["prop4"].value == "node1"
    assert node3.properties["prop4"].type == "reference"
    assert "node4" in node3.children
    assert node3.children["node4"].properties["prop5"].value == "value5"


def test_parse_nested_nodes():
    """Test parsing deeply nested nodes."""
    content = """
    / {
        node1 {
            node2 {
                node3 {
                    node4 {
                        prop1 = "value1";
                    };
                };
            };
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Check nested structure
    node1 = root.root.children["node1"]
    node2 = node1.children["node2"]
    node3 = node2.children["node3"]
    node4 = node3.children["node4"]
    
    assert node4.properties["prop1"].value == "value1"
    assert node4.properties["prop1"].type == "string"


def test_parse_multiple_labels():
    """Test parsing nodes with multiple labels."""
    content = """
    / {
        label1: label2: node1 {
            prop1 = "value1";
        };
        label3: label4: label5: node2 {
            prop2 = "value2";
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Check multiple label mappings
    assert "label1" in root.label_to_node
    assert "label2" in root.label_to_node
    assert "label3" in root.label_to_node
    assert "label4" in root.label_to_node
    assert "label5" in root.label_to_node
    
    # Verify all labels point to correct nodes
    node1 = root.label_to_node["label1"]
    assert node1.name == "node1"
    assert node1.properties["prop1"].value == "value1"
    
    node2 = root.label_to_node["label3"]
    assert node2.name == "node2"
    assert node2.properties["prop2"].value == "value2"


def test_parse_complex_arrays():
    """Test parsing complex array values."""
    content = """
    / {
        node1 {
            prop1 = <0x1 0x2 0x3>;
            prop2 = <0x1000 0x2000 0x3000>;
            prop3 = <0xFFFFFFFF 0x00000000>;
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    node1 = root.root.children["node1"]
    assert node1.properties["prop1"].value == [1, 2, 3]
    assert node1.properties["prop2"].value == [4096, 8192, 12288]
    assert node1.properties["prop3"].value == [4294967295, 0]


def test_parse_boolean_properties():
    """Test parsing boolean properties."""
    content = """
    / {
        node1 {
            prop1 = true;
            prop2 = false;
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    node1 = root.root.children["node1"]
    assert node1.properties["prop1"].value is True
    assert node1.properties["prop1"].type == "boolean"
    assert node1.properties["prop2"].value is False
    assert node1.properties["prop2"].type == "boolean"


def test_parse_empty_nodes():
    """Test parsing empty nodes and properties."""
    content = """
    / {
        node1 {
        };
        node2 {
            prop1 = "";
        };
        node3 {
            prop2 = <>;
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Check empty node
    assert "node1" in root.root.children
    assert len(root.root.children["node1"].properties) == 0
    
    # Check empty string property
    node2 = root.root.children["node2"]
    assert node2.properties["prop1"].value == ""
    assert node2.properties["prop1"].type == "string"
    
    # Check empty array property
    node3 = root.root.children["node3"]
    assert node3.properties["prop2"].value == []
    assert node3.properties["prop2"].type == "array"


def test_parse_comments():
    """Test parsing DTS with comments."""
    content = """
    /* This is a comment */
    / {
        // Another comment
        node1 {
            /* Multi-line
               comment */
            prop1 = "value1"; // Inline comment
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Verify content is parsed correctly despite comments
    node1 = root.root.children["node1"]
    assert node1.properties["prop1"].value == "value1"
    assert node1.properties["prop1"].type == "string"


def test_parse_zmk_specific():
    """Test parsing ZMK-specific DTS constructs."""
    content = """
    / {
        0_layer {
            bindings = <&kp &mt &lt>;
        };
        layer-1 {
            bindings = <1>, <2>, <3>;
        };
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                #binding-cells = <2>;
                tapping-term-ms = <200>;
                bindings = <&kp>, <&kp>;
            };
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    # Check layer with number in name
    layer0 = root.root.children["0_layer"]
    assert layer0.properties["bindings"].type == "array"
    assert layer0.properties["bindings"].value == ["kp", "mt", "lt"]
    
    # Check layer with hyphen in name
    layer1 = root.root.children["layer-1"]
    assert layer1.properties["bindings"].type == "array"
    assert layer1.properties["bindings"].value == [1, 2, 3]
    
    # Check behavior node
    behaviors = root.root.children["behaviors"]
    mt = behaviors.children["mod_tap"]
    assert mt.properties["compatible"].value == "zmk,behavior-hold-tap"
    assert mt.properties["#binding-cells"].value == 2
    assert mt.properties["tapping-term-ms"].value == 200
    assert mt.properties["bindings"].type == "array"
    assert mt.properties["bindings"].value == ["kp", "kp"]


def test_parse_mixed_arrays():
    """Test parsing arrays with mixed content types."""
    content = """
    / {
        node1 {
            prop1 = <1 &ref 2>;
            prop2 = <0xFF &kp 0x100>;
        };
    };
    """
    
    parser = DtsParser()
    root = parser.parse(content)
    
    node1 = root.root.children["node1"]
    assert node1.properties["prop1"].type == "array"
    assert node1.properties["prop1"].value == [1, "ref", 2]
    assert node1.properties["prop2"].type == "array"
    assert node1.properties["prop2"].value == [255, "kp", 256] 