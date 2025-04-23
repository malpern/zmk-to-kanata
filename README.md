# ZMK to Kanata Converter

A tool to convert ZMK keymap files to Kanata format.

## Features

- Converts ZMK keymap files to Kanata format
- Supports matrix layouts of any size
- Handles hold-tap behaviors
- Supports layer switching
- Preserves transparent keys
- Uses DTS parsing for robust handling of ZMK files

## Requirements

- Python 3.11+
- C preprocessor (cpp) installed on your system
- uv for Python package management

## Installation

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt
```

## Usage

```python
from converter.main import convert_zmk_to_kanata

# Convert a ZMK file to Kanata format
kanata_config = convert_zmk_to_kanata(
    "path/to/keymap.zmk",
    include_paths=["path/to/zmk/include"]
)

# Write the configuration to a file
with open("output.kbd", "w") as f:
    f.write(kanata_config)
```

## Supported Features

- Matrix layouts of any size
- Hold-tap behaviors with configurable timing
- Layer switching (to_layer, momentary_layer)
- Transparent keys
- Key bindings

## Limitations

- Some advanced ZMK features may not be supported
- Requires a C preprocessor to be installed
- Include paths must be specified for ZMK header files

## Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Code Style

This project uses black for Python code formatting:

```bash
black .
```

## License

MIT License

## Overview

This project provides a robust conversion tool that maintains feature parity where possible, provides clear error messages for unsupported features, and generates clean, readable Kanata output.

## Features

- Convert ZMK keymap files to Kanata format
- Support for common keyboard features:
  - Basic key mappings
  - Layer definitions
  - Modifiers and modifier combinations
  - Media and special keys
  - Unicode input
  - Macros
- Advanced features support:
  - Hold-tap behaviors (including homerow mods)
  - Sticky keys
  - Custom behaviors
  - Complex modifier combinations
- Comprehensive error reporting
- Clean, readable output

## Known Limitations

- No support for advanced ZMK features like combos
- Limited to standard keyboard layouts
- Focus on common use cases first

## Troubleshooting

### Common Issues

1. **Invalid Key Names**
   - Error: "Invalid key name in binding"
   - Solution: Check that key names match ZMK's key codes

2. **Layer Issues**
   - Error: "Layer not found"
   - Solution: Ensure all referenced layers are defined

3. **Syntax Errors**
   - Error: "Failed to parse ZMK file"
   - Solution: Verify ZMK file syntax and formatting

### Getting Help

If you encounter issues:
1. Check the error message for specific details
2. Verify your ZMK file syntax
3. Open an issue on GitHub with:
   - Your ZMK file
   - The error message
   - Expected behavior

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## DTS Preprocessor

The converter includes a DTS preprocessor that uses the C preprocessor to handle ZMK keymap files. This allows for proper handling of includes, macros, and other preprocessor directives.

### Usage

```python
from converter.dts_preprocessor import DtsPreprocessor

# Initialize with include paths
preprocessor = DtsPreprocessor(include_paths=['/path/to/includes'])

# Preprocess a file
result = preprocessor.preprocess('keymap.zmk')
```

### Features

- Handles include files and paths
- Processes macros and definitions
- Proper error handling for missing files and invalid paths
- Uses the system C preprocessor (cpp)

### Requirements

- A C preprocessor (cpp) must be installed on the system
- Include paths must exist and be accessible
