# Testing Guide for Contributors

This guide provides information on how to write, run, and maintain tests for the ZMK to Kanata Converter project. Following these guidelines will help ensure that the converter remains reliable and maintainable.

## Test Structure

The test suite is organized into several categories:

1. **Unit Tests**: Located in `converter/tests/`
   - Test individual components in isolation
   - Focus on specific functionality
   - Use mocks and stubs when necessary

2. **End-to-End Tests**: Located in `converter/tests/e2e_tests/`
   - Test the entire conversion process
   - Use real input and output files
   - Verify actual behavior of the converter

## Running Tests

### Running All Tests

To run all tests:

```bash
python -m pytest
```

### Running Specific Tests

To run a specific test file:

```bash
python -m pytest converter/tests/test_file.py
```

To run a specific test function:

```bash
python -m pytest converter/tests/test_file.py::test_function
```

### Running with Coverage

To run tests with coverage:

```bash
python -m pytest --cov=converter
```

To generate an HTML coverage report:

```bash
python -m pytest --cov=converter --cov-report=html
```

The HTML report will be available in the `htmlcov` directory.

## Writing Tests

### Unit Tests

When writing unit tests, follow these guidelines:

1. **Test One Thing**: Each test should focus on testing one specific functionality.

2. **Use Descriptive Names**: Test names should clearly describe what is being tested.

3. **Arrange-Act-Assert**: Structure tests with setup, action, and verification.

4. **Use Fixtures**: Use pytest fixtures for common setup and teardown.

Example:

```python
def test_transform_binding():
    # Arrange
    binding = KeyMapping(key="A")
    transformer = LayerTransformer()

    # Act
    result = transformer.transform_binding(binding)

    # Assert
    assert result == "a"
```

### End-to-End Tests

When writing end-to-end tests, follow these guidelines:

1. **Use Real-World Examples**: Test with realistic ZMK configurations.

2. **Verify Output**: Check that the generated Kanata file contains the expected content.

3. **Test Error Cases**: Verify that the converter handles errors gracefully.

4. **Use Temporary Files**: Use the `tmp_path` fixture to create temporary test files.

Example:

```python
def test_basic_file_conversion(tmp_path, monkeypatch):
    # Setup test files
    zmk_file = tmp_path / "test.dtsi"
    kanata_file = tmp_path / "test.kbd"

    # Write test content
    zmk_file.write_text("/ { keymap { compatible = \"zmk,keymap\"; ... } };")

    # Set up CLI arguments
    monkeypatch.setattr(sys, 'argv', ['converter', str(zmk_file), str(kanata_file)])

    # Run the converter
    from converter.main import main
    main()

    # Verify the output
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(deflayer default" in content
```

## Test Coverage

Aim for high test coverage, especially for critical components:

1. **Parser Components**: Ensure all parsing logic is thoroughly tested.

2. **Transformer Components**: Test all transformation logic with various inputs.

3. **Error Handling**: Test error conditions and edge cases.

4. **CLI Interface**: Test command-line interface functionality.

## Adding New Tests

When adding new features or fixing bugs, follow these steps:

1. **Write Tests First**: Consider writing tests before implementing the feature (TDD).

2. **Cover Edge Cases**: Include tests for edge cases and error conditions.

3. **Update Existing Tests**: Update existing tests if the behavior changes.

4. **Run the Full Suite**: Ensure all tests pass after making changes.

## Testing Real-World Configurations

To test with real-world configurations:

1. **Collect Examples**: Gather ZMK configurations from actual users.

2. **Simplify if Needed**: Simplify complex configurations for testing purposes.

3. **Document Limitations**: Note any limitations or unsupported features.

4. **Add to Test Suite**: Add the examples to the test suite in `converter/tests/e2e_tests/test_real_world_configs.py`.

Example:

```python
def test_real_world_example(tmp_path, monkeypatch):
    # Setup test files
    zmk_file = tmp_path / "real_world.dtsi"
    kanata_file = tmp_path / "real_world.kbd"

    # Real-world ZMK configuration (simplified)
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Run the converter
    monkeypatch.setattr(sys, 'argv', ['converter', str(zmk_file), str(kanata_file)])
    from converter.main import main
    main()

    # Verify the output
    assert kanata_file.exists()
    kanata_content = kanata_file.read_text()
    assert "a b c" in kanata_content.lower()
    assert "d e f" in kanata_content.lower()
```

## Continuous Integration

The project uses GitHub Actions for continuous integration:

1. **Automated Testing**: All tests are run automatically on push and pull requests.

2. **Coverage Reports**: Coverage reports are generated for each build.

3. **Linting**: Code is linted to ensure it follows style guidelines.

## Troubleshooting Tests

If tests are failing, consider these steps:

1. **Run Specific Test**: Run the failing test in isolation to see detailed output.

2. **Check Fixtures**: Ensure fixtures are set up correctly.

3. **Check Dependencies**: Verify that all dependencies are installed.

4. **Debug with Print**: Add print statements to debug complex issues.

5. **Use pytest -v**: Run tests with verbose output for more information.

## Conclusion

Testing is a critical part of maintaining the ZMK to Kanata Converter. By following these guidelines, contributors can help ensure that the converter remains reliable and maintainable.

If you have questions about testing or need help writing tests, please open an issue on GitHub.
