# Binding Parser Documentation

## Overview

The Binding Parser is a critical component of the ZMK to Kanata converter that handles parsing of complex ZMK binding formats. It supports various binding types including basic key bindings, layer management bindings, and nested bindings.

## Supported Binding Types

### Basic Bindings

- **Key Press (`&kp`)**: Basic key press bindings
  ```
  &kp A       -> A
  &kp SPACE   -> spc
  &kp LSHIFT  -> lsft
  ```

### Layer Management Bindings

- **Momentary Layer (`&mo`)**: Activates a layer while held
  ```
  &mo 1       -> mo(1)
  ```

- **Toggle Layer (`&tog`)**: Toggles a layer on/off
  ```
  &tog 2      -> tog(2)
  ```

- **To Layer (`&to`)**: Switches to a specific layer
  ```
  &to 3       -> to(3)
  ```

### Special Bindings

- **Layer-Tap (`&lt`)**: Key when tapped, layer when held
  ```
  &lt 1 A     -> lt(1,A)
  ```

- **Mod-Tap (`&mt`)**: Modifier when held, key when tapped
  ```
  &mt LSHIFT A -> mt(lsft,A)
  ```

- **Sticky Key (`&sk`)**: Key remains active until another key is pressed
  ```
  &sk LSHIFT  -> sk(lsft)
  ```

### Nested Bindings

The binding parser also supports nested bindings (bindings within bindings):

```
&lt 1 (&kp A)             -> lt(1,A)
&mt LSHIFT (&kp B)        -> mt(lsft,B)
&lt 2 (&mt LCTRL C)       -> lt(2,mt(lctrl,C))
```

## Binding Components

Each binding consists of:

1. **Behavior**: The binding type (e.g., `kp`, `lt`, `mt`)
2. **Parameters**: The arguments (e.g., layer number, key code)
3. **Optional Nested Binding**: A binding that is wrapped by another binding

## Parsing Process

1. The parser identifies the binding behavior (e.g., `&kp`, `&lt`, `&mt`)
2. It extracts parameters based on the binding type
3. If parentheses are present, it recursively parses the nested binding
4. It validates the binding structure and parameters
5. It converts the parsed binding to Kanata format

## Error Handling

The binding parser includes robust error handling to manage invalid bindings:

- **Invalid Behavior**: Behaviors not recognized are flagged
- **Parameter Validation**: Parameters are validated against expected types
- **Nested Binding Validation**: Nested structures are checked for validity

When errors are encountered, the parser:
1. Logs detailed error information
2. Returns fallback values where possible
3. Provides context for the error location

## Integration with ZMK Parser

The binding parser is integrated with the main ZMK parser:

```python
from converter.parser.binding_parser import BindingParser

class ZMKParser:
    def __init__(self):
        self.binding_parser = BindingParser()
    
    def _parse_binding_line(self, line):
        # Extract binding text from line
        binding_text = self._extract_binding_text(line)
        
        # Parse using binding parser
        try:
            binding = self.binding_parser.parse(binding_text)
            return binding
        except BindingParseError as e:
            # Handle errors
            self.error_manager.report_error(...)
            return fallback_binding
```

## Best Practices

When extending the binding parser:

1. **Add New Behaviors**: Follow the pattern in `_parse_behavior_specific_parameters()`
2. **Extend Validation**: Add validation in appropriate methods
3. **Error Context**: Always include detailed context in error messages
4. **Fallback Values**: Provide sensible fallbacks for invalid bindings

## Examples

### Basic Usage

```python
parser = BindingParser()
result = parser.parse("&kp A")
# Returns a binding with key="A"
```

### Complex Bindings

```python
parser = BindingParser()
result = parser.parse("&lt 1 (&mt LSHIFT B)")
# Returns a binding with key="lt(1,mt(lsft,B))"
```

### Error Recovery

```python
try:
    parser = BindingParser()
    result = parser.parse("&invalid_binding A")
except BindingParseError as e:
    # Handle error
    print(f"Error parsing binding: {e}")
    # Use fallback
    result = create_fallback_binding()
```

## Performance Considerations

The binding parser is optimized for typical ZMK keymaps:

- It uses efficient string parsing techniques
- It minimizes memory allocations
- It handles nested structures without excessive recursion

For very large keymaps (hundreds of keys), parsing performance should remain reasonable. 