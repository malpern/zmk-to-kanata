# ZMK to Kanata Converter User Guide

Welcome! This guide will help you use the ZMK to Kanata Converter to
transform your ZMK keyboard configuration files into Kanata format.

- For installation and quick usage, see the [README](../README.md).
- For API details, see [API Documentation](api_documentation.md).
- For known issues, see [Known Limitations](known_limitations.md).
- For contributing, see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Getting Started (Summary)

1. **Install dependencies** (see [README](../README.md)).
2. **Convert your ZMK file:**
   ```bash
   zmk-to-kanata input.dtsi output.kbd
   ```
3. **Check the output** in `output.kbd`.
4. For advanced options, see below and the [API Documentation](api_documentation.md).

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Command-Line Options](#command-line-options)
4. [Configuration Files](#configuration-files)
5. [Supported Features](#supported-features)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from PyPI

```bash
pip install zmk-to-kanata
```

### Install from Source

```bash
git clone https://github.com/yourusername/zmk-to-kanata.git
cd zmk-to-kanata
pip install -e .
```

## Basic Usage

The basic command to convert a ZMK file to Kanata format is:

```bash
zmk-to-kanata input.dtsi output.kbd
```

Where:
- `input.dtsi` is your ZMK configuration file
- `output.kbd` is the destination file for the Kanata configuration

## Command-Line Options

The converter supports several command-line options:

```
Usage: zmk-to-kanata [OPTIONS] INPUT_FILE OUTPUT_FILE

Options:
  --version       Show the version and exit.
  -v, --verbose   Enable verbose output.
  -h, --help      Show this help message and exit.
```

## Configuration Files

### ZMK Configuration

The converter expects a standard ZMK configuration file with the following structure:

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
                &kp N1 &kp N2 &kp N3
                &kp N4 &kp N5 &kp N6
            >;
        };
    };
};
```

### Kanata Output

The generated Kanata file will have a structure similar to:

```
;; ZMK to Kanata Configuration
;; Generated on: 2023-03-16

(defvar tap-time 200)
(defvar hold-time 250)

(defalias
  ;; Aliases for special keys and behaviors
)

(deflayer default
  a b c
  d e f
)

(deflayer layer_1
  1 2 3
  4 5 6
)
```

## Supported Features

The converter supports the following ZMK features:

### Basic Keys

- Alphanumeric keys (A-Z, 0-9)
- Special characters (!, @, #, etc.)
- Function keys (F1-F24)
- Navigation keys (arrows, home, end, etc.)
- Modifiers (shift, ctrl, alt, gui)

### Layers

- Multiple layers
- Layer switching (`&mo`, `&to`, `&tog`)
- Transparent keys (`&trans`)

### Advanced Features

- Hold-tap behaviors (`&mt`, `&lt`)
- Sticky keys (`&sk`, `&sl`)
- Key sequences with customizable timing
- Macros with support for:
  - Tap, press, and release actions
  - Wait times between actions
  - Multiple key combinations
- Unicode input for special characters

### Simple combos (two or more keys → single key output)

For a complete list of supported features and limitations, see the [Known Limitations](known_limitations.md) document.

## Troubleshooting & FAQ

**Q: The tool says 'Invalid input format'.**
A: Make sure your ZMK file is valid DTS and follows the standard structure.

**Q: How do I enable debug output?**
A: Use the `--debug` flag or see the [README](../README.md#debugging-and-output-flags).

**Q: My output is missing a feature.**
A: See [Known Limitations](known_limitations.md) for unsupported features.

**Q: Where can I get help?**
A: Open an issue on GitHub and include your config and error message.

**Q: How do I contribute improvements?**
A: See [CONTRIBUTING.md](../CONTRIBUTING.md).

**Q: My combo is skipped or not working.**
A: Only simple combos are supported. If your combo is complex (uses layers, macros, or modifiers), you must add it manually in your Kanata config.

**Q: My custom home row mod is not working as expected.**
A: Standard properties (timing, flavor, bindings) are mapped. Check the Kanata output for comments about unmapped properties and adjust manually if needed.

---

For more information:
- [README](../README.md)
- [API Documentation](api_documentation.md)
- [Testing Guide](testing_guide.md)
- [Known Limitations](known_limitations.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)

## Examples

### Basic Keymap Conversion

**ZMK File (input.dtsi):**

```
/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q &kp W &kp E &kp R &kp T
                &kp A &kp S &kp D &kp F &kp G
                &kp Z &kp X &kp C &kp V &kp B
            >;
        };
    };
};
```

**Command:**

```bash
zmk-to-kanata input.dtsi output.kbd
```

**Kanata Output (output.kbd):**

```
;; ZMK to Kanata Configuration
;; Generated on: 2023-03-16

(defvar tap-time 200)
(defvar hold-time 250)

