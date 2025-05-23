import pytest
from converter.kanata_converter import KanataConverter
import os
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.transformer.kanata_transformer import KanataTransformer


def test_convert_simple_keymap():
    """Test converting a simple keymap."""
    # Create test data
    dts_data = {
        "matrix_size": (2, 3),
        "matrix_map": [
            ["((0) << 8 | (0))", "((0) << 8 | (1))", "((0) << 8 | (2))"],
            ["((1) << 8 | (0))", "((1) << 8 | (1))", "((1) << 8 | (2))"],
        ],
        "keymap": {
            "default": [
                ["&kp A", "&kp B", "&kp C"],
                ["&kp D", "&kp E", "&kp F"],
            ],
        },
    }

    # Convert to Kanata
    converter = KanataConverter()
    result = converter.convert(dts_data)

    # Check the result
    expected = """# Generated by ZMK to Kanata converter
# Matrix size: 2x3

# Layer: default
a b c
d e f
"""
    assert result == expected


def test_convert_large_keymap():
    """Test converting a larger keymap."""
    # Create test data
    dts_data = {
        "matrix_size": (4, 5),
        "matrix_map": [
            [
                "((0) << 8 | (0))",
                "((0) << 8 | (1))",
                "((0) << 8 | (2))",
                "((0) << 8 | (3))",
                "((0) << 8 | (4))",
            ],
            [
                "((1) << 8 | (0))",
                "((1) << 8 | (1))",
                "((1) << 8 | (2))",
                "((1) << 8 | (3))",
                "((1) << 8 | (4))",
            ],
            [
                "((2) << 8 | (0))",
                "((2) << 8 | (1))",
                "((2) << 8 | (2))",
                "((2) << 8 | (3))",
                "((2) << 8 | (4))",
            ],
            [
                "((3) << 8 | (0))",
                "((3) << 8 | (1))",
                "((3) << 8 | (2))",
                "((3) << 8 | (3))",
                "((3) << 8 | (4))",
            ],
        ],
        "keymap": {
            "default": [
                ["&kp A", "&kp B", "&kp C", "&kp D", "&kp E"],
                ["&kp F", "&kp G", "&kp H", "&kp I", "&kp J"],
                ["&kp K", "&kp L", "&kp M", "&kp N", "&kp O"],
                ["&kp P", "&kp Q", "&kp R", "&kp S", "&kp T"],
            ],
        },
    }

    # Convert to Kanata
    converter = KanataConverter()
    result = converter.convert(dts_data)

    # Check the result
    expected = """# Generated by ZMK to Kanata converter
# Matrix size: 4x5

# Layer: default
a b c d e
f g h i j
k l m n o
p q r s t
"""
    assert result == expected


def test_convert_multiple_layers():
    """Test converting a keymap with multiple layers."""
    # Create test data
    dts_data = {
        "matrix_size": (2, 2),
        "matrix_map": [
            ["((0) << 8 | (0))", "((0) << 8 | (1))"],
            ["((1) << 8 | (0))", "((1) << 8 | (1))"],
        ],
        "keymap": {
            "default": [
                ["&kp A", "&kp B"],
                ["&kp C", "&kp D"],
            ],
            "lower": [
                ["&kp E", "&kp F"],
                ["&kp G", "&kp H"],
            ],
            "raise": [
                ["&kp I", "&kp J"],
                ["&kp K", "&kp L"],
            ],
        },
    }

    # Convert to Kanata
    converter = KanataConverter()
    result = converter.convert(dts_data)

    # Check the result
    expected = """# Generated by ZMK to Kanata converter
# Matrix size: 2x2

# Layer: default
a b
c d

# Layer: lower
e f
g h

# Layer: raise
i j
k l
"""
    assert result == expected


def test_convert_invalid_key_code():
    """Test converting with an invalid key code."""
    # Create test data with an invalid key code
    dts_data = {
        "matrix_size": (1, 1),
        "matrix_map": [["((0) << 8 | (0))"]],
        "keymap": {
            "default": [["&kp INVALID"]],
        },
    }

    # Convert to Kanata
    converter = KanataConverter()
    with pytest.raises(ValueError):
        converter.convert(dts_data)


