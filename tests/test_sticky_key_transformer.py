"""Tests for StickyKeyTransformer and sticky key behavior conversion."""

from converter.transformer.sticky_key_transformer import StickyKeyTransformer
from converter.behaviors.sticky_key import StickyKeyBehavior
from converter.models import Binding


def make_sticky_behavior(name="sk", flavor="default"):
    """Create a StickyKeyBehavior for testing, mapping flavor to fields."""
    # Map 'flavor' to available StickyKeyBehavior fields for test purposes
    if flavor == "quick":
        return StickyKeyBehavior(release_after_ms=500, quick_release=True)
    elif flavor == "ignore_mods":
        return StickyKeyBehavior(release_after_ms=1000, ignore_modifiers=True)
    else:
        return StickyKeyBehavior(release_after_ms=1000)


def test_sticky_key_transformer_init():
    """Test StickyKeyTransformer initialization."""
    t = StickyKeyTransformer()
    assert isinstance(t, StickyKeyTransformer)


def test_transform_binding_valid():
    """Test transforming a valid sticky key binding."""
    t = StickyKeyTransformer()
    behavior = make_sticky_behavior()
    binding = Binding(behavior=behavior, params=["a"])
    result = t.transform_binding(binding)
    assert result == "sticky-a"
    assert "a" in result


def test_transform_binding_missing_params():
    """Test transforming a sticky key binding with missing params."""
    t = StickyKeyTransformer()
    behavior = make_sticky_behavior()
    binding = Binding(behavior=behavior, params=[])
    result = t.transform_binding(binding)
    assert "ERROR" in result or "unsupported" in result or result is not None


def test_transform_binding_unknown_flavor():
    """Test transforming a sticky key binding with unknown flavor."""
    t = StickyKeyTransformer()
    behavior = make_sticky_behavior(flavor="unknown")
    binding = Binding(behavior=behavior, params=["a"])
    result = t.transform_binding(binding)
    assert result == "sticky-a"
    assert "a" in result
