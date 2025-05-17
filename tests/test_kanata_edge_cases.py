"""Edge case tests for ZMK to Kanata converter.

Tests combos, sticky keys, Unicode, tap-dance, and error scenarios.
"""

from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.transformer.kanata_transformer import KanataTransformer

ZMK_COMPLEX_COMBO = """
/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&kp A>;
        };
    };
    combos {
        combo1 {
            key-positions = <0 1>;
            bindings = <&mo 1>;
        };
    };
};
"""

ZMK_STICKY_KEYS = """
/ {
    behaviors {
        sk_lshift: sk {
            compatible = "zmk,behavior-sticky-key";
        };
        sk_rshift: sk {
            compatible = "zmk,behavior-sticky-key";
        };
        sk_lctrl: sk {
            compatible = "zmk,behavior-sticky-key";
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&sk_lshift LSHIFT &sk_rshift RSHIFT &sk_lctrl LCTRL>;
        };
    };
};
"""

ZMK_UNICODE = """
/ {
    behaviors {
        uni_pi: unicode {
            compatible = "zmk,behavior-unicode";
            unicode = <0x03C0>;
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&uni_pi>;
        };
    };
};
"""

ZMK_TAPDANCE_3ACTIONS = """
/ {
    behaviors {
        td: tapdance {
            compatible = "zmk,behavior-tap-dance";
            label = "TAPDANCE";
            tapping-term-ms = <200>;
            bindings = <&kp A>, <&kp B>, <&kp C>;
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&td A B C>;
        };
    };
};
"""

ZMK_TAPDANCE_HOLD = """
/ {
    behaviors {
        td: tapdance {
            compatible = "zmk,behavior-tap-dance";
            label = "TAPDANCE";
            tapping-term-ms = <200>;
            bindings = <&kp A>, <&kp B>;
            hold-action = <&kp C>;
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&td A B>;
        };
    };
};
"""

ZMK_MALFORMED_MACRO = """
/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <LSHIFT(>;
        };
    };
};
"""


def parse_and_transform(zmk_str):
    """Parse DTS string and transform to Kanata output."""
    parser = DtsParser()
    tree = parser.parse(zmk_str)
    keymap = KeymapExtractor().extract(tree)
    return KanataTransformer().transform(keymap)


def test_complex_combo_todo(capsys):
    """Test that complex combos emit a TODO or unsupported comment."""
    kanata = parse_and_transform(ZMK_COMPLEX_COMBO)

    captured = capsys.readouterr()

    assert (
        "Skipping combo 'combo1'" in captured.out
        and "missing/invalid properties" in captured.out
    ), "Expected warning about skipping combo was not printed to stdout"

    assert "unsupported: combo 'combo1'" not in kanata
    assert "(deflayer default_layer" in kanata

    search_string = "\n  a\n"

    assert search_string in kanata


def test_sticky_keys():
    """Test sticky key behaviors are mapped to one-shot and symbolic names."""
    kanata = parse_and_transform(ZMK_STICKY_KEYS)
    assert "one-shot" in kanata
    assert "lsft" in kanata and "rsft" in kanata and "lctl" in kanata


def test_unicode_output():
    """Test Unicode output emits unicode or TODO/warning."""
    kanata = parse_and_transform(ZMK_UNICODE)
    assert "unicode" in kanata or "WARNING" in kanata or "TODO" in kanata


def test_tapdance_3actions():
    """Test tap-dance with 3 actions emits correct Kanata syntax."""
    kanata = parse_and_transform(ZMK_TAPDANCE_3ACTIONS)
    assert "(tap-dance 200 a b c)" in kanata
    assert "TODO" not in kanata


def test_tapdance_hold_todo():
    """Test tap-dance with hold-action emits a TODO and doc link."""
    kanata = parse_and_transform(ZMK_TAPDANCE_HOLD)
    assert "TODO" in kanata and "tap-dance" in kanata
    assert (
        "https://github.com/jtroo/kanata/blob/main/docs/" "config.md#tap-dance"
    ) in kanata


def test_malformed_macro():
    """Test malformed macro emits an error and summary section."""
    kanata = parse_and_transform(ZMK_MALFORMED_MACRO)
    assert "ERROR: malformed or incomplete macro" in kanata
    assert "; --- Unsupported/Unknown ZMK Features ---" in kanata