def test_convert_invalid_key_type():
    """Test converting with an invalid key type."""
    # Create test data with an invalid key type
    dts_data = {
        "matrix_size": (1, 1),
        "matrix_map": [["((0) << 8 | (0))"]],
        "keymap": {
            "default": [["&invalid A"]],
        },
    }

    # Convert to Kanata
    converter = KanataConverter()
    with pytest.raises(ValueError):
        converter.convert(dts_data)


def test_kanata_transformer_error_binding():
    """Test that error bindings are rendered as Kanata comments and summarized."""
    from converter.model.keymap_model import Binding, Layer, KeymapConfig
    from converter.transformer.kanata_transformer import KanataTransformer

    # Create a binding with an error param
    error_param = "ERROR: test error binding"
    binding = Binding(behavior=None, params=[error_param])
    layer = Layer(name="default", index=0, bindings=[binding])
    keymap = KeymapConfig(layers=[layer])

    transformer = KanataTransformer()
    output = transformer.transform(keymap)

    # Check for the error comment in the layer
    assert "; ERROR: test error binding" in output
    # Check for the error in the summary at the end
    assert "test error binding" in output
    # Check that the error comment is unindented (at start of line)
    for line in output.splitlines():
        if "; ERROR: test error binding" in line:
            assert line.startswith(";")
    # Check line length
    for line in output.splitlines():
        assert len(line) <= 79


def test_kanata_transformer_nested_macro():
    """Test that deeply nested modifier macros are parsed recursively."""
    from converter.model.keymap_model import Binding, Layer, KeymapConfig
    from converter.transformer.kanata_transformer import KanataTransformer

    macro = "LS(LA(LG(A)))"
    binding = Binding(behavior=None, params=[macro])
    layer = Layer(name="default", index=0, bindings=[binding])
    keymap = KeymapConfig(layers=[layer])

    transformer = KanataTransformer()
    output = transformer.transform(keymap)

    # Should produce ls(la(lg(a)))
    assert "ls(la(lg(a)))" in output
    for line in output.splitlines():
        assert len(line) <= 79


def test_kanata_transformer_malformed_macro():
    """Test that malformed modifier macros emit error comments."""
    from converter.model.keymap_model import Binding, Layer, KeymapConfig
    from converter.transformer.kanata_transformer import KanataTransformer

    for macro in ["LS()", "LS(LA())", "LS(A", "LS LA(A)"]:
        binding = Binding(behavior=None, params=[macro])
        layer = Layer(name="default", index=0, bindings=[binding])
        keymap = KeymapConfig(layers=[layer])
        transformer = KanataTransformer()
        output = transformer.transform(keymap)
        # Accept any of the possible error messages
        assert (
            "; ERROR: malformed or incomplete macro" in output
            or "; ERROR: malformed or unknown macro" in output
            or "; unsupported: failed to transform layer" in output
        )
        for line in output.splitlines():
            assert len(line) <= 79


def test_kanata_transformer_unknown_modifier_macro():
    """Test that unknown modifier macros emit error comments."""
    from converter.model.keymap_model import Binding, Layer, KeymapConfig
    from converter.transformer.kanata_transformer import KanataTransformer

    macro = "XX(A)"
    binding = Binding(behavior=None, params=[macro])
    layer = Layer(name="default", index=0, bindings=[binding])
    keymap = KeymapConfig(layers=[layer])
    transformer = KanataTransformer()
    output = transformer.transform(keymap)
    assert "; ERROR: malformed or unknown macro" in output
    for line in output.splitlines():
        assert len(line) <= 79


