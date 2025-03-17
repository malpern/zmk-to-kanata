"""Integration tests for the complete ZMK to Kanata conversion pipeline."""
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


def test_basic_layer_conversion(parser, layer_transformer):
    """Test basic layer conversion from ZMK to Kanata."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp N1 &kp N2 &kp N3
                >;
            };
            num_layer {
                bindings = <
                    &kp F1 &kp F2 &kp F3
                    &trans &mo 1 &kp SPACE
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 2

    # Transform to Kanata format
    result = layer_transformer.transform_layers(layers)

    # Verify basic structure
    assert "(deflayer default" in result
    assert "(deflayer num" in result

    # Verify key mappings
    assert "a b c" in result
    assert "1 2 3" in result
    assert "f1 f2 f3" in result
    assert "_ @layer1 spc" in result


def test_holdtap_conversion(parser, holdtap_transformer):
    """Test hold-tap behavior conversion from ZMK to Kanata."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &ht LSHIFT A &ht LCTRL B
                    &ht LALT C &ht LGUI D
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Transform each binding
    for binding in layers[0].bindings:
        result = holdtap_transformer.transform_binding(binding)
        assert "(tap-hold" in result
        assert any(mod in result for mod in ["lsft", "lctl", "lalt", "lmet"])
        assert any(key in result for key in ["a", "b", "c", "d"])


def test_macro_conversion(parser, macro_transformer):
    """Test macro behavior conversion from ZMK to Kanata."""
    zmk_input = """
    / {
        macros {
            macro1: macro1 {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <&kp A &kp B>, <&kp C>;
                wait-ms = <100>;
                tap-ms = <50>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&macro1>;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Transform macro binding
    result = macro_transformer.transform_binding(layers[0].bindings[0])
    assert "(multi" in result
    assert "(tap-hold-ms 50" in result
    assert "(delay 100)" in result
    assert "a b c" in result


def test_sticky_key_conversion(parser, sticky_transformer):
    """Test sticky key behavior conversion from ZMK to Kanata."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &sk LSHIFT &sk LCTRL
                    &sk LALT &sk LGUI
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Transform each binding
    for binding in layers[0].bindings:
        result = sticky_transformer.transform_binding(binding)
        assert "sticky-" in result
        assert any(mod in result for mod in ["lsft", "lctl", "lalt", "lmet"])


def test_complex_layer_conversion(parser, layer_transformer):
    """Test conversion of complex layer configurations."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &mo 1 &mo 2
                    &kp B &lt 1 C &lt 2 D
                >;
            };
            num_layer {
                bindings = <
                    &trans &trans &trans
                    &kp N1 &kp N2 &kp N3
                >;
            };
            sym_layer {
                bindings = <
                    &kp EXCL &kp AT &kp HASH
                    &trans &trans &trans
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 3

    # Transform to Kanata format
    result = layer_transformer.transform_layers(layers)

    # Verify layer structure
    assert "(deflayer default" in result
    assert "(deflayer num" in result
    assert "(deflayer sym" in result

    # Verify complex bindings
    assert "a @layer1 @layer2" in result
    assert "b" in result
    assert "_ _ _" in result
    assert "1 2 3" in result
    assert "excl at hash" in result


def test_mixed_behavior_conversion(
    parser, layer_transformer, holdtap_transformer,
    macro_transformer, sticky_transformer
):
    """Test conversion of mixed behaviors in a single layer."""
    zmk_input = """
    / {
        macros {
            macro1: macro1 {
                compatible = "zmk,behavior-macro";
                bindings = <&kp A &kp B>;
                wait-ms = <100>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &ht LSHIFT B &macro1
                    &sk LCTRL &mo 1 &lt 2 C
                >;
            };
        };
    };
    """

    # Parse ZMK input
    layers = parser.parse_layers(zmk_input)
    assert len(layers) == 1

    # Transform each binding type
    bindings = layers[0].bindings

    # Regular key
    assert layer_transformer.transform_binding(bindings[0]) == "a"

    # Hold-tap
    ht_result = holdtap_transformer.transform_binding(bindings[1])
    assert "(tap-hold lsft b)" in ht_result

    # Macro
    macro_result = macro_transformer.transform_binding(bindings[2])
    assert "(multi" in macro_result
    assert "a b" in macro_result

    # Sticky key
    sticky_result = sticky_transformer.transform_binding(bindings[3])
    assert "sticky-lctl" in sticky_result

    # Layer tap
    lt_result = layer_transformer.transform_binding(bindings[5])
    assert "@layer2" in lt_result
