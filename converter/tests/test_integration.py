"""Integration Tests

End-to-end tests for the ZMK to Kanata converter.
"""

import tempfile
from pathlib import Path

from converter.output.file_writer import KanataFileWriter
from converter.parser.zmk_parser import ZMKParser
from converter.transformer.kanata_transformer import KanataTransformer


def test_basic_conversion():
    """Test end-to-end conversion of a basic ZMK file to Kanata format."""
    # Get the path to the samples directory
    samples_dir = Path(__file__).parent.parent / "samples"
    input_file = samples_dir / "sample.zmk"

    # Parse the ZMK file
    parser = ZMKParser()
    config = parser.parse(input_file)

    # Transform to Kanata format
    transformer = KanataTransformer()
    kanata_config = transformer.transform(config)

    # Write to a temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".kbd", delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        # Write the configuration
        writer = KanataFileWriter()
        writer.write(kanata_config, temp_path)

        # Read back and verify the content
        with open(temp_path, "r") as f:
            written_content = f.read()

        # Verify the expected content
        expected_lines = [
            ";; ZMK to Kanata Configuration",
            ";; Generated automatically - DO NOT EDIT",
            "",
            ";; Global settings",
            "(defvar tap-time 200)",
            "(defvar hold-time 300)",
            "",
            "(deflayer default",
            "  a  b  c  d",
            "  e  f  g  h",
            "  i  j  k  l",
            ")",
        ]
        assert written_content.splitlines() == expected_lines

    finally:
        # Clean up
        temp_path.unlink()
