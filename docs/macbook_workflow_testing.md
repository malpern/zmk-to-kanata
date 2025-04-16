# Testing Workflow: ZMK Configurator to MacBook Keyboard

## Overview
This document outlines how to test the complete workflow from using a ZMK configurator to create a keymap, converting it to Kanata format, and applying it to a MacBook's built-in keyboard. This workflow effectively turns any ZMK configurator into a MacBook keyboard configurator.

## Step 1: Create a ZMK Keymap using a ZMK Configurator
1. Access a ZMK configurator web interface (such as Nick's configurator)
2. Design a simple keymap with:
   - A base layer with some remapped keys (e.g., swap Caps Lock and Escape)
   - A function layer accessible via a hold action
   - A macro for a frequently used text string
   - A Unicode character binding
3. Export the ZMK keymap file

## Step 2: Convert the ZMK Keymap to Kanata Format
1. Use the ZMK to Kanata converter:
   ```
   python -m converter.cli path/to/zmk_keymap.keymap path/to/output.kbd
   ```
2. Verify the output file contains the expected Kanata configuration:
   - Check that layers are correctly defined
   - Verify hold-tap behaviors are properly translated
   - Confirm macros are correctly converted
   - Ensure Unicode bindings are properly formatted

## Step 3: Install and Configure Kanata on the MacBook
1. Install Kanata on the MacBook:
   ```
   brew install kanata
   ```
2. Place the converted Kanata configuration file in an appropriate location:
   ```
   cp path/to/output.kbd ~/.config/kanata/config.kbd
   ```

## Step 4: Test the Configuration on the MacBook's Built-in Keyboard
1. Launch Kanata with the configuration:
   ```
   kanata -c ~/.config/kanata/config.kbd
   ```
2. Test each feature of the keymap:
   - Verify basic key remappings work
   - Test layer switching functionality
   - Execute the defined macro
   - Input the Unicode character
3. Document any discrepancies between expected and actual behavior

## Step 5: Iterate and Refine
1. If issues are found, determine whether they're related to:
   - The ZMK configuration
   - The conversion process
   - Kanata implementation
2. Make necessary adjustments to the converter or configuration
3. Repeat the testing process until the workflow functions as expected

## Documentation
Throughout the testing process, document:
1. Any limitations discovered
2. Workarounds for common issues
3. Best practices for creating ZMK configurations that convert well to Kanata
4. Setup instructions for end users

## Supported Features
The current implementation supports:
- Multiple layers
- Hold-tap behaviors (for modifier keys, layer switching, etc.)
- Sticky keys
- Key sequences
- Macros
- Unicode input

## Limitations
- No support for advanced ZMK features like combos
- Limited to standard keyboard layouts
- Some hardware-specific ZMK features have no Kanata equivalent

This comprehensive testing approach will validate the entire workflow and ensure that ZMK configurators can effectively serve as MacBook keyboard configurators when paired with the converter and Kanata.
