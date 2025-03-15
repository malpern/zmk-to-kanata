"""Tests for hold-tap keymap integration."""

from textwrap import dedent

from converter.layer_parser import LayerParser
from converter.model.keymap_model import HoldTapBinding, KeyMapping


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
    bindings = parser.parse_bindings_matrix(layers[0].bindings)
    
    # Verify first row
    assert len(bindings[0]) == 3
    assert bindings[0][0].key == "Q"
    assert bindings[0][0].hold_tap is None
    assert bindings[0][1].key == "W"
    assert bindings[0][1].hold_tap is None
    assert bindings[0][2].key == "E"
    assert bindings[0][2].hold_tap == HoldTapBinding("lh_hm", "LALT", "E")
    
    # Verify second row
    assert len(bindings[1]) == 3
    assert bindings[1][0].key == "A"
    assert bindings[1][0].hold_tap == HoldTapBinding("lh_hm", "LGUI", "A")
    assert bindings[1][1].key == "S"
    assert bindings[1][1].hold_tap == HoldTapBinding("lh_hm", "LCTRL", "S")
    assert bindings[1][2].key == "D"
    assert bindings[1][2].hold_tap is None
    
    # Verify third row
    assert len(bindings[2]) == 3
    assert bindings[2][0].key == "Z"
    assert bindings[2][0].hold_tap is None
    assert bindings[2][1].key == "trans"
    assert bindings[2][1].hold_tap is None
    assert bindings[2][2].key == "mo 1"
    assert bindings[2][2].hold_tap is None


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
    
    # Parse bindings matrix
    bindings = parser.parse_bindings_matrix(layers[0].bindings)
    
    # Verify left-hand home row mods
    assert bindings[1][0].key == "A"
    assert bindings[1][0].hold_tap == HoldTapBinding("lh_hm", "LGUI", "A")
    assert bindings[1][1].key == "S"
    assert bindings[1][1].hold_tap == HoldTapBinding("lh_hm", "LALT", "S")
    assert bindings[1][2].key == "D"
    assert bindings[1][2].hold_tap == HoldTapBinding("lh_hm", "LCTRL", "D")
    assert bindings[1][3].key == "F"
    assert bindings[1][3].hold_tap == HoldTapBinding("lh_hm", "LSHIFT", "F")
    
    # Verify right-hand home row mods
    assert bindings[4][0].key == "J"
    assert bindings[4][0].hold_tap == HoldTapBinding("rh_hm", "RSHIFT", "J")
    assert bindings[4][1].key == "K"
    assert bindings[4][1].hold_tap == HoldTapBinding("rh_hm", "RCTRL", "K")
    assert bindings[4][2].key == "L"
    assert bindings[4][2].hold_tap == HoldTapBinding("rh_hm", "RALT", "L")
    assert bindings[4][3].key == "SEMI"
    assert bindings[4][3].hold_tap == HoldTapBinding("rh_hm", "RGUI", "SEMI") 