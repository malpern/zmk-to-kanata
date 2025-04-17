"""Tests for tap-hold keymap functionality."""

import unittest

from converter.layer_parser import LayerParser


class TestTapHoldKeymap(unittest.TestCase):
    """Test cases for tap-hold keymap functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = LayerParser()

    def test_parse_hold_tap_binding(self):
        """Test parsing a hold-tap binding."""
        zmk_content = """
        / {
            keymap {
                compatible = "zmk,keymap";
                default_layer {
                    bindings = <
                        &mt LSHIFT A &ht LCTRL B
                    >;
                };
            };
        };
        """
        layers = self.parser.parse_zmk_file(zmk_content)
        self.assertEqual(len(layers), 1)

        layer = layers[0]
        self.assertEqual(sum(len(row) for row in layer.keys), 2)

        # Check first binding (mt LSHIFT A)
        binding1 = [item for row in layer.keys for item in row][0]
        self.assertEqual(binding1.key, "A")
        self.assertIsNotNone(binding1.hold_tap)
        self.assertEqual(binding1.hold_tap.behavior_name, "mt")
        self.assertEqual(binding1.hold_tap.hold_key, "LSHIFT")
        self.assertEqual(binding1.hold_tap.tap_key, "A")

        # Check second binding (ht LCTRL B)
        binding2 = [item for row in layer.keys for item in row][1]
        self.assertEqual(binding2.key, "B")
        self.assertIsNotNone(binding2.hold_tap)
        self.assertEqual(binding2.hold_tap.behavior_name, "ht")
        self.assertEqual(binding2.hold_tap.hold_key, "LCTRL")
        self.assertEqual(binding2.hold_tap.tap_key, "B")


if __name__ == "__main__":
    unittest.main()
