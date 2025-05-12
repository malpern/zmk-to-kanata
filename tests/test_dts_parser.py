"""Test DTS Parser functionality."""

import os
import pytest
from converter.dts.parser import DtsParser
from converter.dts.preprocessor import DtsPreprocessor
from converter.dts.error_handler import DtsParseError


def test_parse_simple_keymap():
    """Test parsing a simple keymap."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dts")

    preprocessor = DtsPreprocessor(
        include_paths=[os.path.join(fixtures_dir, "include")]
    )
    parser = DtsParser()

    input_file = os.path.join(fixtures_dir, "simple_keymap.zmk")
    preprocessed = preprocessor.preprocess(input_file)
    print("\nPreprocessed content:")
    print(preprocessed)
    root = parser.parse(preprocessed)

    assert root is not None
    assert root.name == "/"

    # First find the matrix_transform node directly
    matrix_transform = root.children.get("matrix_transform")
    assert matrix_transform is not None
    assert matrix_transform.properties["rows"].value == [2]
    assert matrix_transform.properties["columns"].value == [3]

    keymap = root.find_node("/keymap")
    assert keymap is not None
    assert keymap.properties["compatible"].value == "zmk,keymap"

    default_layer = root.find_node("/keymap/default_layer")
    assert default_layer is not None
    assert "&kp" in default_layer.properties["bindings"].value
    assert "A" in default_layer.properties["bindings"].value


def test_parse_large_keymap():
    """Test parsing a larger keymap."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dts")

    preprocessor = DtsPreprocessor(
        include_paths=[os.path.join(fixtures_dir, "include")]
    )
    parser = DtsParser()

    input_file = os.path.join(fixtures_dir, "large_keymap.zmk")
    preprocessed = preprocessor.preprocess(input_file)
    print("\nPreprocessed content:")
    print(preprocessed)
    root = parser.parse(preprocessed)

    assert root is not None
    assert root.name == "/"

    # First find the matrix_transform node directly
    matrix_transform = root.children.get("matrix_transform")
    assert matrix_transform is not None
    assert matrix_transform.properties["rows"].value == [4]
    assert matrix_transform.properties["columns"].value == [5]

    keymap = root.find_node("/keymap")
    assert keymap is not None
    assert keymap.properties["compatible"].value == "zmk,keymap"

    default_layer = root.find_node("/keymap/default_layer")
    assert default_layer is not None
    assert "&kp" in default_layer.properties["bindings"].value
    assert "A" in default_layer.properties["bindings"].value


def test_parse_simple_dts():
    """Test parsing a simple DTS file."""
    content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <1 2 3>;
            };
        };
    };
    """

    parser = DtsParser()
    root = parser.parse(content)

    assert root is not None
    assert root.name == "/"
    assert "keymap" in root.children


def test_parse_with_labels():
    """Test parsing DTS with labels."""
    content = """
    / {
        kp: key_press {
            compatible = "zmk,key-press";
        };

        keymap {
            bindings = <&kp A &kp B>;
        };
    };
    """

    parser = DtsParser()
    root = parser.parse(content)

    key_press = root.children["key_press"]
    assert key_press is not None
    assert "compatible" in key_press.properties


def test_parse_complex_bindings():
    """Test parsing complex bindings."""
    content = """
    / {
        keymap {
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &mo 1 &kp D &kp E
                >;
            };
        };
    };
    """

    parser = DtsParser()
    root = parser.parse(content)

    default_layer = root.children["keymap"].children["default_layer"]
    assert default_layer is not None
    assert "bindings" in default_layer.properties


def test_parse_error_handling():
    """Test error handling in parser."""
    parser = DtsParser()

    with pytest.raises(DtsParseError, match="DTS must start with root node '/'"):
        parser.parse("node {")

    with pytest.raises(
        DtsParseError,
        match="Expected '{' after root node '/'",
    ):
        parser.parse("/ invalid")


def test_parse_invalid_content():
    """Test parsing invalid content."""
    parser = DtsParser()

    with pytest.raises(DtsParseError, match="DTS must start with root node '/'"):
        parser.parse("")


def test_find_node():
    """Test node finding functionality."""
    content = """
    / {
        keymap {
            default_layer {
                bindings = <1 2 3>;
            };
            function_layer {
                bindings = <4 5 6>;
            };
        };
    };
    """

    parser = DtsParser()
    root = parser.parse(content)

    keymap = root.find_node("/keymap")
    assert keymap is not None
    assert keymap.name == "keymap"

    default_layer = root.find_node("/keymap/default_layer")
    assert default_layer is not None
    assert default_layer.name == "default_layer"

    function_layer = root.find_node("/keymap/function_layer")
    assert function_layer is not None
    assert function_layer.name == "function_layer"

    assert root.find_node("/nonexistent") is None
    assert root.find_node("/keymap/nonexistent") is None
