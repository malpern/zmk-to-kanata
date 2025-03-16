"""Main Module

Provides the command-line interface for the ZMK to Kanata converter.
"""
from pathlib import Path
from .layer_parser import LayerParser
from .layer_transformer import LayerTransformer
from .model.keymap_model import GlobalSettings, KeymapConfig


def convert_keymap(input_file: Path, output_file: Path) -> None:
    """Convert a ZMK keymap file to Kanata format.
    
    Args:
        input_file: Path to the input ZMK keymap file
        output_file: Path where the Kanata config will be written
    """
    # Parse the ZMK file
    parser = LayerParser()
    zmk_content = input_file.read_text()
    keymap_content = parser.extract_keymap(zmk_content)
    if not keymap_content:
        raise ValueError("No valid keymap section found in ZMK file")
    
    layers = parser.extract_layers(keymap_content)
    
    # Create a KeymapConfig with default global settings
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=layers
    )
    
    # Transform to Kanata format
    transformer = LayerTransformer()
    kanata_layers = transformer.transform_layers(config.layers)
    
    # Format the output
    kanata_config = []
    
    # Add header comments
    kanata_config.extend([
        ";; ZMK to Kanata Configuration",
        ";; Generated automatically - DO NOT EDIT",
        "",
        ";; Global settings",
        f"(defvar tap-time {config.global_settings.tap_time})",
        f"(defvar hold-time {config.global_settings.hold_time})",
        ""
    ])
    
    # Add layers
    for i, layer in enumerate(kanata_layers):
        # Add layer definition
        kanata_config.append(f"(deflayer {layer.name}")
        # Add key rows with proper spacing
        for row in layer.keys:
            kanata_config.append("  " + " ".join(row))
        kanata_config.append(")")
        # Add empty line between layers, but not after the last one
        if i < len(kanata_layers) - 1:
            kanata_config.append("")
    
    # Ensure file ends with a newline
    kanata_config.append("")
    
    # Write the output
    output_file.write_text("\n".join(kanata_config))

# Implementation will be added in subsequent tasks