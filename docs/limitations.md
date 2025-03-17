# Known Limitations and Constraints

This document outlines the known limitations and intentional constraints of the ZMK to Kanata converter. Understanding these limitations will help users work around them when converting complex keyboard layouts.

## ZMK Features with Limited Support

### 1. Nested Layers

**Limitation**: Nested layers within ZMK keymap files are not supported.

**Reason**: The ZMK parser is designed to handle a flat hierarchy of layers only, which aligns with most standard keyboard layouts.

**Workaround**: Define all layers at the top level of your ZMK keymap.

### 2. Unsupported Nested Behaviors

**Limitation**: Some nested behavior combinations in hold-tap behaviors might not convert correctly.

**Reason**: The hold-tap transformer has specific support for common nested behaviors, but uncommon or complex nested behaviors may not be properly transformed.

**Workaround**: Simplify complex nested behaviors in your ZMK keymap or manually adjust the Kanata configuration after conversion.

## Other Known Limitations

### 1. Conditional Layers

**Limitation**: ZMK conditional layers require special handling when converting to Kanata.

**Reason**: Kanata handles layer transitions differently than ZMK, particularly for conditional activations.

**Workaround**: Use Kanata's layer manipulation functions (`layer-toggle`, `layer-while-held`, etc.) to recreate the conditional logic after conversion.

### 2. Custom Behaviors

**Limitation**: Custom behaviors defined in ZMK are not automatically converted.

**Reason**: The converter only handles standard ZMK behaviors that have direct equivalents in Kanata.

**Workaround**: After conversion, manually define equivalent behaviors in your Kanata configuration.

## Performance Considerations

- Large keymaps with many layers and complex bindings may take longer to convert.
- The converter prioritizes correctness over optimization, so some generated Kanata configurations might benefit from manual optimization.

## Future Improvements

The following limitations are planned to be addressed in future versions:

1. Enhanced handling of conditional layers
2. Support for more complex nested behaviors
3. Optimization of generated Kanata configurations

## Reporting Issues

If you encounter a limitation not documented here, please report it as an issue in the project repository. 