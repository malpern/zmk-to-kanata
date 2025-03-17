"""Tests for error handling in the ZMK to Kanata conversion pipeline."""
import pytest
from converter.zmk_parser import ZMKParser, ParserError
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


def test_syntax_error_recovery(parser, layer_transformer):
    """Test recovery from syntax errors in ZMK input."""
    # Missing closing brace
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &kp B
                >;
            };
        ;  # Missing closing brace
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Syntax error" in str(exc_info.value)
    assert "line" in str(exc_info.value)

    # Invalid binding syntax
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &kp> B  # Invalid binding
                >;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Invalid binding syntax" in str(exc_info.value)


def test_missing_required_fields(parser):
    """Test handling of missing required fields."""
    # Missing compatible field
    zmk_input = """
    / {
        keymap {
            default_layer {
                bindings = <
                    &kp A &kp B
                >;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Missing required field" in str(exc_info.value)
    assert "compatible" in str(exc_info.value)

    # Missing bindings field
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                label = "Default";
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Missing required field" in str(exc_info.value)
    assert "bindings" in str(exc_info.value)


def test_invalid_macro_definition_recovery(parser, macro_transformer):
    """Test recovery from invalid macro definitions."""
    # Invalid bindings format
    zmk_input = """
    / {
        macros {
            test_macro: test_macro {
                compatible = "zmk,behavior-macro";
                bindings = "invalid";  # Should be array
                wait-ms = <100>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&test_macro>;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Invalid macro bindings" in str(exc_info.value)

    # Invalid timing parameter
    zmk_input = """
    / {
        macros {
            test_macro: test_macro {
                compatible = "zmk,behavior-macro";
                bindings = <&kp A>;
                wait-ms = "invalid";  # Should be number
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&test_macro>;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Invalid timing parameter" in str(exc_info.value)


def test_layer_validation_errors(parser, layer_transformer):
    """Test layer validation error handling."""
    # Duplicate layer names
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&kp A>;
            };
            default_layer {  # Duplicate name
                bindings = <&kp B>;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Duplicate layer name" in str(exc_info.value)

    # Invalid layer reference
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&mo invalid>;  # Invalid layer reference
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Invalid layer reference" in str(exc_info.value)


def test_binding_validation_errors(
    parser, holdtap_transformer, sticky_transformer
):
    """Test binding validation error handling."""
    # Invalid hold-tap parameters
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &ht invalid A  # Invalid modifier
                >;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Invalid hold-tap parameters" in str(exc_info.value)

    # Invalid sticky key parameters
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &sk invalid  # Invalid key
                >;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    assert "Invalid sticky key parameters" in str(exc_info.value)


def test_error_context_information(parser):
    """Test that error messages include helpful context."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &invalid_behavior  # Line 6
                >;
            };
        };
    };
    """

    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)
    error_msg = str(exc_info.value)

    # Verify error contains useful information
    assert "line 6" in error_msg
    assert "invalid_behavior" in error_msg
    assert "Unknown behavior" in error_msg


def test_partial_recovery(parser, layer_transformer):
    """Test partial recovery from errors in multi-layer configs."""
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &kp B  # Valid layer
                >;
            };
            broken_layer {
                bindings = <
                    &invalid &error  # Invalid layer
                >;
            };
            valid_layer {
                bindings = <
                    &kp C &kp D  # Valid layer
                >;
            };
        };
    };
    """

    # Should process valid layers and report errors for invalid ones
    with pytest.raises(ParserError) as exc_info:
        parser.parse_layers(zmk_input)

    error_msg = str(exc_info.value)
    assert "broken_layer" in error_msg
    assert "invalid behavior" in error_msg.lower()


def test_error_recovery_strategies(
    parser, layer_transformer, holdtap_transformer,
    macro_transformer, sticky_transformer
):
    """Test various error recovery strategies."""
    # Test recovery from invalid but non-fatal errors
    zmk_input = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A     # Valid
                    &invalid  # Invalid - should be replaced with transparent
                    &kp B     # Valid
                >;
            };
        };
    };
    """

    layers = parser.parse_layers(zmk_input)
    result = layer_transformer.transform_layers(layers)

    # Verify valid bindings are preserved
    assert "a" in result
    assert "b" in result
    assert "_" in result  # Transparent key for invalid binding
