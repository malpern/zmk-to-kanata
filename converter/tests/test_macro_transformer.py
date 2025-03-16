"""Tests for the macro transformer module."""

import unittest

from converter.behaviors.macro import MacroBehavior
from converter.transformer.macro_transformer import MacroTransformer


class TestMacroTransformer(unittest.TestCase):
    """Test cases for the MacroTransformer class."""

    def setUp(self):
        """Set up the test case."""
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
                "&kp LSHIFT"
            ],
            binding_cells=[]
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

    def test_transform_behavior(self):
        """Test transforming a macro behavior using transform_behavior."""
        # Create a macro behavior with bindings that have to_kanata method
        class MockBinding:
            def __init__(self, kanata_str):
                self.kanata_str = kanata_str
                
            def to_kanata(self):
                return self.kanata_str
        
        macro = MacroBehavior(
            name="test_macro",
            wait_ms=50,
            tap_ms=50,
            bindings=[
                MockBinding("a"),
                MockBinding("b"),
                MockBinding("c")
            ],
            binding_cells=[]
        )

        # Transform the behavior
        result = self.transformer.transform_behavior(macro)

        # Verify the result
        expected = """(defsrc test_macro)
(deflayer test_macro
  a b c
)"""
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main() 