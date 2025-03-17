# ZMK to Kanata Converter

A tool to convert ZMK keymaps to Kanata format.

## Features

- Converts ZMK keymap files to Kanata configuration files
- Supports various key behaviors:
  - Basic key mappings
  - Hold-tap behaviors
  - Layer switching
  - Sticky keys
  - Macros with timing configuration
- Comprehensive key validation
- Nested behavior support
- Error handling and validation

## Key Validation

The converter includes a robust key validation system that ensures:

1. All keys are valid and supported
2. Layer numbers are valid
3. Timing values are within acceptable ranges
4. Nested behaviors are properly configured

For detailed information about key validation, see [Key Mapping and Validation](key_mapping.md).

## Usage

```bash
python -m converter input.keymap output.kbd
```

## Documentation

- [Key Mapping and Validation](key_mapping.md)
- [Behavior Support](behaviors.md)
- [Error Handling](error_handling.md)

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project follows PEP 8 guidelines. Key points:
- Line length limit: 79 characters
- Use descriptive variable names
- Include docstrings for all public functions and classes

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details 