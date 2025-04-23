"""End-to-end tests for file operations."""

import pytest
from pathlib import Path
from converter.main import convert_zmk_to_kanata


def test_temp_dir_fixture(temp_test_dir):
    """Test that the temporary directory fixture works."""
    assert temp_test_dir.exists()
    assert temp_test_dir.is_dir()


def test_basic_file_conversion(temp_test_dir):
    """Test basic file conversion from ZMK to Kanata format."""
    # Get the path to the fixtures directory
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "dts"
    include_dir = fixtures_dir / "include"
    dt_bindings_dir = include_dir / "dt-bindings"

    # Create a sample ZMK keymap file
    zmk_content = """
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
"""
    zmk_file = temp_test_dir / "test_keymap.dtsi"
    zmk_file.write_text(zmk_content)

    # Create output path for Kanata config
    kanata_file = temp_test_dir / "test_keymap.kbd"

    # Convert the file with include paths
    convert_zmk_to_kanata(
        str(zmk_file), include_paths=[str(include_dir), str(dt_bindings_dir)]
    )

    # Verify the output file exists
    assert kanata_file.exists()

    # Read and verify the content
    kanata_content = kanata_file.read_text()
    assert "a" in kanata_content.lower()
    assert "b" in kanata_content.lower()
    assert "c" in kanata_content.lower()
    assert "d" in kanata_content.lower()


def test_output_file_format(temp_test_dir):
    """Test that the output file has the correct format."""
    # Get the path to the fixtures directory
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "dts"
    include_dir = fixtures_dir / "include"
    dt_bindings_dir = include_dir / "dt-bindings"

    # Create a sample ZMK keymap file
    zmk_content = """
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
"""
    zmk_file = temp_test_dir / "test_format.dtsi"
    zmk_file.write_text(zmk_content)

    # Create output path for Kanata config
    kanata_file = temp_test_dir / "test_format.kbd"

    # Convert the file with include paths
    convert_zmk_to_kanata(
        str(zmk_file), include_paths=[str(include_dir), str(dt_bindings_dir)]
    )

    # Verify the output file exists and has correct format
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert content.startswith("(defcfg")
    assert "(deflayer default_layer" in content
    assert content.endswith(")\n") or content.endswith(")")


@pytest.mark.e2e
def test_convert_valid_file(tmp_path):
    """Test converting a valid ZMK file."""
    # Get the path to the fixtures directory
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "dts"
    include_dir = fixtures_dir / "include"
    dt_bindings_dir = include_dir / "dt-bindings"

    # Create a sample ZMK keymap file
    zmk_content = """
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
"""
    zmk_file = tmp_path / "valid_keymap.dtsi"
    zmk_file.write_text(zmk_content)

    # Create output path for Kanata config
    kanata_file = tmp_path / "valid_keymap.kbd"

    # Convert the file with include paths
    convert_zmk_to_kanata(
        str(zmk_file), include_paths=[str(include_dir), str(dt_bindings_dir)]
    )

    # Verify the output file exists and has correct content
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "a" in content.lower()
    assert "b" in content.lower()
    assert "c" in content.lower()
    assert "d" in content.lower()


@pytest.mark.e2e
def test_convert_nonexistent_file():
    """Test converting a nonexistent input file."""
    with pytest.raises(FileNotFoundError):
        convert_zmk_to_kanata("nonexistent_file.keymap")


@pytest.mark.e2e
def test_convert_missing_includes(tmp_path):
    """Test converting a file with missing include files."""
    zmk_content = """
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
"""
    zmk_file = tmp_path / "missing_includes.dtsi"
    zmk_file.write_text(zmk_content)

    with pytest.raises(ValueError) as exc_info:
        convert_zmk_to_kanata(str(zmk_file), include_paths=[])
    assert "Preprocessing failed" in str(exc_info.value)
