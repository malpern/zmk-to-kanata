"""Unit tests for the tap-hold behavior parser."""
from textwrap import dedent


def test_basic_holdtap_properties(taphold_parser):
    """Test basic properties of hold-tap behavior parsing."""
    zmk_holdtap = dedent('''
        my_holdtap: example_hold_tap {
            compatible = "zmk,behavior-hold-tap";
            label = "MY_HOLD_TAP";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
        };
    ''')

    result = taphold_parser.parse_behavior(zmk_holdtap)

    assert result.name == "my_holdtap"
    assert result.label == "MY_HOLD_TAP"
    assert result.binding_cells == 2
    assert result.bindings == ["kp", "kp"]
    # Configuration parameters should be None by default
    assert result.tapping_term_ms is None
    assert result.quick_tap_ms is None
    assert result.require_prior_idle_ms is None
    assert result.flavor is None
    # Advanced features should have default values
    assert result.hold_trigger_key_positions is None
    assert result.hold_trigger_on_release is False
    assert result.retro_tap is False


def test_full_configuration(taphold_parser):
    """Test parsing of a fully configured hold-tap behavior."""
    zmk_holdtap = dedent('''
        hm: homerow_mods {
            compatible = "zmk,behavior-hold-tap";
            label = "HOMEROW_MODS";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            tapping-term-ms = <280>;
            quick-tap-ms = <175>;
            require-prior-idle-ms = <150>;
            flavor = "balanced";
        };
    ''')

    result = taphold_parser.parse_behavior(zmk_holdtap)

    assert result.name == "hm"
    assert result.tapping_term_ms == 280
    assert result.quick_tap_ms == 175
    assert result.require_prior_idle_ms == 150
    assert result.flavor == "balanced"


def test_advanced_features(taphold_parser):
    """Test parsing of advanced hold-tap features."""
    zmk_holdtap = dedent('''
        lh_hm: left_home_row_mods {
            compatible = "zmk,behavior-hold-tap";
            label = "LEFT_HOME_ROW_MODS";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            flavor = "balanced";
            hold-trigger-key-positions = <6 7 8 9 10 11>;
            hold-trigger-on-release;
            retro-tap;
        };
    ''')

    result = taphold_parser.parse_behavior(zmk_holdtap)

    assert result.name == "lh_hm"
    assert result.hold_trigger_key_positions == [6, 7, 8, 9, 10, 11]
    assert result.hold_trigger_on_release is True
    assert result.retro_tap is True


def test_partial_configuration(taphold_parser):
    """Test parsing of a partially configured hold-tap behavior."""
    zmk_holdtap = dedent('''
        partial: partial_config {
            compatible = "zmk,behavior-hold-tap";
            label = "PARTIAL";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            tapping-term-ms = <200>;
            flavor = "tap-preferred";
            // Missing quick-tap-ms and require-prior-idle-ms
        };
    ''')

    result = taphold_parser.parse_behavior(zmk_holdtap)

    assert result.name == "partial"
    assert result.tapping_term_ms == 200
    assert result.quick_tap_ms is None
    assert result.require_prior_idle_ms is None
    assert result.flavor == "tap-preferred"


def test_real_world_example(taphold_parser):
    """Test parsing of a real-world home row mods configuration."""
    zmk_holdtap = dedent('''
        lh_hm: left_home_row_mods {
            compatible = "zmk,behavior-hold-tap";
            label = "LEFT_HOME_ROW_MODS";
            #binding-cells = <2>;
            flavor = "balanced";
            tapping-term-ms = <280>;
            quick-tap-ms = <175>;
            require-prior-idle-ms = <150>;
            bindings = <&kp>, <&kp>;
            hold-trigger-key-positions = <6 7 8 9 10 11>;
            hold-trigger-on-release;
        };
    ''')

    result = taphold_parser.parse_behavior(zmk_holdtap)

    assert result.name == "lh_hm"
    assert result.label == "LEFT_HOME_ROW_MODS"
    assert result.binding_cells == 2
    assert result.bindings == ["kp", "kp"]
    assert result.tapping_term_ms == 280
    assert result.quick_tap_ms == 175
    assert result.require_prior_idle_ms == 150
    assert result.flavor == "balanced"
    assert result.hold_trigger_key_positions == [6, 7, 8, 9, 10, 11]
    assert result.hold_trigger_on_release is True
    assert result.retro_tap is False 