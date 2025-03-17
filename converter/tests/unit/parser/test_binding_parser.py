"""Tests for the binding parser."""

import pytest
from converter.parser.binding_parser import (
    BindingParser,
    BindingParseError,
    KeyMapping
)


@pytest.fixture
def parser():
    """Create a binding parser instance."""
    return BindingParser()


def test_simple_key_press(parser):
    """Test parsing simple key press bindings."""
    test_cases = [
        ("&kp A", "A"),
        ("&kp B", "B"),
        ("&kp SPACE", "SPACE"),
        ("&kp LSHIFT", "LSHIFT"),
        ("&kp N1", "N1")
    ]
    for binding, expected in test_cases:
        result = parser.parse(binding)
        assert isinstance(result, KeyMapping)
        assert result.key == expected


def test_layer_tap(parser):
    """Test parsing layer tap bindings."""
    test_cases = [
        ("&lt 1 A", "lt(1,A)"),
        ("&lt 2 B", "lt(2,B)"),
        ("&lt 3 SPACE", "lt(3,SPACE)")
    ]
    for binding, expected in test_cases:
        result = parser.parse(binding)
        assert isinstance(result, KeyMapping)
        assert result.key == expected


def test_mod_tap(parser):
    """Test parsing mod tap bindings."""
    test_cases = [
        ("&mt LSHIFT A", "mt(LSHIFT,A)"),
        ("&mt LCTRL B", "mt(LCTRL,B)"),
        ("&mt LALT SPACE", "mt(LALT,SPACE)")
    ]
    for binding, expected in test_cases:
        result = parser.parse(binding)
        assert isinstance(result, KeyMapping)
        assert result.key == expected


def test_layer_behaviors(parser):
    """Test parsing layer behavior bindings."""
    test_cases = [
        ("&mo 1", "mo(1)"),
        ("&to 2", "to(2)"),
        ("&tog 3", "tog(3)")
    ]
    for binding, expected in test_cases:
        result = parser.parse(binding)
        assert isinstance(result, KeyMapping)
        assert result.key == expected


def test_transparent(parser):
    """Test parsing transparent binding."""
    result = parser.parse("&trans")
    assert isinstance(result, KeyMapping)
    assert result.key == "trans"


def test_nested_bindings(parser):
    """Test parsing nested bindings."""
    test_cases = [
        ("&lt 1 (&kp A)", "lt(1,A)"),
        ("&mt LSHIFT (&kp B)", "mt(LSHIFT,B)"),
        ("&lt 2 (&mt LCTRL C)", "lt(2,mt(LCTRL,C))")
    ]
    for binding, expected in test_cases:
        result = parser.parse(binding)
        assert isinstance(result, KeyMapping)
        assert result.key == expected


def test_invalid_bindings(parser):
    """Test handling of invalid bindings."""
    test_cases = [
        "",  # Empty binding
        "kp A",  # Missing &
        "&invalid A",  # Invalid behavior
        "&kp",  # Missing param
        "&lt 1",  # Missing second param
        "&mt",  # Missing both params
        "&trans A"  # Extra param for trans
    ]
    for binding in test_cases:
        with pytest.raises(BindingParseError) as exc_info:
            parser.parse(binding)
        assert binding in str(exc_info.value)


def test_invalid_nested_bindings(parser):
    """Test handling of invalid nested bindings."""
    test_cases = [
        "&lt 1 (kp A)",  # Missing & in inner binding
        "&lt 1 (&invalid A)",  # Invalid inner behavior
        "&lt 1 (&lt 2 (&kp A))",  # Too deep nesting
        "&lt 1 ()",  # Empty inner binding
        "&lt 1 (&kp)",  # Invalid inner binding
        "&lt (&kp A) 1"  # Invalid nesting format
    ]
    for binding in test_cases:
        with pytest.raises(BindingParseError) as exc_info:
            parser.parse(binding)
        assert binding in str(exc_info.value)


def test_invalid_parameters(parser):
    """Test handling of invalid parameters."""
    test_cases = [
        ("&kp INVALID", "Invalid key"),
        ("&lt INVALID A", "Invalid layer number"),
        ("&lt 1 INVALID", "Invalid key"),
        ("&mt INVALID A", "Invalid modifier"),
        ("&mt LSHIFT INVALID", "Invalid key")
    ]
    for binding, expected_error in test_cases:
        with pytest.raises(BindingParseError) as exc_info:
            parser.parse(binding)
        assert expected_error in str(exc_info.value)


def test_whitespace_handling(parser):
    """Test handling of different whitespace formats."""
    test_cases = [
        ("&kp    A", "A"),  # Multiple spaces
        ("&kp\tB", "B"),  # Tab
        ("&lt    1    A", "lt(1,A)"),  # Multiple spaces in lt
        ("&mt\tLSHIFT\tB", "mt(LSHIFT,B)"),  # Tabs in mt
        ("  &kp C  ", "C"),  # Leading/trailing spaces
        ("&lt 1   (&kp A)", "lt(1,A)")  # Spaces in nested binding
    ]
    for binding, expected in test_cases:
        result = parser.parse(binding)
        assert isinstance(result, KeyMapping)
        assert result.key == expected
