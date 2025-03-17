# Error Handling System

The ZMK to Kanata converter includes a comprehensive error handling system that provides standardized error reporting, logging, and propagation throughout the codebase.

## Components

### Error Severity

The `ErrorSeverity` enum defines five levels of error severity:

1. **DEBUG**: Low-level diagnostic information
2. **INFO**: Informational messages about the conversion process
3. **WARNING**: Issues that don't stop conversion but should be addressed
4. **ERROR**: Serious issues that may prevent successful conversion
5. **CRITICAL**: Critical errors that require immediate attention

### ConversionError

The `ConversionError` class represents an error that occurred during conversion:

- **message**: The error message
- **source**: Module or component that detected the error
- **severity**: The severity level
- **line_number**: Optional line number in the source file
- **column**: Optional column number in the source file
- **context**: Optional context dictionary with additional information
- **traceback_info**: Optional traceback information

### ErrorManager

The `ErrorManager` class provides a centralized error tracking system:

- Collects and categorizes errors by severity and source
- Formats error messages consistently
- Provides filtering and reporting functionality
- Integrates with Python's logging system

## Usage

### Basic Error Handling

```python
from converter.error_handling import ErrorManager, ErrorSeverity

# Create an error manager
error_manager = ErrorManager(verbose=True)

# Add errors of different severities
error_manager.add_error(
    message="Could not parse binding",
    source="binding_parser",
    severity=ErrorSeverity.WARNING,
    line_number=42
)

# Check if there are errors of a certain severity
if error_manager.has_errors(ErrorSeverity.ERROR):
    print("Conversion failed due to errors")

# Get filtered errors
warnings = error_manager.get_errors(ErrorSeverity.WARNING)

# Generate error report
report = error_manager.get_error_report()
```

### Using the Global Error Manager

```python
from converter.error_handling import get_error_manager, ErrorSeverity

# Get the global error manager
error_manager = get_error_manager()

# Add errors
error_manager.add_error(
    message="Invalid key name",
    source="key_validator",
    severity=ErrorSeverity.ERROR,
    line_number=10,
    column=5
)
```

### Integration with Exception Handling

```python
from converter.error_handling import get_error_manager, ErrorSeverity

error_manager = get_error_manager()

try:
    # Code that might raise an exception
    process_file("input.zmk")
except FileNotFoundError as e:
    # Log the error with the exception
    error_manager.add_error(
        message="Input file not found",
        source="file_processor",
        severity=ErrorSeverity.ERROR,
        exception=e
    )
except Exception as e:
    # Log unexpected errors
    error_manager.add_error(
        message="Unexpected error",
        source="file_processor",
        severity=ErrorSeverity.CRITICAL,
        exception=e,
        raise_immediately=True  # Re-raise after logging
    )
```

### Formatting Error Messages

```python
from converter.error_handling import get_error_manager

error_manager = get_error_manager()

# Format an error message
message = error_manager.format_error_message(
    message="Invalid syntax",
    error_type="Parser",
    location="line 42, column 10",
    suggestion="Check for missing semicolon or parenthesis"
)

print(message)
# Output:
# Parser Error: Invalid syntax (at line 42, column 10)
# Suggestion: Check for missing semicolon or parenthesis
```

## Error Reports

The `get_error_report()` method generates a comprehensive report containing:

- Total number of errors
- Error counts by severity level
- Errors grouped by source component

Example report structure:

```json
{
  "total_errors": 3,
  "severity_counts": {
    "DEBUG": 0,
    "INFO": 0,
    "WARNING": 1,
    "ERROR": 2,
    "CRITICAL": 0
  },
  "errors_by_source": {
    "parser": [
      {
        "message": "Invalid binding format",
        "source": "parser",
        "severity": "ERROR",
        "line_number": 42,
        "column": 5,
        "context": {
          "binding": "&kp INVALID"
        },
        "traceback": null
      },
      {
        "message": "Missing closing bracket",
        "source": "parser",
        "severity": "ERROR",
        "line_number": 55,
        "column": null,
        "context": null,
        "traceback": null
      }
    ],
    "validator": [
      {
        "message": "Layer sizes inconsistent",
        "source": "validator",
        "severity": "WARNING",
        "line_number": null,
        "column": null,
        "context": {
          "sizes": [36, 42]
        },
        "traceback": null
      }
    ]
  }
}
```

## Integration with Components

The error handling system is integrated with all major components:

1. **ZMK Parser**: Reports parsing errors with line numbers
2. **Binding Parser**: Provides detailed error context for binding issues
3. **Transformer**: Reports transformation errors and inconsistencies
4. **Validator**: Logs validation issues with suggestions
5. **Main Conversion Function**: Centralizes error collection and reporting

## Best Practices

When using the error handling system:

1. Be specific in error messages
2. Include line/column information when available
3. Add context that helps diagnose the problem
4. Use appropriate severity levels
5. Provide suggestions for fixing common errors
6. Use verbose mode during development for detailed tracebacks 