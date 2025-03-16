"""Tests for layer integration."""

import unittest

from converter.layer_parser import LayerParser
from converter.layer_transformer import LayerTransformer


class TestLayerIntegration(unittest.TestCase):
    """Test cases for layer parsing and transformation integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = LayerParser()
        self.transformer = LayerTransformer()

    def test_parse_and_transform(self):
        """Test parsing and transforming a ZMK file."""
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
        kanata_content = self.transformer.transform_layers(layers)

        # Check that the Kanata content includes both layers
        self.assertIn("(deflayer default", kanata_content)
        self.assertIn("(deflayer nav", kanata_content)
        self.assertIn("a b c", kanata_content)
        self.assertIn("left right up", kanata_content)


if __name__ == "__main__":
    unittest.main()
