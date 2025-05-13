import pytest
from converter.transformer.holdtap_transformer import HoldTapTransformer
from converter.model.keymap_model import HoldTap, HoldTapBinding


def make_binding(
    hold="LSHIFT",
    tap="A",
    flavor=None,
    tapping_term_ms=200,
    hold_time_ms=None,
    quick_tap_ms=None,
    tap_hold_wait_ms=None,
    require_prior_idle_ms=None,
):
    ht = HoldTap(
        name="mt",
        hold_key=hold,
        tap_key=tap,
        tapping_term_ms=tapping_term_ms,
        hold_time_ms=hold_time_ms,
        quick_tap_ms=quick_tap_ms,
        flavor=flavor,
    )
    setattr(ht, "tap_hold_wait_ms", tap_hold_wait_ms)
    setattr(ht, "require_prior_idle_ms", require_prior_idle_ms)
    return HoldTapBinding(
        key=tap,
        hold_tap=ht,
        tap=tap,
        hold=hold,
        params={},
    )


def test_transformer_init():
    t = HoldTapTransformer()
    assert "hold-preferred" in t.flavor_map
    assert "LSHIFT" in t.modifier_map
    assert t.config["tapping_term_ms"] == 200


def test_transform_binding_happy_path():
    t = HoldTapTransformer()
    b = make_binding()
    result = t.transform_binding(b)
    assert result.startswith("(tap-hold ")
    assert "lsft" in result
    assert "a" in result


def test_transform_binding_flavors():
    t = HoldTapTransformer()
    for flavor, kanata in t.flavor_map.items():
        b = make_binding(flavor=flavor)
        result = t.transform_binding(b)
        assert result.startswith(f"({kanata} ")


def test_transform_binding_optional_params():
    t = HoldTapTransformer()
    b = make_binding(quick_tap_ms=50, tap_hold_wait_ms=60, require_prior_idle_ms=70)
    result = t.transform_binding(b)
    assert "50" in result
    assert "60" in result
    assert "70" in result


def test_transform_behavior_happy_path():
    t = HoldTapTransformer()
    ht = HoldTap(
        name="mt",
        hold_key="LSHIFT",
        tap_key="A",
        tapping_term_ms=200,
        hold_time_ms=250,
        quick_tap_ms=None,
        flavor="hold-preferred",
    )
    setattr(ht, "tap_hold_wait_ms", None)
    setattr(ht, "require_prior_idle_ms", None)
    alias_def, alias_name = t.transform_behavior(ht, "LSHIFT", "A")
    assert alias_def.startswith("(defalias ")
    assert "lsft" in alias_def
    assert "a" in alias_def
    assert alias_name


def test_transform_behavior_flavors():
    t = HoldTapTransformer()
    for flavor, kanata in t.flavor_map.items():
        ht = HoldTap(
            name="mt",
            hold_key="LSHIFT",
            tap_key="A",
            tapping_term_ms=200,
            hold_time_ms=250,
            quick_tap_ms=None,
            flavor=flavor,
        )
        setattr(ht, "tap_hold_wait_ms", None)
        setattr(ht, "require_prior_idle_ms", None)
        alias_def, _ = t.transform_behavior(ht, "LSHIFT", "A")
        assert alias_def.startswith("(defalias ")
        assert kanata in alias_def


def test_transform_behavior_optional_params():
    """Test transform_behavior with all optional params set."""
    t = HoldTapTransformer()
    ht = HoldTap(
        name="mt",
        hold_key="LSHIFT",
        tap_key="A",
        tapping_term_ms=200,
        hold_time_ms=250,
        quick_tap_ms=50,
        flavor="hold-preferred",
    )
    setattr(ht, "tap_hold_wait_ms", 60)
    setattr(ht, "require_prior_idle_ms", 70)
    alias_def, alias_name = t.transform_behavior(ht, "LSHIFT", "A")
    assert "50" in alias_def
    assert "60" in alias_def
    assert "70" in alias_def


def test_transform_binding_error_no_hold_tap():
    t = HoldTapTransformer()
    b = make_binding()
    # Patch to remove hold_tap
    b = HoldTapBinding(
        key=b.key, hold_tap=None, tap=b.tap, hold=b.hold, params=b.params
    )
    with pytest.raises(ValueError):
        t.transform_binding(b)


def test_transform_binding_error_no_hold():
    t = HoldTapTransformer()
    b = make_binding()
    b = HoldTapBinding(
        key=b.key, hold_tap=b.hold_tap, tap=b.tap, hold=None, params=b.params
    )
    with pytest.raises(ValueError):
        t.transform_binding(b)


def test_transform_binding_error_no_tap():
    t = HoldTapTransformer()
    b = make_binding()
    b = HoldTapBinding(
        key=b.key, hold_tap=b.hold_tap, tap=None, hold=b.hold, params=b.params
    )
    with pytest.raises(ValueError):
        t.transform_binding(b)
