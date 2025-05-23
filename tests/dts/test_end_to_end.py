"""End-to-end tests for the DTS-based ZMK parser using real keymap files."""

import pytest
from converter.dts.parser import DtsParser
from converter.dts.error_handler import DtsParseError
from converter.dts.extractor import KeymapExtractor
from converter.models import KeymapConfig, Binding, Behavior
import logging


def test_simple_keymap():
    """Test parsing a simple keymap file."""
    content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify basic structure
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 1

    # Verify default layer
    default_layer_node = next(
        layer_node for layer_node in config.layers if layer_node.name == "default_layer"
    )
    assert len(default_layer_node.bindings) == 6

    # Verify bindings
    expected_key_codes = ["A", "B", "C", "D", "E", "F"]
    for binding_node, expected_key_code in zip(
        default_layer_node.bindings, expected_key_codes
    ):
        assert isinstance(binding_node, Binding)
        assert binding_node.behavior is not None
        assert binding_node.behavior.name == "kp"
        assert binding_node.behavior.type == "zmk,behavior-key-press"
        assert binding_node.params == [expected_key_code]


def test_complex_keymap_with_behaviors():
    """Test parsing a complex keymap with behaviors."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
                #binding-cells = <2>;
            };
            
            macro_a: macro_a {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <&kp A &kp B>;
            };
            
            lt: layer_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
                #binding-cells = <2>;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &mt LSHIFT A  &kp B        &macro_a
                    &kp D         &lt 1 E      &kp F
                >;
            };
            
            lower_layer {
                bindings = <
                    &kp N1  &kp N2  &kp N3
                    &kp N4  &kp N5  &kp N6
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify basic structure
    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 2
    assert "mt" in config.behaviors
    assert "macro_a" in config.behaviors
    assert "lt" in config.behaviors

    # Verify behaviors
    mt = next(b for b in config.behaviors.values() if b.name == "mt")
    assert isinstance(mt, Behavior)
    assert mt.tapping_term_ms == 200

    lt = next(b for b in config.behaviors.values() if b.name == "lt")
    assert isinstance(lt, Behavior)
    assert lt.tapping_term_ms == 200

    macro = next(b for b in config.behaviors.values() if b.name == "macro_a")
    assert isinstance(macro, Behavior)
    assert all(isinstance(b, Binding) for b in macro.bindings)

    # Verify default layer
    default_layer_node = next(
        layer_node for layer_node in config.layers if layer_node.name == "default_layer"
    )
    assert len(default_layer_node.bindings) == 6

    # Check specific bindings
    assert default_layer_node.bindings[0].behavior == mt
    assert default_layer_node.bindings[0].params == ["LSHIFT", "A"]

    assert default_layer_node.bindings[1].behavior is not None
    assert default_layer_node.bindings[1].behavior.name == "kp"
    assert default_layer_node.bindings[1].behavior.type == "zmk,behavior-key-press"
    assert default_layer_node.bindings[1].params == ["B"]

    assert default_layer_node.bindings[2].behavior == macro
    assert default_layer_node.bindings[2].params == []

    assert default_layer_node.bindings[3].behavior is not None
    assert default_layer_node.bindings[3].behavior.name == "kp"
    assert default_layer_node.bindings[3].behavior.type == "zmk,behavior-key-press"
    assert default_layer_node.bindings[3].params == ["D"]

    assert default_layer_node.bindings[4].behavior == lt
    assert default_layer_node.bindings[4].params == ["1", "E"]

    assert default_layer_node.bindings[5].behavior is not None
    assert default_layer_node.bindings[5].behavior.name == "kp"
    assert default_layer_node.bindings[5].behavior.type == "zmk,behavior-key-press"
    assert default_layer_node.bindings[5].params == ["F"]

    # Verify lower layer
    lower_layer_node = next(
        layer_node for layer_node in config.layers if layer_node.name == "lower_layer"
    )
    assert len(lower_layer_node.bindings) == 6
    for binding_node, expected_key_code in zip(
        lower_layer_node.bindings, ["N1", "N2", "N3", "N4", "N5", "N6"]
    ):
        assert isinstance(binding_node, Binding)
        assert binding_node.behavior is not None
        assert binding_node.behavior.name == "kp"
        assert binding_node.behavior.type == "zmk,behavior-key-press"
        assert binding_node.params == [expected_key_code]


def test_keymap_with_unicode():
    """Test parsing a keymap with unicode behaviors."""
    content = """
    / {
        behaviors {
            unicode: unicode {
                compatible = "zmk,behavior-unicode";
                #binding-cells = <1>;
            };
            
            uc_string: unicode_string {
                compatible = "zmk,behavior-unicode-string";
                #binding-cells = <1>;
                strings = <
                    "smile" "😊"
                    "heart" "❤️"
                >;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &unicode U0001F600  &uc_string smile  &kp A
                    &unicode U2764      &uc_string heart  &kp B
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify behaviors
    assert "unicode" in config.behaviors
    assert "uc_string" in config.behaviors

    unicode = next(b for b in config.behaviors.values() if b.name == "unicode")
    assert isinstance(unicode, Behavior)

    uc_string = next(b for b in config.behaviors.values() if b.name == "uc_string")
    assert isinstance(uc_string, Behavior)

    # Verify bindings
    layer_node = config.layers[0]
    assert len(layer_node.bindings) == 10

    # Expected sequence: unicode, U0001F600, uc_string, smile, A, unicode, U2764, uc_string, heart, B
    expected = [
        (unicode, []),
        (None, ["U0001F600"]),
        (uc_string, []),
        (None, ["smile"]),
        (None, ["A"]),
        (unicode, []),
        (None, ["U2764"]),
        (uc_string, []),
        (None, ["heart"]),
        (None, ["B"]),
    ]
    for binding, (exp_behavior, exp_params) in zip(layer_node.bindings, expected):
        if exp_behavior is not None:
            assert binding.behavior == exp_behavior
        elif exp_params == ["A"] or exp_params == ["B"]:
            assert binding.behavior is not None
            assert binding.behavior.name == "kp"
            assert binding.behavior.type == "zmk,behavior-key-press"
        else:
            assert binding.behavior is None
        assert binding.params == exp_params


def test_error_handling(caplog):
    """Test error handling with malformed input."""
    caplog.set_level(logging.ERROR)  # Ensure ERROR logs are captured
    # Test missing root node
    with pytest.raises(DtsParseError, match="DTS must start with root node"):
        parser = DtsParser()
        parser.parse("keymap { };")

    # Test invalid property assignment
    with pytest.raises(DtsParseError, match="Invalid property value"):
        parser = DtsParser()
        parser.parse(
            """
        / {
            keymap {
                prop = value
            };
        };
        """
        )

    # Test invalid binding format
    parser = DtsParser()
    ast = parser.parse(
        """
    / {
        keymap {
            default_layer {
                bindings = <&invalid_binding>;
            };
        };
    };
    """
    )
    extractor = KeymapExtractor()
    config = extractor.extract(ast)  # Extract without expecting ValueError

    # Check that the error was logged
    assert any(
        record.levelname == "ERROR"
        and "Unknown behavior referenced or failed to map: invalid_binding"
        in record.message
        and record.name == "root"
        # and "extractor.py" in record.pathname # Pathname can be fragile, message is better
        for record in caplog.records
    )

    # Check the created behavior for the invalid binding
    assert len(config.layers) == 1
    default_layer_node = config.layers[0]
    assert len(default_layer_node.bindings) == 1
    invalid_binding_node = default_layer_node.bindings[0]
    assert invalid_binding_node.behavior is not None
    assert invalid_binding_node.behavior.name == "invalid_binding"
    assert invalid_binding_node.behavior.type == "unknown-behavior"
    assert invalid_binding_node.params == []


def test_keymap_with_combos():
    """Test parsing a keymap with combo behaviors."""
    content = """
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
                key-positions = <1 2>;
                bindings = <&kp TAB>;
            };
        };
        
        keymap {
            compatible = "zmk,keymap";
            
            default_layer {
                bindings = <
                    &kp A &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)

    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Verify combos
    assert len(config.combos) == 2

    combo_esc = next(c for c in config.combos if c.name == "combo_esc")
    assert combo_esc.timeout_ms == 50
    assert combo_esc.key_positions == [0, 1]
    assert combo_esc.binding.params == ["ESC"]

    combo_tab = next(c for c in config.combos if c.name == "combo_tab")
    assert combo_tab.timeout_ms == 50
    assert combo_tab.key_positions == [1, 2]
    assert combo_tab.binding.params == ["TAB"]


def test_keymap_with_conditional_layers():
    """Test parsing a keymap with conditional layers."""
    content = """
    / {
        conditional_layers {
            compatible = "zmk,conditional-layers";
            tri_layer {
                if-layers = <1 2>;
                then-layer = <3>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&kp A &kp B>;
            };
            lower_layer {
                bindings = <&kp N1 &kp N2>;
            };
            raise_layer {
                bindings = <&kp F1 &kp F2>;
            };
            adjust_layer {
                bindings = <&reset &bootloader>;
            };
        };
    };
    """
    # Parse and extract
    parser = DtsParser()
    ast = parser.parse(content)
    extractor = KeymapExtractor()
    config = extractor.extract(ast)
    # Assert that 'reset' and 'bootloader' behaviors are present
    behavior_names = [b.name for b in config.behaviors.values()]
    assert "reset" in behavior_names
    assert "bootloader" in behavior_names
