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

**Limitation**: Best-effort mapping is provided for custom hold-tap behaviors (home row mods). Standard properties (timing, flavor, bindings, quick-tap-ms, tap-hold-wait-ms, require-prior-idle-ms) are mapped to Kanata. Advanced properties (e.g., retro-tap, hold-trigger-key-positions, or unknowns) are not supported and are marked with TODO comments in the output for manual review.

**Workaround**: Review the Kanata output for TODO comments about unmapped properties and adjust manually if needed. See the [Hold-Tap Migration Guide](user_guide.md#hold-tap-migration-guide) for best practices and example macros.

| Property                     | Supported? | Notes/Workaround                        |
|------------------------------|------------|-----------------------------------------|
| tapping-term-ms              | ✅         | Fully mapped                            |
| hold-time-ms                 | ✅         | Fully mapped                            |
| flavor                       | ✅         | Fully mapped                            |
| quick-tap-ms                 | ✅         | Mapped if present                       |
| tap-hold-wait-ms             | ✅         | Mapped if present                       |
| require-prior-idle-ms        | ✅         | Mapped if present                       |
| bindings                     | ✅         | Fully mapped                            |
| retro-tap                    | ❌         | TODO comment, manual review needed      |
| hold-trigger-key-positions   | ❌         | TODO comment, manual review needed      |
| (other/unknown properties)   | ❌         | TODO comment, manual review needed      |

> **Note:** If your ZMK config uses advanced hold-tap features, check the Kanata output for TODO comments and review the migration guide.

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

### 3. Unicode Output

**Description**: ZMK supports Unicode output via macros or custom behaviors, allowing you to type arbitrary Unicode characters (e.g., emoji, accented letters).

**Limitation**: Unicode output is supported on macOS via Kanata's (unicode ...) action. It is experimental on Windows and not supported on Linux. On non-macOS platforms, the converter emits a warning comment instead of Unicode output.

**Workaround**: On macOS, Unicode output works out of the box. On Windows, it is experimental and may not work for all characters. On Linux, Unicode output is not supported by Kanata.

**Example:**

- ZMK: `&pi`
- Kanata (macOS): `(unicode "π")`
- Kanata (Windows/Linux): `; WARNING: Unicode output is only supported on macOS (darwin). Unicode 'π' not emitted.`

| Unicode output         | macOS: ✅ | Windows: ⚠️ | Linux: ❌ | See FAQ and workaround |

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

**Reference**: See [User Guide: ZMK Configuration](user_guide.md#zmk-configuration) for examples and details. For the official ZMK keymap spec, see [ZMK Keymap Documentation](https://zmk.dev/docs/keymap/).

**Workaround**: Ensure your ZMK file follows the standard format with proper indentation and syntax.

### 2. Kanata Output Format

**Description**: The converter generates Kanata files in a specific format.

**Limitation**: The generated Kanata file might not be optimally formatted for readability or might not use all Kanata features.

**Reference**: See [User Guide: Kanata Output](user_guide.md#kanata-output) for examples and details. For the official Kanata config spec, see [Kanata Configuration Documentation](https://github.com/jtroo/kanata/blob/master/docs/config.md).

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

**Q: Can I use Unicode output in my Kanata config?**
A: Unicode output is supported on macOS via Kanata's (unicode ...) action. It is experimental on Windows and not supported on Linux. On non-macOS platforms, the converter emits a warning comment instead of Unicode output. See the Kanata documentation for more information.

## What Kanata Could Change or Add to Enable a More Complete Converter

The following are features or changes that, if implemented in Kanata, would allow the ZMK to Kanata Converter to overcome its current limitations and provide more accurate, lossless conversions:

### 1. Advanced Combo Support

- **Feature Needed:**  
  Native support for combos that can trigger not just simple key outputs, but also layer changes, macros, or advanced logic (e.g., combos that activate a layer or run a macro).
- **Benefit:**  
  Would allow the converter to map all ZMK combos, including those with modifiers, macros, or layer actions, without manual intervention.
- **Reference:**  
  See [issue #1556](https://github.com/jtroo/kanata/issues/1556) for user requests and maintainer discussion about shift-layer and remapping shifted keys to arbitrary actions.

### 2. Custom Behavior Extensibility

- **Feature Needed:**  
  A plugin or scripting interface for defining custom behaviors (e.g., advanced hold-tap, retro-tap, or custom mod-tap logic) with flexible parameters.
- **Benefit:**  
  Would enable direct mapping of ZMK's custom behaviors and advanced hold-tap features, reducing the need for TODO comments and manual edits.
- **Reference:**  
  See [issue #1556](https://github.com/jtroo/kanata/issues/1556) and related comments for discussion of extensible behavior needs.

### 3. Macro Enhancements

- **Feature Needed:**  
  Support for complex macros, including:
  - Conditionals (if/else logic)
  - Delays/timing control within macros
  - Macro composition (macros calling other macros)
- **Benefit:**  
  Would allow the converter to fully translate ZMK macros, including those with advanced logic or timing requirements.
- **Reference:**  
  See [discussion #1578](https://github.com/jtroo/kanata/discussions/1578) for user workarounds and limitations with macros and external scripting.

### 4. Unicode Input and Output Improvements

- **Feature Needed:**  
  - Full Unicode input/output support on all platforms (not just macOS).
  - Consistent Unicode handling in macros and behaviors.
- **Benefit:**  
  Would enable the converter to support ZMK's Unicode features everywhere, not just on macOS.
- **Reference:**  
  See [issue #1556](https://github.com/jtroo/kanata/issues/1556) and [discussion #1578](https://github.com/jtroo/kanata/discussions/1578) for Unicode limitations and user workarounds.

### 5. Advanced Modifier and Sticky Modifier Support

- **Feature Needed:**  
  - More flexible modifier handling, including sticky modifiers and advanced modifier combinations.
  - Ability to define and use custom modifier behaviors.
- **Benefit:**  
  Would allow for accurate conversion of ZMK's advanced modifier features.
- **Reference:**  
  See [issue #1556](https://github.com/jtroo/kanata/issues/1556) for user requests and discussion of modifier handling.

### 6. Layer Switching Parity

- **Feature Needed:**  
  - Support for all ZMK layer switching semantics (e.g., momentary, toggle, one-shot, etc.) with matching syntax and behavior.
- **Benefit:**  
  Would allow the converter to map all ZMK layer actions directly, without approximation.
- **Reference:**  
  See [issue #413](https://github.com/jtroo/kanata/issues/413) and [discussion #422](https://github.com/jtroo/kanata/discussions/422) for edge cases and limitations in layer switching.

### 7. Error Reporting and Recovery

- **Feature Needed:**  
  - Structured error reporting and partial config loading, so that Kanata can load and report on incomplete or partially invalid configs.
- **Benefit:**  
  Would allow the converter to emit partial configs with warnings, improving the user experience during migration.
- **Reference:**  
  See [README](https://github.com/jtroo/kanata#how-you-can-help) and general feedback in issues for ongoing usability improvements.

### 8. Config Import/Include Mechanism

- **Feature Needed:**  
  - A robust include/import system for Kanata configs, similar to C preprocessor includes in ZMK.
- **Benefit:**  
  Would allow the converter to map ZMK's modular config structure more directly.
- **Reference:**  
  No direct issue, but this is a common feature in QMK/ZMK and is missing in Kanata.

---

**If these features are added to Kanata, the converter could achieve near-perfect, lossless conversion of ZMK keymaps, minimizing or eliminating the need for manual adjustments.**

---

**Kanata users and developers:**  
If you would like to see these features, consider opening feature requests or contributing to the Kanata project