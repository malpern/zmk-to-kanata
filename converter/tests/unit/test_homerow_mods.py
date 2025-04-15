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
    assert behavior.mod == "LCTL"
    assert behavior.key == "A"
    assert behavior.is_mac is False
    
    # Test with Mac-specific modifiers
    mac_parser = HomeRowModParser(is_mac=True)
    behavior = mac_parser.parse("&hm LGUI A")
    assert behavior is not None
    assert behavior.mod == "LGUI"
    assert behavior.key == "A"
    assert behavior.is_mac is True
    
    # Test invalid homerow mod bindings
    assert parser.parse("&kp A") is None
    assert parser.parse("&hm") is None
    assert parser.parse("&hm LCTL") is None


def test_homerow_mod_behavior_kanata_mod():
    """Test the kanata_mod property of HomeRowModBehavior."""
    # Test standard modifiers
    behavior = HomeRowModBehavior(mod="LCTL", key="A")
    assert behavior.kanata_mod == "lctl"
    
    behavior = HomeRowModBehavior(mod="LALT", key="S")
    assert behavior.kanata_mod == "lalt"
    
    behavior = HomeRowModBehavior(mod="LSHFT", key="D")
    assert behavior.kanata_mod == "lsft"
    
    behavior = HomeRowModBehavior(mod="LGUI", key="F")
    assert behavior.kanata_mod == "lmet"
    
    # Test right-hand modifiers
    behavior = HomeRowModBehavior(mod="RCTL", key="J")
    assert behavior.kanata_mod == "rctl"
    
    behavior = HomeRowModBehavior(mod="RALT", key="K")
    assert behavior.kanata_mod == "ralt"
    
    behavior = HomeRowModBehavior(mod="RSHFT", key="L")
    assert behavior.kanata_mod == "rsft"
    
    behavior = HomeRowModBehavior(mod="RGUI", key="SEMI")
    assert behavior.kanata_mod == "rmet"
    
    # Test Mac-specific modifiers
    behavior = HomeRowModBehavior(mod="LGUI", key="A", is_mac=True)
    assert behavior.kanata_mod == "lmet"
    
    behavior = HomeRowModBehavior(mod="RGUI", key="SEMI", is_mac=True)
    assert behavior.kanata_mod == "rmet"


def test_homerow_mod_behavior_to_kanata():
    """Test the to_kanata method of HomeRowModBehavior."""
    behavior = HomeRowModBehavior(mod="LCTL", key="A")
    assert behavior.to_kanata() == "(tap-hold 200 200 a lctl)"
    
    behavior = HomeRowModBehavior(mod="LGUI", key="S", tap_time=150, hold_time=250)
    assert behavior.to_kanata() == "(tap-hold 150 250 s lmet)"
    
    behavior = HomeRowModBehavior(mod="RGUI", key="SEMI", is_mac=True)
    assert behavior.to_kanata() == "(tap-hold 200 200 ; rmet)"


def test_homerow_mod_transformer():
    """Test the HomeRowModTransformer class."""
    transformer = HomeRowModTransformer()
    
    behavior = HomeRowModBehavior(mod="LCTL", key="A")
    assert transformer.transform_binding(behavior) == "(tap-hold 200 200 a lctl)"
    
    # Test with custom timing parameters
    transformer.set_timing_parameters(tap_time=150, hold_time=250)
    assert transformer.transform_binding(behavior) == "(tap-hold 150 250 a lctl)"
    
    # Test with Mac-specific modifiers
    mac_transformer = HomeRowModTransformer(is_mac=True)
    behavior = HomeRowModBehavior(mod="LGUI", key="A")
    assert mac_transformer.transform_binding(behavior) == "(tap-hold 200 200 a lmet)" 