# ZMK to Kanata Converter Examples

This directory contains example ZMK configuration files that can be used with the ZMK to Kanata Converter.

## Example Files

### Basic Keymap (`basic_keymap.dtsi`)

A simple ZMK keymap with a single layer. This is a good starting point for understanding the basic structure of a ZMK keymap.

To convert this example:

```bash
zmk-to-kanata examples/basic_keymap.dtsi basic_keymap.kbd
```

### Multi-Layer Keymap (`multi_layer_keymap.dtsi`)

A more complex ZMK keymap with multiple layers. This example demonstrates how to define and use multiple layers in ZMK.

To convert this example:

```bash
zmk-to-kanata examples/multi_layer_keymap.dtsi multi_layer_keymap.kbd
```

### Advanced Features (`advanced_features.dtsi`)

A comprehensive ZMK keymap that demonstrates advanced features such as:
- Homerow mods
- Sticky keys
- Tap dance
- Key sequences
- Bluetooth controls

To convert this example:

```bash
zmk-to-kanata examples/advanced_features.dtsi advanced_features.kbd
```

Note: Some advanced features may not be fully supported by the converter. See the [Known Limitations](../docs/known_limitations.md) document for more information.

## Using the Examples

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/zmk-to-kanata.git
   cd zmk-to-kanata
   ```

2. Install the converter:
   ```bash
   pip install -e .
   ```

3. Convert an example:
   ```bash
   zmk-to-kanata examples/basic_keymap.dtsi output.kbd
   ```

4. Examine the generated Kanata file:
   ```bash
   cat output.kbd
   ```

## Creating Your Own Examples

You can use these examples as a starting point for creating your own ZMK configurations. Simply copy one of the example files and modify it to suit your needs.

For more information on ZMK configuration, see the [ZMK Documentation](https://zmk.dev/docs/).

For more information on Kanata configuration, see the [Kanata Documentation](https://github.com/jtroo/kanata). 