# Test Coverage and Limitations

## Test Coverage Summary

The ZMK to Kanata Converter has an overall test coverage of 86%, with 82 tests covering various aspects of the codebase. The test suite includes unit tests, integration tests, and end-to-end tests to ensure the converter functions correctly.

### Coverage by Module

| Module | Coverage | Notes |
|--------|----------|-------|
| `converter/__init__.py` | 100% | Fully covered |
| `converter/behaviors/__init__.py` | 100% | Fully covered |
| `converter/behaviors/key_sequence.py` | 100% | Fully covered |
| `converter/behaviors/sticky_key.py` | 77% | Missing coverage for error handling paths |
| `converter/cli.py` | 100% | Complete coverage |
| `converter/layer_parser.py` | 95% | Good coverage |
| `converter/layer_transformer.py` | 92% | Good coverage |
| `converter/main.py` | 100% | Complete coverage |
| `converter/model/keymap_model.py` | 38% | Low coverage, needs improvement |
| `converter/output/file_writer.py` | 100% | Fully covered |
| `converter/parser/sticky_key_parser.py` | 38% | Low coverage, needs improvement |
| `converter/parser/zmk_parser.py` | 87% | Good coverage |
| `converter/taphold_parser.py` | 99% | Excellent coverage |
| `converter/transformer/holdtap_transformer.py` | 100% | Fully covered |
| `converter/transformer/kanata_transformer.py` | 91% | Good coverage |

### Test Categories

1. **Unit Tests**: Testing individual components in isolation
   - Parser tests
   - Transformer tests
   - Model tests

2. **Integration Tests**: Testing how components work together
   - Layer integration tests
   - Hold-tap integration tests
   - Key sequence integration tests

3. **End-to-End Tests**: Testing the entire conversion process
   - CLI interface tests
   - File operation tests
   - Real-world configuration tests
   - Error handling tests

## Known Limitations

The ZMK to Kanata Converter has several known limitations that users should be aware of:

### Unsupported ZMK Features

1. **Combos**: ZMK combos are not supported in the current version. Kanata has a different approach to key combinations.

2. **Custom Behaviors**: Custom behaviors defined in ZMK (like homerow mods) are not directly supported. Users need to manually adjust these in the generated Kanata file.

3. **Macros**: ZMK macros are not fully supported yet. Basic key sequences are supported, but complex macros with conditionals are not.

4. **Unicode Input**: Unicode character input is not supported in the current version.

5. **Advanced Modifiers**: Some advanced modifier combinations in ZMK may not translate correctly to Kanata.

### Conversion Accuracy

1. **Hold-Tap Behaviors**: While basic hold-tap behaviors are supported, some advanced configurations may not translate perfectly.

2. **Layer Switching**: Layer switching works, but the exact behavior might differ between ZMK and Kanata.

3. **Timing Parameters**: Timing parameters for key presses and holds may need manual adjustment after conversion.

### Error Handling

1. **Error Reporting**: Error messages could be more specific in some cases, especially for complex configurations.

2. **Recovery from Errors**: The converter currently stops on the first error rather than attempting to continue with a partial conversion.

## Areas for Improvement

Based on the test coverage and known limitations, the following areas could be improved:

1. **Model Coverage**: The `converter/model/keymap_model.py` module has low coverage (38%) and should be a priority for improvement.

2. **Sticky Key Parser**: The `converter/parser/sticky_key_parser.py` module has low coverage (38%) and needs more tests.

3. **Error Handling**: Several modules have missing coverage for error handling paths, which could be improved.

4. **Feature Support**: Adding support for combos, macros, and Unicode input would make the converter more complete.

5. **Documentation**: More detailed documentation on how to manually adjust converted files for unsupported features would be helpful.

## Conclusion

The ZMK to Kanata Converter has good test coverage overall, but there are specific areas that need improvement. The converter supports most common ZMK features, but users should be aware of the limitations when converting complex configurations.

For the best results, users should review the generated Kanata files and make manual adjustments as needed, especially for advanced features like custom behaviors and complex macros.
