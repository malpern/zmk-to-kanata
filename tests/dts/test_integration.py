"""Integration tests for the DTS-based ZMK parser."""

import pytest
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.models import KeymapConfig, Layer, Binding, Behavior


def test_full_pipeline_simple_keymap():
    """Test the full pipeline with a simple keymap."""
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
    
    # Parse DTS
    parser = DtsParser()
    ast = parser.parse(content)
    
    # Extract keymap
    extractor = KeymapExtractor()
    config = extractor.extract(ast)
    
    # Verify results
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 1
    assert config.layers[0].name == "default_layer"
    assert len(config.layers[0].bindings) == 3
    
    # Check bindings
    for binding in config.layers[0].bindings:
        assert isinstance(binding, Binding)
        assert binding.behavior is None  # kp is built-in
        assert len(binding.params) == 1
        assert binding.params[0] in ["A", "B", "C"]


def test_full_pipeline_with_behaviors():
    """Test the full pipeline with behaviors."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
            macro: macro {
                compatible = "zmk,behavior-macro";
                bindings = <&kp A &kp B>;
            };
        };
        keymap {
            default_layer {
                bindings = <&mt LSHIFT A &macro>;
            };
        };
    };
    """
    
    # Parse DTS
    parser = DtsParser()
    ast = parser.parse(content)
    
    # Extract keymap
    extractor = KeymapExtractor()
    config = extractor.extract(ast)
    
    # Verify results
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 1
    assert len(config.behaviors) == 2
    
    # Check behaviors
    mt = next(b for b in config.behaviors if b.name == "mt")
    assert mt.tapping_term_ms == 200
    
    macro = next(b for b in config.behaviors if b.name == "macro")
    assert len(macro.bindings) == 2
    
    # Check layer bindings
    layer = config.layers[0]
    assert len(layer.bindings) == 2
    
    # First binding should be mod-tap
    mt_binding = layer.bindings[0]
    assert mt_binding.behavior == mt
    assert mt_binding.params == ["LSHIFT", "A"]
    
    # Second binding should be macro
    macro_binding = layer.bindings[1]
    assert macro_binding.behavior == macro
    assert not macro_binding.params


def test_full_pipeline_multiple_layers():
    """Test the full pipeline with multiple layers."""
    content = """
    / {
        keymap {
            default_layer {
                bindings = <&kp A &kp B>;
            };
            lower_layer {
                bindings = <&kp C &kp D>;
            };
            raise_layer {
                bindings = <&kp E &kp F>;
            };
        };
    };
    """
    
    # Parse DTS
    parser = DtsParser()
    ast = parser.parse(content)
    
    # Extract keymap
    extractor = KeymapExtractor()
    config = extractor.extract(ast)
    
    # Verify results
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 3
    
    # Check layer names
    layer_names = {layer.name for layer in config.layers}
    assert layer_names == {"default_layer", "lower_layer", "raise_layer"}
    
    # Check each layer
    for layer in config.layers:
        assert len(layer.bindings) == 2
        for binding in layer.bindings:
            assert isinstance(binding, Binding)
            assert binding.behavior is None  # kp is built-in
            assert len(binding.params) == 1


def test_full_pipeline_complex_bindings():
    """Test the full pipeline with complex bindings."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
            lt: layer_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
        };
        keymap {
            default_layer {
                bindings = <
                    &mt LSHIFT A
                    &lt 1 B
                    &kp C
                >;
            };
        };
    };
    """
    
    # Parse DTS
    parser = DtsParser()
    ast = parser.parse(content)
    
    # Extract keymap
    extractor = KeymapExtractor()
    config = extractor.extract(ast)
    
    # Verify results
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 1
    assert len(config.behaviors) == 2
    
    # Check behaviors
    mt = next(b for b in config.behaviors if b.name == "mt")
    lt = next(b for b in config.behaviors if b.name == "lt")
    
    # Check layer bindings
    layer = config.layers[0]
    assert len(layer.bindings) == 3
    
    # First binding should be mod-tap
    mt_binding = layer.bindings[0]
    assert mt_binding.behavior == mt
    assert mt_binding.params == ["LSHIFT", "A"]
    
    # Second binding should be layer-tap
    lt_binding = layer.bindings[1]
    assert lt_binding.behavior == lt
    assert lt_binding.params == ["1", "B"]
    
    # Third binding should be key-press
    kp_binding = layer.bindings[2]
    assert kp_binding.behavior is None
    assert kp_binding.params == ["C"]


def test_full_pipeline_error_handling():
    """Test error handling in the full pipeline."""
    # Test missing root node
    content = "node1 { };"
    parser = DtsParser()
    with pytest.raises(ValueError, match="Expected root node"):
        parser.parse(content)
    
    # Test invalid property assignment
    content = """
    / {
        node1 {
            prop1 = value1
        };
    };
    """
    with pytest.raises(ValueError, match="Expected ';' after property value"):
        parser.parse(content)
    
    # Test invalid node
    content = """
    / {
        node1;
    };
    """
    with pytest.raises(ValueError, match="Expected '{' after node name"):
        parser.parse(content) 