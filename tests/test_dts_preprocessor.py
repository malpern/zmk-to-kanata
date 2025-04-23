import os
import pytest
from converter.dts_preprocessor import DtsPreprocessor


def test_preprocessor():
    # Get the absolute path to the test fixtures directory
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'dts')
    include_path = os.path.join(fixtures_dir, 'include')
    
    # Create preprocessor with include path
    preprocessor = DtsPreprocessor(include_paths=[include_path])
    
    # Preprocess the test file
    input_file = os.path.join(fixtures_dir, 'simple_keymap.zmk')
    result = preprocessor.preprocess(input_file)
    
    # Check that the result contains the expected content
    assert 'RC(0,0)' in result
    assert 'RC(0,1)' in result
    assert 'RC(0,2)' in result
    assert 'RC(1,0)' in result
    assert 'RC(1,1)' in result
    assert 'RC(1,2)' in result
    assert '&kp A' in result
    assert '&kp B' in result
    assert '&kp C' in result
    assert '&kp D' in result
    assert '&kp E' in result
    assert '&kp F' in result


def test_preprocessor_error_handling():
    # Test with non-existent file
    preprocessor = DtsPreprocessor(include_paths=['/nonexistent/path'])
    with pytest.raises(FileNotFoundError):
        preprocessor.preprocess('nonexistent_file.zmk')
    
    # Test with invalid include path
    with pytest.raises(RuntimeError):
        DtsPreprocessor(include_paths=['/nonexistent/path']).preprocess(
            'tests/fixtures/dts/simple_keymap.zmk'
        ) 