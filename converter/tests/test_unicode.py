"""Tests for the Unicode binding and parser."""

import unittest

from converter.behaviors.unicode import UnicodeBinding, is_unicode_binding
from converter.parser.unicode_parser import UnicodeParser


class TestUnicodeBinding(unittest.TestCase):
    """Test cases for the UnicodeBinding class."""

    def test_to_kanata(self):
        """Test converting a Unicode binding to Kanata format."""
        binding = UnicodeBinding("π")
        self.assertEqual(binding.to_kanata(), "(unicode π)")

    def test_from_zmk(self):
        """Test creating a UnicodeBinding from a ZMK binding string."""
        # Test with a known Unicode binding
        binding = UnicodeBinding.from_zmk("&pi")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.character, "π")

        # Test with another known Unicode binding
        binding = UnicodeBinding.from_zmk("&n_tilde")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.character, "ñ")

        # Test with an unknown Unicode binding
        binding = UnicodeBinding.from_zmk("&unicode_unknown")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.character, "?")

        # Test with a non-Unicode binding
        binding = UnicodeBinding.from_zmk("&kp A")
        self.assertIsNone(binding)

    def test_is_unicode_binding(self):
        """Test checking if a binding string is a Unicode binding."""
        self.assertTrue(is_unicode_binding("&unicode_pi"))
        self.assertTrue(is_unicode_binding("&pi"))
        self.assertTrue(is_unicode_binding("&n_tilde"))
        self.assertFalse(is_unicode_binding("&kp A"))
        self.assertFalse(is_unicode_binding("&mt LSHIFT A"))


class TestUnicodeParser(unittest.TestCase):
    """Test cases for the UnicodeParser class."""

    def setUp(self):
        """Set up the test case."""
        self.parser = UnicodeParser()

    def test_parse_unicode_mappings(self):
        """Test parsing Unicode mappings from ZMK content."""
        content = """
        ZMK_UNICODE_SINGLE(pi, N0, N3, C, N0)
        ZMK_UNICODE_PAIR(n_tilde, N0, N0, F, N1, N0, N0, D, N1)
        """
        self.parser.parse_unicode_mappings(content)
        
        # Check that the mappings were parsed correctly
        self.assertEqual(self.parser.unicode_mappings["&pi"], "π")
        self.assertEqual(self.parser.unicode_mappings["&n_tilde"], "ñ")

    def test_parse_binding(self):
        """Test parsing a Unicode binding string."""
        # Set up some mappings
        self.parser.unicode_mappings["&pi"] = "π"
        self.parser.unicode_mappings["&n_tilde"] = "ñ"
        
        # Test with a known Unicode binding
        binding = self.parser.parse_binding("&pi")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.character, "π")
        
        # Test with another known Unicode binding
        binding = self.parser.parse_binding("&n_tilde")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.character, "ñ")
        
        # Test with an unknown Unicode binding
        binding = self.parser.parse_binding("&unicode_unknown")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.character, "?")
        
        # Test with a non-Unicode binding
        binding = self.parser.parse_binding("&kp A")
        self.assertIsNone(binding)


if __name__ == "__main__":
    unittest.main() 