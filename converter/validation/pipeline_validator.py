"""Pipeline validation module for ZMK to Kanata converter.

This module provides validation tools for the complete conversion pipeline.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from converter.model.keymap_model import Layer
from converter.validation.key_validator import validate_key, KeyValidationError


class PipelineValidationError(Exception):
    """Exception raised for validation errors in the conversion pipeline."""
    pass


class PipelineValidator:
    """Validates the complete ZMK to Kanata conversion pipeline."""

    def __init__(self):
        """Initialize the pipeline validator."""
        self.logger = logging.getLogger(__name__)
        self.validation_warnings = []
        self.validation_errors = []

    def validate_input(self, input_content: str) -> Tuple[bool, List[str]]:
        """Validate ZMK input format.

        Args:
            input_content: Content of the ZMK input file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for basic ZMK structure
        if "/ {" not in input_content:
            errors.append("Missing root node '/ {' in ZMK file")

        if "keymap {" not in input_content:
            errors.append("Missing keymap section in ZMK file")

        if "compatible = \"zmk,keymap\";" not in input_content:
            errors.append("Missing or incorrect compatible statement for keymap")

        if "default_layer" not in input_content and not any(
            f"l_{i}" in input_content
            for i in range(10)
        ):
            errors.append("No layers defined in ZMK file")

        # Check for balanced braces, angle brackets, and parentheses
        brace_count = 0
        angle_count = 0
        paren_count = 0

        for char in input_content:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '<':
                angle_count += 1
            elif char == '>':
                angle_count -= 1
            elif char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1

        if brace_count != 0:
            errors.append(
                f"Unbalanced braces in ZMK file (count: {brace_count})"
            )

        if angle_count != 0:
            msg = (
                f"Unbalanced angle brackets in ZMK file "
                f"(count: {angle_count})"
            )
            errors.append(msg)

        if paren_count != 0:
            msg = (
                f"Unbalanced parentheses in ZMK file (count: {paren_count})"
            )
            errors.append(msg)

        return len(errors) == 0, errors

    def validate_intermediate_representation(
        self,
        ir: Dict[str, Union[List[Layer], Dict[str, str]]]
    ) -> Tuple[bool, List[str]]:
        """Validate the intermediate representation.

        Args:
            ir: The intermediate representation dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        warnings = []

        # Validate layers
        if "layers" not in ir:
            errors.append("No layers in intermediate representation")
            return False, errors

        layers = ir["layers"]

        if not layers:
            errors.append("Empty layers list in intermediate representation")
            return False, errors

        # Check default layer
        if layers[0].name != "default":
            warnings.append("First layer is not named 'default'")

        # Check layer bindings
        layer_sizes = set()
        for i, layer in enumerate(layers):
            if not layer.bindings:
                warnings.append(f"Layer '{layer.name}' has no bindings")

            # Check for invalid keys
            for j, binding in enumerate(layer.bindings):
                try:
                    if binding.key != "unknown":
                        validate_key(binding.key)
                except KeyValidationError as e:
                    warnings.append(
                        f"Invalid key in layer '{layer.name}': {e}"
                    )

            layer_sizes.add(len(layer.bindings))

        # Check consistent layer sizes
        if len(layer_sizes) > 1:
            sizes_str = ", ".join(str(s) for s in layer_sizes)
            warnings.append(f"Inconsistent layer sizes: {sizes_str}")

        self.validation_warnings = warnings
        return len(errors) == 0, errors

    def validate_output(self, output_content: str) -> Tuple[bool, List[str]]:
        """Validate Kanata output format.

        Args:
            output_content: Content of the Kanata output file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for basic Kanata structure
        if not output_content.strip():
            errors.append("Empty output content")
            return False, errors

        # Verify layers are defined
        if "(deflayer" not in output_content:
            errors.append("No layers defined in Kanata output")

        # Check for default layer
        if "(deflayer default" not in output_content:
            errors.append("Default layer not defined in Kanata output")

        # Check for balanced parentheses
        paren_count = 0
        for char in output_content:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1

        if paren_count != 0:
            msg = (
                f"Unbalanced parentheses in Kanata output "
                f"(count: {paren_count})"
            )
            errors.append(msg)

        return len(errors) == 0, errors

    def validate_pipeline(
        self,
        input_content: str,
        intermediate_representation: Dict[
            str, Union[List[Layer], Dict[str, str]]
        ],
        output_content: str
    ) -> Dict[str, Union[bool, List[str]]]:
        """Validate the complete pipeline.

        Args:
            input_content: Content of the ZMK input file
            intermediate_representation: The intermediate representation 
                dictionary
            output_content: Content of the Kanata output file

        Returns:
            Dictionary with validation results
        """
        input_valid, input_errors = self.validate_input(input_content)
        ir_valid, ir_errors = self.validate_intermediate_representation(
            intermediate_representation
        )
        output_valid, output_errors = self.validate_output(output_content)

        return {
            "valid": input_valid and ir_valid and output_valid,
            "input_valid": input_valid,
            "ir_valid": ir_valid,
            "output_valid": output_valid,
            "input_errors": input_errors,
            "ir_errors": ir_errors,
            "output_errors": output_errors,
            "warnings": self.validation_warnings
        }

    def validate_files(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        ir: Optional[Dict[str, Union[List[Layer], Dict[str, str]]]] = None
    ) -> Dict[str, Union[bool, List[str]]]:
        """Validate input and output files.

        Args:
            input_file: Path to the ZMK input file
            output_file: Path to the Kanata output file
            ir: Optional intermediate representation

        Returns:
            Dictionary with validation results
        """
        try:
            with open(input_file, 'r') as f:
                input_content = f.read()

            with open(output_file, 'r') as f:
                output_content = f.read()

            if ir is not None:
                return self.validate_pipeline(
                    input_content, ir, output_content
                )
            else:
                input_valid, input_errors = self.validate_input(input_content)
                output_valid, output_errors = self.validate_output(
                    output_content
                )

                return {
                    "valid": input_valid and output_valid,
                    "input_valid": input_valid,
                    "output_valid": output_valid,
                    "input_errors": input_errors,
                    "output_errors": output_errors,
                    "warnings": self.validation_warnings
                }

        except FileNotFoundError as e:
            return {
                "valid": False,
                "errors": [f"File not found: {e}"]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Error validating files: {e}"]
            }
