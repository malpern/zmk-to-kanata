"""Integration tests for key validation."""

import pytest
from converter.model.keymap_model import KeyMapping
from converter.behaviors.hold_tap import HoldTap


def test_key_validation_basic():
    """Test basic key validation in KeyMapping."""
    # Valid keys
    KeyMapping(key='A')  # Letter
    KeyMapping(key='N1')  # Number with N prefix
    KeyMapping(key='1')  # Number without N prefix
    KeyMapping(key='F1')  # Function key
    KeyMapping(key='LEFT')  # Navigation key
    KeyMapping(key='LSHIFT')  # Modifier key
    KeyMapping(key='COMMA')  # Punctuation key
    KeyMapping(key='C_MUTE')  # Media key
    KeyMapping(key='KP_N1')  # Numpad key
    KeyMapping(key='INT1')  # International key
    KeyMapping(key='LANG1')  # Language key


def test_key_validation_special():
    """Test special key validation in KeyMapping."""
    KeyMapping(key='NONE')  # No-op key
    KeyMapping(key='TRANS')  # Transparent key


def test_key_validation_layer():
    """Test layer key validation in KeyMapping."""
    KeyMapping(key='mo 0')  # Momentary layer
    KeyMapping(key='mo 1')
    KeyMapping(key='to 0')  # To layer
    KeyMapping(key='to 2')


def test_key_validation_invalid():
    """Test invalid key validation in KeyMapping."""
    with pytest.raises(ValueError) as exc:
        KeyMapping(key='')
    assert "Empty key" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        KeyMapping(key='INVALID')
    assert "Invalid key" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        KeyMapping(key='mo -1')
    assert "Invalid layer number" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        KeyMapping(key='to invalid')
    assert "Invalid layer key format" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        KeyMapping(key='F0')
    assert "Invalid key" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        KeyMapping(key='F25')
    assert "Invalid key" in str(exc.value)


def test_key_validation_with_layer():
    """Test key validation with layer numbers."""
    # Valid layer numbers
    KeyMapping(key='A', layer=0)
    KeyMapping(key='B', layer=1)
    KeyMapping(key='C', layer=10)

    # Invalid layer numbers
    with pytest.raises(ValueError) as exc:
        KeyMapping(key='A', layer=-1)
    assert "Invalid layer number" in str(exc.value)


def test_key_validation_with_hold_tap():
    """Test key validation with hold-tap behavior."""
    # Valid hold-tap keys
    KeyMapping(
        key='A',
        hold_tap=HoldTap(
            behavior_name='mt',
            hold_key='LSHIFT',
            tap_key='A'
        )
    )

    # Invalid hold key
    with pytest.raises(ValueError) as exc:
        KeyMapping(
            key='A',
            hold_tap=HoldTap(
                behavior_name='mt',
                hold_key='INVALID',
                tap_key='A'
            )
        )
    assert "Invalid key mapping" in str(exc.value)

    # Invalid tap key
    with pytest.raises(ValueError) as exc:
        KeyMapping(
            key='INVALID',
            hold_tap=HoldTap(
                behavior_name='mt',
                hold_key='LSHIFT',
                tap_key='INVALID'
            )
        )
    assert "Invalid key mapping" in str(exc.value)


def test_key_validation_with_sticky():
    """Test key validation with sticky behavior."""
    # Valid sticky keys
    KeyMapping(key='LSHIFT', sticky=True)
    KeyMapping(key='RCTRL', sticky=True)
    KeyMapping(key='LALT', sticky=True)

    # Invalid sticky key
    with pytest.raises(ValueError) as exc:
        KeyMapping(key='INVALID', sticky=True)
    assert "Invalid key mapping" in str(exc.value)
