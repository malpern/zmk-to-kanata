# ZMK to Kanata Converter Implementation Plan

> **Note:** Checkmarks (✅) in the plan below indicate completed major steps. For detailed status and sub-steps, see the progress tracker table at the end of this document. Only update checkmarks at the step (macro) level, not on individual sub-bullets.

## Current Status (May 2025)

The converter is in progress with ongoing work on macro handling and test coverage. Current status:

- ✅ Macro transformer implementation fixed
- ✅ Test coverage for macro transformer improved
- ✅ Error handling and validation improved
- ✅ Macro parser error recovery fixed
- ✅ Basic macro tests passing (all parser error recovery tests pass except for one edge case: missing semicolon)
- ✅ Code formatting standardized with Black
- ✅ Transformer output formats standardized
- ✅ Line length and docstring formatting fixed
- ✅ Parser error messages standardized

## Detailed Progress Update (June 2025)

### Recent Fixes
1. Macro Parser Improvements:
   - Fixed infinite loop in error recovery
   - Improved error message consistency
   - Added proper error context in messages
   - Fixed test_error_recovery_with_context test
   - Standardized error message format
   - Added proper error propagation
   - Fixed bindings parsing in macro settings
   - Added support for invalid command detection
   - Fixed basic and complex macro tests
   - Improved error recovery state handling
   - Fixed line length and docstring formatting issues
   - Standardized parser error messages with rich context

2. Test Coverage:
   - 8/19 macro parser and transformer tests passing
   - Added validation for macro step parameters
   - Improved error message consistency
   - Fixed test assertions for error messages
   - Added proper error context in test cases
   - Added tests for basic and complex macros
   - Added advanced macro transformer tests

3. Code Quality:
   - Set up Black formatter with 79-character line length
   - Added pre-commit hooks for automatic formatting
   - Fixed line length issues across codebase
   - Standardized code formatting
   - Standardized transformer output formats
   - Fixed docstring formatting and line length issues

### Current Issues
1. Macro Parser:
   ✅ Error messages standardized with consistent formatting
   ✅ Added rich context information to error messages
   ✅ Improved error recovery and position tracking
   ✅ Fixed docstring formatting and line length issues
   ✅ All macro parser error recovery tests now pass, including the missing semicolon edge case

2. Error Handling:
   ✅ Fix error message formatting in _check_for_errors
   ✅ Added clear synchronization between parser states
   ✅ Enhanced error messages with better context information

3. Testing:
   ✅ All macro parser and transformer unit tests passing
   Integration tests need updates for new parser and transformer behavior
   Need more test cases for error recovery scenarios
   Advanced macro transformer tests added and passing

### Next Steps
1. Fix integration tests (next priority)
   - Ensure parser and transformer work together in end-to-end scenarios
   - Address any integration failures or output inconsistencies
   - Add or update integration test cases for real-world macro usage

2. Documentation:
   - Update macro parser documentation
   - Add error handling guidelines
   - Document token type requirements
   - Add examples for common macro usage patterns
   - Document error recovery strategies

## Project Goals

1. Convert ZMK keymap files to Kanata configuration
2. Support all ZMK features including:
   - Layers
   - Macros
   - Combos
   - Hold-tap behaviors
3. Provide clear error messages and validation
4. Maintain high test coverage

## Implementation Plan

### 1. Core Architecture ✅
- [x] Define clear data contracts
- [x] Implement modular design
- [x] Set up testing framework

### 2. Parser Implementation ⏳
- [x] Basic keymap parsing
- [x] Layer parsing
- [⏳] Macro parsing with validation (needs fixes)
- [x] Combo parsing
- [x] Hold-tap behavior parsing

### 3. Transformer Implementation ⏳
- [x] Key sequence transformation
- [x] Layer transformation
- [⏳] Macro transformation (needs fixes)
- [x] Combo transformation
- [x] Hold-tap transformation

### 4. Validation and Error Handling ⏳
- [x] Key validation
- [x] Layer validation
- [⏳] Macro validation (needs fixes)
- [⏳] Error recovery (needs improvements)
- [x] Clear error messages

### 5. Testing and Documentation ⏳
- [⏳] Unit tests (69/208 passing)
- [⏳] Integration tests
- [⏳] Documentation
- [⏳] Examples

## Next Steps

1. Fix integration tests
2. Address parser validation issues
3. Standardize transformer output formats
4. Improve error handling and recovery
5. Complete test coverage

# Unified Implementation Plan (April 2025)

### 1. Clarify and Enforce Data Contracts ✅
- Define and document what a "binding" and "layer" should be (use classes, not dicts).
- Add assertions/type checks after parsing bindings and layers.
- Update the parser and binding parser to always return the correct object types for hold-tap, mod-tap, and other behaviors.

### 2. Fix Layer Addition and State Transitions ✅ Complete
- Debug logging is present for layer start, finish, and addition.
- Every parsed layer is finalized and appended to the keymap.
- There are assertions and tests to ensure that for valid files, at least one layer is present after parsing.
- Edge cases and malformed input are handled gracefully with clear errors.

### 3. Key Validation and Filtering ✅
- Filter out non-key tokens (e.g., braces, comments) before passing to the model.
- Ensure each binding is validated before being added to a layer.

### 4. Transformer Standardization ⏳
- Update all transformers to follow standardized output format.
- Ensure consistent structure for all transformers.
- Implement proper handling of nested bindings.
- Fix ZMK to Kanata type mapping.
- Add validation for all transformer outputs.

### 5. Error Handling & Logging ⏳
- Centralized error and warning collection across parser and all transformers, with context-rich logging, summary reporting, fallback mechanisms, robust error recovery, and programmatic access. All issues can be aggregated after a run for a complete report.

