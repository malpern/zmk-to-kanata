# Test Scenarios and Coverage

This document outlines the test scenarios covered in the ZMK to Kanata converter test suite.

## Test Organization

The test suite is organized into three main categories:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test the full conversion pipeline

## Unit Tests

### Binding Parser

Located in `converter/tests/unit/test_binding_parser.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Basic Bindings | Parse simple key press bindings | `&kp A` |
| Layer Bindings | Parse layer activation bindings | `&mo 1`, `&tog 2` |
| Mod-Tap Bindings | Parse modifier-tap bindings | `&mt LSHIFT A` |
| Layer-Tap Bindings | Parse layer-tap bindings | `&lt 1 A` |
| Nested Bindings | Parse bindings with nested behaviors | `&lt 1 (&kp A)` |
| Invalid Bindings | Test error handling for invalid bindings | `&invalid X` |
| Parameter Validation | Verify parameter validation | `&lt TEXT A` (invalid) |
| Edge Cases | Handle edge cases like empty params | `&kp` (invalid) |

### Layer Parser

Located in `converter/tests/unit/test_layer_parser.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Basic Layer Parsing | Parse simple layer definitions | `default_layer { bindings = <...>; };` |
| Multiple Layers | Parse multiple layer definitions | Multiple layer blocks |
| Empty Layers | Handle empty layer definitions | `layer_empty { bindings = <>; };` |
| Malformed Layers | Test error handling for malformed layers | Missing closing tags, etc. |
| Layer Names | Validate layer name conversion | `default_layer` → `default` |

### Key Validation

Located in `converter/tests/unit/test_key_validator.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Standard Keys | Validate standard alphanumeric keys | `A`, `B`, `1`, `2` |
| Special Keys | Validate special keys | `SPACE`, `TAB`, `ENTER` |
| Modifiers | Validate modifier keys | `LSHIFT`, `LCTRL` |
| Function Keys | Validate function keys | `F1`, `F2` |
| Invalid Keys | Test error handling for invalid keys | `INVALID_KEY` |
| Key Conversion | Verify ZMK to Kanata key conversion | `SPACE` → `spc` |

### Error Recovery

Located in `converter/tests/unit/test_error_recovery.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Binding Errors | Recover from invalid bindings | Replace with `unknown` |
| Layer Errors | Recover from invalid layer definitions | Create placeholder layer |
| Syntax Errors | Recover from general syntax errors | Skip/handle invalid lines |
| Error Reporting | Verify error reporting functionality | Check error counts and types |
| Fallback Values | Test fallback value generation | Default values for missing params |

## Integration Tests

### Binding Parser Integration

Located in `converter/tests/integration/test_binding_parser_integration.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Basic Integration | Test binding parser with ZMK parser | Simple keymap with basic bindings |
| Complex Bindings | Test complex binding handling | Keymap with nested behaviors |
| Error Recovery | Test error recovery in binding parser | Keymap with invalid bindings |
| Multiline Bindings | Test multiline binding formats | Bindings across multiple lines |
| Multiple Layers | Test bindings across multiple layers | Keymap with several layers |

### Error Recovery Integration

Located in `converter/tests/integration/test_error_recovery_integration.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Invalid Binding Recovery | Test recovery from invalid bindings | Replace with placeholder |
| Invalid Layer Recovery | Test recovery from invalid layers | Create empty layer |
| Multiple Error Recovery | Test handling multiple errors | Multiple issues in same file |
| Nested Behavior Recovery | Test recovery in nested behaviors | Invalid nested binding |
| Comment Handling | Test error recovery with comments | Commented lines |
| Preserving Valid Content | Verify valid content is preserved | Mix of valid/invalid bindings |

### ZMK to Kanata Conversion

Located in `converter/tests/integration/test_zmk_to_kanata_conversion.py`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Basic Conversion | Test basic keymap conversion | Simple keymap |
| Layer Conversion | Test multi-layer conversion | Keymap with multiple layers |
| Complex Binding Conversion | Test conversion of complex bindings | Nested behaviors |
| Macro Conversion | Test macro definition conversion | Keymap with macros |
| Global Settings | Test handling of global settings | Settings in ZMK keymap |

## End-to-End Tests

Located in `converter/tests/integration/end_to_end/`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Basic Pipeline | Test full conversion pipeline | Simple keymap file |
| Complex Keymap | Test with complex keymap example | Corne keyboard layout |
| Real-World Examples | Test with actual user configs | Ferris Sweep layout |
| Error Handling | Verify error handling in full pipeline | Keymap with errors |
| Multiple Layers | Test multi-layer handling | Keymap with 3+ layers |
| Global Settings | Test global settings handling | Keymap with settings |

## Performance Tests

Located in `converter/tests/performance/`.

| Test Scenario | Description | Example |
|---------------|-------------|---------|
| Parser Performance | Benchmark parser performance | Small/large keymaps |
| Transformer Performance | Benchmark transformer performance | Various keymap sizes |
| Memory Usage | Test memory consumption | Very large keymaps |
| End-to-End Performance | Benchmark full pipeline | Complete conversion |

## Test Coverage

The test suite aims for high coverage across all components:

| Component | Coverage Target | Key Focus Areas |
|-----------|----------------|-----------------|
| Parser | 90%+ | State transitions, error handling |
| Binding Parser | 95%+ | All binding types, nested behaviors |
| Transformer | 90%+ | All key types, special behaviors |
| Error Recovery | 95%+ | All error scenarios |
| CLI | 80%+ | Command-line options, file handling |

## Running Tests

To run the complete test suite:

```bash
pytest
```

To run specific test categories:

```bash
# Unit tests only
pytest converter/tests/unit/

# Integration tests
pytest converter/tests/integration/

# End-to-end tests
pytest converter/tests/integration/end_to_end/

# Performance tests
pytest converter/tests/performance/
```

To generate a coverage report:

```bash
pytest --cov=converter
```

## Test Fixtures

The test suite uses fixtures to provide sample data and test environments:

| Fixture | Purpose | Location |
|---------|---------|----------|
| `sample_keymap` | Provides sample keymap string | `converter/tests/conftest.py` |
| `sample_binding` | Provides sample binding string | `converter/tests/conftest.py` |
| `temp_keymap_file` | Creates temporary file for testing | `converter/tests/conftest.py` |
| `mock_parser` | Provides a mock parser for testing | `converter/tests/unit/conftest.py` |

## Continuous Integration

Tests are run automatically as part of the CI pipeline to ensure code quality and prevent regressions.

### CI Test Environment

The CI environment runs tests against multiple Python versions to ensure compatibility:

- Python 3.8
- Python 3.9
- Python 3.10

### Test Reporting

Test results and coverage statistics are recorded and tracked over time to monitor progress and ensure quality is maintained or improved. 