"""Tests for the DTS parser."""

import pytest
from converter.dts.parser import DtsParser, DtsNode, DtsProperty
from converter.dts.error_handler import DtsParseError


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
    ast = parser.parse(content)  # ast is DtsRoot, which is a DtsNode

    assert isinstance(ast, DtsNode)
    assert ast.name == "/"

    # Check keymap node
    assert "keymap" in ast.children
    keymap = ast.children["keymap"]
    assert isinstance(keymap, DtsNode)
    assert keymap.name == "keymap"

    # Check compatible property
    assert "compatible" in keymap.properties
    compatible = keymap.properties["compatible"]
    assert isinstance(compatible, DtsProperty)
    assert compatible.type == "string"
    assert compatible.value == "zmk,keymap"

    # Check default_layer node (child of keymap)
    assert "default_layer" in keymap.children
    layer = keymap.children["default_layer"]
    assert isinstance(layer, DtsNode)
    assert layer.name == "default_layer"

    # Check bindings property
    assert "bindings" in layer.properties
    bindings = layer.properties["bindings"]
    assert isinstance(bindings, DtsProperty)
    assert bindings.type == "array"
    assert bindings.value == ["&kp", "A", "&kp", "B", "&kp", "C"]


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
    ast = parser.parse(content)  # ast is DtsRoot

    # Check behaviors node
    assert "behaviors" in ast.children
    behaviors = ast.children["behaviors"]

    # Check mod_tap node
    assert "mod_tap" in behaviors.children
    mod_tap = behaviors.children["mod_tap"]
    assert isinstance(mod_tap, DtsNode)
    assert mod_tap.name == "mod_tap"
    assert "mt" in mod_tap.labels  # Labels are on the DtsNode itself

    # Check properties
    assert "compatible" in mod_tap.properties
    compatible = mod_tap.properties["compatible"]
    assert compatible.type == "string"
    assert compatible.value == "zmk,behavior-hold-tap"

    assert "tapping-term-ms" in mod_tap.properties
    tapping_term = mod_tap.properties["tapping-term-ms"]
    assert (
        tapping_term.type == "array"
    )  # DTS properties like <200> are parsed as arrays
    assert tapping_term.value == [200]


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
    ast = parser.parse(content)  # ast is DtsRoot

    # Check reference property
    assert "node1" in ast.children
    node1 = ast.children["node1"]
    assert "prop1" in node1.properties
    assert node1.properties["prop1"].value == "&label1"  # References include '&'
    assert node1.properties["prop1"].type == "reference"

    # Check referenced node via DtsRoot's label_to_node map
    assert "label1" in ast.label_to_node
    node2 = ast.label_to_node["label1"]
    assert node2.name == "node2"
    assert "prop2" in node2.properties
    assert node2.properties["prop2"].value == "value2"


def test_parse_error_handling():
    """Test error handling in DTS parsing."""
    parser = DtsParser()

    with pytest.raises(DtsParseError, match="DTS must start with root node '/'"):
        parser.parse("node1 { };")

    with pytest.raises(DtsParseError) as excinfo:
        parser.parse('/ { prop1 = "value1; };')
    # Accept either the old or new error message
    assert "Unterminated string" in str(
        excinfo.value
    ) or "Expected '{ ' after node" in str(excinfo.value)

    with pytest.raises(DtsParseError, match="Unterminated array"):
        parser.parse("/ { prop1 = <1 2 3; };")

    # This error message comes from _parse_property_value
    with pytest.raises(DtsParseError, match="Invalid property value: value1"):
        parser.parse("/ { prop1 = value1 };")

    # Check that 'node1;' is correctly parsed as a boolean property
    # and does not raise an error expecting '{'
    parsed_node1_boolean = parser.parse("/ { node1; };")
    assert "node1" in parsed_node1_boolean.properties
    assert "node1" not in parsed_node1_boolean.children


