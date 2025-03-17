"""Edge case tests for the sticky key transformer module."""
import pytest
from converter.sticky_key_transformer import StickyKeyTransformer
from converter.model.keymap_model import StickyKeyBehavior, KeyMapping


@pytest.fixture
def transformer():
    """Create a StickyKeyTransformer instance."""
    return StickyKeyTransformer()


def test_empty_sticky_key_transformations(transformer):
    """Test sticky key transformations with empty values."""
    # Test with empty key
    behavior = StickyKeyBehavior(key=KeyMapping(key=""))
    assert transformer.transform_binding(behavior) == "sticky-_"

    # Test with None key
    behavior = StickyKeyBehavior(key=KeyMapping(key=None))
    assert transformer.transform_binding(behavior) == "sticky-_"

    # Test with whitespace key
    behavior = StickyKeyBehavior(key=KeyMapping(key="   "))
    assert transformer.transform_binding(behavior) == "sticky-_"


def test_invalid_timing_parameters(transformer):
    """Test sticky key transformations with invalid timing parameters."""
    # Test negative timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=-100
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft" == result

    # Test zero timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=0
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft" == result

    # Test extremely large timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=999999999
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft-999999999" == result


def test_special_character_sticky_keys(transformer):
    """Test sticky key transformations with special characters."""
    # Test Unicode characters
    behavior = StickyKeyBehavior(key=KeyMapping(key="é"))
    result = transformer.transform_binding(behavior)
    assert "sticky-unknown é" == result

    # Test escape sequences
    behavior = StickyKeyBehavior(key=KeyMapping(key="\n"))
    result = transformer.transform_binding(behavior)
    assert "sticky-unknown" in result

    # Test special symbols
    behavior = StickyKeyBehavior(key=KeyMapping(key="!@#"))
    result = transformer.transform_binding(behavior)
    assert "sticky-unknown !@#" == result


def test_mixed_case_transformations(transformer):
    """Test sticky key transformations with mixed case inputs."""
    # Test mixed case letters
    behavior = StickyKeyBehavior(key=KeyMapping(key="a"))
    assert transformer.transform_binding(behavior) == "sticky-a"

    behavior = StickyKeyBehavior(key=KeyMapping(key="B"))
    assert transformer.transform_binding(behavior) == "sticky-b"

    # Test mixed case modifiers
    behavior = StickyKeyBehavior(key=KeyMapping(key="LSHIFT"))
    assert transformer.transform_binding(behavior) == "sticky-lsft"

    behavior = StickyKeyBehavior(key=KeyMapping(key="lctrl"))
    assert transformer.transform_binding(behavior) == "sticky-lctl"

    # Test mixed case special keys
    behavior = StickyKeyBehavior(key=KeyMapping(key="PG_UP"))
    assert transformer.transform_binding(behavior) == "sticky-pg_up"

    behavior = StickyKeyBehavior(key=KeyMapping(key="pg_dn"))
    assert transformer.transform_binding(behavior) == "sticky-pg_dn"


def test_boundary_timing_values(transformer):
    """Test boundary values for timing parameters."""
    # Test minimum reasonable timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=1
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft-1" == result

    # Test maximum reasonable timeout
    behavior = StickyKeyBehavior(
        key=KeyMapping(key="LSHIFT"),
        timeout=10000
    )
    result = transformer.transform_binding(behavior)
    assert "sticky-lsft-10000" == result


def test_nested_sticky_behaviors(transformer):
    """Test nested sticky key behaviors (should be invalid)."""
    # Test nested sticky key
    nested = StickyKeyBehavior(key=KeyMapping(key="A"))
    behavior = StickyKeyBehavior(key=nested)
    result = transformer.transform_binding(behavior)
    assert "sticky-unknown" in result

    # Test double nested sticky key
    double_nested = StickyKeyBehavior(key=nested)
    result = transformer.transform_binding(double_nested)
    assert "sticky-unknown" in result


def test_invalid_key_combinations(transformer):
    """Test invalid key combinations for sticky keys."""
    # Test with invalid modifier names
    behavior = StickyKeyBehavior(key=KeyMapping(key="INVALID_MOD"))
    result = transformer.transform_binding(behavior)
    assert "sticky-unknown INVALID_MOD" == result

    # Test with invalid function key numbers
    behavior = StickyKeyBehavior(key=KeyMapping(key="F99"))
    result = transformer.transform_binding(behavior)
    assert "sticky-unknown F99" == result

    # Test with invalid layer numbers
    behavior = StickyKeyBehavior(key=KeyMapping(key="mo 999"))
    result = transformer.transform_binding(behavior)
    assert "sticky-@layer999" == result
