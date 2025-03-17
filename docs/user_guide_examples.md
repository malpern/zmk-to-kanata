# ZMK to Kanata Converter User Guide

This guide provides comprehensive instructions and examples for using the ZMK to Kanata converter.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Command-Line Options](#command-line-options)
4. [Input Format](#input-format)
5. [Output Format](#output-format)
6. [Binding Conversion Examples](#binding-conversion-examples)
7. [Layer Management](#layer-management)
8. [Macro Conversion](#macro-conversion)
9. [Error Handling](#error-handling)
10. [Known Limitations](#known-limitations)
11. [Advanced Usage](#advanced-usage)
12. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or later

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/zmk-to-kanata.git
cd zmk-to-kanata

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Install via pip

```bash
pip install zmk-to-kanata
```

## Basic Usage

Convert a ZMK keymap file to Kanata format:

```bash
zmk-to-kanata input.zmk output.kbd
```

The converter reads your ZMK keymap file and produces a Kanata configuration file with equivalent functionality.

## Command-Line Options

```
Usage: zmk-to-kanata [OPTIONS] INPUT_FILE OUTPUT_FILE

Options:
  --version     Show program's version number and exit
  -h, --help    Show this help message and exit
```

## Input Format

The converter expects a standard ZMK keymap file as input. A basic ZMK keymap follows this structure:

```
/ {
    keymap {
        compatible = "zmk,keymap";
        
        default_layer {
            bindings = <
                &kp A &kp B &kp C
                &kp D &kp E &kp F
            >;
        };
        
        layer_1 {
            bindings = <
                &kp X &kp Y &kp Z
                &kp U &kp V &kp W
            >;
        };
    };
};
```

## Output Format

The converter produces a Kanata configuration file with equivalent functionality. A basic output looks like:

```
;; ZMK to Kanata Configuration
;; Generated automatically - DO NOT EDIT

;; Global settings
(defvar tap-time 200)
(defvar hold-time 250)

(deflayer default
  A B C
  D E F
)

(deflayer layer_1
  X Y Z
  U V W
)
```

## Binding Conversion Examples

The converter supports various ZMK binding types and converts them to Kanata equivalents:

### Basic Key Bindings

| ZMK Binding | Kanata Equivalent | Description |
|-------------|------------------|-------------|
| `&kp A` | `A` | Basic key press |
| `&kp SPACE` | `spc` | Space key |
| `&kp ENTER` | `ret` | Enter/Return key |
| `&kp LSHIFT` | `lsft` | Left shift modifier |
| `&kp LGUI` | `lmeta` | Left GUI/Windows/Command key |

### Layer Management

| ZMK Binding | Kanata Equivalent | Description |
|-------------|------------------|-------------|
| `&mo 1` | `mo(1)` | Momentary layer activation |
| `&tog 2` | `tog(2)` | Toggle layer on/off |
| `&to 3` | `to(3)` | Switch to specific layer |
| `&lt 1 A` | `lt(1,A)` | Layer-tap: Layer when held, key when tapped |

### Special Bindings

| ZMK Binding | Kanata Equivalent | Description |
|-------------|------------------|-------------|
| `&mt LSHIFT A` | `mt(lsft,A)` | Mod-tap: Modifier when held, key when tapped |
| `&sk LSHIFT` | `sk(lsft)` | Sticky key (one-shot modifier) |
| `&trans` | `_` | Transparent/pass-through key |

### Nested Bindings

| ZMK Binding | Kanata Equivalent | Description |
|-------------|------------------|-------------|
| `&lt 1 (&kp A)` | `lt(1,A)` | Layer-tap with nested key press |
| `&mt LSHIFT (&kp B)` | `mt(lsft,B)` | Mod-tap with nested key press |
| `&lt 2 (&mt LCTRL C)` | `lt(2,mt(lctrl,C))` | Complex nesting of behaviors |

## Layer Management

### Layer Definition

ZMK layers are converted to Kanata layers:

**ZMK:**
```
default_layer {
    bindings = <
        &kp A &kp B &kp C
        &kp D &kp E &kp F
    >;
};
```

**Kanata:**
```
(deflayer default
  A B C
  D E F
)
```

### Layer Switching

Layer-switching bindings are translated as follows:

**ZMK:**
```
default_layer {
    bindings = <
        &mo 1  &tog 2  &to 3
        &lt 1 A &trans &kp B
    >;
};
```

**Kanata:**
```
(deflayer default
  mo(1) tog(2) to(3)
  lt(1,A) _ B
)
```

## Macro Conversion

ZMK macros are converted to Kanata macros:

**ZMK:**
```
/ {
    macros {
        test_macro: test_macro {
            label = "test macro";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&kp A &kp B &kp C>;
        };
    };
    
    keymap {
        compatible = "zmk,keymap";
        
        default_layer {
            bindings = <
                &test_macro &kp D
            >;
        };
    };
};
```

**Kanata:**
```
(defmacro test_macro
  A B C
)

(deflayer default
  @test_macro D
)
```

### Parameterized Macros

Macros with parameters are also supported:

**ZMK:**
```
param_macro: param_macro {
    label = "parameterized macro";
    compatible = "zmk,behavior-macro-two-param";
    #binding-cells = <2>;
    bindings = <&macro_param_1to1>, <&macro_param_2to1>;
};
```

**Kanata:**
```
(defmacro param_macro (param1 param2)
  @param1 @param2
)
```

## Error Handling

The converter includes robust error handling:

1. Invalid bindings are replaced with `unknown` in the output
2. Error details are logged during conversion
3. The converter attempts to continue processing the file despite errors

When errors occur, inspect the console output for detailed information.

## Known Limitations

The ZMK to Kanata converter has some known limitations and constraints that users should be aware of:

- Nested layers within ZMK keymap files are not supported
- Some complex nested behaviors may not convert correctly
- Conditional layers require special handling

For a complete list of limitations and workarounds, please refer to the [Limitations Documentation](limitations.md).

## Advanced Usage

### Homerow Mods

The converter fully supports ZMK homerow mods (`&hm`) and converts them to Kanata's `tap-hold` functionality. Homerow mods are a popular ergonomic feature that allows keys to act as modifiers when held and normal keys when tapped.

#### Mac-Specific Modifiers

For Mac users, the converter provides a `--mac` flag that ensures the GUI modifier is correctly mapped to the Command (CMD) key in Kanata:

```bash
zmk-to-kanata input.dtsi -o output.kbd --mac
```

#### Example ZMK Homerow Mods

Here's an example of homerow mods in ZMK:

```
&kp ESC   &hm LGUI A &hm LALT S &hm LCTRL D &hm LSHFT F &kp G
&kp H &hm RSHFT J  &hm RCTRL K &hm RALT L &hm RGUI SEMI &kp SQT
```

This will be converted to Kanata's tap-hold format:

```
esc (tap-hold 200 200 a lmet) (tap-hold 200 200 s lalt) (tap-hold 200 200 d lctl) (tap-hold 200 200 f lsft) g
h (tap-hold 200 200 j rsft) (tap-hold 200 200 k rctl) (tap-hold 200 200 l ralt) (tap-hold 200 200 ; rmet) '
```

When using the `--mac` flag, the GUI modifiers will be mapped to the Command key.

## Troubleshooting

### Common Issues

1. **Binding Not Converted Correctly**
   
   Check if the binding type is supported. See the [Binding Conversion Examples](#binding-conversion-examples) section.

2. **Layers Not Appearing in Output**

   Ensure your layer definitions follow ZMK syntax requirements.

3. **Macros Not Working**

   Verify your macro definitions are correctly formatted in the ZMK file.

4. **Syntax Errors**

   Validate your ZMK file syntax before conversion.

5. **Missing Keys**

   Ensure all keys in your ZMK file use standard key codes.

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [troubleshooting documentation](troubleshooting.md)
2. Verify your ZMK file against ZMK documentation
3. Simplify your keymap to isolate problematic sections

## Complete Examples

### Basic Keyboard Layout

**ZMK Input:**
```
/ {
    keymap {
        compatible = "zmk,keymap";
        
        default_layer {
            bindings = <
                &kp Q &kp W &kp E &kp R &kp T   &kp Y &kp U &kp I &kp O &kp P
                &kp A &kp S &kp D &kp F &kp G   &kp H &kp J &kp K &kp L &kp SEMI
                &kp Z &kp X &kp C &kp V &kp B   &kp N &kp M &kp COMMA &kp DOT &kp SLASH
                          &kp LGUI &mo 1 &kp SPACE   &kp ENTER &mo 2 &kp RALT
            >;
        };
        
        lower_layer {
            bindings = <
                &kp N1 &kp N2 &kp N3 &kp N4 &kp N5   &kp N6 &kp N7 &kp N8 &kp N9 &kp N0
                &kp TAB &trans &trans &trans &trans   &kp LEFT &kp DOWN &kp UP &kp RIGHT &kp BSPC
                &kp LSHIFT &trans &trans &trans &trans   &trans &trans &trans &trans &trans
                          &trans &trans &trans   &trans &trans &trans
            >;
        };
        
        raise_layer {
            bindings = <
                &kp EXCL &kp AT &kp HASH &kp DLLR &kp PRCNT   &kp CARET &kp AMPS &kp STAR &kp LPAR &kp RPAR
                &kp ESC &trans &trans &trans &trans   &kp MINUS &kp EQUAL &kp LBKT &kp RBKT &kp BSLH
                &kp LSHIFT &trans &trans &trans &trans   &kp UNDER &kp PLUS &kp LBRC &kp RBRC &kp PIPE
                          &trans &trans &trans   &trans &trans &trans
            >;
        };
    };
};
```

**Kanata Output:**
```
;; ZMK to Kanata Configuration
;; Generated automatically - DO NOT EDIT

;; Global settings
(defvar tap-time 200)
(defvar hold-time 250)

(deflayer default
  q w e r t   y u i o p
  a s d f g   h j k l ;
  z x c v b   n m , . /
    lmeta mo(1) spc   ret mo(2) ralt
)

(deflayer lower_layer
  1 2 3 4 5   6 7 8 9 0
  tab _ _ _ _   left down up right bspc
  lsft _ _ _ _   _ _ _ _ _
    _ _ _   _ _ _
)

(deflayer raise_layer
  ! @ # $ %   ^ & * ( )
  esc _ _ _ _   - = [ ] \
  lsft _ _ _ _   _ + { } |
    _ _ _   _ _ _
)
```

### Complex Keyboard with Macros

**ZMK Input:**
```
/ {
    macros {
        email: email {
            label = "email";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&kp U &kp S &kp E &kp R &kp AT &kp E &kp X &kp A &kp M &kp P &kp L &kp E &kp DOT &kp C &kp O &kp M>;
        };
        
        save: save {
            label = "save file";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&kp LCTRL &kp S>;
        };
    };
    
    keymap {
        compatible = "zmk,keymap";
        
        default_layer {
            bindings = <
                &kp ESC  &kp Q  &kp W  &kp E  &kp R  &kp T  &kp Y  &kp U  &kp I     &kp O    &kp P     &kp BSPC
                &kp TAB  &kp A  &kp S  &kp D  &kp F  &kp G  &kp H  &kp J  &kp K     &kp L    &kp SEMI  &kp SQT
                &kp LSHFT &kp Z  &kp X  &kp C  &kp V  &kp B  &kp N  &kp M  &kp COMMA &kp DOT  &kp SLASH &kp RET
                &kp LCTRL &kp LGUI &kp LALT &mo 1 &lt 2 SPACE &lt 2 SPACE &mo 3 &mt RALT BSPC &email &save &kp RCTRL
            >;
        };
        
        // Additional layers omitted for brevity
    };
};
```

**Kanata Output:**
```
;; ZMK to Kanata Configuration
;; Generated automatically - DO NOT EDIT

;; Global settings
(defvar tap-time 200)
(defvar hold-time 250)

(defmacro email
  u s e r @ e x a m p l e . c o m
)

(defmacro save
  lctrl s
)

(deflayer default
  esc q w e r t y u i o p bspc
  tab a s d f g h j k l ; '
  lsft z x c v b n m , . / ret
  lctrl lmeta lalt mo(1) lt(2,spc) lt(2,spc) mo(3) mt(ralt,bspc) @email @save rctrl
)

;; Additional layers omitted for brevity
```

## Conclusion

This guide covers the basics of using the ZMK to Kanata converter. For more advanced usage, refer to the full documentation or check the examples provided with the converter. 