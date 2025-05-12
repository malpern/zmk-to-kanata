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

    # Check that the result contains the expected content
    assert "((0) << 0x25 /* 8 */ | (0))" in result
    assert "((0) << 0x25 /* 8 */ | (1))" in result
    assert "((0) << 0x25 /* 8 */ | (2))" in result
    assert "((1) << 0x25 /* 8 */ | (0))" in result
    assert "((1) << 0x25 /* 8 */ | (1))" in result
    assert "((1) << 0x25 /* 8 */ | (2))" in result
    assert "&kp 0x04" in result
    assert "&kp 0x05" in result
    assert "&kp 0x06" in result
    assert "&kp 0x07" in result
    assert "&kp 0x08" in result
    assert "&kp 0x09" in result


def test_preprocessor_large_matrix():
    # Get the absolute path to the test fixtures directory
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dts")
    include_path = os.path.join(fixtures_dir, "include")

    # Create preprocessor with include path
    preprocessor = DtsPreprocessor(include_paths=[include_path])

    # Preprocess the test file
    input_file = os.path.join(fixtures_dir, "large_keymap.zmk")
    result = preprocessor.preprocess(input_file)

    # Check that the result contains the expected content
    for row in range(4):
        for col in range(5):
            assert f"(({row}) << 0x25 /* 8 */ | ({col}))" in result

    # Check some key bindings
    assert "&kp 0x04" in result  # A
    assert "&kp 0x17" in result  # T
    assert "&kp 0x10" in result  # M


def test_preprocessor_error_handling():
    # Test with non-existent file
    preprocessor = DtsPreprocessor(include_paths=["/nonexistent/path"])
    with pytest.raises(PreprocessorError):
        preprocessor.preprocess("nonexistent_file.zmk")

    # Test with invalid include path
    with pytest.raises(PreprocessorError):
        DtsPreprocessor(include_paths=["/nonexistent/path"]).preprocess(
            "tests/fixtures/dts/simple_keymap.zmk"
        )
