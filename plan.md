# ZMK to Kanata Converter Project Plan

## Overview
Convert ZMK keymap configurations to Kanata format, enabling users to migrate their keyboard configurations between these firmware options.

## Implementation Approach
Using a modular design with clear separation between parsing, model representation, and output generation.

## Key Concerns
- Maintain feature parity where possible
- Provide clear error messages for unsupported features
- Generate clean, readable Kanata output
- Follow Python best practices and maintain code quality

## Environment
- Python 3.8+
- pytest for testing
- Black for code formatting
- flake8 for linting

## Folder Structure
```
converter/
├── __init__.py
├── model/           # Data models
├── parser/          # Input parsing
├── transformer/     # Output generation
├── samples/         # Example files
└── tests/          # Test suite
```

## Implementation Checklist

### Core Infrastructure
- [x] Project structure setup
- [x] Basic test framework
- [x] Sample ZMK files
- [x] CI/CD pipeline

### Basic Features
- [x] Parse basic key definitions
- [x] Handle layer declarations
- [x] Support basic modifiers
- [x] Generate Kanata output
- [x] Command-line interface

### Advanced Features
- [x] Task 19: Integrate hold-tap behaviors with keymap parsing
  - [x] Add HoldTapBinding class to model
  - [x] Update KeyMapping to support hold-tap
  - [x] Enhance LayerParser for hold-tap bindings
  - [x] Add comprehensive tests
  - [x] Support for advanced hold-tap features:
    - [x] hold-trigger-key-positions
    - [x] hold-trigger-on-release
    - [x] retro-tap

- [x] Task 20: Implement translation to Kanata tap-hold syntax
  - [x] Create HoldTapTransformer
  - [x] Add support for different tap-hold variants
  - [x] Update KanataTransformer
  - [x] Add comprehensive tests for all hold-tap variants
  - [x] Fix linter errors and improve code formatting
    - [x] Fix holdtap_transformer.py
    - [x] Fix kanata_transformer.py
    - [x] Fix test_holdtap_transformer.py
    - [x] Fix keymap_model.py
    - [x] Verify all tests pass after formatting

### Documentation
- [ ] User guide
- [ ] API documentation
- [ ] Example configurations

### Testing
- [x] Unit tests for parsers
- [x] Unit tests for transformers
- [x] Integration tests
- [ ] End-to-end tests
  - [x] Task 21: Setup E2E Test Infrastructure
    - [x] Create e2e_tests directory with separate conftest.py
    - [x] Setup test fixtures for file I/O operations
    - [x] Create helper functions for test file generation
    - [x] Add test data validation utilities
    - [x] Implement basic file conversion test
    - [x] Add format verification test
  - [ ] Task 22: Basic E2E Test Cases
    - [ ] Test CLI interface functionality
      - [ ] Test help command
      - [ ] Test version command
      - [ ] Test basic file conversion command
    - [ ] Test error handling
      - [ ] Invalid input file path
      - [ ] Invalid input file format
      - [ ] Invalid output file path
      - [ ] Permission errors
    - [ ] Test output validation
      - [ ] Verify file permissions
      - [ ] Verify file encoding
      - [ ] Verify file format
    - [ ] Test with different input formats
      - [ ] Single layer keymap
      - [ ] Multiple layer keymap
      - [ ] Empty layers
      - [ ] Comments and whitespace handling
  - [ ] Task 23: Advanced E2E Test Cases
    - [ ] Test multi-layer keymap conversion
    - [ ] Test hold-tap configuration conversion
    - [ ] Test all supported ZMK features
    - [ ] Test error reporting for unsupported features
  - [ ] Task 24: Real-world E2E Test Cases
    - [ ] Test with actual user keymap configurations
    - [ ] Test with various keyboard layouts
    - [ ] Test edge cases from user feedback
    - [ ] Document test coverage and limitations
- [ ] Performance benchmarks

## Limitations
- No support for advanced ZMK features like combos
- Limited to standard keyboard layouts
- Focus on common use cases first