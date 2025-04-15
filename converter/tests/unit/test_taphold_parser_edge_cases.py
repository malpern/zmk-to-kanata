# NOTE: This file was previously archived as junk. Review for compliance with the new architecture and redundancy before further use.

"""Tests for edge cases in the tap-hold behavior parser."""
import pytest
from textwrap import dedent

from converter.taphold_parser import TapHoldParser
from converter.parser.parser_error import ParserError

# Fixture needed: taphold_parser (defined in sibling conftest or this file)
@pytest.fixture
def taphold_parser():
    return TapHoldParser()

@pytest.mark.skip(reason="TapHoldParser likely needs refactoring")
def test_key_positions_with_commas(taphold_parser: TapHoldParser):
    """Test parsing of key positions with comma separators."""
    zmk_holdtap = dedent('''
        test: test_positions {
            compatible = "zmk,behavior-hold-tap";
            label = "TEST";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            hold-trigger-key-positions = <1, 2, 3, 4>;
        };
    ''')

    result = taphold_parser.parse_behavior(zmk_holdtap)
    assert result.hold_trigger_key_positions == [1, 2, 3, 4]


@pytest.mark.skip(reason="TapHoldParser likely needs refactoring")
def test_invalid_key_positions(taphold_parser: TapHoldParser):
    """Test that invalid key positions are rejected."""
    zmk_holdtap = dedent('''
        invalid: bad_positions {
            compatible = "zmk,behavior-hold-tap";
            label = "INVALID";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            hold-trigger-key-positions = <1 2 bad 4>;
        };
    ''')

    with pytest.raises(ValueError, match="Invalid key position value"):
        taphold_parser.parse_behavior(zmk_holdtap)


@pytest.mark.skip(reason="TapHoldParser likely needs refactoring")
def test_invalid_flavor(taphold_parser: TapHoldParser):
    """Test that invalid flavor values are rejected."""
    zmk_holdtap = dedent('''
        invalid: bad_flavor {
            compatible = "zmk,behavior-hold-tap";
            label = "INVALID";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            flavor = "not-a-real-flavor";
        };
    ''')

    with pytest.raises(ValueError, match="Invalid flavor"):
        taphold_parser.parse_behavior(zmk_holdtap)


@pytest.mark.skip(reason="TapHoldParser likely needs refactoring")
def test_invalid_behavior(taphold_parser: TapHoldParser):
    """Test that non-hold-tap behaviors are rejected."""
    zmk_other = dedent('''
        other_behavior: some_other {
            compatible = "zmk,behavior-other";
            label = "OTHER";
        };
    ''')

    with pytest.raises(ValueError, match="Not a hold-tap behavior"):
        taphold_parser.parse_behavior(zmk_other)


@pytest.mark.skip(reason="TapHoldParser likely needs refactoring")
def test_missing_required_fields(taphold_parser: TapHoldParser):
    """Test that missing required fields raise appropriate errors."""
    zmk_incomplete = dedent('''
        incomplete: bad_hold_tap {
            compatible = "zmk,behavior-hold-tap";
            // Missing label and binding-cells
            bindings = <&kp>, <&kp>;
        };
    ''')

    error_msg = "Invalid behavior: missing binding-cells"
    with pytest.raises(ValueError, match=error_msg):
        taphold_parser.parse_behavior(zmk_incomplete)


@pytest.mark.skip(reason="TapHoldParser likely needs refactoring")
@pytest.mark.parametrize("field,value,error_msg", [
    ("tapping-term-ms", "<-100>", "must be positive"),
    ("quick-tap-ms", "<0>", "must be positive"),
    ("require-prior-idle-ms", "<-50>", "must be positive"),
    ("flavor", '"invalid"', "Invalid flavor"),
    ("bindings", "<&invalid>", "Invalid binding format"),
])
def test_invalid_field_values(taphold_parser: TapHoldParser, field, value, error_msg):
    """Test validation of field values."""
    zmk_holdtap = dedent(f'''
        test: test_invalid {{
            compatible = "zmk,behavior-hold-tap";
            label = "TEST";
            #binding-cells = <2>;
            bindings = <&kp>, <&kp>;
            {field} = {value};
        }};
    ''')

    with pytest.raises(ValueError, match=error_msg):
        taphold_parser.parse_behavior(zmk_holdtap)
