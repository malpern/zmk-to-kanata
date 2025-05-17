from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.transformer.kanata_transformer import KanataTransformer

ZMK_HOME_ROW_MODS = """
/ {
    behaviors {
        mt_a: mod_tap_a {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <LSHIFT A>;
        };
        mt_s: mod_tap_s {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <LCTRL S>;
        };
        mt_l: mod_tap_l {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <RALT L>;
        };
        mt_semi: mod_tap_semi {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <RGUI SEMI>;
        };
        mt_slash: mod_tap_slash {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <LALT SLASH>;
        };
        mt_num: mod_tap_num {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            bindings = <56 4>; // Numeric: 56=SLASH, 4=A
        };
        mt_adv: mod_tap_adv {
            compatible = "zmk,behavior-hold-tap";
            tapping-term-ms = <200>;
            flavor = "hold-preferred";
            retro-tap = <1>;
            bindings = <LALT D>;
        };
    };
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &mt_a LSHIFT A &mt_s LCTRL S &mt_l RALT L &mt_semi RGUI SEMI
                &mt_slash LALT SLASH &mt_num 56 4 &mt_adv LALT D
            >;
        };
    };
};
"""


def test_kanata_home_row_mods_symbolic_aliases():
    parser = DtsParser()
    ast = parser.parse(ZMK_HOME_ROW_MODS)
    extractor = KeymapExtractor()
    keymap_config = extractor.extract(ast)
    transformer = KanataTransformer()
    kanata_output = transformer.transform(keymap_config)

    # Check that all mod-tap aliases use symbolic names
    assert "(defalias" in kanata_output
    # Check for each alias
    assert "ht_lsft_a" in kanata_output  # mt_a
    assert "ht_lctl_s" in kanata_output  # mt_s
    assert "ht_ralt_l" in kanata_output  # mt_l
    assert "ht_rmet_semi" in kanata_output  # mt_semi (RGUI->rmet, SEMI->semi)
    assert "ht_lalt_fslh" in kanata_output  # mt_slash (SLASH->fslh)
    assert "ht_fslh_a" in kanata_output  # mt_num (numeric 56->fslh, 4->a)
    # Check that tap/hold keys in alias definitions are symbolic (not numeric)
    for line in kanata_output.splitlines():
        if line.strip().startswith("(defalias"):
            parts = line.strip().split()
            # (defalias name (tap-hold tap_time hold_time tap_key hold_key))
            if len(parts) >= 8 and parts[2] == "(tap-hold":
                tap_key = parts[5]
                hold_key = parts[6].rstrip(")")
                assert not tap_key.isdigit(), f"Numeric tap_key in alias: {line}"
                assert not hold_key.isdigit(), f"Numeric hold_key in alias: {line}"
    # Check for TODO comment for retro-tap
    assert "; TODO: retro-tap property present" in kanata_output
    # Check that all tap/hold keys in alias definitions are symbolic
    for key in ["lsft", "lctl", "ralt", "rmet", "semi", "fslh", "a", "d"]:
        assert key in kanata_output
