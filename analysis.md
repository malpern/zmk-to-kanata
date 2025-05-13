# ZMK-to-Kanata Conversion Analysis Methodology

This document describes a repeatable, step-by-step methodology for analyzing the correctness and fidelity of ZMK-to-Kanata conversions. Use this process for regression testing, debugging, and confidence-building in the converter pipeline.

---

## 1. Preparation
- **Identify the input ZMK file** to be tested (e.g., `examples/basic_keymap.dtsi`).
- **Locate or define the expected/golden Kanata output** (e.g., `.kbd` or `.kanata.yaml` files).
- **Ensure the converter CLI and all debug/dump flags are available.**

## 2. Run the Converter with Full Debug and Dump Flags
- Use the CLI to run the converter with flags to dump:
  - Preprocessed DTS (`--dump-preprocessed`)
  - Parsed AST (`--dump-ast`)
  - Extracted keymap model (`--dump-extracted`)
  - Final Kanata output (`--output`)
  - Enable debug logging (`--debug`)
- Save all intermediate and final outputs for inspection.

## 3. Collect and Organize Outputs
- Input ZMK (DTS)
- Preprocessed DTS
- Parsed AST (JSON)
- Extracted keymap model (YAML/JSON)
- Final Kanata output (YAML or .kbd)
- Golden/reference output (if available)

## 4. Detailed Comparison and Analysis
- **Compare each stage:**
  - Input ZMK (structure, layers, behaviors, macros)
  - Preprocessed DTS (includes/macros expanded)
  - AST (all nodes/properties parsed correctly)
  - Extracted model (all layers, keys, behaviors present and correct)
  - Kanata output (all ZMK features faithfully represented)
- **Look for:**
  - Missing keys/layers/behaviors
  - Incorrect mappings or omissions
  - Structural errors or warnings in logs
  - Differences from golden/reference output

## 5. Methodology for Confidence
- **Golden File Comparison:**
  - Compare generated Kanata output to a known-good (golden) file. Any differences are flagged for review.
- **Property-Based Checks:**
  - Ensure the number of keys, their order, and their names match between ZMK input and Kanata output.
- **Intermediate Output Inspection:**
  - Check that each stage does not introduce spurious tokens or lose information.
- **Manual Review:**
  - Visually inspect the output for obvious errors (e.g., invalid tokens, missing keys).
- **Regression Testing:**
  - Use golden files for automated regression tests.

## 6. Reporting and Next Steps
- **Document findings:**
  - Note any errors, omissions, or mismatches.
  - Suggest root causes and next steps for debugging or improvement.
- **Iterate:**
  - Fix issues, rerun the analysis, and repeat until the output is correct and robust.

---

## Example CLI Command

```
zmk-kanata examples/basic_keymap.dtsi \
  --dump-preprocessed preprocessed.dts \
  --dump-ast ast.json \
  --dump-extracted extracted.yaml \
  --output kanata.yaml \
  --debug
```

---

## Summary
- This methodology ensures thorough, multi-stage validation of the conversion process.
- By capturing all intermediate states, you can pinpoint where issues arise and build confidence in the converter's correctness. 