# ZMK to Kanata Converter

A robust tool to convert ZMK keymap files (DTS format) to Kanata
configuration files, supporting advanced keyboard behaviors and a wide
range of ZMK features. Designed for keyboard enthusiasts and power users
who want to migrate or experiment with Kanata using their existing ZMK
layouts.

---

## Quickstart

```bash
# Install uv (recommended, or use pip)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/zmk-to-kanata.git
cd zmk-to-kanata

# Install dependencies
uv pip install -r requirements.txt

# Convert a ZMK keymap to Kanata format
zmk-to-kanata input.zmk -o output.kbd
```

- For more details, see the [User Guide](docs/user_guide.md).
- For API usage, see [API Documentation](docs/api_documentation.md).
- For known issues, see [Known Limitations](docs/known_limitations.md).

---

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

# Debugging: dump preprocessed DTS to stdout
zmk-to-kanata input.zmk --dump-preprocessed

# Dump AST to a file and enable debug logging
zmk-to-kanata input.zmk --dump-ast ast.json --debug
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

## Debugging and Output Flags

The converter provides robust debugging and output flags to aid in troubleshooting and development. These allow you to inspect intermediate representations at each stage of the conversion pipeline.

| Flag                        | Description                                                      |
|-----------------------------|------------------------------------------------------------------|
| `--dump-preprocessed [FILE]`| Output preprocessed DTS to stdout or FILE                         |
| `--dump-ast [FILE]`         | Output parsed AST (as JSON) to stdout or FILE                     |
| `--dump-extracted [FILE]`   | Output extracted keymap model (as YAML/JSON) to stdout or FILE    |
| `--debug`                   | Print debug logs at all stages (uses logging)                    |
| `-v`, `--verbose`           | Increase verbosity (can be used multiple times)                   |
| `--log-level LEVEL`         | Set logging level (`info`, `debug`, `warning`, etc.)              |

**Examples:**

```bash
# See preprocessed DTS
zmk-to-kanata input.zmk --dump-preprocessed

# Save AST to a file
zmk-to-kanata input.zmk --dump-ast ast.json

# See extracted model in YAML
zmk-to-kanata input.zmk --dump-extracted

# Full debug logs and all intermediate outputs
zmk-to-kanata input.zmk --debug --dump-preprocessed --dump-ast --dump-extracted
```

- If a FILE is not specified, output is sent to stdout.
- You can combine multiple dump flags to inspect all stages.
- Use `--debug` or `-v`/`--verbose` for more detailed logs.

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

## FAQ & Troubleshooting

**Q: The converter fails with a 'cpp not found' error.**
A: Install the C preprocessor (`cpp`). On macOS, use `xcode-select --install`;
on Linux, install `build-essential` or `gcc`.

**Q: My ZMK config uses a feature that isn't supported.**
A: See [Known Limitations](docs/known_limitations.md). Unsupported features
require manual adjustment in the Kanata output.

**Q: How do I add custom include paths?**
A: Use the `-I /path/to/includes` flag. See the [User Guide](docs/user_guide.md)
for details.

**Q: Where can I get help or report bugs?**
A: Open an issue on GitHub and include your ZMK config and error message.

**Q: How do I contribute?**
A: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and workflow.

---

For more information, see:
- [User Guide](docs/user_guide.md)
- [API Documentation](docs/api_documentation.md)
- [Testing Guide](docs/testing_guide.md)
- [Known Limitations](docs/known_limitations.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

# ZMK-to-Kanata Feature Support

- ZMK 'caps word' is now supported and mapped to Kanata's `(caps-word 2000)` action.
- Bluetooth and bootloader remain unsupported and are mapped to comments.
