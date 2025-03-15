"""End-to-end tests for the command-line interface."""

import pytest
from pathlib import Path

from converter.cli import main


def test_help_command(capsys):
    """Test that the help command works."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Convert ZMK keymap files to Kanata format" in captured.out
    assert "input_file" in captured.out
    assert "output_file" in captured.out


def test_version_command(capsys):
    """Test that the version command works."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "0.1.0" in captured.out


def test_basic_file_conversion(temp_test_dir):
    """Test basic file conversion through the CLI."""
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
    
    # Verify success
    assert exit_code == 0
    assert kanata_file.exists()
    
    # Verify content
    kanata_content = kanata_file.read_text()
    assert '(deflayer default' in kanata_content
    assert 'a b' in kanata_content.lower()
    assert 'c d' in kanata_content.lower()


def test_missing_input_file(temp_test_dir, capsys):
    """Test error handling for missing input file."""
    input_file = temp_test_dir / "nonexistent.dtsi"
    output_file = temp_test_dir / "output.kbd"
    
    exit_code = main([str(input_file), str(output_file)])
    
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert str(input_file) in captured.err
    assert not output_file.exists()


def test_invalid_input_format(temp_test_dir, capsys):
    """Test error handling for invalid input file format."""
    # Create an invalid ZMK file
    input_file = temp_test_dir / "invalid.dtsi"
    input_file.write_text("This is not a valid ZMK file")
    output_file = temp_test_dir / "output.kbd"
    
    exit_code = main([str(input_file), str(output_file)])
    
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert not output_file.exists()


def test_invalid_output_path(temp_test_dir, capsys):
    """Test error handling for invalid output path."""
    # Create a valid input file
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
    input_file = temp_test_dir / "test_keymap.dtsi"
    input_file.write_text(zmk_content)
    
    # Try to write to a nonexistent directory
    output_file = temp_test_dir / "nonexistent_dir" / "output.kbd"
    
    exit_code = main([str(input_file), str(output_file)])
    
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert str(output_file) in captured.err 