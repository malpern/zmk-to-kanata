"""
Tests for the DTS preprocessor module.
"""

import pytest
from pathlib import Path
from converter.dts.preprocessor import DtsPreprocessor, PreprocessorError
import os
import tempfile


@pytest.fixture
def include_path():
    """Return the path to the test include directory."""
    return str(Path(__file__).parent.parent / "fixtures" / "dts" / "include")


@pytest.fixture
def preprocessor(include_path):
    """Return a preprocessor instance with test include path."""
    return DtsPreprocessor(include_paths=[include_path])


@pytest.fixture
def simple_keymap_path():
    """Return the path to the simple keymap test file."""
    return Path(__file__).parent.parent / "fixtures" / "dts" / "simple_keymap.zmk"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_dts_file():
    """Create a temporary DTS file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dts", delete=False) as f:
        f.write(
            """
/ {
    keymap {
        compatible = "zmk,keymap";
        label = "Default keymap";

        default_layer {
            bindings = <
                &kp A &kp B
                &kp C &kp D
            >;
            sensor-bindings = <&inc_dec_kp C_VOL_UP C_VOL_DN>;
        };
    };
};
"""
        )
        return f.name


@pytest.fixture
def temp_dts_with_matrix():
    """Create a temporary DTS file with matrix definitions."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dts", delete=False) as f:
        f.write(
            """
/ {
    chosen {
        zmk,matrix_transform = &matrix_transform;
    };

    matrix_transform: matrix_transform {
        compatible = "zmk,matrix-transform";
        rows = <2>;
        columns = <2>;
        map = <
            RC(0,0) RC(0,1)
            RC(1,0) RC(1,1)
        >;
    };
};
"""
        )
        return f.name


def test_preprocessor_initialization():
    """Test preprocessor initialization with different options."""
    # Test default initialization
    preprocessor = DtsPreprocessor()
    cpp_path_str = str(preprocessor.cpp_path)
    assert cpp_path_str.endswith("cpp") or cpp_path_str.endswith("clang")
    assert preprocessor.include_paths == []

    # Test custom cpp path
    custom_path = "/custom/cpp"
    preprocessor = DtsPreprocessor(cpp_path=custom_path)
    assert str(preprocessor.cpp_path) == custom_path

    # Test include paths
    fixtures_dir = str(Path(__file__).parent.parent / "fixtures" / "dts")
    include_paths = [
        str(Path(fixtures_dir) / "include"),
    ]
    preprocessor = DtsPreprocessor(include_paths=include_paths)
    assert preprocessor.include_paths == include_paths


def test_preprocess_simple_file(temp_dir):
    """Test preprocessing a simple DTS file."""
    # Create a simple DTS file
    input_path = os.path.join(temp_dir, "test.dts")
    with open(input_path, "w") as f:
        f.write(
            """
#define TEST_VALUE 42
/ {
    test = <TEST_VALUE>;
};
"""
        )

    # Create a temporary include directory with a header file
    include_dir = os.path.join(temp_dir, "include")
    os.makedirs(include_dir)

    # Create a header file that defines TEST_VALUE
    header_path = os.path.join(include_dir, "test.h")
    with open(header_path, "w") as f:
        f.write("#define TEST_VALUE 42\n")

    preprocessor = DtsPreprocessor(include_paths=[include_dir])
    result = preprocessor.preprocess(input_path)

    # Check that macros are expanded
    assert "42" in result
    assert "TEST_VALUE" not in result


def test_preprocess_with_matrix(temp_dir):
    """Test preprocessing a file with matrix transform."""
    # Create a DTS file with matrix
    input_path = os.path.join(temp_dir, "matrix.dts")
    with open(input_path, "w") as f:
        f.write(
            """
/ {
    RC_MATRIX = <2 3>;
    matrix_transform = <
        RC(0) RC(1) RC(2)
    >;
};
"""
        )

    preprocessor = DtsPreprocessor()
    result = preprocessor.preprocess(input_path)

    # Check that RC macros are preserved (not expanded by preprocessor)
    assert "RC(0)" in result
    assert "RC(1)" in result
    assert "RC(2)" in result


