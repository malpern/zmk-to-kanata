"""Tests for the layer parser module."""

import unittest

from converter.layer_parser import LayerParser


class TestLayerParser(unittest.TestCase):
    """Test cases for the LayerParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = LayerParser()

    def test_extract_layers(self):
        """Test extracting layers from keymap content."""
        keymap_content = """
        default_layer {
            bindings = <
                &kp A &kp B &kp C
                &kp D &kp E &kp F
            >;
        };
        """
        layers = self.parser.extract_layers(keymap_content)
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0].name, "default")
        self.assertEqual(sum(len(row) for row in layers[0].keys), 6)

    def test_parse_zmk_file(self):
        """Test parsing a complete ZMK file."""
        zmk_content = """
        / {
            keymap {
                compatible = "zmk,keymap";
                default_layer {
                    bindings = <
                        &kp A &kp B &kp C
                        &kp D &kp E &kp F
                    >;
                };
                nav_layer {
                    bindings = <
                        &kp LEFT &kp RIGHT &kp UP
                        &kp DOWN &kp HOME &kp END
                    >;
                };
            };
        };
        """
        layers = self.parser.parse_zmk_file(zmk_content)
        self.assertEqual(len(layers), 2)
        self.assertEqual(layers[0].name, "default")
        self.assertEqual(layers[1].name, "nav")


if __name__ == "__main__":
    unittest.main()