(deflayer default
  q w e r t
  a s d f g
  z x c v b
)
```

### Multi-Layer Keymap with Hold-Tap

**ZMK File (input.dtsi):**

```
/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q        &kp W        &kp E        &kp R        &kp T
                &mt LCTRL A  &mt LALT S   &mt LGUI D   &mt LSHIFT F &kp G
                &kp Z        &kp X        &kp C        &kp V        &kp B
                             &mo 1        &kp SPACE    &mo 2
            >;
        };

        lower_layer {
            bindings = <
                &kp N1       &kp N2       &kp N3       &kp N4       &kp N5
                &kp TAB      &kp LEFT     &kp DOWN     &kp UP       &kp RIGHT
                &kp GRAVE    &kp MINUS    &kp EQUAL    &kp LBKT     &kp RBKT
                             &trans       &kp ENTER    &trans
            >;
        };

        raise_layer {
            bindings = <
                &kp F1       &kp F2       &kp F3       &kp F4       &kp F5
                &kp ESC      &kp HOME     &kp PG_DN    &kp PG_UP    &kp END
                &kp CAPS     &kp DEL      &kp BSPC     &kp SEMI     &kp SQT
                             &trans       &kp TAB      &trans
            >;
        };
    };
};
```

**Command:**

```bash
zmk-to-kanata input.dtsi output.kbd
```

**Kanata Output (output.kbd):**

```
;; ZMK to Kanata Configuration
;; Generated on: 2023-03-16

(defvar tap-time 200)
(defvar hold-time 250)

(defalias
  mt_a (tap-hold 200 200 a lctl)
  mt_s (tap-hold 200 200 s lalt)
  mt_d (tap-hold 200 200 d lmet)
  mt_f (tap-hold 200 200 f lsft)
)

(deflayer default
  q w e r t
  @mt_a @mt_s @mt_d @mt_f g
  z x c v b
  @layer1 space @layer2
)

(deflayer lower
  1 2 3 4 5
  tab left down up right
  grave minus equal lbracket rbracket
  _ enter _
)

(deflayer raise
  f1 f2 f3 f4 f5
  esc home pgdn pgup end
  caps del bspc semicolon quote
  _ tab _
)
```

### Macro Example

**ZMK File (macro_example.dtsi):**

```
/ {
    behaviors {
        email_macro: email_macro {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&kp E &kp X &kp A &kp M &kp P &kp L &kp E &kp AT &kp E &kp M &kp A &kp I &kp L &kp DOT &kp C &kp O &kp M>;
        };
    };

    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q &kp W &kp E &email_macro &kp T
                &kp A &kp S &kp D &kp F &kp G
                &kp Z &kp X &kp C &kp V &kp B
            >;
        };
    };
};
```

**Kanata Output:**

```
;; ZMK to Kanata Configuration
;; Generated on: 2023-03-16

(defvar tap-time 200)
(defvar hold-time 250)

(defmacro email_macro ()
  (e x a m p l e @ e m a i l . c o m)
)

(deflayer default
  q w e @email_macro t
  a s d f g
  z x c v b
)
```

### Unicode Input Example

**ZMK File (unicode_example.dtsi):**

```
/ {
    behaviors {
        pi_unicode: pi_unicode {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&macro_press &kp LALT>, <&macro_tap &kp KP_N0 &kp KP_N3 &kp C &kp KP_N0>, <&macro_release &kp LALT>;
            label = "PI_UNICODE";
        };
    };

    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q &kp W &kp E &kp R &kp T
                &kp A &kp S &kp D &pi_unicode &kp G
                &kp Z &kp X &kp C &kp V &kp B
            >;
        };
    };
};
```

**Kanata Output:**

```
;; ZMK to Kanata Configuration
;; Generated on: 2023-03-16

(defvar tap-time 200)
(defvar hold-time 250)

(deflayer default
  q w e r t
  a s d (unicode π) g
  z x c v b
)
```

### Simple Combo Example

**ZMK File (input.dtsi):**

```
combos {
  compatible = "zmk,combos";
  combo_esc {
    key-positions = <0 1>;
    bindings = <&kp ESC>;
  };
};
```

**Kanata Output:**

```
(defalias
  combo_esc (combo a s esc)
)
```

> **Note:** Only simple combos (two or more keys → single key output) are supported. Complex combos (with layers, macros, or modifiers) are not supported and must be added manually.

### Custom Hold-Tap (Home Row Mod) Example

**ZMK Behavior:**
```
hm: homerow_mods {
    compatible = "zmk,behavior-hold-tap";
    tapping-term-ms = <180>;
    flavor = "tap-preferred";
    retro-tap = <1>;
    bindings = <A LCTL>;
};
```

**Kanata Output:**
```
(defalias
  hm (tap-hold 180 180 a lctl)
)
; unsupported: hold-tap 'hm' property 'retro-tap' not mapped
```

> **Note:** Standard properties (timing, flavor, bindings) are mapped. Any unmapped or advanced properties (e.g., retro-tap) are commented in the output for manual review.

For more examples, see the [examples](../examples) directory.
