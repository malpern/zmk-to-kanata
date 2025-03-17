"""Integration tests for the error recovery system."""

from textwrap import dedent

from converter.parser.zmk_parser import ZMKParser
from converter.parser.error_recovery_wrapper import ParserErrorRecoveryWrapper


def test_invalid_binding_recovery():
    """Test recovery from invalid bindings in a layer."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A   &invalid_binding   &kp B
                        &kp C   &kp D             &kp E
                    >;
                };
            };
        };
    """)

    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 6
    # Invalid binding converted to unknown
    assert layer.bindings[1].key == "unknown"
    assert parser.has_errors()

    errors = parser.get_error_summary()
    assert errors["total_errors"] == 1
    assert errors["error_types"]["invalid_binding"] == 1


def test_invalid_layer_recovery():
    """Test recovery from invalid layer definitions."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A   &kp B   &kp C
                    >;
                };

                invalid_layer {
                    invalid content
                    that should be
                    handled gracefully
                };

                layer_2 {
                    bindings = <
                        &kp X   &kp Y   &kp Z
                    >;
                };
            };
        };
    """)

    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)

    assert len(result["layers"]) == 3
    assert result["layers"][0].name == "default"
    assert result["layers"][1].name == "invalid"  # Empty layer created
    assert len(result["layers"][1].bindings) == 0
    assert result["layers"][2].name == "layer_2"
    assert parser.has_errors()

    errors = parser.get_error_summary()
    assert errors["total_errors"] == 1
    assert errors["error_types"]["invalid_layer"] == 1


def test_multiple_error_recovery():
    """Test recovery from multiple types of errors."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A   &invalid_1   &kp B
                        &kp C   &invalid_2   &kp D
                    >;
                };

                broken_layer {
                    invalid content
                };

                layer_2 {
                    bindings = <
                        &kp X   &invalid_3   &kp Z
                    >;
                };
            };
        };
    """)

    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)

    assert len(result["layers"]) == 3
    assert all(
        layer.name in ["default", "broken", "layer_2"]
        for layer in result["layers"]
    )
    assert parser.has_errors()

    errors = parser.get_error_summary()
    assert errors["total_errors"] == 4  # 3 invalid bindings + 1 invalid layer
    assert errors["error_types"]["invalid_binding"] == 3
    assert errors["error_types"]["invalid_layer"] == 1


def test_nested_behavior_recovery():
    """Test recovery from invalid nested behaviors."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &lt 1 (&lt 2 A)    // Invalid nesting
                        &mt LSHIFT (&kp A)  // Valid nesting
                        &lt 3 (&sk B)       // Invalid nesting
                    >;
                };
            };
        };
    """)

    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 3
    assert layer.bindings[0].key == "unknown"  # Invalid nesting
    assert "LSHIFT" in layer.bindings[1].key  # Valid nesting preserved
    assert layer.bindings[2].key == "unknown"  # Invalid nesting
    assert parser.has_errors()

    errors = parser.get_error_summary()
    assert errors["total_errors"] == 2
    assert errors["error_types"]["invalid_nested_behavior"] == 2


def test_error_recovery_with_comments():
    """Test error recovery with commented lines."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        // This line is fine
                        &kp A   &kp B   &kp C
                        // This line has an error
                        &kp D   &invalid   &kp F
                        // This line is also fine
                        &kp G   &kp H   &kp I
                    >;
                };
            };
        };
    """)

    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 9
    assert layer.bindings[4].key == "unknown"  # Invalid binding
    assert parser.has_errors()

    errors = parser.get_error_summary()
    assert errors["total_errors"] == 1
    assert errors["error_types"]["invalid_binding"] == 1


def test_error_recovery_preserves_valid_content():
    """Test that error recovery preserves valid content."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A   &kp B   &kp C
                    >;
                };

                broken_layer {
                    invalid content
                };

                layer_2 {
                    bindings = <
                        &mt LSHIFT A   &kp B   &kp C
                        &kp D         &kp E   &kp F
                    >;
                };
            };
        };
    """)

    parser = ParserErrorRecoveryWrapper(ZMKParser)
    result = parser.parse(content)

    # Check that valid layers are preserved
    assert len(result["layers"]) == 3
    default_layer = result["layers"][0]
    assert len(default_layer.bindings) == 3
    assert all(binding.key != "unknown" for binding in default_layer.bindings)

    # Check that valid complex bindings are preserved
    layer_2 = result["layers"][2]
    assert len(layer_2.bindings) == 6
    assert "LSHIFT" in layer_2.bindings[0].key
    assert all(binding.key != "unknown" for binding in layer_2.bindings)

    # Check error handling
    assert parser.has_errors()
    errors = parser.get_error_summary()
    assert errors["total_errors"] == 1
    assert errors["error_types"]["invalid_layer"] == 1
