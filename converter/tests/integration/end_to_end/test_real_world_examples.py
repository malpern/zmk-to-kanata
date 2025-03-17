"""Tests for real-world complex ZMK keymap examples."""

import tempfile
from pathlib import Path
from textwrap import dedent

from converter.zmk_to_kanata import convert_zmk_to_kanata


def test_corne_keymap_conversion():
    """Test conversion of a real-world Corne keyboard ZMK keymap.

    This tests a common split keyboard layout with multiple layers.
    """
    zmk_content = dedent("""
        /*
         * Copyright (c) 2020 The ZMK Contributors
         *
         * SPDX-License-Identifier: MIT
         */

        #include <behaviors.dtsi>
        #include <dt-bindings/zmk/keys.h>
        #include <dt-bindings/zmk/bt.h>

        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    // -----------------------------------------------------------------------------------------
                    // |  TAB |  Q  |  W  |  E  |  R  |  T  |   |  Y  |  U   |  I  |  O  |  P  | BKSP |
                    // | CTRL |  A  |  S  |  D  |  F  |  G  |   |  H  |  J   |  K  |  L  |  ;  |  '   |
                    // | SHFT |  Z  |  X  |  C  |  V  |  B  |   |  N  |  M   |  ,  |  .  |  /  | ESC  |
                    //                    | GUI | LWR | SPC |   | ENT | RSE  | ALT |

                    bindings = <
                        &kp TAB   &kp Q &kp W &kp E &kp R &kp T   &kp Y &kp U  &kp I     &kp O   &kp P    &kp BSPC
                        &kp LCTRL &kp A &kp S &kp D &kp F &kp G   &kp H &kp J  &kp K     &kp L   &kp SEMI &kp SQT
                        &kp LSHFT &kp Z &kp X &kp C &kp V &kp B   &kp N &kp M  &kp COMMA &kp DOT &kp FSLH &kp ESC
                                        &kp LGUI &mo 1 &kp SPACE   &kp RET &mo 2 &kp RALT
                    >;
                };

                lower_layer {
                    // -----------------------------------------------------------------------------------------
                    // |  TAB |  1  |  2  |  3  |  4  |  5  |   |  6  |  7  |  8  |  9  |  0  | BKSP |
                    // | BTCLR| BT1 | BT2 | BT3 | BT4 | BT5 |   | LFT | DWN |  UP | RGT |     |      |
                    // | SHFT |     |     |     |     |     |   |     |     |     |     |     |      |
                    //                    | GUI |     | SPC |   | ENT |     | ALT |

                    bindings = <
                        &kp TAB    &kp N1       &kp N2       &kp N3       &kp N4       &kp N5         &kp N6   &kp N7   &kp N8 &kp N9    &kp N0 &kp BSPC
                        &bt BT_CLR &bt BT_SEL 0 &bt BT_SEL 1 &bt BT_SEL 2 &bt BT_SEL 3 &bt BT_SEL 4   &kp LEFT &kp DOWN &kp UP &kp RIGHT &trans &trans
                        &kp LSHFT  &trans       &trans       &trans       &trans       &trans         &trans   &trans   &trans &trans    &trans &trans
                                                &kp LGUI     &trans       &kp SPACE    &kp RET &trans &kp RALT
                    >;
                };

                raise_layer {
                    // -----------------------------------------------------------------------------------------
                    // |  TAB |  !  |  @  |  #  |  $  |  %  |   |  ^  |  &  |  *  |  (  |  )  | BKSP |
                    // | CTRL |     |     |     |     |     |   |  -  |  =  |  [  |  ]  |  \\  |  `   |
                    // | SHFT |     |     |     |     |     |   |  _  |  +  |  {  |  }  | "|" |  ~   |
                    //                    | GUI |     | SPC |   | ENT |     | ALT |

                    bindings = <
                        &kp TAB   &kp EXCL &kp AT &kp HASH &kp DLLR &kp PRCNT   &kp CARET &kp AMPS  &kp KP_MULTIPLY &kp LPAR &kp RPAR &kp BSPC
                        &kp LCTRL &trans   &trans &trans   &trans   &trans      &kp MINUS &kp EQUAL &kp LBKT        &kp RBKT &kp BSLH &kp GRAVE
                        &kp LSHFT &trans   &trans &trans   &trans   &trans      &kp UNDER &kp PLUS  &kp LBRC        &kp RBRC &kp PIPE &kp TILDE
                                            &kp LGUI &trans &kp SPACE   &kp RET &trans &kp RALT
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "corne.zmk"
        output_file = Path(tmpdir) / "corne.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        result = convert_zmk_to_kanata(input_file, output_file)

        # Verify success
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        assert "(deflayer lower_layer" in kanata_content
        assert "(deflayer raise_layer" in kanata_content

        # Check specific keys in each layer
        assert "tab q w e r t y u i o p bspc" in kanata_content.lower()
        assert "lctrl a s d f g h j k l ; '" in kanata_content.lower()
        assert "1 2 3 4 5 6 7 8 9 0" in kanata_content
        assert "! @ # $ % ^ & * ( )" in kanata_content


def test_ferris_sweep_keymap():
    """Test conversion of a Ferris Sweep keyboard ZMK keymap.

    This tests a minimalist keyboard with 34 keys and heavy use of combos.
    """
    zmk_content = dedent("""
        /*
         * Copyright (c) 2020 The ZMK Contributors
         *
         * SPDX-License-Identifier: MIT
         */

        #include <behaviors.dtsi>
        #include <dt-bindings/zmk/keys.h>
        #include <dt-bindings/zmk/bt.h>

        #define DEFAULT 0
        #define NAV     1
        #define SYM     2
        #define FUNC    3

        &mt {
            flavor = "tap-preferred";
            tapping_term_ms = <200>;
        };

        / {
            combos {
                compatible = "zmk,combos";
                combo_esc {
                    timeout-ms = <50>;
                    key-positions = <0 1>;
                    bindings = <&kp ESC>;
                };

                combo_tab {
                    timeout-ms = <50>;
                    key-positions = <10 11>;
                    bindings = <&kp TAB>;
                };

                combo_bspc {
                    timeout-ms = <50>;
                    key-positions = <8 9>;
                    bindings = <&kp BSPC>;
                };

                combo_del {
                    timeout-ms = <50>;
                    key-positions = <18 19>;
                    bindings = <&kp DEL>;
                };

                combo_ret {
                    timeout-ms = <50>;
                    key-positions = <28 29>;
                    bindings = <&kp RET>;
                };
            };

            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp Q      &kp W      &kp E       &kp R       &kp T         &kp Y &kp U       &kp I       &kp O      &kp P
                        &mt LGUI A &mt LALT S &mt LCTRL D &mt LSHFT F &kp G         &kp H &mt RSHFT J &mt RCTRL K &mt RALT L &mt RGUI SQT
                        &kp Z      &kp X      &kp C       &kp V       &kp B         &kp N &kp M       &kp COMMA   &kp DOT    &kp FSLH
                                               &lt NAV TAB &kp SPACE   &lt SYM RET   &lt FUNC BSPC
                    >;
                };

                nav_layer {
                    bindings = <
                        &trans &trans &trans &trans &trans   &kp PGUP &kp HOME &kp UP   &kp END  &kp DEL
                        &trans &trans &trans &trans &trans   &kp PGDN &kp LEFT &kp DOWN &kp RIGHT &kp BSPC
                        &trans &trans &trans &trans &trans   &trans   &trans   &trans   &trans    &trans
                                      &trans &trans &trans   &trans
                    >;
                };

                sym_layer {
                    bindings = <
                        &kp EXCL  &kp AT    &kp HASH  &kp DLLR  &kp PRCNT   &kp CARET &kp AMPS  &kp KP_MULTIPLY &kp LPAR  &kp RPAR
                        &kp GRAVE &kp TILDE &kp MINUS &kp UNDER &kp LBKT    &kp RBKT  &kp EQUAL &kp PLUS        &kp BSLH  &kp PIPE
                        &trans    &trans    &trans    &trans    &kp LBRC    &kp RBRC  &trans    &trans          &trans    &trans
                                            &trans    &trans    &trans      &trans
                    >;
                };

                func_layer {
                    bindings = <
                        &kp F1    &kp F2    &kp F3    &kp F4    &kp F5      &kp F6    &kp F7    &kp F8          &kp F9    &kp F10
                        &kp F11   &kp F12   &trans    &trans    &bt BT_CLR  &trans    &trans    &trans          &trans    &trans
                        &trans    &trans    &trans    &trans    &bootloader &trans    &trans    &trans          &trans    &trans
                                            &trans    &trans    &trans      &trans
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "ferris.zmk"
        output_file = Path(tmpdir) / "ferris.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        result = convert_zmk_to_kanata(input_file, output_file)

        # Verify success
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        assert "(deflayer nav_layer" in kanata_content
        assert "(deflayer sym_layer" in kanata_content
        assert "(deflayer func_layer" in kanata_content

        # Check layer-tap keys are converted correctly
        assert "lt(1,tab)" in kanata_content.lower()
        assert "lt(2,ret)" in kanata_content.lower()
        assert "lt(3,bspc)" in kanata_content.lower()

        # Check mod-tap keys are converted correctly
        assert "mt(lgui,a)" in kanata_content.lower()
        assert "mt(lalt,s)" in kanata_content.lower()
        assert "mt(lctrl,d)" in kanata_content.lower()
        assert "mt(lshft,f)" in kanata_content.lower()
