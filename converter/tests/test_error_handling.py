"""Tests for error handling in DTS parsing and processing."""

import unittest

from converter.dts.parser import DtsParser, ParserError
from converter.dts.ast import DtsNode, DtsRoot, DtsProperty
from converter.dts.extractor import DtsExtractor, ExtractionError
from converter.dts.preprocessor import DtsPreprocessor


class TestDtsErrorHandling(unittest.TestCase):
    """Test cases for DTS error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = DtsParser()
        self.extractor = DtsExtractor()
        self.preprocessor = DtsPreprocessor()

    def test_unterminated_string(self):
        """Test error handling for unterminated strings."""
        dts_content = """
            test {
                compatible = "test;
            };
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Unterminated string", str(cm.exception))

    def test_invalid_property_value(self):
        """Test error handling for invalid property values."""
        dts_content = """
            test {
                compatible = @invalid;
            };
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Invalid property value", str(cm.exception))

    def test_missing_closing_brace(self):
        """Test error handling for missing closing braces."""
        dts_content = """
            test {
                compatible = "test";
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Expected closing brace", str(cm.exception))

    def test_invalid_array_format(self):
        """Test error handling for invalid array formats."""
        dts_content = """
            test {
                array = <1 2 3;
            };
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Invalid array format", str(cm.exception))

    def test_invalid_hex_value(self):
        """Test error handling for invalid hexadecimal values."""
        dts_content = """
            test {
                value = <0xZZ>;
            };
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Invalid hexadecimal value", str(cm.exception))

    def test_duplicate_label(self):
        """Test error handling for duplicate node labels."""
        root = DtsNode(name="/")
        node1 = DtsNode(name="test1")
        node2 = DtsNode(name="test2")
        root.add_child(node1)
        root.add_child(node2)
        node1.add_label("duplicate")
        node2.add_label("duplicate")

        with self.assertRaises(ValueError) as cm:
            DtsRoot(root)
        self.assertIn("Duplicate label", str(cm.exception))

    def test_invalid_reference(self):
        """Test error handling for invalid node references."""
        root = DtsNode(name="/")
        dts_root = DtsRoot(root)
        result = dts_root.resolve_reference("&nonexistent")
        self.assertIsNone(result)

    def test_missing_semicolon(self):
        """Test error handling for missing semicolons."""
        dts_content = """
            test {
                compatible = "test"
            };
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Expected semicolon", str(cm.exception))

    def test_unexpected_token(self):
        """Test error handling for unexpected tokens."""
        dts_content = """
            test {
                compatible = "test"; }};
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Unexpected token", str(cm.exception))

    def test_nested_array_error(self):
        """Test error handling for invalid nested arrays."""
        dts_content = """
            test {
                array = <1 <2> 3>;
            };
        """
        with self.assertRaises(ParserError) as cm:
            self.parser.parse(dts_content)
        self.assertIn("Invalid array format", str(cm.exception))

    def test_validation_error(self):
        """Test error handling for validation errors."""
        root = DtsNode(name="/")
        node = DtsNode(name="test")
        root.add_child(node)
        node.add_property(DtsProperty(name="compatible", value=123, type="string"))

        with self.assertRaises(ValueError) as cm:
            self.extractor.validate_node(node)
        self.assertIn("Invalid property type", str(cm.exception))

    def test_extraction_error(self):
        """Test error handling for extraction errors."""
        root = DtsNode(name="/")
        node = DtsNode(name="test")
        root.add_child(node)
        node.add_property(
            DtsProperty(name="compatible", value="zmk,keymap", type="string")
        )

        with self.assertRaises(ExtractionError) as cm:
            self.extractor.extract_keymap(DtsRoot(root))
        self.assertIn("Missing required properties", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
