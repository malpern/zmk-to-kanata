"""End-to-end tests for output file validation."""

import os
import stat
import pytest
from click.testing import CliRunner
from converter.cli import main as cli_main


# Fixture for sample ZMK content
@pytest.fixture
def sample_zmk_content():
    return """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&kp A &kp B>;
            };
        };
    };
    """


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.e2e
def test_output_file_permissions(runner, tmp_path, sample_zmk_content):
    """Test that the output file has correct permissions."""
    zmk_file = tmp_path / "test.keymap"
    zmk_file.write_text(sample_zmk_content)
    kanata_file = tmp_path / "test.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()

    # Check default file permissions (usually 666 minus umask)
    # This check is OS-dependent and might need adjustment
    # We primarily care that it's readable and writable by the user
    st = os.stat(kanata_file)
    assert bool(st.st_mode & stat.S_IRUSR)  # User readable
    assert bool(st.st_mode & stat.S_IWUSR)  # User writable


@pytest.mark.e2e
def test_output_file_encoding(runner, tmp_path, sample_zmk_content):
    """Test that the output file uses UTF-8 encoding."""
    zmk_file = tmp_path / "test_encoding.keymap"
    zmk_file.write_text(sample_zmk_content)
    kanata_file = tmp_path / "test_encoding.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()

    # Try reading the file with UTF-8 encoding
    try:
        with open(kanata_file, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError:
        pytest.fail("Output file is not valid UTF-8")


@pytest.mark.e2e
def test_output_file_format(runner, tmp_path, sample_zmk_content):
    """Test that the output file has the correct Kanata format structure."""
    zmk_file = tmp_path / "test_format.keymap"
    zmk_file.write_text(sample_zmk_content)
    kanata_file = tmp_path / "test_format.kbd"

    args = [str(zmk_file), "-o", str(kanata_file)]
    result = runner.invoke(cli_main, args)

    assert result.exit_code == 0
    assert kanata_file.exists()

    content = kanata_file.read_text()
    # Basic Kanata structure checks
    assert content.startswith("(defcfg")
    assert "(deflayer default_layer" in content
    assert content.endswith(")\n") or content.endswith(")")  # Check closing parenthesis
