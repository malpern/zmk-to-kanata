"""Tests for hold-tap behavior transformation."""

from converter.model.keymap_model import (
    GlobalSettings,
    Layer,
    KeyMapping,
    KeymapConfig,
    HoldTapBinding
)
from converter.transformer.kanata_transformer import KanataTransformer
from converter.transformer.holdtap_transformer import HoldTapTransformer


def test_basic_holdtap_transformation():
    """Test transformation of a basic hold-tap binding."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="lh_hm",
        hold_key="LGUI",
        tap_key="A",
        hold_trigger_key_positions=None,
        hold_trigger_on_release=False,
        retro_tap=False
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold 200 250 a lmet)"


def test_holdtap_with_release():
    """Test hold-tap binding with hold-trigger-on-release."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="rh_hm",
        hold_key="RSHIFT",
        tap_key="J",
        hold_trigger_key_positions=None,
        hold_trigger_on_release=True,
        retro_tap=False
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold-release 200 250 j rsft)"


def test_holdtap_with_key_positions():
    """Test hold-tap binding with hold-trigger-key-positions."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="lh_hm",
        hold_key="LCTRL",
        tap_key="D",
        hold_trigger_key_positions=(1, 2, 3),
        hold_trigger_on_release=False,
        retro_tap=False
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold-release-keys 200 250 d lctl (1 2 3))"


def test_holdtap_with_retro_tap():
    """Test transformation of a hold-tap binding with retro-tap."""
    transformer = HoldTapTransformer()
    binding = HoldTapBinding(
        behavior_name="rh_hm",
        hold_key="RALT",
        tap_key="L",
        hold_trigger_key_positions=None,
        hold_trigger_on_release=False,
        retro_tap=True
    )

    result = transformer.transform_binding(binding, 200, 250)
    assert result == "(tap-hold-press-timeout 200 250 l ralt l)"


def test_full_keymap_transformation():
    """Test transformation of a complete keymap with hold-tap bindings."""
    config = KeymapConfig(
        global_settings=GlobalSettings(tap_time=200, hold_time=250),
        layers=[
            Layer(
                name="default",
                keys=[
                    [
                        KeyMapping(key="Q"),
                        KeyMapping(key="W"),
                        KeyMapping(
                            key="E",
                            hold_tap=HoldTapBinding(
                                behavior_name="lh_hm",
                                hold_key="LALT",
                                tap_key="E",
                                hold_trigger_key_positions=None,
                                hold_trigger_on_release=False,
                                retro_tap=False
                            )
                        )
                    ],
                    [
                        KeyMapping(
                            key="A",
                            hold_tap=HoldTapBinding(
                                behavior_name="lh_hm",
                                hold_key="LGUI",
                                tap_key="A",
                                hold_trigger_key_positions=None,
                                hold_trigger_on_release=True,
                                retro_tap=False
                            )
                        ),
                        KeyMapping(
                            key="S",
                            hold_tap=HoldTapBinding(
                                behavior_name="lh_hm",
                                hold_key="LCTRL",
                                tap_key="S",
                                hold_trigger_key_positions=(1, 2),
                                hold_trigger_on_release=False,
                                retro_tap=False
                            )
                        ),
                        KeyMapping(key="D")
                    ]
                ]
            )
        ]
    )

    transformer = KanataTransformer()
    result = transformer.transform(config)

    expected_lines = [
        ";; ZMK to Kanata Configuration",
        ";; Generated automatically - DO NOT EDIT",
        "",
        ";; Global settings",
        "(defvar tap-time 200)",
        "(defvar hold-time 250)",
        "",
        ";; Hold-tap aliases",
        "(defalias",
        "  lh_hm_LALT_E (tap-hold 200 250 e lalt)",
        "  lh_hm_LCTRL_S (tap-hold-release-keys 200 250 s lctl (1 2))",
        "  lh_hm_LGUI_A (tap-hold-release 200 250 a lmet)",
        ")",
        "",
        "(deflayer default",
        "  q  w  @lh_hm_LALT_E",
        "  @lh_hm_LGUI_A  @lh_hm_LCTRL_S  d",
        ")"
    ]

    assert result.splitlines() == expected_lines
