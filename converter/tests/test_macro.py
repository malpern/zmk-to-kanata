"""Tests for the macro behavior implementation."""

import unittest

from converter.behaviors.macro import (
    MacroBehavior,
    MacroBinding,
    is_macro_binding,
)
from converter.parser.macro_parser import MacroParser


class TestMacroBehavior(unittest.TestCase):
    """Test cases for the MacroBehavior class."""

    def test_macro_behavior_defaults(self):
        """Test that MacroBehavior has correct default values."""
        behavior = MacroBehavior(name="test_macro")
        self.assertEqual(behavior.name, "test_macro")
        self.assertEqual(behavior.wait_ms, 15)
        self.assertEqual(behavior.tap_ms, 30)
        self.assertEqual(behavior.bindings, [])
        self.assertEqual(behavior.binding_cells, 0)

    def test_macro_behavior_custom_values(self):
        """Test that MacroBehavior accepts custom values."""
        behavior = MacroBehavior(
            name="custom_macro", wait_ms=20, tap_ms=40, binding_cells=1
        )
        self.assertEqual(behavior.name, "custom_macro")
        self.assertEqual(behavior.wait_ms, 20)
        self.assertEqual(behavior.tap_ms, 40)
        self.assertEqual(behavior.binding_cells, 1)


class TestMacroBinding(unittest.TestCase):
    """Test cases for the MacroBinding class."""

    def setUp(self):
        """Set up test fixtures."""
        self.behavior = MacroBehavior(name="test_macro")
        self.behaviors = {"test_macro": self.behavior}

    def test_macro_binding_creation(self):
        """Test creating a MacroBinding."""
        binding = MacroBinding(behavior=self.behavior)
        self.assertEqual(binding.behavior, self.behavior)
        self.assertIsNone(binding.param)

    def test_macro_binding_to_kanata(self):
        """Test converting a MacroBinding to Kanata format."""
        binding = MacroBinding(behavior=self.behavior)
        self.assertEqual(binding.to_kanata(), "(macro test_macro)")

    def test_macro_binding_from_zmk(self):
        """Test creating a MacroBinding from a ZMK binding string."""
        binding = MacroBinding.from_zmk("&test_macro", self.behaviors)
        self.assertEqual(binding.behavior, self.behavior)
        self.assertIsNone(binding.param)

    def test_macro_binding_from_zmk_with_param(self):
        """Test creating a MacroBinding with a parameter."""
        behavior = MacroBehavior(name="param_macro", binding_cells=1)
        behaviors = {"param_macro": behavior}
        binding = MacroBinding.from_zmk("&param_macro 1", behaviors)
        self.assertEqual(binding.behavior, behavior)
        self.assertEqual(binding.param, 1)

    def test_macro_binding_from_zmk_unknown_behavior(self):
        """Test error when behavior is unknown."""
        with self.assertRaises(ValueError):
            MacroBinding.from_zmk("&unknown_macro", self.behaviors)


class TestIsMacroBinding(unittest.TestCase):
    """Test cases for the is_macro_binding function."""

    def test_is_macro_binding_true(self):
        """Test that is_macro_binding returns True for macro bindings."""
        self.assertTrue(is_macro_binding("&test_macro"))
        self.assertTrue(is_macro_binding("&custom_macro 1"))

    def test_is_macro_binding_false(self):
        """Test that is_macro_binding returns False for non-macro bindings."""
        self.assertFalse(is_macro_binding("&kp A"))
        self.assertFalse(is_macro_binding("&mo 1"))
        self.assertFalse(is_macro_binding("&lt 1 A"))
        self.assertFalse(is_macro_binding("&to 2"))
        self.assertFalse(is_macro_binding("&sk LSHIFT"))
        self.assertFalse(is_macro_binding("&key_sequence test"))


class TestMacroParser(unittest.TestCase):
    """Test cases for the MacroParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = MacroParser()

    def test_parse_behavior(self):
        """Test parsing a macro behavior configuration."""
        config = {
            "compatible": "zmk,behavior-macro",
            "wait-ms": "20",
            "tap-ms": "40",
        }
        behavior = self.parser.parse_behavior("test_macro", config)
        self.assertEqual(behavior.name, "test_macro")
        self.assertEqual(behavior.wait_ms, 20)
        self.assertEqual(behavior.tap_ms, 40)
        self.assertEqual(behavior.binding_cells, 0)

    def test_parse_behavior_one_param(self):
        """Test parsing a one-param macro behavior."""
        config = {
            "compatible": "zmk,behavior-macro-one-param",
            "wait-ms": "20",
            "tap-ms": "40",
        }
        behavior = self.parser.parse_behavior("param_macro", config)
        self.assertEqual(behavior.binding_cells, 1)

    def test_parse_behavior_two_param(self):
        """Test parsing a two-param macro behavior."""
        config = {
            "compatible": "zmk,behavior-macro-two-param",
            "wait-ms": "20",
            "tap-ms": "40",
        }
        behavior = self.parser.parse_behavior("two_param_macro", config)
        self.assertEqual(behavior.binding_cells, 2)

    def test_parse_behavior_not_macro(self):
        """Test parsing a non-macro behavior."""
        config = {"compatible": "zmk,behavior-other"}
        behavior = self.parser.parse_behavior("not_macro", config)
        self.assertIsNone(behavior)

    def test_parse_bindings(self):
        """Test parsing macro bindings."""
        behavior = MacroBehavior(name="test_macro")
        bindings_str = (
            "<&macro_tap &kp A, &macro_press &kp LSHIFT, "
            "&kp B, &macro_release &kp LSHIFT>"
        )
        self.parser.parse_bindings(behavior, bindings_str)

        # Check that bindings were parsed correctly
        self.assertIn("&kp A", behavior.bindings)
        self.assertIn("&kp LSHIFT", behavior.bindings)
        self.assertIn("&kp B", behavior.bindings)

    def test_extract_behaviors_after_control(self):
        """Test extracting behaviors after a control command."""
        behaviors = self.parser._extract_behaviors_after_control(
            "&macro_tap &kp A &kp B", "&macro_tap"
        )
        # The parser splits by whitespace and then joins them back
        self.assertEqual(behaviors, ["&kp A", "&kp B"])

    def test_parse_binding(self):
        """Test parsing a macro binding string."""
        behavior = MacroBehavior(name="test_macro")
        self.parser.behaviors = {"test_macro": behavior}
        binding = self.parser.parse_binding("&test_macro")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.behavior, behavior)

    def test_parse_binding_not_macro(self):
        """Test parsing a non-macro binding string."""
        binding = self.parser.parse_binding("&kp A")
        self.assertIsNone(binding)


if __name__ == "__main__":
    unittest.main()
