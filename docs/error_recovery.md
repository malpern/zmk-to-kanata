# Error Recovery System

The ZMK to Kanata converter includes a robust error recovery system that helps handle parsing errors gracefully. This document explains how the system works and how to use it effectively.

## Overview

The error recovery system consists of two main components:

1. `ErrorRecoveryManager`: Handles individual errors and maintains error state
2. `ParserErrorRecoveryWrapper`: Wraps any parser to add error recovery capabilities

## Error Recovery Manager

The `ErrorRecoveryManager` class provides methods for handling various types of parsing errors:

- `handle_invalid_binding`: Creates a fallback binding when an invalid binding is encountered
- `handle_invalid_layer`: Creates an empty layer when an invalid layer is encountered
- `get_error_summary`: Returns a summary of all errors that occurred during parsing
- `has_errors`: Checks if any errors occurred during parsing

### Error Types

The system currently handles these types of errors:

- `invalid_binding`: When a binding cannot be parsed
- `invalid_layer`: When a layer definition is invalid

### Error Summary Format

The error summary is a dictionary with the following structure:

```python
{
    "errors": [
        {
            "type": "error_type",
            "line": "original_content",
            "line_number": line_number,
            "message": "error_message"
        }
    ],
    "total_errors": number_of_errors,
    "error_types": {
        "error_type": count
    }
}
```

## Parser Error Recovery Wrapper

The `ParserErrorRecoveryWrapper` class wraps any parser to add error recovery:

```python
from converter.parser.error_recovery_wrapper import ParserErrorRecoveryWrapper
from converter.parser.zmk_parser import ZMKParser

# Create a parser with error recovery
parser = ParserErrorRecoveryWrapper(ZMKParser)

# Parse with error recovery
result = parser.parse(content)

# Check for errors
if parser.has_errors():
    print(parser.get_error_summary())
```

### Recovery Strategies

1. **Invalid Bindings**
   - Returns an "unknown" binding instead of failing
   - Logs a warning with the invalid binding details
   - Continues parsing the rest of the file

2. **Invalid Layers**
   - Creates an empty layer with the specified name
   - Logs a warning with the invalid layer details
   - Continues parsing other layers

## Best Practices

1. **Always Check for Errors**
   ```python
   if parser.has_errors():
       errors = parser.get_error_summary()
       # Handle errors appropriately
   ```

2. **Log Error Details**
   - The system automatically logs warnings and errors
   - Use the error summary for detailed error reporting

3. **Graceful Degradation**
   - Invalid bindings become "unknown" bindings
   - Invalid layers become empty layers
   - This allows partial functionality even with errors

4. **Error Recovery in Tests**
   - Test both successful and error cases
   - Verify error summaries have correct information
   - Check that recovery produces expected fallback values

## Example Usage

```python
from converter.parser.error_recovery_wrapper import ParserErrorRecoveryWrapper
from converter.parser.zmk_parser import ZMKParser

def convert_with_recovery(content: str):
    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)
    
    if parser.has_errors():
        errors = parser.get_error_summary()
        print(f"Encountered {errors['total_errors']} errors:")
        for error in errors["errors"]:
            print(f"- {error['message']}")
    
    return result
```

This system ensures that the converter can handle invalid input gracefully while providing detailed error information for debugging and user feedback. 