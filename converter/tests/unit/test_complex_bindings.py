"""Tests for complex binding formats."""

import pytest
from converter.model.keymap_model import KeyMapping, Layer
from converter.behaviors.hold_tap import HoldTap
from converter.behaviors.macro import MacroBinding
from converter.behaviors.sticky_key import StickyKeyBinding


def test_nested_hold_tap_with_layer():
    """Test hold-tap behavior with layer switching."""
    # Hold: layer switch, Tap: key press
    binding = KeyMapping(
        key='A',
        hold_tap=HoldTap(
            behavior_name='ht',
            hold_key='mo 1',
            tap_key='A'
        )
    )
    assert binding.to_kanata() == '@ht_mo_1_A'


def test_hold_tap_with_sticky():
    """Test hold-tap behavior with sticky keys."""
    # Hold: sticky shift, Tap: key press
    binding = KeyMapping(
        key='B',
        hold_tap=HoldTap(
            behavior_name='ht',
            hold_key='LSHIFT',
            tap_key='B'
        ),
        sticky=True
    )
    assert binding.to_kanata() == '@ht_sticky-lsft_b'


def test_multi_layer_sequence():
    """Test sequence of layer changes."""
    layer = Layer("test_layer", bindings=[
        KeyMapping(key='mo 1'),  # Momentary layer 1
        KeyMapping(key='to 2'),  # Switch to layer 2
        KeyMapping(key='mo 3'),  # Momentary layer 3
    ])
    expected = (
        "(deflayer test_layer\n"
        "  (layer-while-held 1) (layer-switch 2) (layer-while-held 3)\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_complex_modifier_chain():
    """Test chained modifier keys."""
    bindings = [
        KeyMapping(key='LSHIFT', sticky=True),  # Sticky shift
        KeyMapping(key='LCTRL'),   # Regular control
        KeyMapping(key='A'),       # Regular key
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  sticky-lsft lctl a\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_mixed_case_handling():
    """Test handling of mixed case keys."""
    bindings = [
        KeyMapping(key='LSHIFT'),  # All caps
        KeyMapping(key='Ctrl'),    # Mixed case
        KeyMapping(key='a'),       # Lower case
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  lsft lctl a\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_special_key_combinations():
    """Test combinations with special keys."""
    bindings = [
        KeyMapping(key='NONE'),    # No-op
        KeyMapping(key='TRANS'),   # Transparent
        KeyMapping(key='A'),       # Regular key
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  none _ a\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_complex_macro_binding():
    """Test complex macro with timing and modifiers."""
    macro = MacroBinding(
        name="complex_macro",
        sequence=[
            ('LSHIFT', 'press'),
            ('wait', 50),
            ('A', 'tap'),
            ('wait', 50),
            ('LSHIFT', 'release')
        ]
    )
    binding = KeyMapping(key=macro.name)
    assert binding.to_kanata() == "@complex_macro"


def test_layer_with_empty_slots():
    """Test layer with empty slots."""
    bindings = [
        KeyMapping(key='A'),
        KeyMapping(key='NONE'),  # Empty slot
        KeyMapping(key='B'),
        KeyMapping(key='TRANS'), # Transparent slot
        KeyMapping(key='C')
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  a none b _ c\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_complex_sticky_combinations():
    """Test complex combinations with sticky keys."""
    bindings = [
        KeyMapping(key='LSHIFT', sticky=True),
        KeyMapping(key='LCTRL', sticky=True),
        KeyMapping(key='A'),
        KeyMapping(key='B')
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  sticky-lsft sticky-lctl a b\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_function_key_formats():
    """Test various function key formats."""
    bindings = [
        KeyMapping(key='F1'),      # Basic function key
        KeyMapping(key='F11'),     # Two digit function key
        KeyMapping(key='F24'),     # Maximum function key
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  f1 f11 f24\n"
        ")"
    )
    assert layer.to_kanata() == expected


def test_numpad_key_formats():
    """Test various numpad key formats."""
    bindings = [
        KeyMapping(key='KP_N1'),       # Number key
        KeyMapping(key='KP_PLUS'),     # Operator key
        KeyMapping(key='KP_ENTER'),    # Action key
    ]
    layer = Layer("test_layer", bindings=bindings)
    expected = (
        "(deflayer test_layer\n"
        "  kp1 kp_plus kp_enter\n"
        ")"
    )
    assert layer.to_kanata() == expected
