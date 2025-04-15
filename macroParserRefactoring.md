# Macro Parser Refactoring: Existing Issues, Design, and Progress Checklist

### 1.1 Existing Issues
- **Line-based vs. Token-based**: Current parser processes macros line-by-line instead of token-by-token
- **Lack of State Management**: Inconsistent transitions between parsing blocks, macros, and bindings
- **Parameter Parsing Flaws**: Simplistic string splitting fails on complex parameters
- **Error Handling Weaknesses**: Inconsistent error reporting without context
- **Mixed Responsibilities**: Definition parsing and usage parsing are not clearly separated

### 1.2 Impact Areas
- **Test Coverage**: Multiple skipped tests in the macro parser area
- **Edge Cases**: Nested macros, multi-line definitions, complex parameters
- **Error Reporting**: Insufficient context in error messages
- **Downstream Effects**: Impacts macro transformer and Kanata output

## 2. Design Goals & Principles

### 2.1 Core Goals
- **Robust Parsing**: Handle complex, multi-line, and nested macros
- **Clean Separation**: Distinguish macro definition parsing from usage parsing
- **Error Recovery**: Recover gracefully from parsing errors
- **Consistency**: Align with the rest of the pipeline's architecture
- **Testability**: Enable comprehensive test coverage

### 2.2 Design Principles
- **Token-based Parsing**: Process token stream instead of lines
- **Single Responsibility**: Each component has one focused task
- **Clear State Transitions**: Well-defined and logged state changes
- **Centralized Error Handling**: Leverage the existing error manager
- **Defensive Programming**: Validate inputs and handle edge cases

## 3. New Architecture Overview

### 3.1 Component Structure
```
ZMKMacroParser
├── MacroDefinitionParser
│   ├── parse_macro_definition()
│   └── process_macro_steps()
└── MacroUsageParser
    ├── parse_macro_usage()
    └── extract_parameters()

MacroTransformer
├── transform_definition()
└── transform_usage()
```

### 3.2 Data Flow
1. **Token Stream** → ZMKMacroParser
2. **MacroDefinition Objects** → MacroTransformer.transform_definition()
3. **MacroUsage Objects** → MacroTransformer.transform_usage()
4. **Kanata S-expressions** → Output

### 3.3 Error Handling Strategy
- Errors collected via centralized ErrorManager
- Each error includes context (file, line, token position)
- Recovery points defined for resuming parsing after errors

---

## Macro Parser & Transformer Refactor Checklist

### Foundation & Infrastructure
- [x] Create ZMKMacroParser class skeleton
- [x] Define MacroDefinition and MacroUsage data models
- [x] Integrate with ErrorManager for centralized error handling
- [x] Set up logging and validation infrastructure

### Macro Definition Parsing
- [x] Implement parse_macro_definition() to handle macro structure
- [x] Add process_macro_steps() to parse individual macro steps
- [x] Implement state management for macro definition parsing
- [x] Add validation logic for macro definitions

### Macro Usage Parsing
- [x] Define MacroUsage data contract (dataclass)
- [x] Add extract_parameters() to handle complex parameters
- [x] Implement parse_macro_usage() for macro usage in bindings
- [x] Implement state management for macro usage parsing
- [x] Add validation logic for macro usages

### Macro Transformer Updates
- [x] Implement transform_definition() for MacroDefinition objects
- [x] Implement transform_usage() for MacroUsage objects
- [x] Ensure output validation and debug logging
- [x] Add recovery mechanisms for invalid macro inputs
- [x] Remove/deprecate old transform_behavior/transform_binding methods and usages

### Integration & Testing
- [x] Update macro transformer tests to use new MacroDefinition, MacroStep, and MacroUsage contracts (all passing)
- [x] Update sticky key transformer tests to use new contract (all passing)
- [x] Update homerow mod transformer and behavior tests to use new contract (all passing)
- [ ] Update remaining tests (integration/e2e) to use new parser infrastructure
- [ ] Enable skipped tests as functionality is implemented
- [ ] Add tests for edge cases and error handling
- [ ] Validate output against Kanata specifications

---

> This checklist is the single source of truth for macro parser/transformer refactor progress. 