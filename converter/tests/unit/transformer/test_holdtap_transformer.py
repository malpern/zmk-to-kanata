"""Unit tests for the holdtap transformer module."""
import pytest
from converter.holdtap_transformer import HoldTapTransformer
from converter.model.keymap_model import HoldTapBehavior, KeyMapping
from converter.behaviors.layer import LayerBehavior
from converter.behaviors.macro import MacroBehavior
from converter.behaviors.sticky_key import StickyKeyBehavior
from converter.behaviors.key_sequence import KeySequenceBehavior
from converter.transformer.layer_transformer import LayerTransformer


@pytest.fixture
def transformer():
    """Create a HoldTapTransformer instance."""
    return HoldTapTransformer()


@pytest.fixture
def layer_transformer():
    """Create a LayerTransformer instance."""
    return LayerTransformer()


def test_basic_holdtap_transformations(transformer):
    """Test basic hold-tap transformations."""
    # Test letter combinations
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold a b)"

    # Test with modifiers
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeyMapping(key="SPACE")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold lsft spc)"

    # Test with numbers
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="N1"),
        tap=KeyMapping(key="N2")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold 1 2)"


def test_layer_holdtap_transformations(transformer):
    """Test hold-tap transformations with layer switches."""
    # Test layer momentary switch
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="mo 1"),
        tap=KeyMapping(key="A")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold @layer1 a)"

    # Test with transparent key
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="trans"),
        tap=KeyMapping(key="B")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold _ b)"


def test_special_key_holdtap_transformations(transformer):
    """Test hold-tap transformations with special keys."""
    # Test with function keys
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="F1"),
        tap=KeyMapping(key="F2")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold f1 f2)"

    # Test with media keys
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="C_MUTE"),
        tap=KeyMapping(key="C_VOL_UP")
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold c_mute c_vol_up)"

    # Test with navigation keys
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="PG_UP"),
        tap=KeyMapping(key="PG_DN")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold pg_up pg_dn)"


def test_timing_parameter_transformations(transformer):
    """Test hold-tap transformations with timing parameters."""
    # Test with custom timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B"),
        timeout=200
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold-ms 200 a b)" in result

    # Test with default timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B")
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold a b)" in result


def test_modifier_holdtap_combinations(transformer):
    """Test hold-tap transformations with modifier combinations."""
    # Test shift combinations
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeyMapping(key="RSHIFT")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold lsft rsft)"

    # Test control combinations
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LCTRL"),
        tap=KeyMapping(key="RCTRL")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold lctl rctl)"

    # Test alt combinations
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LALT"),
        tap=KeyMapping(key="RALT")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold lalt ralt)"


def test_basic_key_mapping(transformer):
    """Test basic key mapping transformation."""
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeyMapping(key="A")
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold a lshift)"


def test_layer_in_hold_position(transformer, layer_transformer):
    """Test layer behavior in hold position."""
    transformer.set_layer_transformer(layer_transformer)
    behavior = HoldTapBehavior(
        hold=LayerBehavior(layer=1),
        tap=KeyMapping(key="A")
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold a (layer-while-held 1))"


def test_nested_holdtap_invalid(transformer):
    """Test nested hold-tap behavior (should be invalid)."""
    nested = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeyMapping(key="B")
    )
    behavior = HoldTapBehavior(
        hold=nested,
        tap=KeyMapping(key="A")
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold a unknown)"


def test_macro_in_hold_invalid(transformer):
    """Test macro behavior in hold position (should be invalid)."""
    behavior = HoldTapBehavior(
        hold=MacroBehavior(name="test_macro"),
        tap=KeyMapping(key="A")
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold a unknown)"


def test_sticky_key_in_tap_invalid(transformer):
    """Test sticky key behavior in tap position (should be invalid)."""
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=StickyKeyBehavior(key=KeyMapping(key="LCTRL"))
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold unknown lshift)"


def test_key_sequence_in_tap_invalid(transformer):
    """Test key sequence behavior in tap position (should be invalid)."""
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeySequenceBehavior(bindings=["A", "B", "C"])
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold unknown lshift)"


def test_both_positions_invalid(transformer):
    """Test both hold and tap positions being invalid."""
    nested_hold = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeyMapping(key="B")
    )
    nested_tap = StickyKeyBehavior(key=KeyMapping(key="LCTRL"))
    behavior = HoldTapBehavior(
        hold=nested_hold,
        tap=nested_tap
    )
    result = transformer.transform_binding(behavior)
    assert result == "(tap-hold unknown unknown)"


def test_multiple_layers_invalid(transformer, layer_transformer):
    """Test multiple layer behaviors (should be invalid)."""
    transformer.set_layer_transformer(layer_transformer)
    behavior = HoldTapBehavior(
        hold=LayerBehavior(layer=1),
        tap=LayerBehavior(layer=2)
    )
    result = transformer.transform_binding(behavior)
    # Layer behaviors are only valid in hold position
    assert result == "(tap-hold unknown (layer-while-held 1))"
