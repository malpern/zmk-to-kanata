`# Ben Vallack ZMK to Kanata Converter

This script converts Ben Vallack's ZMK configuration to Kanata format.

## Usage

```bash
python -m converter.cli input.dtsi output.kbd
```

### Example

Input ZMK file (`input.dtsi`):
```c
/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B &kp C
                &mo 1 &kp D &kp E
            >;
        };
        
        function_layer {
            bindings = <
                &kp F1 &kp F2 &kp F3
                &trans &kp F4 &kp F5
            >;
        };
    };
};
```

Output Kanata file (`output.kbd`):
```
(defsrc
  a b c
  mo1 d e)

(deflayer default
  a b c
  @fn d e)

(deflayer function
  f1 f2 f3
  _ f4 f5)
```

### Supported Features

1. **Basic Keys**
   - Regular keys (letters, numbers, symbols)
   - Function keys (F1-F24)
   - Navigation keys (arrows, home, end, etc.)
   - System keys (volume, media control, etc.)

2. **Modifiers**
   - Basic modifiers (shift, ctrl, alt, gui)
   - Modifier combinations
   - Sticky modifiers

3. **Layers**
   - Layer switching
   - Momentary layers
   - Transparent keys

4. **Advanced Features**
   - Hold-tap behaviors
   - Custom behaviors
   - Macros
   - Unicode input

## Known Limitations

- No support for advanced ZMK features like combos
- Limited to standard keyboard layouts
- Focus on common use cases first

## Troubleshooting

### Common Issues

1. **Invalid Key Names**
   - Error: "Invalid key name in binding"
   - Solution: Check that key names match ZMK's key codes

2. **Layer Issues**
   - Error: "Layer not found"
   - Solution: Ensure all referenced layers are defined

3. **Syntax Errors**
   - Error: "Failed to parse ZMK file"
   - Solution: Verify ZMK file syntax and formatting

### Getting Help

If you encounter issues:
1. Check the error message for specific details
2. Verify your ZMK file syntax
3. Open an issue on GitHub with:
   - Your ZMK file
   - The error message
   - Expected behavior

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.