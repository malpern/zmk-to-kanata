"""Edge case integration tests for the ZMK to Kanata conversion pipeline."""
import pytest
from converter.zmk_parser import ZMKParser
from converter.layer_transformer import LayerTransformer
from converter.holdtap_transformer import HoldTapTransformer
from converter.macro_transformer import MacroTransformer
from converter.sticky_key_transformer import StickyKeyTransformer


@pytest.fixture
def parser():
    """Create a ZMKParser instance."""
    return ZMKParser()


@pytest.fixture
def layer_transformer():
    """Create a LayerTransformer instance."""
    return LayerTransformer()


@pytest.fixture
def holdtap_transformer():
    """Create a HoldTapTransformer instance."""
    return HoldTapTransformer()


@pytest.fixture
def macro_transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


@pytest.fixture
def sticky_transformer():
    """Create a StickyKeyTransformer instance."""
    return StickyKeyTransformer()


def test_empty_layer_conversion(parser, layer_transformer):
    """Test conversion of empty layers."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <>;
            };
            empty_layer {
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 2

    # Transform to Kanata format
    result = layer_transformer.transform_layers(layers)

    # Verify empty layer handling
    assert "(deflayer default" in result
    assert "(deflayer empty" in result


def test_invalid_macro_conversion(parser, macro_transformer):
    """Test conversion of invalid macro configurations."""
    zmk_input = """
    / {
        macros {
            invalid_macro: invalid_macro {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <>;
                wait-ms = <-100>;
                tap-ms = <0>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&invalid_macro>;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Transform macro binding
    result = macro_transformer.transform_binding(layers[0].bindings[0])
    assert "(multi)" in result


def test_nested_behavior_conversion(
    parser, layer_transformer, holdtap_transformer,
    macro_transformer, sticky_transformer
):
    """Test conversion of nested behaviors."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    // Valid nested behaviors
                    &lt 1 &kp A        // Layer-tap with key press
                    &lt 2 &mo 3        // Layer-tap with momentary layer

                    // Invalid nested behaviors
                    &ht LSHIFT (&sk LCTRL)  // Hold-tap with sticky key
                    &sk (&ht LALT A)        // Sticky key with hold-tap
                    &lt 1 (&mo 2)           // Layer-tap with momentary layer
                    &ht LSHIFT (&ht LCTRL A)  // Nested hold-taps
                >;
            };

            layer_1 {
                bindings = <
                    &trans &trans &trans
                    &trans &trans &trans
                >;
            };

            layer_2 {
                bindings = <
                    &trans &trans &trans
                    &trans &trans &trans
                >;
            };

            layer_3 {
                bindings = <
                    &trans &trans &trans
                    &trans &trans &trans
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 4

    # Get the default layer bindings
    default_bindings = layers[0].bindings

    # Test valid nested behaviors
    # Layer-tap with key press
    result = holdtap_transformer.transform_binding(default_bindings[0])
    assert "(tap-hold a (layer-while-held 1))" in result

    # Layer-tap with momentary layer
    result = holdtap_transformer.transform_binding(default_bindings[1])
    assert "(tap-hold _ (layer-while-held 2))" in result

    # Test invalid nested behaviors
    # Hold-tap with sticky key
    result = holdtap_transformer.transform_binding(default_bindings[2])
    assert "unknown" in result

    # Sticky key with hold-tap
    result = sticky_transformer.transform_binding(default_bindings[3])
    assert "unknown" in result

    # Layer-tap with momentary layer
    result = holdtap_transformer.transform_binding(default_bindings[4])
    assert "unknown" in result

    # Nested hold-taps
    result = holdtap_transformer.transform_binding(default_bindings[5])
    assert "unknown" in result


def test_invalid_layer_references(parser, layer_transformer):
    """Test conversion of invalid layer references."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &mo 99 &lt 999 A
                    &tog 9999 &trans
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Transform to Kanata format
    result = layer_transformer.transform_layers(layers)

    # Verify invalid layer references
    assert "@layer99" in result
    assert "@layer999" in result
    assert "_" in result


def test_special_character_conversion(
    parser, layer_transformer, holdtap_transformer,
    macro_transformer, sticky_transformer
):
    """Test conversion of special characters and Unicode."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp "é" &kp "ñ"
                    &ht "ü" "ö"
                    &sk "π" &mo "∞"
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Verify special character handling
    for binding in layers[0].bindings:
        # Each transformer should handle Unicode gracefully
        result = layer_transformer.transform_binding(binding)
        assert "unknown" in result or "_" in result

        result = holdtap_transformer.transform_binding(binding)
        assert "unknown" in result or "(tap-hold" in result

        result = sticky_transformer.transform_binding(binding)
        assert "unknown" in result or "sticky-" in result


def test_mixed_timing_parameters(
    parser, holdtap_transformer, macro_transformer,
    sticky_transformer
):
    """Test conversion with various timing parameters."""
    zmk_input = """
    / {
        macros {
            timing_macro: timing_macro {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <&kp A>;
                wait-ms = <999999>;
                tap-ms = <999999>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &ht LSHIFT A
                    &timing_macro
                    &sk LCTRL
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Verify timing parameter handling
    bindings = layers[0].bindings

    # Hold-tap with default timing
    ht_result = holdtap_transformer.transform_binding(bindings[0])
    assert "(tap-hold" in ht_result

    # Macro with large timing values
    macro_result = macro_transformer.transform_binding(bindings[1])
    assert "(multi" in macro_result
    assert "999999" in macro_result

    # Sticky key with default timing
    sticky_result = sticky_transformer.transform_binding(bindings[2])
    assert "sticky-" in sticky_result


def test_malformed_input_recovery(
    parser, layer_transformer, holdtap_transformer,
    macro_transformer, sticky_transformer
):
    """Test recovery from malformed input."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp &ht &sk
                    &mo &lt &tog
                    &invalid &unknown &broken
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Verify graceful handling of malformed input
    for binding in layers[0].bindings:
        # Each transformer should handle malformed input without crashing
        layer_result = layer_transformer.transform_binding(binding)
        assert "_" in layer_result or "unknown" in layer_result

        ht_result = holdtap_transformer.transform_binding(binding)
        assert "unknown" in ht_result or "(tap-hold" in ht_result

        macro_result = macro_transformer.transform_binding(binding)
        assert "unknown" in macro_result or "(multi" in macro_result

        sticky_result = sticky_transformer.transform_binding(binding)
        assert "unknown" in sticky_result or "sticky-" in sticky_result
