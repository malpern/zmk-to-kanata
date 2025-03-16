"""Test module for layer transformation."""
from ..layer_transformer import LayerTransformer
from ..model.keymap_model import Layer, KeyMapping
from ..behaviors.key_sequence import KeySequenceBinding


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
    assert transformer.transform_binding(sticky_key) == "sticky-lsft"
    
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
    """Test transformation of complete ZMK layer."""
    transformer = LayerTransformer()

    zmk_layer = Layer(
        name="default_layer",
        keys=[
            [KeyMapping(key="A"), KeyMapping(key="B")],
            [KeyMapping(key="N1"), KeyMapping(key="mo 1")]
        ]
    )

    kanata_layer = transformer.transform_layer(zmk_layer)
    assert kanata_layer.name == "default"
    assert len(kanata_layer.keys) == 2
    assert kanata_layer.keys[0] == ["a", "b"]
    assert kanata_layer.keys[1] == ["1", "@layer1"]


def test_transform_layers():
    """Test transformation of multiple ZMK layers."""
    transformer = LayerTransformer()

    zmk_layers = [
        Layer(
            name="default_layer",
            keys=[[KeyMapping(key="A"), KeyMapping(key="B")]]
        ),
        Layer(
            name="num",  # No _layer suffix
            keys=[[KeyMapping(key="N1"), KeyMapping(key="N2")]]
        )
    ]

    kanata_layers = transformer.transform_layers(zmk_layers)
    assert len(kanata_layers) == 2

    # Check default layer
    default_layers = [
        layer for layer in kanata_layers if layer.name == "default"
    ]
    assert len(default_layers) == 1
    default = default_layers[0]
    assert len(default.keys) == 1
    assert default.keys[0] == ["a", "b"]

    # Check num layer
    num = next(layer for layer in kanata_layers if layer.name == "num")
    assert len(num.keys) == 1
    assert num.keys[0] == ["1", "2"]


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