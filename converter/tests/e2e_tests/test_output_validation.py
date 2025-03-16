"""End-to-end tests for output file validation."""

import os
import stat
import pytest

from converter.cli import main


def test_output_file_permissions(temp_test_dir):
    """Test that output files have correct read/write permissions."""
    # Create a sample ZMK keymap file
    zmk_content = '''
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B
                &kp C &kp D
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'test_keymap.dtsi'
    zmk_file.write_text(zmk_content)
    
    # Create output path for Kanata config
    kanata_file = temp_test_dir / 'test_config.kbd'
    
    # Run the conversion
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    # Check file permissions
    st = os.stat(kanata_file)
    mode = st.st_mode
    
    # Verify owner has read/write permissions
    assert mode & stat.S_IRUSR  # Read permission
    assert mode & stat.S_IWUSR  # Write permission
    
    # Verify group has read permission
    assert mode & stat.S_IRGRP  # Read permission
    
    # Verify others have read permission
    assert mode & stat.S_IROTH  # Read permission


def test_output_file_encoding(temp_test_dir):
    """Test that output files use UTF-8 encoding."""
    # Create a sample ZMK keymap file with non-ASCII characters
    zmk_content = '''
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B  // UTF-8: ñ, é, ß
                &kp C &kp D
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'test_keymap.dtsi'
    zmk_file.write_text(zmk_content, encoding='utf-8')
    
    # Create output path for Kanata config
    kanata_file = temp_test_dir / 'test_config.kbd'
    
    # Run the conversion
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    # Try reading the file with UTF-8 encoding
    try:
        content = kanata_file.read_text(encoding='utf-8')
        assert isinstance(content, str)
    except UnicodeError:
        pytest.fail("Output file is not valid UTF-8")


def test_output_file_format(temp_test_dir):
    """Test that output files follow the Kanata format specification."""
    # Create a sample ZMK keymap file
    zmk_content = '''
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B
                &kp C &kp D
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'test_keymap.dtsi'
    zmk_file.write_text(zmk_content)
    
    # Create output path for Kanata config
    kanata_file = temp_test_dir / 'test_config.kbd'
    
    # Run the conversion
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    # Read and verify the content
    content = kanata_file.read_text()
    
    # Check basic Kanata format requirements
    assert content.strip(), "File should not be empty"
    assert content.endswith("\n"), "File should end with a newline"
    
    # Check layer definition format
    lines = content.splitlines()
    layer_start = next(
        i for i, line in enumerate(lines)
        if line.startswith("(deflayer")
    )
    
    # Verify layer definition syntax
    assert lines[layer_start].startswith("(deflayer")
    assert ")" in lines[layer_start + 3]
    
    # Verify indentation
    for line in lines[layer_start + 1:layer_start + 3]:
        assert line.startswith("  "), "Must be indented with 2 spaces"
    
    # Verify key definitions
    key_line = lines[layer_start + 1].strip()
    assert all(key in key_line for key in ["a", "b"]), "Keys should be lowercase"
    assert " " in key_line, "Keys should be space-separated" 