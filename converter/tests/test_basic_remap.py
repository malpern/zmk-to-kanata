"""Basic Remapping Tests

Tests for basic key-to-key remapping functionality.
"""
from pathlib import Path
from converter.parser.zmk_parser import ZMKParser
from converter.model.keymap_model import KeyMapping


# Get the path to the samples directory
SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def test_parse_global_settings():
    """Test parsing of global settings from ZMK file."""
    parser = ZMKParser()
    config = parser.parse(SAMPLES_DIR / "sample_basic.zmk")
    
    assert config.global_settings.tap_time == 200
    assert config.global_settings.hold_time == 250


def test_parse_default_layer():
    """Test parsing of the default layer key mappings."""
    parser = ZMKParser()
    config = parser.parse(SAMPLES_DIR / "sample_basic.zmk")
    
    assert len(config.layers) == 1
    default_layer = config.layers[0]
    assert default_layer.name == "default"
    
    # Check the key mappings
    expected_keys = [
        [KeyMapping("A"), KeyMapping("B"), KeyMapping("C"), KeyMapping("D")],
        [KeyMapping("E"), KeyMapping("F"), KeyMapping("G"), KeyMapping("H")],
        [KeyMapping("I"), KeyMapping("J"), KeyMapping("K"), KeyMapping("L")]
    ]
    
    assert len(default_layer.keys) == len(expected_keys)
    for row_idx, row in enumerate(default_layer.keys):
        assert len(row) == len(expected_keys[row_idx])
        for key_idx, key in enumerate(row):
            assert key == expected_keys[row_idx][key_idx]