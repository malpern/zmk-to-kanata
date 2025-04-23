"""Tests for the macro transformer module."""

import unittest

from converter.behaviors.macro import MacroBehavior
from converter.transformer.macro_transformer import MacroTransformer


class TestMacroTransformer(unittest.TestCase):
    """Test suite for the MacroTransformer class."""

    def setUp(self):
        """Set up the test environment."""
        self.transformer = MacroTransformer()

    def test_transform_macro(self):
        """Test transforming a macro behavior to Kanata format."""
        # Create a simple macro behavior
        macro = MacroBehavior(
            name="test_macro",
            wait_ms=50,
            tap_ms=50,
            bindings=[
                "&macro_tap",
                "&kp A",
                "&macro_wait_time 100",
                "&kp B",
                "&macro_press",
                "&kp LSHIFT",
                "&kp C",
                "&macro_release",
                "&kp LSHIFT",
            ],
            binding_cells=[],
        )

        # Transform the macro
        result = self.transformer.transform_macro(macro)

        # Verify the result
        expected = """(defmacro test_macro
  tap a
  delay 100
  tap b
  press lsft
  tap c
  release lsft
)"""
        self.assertEqual(result, expected)

    def test_convert_key(self):
        """Test the internal _convert_key method."""
        # Test basic keys
        self.assertEqual(self.transformer._convert_key("A"), "a")
        self.assertEqual(self.transformer._convert_key("N1"), "1")
        self.assertEqual(self.transformer._convert_key("LSHIFT"), "lsft")
        # Test unknown key (should be lowercased)
        self.assertEqual(self.transformer._convert_key("UNKNOWN_KEY"), "unknown_key")


if __name__ == "__main__":
    unittest.main()
