# ZMK to Kanata Converter Development Plan

## Current Status

The parser now successfully handles:
- Basic layer parsing with state machine pattern
- Empty layers and multiline bindings
- Nested layer detection and prevention
- Binding declaration validation
- Clean code with no linter errors

## Remaining Tasks

### 1. Global Settings Parser
- [ ] Create GlobalSettingsParser class
- [ ] Support tap-time and hold-time settings
- [ ] Add validation for setting values
- [ ] Add tests for global settings

### 2. Macro Support
- [ ] Design MacroParser class
- [ ] Implement basic macro parsing
- [ ] Add macro validation
- [ ] Add tests for macro parsing

### 3. Testing Improvements
- [ ] Add tests for complex binding formats
- [ ] Add tests for error recovery scenarios
- [ ] Add tests for state transition edge cases
- [ ] Document test scenarios

### 4. Documentation
- [ ] Document state machine behavior
- [ ] Add binding format guide
- [ ] Create troubleshooting guide
- [ ] Update architecture diagrams

## Development Guidelines

1. **Code Changes**
   - Make small, focused changes
   - Add tests for new features
   - Keep existing functionality working

2. **Error Handling**
   - Include context (line numbers, file names)
   - Maintain consistent error format
   - Suggest fixes where possible

3. **Testing**
   - Test both success and failure cases
   - Include edge cases
   - Document test purpose


## Updated Parser Architecture

```
ZMKCompiler
├── Lexer - Tokenizes input
├── Parser - Builds AST
│   ├── LayerParser
│   ├── BindingParser
│   └── MacroParser
├── SemanticAnalyzer - Validates semantics
├── SymbolTable - Manages symbols
└── KanataGenerator - Generates output
```

### Implementation Phases

1. **Phase 1: Lexical Analysis**
   - [ ] Define token types
   - [ ] Implement lexer
   - [ ] Add token stream tests

2. **Phase 2: Parsing**
   - [ ] Define grammar rules
   - [ ] Implement recursive descent parser
   - [ ] Build AST
   - [ ] Add parser tests

3. **Phase 3: Semantic Analysis**
   - [ ] Implement symbol table
   - [ ] Add reference resolution
   - [ ] Validate layer references
   - [ ] Add semantic tests

4. **Phase 4: Code Generation**
   - [ ] Implement visitor pattern
   - [ ] Add Kanata output generation
   - [ ] Add transformation tests

### Migration Strategy

1. **Gradual Migration**
   - Keep current implementation working
   - Add new components alongside existing code
   - Switch components one at a time
   - Run both parsers in parallel for validation

2. **Testing Strategy**
   - Add tests for new components
   - Verify identical output between implementations
   - Maintain backward compatibility
   - Add performance benchmarks