"""Test DTS Preprocessor functionality."""

import os
import pytest
from converter.dts.preprocessor import DtsPreprocessor, PreprocessorError


def test_preprocessor():
    # Get the absolute path to the test fixtures directory
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dts")
    include_path = os.path.join(fixtures_dir, "include")

    # Create preprocessor with include path
    preprocessor = DtsPreprocessor(include_paths=[include_path])

    # Preprocess the test file
    input_file = os.path.join(fixtures_dir, "simple_keymap.zmk")
    result = preprocessor.preprocess(input_file)
    # Remove preprocessor line markers
    filtered = "\n".join(
        line for line in result.splitlines() if not line.strip().startswith("#")
    )
    # Check that the result contains the expected content
    assert "((0) << 0x25 | (0))" in filtered
    assert "((0) << 0x25 | (1))" in filtered
    assert "((0) << 0x25 | (2))" in filtered
    assert "((1) << 0x25 | (0))" in filtered
    assert "((1) << 0x25 | (1))" in filtered
    assert "((1) << 0x25 | (2))" in filtered
    assert "&hm 0x04 LCTL" in filtered
    assert "&kp 0x05" in filtered
    assert "&kp 0x06" in filtered
    assert "&kp 0x07" in filtered
    assert "&kp 0x08" in filtered
    assert "&kp 0x09" in filtered


def test_preprocessor_large_matrix():
    # Get the absolute path to the test fixtures directory
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dts")
    include_path = os.path.join(fixtures_dir, "include")

    # Create preprocessor with include path
    preprocessor = DtsPreprocessor(include_paths=[include_path])

    # Preprocess the test file
    input_file = os.path.join(fixtures_dir, "large_keymap.zmk")
    result = preprocessor.preprocess(input_file)
    # Remove preprocessor line markers
    filtered = "\n".join(
        line for line in result.splitlines() if not line.strip().startswith("#")
    )
    # Check that the result contains the expected content
    for row in range(4):
        for col in range(5):
            assert f"(({row}) << 0x25 | ({col}))" in filtered

    # Check some key bindings
    assert "&kp 0x04" in filtered  # A
    assert "&kp 0x17" in filtered  # T
    assert "&kp 0x10" in filtered  # M


def test_preprocessor_error_handling():
    # Test with non-existent include path (should raise on creation)
    with pytest.raises(PreprocessorError):
        DtsPreprocessor(include_paths=["/nonexistent/path"])

    # Test with non-existent file (should raise on preprocess)
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dts")
    include_path = os.path.join(fixtures_dir, "include")
    preprocessor = DtsPreprocessor(include_paths=[include_path])
    with pytest.raises(PreprocessorError):
        preprocessor.preprocess("nonexistent_file.zmk")
