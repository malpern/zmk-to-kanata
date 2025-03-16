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
  - [x] Task 22: Basic E2E Test Cases
    - [x] Test CLI interface functionality
      - [x] Test help command
      - [x] Test version command
      - [x] Test basic file conversion command
    - [x] Test error handling
      - [x] Invalid input file path
      - [x] Invalid input file format
      - [x] Invalid output file path
      - [x] Permission errors
    - [x] Test output validation
      - [x] Verify file permissions
      - [x] Verify file encoding
      - [x] Verify output format
    - [x] Test input formats
      - [x] Single layer keymap
      - [x] Multiple layer keymap
      - [x] Empty layer keymap
      - [x] Comments and whitespace handling
  - [ ] Task 23: Advanced E2E Test Cases
    - [x] Test multi-layer keymap conversion
    - [x] Test hold-tap configuration conversion
    - [x] Test remaining ZMK features:
      - [x] Sticky keys
      - [ ] Key sequences
      - [ ] Macros
      - [ ] Unicode input
    - [x] Test error reporting for unsupported features
  - [ ] Task 24: Real-world E2E Test Cases
    - [ ] Test with actual user keymap configurations
      - [ ] Collect sample configurations from ZMK users
      - [ ] Create test suite for each sample config
      - [ ] Validate conversion accuracy
    - [ ] Test with various keyboard layouts
      - [ ] QWERTY
      - [ ] Dvorak
      - [ ] Colemak
      - [ ] Split keyboards
      - [ ] Ergonomic layouts
    - [ ] Test edge cases from user feedback
      - [ ] Create issue tracking system for user-reported cases
      - [ ] Add regression tests for fixed issues
    - [ ] Document test coverage and limitations
      - [ ] Generate coverage reports
      - [ ] Document known limitations
      - [ ] Create testing guide for contributors
- [ ] Performance benchmarks
  - [ ] Measure conversion speed for different file sizes
  - [ ] Profile memory usage
  - [ ] Establish performance baselines
  - [ ] Document performance recommendations

## Limitations
- No support for advanced ZMK features like combos
- Limited to standard keyboard layouts
- Focus on common use cases first

## Next Steps
1. Complete remaining ZMK features in Task 23 (key sequences, macros, Unicode input)
2. Begin collecting real-world configurations for testing (Task 24)
3. Start documentation tasks
4. Implement performance benchmarking

## Recent Progress
- Added proper error handling for invalid input format and output paths
- Fixed hold-tap bindings to include behavior_name attribute
- Added sticky key support with comprehensive tests
- Updated layer parser to handle optional _layer suffix
- All current tests passing (63/63)
- Improved error reporting and exit codes for CLI
- Enhanced code organization with new modules for behaviors and parsers