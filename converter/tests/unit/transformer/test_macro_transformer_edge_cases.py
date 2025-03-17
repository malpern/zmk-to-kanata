"""Edge case tests for the macro transformer module."""
import pytest
from converter.macro_transformer import MacroTransformer
from converter.model.keymap_model import MacroBehavior


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_empty_macro_transformations(transformer):
    """Test macro transformations with empty values."""
    # Test empty key sequence
    behavior = MacroBehavior(
        keys=[],
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi)"

    # Test None keys
    behavior = MacroBehavior(
        keys=None,
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi)"

    # Test sequence with empty strings
    behavior = MacroBehavior(
        keys=["", "", ""],
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi _ _ _)"


def test_invalid_timing_parameters(transformer):
    """Test macro transformations with invalid timing parameters."""
    # Test negative wait time
    behavior = MacroBehavior(
        keys=["A", "B"],
        wait_ms=-100,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert "(multi a b)" == result

    # Test negative tap time
    behavior = MacroBehavior(
        keys=["A", "B"],
        wait_ms=None,
        tap_ms=-50
    )
    result = transformer.transform_binding(behavior)
    assert "(multi a b)" == result

    # Test zero timing values
    behavior = MacroBehavior(
        keys=["A", "B"],
        wait_ms=0,
        tap_ms=0
    )
    result = transformer.transform_binding(behavior)
    assert "(multi a b)" == result

    # Test extremely large values
    behavior = MacroBehavior(
        keys=["A", "B"],
        wait_ms=999999999,
        tap_ms=999999999
    )
    result = transformer.transform_binding(behavior)
    assert "(multi" in result
    assert "(tap-hold-ms 999999999" in result
    assert "(delay 999999999)" in result


def test_special_character_macros(transformer):
    """Test macro transformations with special characters."""
    # Test Unicode characters
    behavior = MacroBehavior(
        keys=["é", "ñ", "ü"],
        wait_ms=None,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert "unknown é" in result
    assert "unknown ñ" in result
    assert "unknown ü" in result

    # Test escape sequences
    behavior = MacroBehavior(
        keys=["\n", "\t", "\r"],
        wait_ms=None,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert "unknown" in result

    # Test special symbols
    behavior = MacroBehavior(
        keys=["!@#", "$%^", "&*()"],
        wait_ms=None,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert "unknown !@#" in result
    assert "unknown $%^" in result
    assert "unknown &*()" in result


def test_mixed_case_transformations(transformer):
    """Test macro transformations with mixed case inputs."""
    # Test mixed case letters
    behavior = MacroBehavior(
        keys=["a", "B", "c", "D"],
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi a b c d)"

    # Test mixed case modifiers
    behavior = MacroBehavior(
        keys=["LSHIFT", "lctrl", "RALT", "rgui"],
        wait_ms=None,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert result == "(multi lsft lctl ralt rgui)"

    # Test mixed case special keys
    behavior = MacroBehavior(
        keys=["PG_UP", "pg_dn", "HOME", "end"],
        wait_ms=None,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert result == "(multi pg_up pg_dn home end)"


def test_boundary_timing_values(transformer):
    """Test boundary values for timing parameters."""
    # Test minimum reasonable values
    behavior = MacroBehavior(
        keys=["A", "B"],
        wait_ms=1,
        tap_ms=1
    )
    result = transformer.transform_binding(behavior)
    assert "(multi" in result
    assert "(tap-hold-ms 1 a)" in result
    assert "(delay 1)" in result
    assert "(tap-hold-ms 1 b)" in result

    # Test maximum reasonable values
    behavior = MacroBehavior(
        keys=["A", "B"],
        wait_ms=10000,
        tap_ms=10000
    )
    result = transformer.transform_binding(behavior)
    assert "(multi" in result
    assert "(tap-hold-ms 10000 a)" in result
    assert "(delay 10000)" in result
    assert "(tap-hold-ms 10000 b)" in result


def test_duplicate_keys(transformer):
    """Test macro transformations with duplicate keys."""
    # Test repeated letters
    behavior = MacroBehavior(
        keys=["A", "A", "A"],
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi a a a)"

    # Test repeated modifiers
    behavior = MacroBehavior(
        keys=["LSHIFT", "LSHIFT", "A", "LSHIFT"],
        wait_ms=None,
        tap_ms=None
    )
    result = transformer.transform_binding(behavior)
    assert result == "(multi lsft lsft a lsft)"

    # Test alternating duplicates
    behavior = MacroBehavior(
        keys=["A", "B", "A", "B"],
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi a b a b)"
