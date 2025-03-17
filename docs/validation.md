# Validation System Documentation

The ZMK to Kanata converter includes comprehensive validation at multiple stages of the conversion process to ensure reliable transformations and provide helpful error messages.

## Components

### 1. Key Validator

The key validator ensures that key names and bindings are valid and properly formatted. It includes:

- Validation of standard ZMK key codes
- Key code normalization for Kanata format
- Support for modifiers and special keys
- Validation for layer references

### 2. Pipeline Validator

The pipeline validator provides comprehensive validation of the complete conversion pipeline, including:

- **Input Validation**: Ensures ZMK file is well-formed
- **Intermediate Representation Validation**: Validates the parsed data structure
- **Output Validation**: Verifies the generated Kanata file is correct

## Usage

### Key Validation

```python
from converter.validation.key_validator import validate_key, KeyValidationError

try:
    validate_key("A")  # Valid key
    validate_key("INVALID_KEY")  # Will raise KeyValidationError
except KeyValidationError as e:
    print(f"Invalid key: {e}")
```

### Pipeline Validation

```python
from converter.validation.pipeline_validator import PipelineValidator
from converter.zmk_to_kanata import validate_conversion

# Option 1: Direct validation
validator = PipelineValidator()
result = validator.validate_files("input.zmk", "output.kbd")

if result["valid"]:
    print("Conversion is valid!")
else:
    print("Validation errors:")
    for error in result["input_errors"] + result["output_errors"]:
        print(f"- {error}")
    
    # Check warnings
    for warning in result["warnings"]:
        print(f"Warning: {warning}")

# Option 2: Use convenience function
result = validate_conversion("input.zmk", "output.kbd")
```

## Validation Checks

### Input Validation

The input validator checks:

- Basic ZMK structure and syntax
- Presence of required sections (keymap, compatible statement)
- Layer definitions
- Balanced braces, angle brackets, and parentheses

### Intermediate Representation Validation

The IR validator checks:

- Layer presence and structure
- Key binding validity
- Layer consistency (consistent number of keys across layers)
- Default layer existence

### Output Validation

The output validator checks:

- Basic Kanata structure
- Presence of required sections (layers, default layer)
- Balanced parentheses
- Content integrity

## Error Handling

Validation errors are reported through the return values of the validation methods:

- Each validation method returns a tuple of `(is_valid, list_of_errors)`
- The `validate_pipeline` and `validate_files` methods return a dictionary with detailed validation information

### Validation Result Dictionary

```python
{
    "valid": bool,  # Overall validity
    "input_valid": bool,  # Input file validity
    "ir_valid": bool,  # Intermediate representation validity
    "output_valid": bool,  # Output file validity
    "input_errors": List[str],  # Input errors
    "ir_errors": List[str],  # IR errors
    "output_errors": List[str],  # Output errors
    "warnings": List[str]  # Validation warnings
}
```

## Integration with Conversion Pipeline

The validation system is integrated with the main conversion pipeline to provide error checking before, during, and after conversion:

1. Input validation is performed before parsing begins
2. Intermediate representation validation after parsing completes
3. Output validation before returning the final Kanata configuration

This multi-stage validation ensures robust error detection and reporting throughout the conversion process. 