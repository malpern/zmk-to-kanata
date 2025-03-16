"""Basic Remapping Tests

Tests for basic key-to-key remapping functionality.
"""
from pathlib import Path
import tempfile
import pytest

from converter.model.keymap_model import (
    KeyMapping,
    GlobalSettings,
    Layer,
    KeymapConfig
)
from converter.transformer.kanata_transformer import KanataTransformer
from converter.output.file_writer import KanataFileWriter


def test_key_mapping_equality():
    """Test KeyMapping equality comparison."""
    key1 = KeyMapping(key="A")
    key2 = KeyMapping(key="A")
    key3 = KeyMapping(key="B")

    assert key1 == key2
    assert key1 != key3
    assert key1 != "A"  # Compare with non-KeyMapping object


def test_parse_global_settings():
    """Test parsing global settings from a sample ZMK file."""
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=[]
    )
    assert config.global_settings.tap_time == 200
    assert config.global_settings.hold_time == 250


def test_parse_default_layer():
    """Test parsing default layer key mappings."""
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=[
            Layer(
                name="default",
                keys=[
                    [KeyMapping(key="A"), KeyMapping(key="B")],
                    [KeyMapping(key="C"), KeyMapping(key="D")]
                ]
            )
        ]
    )
    assert len(config.layers) == 1
    assert config.layers[0].name == "default"
    assert len(config.layers[0].keys) == 2
    assert len(config.layers[0].keys[0]) == 2
    assert config.layers[0].keys[0][0].key == "A"
    assert config.layers[0].keys[0][1].key == "B"
    assert config.layers[0].keys[1][0].key == "C"
    assert config.layers[0].keys[1][1].key == "D"


def test_transform_global_settings():
    """Test transforming global settings to Kanata format."""
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=[]
    )

    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    expected_lines = [
        ";; ZMK to Kanata Configuration",
        ";; Generated automatically - DO NOT EDIT",
        "",
        ";; Global settings",
        "(defvar tap-time 200)",
        "(defvar hold-time 250)"
    ]

    assert kanata_config.splitlines() == expected_lines


def test_transform_default_layer():
    """Test transforming a basic layer to Kanata format."""
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=[
            Layer(
                name="default",
                keys=[
                    [KeyMapping(key="A"), KeyMapping(key="B")],
                    [KeyMapping(key="C"), KeyMapping(key="D")]
                ]
            )
        ]
    )

    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    expected_lines = [
        ";; ZMK to Kanata Configuration",
        ";; Generated automatically - DO NOT EDIT",
        "",
        ";; Global settings",
        "(defvar tap-time 200)",
        "(defvar hold-time 250)",
        "",
        "(deflayer default",
        "  a  b",
        "  c  d",
        ")"
    ]

    assert kanata_config.splitlines() == expected_lines


def test_write_kanata_config():
    """Test writing Kanata configuration to a file."""
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=[
            Layer(
                name="default",
                keys=[
                    [KeyMapping(key="A"), KeyMapping(key="B")],
                    [KeyMapping(key="C"), KeyMapping(key="D")]
                ]
            )
        ]
    )

    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.kbd', delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        # Write the configuration
        writer = KanataFileWriter()
        writer.write(kanata_config, temp_path)

        # Read back and verify
        with open(temp_path, 'r') as f:
            written_content = f.read()

        assert written_content == kanata_config

    finally:
        # Clean up
        temp_path.unlink()


def test_write_invalid_content():
    """Test writing invalid content raises TypeError."""
    writer = KanataFileWriter()
    with tempfile.NamedTemporaryFile(suffix='.kbd', delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        with pytest.raises(TypeError, match="Content must be a string"):
            writer.write(None, temp_path)  # type: ignore
    finally:
        temp_path.unlink()


def test_write_invalid_path():
    """Test writing to invalid path type raises TypeError."""
    writer = KanataFileWriter()
    with pytest.raises(TypeError, match="Output path must be a Path object"):
        writer.write("content", "not/a/path")  # type: ignore


def test_parse_malformed_file(tmp_path):
    """Test parsing a malformed ZMK file raises appropriate errors."""
    from converter.parser.zmk_parser import ZMKParser

    # Test missing global settings
    malformed_file = tmp_path / "malformed.zmk"
    malformed_file.write_text("/ { keymap { } };")
    parser = ZMKParser()
    with pytest.raises(ValueError, match="Could not find global settings"):
        parser.parse(malformed_file)

    # Test missing bindings
    malformed_file.write_text("""
    / {
        global {
            tap-time = <200>;
            hold-time = <250>;
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer { };
        };
    };
    """)
    with pytest.raises(ValueError, match="Could not find key bindings"):
        parser.parse(malformed_file)
