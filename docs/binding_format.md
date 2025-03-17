# ZMK Binding Format Guide

## Overview

This guide explains the various binding formats supported by the ZMK to Kanata converter. It covers basic key bindings, modifiers, layers, and special behaviors like hold-tap and macros.

## Basic Bindings

### Key Press (&kp)

```zmk
&kp <key_code>
```

Examples:
```zmk
&kp A          // Letter A
&kp N1         // Number 1
&kp SPACE      // Space key
&kp SEMICOLON  // Semicolon key
```

### Modifiers

```zmk
&kp <modifier>
&kp <modifier>+<key>
```

Examples:
```zmk
&kp LSHIFT      // Left Shift
&kp LCTRL       // Left Control
&kp LGUI        // Left GUI (Windows/Command)
&kp LALT        // Left Alt
&kp LSHIFT+A    // Shift + A
```

## Layer Behaviors

### Momentary Layer (&mo)

```zmk
&mo <layer>
```

Activates layer while held:
```zmk
&mo 1    // Activate layer 1 while held
&mo 2    // Activate layer 2 while held
```

### Toggle Layer (&tog)

```zmk
&tog <layer>
```

Toggles layer on/off:
```zmk
&tog 1    // Toggle layer 1
&tog 2    // Toggle layer 2
```

### Layer Tap (&lt)

```zmk
&lt <layer> <key>
```

Tap for key, hold for layer:
```zmk
&lt 1 ESC     // Tap for ESC, hold for layer 1
&lt 2 SPACE   // Tap for SPACE, hold for layer 2
```

## Special Behaviors

### Hold-Tap (&ht)

```zmk
&ht <hold_behavior> <tap_behavior>
```

Examples:
```zmk
&ht LSHIFT A    // Hold for SHIFT, tap for A
&ht LCTRL B     // Hold for CTRL, tap for B
&ht LGUI TAB    // Hold for GUI, tap for TAB
```

### Sticky Key (&sk)

```zmk
&sk <modifier>
```

Examples:
```zmk
&sk LSHIFT    // Sticky Shift
&sk LCTRL     // Sticky Control
&sk LALT      // Sticky Alt
```

### Macros

```zmk
macro_name: macro_name {
    compatible = "zmk,behavior-macro";
    bindings = <...>;
    wait-ms = <time>;    // Optional
    tap-ms = <time>;     // Optional
};
```

Example:
```zmk
copy_paste: copy_paste {
    compatible = "zmk,behavior-macro";
    bindings = <
        &kp LCTRL &kp C  // Copy
        &macro_wait_time 100
        &kp LCTRL &kp V  // Paste
    >;
};
```

## Binding Arrays

Bindings are grouped in arrays using angle brackets:

```zmk
bindings = <
    &kp A &kp B &kp C
    &mo 1 &tog 2 &lt 3 SPACE
>;
```

## Layer Definition

Complete layer example:

```zmk
default_layer {
    bindings = <
        &kp A      &kp B       &kp C
        &mo 1      &lt 2 SPACE &sk LSHIFT
        &ht LCTRL Z &tog 3     &macro_name
    >;
};
```

## Common Patterns

### Modifier Combinations

```zmk
// Control + Shift + Key
&kp LC(LS(A))    // Ctrl + Shift + A

// GUI + Alt + Key
&kp LG(LA(TAB))  // GUI + Alt + Tab
```

### Layer Access Patterns

```zmk
// Common thumb key pattern
&lt 1 SPACE    // Tap for space, hold for layer 1
&mo 2          // Momentary layer 2
&tog 3         // Toggle layer 3
```

### Sticky Modifier Combinations

```zmk
// Multiple sticky modifiers
&sk LSHIFT
&sk LCTRL
```

## Validation Rules

1. **Key Codes**
   - Must be valid ZMK key codes
   - Case sensitive
   - No spaces in key names

2. **Layer References**
   - Must reference existing layers
   - Layer numbers must be valid
   - Cannot reference current layer

3. **Behavior Parameters**
   - Must match behavior requirements
   - Numbers must be within valid ranges
   - Required parameters cannot be omitted

## Error Examples

### Invalid Formats

```zmk
&kp a           // Invalid: key code must be uppercase
&mo LAYER1      // Invalid: layer must be number
&ht SHIFT       // Invalid: missing tap behavior
```

### Correct Formats

```zmk
&kp A           // Valid: uppercase key code
&mo 1           // Valid: numeric layer reference
&ht LSHIFT A    // Valid: both behaviors specified
```

## Best Practices

1. **Readability**
   - Align bindings in grid format
   - Use comments for complex bindings
   - Group related bindings together

2. **Maintainability**
   - Use descriptive layer names
   - Document non-obvious behaviors
   - Keep macro definitions organized

3. **Reliability**
   - Test all layer transitions
   - Verify modifier combinations
   - Ensure consistent behavior across layers 

## Nested Behaviors

Some ZMK behaviors can be nested within others, but there are important restrictions to ensure proper functionality:

### Valid Nested Behaviors

1. **Layer-tap with Key Press**
   ```zmk
   &lt 1 &kp A  // Layer 1 when held, types 'A' when tapped
   ```

2. **Layer-tap with Momentary Layer**
   ```zmk
   &lt 2 &mo 3  // Layer 2 when held, momentarily activates layer 3 when tapped
   ```

### Invalid Nested Behaviors

The following combinations are not supported and will be converted to "unknown" bindings:

1. **Hold-tap with Sticky Key**
   ```zmk
   &ht LSHIFT (&sk LCTRL)  // Not supported
   ```

2. **Sticky Key with Hold-tap**
   ```zmk
   &sk (&ht LALT A)  // Not supported
   ```

3. **Nested Hold-taps**
   ```zmk
   &ht LSHIFT (&ht LCTRL A)  // Not supported
   ```

4. **Layer-tap with Nested Layer**
   ```zmk
   &lt 1 (&mo 2)  // Not supported
   ```

### Nesting Rules

1. **Hold-tap Behaviors**
   - Cannot be nested within other behaviors
   - Can only contain simple key mappings or layer behaviors in the hold position

2. **Layer Behaviors**
   - Can be used in hold position of hold-tap behaviors
   - Cannot be nested within other layer behaviors

3. **Sticky Key Behaviors**
   - Cannot be nested within other behaviors
   - Cannot contain nested behaviors

4. **Macro Behaviors**
   - Cannot be nested within other behaviors
   - Cannot contain nested behaviors

5. **Key Sequence Behaviors**
   - Cannot be nested within other behaviors
   - Cannot contain nested behaviors

### Error Handling

When an invalid nested behavior is encountered:
1. The behavior will be converted to an "unknown" binding
2. A warning will be logged
3. The conversion will continue with the next binding

### Best Practices

1. Keep behavior nesting simple and avoid complex combinations
2. Use layer-tap with key press as the primary nested behavior
3. Test complex combinations before deploying to ensure proper functionality
4. Consider using simpler alternatives when possible 