def test_preprocess_with_includes(temp_dir):
    """Test preprocessing with include files."""
    # Create include directory and file
    include_dir = os.path.join(temp_dir, "include")
    os.makedirs(include_dir)

    header_path = os.path.join(include_dir, "test.h")
    with open(header_path, "w") as f:
        f.write("#define HEADER_VALUE 123\n")

    # Create main DTS file
    input_path = os.path.join(temp_dir, "main.dts")
    with open(input_path, "w") as f:
        f.write(
            """
#include "test.h"
/ {
    test = <HEADER_VALUE>;
};
"""
        )

    preprocessor = DtsPreprocessor(include_paths=[include_dir])
    result = preprocessor.preprocess(input_path)

    # Check that included macros are expanded
    assert "123" in result
    assert "HEADER_VALUE" not in result


def test_preprocess_invalid_file():
    """Test preprocessing a non-existent file."""
    preprocessor = DtsPreprocessor()
    with pytest.raises(PreprocessorError):
        preprocessor.preprocess("nonexistent.dts")


def test_preprocess_invalid_cpp_command(temp_dir):
    """Test preprocessing with invalid cpp command."""
    # Create a simple DTS file
    input_path = os.path.join(temp_dir, "test.dts")
    with open(input_path, "w") as f:
        f.write("/ { test = <1>; };")

    # Use invalid cpp path
    preprocessor = DtsPreprocessor(cpp_path="invalid_cpp")
    # The preprocessor falls back to clang, so no exception is raised
    result = preprocessor.preprocess(input_path)
    assert "test" in result


def test_matrix_size_extraction():
    """Test matrix size extraction from DTS content."""
    # Test with matrix_transform
    content = """
    matrix_transform: matrix_transform {
        rows = <4>;
        columns = <5>;
    };
    """
    preprocessor = DtsPreprocessor()
    size = preprocessor._get_matrix_size(content)
    assert size == (4, 5)

    # Test with RC_MATRIX
    content = """
    RC_MATRIX = <2 3>;
    """
    size = preprocessor._get_matrix_size(content)
    assert size == (2, 3)

    # Test with no matrix
    content = "/ { test = <1>; };"
    size = preprocessor._get_matrix_size(content)
    assert size is None


def test_preprocess_simple_keymap(preprocessor, simple_keymap_path):
    """Test preprocessing a simple keymap."""
    result = preprocessor.preprocess(str(simple_keymap_path))
    # Remove preprocessor line markers
    filtered = "\n".join(line for line in result.splitlines() if not line.strip().startswith("#"))
    # Check that the result contains the expected content
    assert "((0) << 0x25 | (0))" in filtered
    assert "((0) << 0x25 | (1))" in filtered
    assert "((0) << 0x25 | (2))" in filtered
    assert "((1) << 0x25 | (0))" in filtered
    assert "((1) << 0x25 | (1))" in filtered
    assert "((1) << 0x25 | (2))" in filtered
    assert "&kp 0x04" in filtered
    assert "&kp 0x05" in filtered
    assert "&kp 0x06" in filtered
    assert "&kp 0x07" in filtered
    assert "&kp 0x08" in filtered
    assert "&kp 0x09" in filtered


def test_preprocess_with_include_paths():
    """Test preprocessor with include paths."""
    fixtures_dir = str(Path(__file__).parent.parent / "fixtures" / "dts")
    include_paths = [
        str(Path(fixtures_dir) / "include"),
    ]
    preprocessor = DtsPreprocessor(include_paths=include_paths)
    assert preprocessor.include_paths == include_paths


def test_matrix_size_detection(temp_dts_with_matrix):
    """Test matrix size detection."""
    preprocessor = DtsPreprocessor()
    size = preprocessor._get_matrix_size(open(temp_dts_with_matrix).read())
    assert size == (2, 2)


def test_matrix_size_detection_no_matrix():
    """Test matrix size detection with no matrix."""
    preprocessor = DtsPreprocessor()
    size = preprocessor._get_matrix_size("/ { test = <1>; };")
    assert size is None
