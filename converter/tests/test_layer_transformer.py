"""Test module for layer transformation."""
from converter.layer_transformer import LayerTransformer
from converter.model.keymap_model import Layer, KeyMapping
from converter.behaviors.key_sequence import KeySequenceBinding


def test_transform_binding():
    """Test transformation of individual ZMK bindings."""
    transformer = LayerTransformer()

    # Test letters
    assert transformer.transform_binding(KeyMapping(key="A")) == "a"
    assert transformer.transform_binding(KeyMapping(key="B")) == "b"

    # Test numbers
    assert transformer.transform_binding(KeyMapping(key="N1")) == "1"
    assert transformer.transform_binding(KeyMapping(key="N0")) == "0"
    key = KeyMapping(key="KP_N7")
    assert transformer.transform_binding(key) == "kp7"

    # Test symbols and punctuation
    assert transformer.transform_binding(KeyMapping(key="EXCL")) == "excl"
    assert transformer.transform_binding(KeyMapping(key="MINUS")) == "minus"
    assert transformer.transform_binding(KeyMapping(key="PLUS")) == "plus"
    assert transformer.transform_binding(KeyMapping(key="DOT")) == "dot"

    # Test function keys
    assert transformer.transform_binding(KeyMapping(key="F1")) == "f1"
    assert transformer.transform_binding(KeyMapping(key="F12")) == "f12"

    # Test navigation and editing
    key_mapping = KeyMapping(key="ENTER")
    assert transformer.transform_binding(key_mapping) == "enter"
    space_key = KeyMapping(key="SPACE")
    assert transformer.transform_binding(space_key) == "space"
    key_up = KeyMapping(key="PG_UP")
    assert transformer.transform_binding(key_up) == "pg_up"

    # Test modifiers
    assert transformer.transform_binding(KeyMapping(key="LSHIFT")) == "lshift"
    assert transformer.transform_binding(KeyMapping(key="RGUI")) == "rgui"

    # Test system and media
    assert transformer.transform_binding(KeyMapping(key="C_MUTE")) == "c_mute"
    key_vol = KeyMapping(key="C_VOL_UP")
    assert transformer.transform_binding(key_vol) == "c_vol_up"

    # Test numpad special keys
    kp_plus = KeyMapping(key="KP_PLUS")
    assert transformer.transform_binding(kp_plus) == "kp_plus"
    assert transformer.transform_binding(KeyMapping(key="KP_DOT")) == "kp_dot"

    # Test layer momentary switch
    assert transformer.transform_binding(KeyMapping(key="mo 1")) == "@layer1"
    assert transformer.transform_binding(KeyMapping(key="mo 2")) == "@layer2"

    # Test transparent key
    assert transformer.transform_binding(KeyMapping(key="trans")) == "_"

    # Test sticky key
    sticky_key = KeyMapping(key="sk LSHIFT")
    expected_sticky = "sticky-lsft"
    assert transformer.transform_binding(sticky_key) == expected_sticky

    # Test unknown binding
    unknown_key = KeyMapping(key="unknown X")
    assert transformer.transform_binding(unknown_key) == "unknown x"


def test_parse_binding_matrix():
    """Test parsing of ZMK bindings matrix."""
    transformer = LayerTransformer()

    # Create a matrix of KeyMapping objects
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


def test_transform_layer():
    """Test transforming a layer to Kanata format."""
    layer = Layer(
        name="default",
        bindings=[
            KeyMapping(key="A"),
            KeyMapping(key="B"),
            KeyMapping(key="C"),
        ]
    )

    transformer = LayerTransformer()
    result = transformer.transform_layer(layer)

    assert "(deflayer default" in result
    assert "a b c" in result


def test_transform_layers():
    """Test transforming multiple layers to Kanata format."""
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

    transformer = LayerTransformer()
    result = transformer.transform_layers(layers)

    assert "(deflayer default" in result
    assert "(deflayer num" in result
    assert "a b" in result
    assert "1 2" in result


def test_transform_key_sequence():
    """Test transforming key sequence bindings."""
    transformer = LayerTransformer()

    # Test basic key sequence
    key_sequence = KeySequenceBinding(keys=["A", "B", "C"])
    assert transformer.transform_binding(key_sequence) == "(chord a b c)"

    # Test key sequence with modifiers
    key_sequence = KeySequenceBinding(keys=["LSHIFT", "A", "B"])
    assert transformer.transform_binding(key_sequence) == "(chord lsft a b)"

    # Test key sequence with special keys
    key_sequence = KeySequenceBinding(keys=["ENTER", "SPACE", "TAB"])
    assert transformer.transform_binding(key_sequence) == "(chord ret spc tab)"
