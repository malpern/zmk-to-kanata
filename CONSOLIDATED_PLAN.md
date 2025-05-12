# ZMK to Kanata Converter: Development Plan and Status

## 1. Overview and Goals

The ZMK to Kanata Converter is a tool designed to convert ZMK keymap files (using DTS - Device Tree Source) into the Kanata configuration format.

**Key Goals:**
- Robust parsing of ZMK keymap files, including complex DTS structures.
- Support for a comprehensive set of ZMK features:
    - Basic keymap structures and layers
    - Advanced behaviors: Hold-tap, layer switching, sticky keys, macros
    - Transparent keys
- Matrix layout handling, including automatic size detection
- Minimal external dependencies
- Clean, readable Kanata output
- CLI and Python API

## 2. Architecture

The pipeline:

```
Input ZMK File (.zmk/.dts)
     |
     V
DTS Preprocessor (cpp)
     |
     V
DTS Parser (AST)
     |
     V
Keymap Extractor
     |
     V
Behavior Transformers
     |
     V
Kanata Output Generator
```

**Key Components:**
- **DTS Preprocessor:** Integrates with cpp, manages includes, matrix size, error handling
- **AST Implementation:** DtsNode, DtsProperty, DtsRoot
- **DTS Parser:** Tokenizes and parses DTS to AST
- **Keymap Extractor:** Extracts layers, behaviors, bindings from AST
- **Behavior Transformers:** Converts ZMK behaviors to Kanata equivalents
- **Kanata Output Generator:** Produces final Kanata config

## 3. Current Status (June 2024)

### What is Stable
- Core extraction, parsing, and transformation logic is robust and in sync with the test suite
- All major test and linter issues (iteration over behaviors, error handling, boolean property handling, linter/style) have been fixed
- Most core and end-to-end tests pass
- Codebase is well-documented, type-hinted, and formatted (Black, Ruff)

### What Remains for Full Stability
- **Environment/toolchain:**
    - Some tests (especially performance and preprocessor tests) fail due to cpp/preprocessor environment issues (e.g., cpp not found, platform-specific path issues)
    - Action: Ensure cpp is available and correctly configured on all target platforms
- **Parser edge-case tests:**
    - A few parser tests may need review/updates to match current parser output or error messages
    - Action: Review and update parser tests for edge cases and error handling
- **Performance tests:**
    - Some performance/benchmark tests depend on cpp and may fail if the environment is not set up
    - Action: Set up environment or mark these as expected failures if not critical
- **Documentation:**
    - Update and complete documentation for preprocessor configuration, troubleshooting, and platform-specific setup
    - Action: Add/expand docs as needed

## 4. Next Steps (Actionable)

1. **Fix cpp/preprocessor environment issues:**
    - Ensure cpp is installed and available in CI/dev environments
    - Add platform-specific detection and error messages if needed
2. **Review and update parser edge-case tests:**
    - Align test expectations with current parser output and error handling
3. **Performance test environment:**
    - Set up or skip/mark as expected fail if not critical
4. **Documentation:**
    - Finalize setup, troubleshooting, and usage docs

## 5. Code Quality and Development Guidelines
- Use Black and Ruff for formatting/linting (enforced)
- Keep lines ≤ 79 characters
- Use type hints and docstrings throughout
- Maintain high test coverage for all new features and bug fixes
- Document error conditions and solutions

## 6. macOS cpp/Preprocessor Issue: Detailed Problem Statement & Debugging Checklist

### Problem Description
- On macOS, running the preprocessor (`cpp`) on `.dts` files with the `-x c` flag (or without) results in errors like:
  - `cc: error: no such file or directory: 'c'`
  - `cc: warning: <include_path>: 'linker' input unused [-Wunused-command-line-argument]`
- This occurs with both `/usr/bin/cpp` and the Xcode toolchain's `cpp`.
- The error persists regardless of argument order, and is a known quirk of Clang's `cpp` on macOS, especially with non-standard file extensions.

### What Has Been Tried
- [x] Using Xcode toolchain's `cpp`
- [x] Using `/usr/bin/cpp`
- [x] Adding/removing `-x c` in various positions
- [x] Ensuring correct argument order per Clang docs
- [x] Verifying include paths and temp file contents
- [x] Running the same command in shell and Python (error is consistent)
- [x] Use clang -E -nostdinc -undef -x assembler-with-cpp for .dts preprocessing (canonical kernel solution)

### Comprehensive Checklist of Alternative Approaches & Debugging Steps
- [ ] Remove `-x c` and try with `.dts` extension
- [ ] Change temp file extension to `.c` and try without `-x c`
- [ ] Change temp file extension to `.c` and try with `-x c`
- [ ] Try using a different C preprocessor (e.g., install GCC and use its `cpp`)
- [ ] Use a wrapper script to rename the file before preprocessing
- [ ] Use Docker with a Linux toolchain for preprocessing
- [ ] Use a Python-based preprocessor (e.g., `pycparser`) as a fallback
- [ ] Add platform-specific logic to skip or mark preprocessor tests as expected fail on macOS
- [ ] Document the issue and provide troubleshooting steps in the README
- [ ] Ask the community (e.g., Stack Overflow, GitHub Issues) for macOS-specific solutions

### Notes
- This checklist should be updated as new ideas are generated or steps are completed.
- Once all steps are checked or a solution is found, update the plan and documentation accordingly.

### References
- This approach is used by the Linux kernel build system and dtc (Device Tree Compiler) maintainers for robust cross-platform preprocessing of .dts files.

### Status Update (July 2024)
- The canonical kernel solution for preprocessing .dts files on macOS is now implemented and working.
- The preprocessor step is robust and cross-platform.
- Tests currently expect macro names (e.g., RC(0,0)), but the preprocessor now outputs macro-expanded values (e.g., ((0) << 8 | (0))).
- Next steps: Update tests to expect macro-expanded output, and align error handling tests with new exception types.

---

**Summary:**
- The codebase is very close to fully stable/green for all core features.
- Remaining blockers are environment/toolchain setup for cpp, parser edge-case test review, and documentation polish.
- Once these are addressed, the project will be fully robust and ready for broader use. 