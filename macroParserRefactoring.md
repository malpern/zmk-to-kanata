# Macro Parser Refactoring: Detailed Planning Document

> **Progress Tracking:** Each task has a checkbox. Mark tasks as complete by changing `[ ]` to `[x]`. Current status is visible at the bottom of this document.

## 1. Current State Analysis

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

## 4. Implementation Steps

### 4.1 Foundation & Infrastructure
- [x] Create skeleton for new ZMKMacroParser class
- [x] Add MacroDefinition and MacroUsage data models
- [x] Integrate with ErrorManager for centralized error handling
- [x] Set up logging and validation infrastructure

### 4.2 MacroDefinitionParser Implementation
- [x] Implement parse_macro_definition() to handle the overall structure
- [x] Add process_macro_steps() to parse individual macro steps
- [x] Implement state management for macro definition parsing
- [x] Add validation logic for macro definitions

> **Note:**
> Macro definition parsing, step parsing, state management, and validation logic are all implemented and active. Validation and error handling use the centralized ErrorManager, and all macro definitions and steps are validated after parsing. No validation work has been lost during refactoring.

### 4.3 MacroUsageParser Implementation
- [x] Define MacroUsage data contract (dataclass)
- [x] Add extract_parameters() to handle complex parameters
- [x] Implement parse_macro_usage() for macro usage in bindings
- [x] Implement state management for macro usage parsing
- [x] Add validation logic for macro usages

> **Note:**
> Macro usage parsing, parameter extraction, state management, and validation are all implemented and integrated. The parser now robustly handles macro usages with error recovery and centralized error reporting.

### 4.4 MacroTransformer Updates
- [ ] Update transform_behavior() to handle MacroDefinition objects
- [ ] Update transform_binding() to handle MacroUsage objects
- [ ] Ensure output validation and debug logging
- [ ] Add recovery mechanisms for invalid inputs

### 4.5 Integration & Testing
- [ ] Update existing tests to use new parser infrastructure
- [ ] Enable skipped tests as functionality is implemented
- [ ] Add tests for edge cases and error handling
- [ ] Validate output against Kanata specifications

## 5. Testing Strategy

### 5.1 Unit Tests
- [ ] Test each parser component in isolation
- [ ] Test state transitions and error recovery
- [ ] Test parameter extraction and validation
- [ ] Test transformation logic

### 5.2 Integration Tests
- [ ] Test parsing and transformation pipeline as a whole
- [ ] Test with real-world and edge case inputs
- [ ] Test error aggregation and reporting

### 5.3 Regression Tests
- [ ] Ensure previously working functionality remains intact
- [ ] Validate output format consistency
- [ ] Confirm error handling across the pipeline

## 6. Detailed Implementation Schedule

### Phase 1: Foundation (Days 1-2)
- [ ] Create ZMKMacroParser class skeleton
- [ ] Define MacroDefinition and MacroUsage data models
- [ ] Set up ErrorManager integration
- [ ] Implement basic logging and validation

### Phase 2: Definition Parsing (Days 3-5)
- [ ] Implement parse_macro_definition()
- [ ] Add state management for definition parsing
- [ ] Implement process_macro_steps()
- [ ] Add validation for macro definitions

### Phase 3: Usage Parsing (Days 6-7)
- [ ] Implement parse_macro_usage()
- [ ] Add state management for usage parsing
- [ ] Implement extract_parameters()
- [ ] Add validation for macro usages

### Phase 4: Transformer Updates (Days 8-9)
- [ ] Update transform_behavior() for definitions
- [ ] Update transform_binding() for usages
- [ ] Implement output validation
- [ ] Add recovery mechanisms

### Phase 5: Testing & Integration (Days 10-12)
- [ ] Update existing tests
- [ ] Enable skipped tests
- [ ] Add edge case and error handling tests
- [ ] Validate against Kanata specifications

## 7. Success Criteria

### 7.1 Functional Criteria
- [ ] All previously skipped macro tests now pass
- [ ] Complex macros are correctly parsed and transformed
- [ ] Nested structures are properly handled
- [ ] Error recovery works for invalid inputs

### 7.2 Quality Criteria
- [ ] Clean separation of concerns in architecture
- [ ] Comprehensive error context and reporting
- [ ] Robust state management with clear transitions
- [ ] Consistent with the rest of the pipeline's architecture

### 7.3 Performance Criteria
- [ ] No significant performance regression
- [ ] Maintain or improve memory usage
- [ ] Suitable for large configuration files

## 8. Risks & Mitigation

### 8.1 Identified Risks
- **Token-based parsing complexity**: May be harder than anticipated
- **Edge case coverage**: Difficult to anticipate all macro formats
- **Integration challenges**: Changes may impact other parts of the system
- **Test expectations**: Existing tests may have incorrect expectations

### 8.2 Mitigation Strategies
- **Start simple**: Implement core functionality first, then add complexity
- **Progressive testing**: Test each component as it's developed
- **Maintain backward compatibility**: Ensure existing valid inputs still work
- **Regular code reviews**: Get feedback on design and implementation

## 9. Dependencies & Constraints

### 9.1 Dependencies
- Existing ErrorManager for error handling
- Token-based lexer for input processing
- AST models for output representation

### 9.2 Constraints
- Must maintain compatibility with existing pipeline
- Must handle all valid ZMK macro formats
- Must produce valid Kanata output
- Must integrate with existing error reporting system

---

## Progress Summary

### Overall Progress
- [x] Foundation & Infrastructure (4/4)
- [x] MacroDefinitionParser Implementation (4/4)
- [x] MacroUsageParser Implementation (5/5)
- [ ] MacroTransformer Updates (0/4)
- [ ] Integration & Testing (0/4)
- [ ] Unit Tests (0/4)
- [ ] Integration Tests (0/3)
- [ ] Regression Tests (0/3)
- [ ] Success Criteria (0/10)

### Current Phase
- [x] Phase 1: Foundation (4/4) 