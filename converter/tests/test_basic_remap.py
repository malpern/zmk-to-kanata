"""Basic Remapping Tests

Tests for basic key-to-key remapping functionality.
"""

import os
import tempfile
from pathlib import Path

import pytest

from converter.models import (
    KeymapConfig,
    Layer,
    Binding,
    KeyMapping,
    GlobalSettings,
)
from converter.output.file_writer import KanataFileWriter
from converter.transformer.kanata_transformer import KanataTransformer


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
        global_settings=GlobalSettings(tap_time=200, hold_time=250), layers=[]
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
                    [KeyMapping(key="C"), KeyMapping(key="D")],
                ],
            )
        ],
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
    """Test transforming global settings (or lack thereof) to Kanata format."""
    config = KeymapConfig(layers=[], behaviors={})

    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    assert "(defcfg" in kanata_config


def test_transform_default_layer():
    """Test transforming a basic layer to Kanata format."""
    layer0 = Layer(
        name="default",
        bindings=[
            Binding(params=["A"], behavior=None),
            Binding(params=["B"], behavior=None),
            Binding(params=["C"], behavior=None),
            Binding(params=["D"], behavior=None),
        ],
        index=0,
    )
    config = KeymapConfig(layers=[layer0], behaviors={})

    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    assert "(deflayer default" in kanata_config
    assert "a b c d" in kanata_config


def test_write_kanata_config(temp_dir):
    """Test writing Kanata configuration to a file."""
    layer0 = Layer(
        name="default",
        bindings=[
            Binding(params=["A"], behavior=None),
            Binding(params=["B"], behavior=None),
            Binding(params=["C"], behavior=None),
            Binding(params=["D"], behavior=None),
        ],
        index=0,
    )
    config = KeymapConfig(layers=[layer0], behaviors={})

    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    output_path = os.path.join(temp_dir, "output.kbd")
    with open(output_path, "w") as f:
        f.write(kanata_config)

    assert os.path.exists(output_path)
    with open(output_path, "r") as f:
        content = f.read()
        assert "(deflayer default" in content
        assert "a b c d" in content


def test_write_invalid_content():
    """Test writing invalid content raises TypeError."""
    writer = KanataFileWriter()
    with tempfile.NamedTemporaryFile(suffix=".kbd", delete=False) as temp_file:
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
