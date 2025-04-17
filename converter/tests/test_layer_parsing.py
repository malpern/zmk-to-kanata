"""Tests for layer parsing in the ZMK parser."""

import tempfile
from pathlib import Path

import pytest

from converter.parser.zmk_parser import ParserError, ZMKParser


def test_empty_layer():
    """Test that empty layers are handled correctly."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".keymap") as f:
        f.write(
            """
/ {
    keymap {
        empty_layer {
            bindings = <>;
        };
    };
};
        """
        )
        f.flush()

        parser = ZMKParser()
        config = parser.parse(Path(f.name))
        assert len(config.layers) == 1
        assert config.layers[0].name == "empty"
        assert sum(len(row) for row in config.layers[0].keys) == 0


def test_multiple_layers():
    """Test parsing multiple layers."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".keymap") as f:
        f.write(
            """
/ {
    keymap {
        first_layer {
            bindings = <&kp A>;
        };
        second_layer {
            bindings = <&kp B>;
        };
    };
};
        """
        )
        f.flush()

        parser = ZMKParser()
        config = parser.parse(Path(f.name))
        assert len(config.layers) == 2
        assert config.layers[0].name == "first"
        assert config.layers[1].name == "second"
        assert sum(len(row) for row in config.layers[0].keys) == 1
        assert sum(len(row) for row in config.layers[1].keys) == 1


def test_multiline_bindings():
    """Test parsing bindings that span multiple lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".keymap") as f:
        f.write(
            """
/ {
    keymap {
        test_layer {
            bindings = <
                &kp A
                &kp B
                &kp C
            >;
        };
    };
};
        """
        )
        f.flush()

        parser = ZMKParser()
        config = parser.parse(Path(f.name))
        assert len(config.layers) == 1
        assert sum(len(row) for row in config.layers[0].keys) == 3
        assert [b.key for row in config.layers[0].keys for b in row] == ["A", "B", "C"]


def test_invalid_layer_name():
    """Test that invalid layer names are rejected."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".keymap") as f:
        f.write(
            """
/ {
    keymap {
        _layer {
            bindings = <&kp A>;
        };
    };
};
        """
        )
        f.flush()

        parser = ZMKParser()
        with pytest.raises(ParserError):
            parser.parse(Path(f.name))


def test_missing_bindings():
    """Test that layers without bindings are rejected."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".keymap") as f:
        f.write(
            """
/ {
    keymap {
        test_layer {
        };
    };
};
        """
        )
        f.flush()

        parser = ZMKParser()
        with pytest.raises(ParserError):
            parser.parse(Path(f.name))


def test_nested_layers():
    """Test that nested layers are rejected."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".keymap") as f:
        f.write(
            """
/ {
    keymap {
        outer_layer {
            bindings = <&kp A>;
            inner_layer {
                bindings = <&kp B>;
            };
        };
    };
};
        """
        )
        f.flush()

        parser = ZMKParser()
        with pytest.raises(ParserError):
            parser.parse(Path(f.name))
