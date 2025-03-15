"""Tests for the LayerTransformer class."""

from ..layer_parser import Layer
from ..layer_transformer import LayerTransformer


def test_transform_binding():
    """Test transformation of individual ZMK bindings."""
    transformer = LayerTransformer()
    
    # Test letters
    assert transformer.transform_binding("&kp A") == "a"
    assert transformer.transform_binding("&kp Z") == "z"
    
    # Test numbers (both number row and numpad)
    assert transformer.transform_binding("&kp N1") == "1"
    assert transformer.transform_binding("&kp N0") == "0"
    assert transformer.transform_binding("&kp KP_N7") == "kp7"
    
    # Test symbols and punctuation
    assert transformer.transform_binding("&kp EXCL") == "excl"
    assert transformer.transform_binding("&kp MINUS") == "minus"
    assert transformer.transform_binding("&kp PLUS") == "plus"
    assert transformer.transform_binding("&kp LBKT") == "lbracket"
    assert transformer.transform_binding("&kp DOT") == "dot"
    
    # Test function keys
    assert transformer.transform_binding("&kp F1") == "f1"
    assert transformer.transform_binding("&kp F12") == "f12"
    
    # Test navigation and editing
    assert transformer.transform_binding("&kp ENTER") == "ret"
    assert transformer.transform_binding("&kp SPACE") == "spc"
    assert transformer.transform_binding("&kp PG_UP") == "pgup"
    
    # Test modifiers
    assert transformer.transform_binding("&kp LSHIFT") == "lshift"
    assert transformer.transform_binding("&kp RGUI") == "rmeta"
    
    # Test system and media
    assert transformer.transform_binding("&kp C_MUTE") == "mute"
    assert transformer.transform_binding("&kp C_VOL_UP") == "volu"
    
    # Test numpad special keys
    assert transformer.transform_binding("&kp KP_PLUS") == "kp_plus"
    assert transformer.transform_binding("&kp KP_DOT") == "kp_dot"
    
    # Test layer momentary switch
    assert transformer.transform_binding("&mo 1") == "@layer1"
    assert transformer.transform_binding("&mo 2") == "@layer2"
    
    # Test transparent key
    assert transformer.transform_binding("&trans") == "_"
    
    # Test unknown binding
    assert transformer.transform_binding("&unknown X") is None


def test_parse_binding_matrix():
    """Test parsing of ZMK bindings matrix."""
    transformer = LayerTransformer()
    
    zmk_bindings = """
        &kp A &kp B
        &kp N1 &mo 1
        &trans &kp C
    """
    
    matrix = transformer.parse_binding_matrix(zmk_bindings)
    assert len(matrix) == 3  # Three rows
    assert matrix[0] == ["a", "b"]  # First row
    assert matrix[1] == ["1", "@layer1"]  # Second row
    assert matrix[2] == ["_", "c"]  # Third row


def test_transform_layer():
    """Test transformation of complete ZMK layer."""
    transformer = LayerTransformer()
    
    zmk_layer = Layer(
        name="default_layer",
        bindings="""
            &kp A &kp B
            &kp N1 &mo 1
        """
    )
    
    kanata_layer = transformer.transform_layer(zmk_layer)
    assert kanata_layer.name == "default"  # _layer suffix removed
    assert len(kanata_layer.bindings) == 2  # Two rows
    assert kanata_layer.bindings[0] == ["a", "b"]
    assert kanata_layer.bindings[1] == ["1", "@layer1"]


def test_transform_layers():
    """Test transformation of multiple ZMK layers."""
    transformer = LayerTransformer()
    
    zmk_layers = [
        Layer(
            name="default_layer",
            bindings="&kp A &kp B"
        ),
        Layer(
            name="num",  # No _layer suffix
            bindings="&kp N1 &kp N2"
        )
    ]
    
    kanata_layers = transformer.transform_layers(zmk_layers)
    assert len(kanata_layers) == 2
    
    # Check first layer
    assert kanata_layers[0].name == "default"
    assert kanata_layers[0].bindings == [["a", "b"]]
    
    # Check second layer
    assert kanata_layers[1].name == "num"
    assert kanata_layers[1].bindings == [["1", "2"]] 