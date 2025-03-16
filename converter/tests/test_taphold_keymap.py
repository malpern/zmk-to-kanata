"""Test module for tap-hold keymap functionality."""
from textwrap import dedent

from ..layer_parser import LayerParser


def test_basic_holdtap_binding():
    """Test parsing of a basic hold-tap binding."""
    parser = LayerParser()
    binding = "&lh_hm LGUI A"
    
    result = parser.parse_binding(binding)
    
    assert result.key == "A"
    assert result.hold_tap is not None
    assert result.hold_tap.behavior_name == "lh_hm"
    assert result.hold_tap.hold_key == "LGUI"
    assert result.hold_tap.tap_key == "A"


def test_mixed_bindings_layer():
    """Test parsing a layer with mixed hold-tap and regular bindings."""
    parser = LayerParser()
    layer_content = dedent('''
        default_layer {
            bindings = <
                &kp Q       &kp W       &lh_hm LALT E
                &lh_hm LGUI A &lh_hm LCTRL S &kp D
                &kp Z       &trans      &mo 1
            >;
        };
    ''')
    
    layers = parser.extract_layers(layer_content)
    assert len(layers) == 1
    
    # Parse bindings matrix
    layer = layers[0]
    assert len(layer.keys) == 3  # Three rows
    assert len(layer.keys[0]) == 3  # Three columns

    # Check regular key
    assert layer.keys[0][0].key == "Q"

    # Check hold-tap binding
    assert layer.keys[1][0].hold_tap is not None
    assert layer.keys[1][0].hold_tap.hold_key == "LGUI"
    assert layer.keys[1][0].hold_tap.tap_key == "A"

    # Check layer switch
    assert layer.keys[2][2].key == "mo 1"


def test_real_world_homerow_mods():
    """Test parsing real-world home row mods configuration."""
    parser = LayerParser()
    layer_content = dedent('''
        default_layer {
            bindings = <
                &kp Q       &kp W       &kp E          &kp R
                &lh_hm LGUI A &lh_hm LALT S &lh_hm LCTRL D &lh_hm LSHIFT F
                &kp Z       &kp X       &kp C          &kp V
                
                &kp U       &kp I       &kp O          &kp P
                &rh_hm RSHIFT J &rh_hm RCTRL K &rh_hm RALT L &rh_hm RGUI SEMI
                &kp M       &kp COMMA   &kp DOT        &kp FSLH
            >;
        };
    ''')
    
    layers = parser.extract_layers(layer_content)
    assert len(layers) == 1
    
    # Parse keys matrix
    layer = layers[0]
    assert len(layer.keys) == 6  # 6 rows
    
    # Check first row
    assert len(layer.keys[0]) == 4  # 4 columns
    assert layer.keys[0][0].key == "Q"
    assert layer.keys[0][1].key == "W"
    assert layer.keys[0][2].key == "E"
    assert layer.keys[0][3].key == "R"

    # Check home row mods
    assert layer.keys[1][0].hold_tap is not None
    assert layer.keys[1][0].hold_tap.hold_key == "LGUI"
    assert layer.keys[1][0].hold_tap.tap_key == "A"

    assert layer.keys[4][3].hold_tap is not None
    assert layer.keys[4][3].hold_tap.hold_key == "RGUI"
    assert layer.keys[4][3].hold_tap.tap_key == "SEMI" 