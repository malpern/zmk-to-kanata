"""Module for converting ZMK keymap files to Kanata format."""

from converter.layer_parser import LayerParser
from converter.layer_transformer import LayerTransformer
from converter.model.keymap_model import GlobalSettings, KeymapConfig
from converter.parser.macro_parser import MacroParser
from converter.parser.unicode_parser import UnicodeParser
from converter.transformer.kanata_transformer import KanataTransformer


def convert_zmk_to_kanata(input_file: str) -> str:
    """Convert a ZMK keymap file to Kanata format.

    Args:
        input_file: Path to the input ZMK keymap file

    Returns:
        String containing the Kanata keymap configuration

    Raises:
        FileNotFoundError: If input_file doesn't exist
        ValueError: If input file format is invalid
        Exception: For other unexpected errors
    """
    try:
        with open(input_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")

    # Parse the ZMK file
    layer_parser = LayerParser()
    macro_parser = MacroParser()
    unicode_parser = UnicodeParser()

    try:
        # Parse layers
        layers = layer_parser.parse_zmk_file(content)

        # Parse macros
        macro_behaviors = macro_parser.parse_behaviors(content)

        # Parse Unicode mappings
        unicode_parser.parse_unicode_mappings(content)
    except ValueError as e:
        raise ValueError(f"Invalid input file format: {e}")

    # Transform layers
    transformer = LayerTransformer()
    kanata_layers = [transformer.transform_layer(layer) for layer in layers]

    # Create the Kanata transformer
    kanata_transformer = KanataTransformer()

    # Register macro behaviors
    for macro in macro_behaviors:
        kanata_transformer.register_macro_behavior(macro)

    # Create a KeymapConfig object with default global settings
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=kanata_layers,
    )

    # Generate the Kanata configuration
    output = kanata_transformer.transform(config)

    return output
