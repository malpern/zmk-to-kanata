# ZMK to Kanata Converter Development Plan

## Current Status

The parser now successfully handles:
- Basic layer parsing with state machine pattern
- Empty layers and multiline bindings
- Nested layer detection and prevention
- Binding declaration validation
- Global settings parsing with validation
- Clean code organization with separate modules
- Comprehensive test coverage for core features
- Basic and parameterized macro support
- Multi-line settings with proper quote handling
- Macro placeholder bindings

## Remaining Tasks

### 1. Macro Support
- [x] Design MacroParser class
- [x] Implement basic macro parsing
- [x] Add macro validation
- [x] Add tests for macro parsing
- [x] Add support for parameterized macros
- [ ] Add support for macro wait times
- [ ] Add support for macro tap times

### 2. Testing Improvements
- [ ] Add tests for complex binding formats
- [ ] Add tests for error recovery scenarios
- [ ] Add tests for state transition edge cases
- [ ] Document test scenarios
- [ ] Add tests for macro timing configurations

### 3. Documentation
- [ ] Document state machine behavior
- [ ] Add binding format guide
- [ ] Create troubleshooting guide
- [ ] Update architecture diagrams
- [ ] Document macro configuration options

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

## Parser Architecture

```
ZMKParser
├── ParserError - Base error class
├── LayerParser - Handles layer parsing
├── GlobalSettingsParser - Handles settings
├── MacroParser - Handles macros
└── StickyKeyParser - Handles sticky keys
```

### Next Steps

1. **Macro Support**
   - Implement macro timing configurations
   - Add support for complex macro sequences
   - Add validation for timing values
   - Update documentation

2. **Testing Enhancements**
   - Add more edge case tests
   - Improve error messages
   - Add performance tests
   - Document test coverage

3. **Documentation Updates**
   - Document parser state machine
   - Create user guide for macros
   - Add troubleshooting section
   - Update architecture docs