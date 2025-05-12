"""Tests for the DTS extractor."""

from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.models import KeymapConfig, Binding, HoldTap, MacroBehavior


def test_extract_simple_keymap():
    """Test extracting a simple keymap."""
    content = """
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <&kp A &kp B &kp C>;
            };
        };
    };
    """

    parser = DtsParser()
    ast = parser.parse(content)
    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    assert isinstance(config, KeymapConfig)
    assert len(config.layers) == 1
    assert config.layers[0].name == "default_layer"
    assert len(config.layers[0].bindings) == 3
    assert all(isinstance(b, Binding) for b in config.layers[0].bindings)


def test_extract_with_behaviors():
    """Test extracting keymap with behaviors."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
            macro: macro {
                compatible = "zmk,behavior-macro";
                bindings = <&kp A &kp B>;
            };
        };
        keymap {
            default_layer {
                bindings = <&mt LSHIFT A &macro>;
            };
        };
    };
    """

    parser = DtsParser()
    ast = parser.parse(content)
    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    assert len(config.behaviors) == 2
    assert any(isinstance(b, HoldTap) for b in config.behaviors.values())
    assert any(isinstance(b, MacroBehavior) for b in config.behaviors.values())

    mt = next(b for b in config.behaviors.values() if isinstance(b, HoldTap))
    assert mt.tapping_term_ms == 200

    macro = next(b for b in config.behaviors.values() if isinstance(b, MacroBehavior))
    assert len(macro.bindings) == 2


def test_extract_multiple_layers():
    """Test extracting keymap with multiple layers."""
    content = """
    / {
        keymap {
            default_layer {
                bindings = <&kp A &kp B>;
            };
            lower_layer {
                bindings = <&kp C &kp D>;
            };
            raise_layer {
                bindings = <&kp E &kp F>;
            };
        };
    };
    """

    parser = DtsParser()
    ast = parser.parse(content)
    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    assert len(config.layers) == 3
    assert {layer.name for layer in config.layers} == {
        "default_layer",
        "lower_layer",
        "raise_layer",
    }
    assert all(len(layer.bindings) == 2 for layer in config.layers)


def test_extract_complex_bindings():
    """Test extracting complex bindings."""
    content = """
    / {
        behaviors {
            mt: mod_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
            lt: layer_tap {
                compatible = "zmk,behavior-hold-tap";
                tapping-term-ms = <200>;
            };
        };
        keymap {
            default_layer {
                bindings = <
                    &mt LSHIFT A
                    &lt 1 B
                    &kp C
                >;
            };
        };
    };
    """

    parser = DtsParser()
    ast = parser.parse(content)
    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    layer = config.layers[0]
    assert len(layer.bindings) == 3

    # Check first binding (mod-tap)
    mt_binding = layer.bindings[0]
    assert mt_binding.behavior.name == "mt"
    assert mt_binding.params == ["LSHIFT", "A"]

    # Check second binding (layer-tap)
    lt_binding = layer.bindings[1]
    assert lt_binding.behavior.name == "lt"
    assert lt_binding.params == ["1", "B"]

    # Check third binding (key-press)
    kp_binding = layer.bindings[2]
    assert kp_binding.behavior is None  # Key press is built-in
    assert kp_binding.params == ["C"]


def test_extract_invalid_content():
    """Test extracting invalid content."""
    content = """
    / {
        keymap {
            invalid_layer {
                # Missing bindings
            };
        };
    };
    """

    parser = DtsParser()
    ast = parser.parse(content)
    extractor = KeymapExtractor()
    config = extractor.extract(ast)

    # Invalid layer should be skipped
    assert len(config.layers) == 0
