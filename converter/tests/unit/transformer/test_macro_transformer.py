"""Unit tests for the macro transformer module."""
import pytest
from converter.transformer.macro_transformer import MacroTransformer
from converter.parser.macro_parser_new import MacroDefinition, MacroStep, MacroUsage
from converter.error_handling.error_manager import get_error_manager, ErrorSeverity


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_transform_definition_basic(transformer):
    macro_def = MacroDefinition(
        name="test_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="macro_tap_time", params=["50"]),
            MacroStep(command="macro_press", params=[]),
            MacroStep(command="macro_release", params=[]),
        ]
    )
    result = transformer.transform_definition(macro_def)
    assert result.startswith("(defmacro test_macro ")
    assert "a" in result
    assert "(delay 100)" in result
    assert "(tap-hold-ms 50)" in result
    assert "press" in result
    assert "release" in result
    assert result.endswith(")")


def test_transform_usage_basic(transformer):
    usage = MacroUsage(name="test_macro", params=["param1", "param2"])
    result = transformer.transform_usage(usage)
    assert result == "(macro test_macro param1 param2)"

    usage_no_params = MacroUsage(name="simple_macro", params=[])
    result2 = transformer.transform_usage(usage_no_params)
    assert result2 == "(macro simple_macro)"


def test_transform_definition_invalid_steps(transformer):
    """Test that invalid macro steps/parameters are handled gracefully."""
    get_error_manager().clear_errors()

    # Macro with unknown command and invalid wait-time
    macro_def = MacroDefinition(
        name="bad_macro",
        steps=[
            MacroStep(command="unknown_cmd", params=["foo"]),
            MacroStep(command="macro_wait_time", params=["not_an_int"]),
            MacroStep(command="macro_tap_time", params=["-50"]),  # Negative tap time
            MacroStep(command="kp", params=[]),  # Missing key param
        ]
    )
    result = transformer.transform_definition(macro_def)
    errors = get_error_manager().get_errors()

    # Output should contain <unknown:...> for unknown/invalid steps
    assert "<unknown:unknown_cmd>" in result
    assert "<unknown:macro_wait_time>" in result or "delay" not in result
    assert "(tap-hold-ms -50)" not in result  # Should not output invalid tap time
    # There should be at least one error for each invalid step
    assert any("Unknown macro step" in e.message for e in errors)
    assert any("Invalid wait-time" in e.message for e in errors)
    assert any("Negative tap-time value" in e.message or "Invalid tap-time" in e.message for e in errors)
    # Missing key param should not crash, may produce <unknown:kp> or similar
