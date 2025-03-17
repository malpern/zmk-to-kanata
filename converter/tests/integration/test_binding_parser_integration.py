"""Integration tests for binding parser with ZMK parser."""

from textwrap import dedent

from converter.parser.zmk_parser import ZMKParser
from converter.parser.error_recovery_wrapper import ParserErrorRecoveryWrapper


def test_basic_binding_integration():
    """Test basic binding parsing integration."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A   &kp B   &kp C
                        &kp D   &kp E   &kp F
                    >;
                };
            };
        };
    """)

    parser = ZMKParser()
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 6
    assert [b.key for b in layer.bindings] == [
        "A", "B", "C", "D", "E", "F"
    ]


def test_complex_binding_integration():
    """Test complex binding parsing integration."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &lt 1 A      &mt LSHIFT B    &kp C
                        &mo 2        &tog 3          &to 1
                    >;
                };
            };
        };
    """)

    parser = ZMKParser()
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 6
    assert [b.key for b in layer.bindings] == [
        "lt(1,A)", "mt(LSHIFT,B)", "C",
        "mo(2)", "tog(3)", "to(1)"
    ]


def test_nested_binding_integration():
    """Test nested binding parsing integration."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &lt 1 (&kp A)    &mt LSHIFT (&kp B)    &kp C
                        &lt 2 (&mt LCTRL D)
                    >;
                };
            };
        };
    """)

    parser = ZMKParser()
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 4
    assert [b.key for b in layer.bindings] == [
        "lt(1,A)", "mt(LSHIFT,B)", "C",
        "lt(2,mt(LCTRL,D))"
    ]


def test_error_recovery_integration():
    """Test error recovery integration."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A          &invalid B     &kp C
                        &lt INVALID D  &mt E F       &kp G
                        &lt 1 (&invalid X)
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

    # Check valid bindings are preserved
    assert layer.bindings[0].key == "A"
    assert layer.bindings[2].key == "C"
    assert layer.bindings[5].key == "G"

    # Check invalid bindings are converted to unknown
    assert layer.bindings[1].key == "unknown"  # invalid behavior
    assert layer.bindings[3].key == "unknown"  # invalid lt param
    assert layer.bindings[4].key == "unknown"  # invalid mt params
    assert layer.bindings[6].key == "unknown"  # invalid nested binding

    # Check error reporting
    assert parser.has_errors()
    errors = parser.get_error_summary()
    assert errors["total_errors"] == 4
    assert "invalid_binding" in errors["error_types"]
    assert "invalid_parameter" in errors["error_types"]
    assert "invalid_nested_binding" in errors["error_types"]


def test_multiline_binding_integration():
    """Test multi-line binding parsing integration."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A
                        &lt 1 B
                        &mt LSHIFT C
                        &mo 2
                    >;
                };
            };
        };
    """)

    parser = ZMKParser()
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 4
    assert [b.key for b in layer.bindings] == [
        "A",
        "lt(1,B)",
        "mt(LSHIFT,C)",
        "mo(2)"
    ]


def test_inline_binding_integration():
    """Test inline binding parsing integration."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <&kp A &lt 1 B &mt LSHIFT C>;
                };
            };
        };
    """)

    parser = ZMKParser()
    result = parser.parse(content)

    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert len(layer.bindings) == 3
    assert [b.key for b in layer.bindings] == [
        "A",
        "lt(1,B)",
        "mt(LSHIFT,C)"
    ]


def test_multiple_layers_integration():
    """Test binding parsing with multiple layers."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A &kp B
                    >;
                };

                layer_1 {
                    bindings = <
                        &lt 2 C &mt LSHIFT D
                    >;
                };

                layer_2 {
                    bindings = <
                        &mo 3 &to 1
                    >;
                };
            };
        };
    """)

    parser = ZMKParser()
    result = parser.parse(content)

    assert len(result["layers"]) == 3

    # Check default layer
    layer = result["layers"][0]
    assert layer.name == "default"
    assert len(layer.bindings) == 2
    assert [b.key for b in layer.bindings] == ["A", "B"]

    # Check layer 1
    layer = result["layers"][1]
    assert layer.name == "layer_1"
    assert len(layer.bindings) == 2
    assert [b.key for b in layer.bindings] == [
        "lt(2,C)",
        "mt(LSHIFT,D)"
    ]

    # Check layer 2
    layer = result["layers"][2]
    assert layer.name == "layer_2"
    assert len(layer.bindings) == 2
    assert [b.key for b in layer.bindings] == [
        "mo(3)",
        "to(1)"
    ]
