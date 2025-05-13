# Contributing to ZMK to Kanata Converter

Thank you for your interest in contributing to the ZMK to Kanata Converter! This document provides guidelines and information for contributors.

## Development Setup

1. **Prerequisites**
   - Python 3.11+
   - C preprocessor (cpp)
   - uv package manager (recommended)

2. **Setting Up Development Environment**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/zmk-to-kanata.git
   cd zmk-to-kanata

   # Install dependencies
   uv pip install -r requirements.txt

   # Install for development
   uv pip install -e .
   ```

3. **Running Tests**
   ```bash
   # Run all tests
   python -m pytest tests/

   # Run specific test file
   python -m pytest tests/test_holdtap_transformer.py

   # Run with coverage
   python -m pytest --cov=converter tests/
   ```

## Code Style

1. **Formatting**
   - We use Black for code formatting
   - Maximum line length is 79 characters
   - Run `black .` before committing

2. **Linting**
   - We use Ruff for linting
   - Run `ruff check .` to check for issues
   - Run `ruff check . --fix` to auto-fix issues

3. **Type Hints**
   - All new code should include type hints
   - Use `mypy` to check type correctness

4. **Data Contracts**
   - All data models must use Python's `@dataclass` for data contracts
   - Do **not** use Pydantic, attrs, TypedDict, or NamedTuple for new models
   - Ensure all fields are type-annotated and include docstrings
   - Maintain consistency with existing model style throughout the codebase

## Pull Request Process

1. **Before Creating a PR**
   - Create a new branch for your changes
   - Ensure all tests pass
   - Add tests for new functionality
   - Update documentation as needed
   - Run formatters and linters

2. **PR Guidelines**
   - Provide a clear description of changes
   - Link to any related issues
   - Include test coverage for new code
   - Keep changes focused and atomic

3. **Review Process**
   - PRs require one approval
   - Address review feedback promptly
   - Maintain a clean commit history

## Testing Guidelines

1. **Unit Tests**
   - Write tests for all new functionality
   - Use descriptive test names
   - Follow the existing test structure
   - Include edge cases and error conditions

2. **Integration Tests**
   - Add tests for new feature interactions
   - Test with real-world ZMK configs
   - Verify Kanata output correctness

3. **Test Coverage**
   - Aim for 90%+ coverage on new code
   - Include both success and error cases
   - Test edge cases and invalid inputs

## Documentation

1. **Code Documentation**
   - Add docstrings to all new functions/classes
   - Include type hints and parameter descriptions
   - Document exceptions and return values
   - Add inline comments for complex logic

2. **User Documentation**
   - Update README.md for user-facing changes
   - Add examples for new features
   - Document breaking changes
   - Include troubleshooting information

## Issue Guidelines

1. **Bug Reports**
   - Include Python and system versions
   - Provide minimal reproduction steps
   - Attach relevant ZMK config files
   - Include complete error messages

2. **Feature Requests**
   - Clearly describe the use case
   - Provide example configurations
   - Discuss limitations and alternatives
   - Consider backward compatibility

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 