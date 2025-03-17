"""Module for converting ZMK keymap files to Kanata format."""

from pathlib import Path
from typing import Dict, Optional, Union, Any, Tuple

from converter.error_handling import (
    ErrorManager,
    ErrorSeverity,
    get_error_manager,
    set_error_manager,
)
from converter.parser.zmk_parser import ZMKParser
from converter.transformer.kanata_transformer import KanataTransformer
from converter.validation.pipeline_validator import PipelineValidator


def convert_zmk_to_kanata(
    zmk_content: str,
    output_path: Optional[str] = None,
    error_manager: Optional[ErrorManager] = None,
    is_mac: bool = False
) -> Tuple[str, Dict[str, Any]]:
    """Convert ZMK keymap to Kanata format.
    
    Args:
        zmk_content: Content of the ZMK keymap file
        output_path: Optional path to write the Kanata config to
        error_manager: Optional error manager for reporting issues
        is_mac: Whether to use Mac-specific modifiers
        
    Returns:
        Tuple of (Kanata config string, metadata dict)
        
    Raises:
        Exception: If there's an error during conversion
    """
    # Set up error manager
    if error_manager:
        set_error_manager(error_manager)
    else:
        set_error_manager(ErrorManager())
    
    error_mgr = get_error_manager()
    
    try:
        # Parse ZMK keymap
        parser = ZMKParser()
        keymap_config = parser.parse(zmk_content)
        
        # Transform to Kanata format
        transformer = KanataTransformer(is_mac=is_mac)
        kanata_layers = []
        
        for layer in keymap_config.layers:
            kanata_layer = transformer.transform_layer(layer)
            kanata_layers.append(kanata_layer)
            
        # Generate Kanata keymap
        source_keys = transformer.get_source_keys(keymap_config.layers)
        kanata_config = transformer.generate_kanata_keymap(
            source_keys, kanata_layers
        )
        
        # Write to file if output path is provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(kanata_config)
            output_msg = (
                f"Successfully wrote Kanata config to {output_path}"
            )
            error_mgr.add_error(
                message=output_msg,
                source="converter",
                severity=ErrorSeverity.INFO
            )
            
        # Return the Kanata config and metadata
        metadata = {
            "layer_count": len(keymap_config.layers),
            "global_settings": keymap_config.global_settings,
            "errors": error_mgr.get_error_report()
        }
        
        return kanata_config, metadata
        
    except Exception as e:
        error_mgr.add_error(
            message=f"Error during conversion: {str(e)}",
            source="converter",
            severity=ErrorSeverity.ERROR,
            exception=e,
            raise_immediately=True
        )
        # This will never be reached due to raise_immediately=True
        return "", {}


def validate_conversion(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    error_manager: Optional[ErrorManager] = None,
) -> Dict[str, Any]:
    """Validate a conversion without performing it.

    Args:
        input_file: Path to the input ZMK file
        output_file: Path to the output Kanata file
        error_manager: Optional custom error manager instance

    Returns:
        Dictionary with validation results
    """
    error_mgr = error_manager or get_error_manager()
    validator = PipelineValidator()

    try:
        result = validator.validate_files(input_file, output_file)

        # Log validation issues
        if not result.get("valid", False):
            for error_type in ["input_errors", "output_errors"]:
                for error in result.get(error_type, []):
                    error_mgr.add_error(
                        message=error,
                        source=f"validation_{error_type}",
                        severity=ErrorSeverity.ERROR
                    )

        # Log any warnings
        for warning in result.get("warnings", []):
            error_mgr.add_error(
                message=warning,
                source="validation",
                severity=ErrorSeverity.WARNING
            )

        return result
    except Exception as e:
        error_mgr.add_error(
            message=f"Error during validation: {e}",
            source="validation",
            severity=ErrorSeverity.ERROR,
            exception=e,
            raise_immediately=True
        )
