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
    default_layer = next(
        layer for layer in config.layers 
        if layer.name == "default_layer"
    )
    assert len(default_layer.bindings) == 6
    
    # Verify bindings
    expected_keys = ["A", "B", "C", "D", "E", "F"]
    for binding, expected_key in zip(default_layer.bindings, expected_keys):
        assert isinstance(binding, Binding)
        assert binding.behavior is None  # kp is built-in
        assert binding.params == [expected_key]


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
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &mt LSHIFT A  &kp B        &macro_a
                    &kp D         &mt LCTRL E  &kp F
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
    assert len(config.behaviors) == 2
    
    # Verify behaviors
    mt = next(b for b in config.behaviors if b.name == "mt")
    assert isinstance(mt, Behavior)
    assert mt.tapping_term_ms == 200
    
    macro = next(b for b in config.behaviors if b.name == "macro_a")
    assert isinstance(macro, Behavior)
    assert len(macro.bindings) == 2
    
    # Verify default layer
    default_layer = next(
        layer for layer in config.layers 
        if layer.name == "default_layer"
    )
    assert len(default_layer.bindings) == 6
    
    # Check specific bindings
    assert default_layer.bindings[0].behavior == mt
    assert default_layer.bindings[0].params == ["LSHIFT", "A"]
    
    assert default_layer.bindings[1].behavior is None  # kp is built-in
    assert default_layer.bindings[1].params == ["B"]
    
    assert default_layer.bindings[2].behavior == macro
    assert not default_layer.bindings[2].params
    
    # Verify lower layer
    lower_layer = next(
        layer for layer in config.layers 
        if layer.name == "lower_layer"
    )
    assert len(lower_layer.bindings) == 6
    for binding in lower_layer.bindings:
        assert binding.behavior is None  # kp is built-in
        assert binding.params[0].startswith("N")


def test_error_handling():
    """Test error handling with malformed input."""
    # Test missing root node
    with pytest.raises(ValueError, match="Expected root node"):
        parser = DtsParser()
        parser.parse("keymap { };")
    
    # Test invalid property assignment
    with pytest.raises(ValueError, match="Expected ';' after property value"):
        parser = DtsParser()
        parser.parse("""
        / {
            keymap {
                prop = value
            };
        };
        """)
    
    # Test invalid binding format
    parser = DtsParser()
    ast = parser.parse("""
    / {
        keymap {
            default_layer {
                bindings = <&invalid_binding>;
            };
        };
    };
    """)
    extractor = KeymapExtractor()
    with pytest.raises(
        ValueError, 
        match="Invalid binding format: invalid_binding"
    ):
        extractor.extract(ast) 