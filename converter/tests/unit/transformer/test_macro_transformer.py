"""Unit tests for the macro transformer module."""
import pytest
from converter.behaviors.macro import MacroBehavior
from converter.transformer.macro_transformer import MacroTransformer


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_basic_macro_transformation(transformer):
    """Test basic macro transformation without timing parameters."""
    behavior = MacroBehavior(
        name="test_macro",
        bindings=[
            "&macro_tap",
            "&kp A",
            "&kp B",
        ]
    )
    result = transformer.transform_behavior(behavior)
    assert "(defmacro test_macro" in result
    assert "tap-hold-ms" in result
    assert "a" in result
    assert "b" in result


def test_macro_with_wait_time(transformer):
    """Test macro transformation with wait time."""
    behavior = MacroBehavior(
        name="wait_macro",
        bindings=[
            "&kp A",
            "&macro_wait_time 100",
            "&kp B",
        ]
    )
    result = transformer.transform_behavior(behavior)
    assert "(defmacro wait_macro" in result
    assert "delay 100" in result
    assert "a" in result
    assert "b" in result


def test_macro_with_tap_time(transformer):
    """Test macro transformation with tap time."""
    behavior = MacroBehavior(
        name="tap_macro",
        bindings=[
            "&kp A",
            "&macro_tap_time 50",
            "&kp B",
        ]
    )
    result = transformer.transform_behavior(behavior)
    assert "(defmacro tap_macro" in result
    assert "tap-hold-ms 50" in result
    assert "a" in result
    assert "b" in result


def test_macro_with_press_release(transformer):
    """Test macro transformation with press and release."""
    behavior = MacroBehavior(
        name="mod_macro",
        bindings=[
            "&macro_press",
            "&kp LSHIFT",
            "&kp A",
            "&macro_release",
            "&kp LSHIFT",
        ]
    )
    result = transformer.transform_behavior(behavior)
    assert "(defmacro mod_macro" in result
    assert "press lsft" in result
    assert "tap a" in result
    assert "release lsft" in result


def test_invalid_wait_time(transformer):
    """Test handling of invalid wait time."""
    behavior = MacroBehavior(
        name="invalid_wait",
        bindings=[
            "&kp A",
            "&macro_wait_time -100",  # Negative wait time
            "&kp B",
        ]
    )
    with pytest.raises(ValueError) as exc_info:
        transformer.transform_behavior(behavior)
    assert "Negative wait-time value" in str(exc_info.value)


def test_invalid_tap_time(transformer):
    """Test handling of invalid tap time."""
    behavior = MacroBehavior(
        name="invalid_tap",
        bindings=[
            "&kp A",
            "&macro_tap_time 0",  # Zero tap time
            "&kp B",
        ]
    )
    with pytest.raises(ValueError) as exc_info:
        transformer.transform_behavior(behavior)
    assert "Zero tap-time value" in str(exc_info.value)


def test_large_timing_values(transformer):
    """Test handling of large timing values."""
    behavior = MacroBehavior(
        name="large_timing",
        bindings=[
            "&kp A",
            "&macro_wait_time 20000",  # Too large
            "&kp B",
        ]
    )
    with pytest.raises(ValueError) as exc_info:
        transformer.transform_behavior(behavior)
    assert "wait-time value too large" in str(exc_info.value)


def test_complex_macro_timing(transformer):
    """Test complex macro with multiple timing parameters."""
    behavior = MacroBehavior(
        name="complex_timing",
        bindings=[
            "&macro_tap",
            "&kp A",
            "&macro_wait_time 100",
            "&macro_tap_time 50",
            "&kp B",
            "&macro_press",
            "&kp LSHIFT",
            "&macro_wait_time 200",
            "&kp C",
            "&macro_release",
            "&kp LSHIFT",
        ]
    )
    result = transformer.transform_behavior(behavior)

    # Check presence of all timing-related commands
    assert "(defmacro complex_timing" in result
    assert "tap-hold-ms" in result
    assert "delay 100" in result
    assert "tap-hold-ms 50" in result
    assert "delay 200" in result

    # Check correct sequence of operations
    result_lines = result.split("\n")
    for line in result_lines:
        if "tap-hold-ms" in line and "a" in line:
            break
    else:
        assert False, "Missing tap-hold-ms with 'a'"

    for line in result_lines:
        if "delay 100" in line:
            break
    else:
        assert False, "Missing delay 100"

    for line in result_lines:
        if "tap-hold-ms 50" in line and "b" in line:
            break
    else:
        assert False, "Missing tap-hold-ms with 'b'"

    for line in result_lines:
        if "press lsft" in line:
            break
    else:
        assert False, "Missing press lsft"

    for line in result_lines:
        if "delay 200" in line:
            break
    else:
        assert False, "Missing delay 200"

    for line in result_lines:
        if "tap c" in line:
            break
    else:
        assert False, "Missing tap c"

    for line in result_lines:
        if "release lsft" in line:
            break
    else:
        assert False, "Missing release lsft"
