"""Main Module

Provides the command-line interface for the ZMK to Kanata converter.
"""
from pathlib import Path
from .layer_parser import LayerParser
from .layer_transformer import LayerTransformer


def convert_keymap(input_file: Path, output_file: Path) -> None:
    """Convert a ZMK keymap file to Kanata format.
    
    Args:
        input_file: Path to the input ZMK keymap file
        output_file: Path where the Kanata config will be written
    """
    # Parse the ZMK file
    parser = LayerParser()
    zmk_content = input_file.read_text()
    keymap = parser.parse_zmk_file(zmk_content)
    
    # Transform to Kanata format
    transformer = LayerTransformer()
    kanata_layers = transformer.transform_layers(keymap)
    
    # Format the output
    kanata_config = []
    for layer in kanata_layers:
        kanata_config.append(f"(deflayer {layer.name}")
        for row in layer.bindings:
            kanata_config.append("  " + " ".join(row))
        kanata_config.append(")")
        kanata_config.append("")  # Empty line between layers
    
    # Write the output
    output_file.write_text("\n".join(kanata_config))

# Implementation will be added in subsequent tasks