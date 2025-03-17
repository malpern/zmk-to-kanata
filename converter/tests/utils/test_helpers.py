"""Test helper utilities for the ZMK to Kanata converter."""
from pathlib import Path


def get_test_file_path(filename: str) -> Path:
    """Get the full path to a test file in the fixtures directory."""
    return Path(__file__).parent.parent / 'fixtures' / filename


def load_test_file(filename: str) -> str:
    """Load the contents of a test file from the fixtures directory."""
    with open(get_test_file_path(filename)) as f:
        return f.read()


def assert_keymap_valid(keymap: str) -> None:
    """Assert that a keymap string is valid."""
    # Basic validation - will be expanded
    assert keymap.strip(), "Keymap cannot be empty"
    assert "{" in keymap and "}" in keymap, "Must contain at least one layer"


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text for comparison."""
    return " ".join(text.split()) 