### 6. Integration & Testing ⏳
- Consolidate conversion pipeline into a single system.
- Remove special case handling and workarounds.
- Integrate the new parser with existing transformers.
- Create end-to-end tests for complex real-world configurations.
- Test with Ben Vallack's configuration.
- Benchmark performance with large configuration files.
- Re-run all tests after each major step and address new errors as they arise.
- (Optional) Add parser unit tests for parsing a single layer, a single binding, and state transitions.

### 7. Documentation & Cleanup ⏳
- Update documentation to reflect new parsing approach and architecture.
- Add concise examples for common conversion cases (for maintainers).
- Cleanup deprecated code and remove outdated or redundant documentation.
- Ensure consistent coding style and remove duplication.
- Final refactoring and optimization pass.

---

# Progress Tracking & Audit Status (May 2025)

**Current Status:**
- Core modules have been restored and refactored.
- Data contracts and type safety are in place.
- Macro transformer implementation has been fixed and tested.
- Error/warning collection and output validation need improvements.
- Integration/testing and documentation/cleanup are in progress.

## Audit Issue Status Table (Current)

| Audit Issue Section                | Status         | Indicator | Notes |
|------------------------------------|---------------|-----------|-------|
| Macro binding handling             | In Progress   | 🟡        | Parser fixed, tests passing |
| Parser/model/transformer alignment | Complete      | 🟢        | Output formats standardized, Layer model uses 2D keys matrix |
| Unit tests                         | In Progress   | 🟡        | Macro parser tests passing, others need fixes |
| Integration tests                  | Complete      | 🟢        | Integration tests pass, parser/model/transformer aligned |
| End-to-end tests                   | In Progress   | 🟡        | Real-world config tests needed |
| Other tests                        | In Progress   | 🟡        | Performance and error handling tests failing |
| Documentation/cleanup              | In Progress   | 🟡        | Needs update after implementation fixes |

**Legend:** 🟢 Complete / 🟡 In Progress / 🔴 Not Started

**Next critical actions:**
1. Update macro parser implementation:
   - Fix validation issues
   - Improve error recovery
   - Standardize state transitions
2. Standardize transformer output formats:
   - Ensure consistent structure across all transformers
   - Fix special character handling
   - Standardize error messages
3. Complete test coverage:
   - Add missing test cases for macro parser
   - Improve error handling tests
   - Add performance tests
4. Update documentation:
   - Document macro transformer changes
   - Add examples for macro usage
   - Update error handling guidelines

> **Note:** All future updates to project progress or next steps should be incorporated into this single audit table. Do not create new or duplicate progress tracking lists elsewhere in this document.

---

## Macro Parser and Transformer Test Status (as of latest run)

- All macro parser and macro transformer tests pass, including parameterized, nested, and error recovery scenarios.
- Error aggregation and reporting have been improved for both parser and transformer.
- Linter compliance (line length, whitespace) has been enforced throughout the codebase.

## Remaining Work

- Run and fix integration tests to ensure end-to-end correctness.
- Continue to monitor and improve edge case coverage and robustness.

### Parser Implementation Improvements: Robust Token-Based Row Handling (Complete)

**Goal:**
Make the parser robust to both single-line and multi-line ZMK bindings formatting by accumulating all bindings in a block as a flat list, then reshaping into rows according to the expected layout.

**Status:** ✅ Complete. The parser now accumulates all bindings as a flat list, infers the number of columns, reshapes into a matrix, and the Layer model stores keys as a 2D matrix. All code and tests have been updated to use this structure. Integration tests now pass, confirming end-to-end correctness.

**Implementation Steps:**
1. **Parser Refactor – Accumulate All Bindings as a Flat List** ✅
2. **Determine Row/Column Structure** ✅
3. **Reshape the Flat List into Rows** ✅
4. **Update the Layer Model** ✅
5. **Update Tests** ✅
6. **Document the Change** ✅

**Confidence:** High. This approach is directly aligned with ZMK's documented flexibility and real-world usage. It is a common pattern in keyboard firmware parsers.

**Scope:** Medium. Requires parser changes, possible config/template addition, test updates, and documentation changes. No changes needed to ZMK input format or user keymaps.

---

## Current Test Failures (June 2025)

After the latest round of parser and transformer fixes, the following issues remain:

- **Unicode Output:** Unicode bindings like `&pi` and `&n_tilde` are still output as `(unicode ?)` instead of the correct character (e.g., `(unicode π)`).
- **Sticky Key Output:** Sticky key output does not match the expected Kanata format (e.g., outputs `sk lshift` instead of `sticky-lsft`).
- **Layer Switching Output:** Layer switching keys (e.g., `&mo 1`) are not always output as `@layer1` or `@lower` as expected by tests.
- **Macro Round-Trip Tests:** Some macro round-trip and integration tests fail due to parameter or step mismatches.
- **Parser Debug/Pattern Matching:** Some parser debug tests fail due to regex or output format mismatches.
- **General Output Formatting:** Some integration tests fail due to minor output formatting or content mismatches.

### Next Steps (June 2025)

1. **Fix Unicode Output:**
   - Ensure Unicode parser maps known bindings (e.g., `&pi`, `&n_tilde`) to the correct characters.
2. **Fix Sticky Key Output:**
   - Update transformer logic to output sticky keys in the expected Kanata format.
3. **Fix Layer Switching Output:**
   - Ensure layer switching keys are output as expected by tests.
4. **Fix Macro Round-Trip and Integration Tests:**
   - Address parameter and step mismatches in macro round-trip tests.
5. **Fix Parser Debug/Pattern Matching Tests:**
   - Update regex or output logic to match test expectations.
6. **General Output Formatting:**
   - Standardize output formatting to match test expectations.

---
