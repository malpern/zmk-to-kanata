"""End-to-end tests for Unicode support."""

import unittest
import os
import tempfile

from converter.zmk_to_kanata import convert_zmk_to_kanata


class TestUnicodeIntegration(unittest.TestCase):
    """End-to-end tests for Unicode support."""

    def test_unicode_conversion(self):
        """Test converting a ZMK file with Unicode to Kanata format."""
        # Create a temporary ZMK file with Unicode definitions
        zmk_content = """
/ {
    macros {
        // Define a macro for the pi symbol
        ZMK_UNICODE_SINGLE(pi, N0, N3, C, N0)
        
        // Define a macro for the n with tilde
        ZMK_UNICODE_PAIR(n_tilde, N0, N0, F, N1, N0, N0, D, N1)
    };

    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &pi &n_tilde &kp A
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

            # Check that the Unicode characters are included in the output
            self.assertIn("(unicode π)", kanata_content)
            self.assertIn("(unicode ñ)", kanata_content)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main() 