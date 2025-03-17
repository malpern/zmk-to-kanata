"""Unit tests for the layer parser module."""
import pytest


def test_extract_layers(basic_layer_parser):
    """Test extracting layers from keymap content."""
    keymap_content = """
    default_layer {
        bindings = <
            &kp A &kp B &kp C
            &kp D &kp E &kp F
        >;
    };
    """
    layers = basic_layer_parser.extract_layers(keymap_content)
    assert len(layers) == 1
    assert layers[0].name == "default"
    assert len(layers[0].bindings) == 6


def test_parse_zmk_file(basic_layer_parser):
    """Test parsing a complete ZMK file."""
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
            nav_layer {
                bindings = <
                    &kp LEFT &kp RIGHT &kp UP
                    &kp DOWN &kp HOME &kp END
                >;
            };
        };
    };
    """
    layers = basic_layer_parser.parse_zmk_file(zmk_content)
    assert len(layers) == 2
    assert layers[0].name == "default"
    assert layers[1].name == "nav"


def test_empty_layer(basic_layer_parser):
    """Test parsing an empty layer."""
    keymap_content = """
    empty_layer {
        bindings = <>;
    };
    """
    layers = basic_layer_parser.extract_layers(keymap_content)
    assert len(layers) == 1
    assert layers[0].name == "empty"
    assert len(layers[0].bindings) == 0


def test_invalid_layer_syntax(basic_layer_parser):
    """Test handling of invalid layer syntax."""
    invalid_content = """
    invalid_layer {
        bindings = <
            &kp A &kp B
        // Missing closing angle bracket and semicolon
    """
    with pytest.raises(ValueError, match="Invalid layer syntax"):
        basic_layer_parser.extract_layers(invalid_content)
