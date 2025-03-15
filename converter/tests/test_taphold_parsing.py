import pytest
from textwrap import dedent

from converter.taphold_parser import HoldTapParser

def test_basic_holdtap_properties():
    """Test parsing of basic hold-tap behavior properties."""
    zmk_holdtap = dedent('''
        my_holdtap: example_hold_tap {
            compatible = "zmk,behavior-hold-tap";
            label = "MY_HOLD_TAP";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
        };
    ''')
    
    parser = HoldTapParser()
    result = parser.parse_behavior(zmk_holdtap)
    
    assert result.name == "my_holdtap"
    assert result.label == "MY_HOLD_TAP"
    assert result.binding_cells == 2
    assert result.bindings == ["kp", "kp"]

def test_invalid_behavior():
    """Test that non-hold-tap behaviors are rejected."""
    zmk_other = dedent('''
        other_behavior: some_other {
            compatible = "zmk,behavior-other";
            label = "OTHER";
        };
    ''')
    
    parser = HoldTapParser()
    with pytest.raises(ValueError, match="Not a hold-tap behavior"):
        parser.parse_behavior(zmk_other)

def test_missing_required_fields():
    """Test that missing required fields raise appropriate errors."""
    zmk_incomplete = dedent('''
        incomplete: bad_hold_tap {
            compatible = "zmk,behavior-hold-tap";
            // Missing label and binding-cells
            bindings = <&kp>, <&kp>;
        };
    ''')
    
    parser = HoldTapParser()
    with pytest.raises(ValueError, match="Missing required fields"):
        parser.parse_behavior(zmk_incomplete) 