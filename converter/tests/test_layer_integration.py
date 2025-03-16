"""Integration tests for layer transformation with various behaviors."""

from pathlib import Path

from ..layer_parser import LayerParser
from ..layer_transformer import LayerTransformer
from converter.model.keymap_model import (
    Layer,
    KeyMapping
)
from converter.behaviors.key_sequence import (
    KeySequenceBinding,
    KeySequenceBehavior
)


def test_layer_conversion():
    """Test basic layer conversion."""
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


def test_key_sequence_layer_conversion():
    """Test layer conversion with key sequences."""
    transformer = LayerTransformer()

    # Create a layer with key sequences
    zmk_layer = Layer(
        name="sequences_layer",
        keys=[
            [
                KeySequenceBinding(keys=["LSHIFT", "A", "B"]),
                KeyMapping(key="C"),
                KeySequenceBinding(keys=["LCTRL", "X"])
            ],
            [
                KeyMapping(key="D"),
                KeySequenceBinding(
                    keys=["LGUI", "TAB"],
                    behavior=KeySequenceBehavior(
                        wait_ms=50,
                        tap_ms=50,
                        bindings=["kp LGUI", "kp TAB"]
                    )
                ),
                KeyMapping(key="E")
            ]
        ]
    )

    kanata_layer = transformer.transform_layer(zmk_layer)
    assert kanata_layer.name == "sequences"
    assert len(kanata_layer.keys) == 2
    
    # First row: key sequence, normal key, key sequence
    assert kanata_layer.keys[0] == ["(chord lsft a b)", "c", "(chord lctl x)"]
    
    # Second row: normal key, key sequence with custom behavior, normal key
    assert kanata_layer.keys[1] == ["d", "(chord lmet tab)", "e"]


def test_mixed_behavior_layer():
    """Test layer conversion with mixed behaviors."""
    transformer = LayerTransformer()
    
    # Create a layer with mixed behaviors
    zmk_layer = Layer(
        name="mixed_layer",
        keys=[
            [
                KeySequenceBinding(keys=["LSHIFT", "A"]),  # Key sequence
                KeyMapping(key="sk LCTRL"),                # Sticky key
                KeyMapping(key="mo 1")                     # Layer switch
            ],
            [
                KeyMapping(key="trans"),                   # Transparent
                KeySequenceBinding(keys=["LGUI", "TAB"]),  # Key sequence
                KeyMapping(key="N1")                       # Number key
            ]
        ]
    )
    
    kanata_layer = transformer.transform_layer(zmk_layer)
    assert kanata_layer.name == "mixed"
    assert len(kanata_layer.keys) == 2
    
    # First row: key sequence, sticky key, layer switch
    assert kanata_layer.keys[0] == ["(chord lsft a)", "sticky-lctl", "@layer1"]
    
    # Second row: transparent, key sequence, number key
    assert kanata_layer.keys[1] == ["_", "(chord lmet tab)", "1"]


def test_layer_conversion_end_to_end():
    """Test end-to-end conversion of a ZMK file with multiple layers."""
    # Get the path to our sample file
    samples_dir = Path(__file__).parent.parent / "samples"
    zmk_file = samples_dir / "sample_layers.zmk"
    
    # Read the ZMK file
    with open(zmk_file, "r") as f:
        zmk_content = f.read()
    
    # Parse the layers
    parser = LayerParser()
    layers = parser.parse_zmk_file(zmk_content)
    
    # Transform to Kanata format
    transformer = LayerTransformer()
    kanata_layers = transformer.transform_layers(layers)
    
    # Verify the results
    assert len(kanata_layers) == 3, "Should have three layers"
    
    # Check default layer
    default = next(layer for layer in kanata_layers if layer.name == "default")
    assert len(default.keys) == 3, "Default layer should have 3 rows"
    assert len(default.keys[0]) == 4, "Each row should have 4 keys"
    assert default.keys[0][0] == "a"
    assert default.keys[1][2] == "@layer1"
    
    # Check number layer
    num = next(layer for layer in kanata_layers if layer.name == "num")
    assert len(num.keys) == 3, "Num layer should have 3 rows"
    assert len(num.keys[0]) == 4, "Each row should have 4 keys"
    assert num.keys[0][0] == "1"
    assert num.keys[1][2] == "_"  # transparent key
    
    # Check symbol layer
    sym = next(layer for layer in kanata_layers if layer.name == "sym")
    assert len(sym.keys) == 3, "Symbol layer should have 3 rows"
    assert len(sym.keys[0]) == 4, "Each row should have 4 keys"
    assert sym.keys[0][0] == "excl"
    assert sym.keys[1][1] == "caret"
    assert sym.keys[2][2] == "lpar" 