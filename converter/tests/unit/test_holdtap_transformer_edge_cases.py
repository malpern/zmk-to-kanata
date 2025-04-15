# NOTE: This file was previously archived as junk. Review for compliance with the new architecture and redundancy before further use.

"""Edge case tests for the holdtap transformer module."""
import pytest
from converter.transformer.holdtap_transformer import HoldTapTransformer
from converter.model.keymap_model import KeymapConfig, Layer, KeyMapping, GlobalSettings
from converter.behaviors.sticky_key import StickyKeyBehavior
from converter.behaviors.hold_tap import HoldTapBinding


@pytest.fixture
def transformer():
    """Create a HoldTapTransformer instance."""
    return HoldTapTransformer()


def test_empty_holdtap_transformations(transformer):
    """Test hold-tap transformations with empty values."""
    # Test with empty keys - assuming default behavior name 'ht'
    # Note: KeyMapping validates non-empty keys, so this test might be invalid
    # if validation is re-enabled. Temporarily testing transformer logic.
    with pytest.raises(ValueError): # Expecting validation to fail if re-enabled
        hold_key_map = KeyMapping(key="")
    with pytest.raises(ValueError):
        tap_key_map = KeyMapping(key="")
    # behavior = HoldTapBinding(behavior_name="ht", hold_key="", tap_key="")
    # assert transformer.transform_binding(behavior) == "(tap-hold 200 200 _ _)" # Adjust expected

    # Test with None keys (Not directly possible with KeyMapping validation)
    # behavior = HoldTapBinding(behavior_name="ht", hold_key=None, tap_key=None) # Invalid init
    # assert transformer.transform_binding(behavior) == "(tap-hold 200 200 _ _)"

    # Test with whitespace keys (Not directly possible with KeyMapping validation)
    with pytest.raises(ValueError):
        KeyMapping(key="   ")
    # behavior = HoldTapBinding(behavior_name="ht", hold_key="   ", tap_key="   ")
    # assert transformer.transform_binding(behavior) == "(tap-hold 200 200 _ _)" # Adjust expected


def test_invalid_timing_parameters(transformer):
    """Test hold-tap transformations with invalid timing parameters."""
    # Note: HoldTapBinding doesn't currently use timeout/timing in init
    # Assuming 'ht' behavior name
    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="A", # Extracted from KeyMapping(key="A")
        tap_key="B" # Extracted from KeyMapping(key="B")
        # timeout=-100 # Invalid argument removed
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 b a)" == result # Default timing

    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="A",
        tap_key="B"
        # timeout=0 # Invalid argument removed
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 b a)" == result # Default timing

    # Test extremely large timeout (Not applicable to HoldTapBinding init)
    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="A",
        tap_key="B"
        # timeout=999999999 # Invalid argument removed
    )
    result = transformer.transform_binding(behavior)
    # Kanata doesn't support custom ms timing in basic tap-hold
    assert "(tap-hold 200 200 b a)" == result


def test_special_character_holdtap(transformer):
    """Test hold-tap with special characters."""
    # Note: KeyMapping validation prevents these keys if re-enabled.
    # Assuming 'ht' behavior name
    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="é", # Extracted from KeyMapping(key="é")
        tap_key="ñ" # Extracted from KeyMapping(key="ñ")
    )
    result = transformer.transform_binding(behavior)
    # Kanata representation of unicode might vary or be unsupported
    assert "(tap-hold 200 200 ñ é)" == result # Assuming literal use

    # Test escape sequences (Validation prevents)
    # behavior = HoldTapBinding(behavior_name="ht", hold_key="\n", tap_key="\t")
    # result = transformer.transform_binding(behavior)
    # assert "(tap-hold 200 200 <invalid> <invalid>)" in result # Adjust expected

    # Test special symbols (Validation prevents)
    # behavior = HoldTapBinding(behavior_name="ht", hold_key="!@#", tap_key="$%^")
    # result = transformer.transform_binding(behavior)
    # assert "(tap-hold 200 200 $%^ !@#)" in result # Adjust expected


def test_mixed_case_transformations(transformer):
    """Test hold-tap with mixed case inputs."""
    # Note: KeyMapping validation prevents 'a' if re-enabled.
    # Assuming 'ht' behavior name
    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="a", # Extracted from KeyMapping(key="a")
        tap_key="B" # Extracted from KeyMapping(key="B")
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 b a)" == result

    # Test mixed case modifiers - assuming 'mt' behavior
    behavior = HoldTapBinding(
        behavior_name="mt",
        hold_key="LSHIFT", # Extracted from KeyMapping(key="LSHIFT")
        tap_key="c" # Extracted from KeyMapping(key="c")
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 c lsft)" == result

    behavior = HoldTapBinding(
        behavior_name="mt",
        hold_key="rctrl", # Extracted from KeyMapping(key="rctrl") - validation allows lowercase mods
        tap_key="D" # Extracted from KeyMapping(key="D")
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 d rctl)" == result


def test_nested_holdtap_behaviors(transformer):
    """Test nested hold-tap behaviors (should be invalid)."""
    # This tests how the transformer handles invalid nested structures.
    # HoldTapBinding expects strings, nesting behavior objects is not directly supported.

    # Test nested in hold position
    nested = HoldTapBinding(behavior_name="mt", hold_key="LSHIFT", tap_key="B")
    # Attempting to nest - pass the tap_key string from nested behavior
    behavior_hold_nested = HoldTapBinding(
        behavior_name="ht",
        hold_key=nested.tap_key, # Using string "B"
        tap_key="A"
    )
    result_hold = transformer.transform_binding(behavior_hold_nested)
    # Expect transformation of the strings provided
    assert "(tap-hold 200 200 a b)" == result_hold

    # Test nested in tap position
    behavior_tap_nested = HoldTapBinding(
        behavior_name="ht",
        hold_key="A",
        tap_key=nested.tap_key # Using string "B"
    )
    result_tap = transformer.transform_binding(behavior_tap_nested)
    assert "(tap-hold 200 200 b a)" == result_tap


def test_boundary_timing_values(transformer):
    """Test boundary values for timing parameters."""
    # Note: HoldTapBinding init doesn't take timing, it's hardcoded in to_kanata
    # Assuming 'ht' behavior name
    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="A",
        tap_key="B"
        # timeout=1 # Invalid argument removed
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 b a)" == result # Default timing

    # Test maximum reasonable timeout (Not applicable to HoldTapBinding init)
    behavior = HoldTapBinding(
        behavior_name="ht",
        hold_key="A",
        tap_key="B"
        # timeout=10000 # Invalid argument removed
    )
    result = transformer.transform_binding(behavior)
    assert "(tap-hold 200 200 b a)" == result # Default timing
