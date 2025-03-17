# ZMK to Kanata Converter Troubleshooting Guide

## Common Issues and Solutions

### Syntax Errors

#### 1. Missing Closing Brace

**Problem:**
```zmk
default_layer {
    bindings = <
        &kp A &kp B
    >;
// Missing closing brace
```

**Solution:**
- Check for matching braces in each block
- Ensure all sections are properly closed
- Use an editor with brace matching

#### 2. Invalid Binding Syntax

**Problem:**
```zmk
bindings = <
    &kp A &kp> B  // Invalid syntax
>;
```

**Solution:**
- Remove extra characters (>, <, etc.)
- Ensure proper spacing between bindings
- Check binding format guide for correct syntax

#### 3. Missing Angle Brackets

**Problem:**
```zmk
bindings = 
    &kp A &kp B
;
```

**Solution:**
- Add opening and closing angle brackets
- Correct format: `bindings = <...>;`
- Check all binding arrays for proper delimiters

### Layer Issues

#### 1. Undefined Layer Reference

**Problem:**
```zmk
&mo UNDEFINED_LAYER  // Layer doesn't exist
```

**Solution:**
- Use numeric layer references (e.g., `&mo 1`)
- Ensure referenced layers are defined
- Check layer numbers are within valid range

#### 2. Duplicate Layer Names

**Problem:**
```zmk
default_layer {
    // Layer content
};
default_layer {  // Duplicate name
    // More content
};
```

**Solution:**
- Use unique names for each layer
- Check for typos in layer names
- Consider using numbered suffixes for similar layers

#### 3. Missing Default Layer

**Problem:**
```zmk
// No default_layer defined
layer_1 {
    // Layer content
};
```

**Solution:**
- Add a default_layer definition
- Ensure it's the first layer defined
- Include basic key mappings

### Macro Issues

#### 1. Invalid Macro Bindings

**Problem:**
```zmk
test_macro: test_macro {
    compatible = "zmk,behavior-macro";
    bindings = "invalid";  // Should be array
};
```

**Solution:**
- Use angle brackets for bindings array
- Include valid key codes or behaviors
- Follow macro binding format

#### 2. Invalid Timing Parameters

**Problem:**
```zmk
test_macro: test_macro {
    wait-ms = "100";  // Should be <100>
    tap-ms = invalid;
};
```

**Solution:**
- Use angle brackets for timing values
- Ensure values are numeric
- Keep values within reasonable range

#### 3. Missing Compatible Field

**Problem:**
```zmk
test_macro: test_macro {
    bindings = <&kp A &kp B>;
};
```

**Solution:**
- Add compatible = "zmk,behavior-macro"
- Check macro documentation for required fields
- Ensure proper macro structure

### Behavior Issues

#### 1. Invalid Hold-Tap Parameters

**Problem:**
```zmk
&ht INVALID A  // Invalid modifier
```

**Solution:**
- Use valid modifier names (LSHIFT, LCTRL, etc.)
- Check behavior documentation for valid parameters
- Ensure both hold and tap behaviors are specified

#### 2. Invalid Sticky Key Parameters

**Problem:**
```zmk
&sk INVALID  // Invalid key
```

**Solution:**
- Use valid modifier names
- Check sticky key documentation
- Ensure proper parameter format

#### 3. Invalid Key Codes

**Problem:**
```zmk
&kp a  // Lowercase invalid
&kp KEY_A  // Invalid format
```

**Solution:**
- Use uppercase key codes
- Follow ZMK key code format
- Check key code documentation

## Performance Issues

### 1. Slow Processing

**Symptoms:**
- Long conversion times
- High CPU usage
- Delayed response

**Solutions:**
- Reduce configuration size
- Split into multiple files
- Optimize macro definitions
- Remove unused layers

### 2. Memory Issues

**Symptoms:**
- Out of memory errors
- Slow performance
- System unresponsive

**Solutions:**
- Reduce number of layers
- Simplify macro definitions
- Split large configurations
- Clean up unused definitions

## Error Messages

### 1. Understanding Error Output

```
Error: Syntax error at line 10
Expected: '}'
Found: ';'
Context: default_layer
```

**Components:**
- Error type (Syntax error)
- Location (line number)
- Expected token
- Found token
- Context (current section)

### 2. Common Error Messages

#### Parser Errors
- "Syntax error at line X"
- "Missing required field"
- "Invalid binding format"
- "Unknown behavior"

#### Validation Errors
- "Duplicate layer name"
- "Invalid layer reference"
- "Invalid key code"
- "Invalid parameter"

#### Runtime Errors
- "Memory limit exceeded"
- "Stack overflow"
- "Maximum recursion depth"

## Prevention Tips

### 1. Code Organization

- Use consistent indentation
- Group related bindings
- Comment complex configurations
- Keep files modular

### 2. Testing

- Test each layer individually
- Verify all transitions
- Check macro timing
- Validate key combinations

### 3. Maintenance

- Regular syntax validation
- Remove unused definitions
- Update documentation
- Keep backups

## Getting Help

### 1. Debugging Steps

1. Check syntax
2. Validate configuration
3. Test in isolation
4. Review error messages
5. Check documentation

### 2. Reporting Issues

Include:
- Error message
- Configuration snippet
- Steps to reproduce
- Expected behavior
- Actual behavior

### 3. Resources

- Documentation
- Binding format guide
- State machine guide
- Example configurations

## Common Binding Parser Issues

### Invalid Behavior Errors

