"""Tests for the LayerParser class."""

import pytest
from ..layer_parser import LayerParser


def test_extract_keymap():
    """Test extracting keymap section from ZMK content."""
    parser = LayerParser()
    
    # Valid keymap
    valid_input = '''
    / {
        keymap {
            compatible = "zmk,keymap";
            layer_content
        };
    };
    '''
    result = parser.extract_keymap(valid_input)
    assert result is not None
    assert "layer_content" in result
    
    # Invalid keymap (missing compatible line)
    invalid_input = '''
    / {
        keymap {
            layer_content
        };
    };
    '''
    assert parser.extract_keymap(invalid_input) is None


def test_extract_layers():
    """Test extracting layers from keymap content."""
    parser = LayerParser()
    
    keymap_content = '''
        default_layer {
            bindings = <
                &kp A &kp B
            >;
        };
        
        num_layer {
            bindings = <
                &kp N1 &kp N2
            >;
        };
    '''
    
    layers = parser.extract_layers(keymap_content)
    assert len(layers) == 2
    
    default_layer = next(layer for layer in layers if layer.name == "default")
    assert "&kp A &kp B" in default_layer.bindings
    
    num_layer = next(layer for layer in layers if layer.name == "num")
    assert "&kp N1 &kp N2" in num_layer.bindings


def test_parse_zmk_file():
    """Test parsing a complete ZMK file."""
    parser = LayerParser()
    
    valid_input = '''
    / {
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &kp A &kp B
                    &kp C &mo 1
                >;
            };
            
            num_layer {
                bindings = <
                    &kp N1 &kp N2
                    &trans &mo 2
                >;
            };
        };
    };
    '''
    
    layers = parser.parse_zmk_file(valid_input)
    assert len(layers) == 2
    assert any(layer.name == "default" for layer in layers)
    assert any(layer.name == "num" for layer in layers)
    
    # Test invalid input
    with pytest.raises(ValueError):
        parser.parse_zmk_file("invalid content") 