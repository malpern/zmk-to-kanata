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
└── tests/           # Test suite
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

### Documentation
- [x] User guide
- [x] API documentation
- [x] Example configurations

### Testing
- [x] Unit tests for parsers
- [x] Unit tests for transformers
- [x] Integration tests
- [x] End-to-end tests
  - [x] Task 21: Setup E2E Test Infrastructure
    - [x] Create e2e_tests directory with separate conftest.py
    - [x] Setup test fixtures for file I/O operations
    - [x] Create helper functions for test file generation
    - [x] Add test data validation utilities
    - [x] Implement basic file conversion test
    - [x] Add format verification test
  - [x] Task 22: Basic E2E Test Cases
    - [x] Test CLI interface functionality
    - [x] Test error handling
    - [x] Test output validation
    - [x] Test input formats
  - [x] Task 23: Advanced E2E Test Cases
    - [x] Test multi-layer keymap conversion
    - [x] Test hold-tap configuration conversion
    - [x] Test remaining ZMK features:
      - [x] Sticky keys
      - [x] Key sequences (basic functionality)
      - [x] Macros
      - [x] Unicode input
    - [x] Test error reporting for unsupported features
  - [x] Task 24: Implement Key Sequence Support
    - [x] Key Sequence Behavior Model
    - [x] Key Sequence Parser
    - [x] Key Sequence Transformer
    - [x] Integration
  - [x] Task 25: Real-world E2E Test Cases
    - [x] Test with actual user keymap configurations
      - [x] Create test framework for sample configurations
      - [x] Add tests for QWERTY layout
      - [x] Add tests for Colemak layout
      - [x] Add tests for split keyboards
      - [x] Add tests for homerow mods (with error handling)
      - [x] Add test for Ben Vallack's Cradio layout
      - [x] Validate conversion accuracy with more complex examples
    - [x] Test with various keyboard layouts
      - [x] QWERTY
      - [x] Colemak
      - [x] Dvorak
      - [x] Split keyboards
      - [x] Ergonomic layouts (Kyria)
    - [ ] Test edge cases from user feedback
      - [ ] Add regression tests for fixed issues

## Limitations
- No support for advanced ZMK features like combos
- Limited to standard keyboard layouts
- Focus on common use cases first

## Task 26: Resolve Keymap Model Duplication
- [x] Short-term solution
  - [x] Make the root keymap_model.py re-export from the model directory version
  - [x] Add deprecation warning to the root version
  - [x] Update imports in new code to use the model directory version
- [x] Long-term solution
  - [x] Move all conversion logic to the model directory version
  - [x] Update the HoldTap class in the model directory version
  - [x] Update the KeyMapping class for consistent key mapping
  - [x] Remove duplicate implementations from the root version
  - [x] Update remaining imports to use converter.model.keymap_model directly
  - [ ] Eventually remove the root version once all code is migrated
- [x] Analysis and Implementation
  - [x] Document all current usages of both model versions
  - [x] Identify unique features in each model version
  - [x] Create and implement a migration strategy
  - [x] Ensure all tests pass with the consolidated model

## Task 27: Fix Remaining Linter Errors
- [x] Fix whitespace issues (trailing whitespace, blank lines with whitespace)
- [x] Add missing newlines at the end of files
- [x] Fix unused imports in key files
- [x] Fix spacing between class definitions (E302)
- [x] Fix remaining import issues in non-test files

## Task 28: Implement Macro Support
- [x] Create MacroBehavior class to represent ZMK macro behaviors
- [x] Create MacroBinding class to represent macro bindings
- [x] Create MacroParser to parse ZMK macro definitions
- [x] Update LayerParser to detect and parse macro behaviors
- [x] Add unit tests for macro behavior and parser
- [x] Add end-to-end tests for macro support
- [x] Implement conversion of macro bindings to Kanata format
- [x] Support different activation modes (tap, press, release)
- [x] Support wait times and tap times
- [x] Test with various macro types (basic, parameterized, complex)

## Next Steps
1. Add regression tests for fixed issues (Task 25)
2. Eventually remove the root keymap_model.py once all code is migrated (Task 26)