"""Edge case tests for the holdtap transformer module."""
import pytest
from converter.holdtap_transformer import HoldTapTransformer
from converter.model.keymap_model import HoldTapBehavior, KeyMapping


@pytest.fixture
def transformer():
    """Create a HoldTapTransformer instance."""
    return HoldTapTransformer()


def test_empty_holdtap_transformations(transformer):
    """Test hold-tap transformations with empty values."""
    # Test with empty keys
    behavior = HoldTapBehavior(
        hold=KeyMapping(key=""),
        tap=KeyMapping(key="")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold _ _)"

    # Test with None values
    behavior = HoldTapBehavior(
        hold=KeyMapping(key=None),
        tap=KeyMapping(key=None)
    )
    assert transformer.transform_binding(behavior) == "(tap-hold _ _)"

    # Test with whitespace
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="   "),
        tap=KeyMapping(key="\t")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold _ _)"


def test_invalid_timing_parameters(transformer):
    """Test hold-tap transformations with invalid timing parameters."""
    # Test negative timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B"),
        timeout=-100
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold a b)" in result

    # Test zero timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B"),
        timeout=0
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold a b)" in result

    # Test very large timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B"),
        timeout=999999
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold-ms 999999 a b)" in result


def test_special_character_holdtap(transformer):
    """Test hold-tap with special characters."""
    # Test Unicode characters
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="é"),
        tap=KeyMapping(key="ñ")
    )
    result = transformer.transform_binding(behavior)
    assert "unknown é" in result
    assert "unknown ñ" in result

    # Test escape sequences
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="\n"),
        tap=KeyMapping(key="\r")
    )
    result = transformer.transform_binding(behavior)
    assert "unknown" in result

    # Test special symbols
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="!@#"),
        tap=KeyMapping(key="$%^")
    )
    result = transformer.transform_binding(behavior)
    assert "unknown !@#" in result
    assert "unknown $%^" in result


def test_mixed_case_transformations(transformer):
    """Test hold-tap with mixed case inputs."""
    # Test mixed case letters
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="a"),
        tap=KeyMapping(key="B")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold a b)"

    # Test mixed case modifiers
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="LSHIFT"),
        tap=KeyMapping(key="lctrl")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold lsft lctl)"

    # Test mixed case special keys
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="PG_UP"),
        tap=KeyMapping(key="pg_dn")
    )
    assert transformer.transform_binding(behavior) == "(tap-hold pg_up pg_dn)"


def test_nested_holdtap_behaviors(transformer):
    """Test nested hold-tap behaviors (should be invalid)."""
    # Test nested in hold position
    nested = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B")
    )
    behavior = HoldTapBehavior(
        hold=nested,
        tap=KeyMapping(key="C")
    )
    result = transformer.transform_binding(behavior)
    assert "unknown" in result

    # Test nested in tap position
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=nested
    )
    result = transformer.transform_binding(behavior)
    assert "unknown" in result


def test_boundary_timing_values(transformer):
    """Test boundary values for timing parameters."""
    # Test minimum valid timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B"),
        timeout=1
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold-ms 1 a b)" in result

    # Test maximum reasonable timeout
    behavior = HoldTapBehavior(
        hold=KeyMapping(key="A"),
        tap=KeyMapping(key="B"),
        timeout=10000
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold-ms 10000 a b)" in result
