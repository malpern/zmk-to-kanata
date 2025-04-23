"""Integration tests for the main converter script (converter/main.py)."""

import pytest
import subprocess
from pathlib import Path

# Define sample DTS content
SIMPLE_DTS = """
/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&kp A &kp B>;
        };
        shifted_layer {
            bindings = <&kp C &kp D>;
        };
    };
};
"""

INCLUDE_HEADER = """
#define TEST_KEY &kp E
"""

DTS_WITH_INCLUDE = """
#include "test_header.h"

/ {
    keymap {
        compatible = "zmk,keymap";
        main_layer {
            bindings = <TEST_KEY &kp F>;
        };
    };
};
"""

INVALID_DTS = """
/ {
    keymap {
        layer // Missing braces
    };
};
"""


@pytest.fixture
def simple_dts_file(tmp_path: Path) -> Path:
    """Fixture to create a simple DTS file."""
    dts_file = tmp_path / "simple.keymap"
    dts_file.write_text(SIMPLE_DTS)
    return dts_file


@pytest.fixture
def dts_with_include_files(tmp_path: Path) -> Path:
    """Fixture to create a DTS file and its include header."""
    include_dir = tmp_path / "include"
    include_dir.mkdir()
    header_file = include_dir / "test_header.h"
    header_file.write_text(INCLUDE_HEADER)

    dts_file = tmp_path / "with_include.keymap"
    dts_file.write_text(DTS_WITH_INCLUDE)
    return dts_file


@pytest.fixture
def invalid_dts_file(tmp_path: Path) -> Path:
    """Fixture to create an invalid DTS file."""
    dts_file = tmp_path / "invalid.keymap"
    dts_file.write_text(INVALID_DTS)
    return dts_file


def run_main_script(args: list[str]) -> subprocess.CompletedProcess:
    """Helper function to run the main script via subprocess."""
    script_path = Path("converter/main.py").resolve()
    # Ensure the script path is correct relative to the project root
    # Adjust if necessary based on where pytest is run from
    command = ["python", str(script_path)] + args
    return subprocess.run(command, capture_output=True, text=True, check=False)


# --- Test Cases ---


def test_main_simple_conversion_stdout(simple_dts_file: Path):
    """Test converting a simple file and printing to stdout."""
    result = run_main_script([str(simple_dts_file)])

    assert result.returncode == 0
    assert "(deflayer default_layer" in result.stdout
    assert "  A B" in result.stdout
    assert "(deflayer shifted_layer" in result.stdout
    assert "  C D" in result.stdout
    assert result.stderr == ""


def test_main_simple_conversion_outfile(simple_dts_file: Path, tmp_path: Path):
    """Test converting a simple file and writing to an output file."""
    output_file = tmp_path / "output.kanata"
    result = run_main_script([str(simple_dts_file), "-o", str(output_file)])

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert output_file.exists()

    content = output_file.read_text()
    assert "(deflayer default_layer" in content
    assert "  A B" in content
    assert "(deflayer shifted_layer" in content
    assert "  C D" in content


def test_main_with_include(dts_with_include_files: Path, tmp_path: Path):
    """Test conversion with an include path."""
    include_dir = tmp_path / "include"
    result = run_main_script([str(dts_with_include_files), "-I", str(include_dir)])

    assert result.returncode == 0
    assert "(deflayer main_layer" in result.stdout
    # TEST_KEY should be expanded to E
    assert "  E F" in result.stdout
    assert result.stderr == ""


def test_main_input_file_not_found(tmp_path: Path):
    """Test error handling for non-existent input file."""
    non_existent_file = tmp_path / "does_not_exist.keymap"
    result = run_main_script([str(non_existent_file)])

    assert result.returncode != 0
    assert "Error: Input file not found" in result.stderr
    assert result.stdout == ""


def test_main_invalid_dts(invalid_dts_file: Path):
    """Test error handling for invalid DTS content."""
    result = run_main_script([str(invalid_dts_file)])

    assert result.returncode != 0
    # Check for a generic conversion failure message,
    # as the exact parser error might change
    assert "Error: Failed to convert keymap" in result.stderr
    assert result.stdout == ""


def test_main_no_args():
    """Test running the script with no arguments (should show usage)."""
    result = run_main_script([])

    assert result.returncode != 0
    # argparse usually prints usage to stderr
    assert "usage:" in result.stderr.lower()
    assert (
        "error: the following arguments are required: input_file"
        in result.stderr.lower()
    )


def test_main_help():
    """Test the --help argument."""
    result = run_main_script(["--help"])

    assert result.returncode == 0
    assert "usage: main.py" in result.stdout.lower()
    assert "positional arguments:" in result.stdout.lower()
    assert "options:" in result.stdout.lower()
    assert result.stderr == ""
