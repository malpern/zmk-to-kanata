# ZMK Parser State Machine Documentation

## Overview

The ZMK to Kanata converter uses a state machine pattern to parse ZMK configuration files. This document explains how the state machine works, its different states, transitions, and error handling mechanisms.

## State Machine Architecture

### Parser Components

```
ZMKParser
├── LayerParser - Handles layer definitions and bindings
├── GlobalSettingsParser - Processes global configuration
├── MacroParser - Handles macro definitions
└── StickyKeyParser - Processes sticky key behaviors
```

### States

1. **INITIAL**
   - Starting state when parser begins
   - Expects root node '/' token
   - Transitions to ROOT_NODE on success

2. **ROOT_NODE**
   - Processes top-level nodes (keymap, macros)
   - Validates basic file structure
   - Transitions to:
     - KEYMAP_NODE for keymap section
     - MACRO_SECTION for macros section

3. **KEYMAP_NODE**
   - Processes keymap configuration
   - Validates 'compatible = "zmk,keymap"'
   - Transitions to LAYER_SECTION for layer definitions

4. **LAYER_SECTION**
   - Handles individual layer definitions
   - Processes layer names and properties
   - Transitions to BINDING_SECTION for layer bindings

5. **BINDING_SECTION**
   - Processes key bindings within layers
   - Handles behavior definitions (&kp, &mt, etc.)
   - Returns to LAYER_SECTION after completion

6. **MACRO_SECTION**
   - Processes macro definitions
   - Handles macro bindings and timing
   - Returns to ROOT_NODE after completion

### State Transitions

```
INITIAL
   │
   ▼
ROOT_NODE ◄────────────┐
   │                   │
   ├─► KEYMAP_NODE    │
   │       │          │
   │       ▼          │
   │   LAYER_SECTION  │
   │       │          │
   │       ▼          │
   │   BINDING_SECTION│
   │                  │
   └─► MACRO_SECTION ─┘
```

## Error Handling

### Recovery Points

The state machine implements strategic recovery points that allow parsing to continue even when errors are encountered:

1. **Layer Recovery**
   - If a layer contains invalid bindings, the parser:
     - Marks the layer as partially valid
     - Continues processing remaining bindings
     - Records errors for reporting

2. **Macro Recovery**
   - For invalid macro definitions:
     - Skips the invalid macro
     - Continues processing other macros
     - Logs the error for reporting

3. **Binding Recovery**
   - When encountering invalid bindings:
     - Replaces with transparent key (_)
     - Continues processing next binding
     - Records the error location

### Error Context

Each error includes:
- Current state
- Line number
- Token that caused the error
- Expected valid tokens
- Suggested fixes when possible

## Validation Rules

### Layer Validation

1. **Structure Validation**
   ```zmk
   layer_name {
       bindings = <...>;
   };
   ```
   - Must have bindings field
   - Must use correct syntax for bindings array

2. **Name Validation**
   - Layer names must be unique
   - Default layer must exist
   - Referenced layers must exist

3. **Binding Validation**
   - Must start with &
   - Must use valid behavior
   - Parameters must match behavior requirements

### Macro Validation

1. **Structure Validation**
   ```zmk
   macro_name: macro_name {
       compatible = "zmk,behavior-macro";
       bindings = <...>;
       wait-ms = <...>;  // Optional
       tap-ms = <...>;   // Optional
   };
   ```
   - Must have compatible field
   - Must have bindings field
   - Timing parameters must be valid numbers

2. **Binding Validation**
   - Must be valid key codes or behaviors
   - Wait/tap times must be reasonable values

## Implementation Details

### State Tracking

```python
class ParserState:
    def __init__(self):
        self.current_state = State.INITIAL
        self.context = {}
        self.errors = []

    def transition(self, new_state):
        if self._is_valid_transition(new_state):
            self.current_state = new_state
            return True
        return False
```

### Error Recording

```python
def record_error(self, error_type, message, line_number):
    self.errors.append({
        'type': error_type,
        'message': message,
        'line': line_number,
        'state': self.current_state
    })
```

## Best Practices

1. **Error Prevention**
   - Validate input before state transitions
   - Maintain clear state boundaries
   - Document expected tokens for each state

2. **Error Recovery**
   - Implement recovery strategies for common errors
   - Provide clear error messages
   - Maintain partial results when possible

3. **State Management**
   - Keep state transitions explicit
   - Validate state invariants
   - Clean up resources on state exit

## Common Issues and Solutions

1. **Missing Closing Brace**
   ```zmk
   default_layer {
       bindings = <
           &kp A &kp B
       >;
   // Missing closing brace
   ```
   - Parser detects unclosed block
   - Reports line number of opening brace
   - Suggests adding closing brace

2. **Invalid Binding Format**
   ```zmk
   bindings = <
       &kp A &kp> B  // Invalid syntax
   >;
   ```
   - Parser identifies invalid token
   - Reports specific syntax error
   - Suggests correct format

3. **Undefined Layer Reference**
   ```zmk
   &mo INVALID_LAYER
   ```
   - Parser detects unknown layer
   - Reports reference location
   - Lists available layer names 