**Issue**: Error message like `Invalid behavior '&invalid'` or `Unknown binding type`

**Cause**: The parser encountered a binding behavior that is not recognized. This could be due to:
- Typos in behavior names (e.g., `&kp` misspelled as `&kpp`)
- Using custom behaviors that are not supported by the converter
- Missing whitespace between behavior and parameters

**Solution**:
1. Check for typos in your ZMK config and correct them
2. Ensure all behaviors used are supported by the converter
3. Add proper spacing between behavior names and parameters:
   ```
   // WRONG
   &kpA
   
   // CORRECT
   &kp A
   ```

### Parameter Validation Errors

**Issue**: Error messages like `Invalid parameter for &lt: expected integer, got 'INVALID'`

**Cause**: The binding parameters don't match what the behavior expects:
- Wrong parameter type (e.g., text instead of number for layer index)
- Missing required parameters
- Extra parameters that aren't supported

**Solution**:
1. Check the binding documentation to confirm the correct parameters
2. For layer bindings (`&mo`, `&lt`, etc.), ensure layer numbers are integers
3. For mod-tap bindings (`&mt`), ensure the modifier is valid:
   ```
   // WRONG
   &lt TEXT A
   
   // CORRECT
   &lt 1 A
   ```

### Nested Binding Errors

**Issue**: Error messages like `Invalid nested binding` or `Unmatched parentheses`

**Cause**: Issues with nested binding syntax:
- Mismatched or missing parentheses
- Malformed inner binding
- Unsupported nesting combinations

**Solution**:
1. Check parentheses matching and ensure they are properly balanced
2. Verify the inner binding is valid on its own
3. Use supported nesting patterns:
   ```
   // WRONG
   &lt 1 (&invalid X)
   &lt 1 (X)  // Missing behavior in nested binding
   
   // CORRECT
   &lt 1 (&kp A)
   &mt LSHIFT (&kp B)
   ```

### Binding Syntax Errors

**Issue**: Error messages like `Binding format error` or `Unexpected token`

**Cause**: General syntax issues in binding definitions:
- Missing & prefix before behavior name
- Extra/unexpected characters in binding definitions
- Invalid ZMK syntax

**Solution**:
1. Ensure all behaviors start with an ampersand (&)
2. Remove any unexpected characters or comments within binding lines
3. Follow ZMK binding syntax rules:
   ```
   // WRONG
   kp A       // Missing &
   &kp A;     // Extra semicolon
   
   // CORRECT
   &kp A
   ```

## Layer-Related Issues

### Missing or Invalid Layer

**Issue**: Error message like `Layer not found` or `Invalid layer reference`

**Cause**: Referencing a layer that doesn't exist or has an invalid definition:
- Layer number in `&mo`, `&lt`, etc. references non-existent layer
- Layer definition is malformed

**Solution**:
1. Ensure all referenced layer numbers actually exist in your keymap
2. Check layer definitions for syntax errors
3. Make sure layer indices start from 0 for the default layer

### Inconsistent Layer Size

**Issue**: Warning message like `Inconsistent row count in layer`

**Cause**: Different layers have different numbers of keys:
- Missing or extra keys in some layers
- Rows not properly aligned

**Solution**:
1. Ensure all layers have the same number of keys
2. Add `&trans` for transparent/pass-through keys where needed
3. Align rows consistently across all layers

## Macro Issues

### Macro Definition Not Found

**Issue**: Error message like `Macro not found` or `Referenced macro undefined`

**Cause**: Referencing a macro that isn't defined:
- Typo in macro name
- Macro definition missing
- Macro defined after it's used

**Solution**:
1. Ensure macro names match exactly between definition and usage
2. Define all macros before using them in bindings
3. Check for typos in macro names

### Macro Parameter Errors

**Issue**: Error message like `Wrong number of parameters for macro`

**Cause**: Providing incorrect parameters to parameterized macros:
- Missing required parameters
- Too many parameters
- Wrong parameter types

**Solution**:
1. Check macro definition to confirm required parameter count
2. Ensure correct number of parameters are provided
3. Verify parameter types match what the macro expects

## General Issues

### File Parsing Errors

**Issue**: Error message like `Failed to parse ZMK file` or `Unexpected EOF`

**Cause**: General file structure issues:
- Incomplete file content
- Missing closing brackets or braces
- Severe syntax errors

**Solution**:
1. Validate your ZMK file structure with proper opening/closing brackets
2. Ensure the file is complete and not truncated
3. Use an IDE or text editor with syntax highlighting to spot errors

### Invalid Key Names

**Issue**: Error message like `Invalid key: 'XYZ'`

**Cause**: Key names that aren't recognized:
- Using ZMK key names not supported in Kanata
- Typos in key names
- Custom keycodes not available in Kanata

**Solution**:
1. Use standard key names supported by both ZMK and Kanata
2. Check for typos in key names
3. Replace custom keycodes with standard ones or macros

## Error Recovery

The converter includes error recovery mechanisms that attempt to handle issues gracefully. When errors occur:

1. Invalid bindings are replaced with `unknown` in the Kanata output
2. Error details are logged with line numbers and context
3. The converter attempts to continue processing the rest of the file

To get more detailed error information, check the error report that may be generated alongside the converted file.

## Getting Help

If you encounter issues not covered in this guide:

1. Check if your ZMK file is valid and works with ZMK firmware
2. Verify your keymap syntax against the ZMK documentation
3. Try simplifying your keymap to isolate the problematic sections
4. Review the error messages and line numbers to identify the exact issue location 