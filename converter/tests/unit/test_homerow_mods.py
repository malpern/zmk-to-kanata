"""Unit tests for homerow mods functionality."""

import pytest

from converter.behaviors.homerow_mods import (
    HomeRowModBehavior,
    HomeRowModParser,
    is_homerow_mod_binding
)
from converter.transformer.homerow_mod_transformer import HomeRowModTransformer


def test_is_homerow_mod_binding():
    """Test the is_homerow_mod_binding function."""
    assert is_homerow_mod_binding("&hm LCTL A")
    assert is_homerow_mod_binding("&hm LGUI S")
    assert not is_homerow_mod_binding("&kp A")
    assert not is_homerow_mod_binding("&mt LCTL A")
    assert not is_homerow_mod_binding("")


def test_homerow_mod_parser():
    """Test the HomeRowModParser class."""
    parser = HomeRowModParser()
    
    # Test valid homerow mod bindings
    behavior = parser.parse("&hm LCTL A")
    assert behavior is not None
    assert behavior.mod_key == "LCTL"
    assert behavior.tap_key == "A"
    assert behavior.is_mac is False
    
    # Test with Mac-specific modifiers
    mac_parser = HomeRowModParser(is_mac=True)
    behavior = mac_parser.parse("&hm LGUI A")
    assert behavior is not None
    assert behavior.mod_key == "LGUI"
    assert behavior.tap_key == "A"
    assert behavior.is_mac is True
    
    # Test invalid homerow mod bindings
    assert parser.parse("&kp A") is None
    assert parser.parse("&hm") is None
    assert parser.parse("&hm LCTL") is None


def test_homerow_mod_behavior_kanata_mod():
    """Test the kanata_mod property of HomeRowModBehavior."""
    # Test standard modifiers
    behavior = HomeRowModBehavior(mod_key="LCTL", tap_key="A")
    assert behavior.kanata_mod == "lctl"
    
    behavior = HomeRowModBehavior(mod_key="LALT", tap_key="S")
    assert behavior.kanata_mod == "lalt"
    
    behavior = HomeRowModBehavior(mod_key="LSHIFT", tap_key="D")
    assert behavior.kanata_mod == "lsft"
    
    behavior = HomeRowModBehavior(mod_key="LGUI", tap_key="F")
    assert behavior.kanata_mod == "lmet"
    
    # Test right-hand modifiers
    behavior = HomeRowModBehavior(mod_key="RCTL", tap_key="J")
    assert behavior.kanata_mod == "rctl"
    
    behavior = HomeRowModBehavior(mod_key="RALT", tap_key="K")
    assert behavior.kanata_mod == "ralt"
    
    behavior = HomeRowModBehavior(mod_key="RSHIFT", tap_key="L")
    assert behavior.kanata_mod == "rsft"
    
    behavior = HomeRowModBehavior(mod_key="RGUI", tap_key="SEMI")
    assert behavior.kanata_mod == "rmet"
    
    # Test Mac-specific modifiers
    behavior = HomeRowModBehavior(mod_key="LGUI", tap_key="A", is_mac=True)
    assert behavior.kanata_mod == "lcmd"
    
    behavior = HomeRowModBehavior(mod_key="RGUI", tap_key="SEMI", is_mac=True)
    assert behavior.kanata_mod == "rcmd"


def test_homerow_mod_behavior_to_kanata():
    """Test the to_kanata method of HomeRowModBehavior."""
    behavior = HomeRowModBehavior(mod_key="LCTL", tap_key="A")
    assert behavior.to_kanata() == "(tap-hold 200 200 a lctl)"
    
    behavior = HomeRowModBehavior(mod_key="LGUI", tap_key="S", tapping_term_ms=150)
    assert behavior.to_kanata() == "(tap-hold 150 150 s lmet)"
    
    behavior = HomeRowModBehavior(mod_key="RGUI", tap_key="SEMI", is_mac=True)
    assert behavior.to_kanata() == "(tap-hold 200 200 semi rcmd)"


class SimpleHomerowModBinding:
    def __init__(self, key, mod):
        self.key = key
        self.mod = mod


def test_homerow_mod_transformer():
    """Test the HomeRowModTransformer."""
    transformer = HomeRowModTransformer()

    # Test non-Mac
    behavior = SimpleHomerowModBinding(key="A", mod="LCTL")
    assert transformer.transform_binding(behavior) == "(tap-hold-release 200 200 a lctl)"

    behavior = SimpleHomerowModBinding(key="S", mod="LGUI")
    assert transformer.transform_binding(behavior) == "(tap-hold-release 200 200 s lgui)"

    # Test Mac (simulate by lowercasing mod)
    mac_transformer = HomeRowModTransformer()
    behavior_mac = SimpleHomerowModBinding(key="A", mod="lcmd")
    assert mac_transformer.transform_binding(behavior_mac) == "(tap-hold-release 200 200 a lcmd)"

    # Test with custom tapping term (simulate by changing transformer's timeout)
    transformer_custom = HomeRowModTransformer(timeout_ms=150, hold_ms=150)
    behavior_term = SimpleHomerowModBinding(key="F", mod="LALT")
    assert transformer_custom.transform_binding(behavior_term) == "(tap-hold-release 150 150 f lalt)" 