"""Basic file operation tests for end-to-end testing."""

import pytest
from pathlib import Path
from converter.main import convert_keymap


def test_temp_dir_fixture(temp_test_dir):
    """Test that the temporary directory fixture works."""
    assert temp_test_dir.exists()
    assert temp_test_dir.is_dir()


def test_basic_file_conversion(temp_test_dir):
    """Test basic file conversion from ZMK to Kanata format."""
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
    
    # Convert the file
    convert_keymap(zmk_file, kanata_file)
    
    # Verify the output file exists
    assert kanata_file.exists()
    
    # Read and verify the content
    kanata_content = kanata_file.read_text()
    assert 'a' in kanata_content.lower()
    assert 'b' in kanata_content.lower()
    assert 'c' in kanata_content.lower()
    assert 'd' in kanata_content.lower()


def test_output_file_format(temp_test_dir):
    """Test that the output file follows the Kanata format."""
    # Create a sample ZMK keymap file with multiple layers
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
        
        symbol_layer {
            bindings = <
                &kp N1 &kp N2
                &kp N3 &kp N4
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'test_keymap.dtsi'
    zmk_file.write_text(zmk_content)
    
    # Create output path for Kanata config
    kanata_file = temp_test_dir / 'test_config.kbd'
    
    # Convert the file
    convert_keymap(zmk_file, kanata_file)
    
    # Read and verify the content
    kanata_content = kanata_file.read_text()
    
    # Verify layer definitions
    assert '(deflayer default' in kanata_content
    assert '(deflayer symbol' in kanata_content
    
    # Verify key mappings
    lines = kanata_content.splitlines()
    
    # Find the default layer
    default_layer_start = next(
        i for i, line in enumerate(lines)
        if '(deflayer default' in line
    )
    assert 'a b' in lines[default_layer_start + 1].strip()
    assert 'c d' in lines[default_layer_start + 2].strip()
    
    # Find the symbol layer
    symbol_layer_start = next(
        i for i, line in enumerate(lines)
        if '(deflayer symbol' in line
    )
    assert '1 2' in lines[symbol_layer_start + 1].strip()
    assert '3 4' in lines[symbol_layer_start + 2].strip() 