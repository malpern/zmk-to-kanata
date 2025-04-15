"""Fixtures for parser unit tests."""

import pytest
from converter.parser.layer_parser import LayerParser
from converter.parser.macro_parser import MacroParser  # Import MacroParser


@pytest.fixture
def basic_layer_parser():
    """Provides a basic instance of LayerParser."""
    return LayerParser()


@pytest.fixture
def macro_parser():
    """Provides a basic instance of MacroParser."""
    return MacroParser()