def test_parse_complex_dts():
    """Test parsing a complex DTS file."""
    content = """
    / {
        node1 {
            prop1 = "value1";
            prop2 = <1 2 3>;
            node2 {
                prop3 = 42; // Parsed as integer if not in < >
            };
        };
        node3: node3_label { // Changed node name to avoid conflict if node3 is also a label
            prop4 = &node1;
            node4 {
                prop5 = "value5";
            };
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)  # ast is DtsRoot

    assert ast.name == "/"
    assert "node1" in ast.children
    assert "node3_label" in ast.children  # Node is named node3_label

    node1 = ast.children["node1"]
    assert node1.properties["prop1"].value == "value1"
    assert node1.properties["prop2"].value == [1, 2, 3]
    assert "node2" in node1.children
    assert node1.children["node2"].properties["prop3"].value == 42  # Will be integer
    assert node1.children["node2"].properties["prop3"].type == "integer"

    node3 = ast.children["node3_label"]
    assert "node3" in node3.labels  # label is "node3"
    assert node3.properties["prop4"].value == "&node1"
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
    ast = parser.parse(content)  # ast is DtsRoot

    node1 = ast.children["node1"]
    node2 = node1.children["node2"]
    node3 = node2.children["node3"]
    node4 = node3.children["node4"]

    assert node4.properties["prop1"].value == "value1"
    assert node4.properties["prop1"].type == "string"


def test_parse_multiple_labels():
    """Test parsing nodes with multiple labels."""
    content = """
    / {
        label1: label2: node_alpha {
            prop1 = "value1";
        };
        label3: label4: label5: node_beta {
            prop2 = "value2";
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)  # ast is DtsRoot

    assert "label1" in ast.label_to_node
    assert "label2" in ast.label_to_node
    assert "label3" in ast.label_to_node
    assert "label4" in ast.label_to_node
    assert "label5" in ast.label_to_node

    node_alpha = ast.label_to_node["label1"]
    assert node_alpha.name == "node_alpha"
    assert node_alpha.properties["prop1"].value == "value1"
    assert ast.label_to_node["label2"] == node_alpha

    node_beta = ast.label_to_node["label3"]
    assert node_beta.name == "node_beta"
    assert node_beta.properties["prop2"].value == "value2"
    assert ast.label_to_node["label4"] == node_beta
    assert ast.label_to_node["label5"] == node_beta


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
    ast = parser.parse(content)

    node1 = ast.children["node1"]
    assert node1.properties["prop1"].value == [1, 2, 3]
    assert node1.properties["prop2"].value == [4096, 8192, 12288]
    assert node1.properties["prop3"].value == [4294967295, 0]


def test_parse_boolean_properties():
    """Test parsing boolean properties."""
    content = """
    / {
        node1 {
            prop_true; // Boolean true
            prop_false = false; // Explicit false
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)

    node1 = ast.children["node1"]
    assert node1.properties["prop_true"].value is True
    assert node1.properties["prop_true"].type == "boolean"
    assert node1.properties["prop_false"].value is False
    assert node1.properties["prop_false"].type == "boolean"


def test_parse_empty_nodes_and_properties():
    """Test parsing empty nodes and properties."""
    content = """
    / {
        node_empty {};
        node_with_empty_props {
            empty_str = "";
            empty_arr = <>;
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)

    assert "node_empty" in ast.children
    assert len(ast.children["node_empty"].properties) == 0
    assert len(ast.children["node_empty"].children) == 0

    node_props = ast.children["node_with_empty_props"]
    assert node_props.properties["empty_str"].value == ""
    assert node_props.properties["empty_str"].type == "string"
    assert node_props.properties["empty_arr"].value == []
    assert node_props.properties["empty_arr"].type == "array"


def test_parse_comments():
    """Test parsing DTS with comments."""
    content = """
    /* This is a block comment */
    / { // Line comment after brace
        // Line comment before node
        node1 {
            /* Multi-line
               block comment */
            prop1 = "value1"; // Inline comment after property
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)

    node1 = ast.children["node1"]
    assert node1.properties["prop1"].value == "value1"
    assert node1.properties["prop1"].type == "string"


def test_parse_zmk_specific_constructs():
    """Test parsing ZMK-specific DTS constructs."""
    content = """
    / {
        layer_0 { // Node names can have underscores
            bindings = <&kp A &mt LEFT_SHIFT A &lt 1 B>;
        };
        keymap {
             compatible = "zmk,keymap";
             layer-1 { // Node names can have hyphens
                 bindings = <&kp C>;
                 sensor-bindings = <&scroll_up &scroll_down>;
             };
        };
        behaviors {
            hm: hold_mod {
                compatible = "zmk,behavior-hold-tap";
                #binding-cells = <2>; // Special property
                tapping-term-ms = <200>;
                bindings = <&kp>, <&kp>; // Array of cells
            };
            tap_dance_0: td0 {
                 compatible = "zmk,behavior-tap-dance";
                 #binding-cells = <0>;
                 tapping-term-ms = <200>;
                 bindings = <&kp A>, <&kp B>, <&kp C>;
            };
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)

    # Check layer_0
    layer_0 = ast.children["layer_0"]
    assert layer_0.properties["bindings"].value == [
        "&kp",
        "A",
        "&mt",
        "LEFT_SHIFT",
        "A",
        "&lt",
        1,
        "B",
    ]

    # Check keymap and layer-1
    keymap_node = ast.children["keymap"]
    layer_1 = keymap_node.children["layer-1"]
    assert layer_1.properties["bindings"].value == ["&kp", "C"]
    assert layer_1.properties["sensor-bindings"].value == ["&scroll_up", "&scroll_down"]

    # Check behaviors
    behaviors_node = ast.children["behaviors"]
    hm = behaviors_node.children["hold_mod"]
    assert "hm" in hm.labels
    assert hm.properties["compatible"].value == "zmk,behavior-hold-tap"
    assert hm.properties["#binding-cells"].value == [2]  # Parsed as array
    assert hm.properties["#binding-cells"].type == "array"
    assert hm.properties["tapping-term-ms"].value == [200]  # Parsed as array
    assert hm.properties["tapping-term-ms"].type == "array"
    assert hm.properties["bindings"].value == [
        "&kp",
        "&kp",
    ]  # Array of references, parser handles commas

    td0 = behaviors_node.children["td0"]
    assert "tap_dance_0" in td0.labels
    assert td0.properties["#binding-cells"].value == [0]
    assert td0.properties["bindings"].value == [
        "&kp",
        "A",
        "&kp",
        "B",
        "&kp",
        "C",
    ]


def test_parse_array_with_mixed_cell_types_and_references():
    """Test parsing arrays with mixed cell types including references."""
    content = """
    / {
        node_mixed {
            prop_mix = <&kp LCTRL 0x10 &some_label 255>;
        };
    };
    """
    parser = DtsParser()
    ast = parser.parse(content)

    node_mixed = ast.children["node_mixed"]
    prop = node_mixed.properties["prop_mix"]
    assert prop.type == "array"
    assert prop.value == ["&kp", "LCTRL", 0x10, "&some_label", 255]
