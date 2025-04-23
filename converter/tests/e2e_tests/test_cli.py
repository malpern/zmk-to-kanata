"""End-to-end tests for the command-line interface."""

import pytest
from click.testing import CliRunner

from converter.cli import main as cli_main


def test_help_command(capsys):
    """Test that the help command works."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Convert ZMK keymap files to Kanata format" in captured.out
    assert "input_file" in captured.out
    assert "output_file" in captured.out


def test_version_command(capsys):
    """Test that the version command works."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["--version"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "0.1.0" in captured.out


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.e2e
def test_basic_file_conversion(runner, tmp_path):
    """Test basic file conversion via CLI."""
    zmk_file = tmp_path / "test.keymap"
    kanata_file = tmp_path / "test.kbd"

    # Minimal valid ZMK content
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            layer_0 {
                bindings = <&kp A>;
            };
        };
    };
    """
    zmk_file.write_text(zmk_content)

    # Use cli_main directly with args list
    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(deflayer layer_0" in content
    assert "a" in content  # Check basic transformation


@pytest.mark.e2e
def test_missing_input_file(runner):
    """Test CLI error handling for missing input file."""
    args = ["nonexistent.keymap", "-o", "output.kbd"]
    result = runner.invoke(cli_main, args)
    assert result.exit_code != 0  # Expect non-zero exit code
    # Error message comes from argparse/main, check stderr
    assert "Error: Input file not found" in result.stderr


@pytest.mark.e2e
def test_invalid_input_format(runner, tmp_path):
    """Test CLI error handling for invalid ZMK format."""
    zmk_file = tmp_path / "invalid.keymap"
    kanata_file = tmp_path / "invalid.kbd"
    zmk_file.write_text("this is not valid dts content")

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)
    assert result.exit_code != 0  # Expect non-zero exit code
    # Check for a relevant error message in stderr (exact message might vary)
    assert "Error: Failed to convert keymap" in result.stderr
    assert "Parsing failed" in result.stderr  # Or similar from parser


@pytest.mark.e2e
def test_invalid_output_path(runner, tmp_path):
    """Test CLI error handling for invalid output path (e.g., directory)."""
    zmk_file = tmp_path / "test.keymap"
    # Minimal valid ZMK content
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            layer_0 {
                bindings = <&kp A>;
            };
        };
    };
    """
    zmk_file.write_text(zmk_content)

    # Use the directory itself as the output path
    args = [str(zmk_file), "-o", str(tmp_path)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code != 0  # Expect non-zero exit code
    # Check for file writing error (exact message depends on OS/Python version)
    assert "Error:" in result.stderr
    assert "Is a directory" in result.stderr or "Permission denied" in result.stderr
