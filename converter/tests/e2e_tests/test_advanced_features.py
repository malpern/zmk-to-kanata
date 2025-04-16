"""End-to-end tests for advanced ZMK features."""

from converter.cli import main


def test_multi_layer_with_hold_tap(temp_test_dir):
    """Test conversion of a multi-layer keymap with hold-tap behaviors."""
    zmk_content = """#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    behaviors {
        ht: hold_tap {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            tapping-term-ms = <200>;
            quick-tap-ms = <150>;
            flavor = "tap-preferred";
            bindings = <&kp>, <&kp>;
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &ht LSHIFT A &ht LCTRL B  &mo 1
                &ht LALT C   &ht LGUI D   &mo 2
            >;
        };
        nav_layer {
            bindings = <
                &kp LEFT  &kp RIGHT  &trans
                &kp UP    &kp DOWN   &mo 3
            >;
        };
        num_layer {
            bindings = <
                &kp N1    &kp N2     &trans
                &kp N3    &kp N4     &trans
            >;
        };
        fn_layer {
            bindings = <
                &kp F1    &kp F2     &trans
                &kp F3    &kp F4     &trans
            >;
        };
    };
}; """

    zmk_file = temp_test_dir / "multi_layer_advanced.dtsi"
    zmk_file.write_text(zmk_content)

    kanata_file = temp_test_dir / "multi_layer_advanced.kbd"

    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0

    content = kanata_file.read_text()

    # Verify layer definitions
    assert "(deflayer default" in content
    assert "(deflayer nav" in content
    assert "(deflayer num" in content
    assert "(deflayer fn" in content

    # Verify hold-tap bindings in default layer
    assert "tap-hold lshift a" in content.lower()
    assert "tap-hold lctrl b" in content.lower()
    assert "tap-hold lalt c" in content.lower()
    assert "tap-hold lgui d" in content.lower()

    # Verify layer switching
    assert "@layer1" in content
    assert "@layer2" in content
    assert "@layer3" in content

    # Verify navigation layer
    assert "left" in content.lower()
    assert "right" in content.lower()
    assert "up" in content.lower()
    assert "down" in content.lower()

    # Verify number layer
    assert "1" in content
    assert "2" in content
    assert "3" in content
    assert "4" in content

    # Verify function layer
    assert "f1" in content.lower()
    assert "f2" in content.lower()
    assert "f3" in content.lower()
    assert "f4" in content.lower()


def test_multi_layer_with_custom_behaviors(temp_test_dir):
    """Test conversion of a multi-layer keymap with custom behaviors."""
    zmk_content = """#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    behaviors {
        mt: mod_tap {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <&kp>, <&kp>;
        };
        td: tap_dance {
            compatible = "zmk,behavior-tap-dance";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&kp A>, <&kp B>, <&kp C>;
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &mt LSHIFT A &mt LCTRL B  &mo 1
                &mt LALT C   &mt LGUI D   &mo 2
            >;
        };
        nav_layer {
            bindings = <
                &kp LEFT  &kp RIGHT  &trans
                &kp UP    &kp DOWN   &mo 3
            >;
        };
        num_layer {
            bindings = <
                &kp N1    &kp N2     &trans
                &kp N3    &kp N4     &trans
            >;
        };
        fn_layer {
            bindings = <
                &kp F1    &kp F2     &trans
                &kp F3    &kp F4     &trans
            >;
        };
    };
}; """

    zmk_file = temp_test_dir / "multi_layer_behaviors.dtsi"
    zmk_file.write_text(zmk_content)

    kanata_file = temp_test_dir / "multi_layer_behaviors.kbd"

    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0

    content = kanata_file.read_text()

    # Verify layer definitions
    assert "(deflayer default" in content
    assert "(deflayer nav" in content
    assert "(deflayer num" in content
    assert "(deflayer fn" in content

    # Verify mod-tap bindings in default layer
    assert "tap-hold lshift a" in content.lower()
    assert "tap-hold lctrl b" in content.lower()
    assert "tap-hold lalt c" in content.lower()
    assert "tap-hold lgui d" in content.lower()

    # Verify layer switching
    assert "@layer1" in content
    assert "@layer2" in content
    assert "@layer3" in content

    # Verify navigation layer
    assert "left" in content.lower()
    assert "right" in content.lower()
    assert "up" in content.lower()
    assert "down" in content.lower()

    # Verify number layer
    assert "1" in content
    assert "2" in content
    assert "3" in content
    assert "4" in content

    # Verify function layer
    assert "f1" in content.lower()
    assert "f2" in content.lower()
    assert "f3" in content.lower()
    assert "f4" in content.lower()
