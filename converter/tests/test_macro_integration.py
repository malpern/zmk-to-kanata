"""End-to-end tests for macro support."""

import unittest
import os
import tempfile

from converter.zmk_to_kanata import convert_zmk_to_kanata


class TestMacroIntegration(unittest.TestCase):
    """End-to-end tests for macro support."""

    def test_macro_conversion(self):
        """Test converting a ZMK file with macros to Kanata format."""
        # Create a temporary ZMK file with a macro definition
        zmk_content = """
/ {
    macros {
        test_macro: test_macro {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <50>;
            tap-ms = <40>;
            bindings
                = <&macro_tap &kp A>
                , <&macro_wait_time 100>
                , <&macro_tap &kp B>
                , <&macro_press &kp LSHIFT>
                , <&kp C>
                , <&macro_release &kp LSHIFT>
                ;
        };
    };

    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &test_macro &kp B
            >;
        };
    };
};
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(zmk_content)
            temp_file_path = temp_file.name

        try:
            # Convert the ZMK file to Kanata format
            kanata_content = convert_zmk_to_kanata(temp_file_path)

            # Check that the macro definition is included in the output
            self.assertIn("(defmacro test_macro", kanata_content)
            self.assertIn("tap a", kanata_content)
            self.assertIn("delay 100", kanata_content)
            self.assertIn("tap b", kanata_content)
            self.assertIn("press lsft", kanata_content)
            self.assertIn("tap c", kanata_content)
            self.assertIn("release lsft", kanata_content)

            # Check that the macro is used in the keymap
            self.assertIn("(macro test_macro)", kanata_content)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main() 