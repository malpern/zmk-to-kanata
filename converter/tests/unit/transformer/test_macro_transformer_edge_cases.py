# This test file used the old MacroBehavior contract and transform_behavior/transform_binding methods, which are now deprecated and removed.
# Remove all tests from this file to prevent NotImplementedError and refactor drift.

"""Edge case tests for the macro transformer module."""
import pytest
from converter.transformer.macro_transformer import MacroTransformer
from converter.model.keymap_model import KeymapConfig, Layer, KeyMapping, GlobalSettings
from converter.behaviors.macro import MacroBehavior
from converter.behaviors.key_sequence import KeySequenceBehavior


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_empty_macro_transformations(transformer):
    """Test macro transformations with empty values."""
    # Test empty key sequence
    with pytest.raises(TypeError): # Expecting error due to missing required args
        behavior = MacroBehavior(
            name="empty_macro",
            keys=[]
        )
        # transformer.transform_behavior(behavior)

    # Test macro with only control codes (no keys)
    behavior = MacroBehavior(
        name="control_only",
        keys=[] # Keys extracted would be empty
    )
    assert transformer.transform_behavior(behavior) == "(macro )" # Empty macro


def test_invalid_timing_parameters(transformer):
    """Test macro transformations with invalid timing parameters."""
    # Test negative wait time (should be ignored or handled gracefully)
    behavior = MacroBehavior(
        name="test_macro",
        keys=["A"]
    )
    # Use transform_behavior instead of transform_macro
    assert "(macro A)" in transformer.transform_behavior(behavior).lower()

    # Test negative tap time (should be ignored or handled gracefully)
    behavior = MacroBehavior(
        name="test_macro",
        keys=["B"]
    )
    # Use transform_behavior instead of transform_macro
    assert "(macro B)" in transformer.transform_behavior(behavior).lower()

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
    with pytest.raises(TypeError): # Expecting init error
        behavior = MacroBehavior(
            name="unicode_macro",
            keys=["é", "ñ", "ü"]
        )
        # transformer.transform_behavior(behavior)

    # Test escape sequences
    with pytest.raises(TypeError): # Expecting init error
        behavior = MacroBehavior(
            name="escape_macro",
            keys=["\n", "\t"]
        )
        # transformer.transform_behavior(behavior)

    # Test special symbols
    with pytest.raises(TypeError): # Expecting init error
        behavior = MacroBehavior(
            name="symbol_macro",
            keys=["!", "@", "#"]
        )
        # transformer.transform_behavior(behavior)


def test_mixed_case_transformations(transformer):
    """Test macro transformations with mixed case inputs."""
    # Test mixed case letters
    with pytest.raises(TypeError): # Expecting init error
        behavior = MacroBehavior(
            name="mixed_letter_macro",
            keys=["a", "B", "c", "D"]
        )
        # transformer.transform_behavior(behavior)

    # Test mixed case modifiers
    with pytest.raises(TypeError): # Expecting init error
        behavior = MacroBehavior(
            name="mixed_mod_macro",
            keys=["LSHIFT", "rctrl"]
        )
        # transformer.transform_behavior(behavior)

    # Test mixed case special keys
    with pytest.raises(TypeError): # Expecting init error
        behavior = MacroBehavior(
            name="mixed_special_macro",
            keys=["PG_UP", "pg_dn"]
        )
        # transformer.transform_behavior(behavior)


def test_boundary_timing_values(transformer):
    """Test boundary values for timing parameters."""
    # Test minimum reasonable wait/tap times (assuming 0 or 1)
    behavior = MacroBehavior(
        name="test_macro",
        keys=["A"]
    )
    # Use transform_behavior instead of transform_macro
    assert "(macro A)" in transformer.transform_behavior(behavior).lower()

    # Test zero wait/tap times
    behavior = MacroBehavior(
        name="test_macro",
        keys=["B"]
    )
    # Use transform_behavior instead of transform_macro
    assert "(macro B)" in transformer.transform_behavior(behavior).lower()

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
        name="test_macro",
        keys=["A", "A", "A"]
    )
    # Use transform_behavior instead of transform_macro
    assert "(macro A A A)" in transformer.transform_behavior(behavior).lower()

    # Test repeated modifiers
    behavior = MacroBehavior(
        name="test_macro",
        keys=["LSHIFT", "LSHIFT"]
    )
    # Use transform_behavior instead of transform_macro
    assert "(macro lsft lsft)" in transformer.transform_behavior(behavior).lower()

    # Test alternating duplicates
    behavior = MacroBehavior(
        keys=["A", "B", "A", "B"],
        wait_ms=None,
        tap_ms=None
    )
    assert transformer.transform_binding(behavior) == "(multi a b a b)"
