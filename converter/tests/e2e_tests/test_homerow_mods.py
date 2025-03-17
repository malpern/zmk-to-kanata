"""End-to-end tests for homerow mods functionality."""

import sys
import io
from pathlib import Path

from converter.zmk_to_kanata import convert_zmk_to_kanata
from converter.error_handling import ErrorManager


def test_homerow_mods_conversion():
    """Test conversion of ZMK homerow mods to Kanata format."""
    # Setup test content
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp ESC   &hm LGUI A &hm LALT S &hm LCTRL D &hm LSHFT F &kp G
                    &kp H &hm RSHFT J  &hm RCTRL K &hm RALT L &hm RGUI SEMI &kp SQT
                >;
            };
        };
    };
    """
    
    # Convert ZMK to Kanata
    error_manager = ErrorManager()
    kanata_config, _ = convert_zmk_to_kanata(
        zmk_content=zmk_content,
        error_manager=error_manager
    )
    
    # Check that homerow mods were converted correctly
    assert "(tap-hold 200 200 a lmet)" in kanata_config
    assert "(tap-hold 200 200 s lalt)" in kanata_config
    assert "(tap-hold 200 200 d lctl)" in kanata_config
    assert "(tap-hold 200 200 f lsft)" in kanata_config
    assert "(tap-hold 200 200 j rsft)" in kanata_config
    assert "(tap-hold 200 200 k rctl)" in kanata_config
    assert "(tap-hold 200 200 l ralt)" in kanata_config
    assert "(tap-hold 200 200 ; rmet)" in kanata_config


def test_homerow_mods_mac_conversion():
    """Test conversion of ZMK homerow mods to Kanata format with Mac modifiers."""
    # Setup test content
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp ESC   &hm LGUI A &hm LALT S &hm LCTRL D &hm LSHFT F &kp G
                    &kp H &hm RSHFT J  &hm RCTRL K &hm RALT L &hm RGUI SEMI &kp SQT
                >;
            };
        };
    };
    """
    
    # Convert ZMK to Kanata with Mac modifiers
    error_manager = ErrorManager()
    kanata_config, _ = convert_zmk_to_kanata(
        zmk_content=zmk_content,
        error_manager=error_manager,
        is_mac=True
    )
    
    # Check that homerow mods were converted correctly with Mac modifiers
    assert "(tap-hold 200 200 a lmet)" in kanata_config
    assert "(tap-hold 200 200 s lalt)" in kanata_config
    assert "(tap-hold 200 200 d lctl)" in kanata_config
    assert "(tap-hold 200 200 f lsft)" in kanata_config
    assert "(tap-hold 200 200 j rsft)" in kanata_config
    assert "(tap-hold 200 200 k rctl)" in kanata_config
    assert "(tap-hold 200 200 l ralt)" in kanata_config
    assert "(tap-hold 200 200 ; rmet)" in kanata_config 