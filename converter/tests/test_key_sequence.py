"""Tests for key sequence behavior model."""
import pytest
from converter.behaviors.key_sequence import KeySequenceBehavior


def test_key_sequence_creation():
    """Test creating a valid key sequence behavior."""
    sequence = KeySequenceBehavior(
        wait_ms=40,
        tap_ms=40,
        bindings=["A", "B", "C"]
    )
    assert sequence.wait_ms == 40
    assert sequence.tap_ms == 40
    assert sequence.bindings == ["A", "B", "C"]


def test_key_sequence_validation():
    """Test validation of key sequence behavior attributes."""
    # Test negative wait_ms
    with pytest.raises(ValueError, match="wait_ms must be non-negative"):
        KeySequenceBehavior(wait_ms=-1, tap_ms=40, bindings=["A"])

    # Test negative tap_ms
    with pytest.raises(ValueError, match="tap_ms must be non-negative"):
        KeySequenceBehavior(wait_ms=40, tap_ms=-1, bindings=["A"])

    # Test empty bindings
    with pytest.raises(ValueError, match="bindings list cannot be empty"):
        KeySequenceBehavior(wait_ms=40, tap_ms=40, bindings=[]) 