def test_kanata_transformer_no_duplicate_macros_or_aliases():
    """Test that macros and hold-tap aliases are defined only once in the output."""
    from converter.model.keymap_model import Binding, Layer, KeymapConfig
    from converter.transformer.kanata_transformer import KanataTransformer
    from converter.behaviors.macro import MacroBehavior
    from converter.behaviors.hold_tap import HoldTapBehavior

    # Define a macro behavior
    macro_behavior = MacroBehavior(name="my_macro", bindings=["&kp A", "&kp B"])
    macro_behavior.type = "macro"  # Patch for transformer compatibility
    # Define a hold-tap behavior
    holdtap_behavior = HoldTapBehavior(
        name="lt",
        label="LT",
        binding_cells=2,
        bindings=[],
        tapping_term_ms=200,
        flavor="hold-preferred",
    )
    holdtap_behavior.hold_time_ms = 250  # Patch for transformer compatibility
    holdtap_behavior.type = "hold-tap"  # Patch for transformer compatibility
    holdtap_behavior.tap_hold_wait_ms = None  # Patch for transformer compatibility

    # Macro binding (referenced twice)
    macro_binding1 = Binding(behavior=macro_behavior, params=[])
    macro_binding2 = Binding(behavior=macro_behavior, params=[])
    # Hold-tap binding (referenced twice)
    holdtap_binding1 = Binding(behavior=holdtap_behavior, params=["LCTRL", "A"])
    holdtap_binding2 = Binding(behavior=holdtap_behavior, params=["LCTRL", "A"])

    # Two layers, each referencing the same macro and hold-tap alias
    layer1 = Layer(name="base", index=0, bindings=[macro_binding1, holdtap_binding1])
    layer2 = Layer(name="fn", index=1, bindings=[macro_binding2, holdtap_binding2])
    keymap = KeymapConfig(
        layers=[layer1, layer2],
        behaviors={"my_macro": macro_behavior, "lt": holdtap_behavior},
    )

    transformer = KanataTransformer()
    output = transformer.transform(keymap)

    print("\nKANATA OUTPUT:\n", output)

    # Macro and alias should only be defined once each
    macro_count = output.count("(defmacro my_macro")
    alias_count = output.count("(defalias lt ")
    assert macro_count == 1, f"Macro defined {macro_count} times"
    assert alias_count == 1, f"Alias defined {alias_count} times"


def test_simple_combo_full_pipeline():
    """Test that a simple combo in the ZMK keymap is converted to a Kanata alias using the full pipeline."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "dts", "simple_keymap.zmk"
    )
    with open(fixture_path, "r") as f:
        dts_content = f.read()
    parser = DtsParser()
    ast = parser.parse(dts_content)
    extractor = KeymapExtractor()
    keymap_config = extractor.extract(ast)
    transformer = KanataTransformer()
    kanata_output = transformer.transform(keymap_config)
    # Check for the expected combo alias in the output
    assert "(defalias" in kanata_output
    assert "combo_esc" in kanata_output
    assert "(combo a b esc)" in kanata_output


def test_custom_hold_tap_behavior_full_pipeline():
    """Test that a custom hold-tap behavior (home row mod) is mapped best-effort and unmapped properties are commented."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "dts", "simple_keymap.zmk"
    )
    with open(fixture_path, "r") as f:
        dts_content = f.read()
    parser = DtsParser()
    ast = parser.parse(dts_content)
    extractor = KeymapExtractor()
    keymap_config = extractor.extract(ast)
    transformer = KanataTransformer()
    kanata_output = transformer.transform(keymap_config)
    # Check for the expected home row mod alias
    assert "(defalias" in kanata_output
    assert "hm" in kanata_output
    assert "tap-hold" in kanata_output
    # Check for a comment about the unmapped retro-tap property
    assert "retro-tap" in kanata_output


def test_unicode_macro_full_pipeline(monkeypatch):
    """Test that a Unicode macro (&pi) is converted to Kanata unicode output on macOS, and a warning comment on other platforms."""
    import sys

    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "dts", "simple_keymap.zmk"
    )
    with open(fixture_path, "r") as f:
        dts_content = f.read()
    parser = DtsParser()
    ast = parser.parse(dts_content)
    extractor = KeymapExtractor()
    keymap_config = extractor.extract(ast)
    transformer = KanataTransformer()
    # Simulate macOS
    monkeypatch.setattr(sys, "platform", "darwin")
    kanata_output = transformer.transform(keymap_config)
    assert '(unicode "π")' in kanata_output
    # Simulate Linux
    monkeypatch.setattr(sys, "platform", "linux")
    kanata_output = transformer.transform(keymap_config)
    assert (
        "; WARNING: Unicode output is only supported on macOS (darwin). Unicode 'π' not emitted."
        in kanata_output
    )
    # Simulate Windows
    monkeypatch.setattr(sys, "platform", "win32")
    kanata_output = transformer.transform(keymap_config)
    assert (
        "; WARNING: Unicode output is only supported on macOS (darwin). Unicode 'π' not emitted."
        in kanata_output
    )
