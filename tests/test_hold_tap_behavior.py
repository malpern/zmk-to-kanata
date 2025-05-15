import pytest
from converter.model.keymap_model import HoldTap, HoldTapBinding
from converter.behaviors.hold_tap import HoldTapBehavior


def test_holdtap_happy_path():
    ht = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    assert ht.name == "mt"
    assert ht.hold_key == "LSHIFT"
    assert ht.tap_key == "A"
    assert ht.to_kanata().startswith("(")


def test_holdtap_type_errors():
    with pytest.raises(TypeError):
        HoldTap(name=123, hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    with pytest.raises(TypeError):
        HoldTap(name="mt", hold_key=123, tap_key="A", tapping_term_ms=200)
    with pytest.raises(TypeError):
        HoldTap(name="mt", hold_key="LSHIFT", tap_key=123, tapping_term_ms=200)


def test_holdtapbinding_happy_path():
    ht = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    htb = HoldTapBinding(
        key="A",
        hold_tap=ht,
        tap="A",
        hold="LSHIFT",
        params={"tapping_term_ms": 200, "hold_time_ms": 200},
    )
    assert htb.key == "A"
    assert htb.hold_tap == ht
    assert htb.tap == "A"
    assert htb.hold == "LSHIFT"
    assert htb.params == {"tapping_term_ms": 200, "hold_time_ms": 200}
    assert htb.to_kanata() == ht.to_kanata()


def test_holdtapbinding_type_errors():
    ht = HoldTap(name="mt", hold_key="LSHIFT", tap_key="A", tapping_term_ms=200)
    with pytest.raises(TypeError):
        HoldTapBinding(key=123, hold_tap=ht, tap="A", hold="LSHIFT", params={})
    with pytest.raises(TypeError):
        HoldTapBinding(
            key="A", hold_tap="not_a_holdtap", tap="A", hold="LSHIFT", params={}
        )
    with pytest.raises(TypeError):
        HoldTapBinding(key="A", hold_tap=ht, tap=123, hold="LSHIFT", params={})
    with pytest.raises(TypeError):
        HoldTapBinding(key="A", hold_tap=ht, tap="A", hold=123, params={})
    with pytest.raises(TypeError):
        HoldTapBinding(
            key="A", hold_tap=ht, tap="A", hold="LSHIFT", params={123: "bad"}
        )
    with pytest.raises(TypeError):
        HoldTapBinding(
            key="A", hold_tap=ht, tap="A", hold="LSHIFT", params={"good": 1.23}
        )


def test_holdtapbehavior_happy_path():
    htb = HoldTapBehavior(
        name="mt",
        label="My HoldTap",
        binding_cells=2,
        bindings=["&mt LSHIFT A", "&mt LCTRL B"],
        tapping_term_ms=200,
        quick_tap_ms=100,
        require_prior_idle_ms=50,
        flavor="balanced",
        hold_trigger_key_positions=[1, 2],
        hold_trigger_on_release=True,
        retro_tap=True,
    )
    assert htb.name == "mt"
    assert htb.label == "My HoldTap"
    assert htb.binding_cells == 2
    assert htb.bindings == ["&mt LSHIFT A", "&mt LCTRL B"]
    assert htb.tapping_term_ms == 200
    assert htb.quick_tap_ms == 100
    assert htb.require_prior_idle_ms == 50
    assert htb.flavor == "balanced"
    assert htb.hold_trigger_key_positions == [1, 2]
    assert htb.hold_trigger_on_release is True
    assert htb.retro_tap is True
    assert htb.to_kanata().startswith("(holdtap-behavior mt My HoldTap 2 [")


def test_holdtapbehavior_type_errors():
    with pytest.raises(TypeError):
        HoldTapBehavior(name=123, label="lbl", binding_cells=2, bindings=["a"])
    with pytest.raises(TypeError):
        HoldTapBehavior(name="mt", label=123, binding_cells=2, bindings=["a"])
    with pytest.raises(TypeError):
        HoldTapBehavior(name="mt", label="lbl", binding_cells="2", bindings=["a"])
    with pytest.raises(TypeError):
        HoldTapBehavior(name="mt", label="lbl", binding_cells=2, bindings="a")
    with pytest.raises(TypeError):
        HoldTapBehavior(name="mt", label="lbl", binding_cells=2, bindings=[1])
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt",
            label="lbl",
            binding_cells=2,
            bindings=["a"],
            tapping_term_ms="200",
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt", label="lbl", binding_cells=2, bindings=["a"], quick_tap_ms="100"
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt",
            label="lbl",
            binding_cells=2,
            bindings=["a"],
            require_prior_idle_ms="50",
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt", label="lbl", binding_cells=2, bindings=["a"], flavor=123
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt",
            label="lbl",
            binding_cells=2,
            bindings=["a"],
            hold_trigger_key_positions="notalist",
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt",
            label="lbl",
            binding_cells=2,
            bindings=["a"],
            hold_trigger_key_positions=[1, "bad"],
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt",
            label="lbl",
            binding_cells=2,
            bindings=["a"],
            hold_trigger_on_release="bad",
        )
    with pytest.raises(TypeError):
        HoldTapBehavior(
            name="mt", label="lbl", binding_cells=2, bindings=["a"], retro_tap="bad"
        )
