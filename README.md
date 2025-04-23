# ZMK to Kanata Converter

A tool to convert ZMK keymap files to Kanata format, using a robust DTS (Device Tree Source) parser.

## Features

- Full DTS parsing support for ZMK keymap files
- Comprehensive behavior handling:
  - Hold-tap behaviors with configurable timing and flavors
  - Layer switching (momentary, toggle, to-layer)
  - Sticky keys and modifiers
  - Macro support
  - Transparent keys
- Matrix layout support with automatic size detection
- Built-in ZMK header files - no external dependencies needed
- Clean, readable Kanata output

## Requirements

- Python 3.11+
- C preprocessor (cpp) - included on most Unix systems, needs manual install on Windows
- uv for Python package management (recommended)

## Installation

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/zmk-to-kanata.git
cd zmk-to-kanata

# Install dependencies
uv pip install -r requirements.txt

# Install for development
uv pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
zmk-to-kanata input.zmk -o output.kbd

# With custom include paths (optional)
zmk-to-kanata input.zmk -o output.kbd -I /path/to/includes
```

### Python API

```python
from converter.main import convert_zmk_to_kanata

# Convert a ZMK file to Kanata format
kanata_config = convert_zmk_to_kanata(
    "path/to/keymap.zmk",
    include_paths=None  # Optional - converter includes ZMK headers by default
)

# Write the configuration to a file
with open("output.kbd", "w") as f:
    f.write(kanata_config)
```

## Supported Features

### Basic Features
- Complete keymap configuration
- Layer definitions and switching
- Basic key bindings and modifiers
- Matrix layout detection

### Advanced Features
- Hold-tap behaviors with full configuration:
  - Timing parameters (tap-time, hold-time)
  - Flavor selection (balanced, hold-preferred, tap-preferred)
  - Quick-tap and global quick-tap
  - Hold-trigger key positions
- Sticky keys with timing configuration
- Macro support with key sequences
- Transparent key handling

### DTS Features
- Full DTS syntax support
- Built-in ZMK header files
- Proper handling of:
  - Node definitions
  - Properties and values
  - Labels and references
  - Include directives
  - Preprocessor macros

## Breaking Changes

If upgrading from a previous version, note these changes:

1. **API Changes**
   - `convert_zmk_to_kanata()` now uses DTS parsing by default
   - Include paths are optional - ZMK headers are bundled
   - Improved error messages with file/line context

2. **Configuration Changes**
   - Hold-tap configuration format updated
   - Layer behavior syntax aligned with ZMK spec
   - Macro definition structure changed

## Examples

### Basic Keymap

```dts
/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B
                &kp C &kp D
            >;
        };
    };
};
```

### Hold-Tap Configuration

```dts
/ {
    behaviors {
        hm: homerow_mods {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            tapping-term-ms = <200>;
            flavor = "tap-preferred";
            bindings = <&kp>, <&kp>;
        };
    };
    
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &hm LSHIFT A &hm LCTL B
                &kp C        &kp D
            >;
        };
    };
};
```

## Known Limitations

1. **Unsupported ZMK Features**
   - Combos
   - RGB/LED controls
   - Bluetooth profiles
   - Custom behaviors beyond standard types

2. **Technical Limitations**
   - Matrix size must be defined or detectable
   - Some advanced preprocessor directives may not work
   - Windows requires manual cpp installation

## Troubleshooting

### Common Issues

1. **Preprocessing Errors**
   - Error: "Failed to preprocess DTS file"
   - Solution: Verify cpp is installed and in PATH

2. **Node Resolution Errors**
   - Error: "Cannot resolve node reference"
   - Solution: Check label definitions and references

3. **Behavior Configuration**
   - Error: "Invalid behavior configuration"
   - Solution: Verify behavior properties match ZMK spec

### Getting Help

If you encounter issues:
1. Enable debug logging: `zmk-to-kanata --debug input.zmk`
2. Check error messages for file/line information
3. Open an issue with:
   - Your ZMK file
   - Complete error output
   - Expected behavior

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
