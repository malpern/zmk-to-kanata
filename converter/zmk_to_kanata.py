"""Module for converting ZMK keymap files to Kanata format."""

from pathlib import Path
from typing import Dict, Optional, Union, Any

from converter.error_handling import (
    ErrorManager,
    ErrorSeverity,
    get_error_manager,
)
from converter.parser.zmk_parser import ZMKParser
from converter.transformer.kanata_transformer import KanataTransformer
from converter.validation.pipeline_validator import PipelineValidator


def convert_zmk_to_kanata(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    error_manager: Optional[ErrorManager] = None,
) -> Union[str, bool]:
    """Convert a ZMK keymap file to Kanata format.

    Args:
        input_file: Path to the input ZMK keymap file
        output_file: Optional path to write the output Kanata file.
                     If not provided, the function returns the
                     Kanata content as a string.
        error_manager: Optional custom error manager instance. If not
                      provided, the global error manager is used.

    Returns:
        If output_file is provided, returns True on successful conversion,
        otherwise returns the Kanata keymap configuration as a string.

    Raises:
        FileNotFoundError: If input_file doesn't exist
        ValueError: If input file format is invalid
        Exception: For other unexpected errors
    """
    # Set up error manager
    error_mgr = error_manager or get_error_manager()

    # Convert paths to Path objects
    input_path = Path(input_file)
    output_path = Path(output_file) if output_file else None

    try:
        with open(input_path, 'r') as f:
            content = f.read()
    except FileNotFoundError as e:
        error_mgr.add_error(
            message=f"Input file not found: {input_path}",
            source="zmk_to_kanata",
            severity=ErrorSeverity.ERROR,
            exception=e,
            raise_immediately=True
        )
    except Exception as e:
        error_mgr.add_error(
            message=f"Error reading input file: {e}",
            source="zmk_to_kanata",
            severity=ErrorSeverity.ERROR,
            exception=e,
            raise_immediately=True
        )

    # Validate input file format
    validator = PipelineValidator()
    input_valid, input_errors = validator.validate_input(content)

    if not input_valid:
        # Log all validation errors
        for error in input_errors:
            error_mgr.add_error(
                message=error,
                source="input_validation",
                severity=ErrorSeverity.ERROR
            )

        # Raise the first error
        error_mgr.add_error(
            message=f"Invalid input file format: {input_errors[0]}",
            source="zmk_to_kanata",
            severity=ErrorSeverity.ERROR,
            raise_immediately=True
        )

    # Parse the ZMK file
    parser = ZMKParser(error_manager=error_mgr)

    try:
        # Parse ZMK file
        ir = parser.parse(content)

        # Create the Kanata transformer
        transformer = KanataTransformer()

        # Generate the Kanata configuration
        output = transformer.transform(ir)

        # Validate intermediate representation and output
        ir_valid, ir_errors = validator.validate_intermediate_representation(
            ir
        )
        output_valid, output_errors = validator.validate_output(output)

        if not ir_valid:
            for error in ir_errors:
                error_mgr.add_error(
                    message=error,
                    source="ir_validation",
                    severity=ErrorSeverity.WARNING
                )

        if not output_valid:
            for error in output_errors:
                error_mgr.add_error(
                    message=error,
                    source="output_validation",
                    severity=ErrorSeverity.WARNING
                )

        # Log any validation warnings
        for warning in validator.validation_warnings:
            error_mgr.add_error(
                message=warning,
                source="validation",
                severity=ErrorSeverity.WARNING
            )

        # Write output to file if specified
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    f.write(output)

                # Log success
                output_msg = (
                    f"Successfully wrote Kanata config to {output_path}"
                )
                error_mgr.add_error(
                    message=output_msg,
                    source="zmk_to_kanata",
                    severity=ErrorSeverity.INFO
                )
                return True
            except Exception as e:
                error_mgr.add_error(
                    message=f"Error writing to output file {output_path}",
                    source="zmk_to_kanata",
                    severity=ErrorSeverity.ERROR,
                    exception=e,
                    raise_immediately=True
                )

        # Return the output string if no output file is specified
        return output

    except ValueError as e:
        error_mgr.add_error(
            message=f"Error parsing ZMK file: {e}",
            source="zmk_parser",
            severity=ErrorSeverity.ERROR,
            exception=e,
            raise_immediately=True
        )
    except Exception as e:
        error_mgr.add_error(
            message=f"Unexpected error during conversion: {e}",
            source="zmk_to_kanata",
            severity=ErrorSeverity.ERROR,
            exception=e,
            raise_immediately=True
        )


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
