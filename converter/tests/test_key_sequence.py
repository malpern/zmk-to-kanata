"""Tests for key sequence behavior model."""

import pytest

from converter.behaviors.key_sequence import (
    KeySequenceBehavior,
    KeySequenceBinding,
    is_key_sequence_binding,
    parse_key_sequence_behavior,
)


def test_key_sequence_creation():
    """Test creating a valid key sequence behavior."""
    sequence = KeySequenceBehavior(wait_ms=40, tap_ms=40, bindings=["A", "B", "C"])
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


def test_key_sequence_binding_creation():
    """Test creating a key sequence binding."""
    behavior = KeySequenceBehavior(wait_ms=40, tap_ms=40, bindings=["A", "B", "C"])
    binding = KeySequenceBinding(keys=["A", "B", "C"], behavior=behavior)
    assert binding.keys == ["A", "B", "C"]
    assert binding.behavior.wait_ms == 40
    assert binding.behavior.tap_ms == 40


def test_key_sequence_binding_to_kanata():
    """Test converting key sequence binding to Kanata format."""
    binding = KeySequenceBinding(keys=["LSHIFT", "A", "B"])
    assert binding.to_kanata() == "(chord lsft a b)"


def test_key_sequence_binding_from_zmk():
    """Test creating key sequence binding from ZMK format."""
    binding = KeySequenceBinding.from_zmk("&key_sequence LSHIFT A B")
    assert binding.keys == ["lsft", "a", "b"]
    assert binding.to_kanata() == "(chord lsft a b)"


def test_is_key_sequence_binding():
    """Test key sequence binding detection."""
    assert is_key_sequence_binding("&key_sequence A B C")
    assert is_key_sequence_binding("  &key_sequence LSHIFT A  ")
    assert not is_key_sequence_binding("&kp A")
    assert not is_key_sequence_binding("&mo 1")


def test_parse_key_sequence_behavior():
    """Test parsing key sequence behavior configuration."""
    config = {
        "wait-ms": "50",
        "tap-ms": "30",
        "bindings": "<&kp A, &kp B, &kp C>",
    }
    behavior = parse_key_sequence_behavior(config)
    assert behavior.wait_ms == 50
    assert behavior.tap_ms == 30
    assert behavior.bindings == ["kp A", "kp B", "kp C"]


def test_parse_key_sequence_behavior_defaults():
    """Test parsing key sequence behavior with default values."""
    config = {"bindings": "<&kp A>"}
    behavior = parse_key_sequence_behavior(config)
    assert behavior.wait_ms == 30  # Default value
    assert behavior.tap_ms == 30  # Default value
    assert behavior.bindings == ["kp A"]
