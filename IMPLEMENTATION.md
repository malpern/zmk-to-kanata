# ZMK to Kanata Converter Implementation Plan

> **Note:** Checkmarks (✅) in the plan below indicate completed major steps. For detailed status and sub-steps, see the progress tracker table at the end of this document. Only update checkmarks at the step (macro) level, not on individual sub-bullets.

## Current Status (May 2025)

- **Data contracts and type safety for bindings and layers are now enforced and documented.**
  - All core data structures (`KeyMapping`, `Layer`) are now classes with explicit contracts and runtime type assertions.
  - The parser and model guarantee correct object types for all bindings and layers.
- **All transformers now output standardized Kanata S-expressions, validate their output, and aggregate errors/warnings via a centralized error manager.**
  - Output validation and debug logging are present in all transformers.
  - Error and warning collection is robust and context-rich, with summary reporting and programmatic access.
- **Layer addition and state transitions are robust and fully tested.**
  - Debug logging is present for layer start, finish, and addition.
  - Every parsed layer is finalized and appended to the keymap.
  - There are assertions and tests to ensure that for valid files, at least one layer is present after parsing.
- **Macro parser refactoring and transformer edge case handling are complete.**
  - Macro definition and usage parsing are robust, token-based, and fully validated.
  - All edge cases, including invalid macro steps/parameters, are handled and tested.
  - Integration and unit tests for complex/nested macros and error recovery all pass.
- **Integration and end-to-end testing is complete.**
  - Multiple integration tests run the full pipeline (parse, transform, aggregate errors) on real and edge-case ZMK configs, and all pass.
  - The error manager is reset between tests, and all issues are aggregated and reported at the end of each run.
  - The pipeline is robust and ready for documentation/cleanup and future enhancements.
- **Summary:**
  - The codebase is now robust, with architectural stability, standardized output, and reliable error handling. All major refactor and testing steps are complete. The next focus is on documentation, cleanup, and future feature work.

---

# ZMK to Kanata Converter Implementation Plan

This document outlines our plan to overhaul the ZMK to Kanata converter, eliminating the Ben Vallack workaround and fixing underlying parser and transformer issues.

## Project Goals

1. Create a unified conversion pipeline that can handle all ZMK configurations including Ben Vallack's
2. Standardize output format following Kanata's Lisp-like syntax
3. Improve error handling and validation throughout the codebase
4. Align tests with implementation
5. Remove the need for special case workarounds

## Unified Implementation Plan (April 2025)

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

### 4. Transformer Standardization ✅
- Update all transformers to follow standardized output format.
- Ensure consistent structure for all transformers.
- Implement proper handling of nested bindings.
- Fix ZMK to Kanata type mapping.
- Add validation for all transformer outputs.

### 5. Error Handling & Logging ✅
- Centralized error and warning collection across parser and all transformers, with context-rich logging, summary reporting, fallback mechanisms, robust error recovery, and programmatic access. All issues can be aggregated after a run for a complete report.

### 6. Integration & Testing ✅ Complete
- Consolidate conversion pipeline into a single system.
- Remove special case handling and workarounds.
- Integrate the new parser with existing transformers.
- Create end-to-end tests for complex real-world configurations.
- Test with Ben Vallack's configuration.
- Benchmark performance with large configuration files.
- Re-run all tests after each major step and address new errors as they arise.
- (Optional) Add parser unit tests for parsing a single layer, a single binding, and state transitions.

### 7. Documentation & Cleanup ✅ Complete
- Update documentation to reflect new parsing approach and architecture.
- Add concise examples for common conversion cases (for maintainers).
- Cleanup deprecated code and remove outdated or redundant documentation.
- Ensure consistent coding style and remove duplication.
- Final refactoring and optimization pass.

#### Macro Parser Refactoring (Next Major Task)

**Goal:**
- Make macro parsing robust, maintainable, and consistent with the rest of the pipeline.

**Steps:**
1. Separate macro definition parsing from macro usage parsing.
2. Implement a token-based (not line-based) macro parser for correct handling of multi-line and nested macros.
3. Add proper state management and cleanup after errors.
4. Support nested/timed macro steps and all Kanata macro syntax.
5. Integrate macro error handling with the centralized error manager, including context (line, file, etc.).
6. Add/expand tests for complex macros, error recovery, and edge cases.
7. Ensure output validation and debug logging are present as with other transformers.

#### Transformer and Edge Case Handling (Next Major Task)

**Goal:**
- Ensure all transformers handle edge cases, output format mismatches, and data model inconsistencies, and that all related tests pass.

**Steps:**
1. Review all transformer and edge case tests (including skipped and failing ones).
2. Update transformer logic to handle all edge cases (e.g., special characters, empty/None bindings, mixed case, Unicode, invalid keys, etc.).
3. Ensure output format matches test expectations and Kanata DSL for all cases.
4. Fix attribute errors and data model mismatches in test objects and transformers.
5. Update or add tests for new edge cases and ensure all pass.
6. Maintain robust error handling and output validation throughout.

---

## Progress Tracking

| Step | Component | Status | Notes |
|-------|-----------|--------|-------|
| 1 | Clarify/enforce contracts | ✅ Complete | Data contracts and type safety enforced |
| 2 | Fix layer addition/state transitions | ✅ Complete | Debug logging, layer finalization, and tests/assertions for non-empty layers present |
| 3 | Key validation/filtering | ✅ Complete | Filtering and validation logic implemented in parser |
| 4 | Transformer standardization | ✅ Complete | All transformers output Kanata S-expressions, handle edge cases, and log/validate |
| 5 | Error handling/logging | ✅ Complete | Centralized error/warning collection, output validation, and reporting in all transformers |
| 6 | Integration/testing | ✅ Complete | Multiple integration tests run the full pipeline on real and edge-case configs, all pass |
| 7 | Documentation/cleanup | ✅ Complete | Macro parser refactoring and transformer edge case handling are complete; ready for documentation and future enhancements |

> **Note:** All future updates to project progress or next steps should be incorporated into this single progress tracker. Do not create new or duplicate progress tracking lists elsewhere in this document.

---

## Maintainer Notes: Architecture, Error Handling, and Output Validation

- The ZMK to Kanata converter is now architecturally stable and robust.
- All core data structures are type-checked and validated at runtime.
- The parser guarantees that all layers and bindings are valid objects, and logs all key state transitions.
- All transformers output standardized Kanata S-expressions, validate their output, and aggregate errors/warnings via a centralized error manager.
- Error and warning collection is context-rich, with summary reporting and programmatic access. The error manager is reset between tests and all issues are aggregated after each run.
- Integration and end-to-end tests cover real and edge-case ZMK configs, and all pass.
- There is no user-facing documentation at this time; this document is for maintainers and future contributors.
- For further details, see the code and test suite for up-to-date examples and edge case handling.