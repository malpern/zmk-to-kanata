# ZMK to Kanata Converter API Documentation

This document provides detailed information about the API of the ZMK to Kanata Converter. It's intended for developers who want to use the converter programmatically or contribute to its development.

## Table of Contents

1. [Module Structure](#module-structure)
2. [Core Classes](#core-classes)
3. [Parser API](#parser-api)
4. [Transformer API](#transformer-api)
5. [Model API](#model-api)
6. [Behaviors API](#behaviors-api)
7. [CLI API](#cli-api)
8. [Examples](#examples)

## Module Structure

The converter is organized into several modules:

```
converter/
├── __init__.py
├── cli.py                  # Command-line interface
├── main.py                 # Main entry point
├── layer_parser.py         # ZMK layer parsing
├── layer_transformer.py    # Layer transformation
├── taphold_parser.py       # Hold-tap behavior parsing
├── behaviors/              # Behavior-specific modules
│   ├── __init__.py
│   ├── key_sequence.py     # Key sequence behavior
│   └── sticky_key.py       # Sticky key behavior
├── model/                  # Data models
│   ├── __init__.py
│   └── keymap_model.py     # Keymap data structures
├── output/                 # Output generation
│   ├── __init__.py
│   └── file_writer.py      # File writing utilities
├── parser/                 # Input parsing
│   ├── __init__.py
│   ├── sticky_key_parser.py # Sticky key parsing
│   └── zmk_parser.py       # ZMK file parsing
└── transformer/            # Output transformation
    ├── __init__.py
    ├── holdtap_transformer.py # Hold-tap transformation
    └── kanata_transformer.py  # Kanata output generation
```

## Core Classes

### `main.py`

The main entry point for the converter.

#### `main()`

The main function that orchestrates the conversion process.

**Parameters**: None (uses `sys.argv`)

**Returns**: Exit code (0 for success, non-zero for failure)

**Example**:

```python
from converter.main import main

# Run the converter with command-line arguments
exit_code = main()
```

### `cli.py`

Command-line interface for the converter.

#### `parse_args(args)`

Parse command-line arguments.

**Parameters**:
- `args` (list): Command-line arguments

**Returns**: Parsed arguments object

**Example**:

```python
from converter.cli import parse_args

# Parse custom arguments
args = parse_args(['input.dtsi', 'output.kbd', '--verbose'])
```

## Parser API

### `layer_parser.py`

#### `parse_zmk_file(file_path)`

Parse a ZMK file and extract the keymap configuration.

**Parameters**:
- `file_path` (str): Path to the ZMK file

**Returns**: `KeymapConfig` object

**Example**:

```python
from converter.layer_parser import parse_zmk_file

# Parse a ZMK file
keymap = parse_zmk_file('input.dtsi')
```

#### `extract_keymap(content)`

Extract the keymap configuration from ZMK file content.

**Parameters**:
- `content` (str): ZMK file content

**Returns**: `KeymapConfig` object

**Example**:

```python
from converter.layer_parser import extract_keymap

# Parse ZMK content
with open('input.dtsi', 'r') as f:
    content = f.read()
keymap = extract_keymap(content)
```

### `parser/zmk_parser.py`

#### `parse_zmk_content(content)`

Parse ZMK content and extract the keymap configuration.

**Parameters**:
- `content` (str): ZMK file content

**Returns**: `KeymapConfig` object

**Example**:

```python
from converter.parser.zmk_parser import parse_zmk_content

# Parse ZMK content
with open('input.dtsi', 'r') as f:
    content = f.read()
keymap = parse_zmk_content(content)
```

## Transformer API

### `layer_transformer.py`

#### `transform_layers(layers)`

Transform ZMK layers into Kanata layers.

**Parameters**:
- `layers` (list): List of `Layer` objects

**Returns**: List of transformed layers

**Example**:

```python
from converter.layer_transformer import transform_layers

# Transform layers
kanata_layers = transform_layers(keymap.layers)
```

### `transformer/kanata_transformer.py`

#### `generate_kanata_config(keymap)`

Generate a Kanata configuration from a keymap.

**Parameters**:
- `keymap` (KeymapConfig): Keymap configuration

**Returns**: Kanata configuration string

**Example**:

```python
from converter.transformer.kanata_transformer import generate_kanata_config

# Generate Kanata configuration
kanata_config = generate_kanata_config(keymap)
```

## Model API

### `model/keymap_model.py`

#### `KeymapConfig`

Class representing a complete keymap configuration.

**Attributes**:
- `global_settings` (GlobalSettings): Global settings
- `layers` (list): List of `Layer` objects

**Methods**:
- `add_layer(layer)`: Add a layer to the configuration
- `get_layer_by_name(name)`: Get a layer by name

**Example**:

```python
from converter.model.keymap_model import KeymapConfig, Layer

# Create a keymap configuration
keymap = KeymapConfig()
layer = Layer(name="default")
keymap.add_layer(layer)
```

#### `Layer`

Class representing a keyboard layer.

**Attributes**:
- `name` (str): Layer name
- `bindings` (list): List of `KeyMapping` objects

**Methods**:
- `add_binding(binding)`: Add a binding to the layer
- `get_binding_at(row, col)`: Get a binding at a specific position

**Example**:

```python
from converter.model.keymap_model import Layer, KeyMapping

# Create a layer
layer = Layer(name="default")
binding = KeyMapping(key="A")
layer.add_binding(binding)
```

#### `KeyMapping`

Class representing a key mapping.

**Attributes**:
- `key` (str): Key name
- `modifiers` (list): List of modifiers
- `layer` (int): Layer number (for layer switching)
- `behavior` (str): Behavior name

**Methods**:
- `is_transparent()`: Check if the mapping is transparent
- `is_layer_switch()`: Check if the mapping is a layer switch
- `to_kanata()`: Convert to Kanata format

**Example**:

```python
from converter.model.keymap_model import KeyMapping

# Create a key mapping
mapping = KeyMapping(key="A", modifiers=["LSHIFT"])
```

## Behaviors API

### `behaviors/key_sequence.py`

#### `KeySequenceBehavior`

Class representing a key sequence behavior.

**Attributes**:
- `wait_ms` (int): Wait time in milliseconds
- `tap_ms` (int): Tap time in milliseconds
- `bindings` (list): List of key bindings

**Methods**:
- `to_kanata()`: Convert to Kanata format

**Example**:

```python
from converter.behaviors.key_sequence import KeySequenceBehavior

# Create a key sequence behavior
sequence = KeySequenceBehavior(wait_ms=100, tap_ms=50, bindings=["A", "B", "C"])
```

### `behaviors/sticky_key.py`

#### `StickyKeyBehavior`

Class representing a sticky key behavior.

**Attributes**:
- `key` (str): Key name
- `release_after_ms` (int): Release time in milliseconds

**Methods**:
- `to_kanata()`: Convert to Kanata format

**Example**:

```python
from converter.behaviors.sticky_key import StickyKeyBehavior

# Create a sticky key behavior
sticky = StickyKeyBehavior(key="LSHIFT", release_after_ms=1000)
```

## CLI API

### `cli.py`

#### `main()`

The main CLI entry point.

**Parameters**: None (uses `sys.argv`)

**Returns**: Exit code (0 for success, non-zero for failure)

**Example**:

```python
from converter.cli import main

# Run the CLI
exit_code = main()
```

## Examples

### Basic Conversion

```python
from converter.layer_parser import parse_zmk_file
from converter.transformer.kanata_transformer import generate_kanata_config
from converter.output.file_writer import write_kanata_file

# Parse ZMK file
keymap = parse_zmk_file('input.dtsi')

# Generate Kanata configuration
kanata_config = generate_kanata_config(keymap)

# Write to file
write_kanata_file(kanata_config, 'output.kbd')
```

### Custom Transformation

```python
from converter.layer_parser import parse_zmk_file
from converter.layer_transformer import transform_layers
from converter.transformer.kanata_transformer import generate_kanata_config
from converter.output.file_writer import write_kanata_file

# Parse ZMK file
keymap = parse_zmk_file('input.dtsi')

# Custom transformation
for layer in keymap.layers:
    for binding in layer.bindings:
        if binding.key == "A":
            binding.key = "B"  # Replace all A keys with B

# Transform layers
kanata_layers = transform_layers(keymap.layers)

# Generate Kanata configuration
kanata_config = generate_kanata_config(keymap)

# Write to file
write_kanata_file(kanata_config, 'output.kbd')
```

### Programmatic Usage

```python
from converter.model.keymap_model import KeymapConfig, Layer, KeyMapping
from converter.transformer.kanata_transformer import generate_kanata_config
from converter.output.file_writer import write_kanata_file

# Create a keymap programmatically
keymap = KeymapConfig()

# Create default layer
default_layer = Layer(name="default")
default_layer.add_binding(KeyMapping(key="A"))
default_layer.add_binding(KeyMapping(key="B"))
default_layer.add_binding(KeyMapping(key="C"))

# Add layer to keymap
keymap.add_layer(default_layer)

# Generate Kanata configuration
kanata_config = generate_kanata_config(keymap)

# Write to file
write_kanata_file(kanata_config, 'output.kbd')
```

For more examples, see the [examples](../examples) directory. 