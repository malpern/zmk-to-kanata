"""Integration tests for layer support in the ZMK to Kanata converter."""

from pathlib import Path

from ..layer_parser import LayerParser
from ..layer_transformer import LayerTransformer


def test_layer_conversion():
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