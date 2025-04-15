"""Unit tests for the macro transformer module."""
import pytest
from converter.transformer.macro_transformer import MacroTransformer
from converter.parser.macro_parser_new import MacroDefinition, MacroStep, MacroUsage


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
