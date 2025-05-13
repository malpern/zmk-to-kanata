"""Test DTS Parser functionality."""

import os
import pytest
from converter.dts.parser import DtsParser, DtsParseError
from converter.dts.preprocessor import DtsPreprocessor
from converter.dts.extractor import KeymapExtractor


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
    # Expect macro-expanded values (e.g., [31] and [32])
    assert matrix_transform.properties["rows"].value == [31]
    assert matrix_transform.properties["columns"].value == [32]

    keymap = root.find_node("/keymap")
    assert keymap is not None
    assert keymap.properties["compatible"].value == "zmk,keymap"

    default_layer = root.find_node("/keymap/default_layer")
    assert default_layer is not None
    # Check for numeric keycodes (A=0x04, B=0x05, C=0x06, D=0x07, E=0x08, F=0x09)
    bindings = default_layer.properties["bindings"].value
    for code in [0x04, 0x05, 0x06, 0x07, 0x08, 0x09]:
        assert code in bindings


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
    # Expect macro-expanded values (e.g., [33] and [34])
    assert matrix_transform.properties["rows"].value == [33]
    assert matrix_transform.properties["columns"].value == [34]

    keymap = root.find_node("/keymap")
    assert keymap is not None
    assert keymap.properties["compatible"].value == "zmk,keymap"

    default_layer = root.find_node("/keymap/default_layer")
    assert default_layer is not None
    # Check for numeric keycodes (A=0x04, ..., T=0x17)
    bindings = default_layer.properties["bindings"].value
    for code in range(0x04, 0x18):
        assert code in bindings


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

    with pytest.raises(DtsParseError, match="DTS must start with root node '/'"):
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

    # Remove matrix_transform assertions, as this test does not define such a node
    # matrix_transform = root.children.get("matrix_transform")
    # assert matrix_transform is not None
    # assert matrix_transform.properties["rows"].value == [31]
    # assert matrix_transform.properties["columns"].value == [32]
    # matrix_transform = root.children.get("matrix_transform")
    # assert matrix_transform is not None
    # assert matrix_transform.properties["rows"].value == [33]
    # assert matrix_transform.properties["columns"].value == [34]


MULTI_ROOT_DTS = """
/ {
    behaviors {
        compatible = "zmk,behaviors";
    };
};
/ {
    keymap {
        compatible = "zmk,keymap";
    };
};
"""

STRAY_BLOCK_DTS = """
/ {
    behaviors {
        compatible = "zmk,behaviors";
    };
};
{ keymap { compatible = "zmk,keymap"; }; };
"""

EXTRA_SEMICOLONS_DTS = """
/ {
    behaviors { compatible = "zmk,behaviors"; };
    ; ;
    keymap { compatible = "zmk,keymap"; };
};
"""

PREPROCESSOR_ARTIFACTS_DTS = """
# 0x1E /* 1 */ "/some/file"
/ {
    behaviors { compatible = "zmk,behaviors"; };
    keymap { compatible = "zmk,keymap"; };
};
"""

STRAY_BRACES_DTS = """
/ {
    behaviors { compatible = "zmk,behaviors"; };
    { keymap { compatible = "zmk,keymap"; }; }
};
"""


@pytest.mark.parametrize(
    "dts_content,expected_children",
    [
        (MULTI_ROOT_DTS, {"behaviors", "keymap"}),
        (STRAY_BLOCK_DTS, {"behaviors", "keymap"}),
        (EXTRA_SEMICOLONS_DTS, {"behaviors", "keymap"}),
        (PREPROCESSOR_ARTIFACTS_DTS, {"behaviors", "keymap"}),
        (STRAY_BRACES_DTS, {"behaviors", "keymap"}),
    ],
)
def test_ast_root_children_regressions(dts_content, expected_children):
    parser = DtsParser()
    ast = parser.parse(dts_content)
    assert expected_children.issubset(set(ast.children.keys()))


# Extraction test: ensure keymap node is found and extracted
KEYMAP_EXTRACTION_DTS = """
/ {
    behaviors { compatible = "zmk,behaviors"; };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&kp A &kp B>;
        };
    };
};
"""


def test_keymap_extraction():
    parser = DtsParser()
    ast = parser.parse(KEYMAP_EXTRACTION_DTS)
    extractor = KeymapExtractor()
    model = extractor.extract(ast)
    assert hasattr(model, "layers")
    assert any(layer.name == "default_layer" for layer in model.layers)
    assert any(
        "A" in str(b.params) or "B" in str(b.params)
        for layer in model.layers
        for b in layer.bindings
    )
