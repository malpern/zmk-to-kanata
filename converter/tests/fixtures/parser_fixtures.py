"""Fixtures for parser tests."""
import pytest
from converter.layer_parser import LayerParser
from converter.taphold_parser import TapHoldParser
from converter.parser.macro_parser_v2 import MacroParser
from ..utils.test_helpers import load_test_file


@pytest.fixture
def basic_layer_parser():
    """Create a clean LayerParser instance."""
    return LayerParser(clean_state=True)


@pytest.fixture
def taphold_parser():
    """Create a clean TapHoldParser instance."""
    return TapHoldParser()


@pytest.fixture
def macro_parser():
    """Create a clean MacroParser instance."""
    return MacroParser()


@pytest.fixture
def basic_keymap():
    """Load the basic keymap test file."""
    return load_test_file('basic_keymap.kbd')


@pytest.fixture
def complex_keymap():
    """Load the complex keymap test file."""
    return load_test_file('complex_keymap.kbd')
