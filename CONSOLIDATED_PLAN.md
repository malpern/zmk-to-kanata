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
- **DTS Parser:** Tokenizes and parses DTS to AST
- **Keymap Extractor:** Extracts layers, behaviors, bindings from AST
- **Behavior Transformers:** Converts ZMK behaviors to Kanata equivalents
- **Kanata Output Generator:** Produces final Kanata config

## 3. Current Status (July 2024)

- Codebase is fully green: all tests pass, all linter/style checks pass
- Robust, cross-platform preprocessor and parser
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

To achieve 90%+ test coverage, focus on the following files in order of priority (lowest coverage first):

1. `converter/model/keymap_model.py` (**91% covered, fully tested as of July 2024**)
   - All model logic, methods, and edge cases are now exercised by unit tests.
2. `converter/behaviors/hold_tap.py` (**100% covered, fully tested as of July 2024**)
   - All logic, error handling, and conversion methods are now exercised by unit tests.
3. `converter/behaviors/unicode.py` (**100% covered, fully tested as of July 2024**)
   - All logic and conversion methods are now exercised by unit tests.
4. `converter/transformer/holdtap_transformer.py` (**92% covered, fully tested as of July 2024**)
   - All main logic, branches, and error cases are now exercised by unit tests.
5. `converter/transformer/macro_transformer.py` (**48% covered**)
   - Add tests for macro transformation logic, including edge cases and error handling.
6. `converter/behaviors/sticky_key.py` (**54% covered**)
   - Add tests for sticky key behavior logic and error handling.
7. `converter/models.py` (**51% covered**)
   - Add tests for all data models and their methods.
8. `converter/behaviors/macro.py` (**63% covered**)
   - Add tests for macro behavior logic and conversion.
9. `converter/transformer/kanata_transformer.py` (**66% covered**)
   - Add tests for Kanata transformation logic, especially for less common behaviors.
10. `converter/kanata_converter.py` (**71% covered**)
    - Add tests for Kanata output generation and error handling.
11. `converter/error_handling/error_manager.py` (**68% covered**)
    - Add tests for error manager logic, including all error types and logging.
12. `converter/dts/error_handler.py` (**73% covered**)
    - Add tests for DTS error handling, especially for edge cases.
13. `converter/dts/preprocessor.py` (**77% covered**)
    - Add tests for preprocessor logic, including all code paths and error handling.
14. `converter/dts/extractor.py` (**77% covered**)
    - Add tests for extractor logic, especially for complex keymap structures.
15. `converter/dts/parser.py` (**83% covered**)
    - Add tests for parser edge cases and error handling.
16. `converter/dts/ast.py` (**91% covered**)
    - Add tests for AST node methods and edge cases.

**Step-by-step approach:**
1. Start with `converter/model/keymap_model.py` and work down the list.
2. For each file, identify untested functions, methods, and branches (see coverage report for missing lines).
3. Write targeted unit tests to cover missing logic, edge cases, and error handling.
4. Rerun coverage after each batch of tests to track progress.
5. Continue until all files are at or above 90% coverage.

---

**Summary:**
- The codebase is stable, robust, and fully green (v1.0.0)
- Ready for broader use and future development

## 7. Debugging and Output Flags (Implemented)

Robust debugging and output flags are now fully implemented in the CLI and documented in the README. These provide visibility at each important stage of the conversion pipeline:

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