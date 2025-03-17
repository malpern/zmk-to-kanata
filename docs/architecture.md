# ZMK to Kanata Converter Architecture

## High-Level Architecture

The ZMK to Kanata converter is built with a modular architecture that separates concerns and allows for flexible extension. The following diagram shows the high-level architecture:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │     │               │
│   ZMK Input   │ ──> │    Parser     │ ──> │  Transformer  │ ──> │  Kanata Output│
│               │     │               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                            │  ▲
                            │  │
                            ▼  │
                      ┌───────────────┐
                      │               │
                      │ Error Recovery│
                      │               │
                      └───────────────┘
```

## Parser Architecture

The parser has several specialized components:

```
┌─────────────────────────────────────────────────────────┐
│                       ZMKParser                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │              │  │              │  │               │  │
│  │ Layer Parser │  │ Binding      │  │ Global        │  │
│  │              │  │ Parser       │  │ Settings      │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │              │  │              │  │               │  │
│  │ Macro Parser │  │ Sticky Key   │  │ Unicode       │  │
│  │              │  │ Parser       │  │ Parser        │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Binding Parser Integration

The binding parser is a key component that handles complex binding formats:

```
┌─────────────────────────────────────────────────────────┐
│                     BindingParser                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Parse        │  │ Validate     │  │ Convert to    │  │
│  │ Behavior     │  │ Parameters   │  │ Kanata Format │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │                                                  │   │
│  │            Nested Binding Support               │   │
│  │                                                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

The data flow through the system is as follows:

```
┌──────────┐   ┌───────────┐   ┌─────────────────┐   ┌────────────────┐
│ ZMK      │   │ Parsed    │   │ Intermediate    │   │ Kanata         │
│ Keymap   │──>│ State     │──>│ Representation  │──>│ Configuration  │
│ File     │   │ Machine   │   │ (IR)            │   │ File           │
└──────────┘   └───────────┘   └─────────────────┘   └────────────────┘
```

## Error Recovery System

The error recovery system integrates with the parsing process:

```
┌─────────────────────────────────┐
│     ParserErrorRecoveryWrapper  │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────┐        │
│  │ ErrorRecoveryManager│        │
│  └─────────────────────┘        │
│                                 │
│  ┌─────────────────────┐        │
│  │ Error Strategies    │        │
│  │ - Invalid Binding   │        │
│  │ - Invalid Layer     │        │
│  │ - Invalid Macro     │        │
│  └─────────────────────┘        │
│                                 │
└─────────────────────────────────┘
```

## Binding Parser Detail

The binding parser component handles complex binding formats with nested behaviors:

```
┌───────────────────────────────────────────────────────────┐
│                     Parse Binding                          │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│                  Extract Behavior Type                     │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│                Parse Behavior Parameters                   │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
      ┌───────────────────┴───────────────────┐
      │                                       │
      ▼                                       ▼
┌─────────────────────┐             ┌──────────────────────┐
│  Simple Parameter   │             │  Contains Nested     │
│                     │             │  Binding (Parentheses)│
└─────────────────────┘             └──────────────────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │  Recursive Parse     │
                                     │  Nested Binding      │
                                     └──────────────────────┘
```

## Component Interactions

The interaction between components during the parsing of a keymap:

```
┌──────────┐          ┌───────────┐        ┌────────────┐       ┌────────────┐
│          │  parse   │           │ parse  │            │ parse │            │
│ ZMKParser│─────────>│ LayerParser│───────>│BindingParser│──────>│ KeyValidator│
│          │<─────────│           │<───────│            │<──────│            │
└──────────┘  layer   └───────────┘binding └────────────┘ valid └────────────┘
     │         object    objects                key          │
     │                                                       │
     │                                                       │
     ▼                                                       ▼
┌──────────┐                                            ┌────────────┐
│          │                                            │            │
│ErrorManager│<────────────────────────────────────────│ErrorRecovery│
│          │                                            │            │
└──────────┘                                            └────────────┘
     │
     │
     ▼
┌──────────┐
│          │
│Error Report│
│          │
└──────────┘
```

## Transformer Architecture

The transformer system converts the intermediate representation to Kanata:

```
┌─────────────────────────────────────────────────────────┐
│                   KanataTransformer                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │              │  │              │  │               │  │
│  │ Layer        │  │ HoldTap      │  │ Key           │  │
│  │ Transformer  │  │ Transformer  │  │ Transformer   │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │              │  │              │  │               │  │
│  │ Macro        │  │ Settings     │  │ Layout        │  │
│  │ Transformer  │  │ Transformer  │  │ Generator     │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Language**: Python 3.8+
- **Core Libraries**: Standard library (no external dependencies)
- **State Management**: Custom state machine implementation
- **Error Handling**: Context-aware error recovery system
- **Testing**: pytest for unit and integration testing

## Files and Modules

### Parser Module
- `zmk_parser.py`: Main parser implementing the state machine
- `binding_parser.py`: Handles complex binding formats
- `layer_parser.py`: Manages layer parsing
- `macro_parser.py`: Parses macro definitions
- `global_settings_parser.py`: Handles global settings
- `sticky_key_parser.py`: Parses sticky key behaviors
- `unicode_parser.py`: Handles Unicode characters
- `error_recovery_wrapper.py`: Error recovery system

### Transformer Module
- `kanata_transformer.py`: Main transformer
- `holdtap_transformer.py`: Transforms hold-tap behaviors
- `macro_transformer.py`: Transforms macros

### Model Module
- `keymap_model.py`: Intermediate representation classes
- `layer_model.py`: Layer representation

### Other
- `main.py`: Main entry point
- `cli.py`: Command-line interface
- `error_recovery.py`: Error recovery strategies

## File Organization

```
converter/
├── __init__.py
├── main.py
├── cli.py
├── error_recovery.py
├── zmk_to_kanata.py
├── parser/
│   ├── __init__.py
│   ├── zmk_parser.py
│   ├── binding_parser.py
│   ├── layer_parser.py
│   ├── macro_parser.py
│   ├── global_settings_parser.py
│   ├── sticky_key_parser.py
│   ├── unicode_parser.py
│   ├── key_sequence_parser.py
│   └── error_recovery_wrapper.py
├── transformer/
│   ├── __init__.py
│   ├── kanata_transformer.py
│   ├── holdtap_transformer.py
│   └── macro_transformer.py
├── model/
│   ├── __init__.py
│   └── keymap_model.py
├── validation/
│   ├── __init__.py
│   └── key_validator.py
├── output/
│   ├── __init__.py
│   └── file_writer.py
└── tests/
    ├── __init__.py
    ├── unit/
    ├── integration/
    └── performance/
``` 