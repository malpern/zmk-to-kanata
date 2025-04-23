"""
Tests for the DTS preprocessor module.
"""

import pytest
from pathlib import Path
from converter.dts.preprocessor import DtsPreprocessor, PreprocessorError
import os
import tempfile
import shutil


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
    assert preprocessor.cpp_path.endswith("cpp") or preprocessor.cpp_path.endswith(
        "clang"
    )
    assert preprocessor.include_paths == []

    # Test custom cpp path
    custom_path = "/custom/cpp"
    preprocessor = DtsPreprocessor(cpp_path=custom_path)
    assert preprocessor.cpp_path == custom_path

    # Test include paths
    include_paths = ["/path1", "/path2"]
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

    preprocessor = DtsPreprocessor()
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

    # Check that RC macros are preserved
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
    with pytest.raises(FileNotFoundError):
        preprocessor.preprocess("nonexistent.dts")


def test_preprocess_invalid_cpp_command(temp_dir):
    """Test preprocessing with invalid cpp command."""
    # Create a simple DTS file
    input_path = os.path.join(temp_dir, "test.dts")
    with open(input_path, "w") as f:
        f.write("/ { test = <1>; };")

    # Use invalid cpp path
    preprocessor = DtsPreprocessor(cpp_path="invalid_cpp")
    with pytest.raises(PreprocessorError):
        preprocessor.preprocess(input_path)


def test_matrix_size_extraction():
    """Test matrix size extraction from DTS content."""
    preprocessor = DtsPreprocessor()

    # Test valid matrix size
    content = "RC_MATRIX = <2 3>;"
    size = preprocessor._get_matrix_size(content)
    assert size == (2, 3)

    # Test invalid matrix size
    content = "no matrix size here"
    size = preprocessor._get_matrix_size(content)
    assert size is None


def test_preprocess_simple_keymap(preprocessor, simple_keymap_path):
    """Test preprocessing a simple keymap file."""
    result = preprocessor.preprocess(str(simple_keymap_path))

    # Basic checks for preprocessed content
    assert "keymap" in result
    assert "compatible" in result
    assert "zmk,keymap" in result
    assert "default_layer" in result
    assert "bindings" in result


def test_preprocess_with_include_paths():
    """Test preprocessing with include paths."""
    include_dir = tempfile.mkdtemp()
    try:
        # Create a test header
        with open(os.path.join(include_dir, "test.h"), "w") as f:
            f.write("#define TEST_MACRO 42\n")

        # Create a DTS file that uses the macro
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dts", delete=False) as f:
            f.write(
                """
#include "test.h"
/ {
    test = <TEST_MACRO>;
};
"""
            )
            dts_path = f.name

        # Test preprocessing with include path
        preprocessor = DtsPreprocessor(include_paths=[include_dir])
        result = preprocessor.preprocess(dts_path)

        # Check that macro is expanded
        assert "42" in result
        assert "TEST_MACRO" not in result

    finally:
        # Clean up
        os.unlink(dts_path)
        shutil.rmtree(include_dir)


def test_matrix_size_detection(temp_dts_with_matrix):
    """Test matrix size detection from DTS content."""
    preprocessor = DtsPreprocessor()
    with open(temp_dts_with_matrix, "r") as f:
        content = f.read()

    size = preprocessor._get_matrix_size(content)
    assert size == (2, 2)


def test_matrix_size_detection_no_matrix():
    """Test matrix size detection when no matrix is present."""
    preprocessor = DtsPreprocessor()
    content = "/ { test = <1>; };"
    size = preprocessor._get_matrix_size(content)
    assert size is None
