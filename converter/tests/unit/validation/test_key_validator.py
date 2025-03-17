"""Tests for the key validator module."""

import pytest
from converter.validation.key_validator import (
    validate_key,
    convert_to_kanata,
    get_key_category,
    KeyValidationError
)


def test_validate_key_basic():
    """Test basic key validation."""
    # Valid keys
    assert validate_key('A') is True
    assert validate_key('B') is True
    assert validate_key('Z') is True
    assert validate_key('N1') is True
    assert validate_key('F1') is True
    assert validate_key('F24') is True
    assert validate_key('LEFT') is True
    assert validate_key('RIGHT') is True
    assert validate_key('LSHIFT') is True
    assert validate_key('RCTRL') is True


def test_validate_key_special():
    """Test special key validation."""
    assert validate_key('NONE') is True
    assert validate_key('TRANS') is True


def test_validate_key_layer():
    """Test layer key validation."""
    assert validate_key('mo 0') is True
    assert validate_key('mo 1') is True
    assert validate_key('to 0') is True
    assert validate_key('to 2') is True


def test_validate_key_invalid():
    """Test invalid key validation."""
    with pytest.raises(KeyValidationError):
        validate_key('')

    with pytest.raises(KeyValidationError):
        validate_key('INVALID')

    with pytest.raises(KeyValidationError):
        validate_key('mo -1')

    with pytest.raises(KeyValidationError):
        validate_key('to invalid')

    with pytest.raises(KeyValidationError):
        validate_key('F0')

    with pytest.raises(KeyValidationError):
        validate_key('F25')


def test_convert_to_kanata_basic():
    """Test basic key conversion to Kanata format."""
    assert convert_to_kanata('A') == 'a'
    assert convert_to_kanata('B') == 'b'
    assert convert_to_kanata('N1') == '1'
    assert convert_to_kanata('1') == '1'
    assert convert_to_kanata('F1') == 'f1'
    assert convert_to_kanata('F12') == 'f12'


def test_convert_to_kanata_special():
    """Test special key conversion to Kanata format."""
    assert convert_to_kanata('NONE') == 'none'
    assert convert_to_kanata('TRANS') == '_'
    assert convert_to_kanata('LSHIFT') == 'lsft'
    assert convert_to_kanata('RCTRL') == 'rctl'
    assert convert_to_kanata('LGUI') == 'lmet'
    assert convert_to_kanata('RWIN') == 'rmet'


def test_convert_to_kanata_layer():
    """Test layer key conversion to Kanata format."""
    assert convert_to_kanata('mo 0') == '(layer-while-held 0)'
    assert convert_to_kanata('mo 1') == '(layer-while-held 1)'
    assert convert_to_kanata('to 0') == '(layer-switch 0)'
    assert convert_to_kanata('to 2') == '(layer-switch 2)'


def test_convert_to_kanata_invalid():
    """Test invalid key conversion to Kanata format."""
    with pytest.raises(KeyValidationError):
        convert_to_kanata('')

    with pytest.raises(KeyValidationError):
        convert_to_kanata('INVALID')

    with pytest.raises(KeyValidationError):
        convert_to_kanata('mo -1')

    with pytest.raises(KeyValidationError):
        convert_to_kanata('to invalid')


def test_get_key_category():
    """Test key categorization."""
    assert get_key_category('A') == 'letter'
    assert get_key_category('N1') == 'number'
    assert get_key_category('1') == 'number'
    assert get_key_category('F1') == 'function'
    assert get_key_category('LEFT') == 'navigation'
    assert get_key_category('ENTER') == 'editing'
    assert get_key_category('LSHIFT') == 'modifier'
    assert get_key_category('COMMA') == 'punctuation'
    assert get_key_category('EXCL') == 'symbol'
    assert get_key_category('C_MUTE') == 'media'
    assert get_key_category('KP_N1') == 'numpad'
    assert get_key_category('INT1') == 'international'
    assert get_key_category('LANG1') == 'language'
    assert get_key_category('NONE') == 'special'
    assert get_key_category('mo 0') == 'layer'
    assert get_key_category('INVALID') is None
