"""Unit tests for the layer transformer module."""
import pytest
from converter.layer_transformer import LayerTransformer
from converter.model.keymap_model import Layer, KeyMapping
from converter.behaviors.key_sequence import KeySequenceBinding


@pytest.fixture
def transformer():
    """Create a LayerTransformer instance."""
    return LayerTransformer()


def test_basic_key_transformations(transformer):
    """Test transformation of basic key types."""
    # Test letters
    assert transformer.transform_binding(KeyMapping(key="A")) == "a"
    assert transformer.transform_binding(KeyMapping(key="B")) == "b"

    # Test numbers
    assert transformer.transform_binding(KeyMapping(key="N1")) == "1"
    assert transformer.transform_binding(KeyMapping(key="N0")) == "0"
    assert transformer.transform_binding(KeyMapping(key="KP_N7")) == "kp7"

    # Test function keys
    assert transformer.transform_binding(KeyMapping(key="F1")) == "f1"
    assert transformer.transform_binding(KeyMapping(key="F12")) == "f12"

    # Test navigation keys
    assert transformer.transform_binding(KeyMapping(key="ENTER")) == "enter"
    assert transformer.transform_binding(KeyMapping(key="SPACE")) == "space"
    assert transformer.transform_binding(KeyMapping(key="PG_UP")) == "pg_up"


def test_special_key_transformations(transformer):
    """Test transformation of special key types."""
    # Test symbols and punctuation
    assert transformer.transform_binding(
        KeyMapping(key="EXCL")
    ) == "excl"
    assert transformer.transform_binding(
        KeyMapping(key="MINUS")
    ) == "minus"
    assert transformer.transform_binding(KeyMapping(key="PLUS")) == "plus"
    assert transformer.transform_binding(KeyMapping(key="DOT")) == "dot"

    # Test modifiers
    assert transformer.transform_binding(KeyMapping(key="LSHIFT")) == "lshift"
    assert transformer.transform_binding(KeyMapping(key="RGUI")) == "rgui"

    # Test system and media
    assert transformer.transform_binding(
        KeyMapping(key="C_MUTE")
    ) == "c_mute"
    assert transformer.transform_binding(
        KeyMapping(key="C_VOL_UP")
    ) == "c_vol_up"

    # Test numpad special keys
    assert transformer.transform_binding(
        KeyMapping(key="KP_PLUS")
    ) == "kp_plus"
    assert transformer.transform_binding(KeyMapping(key="KP_DOT")) == "kp_dot"


def test_layer_control_transformations(transformer):
    """Test transformation of layer control bindings."""
    # Test layer momentary switch
    assert transformer.transform_binding(KeyMapping(key="mo 1")) == "@layer1"
    assert transformer.transform_binding(KeyMapping(key="mo 2")) == "@layer2"

    # Test transparent key
    assert transformer.transform_binding(KeyMapping(key="trans")) == "_"

    # Test sticky key
    assert transformer.transform_binding(
        KeyMapping(key="sk LSHIFT")
    ) == "sticky-lsft"

    # Test unknown binding
    assert transformer.transform_binding(
        KeyMapping(key="unknown X")
    ) == "unknown x"


def test_key_sequence_transformations(transformer):
    """Test transforming key sequence bindings."""
    # Test basic key sequence
    key_sequence = KeySequenceBinding(keys=["A", "B", "C"])
    assert transformer.transform_binding(key_sequence) == "(chord a b c)"

    # Test key sequence with modifiers
    key_sequence = KeySequenceBinding(keys=["LSHIFT", "A", "B"])
    assert transformer.transform_binding(key_sequence) == "(chord lsft a b)"

    # Test key sequence with special keys
    key_sequence = KeySequenceBinding(keys=["ENTER", "SPACE", "TAB"])
    assert transformer.transform_binding(key_sequence) == "(chord ret spc tab)"


def test_layer_transformations(transformer):
    """Test transforming layers to Kanata format."""
    # Test single layer
    layer = Layer(
        name="default",
        bindings=[
            KeyMapping(key="A"),
            KeyMapping(key="B"),
            KeyMapping(key="C"),
        ]
    )
    result = transformer.transform_layer(layer)
    assert "(deflayer default" in result
    assert "a b c" in result

    # Test multiple layers
    layers = [
        Layer(
            name="default",
            bindings=[
                KeyMapping(key="A"),
                KeyMapping(key="B"),
            ]
        ),
        Layer(
            name="num",
            bindings=[
                KeyMapping(key="1"),
                KeyMapping(key="2"),
            ]
        ),
    ]
    result = transformer.transform_layers(layers)
    assert "(deflayer default" in result
    assert "(deflayer num" in result
    assert "a b" in result
    assert "1 2" in result


def test_binding_matrix_transformations(transformer):
    """Test parsing of ZMK bindings matrix."""
    matrix = [
        [KeyMapping(key="A"), KeyMapping(key="B")],
        [KeyMapping(key="N1"), KeyMapping(key="mo 1")],
        [KeyMapping(key="trans"), KeyMapping(key="C")]
    ]

    result = transformer.transform_bindings_matrix(matrix)
    assert len(result) == 3
    assert result[0] == ["a", "b"]
    assert result[1] == ["1", "@layer1"]
    assert result[2] == ["_", "c"]
