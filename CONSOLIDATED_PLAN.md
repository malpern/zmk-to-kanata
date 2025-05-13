# ZMK to Kanata Converter: Development Plan and Status

## 1. Overview and Goals

The ZMK to Kanata Converter is a tool to convert ZMK keymap files (DTS) into Kanata configuration format.

**Key Goals:**
- Robust parsing of ZMK keymap files, including complex DTS structures
- Support for a comprehensive set of ZMK features (layers, advanced behaviors, macros, transparent keys)
- Matrix layout handling, including automatic size detection
- Minimal external dependencies
- Clean, readable Kanata output
- CLI and Python API

## 2. Architecture

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
- **DTS Parser:** Tokenizes and parses DTS to AST (supports all ZMK property names, including #binding-cells)
- **Keymap Extractor:** Extracts layers, behaviors, bindings from AST
- **Behavior Transformers:** Converts ZMK behaviors to Kanata equivalents
- **Kanata Output Generator:** Produces final Kanata config

## 3. Current Status (July 2024)

- Codebase is fully green: all tests pass, all linter/style checks pass
- Robust, cross-platform preprocessor and parser (including #binding-cells and all ZMK property names)
- All core, preprocessor, parser, and main CLI/integration tests pass
- Error handling and macro expansion are consistent and well-tested
- Codebase is well-documented, type-hinted, and formatted
- **v1.0.0 tag created:** First fully stable, robust release

## 4. Remaining Work

- **Documentation:**
    - (Optional) Finalize and polish documentation for preprocessor configuration, troubleshooting, and platform-specific setup
- **Future Enhancements:**
    - Add new features or performance improvements as needed

## 5. Next Steps

1. (Optional) Polish and expand documentation
2. Plan and implement future enhancements as desired

## 6. Test Coverage Improvement Plan

To maintain 90%+ test coverage, periodically review coverage reports and add targeted tests for any new or changed code, especially for edge cases and error handling.

**Step-by-step approach:**
1. For each file, identify untested functions, methods, and branches (see coverage report for missing lines).
2. Write targeted unit tests to cover missing logic, edge cases, and error handling.
3. Rerun coverage after each batch of tests to track progress.
4. Continue until all files are at or above 90% coverage.

---

**Summary:**
- The codebase is stable, robust, and fully green (v1.0.0)
- Ready for broader use and future development

## 7. Debugging and Output Flags (Implemented)

Robust debugging and output flags are fully implemented in the CLI and documented in the README. These provide visibility at each important stage of the conversion pipeline:

### Key Processing Stages
- **Preprocessing:** Raw DTS → Preprocessed DTS
- **Parsing:** Preprocessed DTS → AST (Abstract Syntax Tree)
- **Extraction:** AST → Keymap Model (Python dataclasses)
- **Transformation/Output:** Keymap Model → Kanata YAML

### Available CLI Flags
| Flag                        | Description                                                      |
|-----------------------------|------------------------------------------------------------------|
| `--dump-preprocessed [FILE]`| Output preprocessed DTS to stdout or FILE                         |
| `--dump-ast [FILE]`         | Output parsed AST (as JSON) to stdout or FILE                     |
| `--dump-extracted [FILE]`   | Output extracted keymap model (as YAML/JSON) to stdout or FILE    |
| `--debug`                   | Print debug logs at all stages (uses logging)                    |
| `-v`, `--verbose`           | Increase verbosity (can be used multiple times)                   |
| `--log-level LEVEL`         | Set logging level (`info`, `debug`, `warning`, etc.)              |

### Example CLI Usage
```
# Just convert, no extra output
zmk-to-kanata input.dtsi -o output.yaml

# See preprocessed DTS
zmk-to-kanata input.dtsi --dump-preprocessed

# Save AST to a file
zmk-to-kanata input.dtsi --dump-ast ast.json

# See extracted model in YAML
zmk-to-kanata input.dtsi --dump-extracted

# Full debug logs and all intermediate outputs
zmk-to-kanata input.dtsi --debug --dump-preprocessed --dump-ast --dump-extracted
```

- If a FILE is not specified, output is sent to stdout.
- You can combine multiple dump flags to inspect all stages.
- Use `--debug` or `-v`/`--verbose` for more detailed logs.

---

## 8. Parser Logging and Visibility

- All parser debug and trace output uses the logging module, controlled by CLI flags.
- Key parsing steps, errors, and edge cases are logged at appropriate levels.
- No ad hoc print statements remain; all output is structured and suppressible unless requested.
- See README for details on enabling debug output.

---

## 9. Real-World ZMK File Coverage

The following real-world ZMK files have been collected and tested:

| File Location                          | Status                |
|----------------------------------------|-----------------------|
| examples/basic_keymap.dtsi             | ✅ Successfully tested |
| examples/advanced_features.dtsi        | ⏳ Collected, not yet tested |
| examples/multi_layer_keymap.dtsi       | ✅ Successfully tested |
| examples/complex_keymap.dtsi           | ⏳ Collected, not yet tested |
| examples/ben_vallack_test.dtsi         | ⏳ Collected, not yet tested |
| tests/fixtures/real_world/card.keymap  | ⏳ Collected, not yet tested |
| tests/fixtures/real_world/piano.keymap | ⏳ Collected, not yet tested |
| tests/fixtures/dts/simple_keymap.zmk   | ✅ Successfully tested |
| tests/fixtures/dts/large_keymap.zmk    | ⏳ Collected, not yet tested |
| tests/fixtures/dts/complex_keymap.zmk  | ⏳ Collected, not yet tested |

- ✅ = Successfully tested end-to-end (parse, extract, convert)
- ⏳ = Collected, but not yet fully tested

Update this table as more files are tested or added.