# Known Limitations of ZMK to Kanata Converter

This document outlines the known limitations of the ZMK to Kanata Converter. Understanding these limitations will help you make the most of the converter and know when manual adjustments might be necessary.

- For installation and usage, see the [README](../README.md).
- For user instructions, see the [User Guide](user_guide.md).
- For API details, see [API Documentation](api_documentation.md).
- For contributing, see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Unsupported ZMK Features

### 1. Combos

**Description**: ZMK combos allow you to trigger a key or behavior when multiple keys are pressed together.

**Limitation**: Only simple combos (two or more keys → single key output) are supported. Combos involving layers, macros, or advanced logic are not supported and must be added manually.

**Workaround**: You'll need to manually define complex combos in your Kanata configuration using Kanata's syntax:

```
(defalias
  combo (tap-dance 200 (combo a s d)))

(deflayer default
  ...
  combo ...
  ...
)
```

| Combo Type         | Supported? | Notes                                 |
|--------------------|------------|---------------------------------------|
| Simple (A+B → ESC) | ✅         | Fully supported, auto-converted       |
| Layered            | ❌         | Not supported, must add manually      |
| With Modifiers     | ❌         | Not supported, must add manually      |
| Macro Output       | ❌         | Not supported, must add manually      |
| Overlapping Combos | ❌         | Not supported, must add manually      |

### 2. Custom Behaviors

**Description**: ZMK allows defining custom behaviors like homerow mods using the `zmk,behavior-hold-tap` compatible property.

**Limitation**: Best-effort mapping is provided for custom hold-tap behaviors (home row mods). Standard properties (timing, flavor, bindings) are mapped to Kanata. Any unmapped or advanced properties (e.g., retro-tap, hold-trigger-key-positions) are commented in the output for manual review.

**Workaround**: Review the Kanata output for comments about unmapped properties and adjust manually if needed.

| Custom hold-tap (home row mod) | ⚠️         | Best-effort mapping; unmapped properties commented |

### 3. Macros

**Description**: ZMK supports macros for executing multiple key presses in sequence.

**Limitation**: The converter supports basic key sequences but not complex macros with conditionals or delays.

**Workaround**: You'll need to manually define complex macros in your Kanata configuration:

```
(defalias
  mymacro (macro
    a b c
    (release a b c)
    d e f
  )
)
```

### 4. Unicode Input

**Description**: ZMK supports Unicode input for typing special characters.

**Limitation**: The converter does not currently support Unicode input.

**Workaround**: You'll need to manually define Unicode input in your Kanata configuration using Kanata's Unicode syntax.

### 5. Advanced Modifiers

**Description**: ZMK supports advanced modifier combinations and sticky modifiers.

**Limitation**: Some advanced modifier combinations may not translate correctly to Kanata.

**Workaround**: Review and adjust modifier keys in the generated Kanata file.

## Conversion Accuracy Issues

### 1. Hold-Tap Behaviors

**Description**: ZMK and Kanata have different approaches to hold-tap behaviors.

**Limitation**: While basic hold-tap behaviors are supported, some advanced configurations may not translate perfectly:
- `quick-tap-ms` in ZMK vs. `quick-release-ms` in Kanata
- `hold-trigger-key-positions` has different syntax
- `retro-tap` behavior might differ

**Workaround**: Review and adjust hold-tap configurations in the generated Kanata file:

```
;; Original ZMK:
;; &mt LSHIFT A

;; Generated Kanata:
(defalias
  mt_a (tap-hold 200 200 a lsft)
)

;; You might need to adjust timing parameters:
(defalias
  mt_a (tap-hold 200 150 a lsft)
)
```

### 2. Layer Switching

**Description**: ZMK and Kanata have different layer switching mechanisms.

**Limitation**: Layer switching works, but the exact behavior might differ:
- ZMK uses `&mo`, `&to`, `&tog` for different layer behaviors
- Kanata uses `@layer` with different modifiers

**Workaround**: Review and adjust layer switching in the generated Kanata file:

```
;; Original ZMK:
;; &mo 1

;; Generated Kanata:
@layer1

;; You might need to adjust to use a different layer mechanism:
@momentary1
```

### 3. Timing Parameters

**Description**: ZMK and Kanata use different default timing parameters.

**Limitation**: The converter uses standard timing parameters that might not match your preferences.

**Workaround**: Adjust timing parameters in the generated Kanata file:

```
;; Default generated values:
(defvar tap-time 200)
(defvar hold-time 250)

;; Adjust to your preference:
(defvar tap-time 180)
(defvar hold-time 220)
```

## Error Handling Limitations

### 1. Error Reporting

**Description**: The converter reports errors when it encounters unsupported features or syntax.

**Limitation**: Error messages could be more specific in some cases, especially for complex configurations.

**Workaround**: If you encounter an error, try simplifying your ZMK configuration to isolate the issue.

### 2. Recovery from Errors

**Description**: The converter stops on the first error it encounters.

**Limitation**: The converter currently stops on the first error rather than attempting to continue with a partial conversion.

**Workaround**: Fix errors one at a time and run the converter again.

## File Format Limitations

### 1. ZMK File Format

**Description**: The converter expects ZMK files in a specific format.

**Limitation**: The converter might not handle all variations of ZMK file formats, especially custom or non-standard formats.

**Workaround**: Ensure your ZMK file follows the standard format with proper indentation and syntax.

### 2. Kanata Output Format

**Description**: The converter generates Kanata files in a specific format.

**Limitation**: The generated Kanata file might not be optimally formatted for readability or might not use all Kanata features.

**Workaround**: Manually format and optimize the generated Kanata file as needed.

## Conclusion

While the ZMK to Kanata Converter handles most common ZMK features, there are limitations that require manual intervention. By understanding these limitations, you can more effectively use the converter and make the necessary adjustments to your Kanata configuration.

If you encounter issues not listed here, please report them on GitHub to help improve the converter.

---

## FAQ & Troubleshooting

**Q: My combo or macro doesn't work in Kanata.**
A: Only simple combos (e.g., A+B → ESC) are supported. See the relevant section above and manually define complex combos in your Kanata config.

**Q: The converter gives an error about an unsupported feature.**
A: Check this document for workarounds or see the [User Guide](user_guide.md) for more help.

**Q: How do I report a limitation or request support for a feature?**
A: Open an issue on GitHub and describe your use case and ZMK config.

**Q: Where can I get more help?**
A: See the [User Guide](user_guide.md), [README](../README.md), or [CONTRIBUTING.md](../CONTRIBUTING.md).

**Q: My custom home row mod is not working as expected.**
A: Standard properties (timing, flavor, bindings) are mapped. Check the Kanata output for comments about unmapped properties and adjust manually if needed.
