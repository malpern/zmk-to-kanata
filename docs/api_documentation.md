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
│   └── keymap_model.py     # Keymap data structures
├── output/                 # Output generation
│   ├── __init__.py
│   └── file_writer.py      # File writing utilities
├── parser/                 # Input parsing
│   └── zmk_parser.py       # ZMK file parser
└── transformer/            # Output transformation
    └── kanata_transformer.py  # Kanata output generator
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

This module contains the data models for representing keyboard mappings.

```python
from converter.model.keymap_model import KeymapConfig, Layer, KeyMapping, HoldTap
```

The module provides classes for representing keyboard mappings, layers, and key bindings.

#### KeymapConfig

The `KeymapConfig` class is the top-level container for all keymap data:

```python
@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""
    global_settings: GlobalSettings
    layers: List[Layer]
```

#### GlobalSettings

The `GlobalSettings` class contains global configuration for the keymap:

```python
@dataclass
class GlobalSettings:
    """Global keymap settings."""
    tap_time: int
    hold_time: int
```

#### Layer

The `Layer` class represents a keyboard layer with its key bindings:

```python
@dataclass
class Layer(Binding):
    """Represents a layer with its name and key bindings."""
    name: str
    keys: List[List[KeyMapping]]

    def to_kanata(self) -> str:
        """Convert the layer to Kanata format."""
        # Implementation details...
```

#### KeyMapping

The `KeyMapping` class represents a single key binding:

```python
@dataclass
class KeyMapping(Binding):
    """Represents a single key mapping."""
    key: str  # For basic key press (e.g., "A", "B")
    hold_tap: Optional[HoldTap] = None  # For hold-tap behavior

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        # Implementation details...
```

#### HoldTap

The `HoldTap` class represents a hold-tap key binding:

```python
@dataclass
class HoldTap:
    """Hold-tap key binding."""
    behavior_name: str
    hold_key: str
    tap_key: str

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        # Implementation details...
```

#### HoldTapBinding

The `HoldTapBinding` class represents a more detailed hold-tap binding with additional parameters:

```python
@dataclass(frozen=True)
class HoldTapBinding:
    """Represents a hold-tap binding with its behavior and parameters."""
    behavior_name: str  # e.g., "lh_hm", "rh_hm"
    hold_key: str      # e.g., "LGUI", "LALT"
    tap_key: str       # e.g., "A", "S"
    # Key positions that trigger hold
    hold_trigger_key_positions: Optional[Tuple[int, ...]] = None
    # Whether to trigger hold on key release
    hold_trigger_on_release: bool = False
    # Whether to allow tap on release after hold timeout
    retro_tap: bool = False

    def to_kanata(self) -> str:
        """Convert to Kanata format."""
        # Implementation details...
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
