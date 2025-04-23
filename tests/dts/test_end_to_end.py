"""End-to-end tests for the DTS-based ZMK parser using real keymap files."""

import pytest
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.models import KeymapConfig, Binding, Behavior


def test_simple_keymap():
    """Test parsing a simple keymap file."""
    content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify basic structure
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 1

    # Verify default layer
    default_layer_node = next(
        layer_node for layer_node in config.layers if layer_node.name == "default_layer"
    )
    assert len(default_layer_node.bindings) == 6

    # Verify bindings
    expected_key_codes = ["A", "B", "C", "D", "E", "F"]
    for binding_node, expected_key_code in zip(
        default_layer_node.bindings, expected_key_codes
    ):
        assert isinstance(binding_node, Binding)
        assert binding_node.behavior is None  # kp is built-in
        assert binding_node.params == [expected_key_code]


def test_complex_keymap_with_behaviors():
    """Test parsing a complex keymap with behaviors."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
                #binding-cells = <2>;
            };
            
            macro_a: macro_a {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <&kp A &kp B>;
            };
            
            lt: layer_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
                #binding-cells = <2>;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &mt LSHIFT A  &kp B        &macro_a
                    &kp D         &lt 1 E      &kp F
                >;
            };
            
            lower_layer {
                bindings = <
                    &kp N1  &kp N2  &kp N3
                    &kp N4  &kp N5  &kp N6
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify basic structure
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 2
    assert len(config.behaviors) == 3

    # Verify behaviors
    mt = next(b for b in config.behaviors if b.name == "mt")
    assert isinstance(mt, Behavior)
    assert mt.tapping_term_ms == 200

    lt = next(b for b in config.behaviors if b.name == "lt")
    assert isinstance(lt, Behavior)
    assert lt.tapping_term_ms == 200

    macro = next(b for b in config.behaviors if b.name == "macro_a")
    assert isinstance(macro, Behavior)
    assert len(macro.bindings) == 2

    # Verify default layer
    default_layer_node = next(
        layer_node for layer_node in config.layers if layer_node.name == "default_layer"
    )
    assert len(default_layer_node.bindings) == 6

    # Check specific bindings
    assert default_layer_node.bindings[0].behavior == mt
    assert default_layer_node.bindings[0].params == ["LSHIFT", "A"]

    assert default_layer_node.bindings[1].behavior is None  # kp is built-in
    assert default_layer_node.bindings[1].params == ["B"]

    assert default_layer_node.bindings[2].behavior == macro
    assert not default_layer_node.bindings[2].params

    assert default_layer_node.bindings[4].behavior == lt
    assert default_layer_node.bindings[4].params == ["1", "E"]

    # Verify lower layer
    lower_layer_node = next(
        layer_node for layer_node in config.layers if layer_node.name == "lower_layer"
    )
    assert len(lower_layer_node.bindings) == 6
    for binding_node in lower_layer_node.bindings:
        assert binding_node.behavior is None  # kp is built-in
        assert binding_node.params[0].startswith("N")


def test_keymap_with_unicode():
    """Test parsing a keymap with unicode behaviors."""
    content = """
    / {
        behaviors {
            unicode: unicode {
                compatible = "zmk,behavior-unicode";
                #binding-cells = <1>;
            };
            
            uc_string: unicode_string {
                compatible = "zmk,behavior-unicode-string";
                #binding-cells = <1>;
                strings = <
                    "smile" "😊"
                    "heart" "❤️"
                >;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &unicode U0001F600  &uc_string smile  &kp A
                    &unicode U2764      &uc_string heart  &kp B
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify behaviors
    assert len(config.behaviors) == 2

    unicode = next(b for b in config.behaviors if b.name == "unicode")
    assert isinstance(unicode, Behavior)

    uc_string = next(b for b in config.behaviors if b.name == "uc_string")
    assert isinstance(uc_string, Behavior)

    # Verify bindings
    layer_node = config.layers[0]
    assert len(layer_node.bindings) == 6

    assert layer_node.bindings[0].behavior == unicode
    assert layer_node.bindings[0].params == ["U0001F600"]

    assert layer_node.bindings[1].behavior == uc_string
    assert layer_node.bindings[1].params == ["smile"]


def test_error_handling():
    """Test error handling with malformed input."""
    # Test missing root node
    with pytest.raises(ValueError, match="Expected root node"):
        parser = DtsParser()
        parser.parse("keymap { };")

    # Test invalid property assignment
    with pytest.raises(ValueError, match="Expected ';' after property value"):
        parser = DtsParser()
        parser.parse(
            """
        / {
            keymap {
                prop = value
            };
        };
        """
        )

    # Test invalid binding format
    parser = DtsParser()
    ast = parser.parse(
        """
    / {
        keymap {
            default_layer {
                bindings = <&invalid_binding>;
            };
        };
    };
    """
    )
    extractor = KeymapExtractor()
    with pytest.raises(ValueError, match="Invalid binding format: invalid_binding"):
        extractor.extract(ast)


def test_keymap_with_combos():
    """Test parsing a keymap with combo behaviors."""
    content = """
    / {
        combos {
            compatible = "zmk,combos";
            combo_esc {
                timeout-ms = <50>;
                key-positions = <0 1>;
                bindings = <&kp ESC>;
            };
            combo_tab {
                timeout-ms = <50>;
                key-positions = <1 2>;
                bindings = <&kp TAB>;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify combos
    assert len(config.combos) == 2

    combo_esc = next(c for c in config.combos if c.name == "combo_esc")
    assert combo_esc.timeout_ms == 50
    assert combo_esc.key_positions == [0, 1]
    assert combo_esc.binding.params == ["ESC"]

    combo_tab = next(c for c in config.combos if c.name == "combo_tab")
    assert combo_tab.timeout_ms == 50
    assert combo_tab.key_positions == [1, 2]
    assert combo_tab.binding.params == ["TAB"]


def test_keymap_with_conditional_layers():
    """Test parsing a keymap with conditional layers."""
    content = """
    / {
        conditional_layers {
            compatible = "zmk,conditional-layers";
            tri_layer {
                if-layers = <1 2>;
                then-layer = <3>;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <&kp A &kp B>;
            };
            
            lower_layer {
                bindings = <&kp N1 &kp N2>;
            };
            
            raise_layer {
                bindings = <&kp F1 &kp F2>;
            };
            
            adjust_layer {
                bindings = <&reset &bootloader>;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify conditional layers
    assert len(config.conditional_layers) == 1

    tri_layer = config.conditional_layers[0]
    assert tri_layer.if_layers == [1, 2]
    assert tri_layer.then_layer == 3

    # Verify all layers exist
    assert len(config.layers) == 4
    layer_names = [layer_node.name for layer_node in config.layers]
    assert "default_layer" in layer_names
    assert "lower_layer" in layer_names
    assert "raise_layer" in layer_names
    assert "adjust_layer" in layer_names
