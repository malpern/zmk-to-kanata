"""Tests for hold-tap behavior transformation."""

import unittest

from converter.models import KeymapConfig, Layer, Binding, HoldTap
from converter.model.keymap_model import HoldTapBinding
from converter.transformer.holdtap_transformer import HoldTapTransformer
from converter.transformer.kanata_transformer import KanataTransformer


class TestHoldTapTransformer(unittest.TestCase):
    """Test cases for the HoldTapTransformer class."""

    def setUp(self):
        """Set up the test case."""
        self.transformer = HoldTapTransformer()

    def test_transform_basic_hold_tap(self):
        """Test transforming a basic hold-tap behavior."""
        ht_behavior = HoldTap(
            name="ht_lctl_a", tapping_term_ms=200, flavor="tap-preferred"
        )
        # Assuming the transformer now takes the Behavior object
        # and generates the alias definition + name
        alias_def, alias_name = self.transformer.transform_behavior(
            ht_behavior, hold_param="LCTRL", tap_param="A"
        )

        expected_name = "ht_lctl_a"  # Or whatever naming convention is used
        expected_def = "(defalias ht_lctl_a (tap-hold 200 200 a lctl))"

        self.assertEqual(alias_name, expected_name)
        # Test both the full string and individual components
        self.assertEqual(alias_def, expected_def)
        self.assertIn("(tap-hold", alias_def)
        self.assertIn("200", alias_def)
        self.assertIn("a", alias_def)
        self.assertIn("lctl", alias_def)

    def test_transform_hold_tap_with_quick_tap(self):
        """Test hold-tap with quick_tap_ms."""
        ht_behavior = HoldTap(
            name="ht_ralt_b",
            tapping_term_ms=180,
            quick_tap_ms=100,
            flavor="balanced",
        )
        alias_def, alias_name = self.transformer.transform_behavior(
            ht_behavior, hold_param="RALT", tap_param="B"
        )

        expected_name = "ht_ralt_b"
        self.assertEqual(alias_name, expected_name)
        # Example assertion - adjust based on actual output format
        self.assertIn("(tap-hold 180 100 b ralt)", alias_def)

    def test_transform_layer_tap(self):
        """Test transforming a layer-tap behavior."""
        # Layer-tap might be handled differently, maybe needing layer index?
        # Assuming it's represented similarly for now
        lt_behavior = HoldTap(
            name="lt_1_spc", tapping_term_ms=200, flavor="tap-preferred"
        )
        # Assume hold_param is layer index/name, tap_param is the key
        alias_def, alias_name = self.transformer.transform_behavior(
            lt_behavior, hold_param="1", tap_param="SPC"
        )

        expected_name = "lt_1_spc"  # Example naming convention for layer-tap
        self.assertEqual(alias_name, expected_name)
        # Adjust assertion based on expected layer-tap Kanata syntax
        self.assertIn("(layer-tap", alias_def)
        self.assertIn("1", alias_def)
        self.assertIn("spc", alias_def)


def test_basic_holdtap_transformation():
    """Test transformation of a basic hold-tap binding."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="lh_hm",
        hold_key="LGUI",
        tap_key="A",
        hold_trigger_key_positions=None,
        hold_trigger_on_release=False,
        retro_tap=False,
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold 200 250 a lmet)"


def test_holdtap_with_release():
    """Test hold-tap binding with hold-trigger-on-release."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="rh_hm",
        hold_key="RSHIFT",
        tap_key="J",
        hold_trigger_key_positions=None,
        hold_trigger_on_release=True,
        retro_tap=False,
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold-release 200 250 j rsft)"


def test_holdtap_with_key_positions():
    """Test hold-tap binding with hold-trigger-key-positions."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="lh_hm",
        hold_key="LCTRL",
        tap_key="D",
        hold_trigger_key_positions=(1, 2, 3),
        hold_trigger_on_release=False,
        retro_tap=False,
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold-release-keys 200 250 d lctl (1 2 3))"


def test_holdtap_with_retro_tap():
    """Test transformation of a hold-tap binding with retro-tap."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="rh_hm",
        hold_key="RALT",
        tap_key="L",
        hold_trigger_key_positions=None,
        hold_trigger_on_release=False,
        retro_tap=True,
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold-press-timeout 200 250 l ralt l)"


def test_full_keymap_transformation():
    """Test the integration of KanataTransformer with HoldTapTransformer.

    Verifies that a complete keymap configuration with hold-tap behaviors
    is correctly transformed into Kanata format, including:
    - Behavior alias definitions
    - Layer definitions with bindings
    - Proper integration of both transformers
    """
    # Define behaviors using the new models
    ht_behavior_e = HoldTap(
        name="ht_lalt_e",
        tapping_term_ms=200,
        flavor="tap-preferred",
    )
    ht_behavior_a = HoldTap(
        name="ht_lgui_a",
        tapping_term_ms=200,
        flavor="hold-preferred",
    )
    ht_behavior_s = HoldTap(
        name="ht_lctl_s",
        tapping_term_ms=180,
        flavor="balanced",
    )

    behaviors_dict = {
        "ht_lalt_e": ht_behavior_e,
        "ht_lgui_a": ht_behavior_a,
        "ht_lctl_s": ht_behavior_s,
    }

    # Define layer using new Binding model
    layer0 = Layer(
        name="default",
        index=0,
        bindings=[
            Binding(behavior=None, params=["Q"]),
            Binding(behavior=None, params=["W"]),
            Binding(behavior=ht_behavior_e, params=["LALT", "E"]),
            Binding(behavior=ht_behavior_a, params=["LGUI", "A"]),
            Binding(behavior=ht_behavior_s, params=["LCTRL", "S"]),
            Binding(behavior=None, params=["D"]),
        ],
    )

    config = KeymapConfig(layers=[layer0], behaviors=behaviors_dict)
    transformer = KanataTransformer()
    result = transformer.transform(config)

    # Verify expected aliases are defined
    assert "(defalias ht_lalt_e" in result
    assert "(defalias ht_lgui_a" in result
    assert "(defalias ht_lctl_s" in result

    # Verify layer definition and bindings
    assert "(deflayer default" in result
    expected_bindings = "q w @ht_lalt_e @ht_lgui_a @ht_lctl_s d"
    assert expected_bindings in result
