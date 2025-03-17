"""Unit tests for the sticky key transformer module."""
import pytest
from converter.sticky_key_transformer import StickyKeyTransformer
from converter.model.keymap_model import StickyKeyBehavior, KeyMapping


@pytest.fixture
def transformer():
    """Create a StickyKeyTransformer instance."""
    return StickyKeyTransformer()


def test_basic_sticky_key_transformations(transformer):
    """Test basic sticky key transformations."""
    # Test with modifiers
    behavior = StickyKeyBehavior(key=KeyMapping(key="LSHIFT"))
    assert transformer.transform_binding(behavior) == "sticky-lsft"

    behavior = StickyKeyBehavior(key=KeyMapping(key="RSHIFT"))
    assert transformer.transform_binding(behavior) == "sticky-rsft"

    behavior = StickyKeyBehavior(key=KeyMapping(key="LCTRL"))
    assert transformer.transform_binding(behavior) == "sticky-lctl"


def test_modifier_combinations(transformer):
    """Test sticky key transformations with different modifiers."""
    # Test all shift variants
    behavior = StickyKeyBehavior(key=KeyMapping(key="LSHIFT"))
    assert transformer.transform_binding(behavior) == "sticky-lsft"

    behavior = StickyKeyBehavior(key=KeyMapping(key="RSHIFT"))
    assert transformer.transform_binding(behavior) == "sticky-rsft"

    # Test all control variants
    behavior = StickyKeyBehavior(key=KeyMapping(key="LCTRL"))
    assert transformer.transform_binding(behavior) == "sticky-lctl"

    behavior = StickyKeyBehavior(key=KeyMapping(key="RCTRL"))
    assert transformer.transform_binding(behavior) == "sticky-rctl"

    # Test all alt variants
    behavior = StickyKeyBehavior(key=KeyMapping(key="LALT"))
    assert transformer.transform_binding(behavior) == "sticky-lalt"

    behavior = StickyKeyBehavior(key=KeyMapping(key="RALT"))
    assert transformer.transform_binding(behavior) == "sticky-ralt"

    # Test all GUI/meta variants
    behavior = StickyKeyBehavior(key=KeyMapping(key="LGUI"))
    assert transformer.transform_binding(behavior) == "sticky-lmet"

    behavior = StickyKeyBehavior(key=KeyMapping(key="RGUI"))
    assert transformer.transform_binding(behavior) == "sticky-rmet"


def test_special_key_sticky_transformations(transformer):
    """Test sticky key transformations with special keys."""
    # Test function keys
    behavior = StickyKeyBehavior(key=KeyMapping(key="F1"))
    result = transformer.transform_binding(behavior)
    assert "sticky-f1" == result

    # Test navigation keys
    behavior = StickyKeyBehavior(key=KeyMapping(key="PG_UP"))
    result = transformer.transform_binding(behavior)
    assert "sticky-pg_up" == result

    # Test media keys
    behavior = StickyKeyBehavior(key=KeyMapping(key="C_MUTE"))
    result = transformer.transform_binding(behavior)
    assert "sticky-c_mute" == result


def test_layer_sticky_transformations(transformer):
    """Test sticky key transformations with layer switches."""
    # Test layer momentary switch
    behavior = StickyKeyBehavior(key=KeyMapping(key="mo 1"))
    result = transformer.transform_binding(behavior)
    assert result == "sticky-@layer1"

    # Test with transparent key
    behavior = StickyKeyBehavior(key=KeyMapping(key="trans"))
    result = transformer.transform_binding(behavior)
    assert result == "sticky-_"


def test_timing_parameter_transformations(transformer):
    """Test sticky key transformations with timing parameters."""
    # Test with custom timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=200
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft-200" == result

    # Test with default timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=None
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft" == result


def test_basic_key_sticky_transformations(transformer):
    """Test sticky key transformations with basic keys."""
    # Test letters
    behavior = StickyKeyBehavior(key=KeyMapping(key="A"))
    assert transformer.transform_binding(behavior) == "sticky-a"

    behavior = StickyKeyBehavior(key=KeyMapping(key="B"))
    assert transformer.transform_binding(behavior) == "sticky-b"

    # Test numbers
    behavior = StickyKeyBehavior(key=KeyMapping(key="N1"))
    assert transformer.transform_binding(behavior) == "sticky-1"

    behavior = StickyKeyBehavior(key=KeyMapping(key="N0"))
    assert transformer.transform_binding(behavior) == "sticky-0"

    # Test numpad
    behavior = StickyKeyBehavior(key=KeyMapping(key="KP_N7"))
    assert transformer.transform_binding(behavior) == "sticky-kp7"
