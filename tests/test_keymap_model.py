"""Unit tests for converter/model/keymap_model.py."""

import pytest
from converter.model.keymap_model import Binding, GlobalSettings, HoldTap


def test_binding_to_kanata_raises():
    """Binding.to_kanata should raise NotImplementedError."""
    b = Binding()
    with pytest.raises(NotImplementedError):
        b.to_kanata()


def test_global_settings_fields_and_equality():
    """GlobalSettings fields are set correctly and support equality."""
    gs1 = GlobalSettings(tap_time=200, hold_time=250)
    gs2 = GlobalSettings(tap_time=200, hold_time=250)
    gs3 = GlobalSettings(tap_time=180, hold_time=220)
    assert gs1.tap_time == 200
    assert gs1.hold_time == 250
    assert gs1 == gs2
    assert gs1 != gs3


def test_holdtap_to_kanata_default():
    """HoldTap to_kanata outputs correct Kanata S-expression for default flavor."""
    ht = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    result = ht.to_kanata()
    assert result.startswith("(tap-hold ")
    assert "lsft" in result
    assert "a" in result


def test_holdtap_to_kanata_flavors():
    """HoldTap to_kanata outputs correct type for each flavor."""
    ht_balanced = HoldTap(
        name="mt", hold_key="LCTRL", tap_key="B", tapping_term_ms=200, flavor="balanced"
    )
    ht_hold = HoldTap(
        name="mt",
        hold_key="LCTRL",
        tap_key="B",
        tapping_term_ms=200,
        flavor="hold-preferred",
    )
    assert "tap-hold-release" in ht_balanced.to_kanata()
    assert "tap-hold-press" in ht_hold.to_kanata()


def test_holdtap_to_kanata_number_and_numpad():
    """HoldTap to_kanata handles number and numpad keys correctly."""
    ht_num = HoldTap(name="mt", hold_key="LALT", tap_key="N1", tapping_term_ms=200)
    ht_numpad = HoldTap(
        name="mt", hold_key="LALT", tap_key="KP_N2", tapping_term_ms=200
    )
    assert "1" in ht_num.to_kanata()
    assert "kp_n2" in ht_numpad.to_kanata()


def test_holdtapbinding_equality_and_to_kanata():
    """Test HoldTapBinding equality and to_kanata delegation."""
    ht1 = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    ht2 = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    from converter.model.keymap_model import HoldTapBinding

    b1 = HoldTapBinding(key="A", hold_tap=ht1, tap="A", hold="LSHIFT")
    b2 = HoldTapBinding(key="A", hold_tap=ht2, tap="A", hold="LSHIFT")
    b3 = HoldTapBinding(key="B", hold_tap=ht1, tap="B", hold="LSHIFT")
    assert b1 == b2
    assert b1 != b3
    assert b1.to_kanata() == ht1.to_kanata()


def test_keymapping_equality():
    """Test KeyMapping equality logic."""
    from converter.model.keymap_model import KeyMapping

    k1 = KeyMapping(key="A")
    k2 = KeyMapping(key="A")
    k3 = KeyMapping(key="B")
    assert k1 == k2
    assert k1 != k3


def test_keymapping_to_kanata_branches():
    """Test KeyMapping.to_kanata for all major branches."""
    from converter.model.keymap_model import KeyMapping, HoldTap, HoldTapBinding

    # hold_tap with name attribute
    ht = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    htb = HoldTapBinding(key="A", hold_tap=ht, tap="A", hold="LSHIFT")
    km = KeyMapping(key="A", hold_tap=htb)
    assert km.to_kanata().startswith("@mt_LSHIFT_A")

    # hold_tap without name attribute (simulate fallback)
    class DummyHT:
        def to_kanata(self):
            return "(dummy)"

    km2 = KeyMapping(key="A", hold_tap=DummyHT())
    assert km2.to_kanata() == "(dummy)"
    # mo/layer
    km3 = KeyMapping(key="mo 2")
    assert km3.to_kanata() == "(layer-while-held 2)"
    # trans
    km4 = KeyMapping(key="trans")
    assert km4.to_kanata() == "_"
    # sticky F-key
    km5 = KeyMapping(key="F1", sticky=True)
    assert km5.to_kanata() == "sticky-F1"
    # sticky modifier
    km6 = KeyMapping(key="LSHIFT", sticky=True)
    assert km6.to_kanata() == "sticky-lsft"
    # regular key
    km7 = KeyMapping(key="a")
    assert km7.to_kanata() == "a"
    # number key with n prefix
    km8 = KeyMapping(key="n2")
    assert km8.to_kanata() == "2"
    # numpad key
    km9 = KeyMapping(key="kp_n3")
    assert km9.to_kanata() == "kp3"


def test_keymapping_from_zmk_branches():
    """Test KeyMapping.from_zmk for all supported and error branches."""
    from converter.model.keymap_model import KeyMapping

    # &none
    km_none = KeyMapping.from_zmk("&none")
    assert km_none.key == "none"
    # &trans
    km_trans = KeyMapping.from_zmk("&trans")
    assert km_trans.key == "trans"
    # &sk (sticky)
    km_sticky = KeyMapping.from_zmk("&sk LSHIFT")
    assert km_sticky.key == "LSHIFT" and km_sticky.sticky
    # &sk error
    import pytest

    with pytest.raises(ValueError):
        KeyMapping.from_zmk("&sk")
    # Hold-tap valid
    km_ht = KeyMapping.from_zmk("&mt LSHIFT A")
    assert km_ht.hold_tap is not None
    # Hold-tap error (too few parts)
    with pytest.raises(ValueError):
        KeyMapping.from_zmk("&mt LSHIFT")
    # &mo (momentary layer)
    km_mo = KeyMapping.from_zmk("&mo 2")
    assert km_mo.key == "mo 2"
    # &mo error
    with pytest.raises(ValueError):
        KeyMapping.from_zmk("&mo")
    # &to (layer toggle)
    km_to = KeyMapping.from_zmk("&to 1")
    assert km_to.key == "to 1"
    # &to error
    with pytest.raises(ValueError):
        KeyMapping.from_zmk("&to")
    # &kp (regular key)
    km_kp = KeyMapping.from_zmk("&kp A")
    assert km_kp.key == "A"
    # &kp error
    with pytest.raises(ValueError):
        KeyMapping.from_zmk("&kp")
    # Unknown & prefix
    with pytest.raises(ValueError):
        KeyMapping.from_zmk("&foo BAR")
    # Direct key (no prefix)
    km_direct = KeyMapping.from_zmk("C")
    assert km_direct.key == "C"


def test_layer_and_keymapconfig():
    """Test Layer and KeymapConfig dataclasses for instantiation and equality."""
    from converter.model.keymap_model import Layer, KeymapConfig

    l1 = Layer(name="base", index=0)
    l2 = Layer(name="base", index=0)
    l3 = Layer(name="fn", index=1)
    assert l1 == l2
    assert l1 != l3
    # KeymapConfig
    kc1 = KeymapConfig(layers=[l1, l3])
    kc2 = KeymapConfig(layers=[l1, l3])
    assert kc1 == kc2
