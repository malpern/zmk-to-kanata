"""Advanced tests for the macro transformer module."""
import pytest
from converter.transformer.macro_transformer import MacroTransformer
from converter.parser.macro_parser import MacroDefinition, MacroStep, MacroUsage
from converter.error_handling.error_manager import get_error_manager, ErrorSeverity


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_parameterized_macro_definition(transformer):
    """Test transformation of parameterized macro definitions."""
    macro_def = MacroDefinition(
        name="param_macro",
        params=["key1", "key2"],
        steps=[
            MacroStep(command="kp", params=["key1"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="kp", params=["key2"]),
        ]
    )
    result = transformer.transform_definition(macro_def)
    assert result.startswith("(defmacro param_macro (key1 key2)")
    assert "key1" in result
    assert "key2" in result
    assert "(delay 100)" in result


def test_parameterized_macro_usage(transformer):
    """Test transformation of parameterized macro usages."""
    usage = MacroUsage(name="param_macro", params=["A", "B"])
    result = transformer.transform_usage(usage)
    assert result == "(macro param_macro A B)"


def test_nested_macro_definition(transformer):
    """Test transformation of nested macro definitions."""
    macro_def = MacroDefinition(
        name="nested_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="macro_usage", params=["inner_macro"]),
            MacroStep(command="kp", params=["B"]),
        ]
    )
    result = transformer.transform_definition(macro_def)
    assert result.startswith("(defmacro nested_macro")
    assert "a" in result
    assert "(delay 100)" in result
    assert "(macro inner_macro)" in result
    assert "b" in result


def test_nested_macro_usage(transformer):
    """Test transformation of nested macro usages."""
    usage = MacroUsage(name="nested_macro", params=[])
    result = transformer.transform_usage(usage)
    assert result == "(macro nested_macro)"


def test_parameterized_nested_macro(transformer):
    """Test transformation of parameterized nested macros."""
    macro_def = MacroDefinition(
        name="complex_macro",
        params=["key1", "key2"],
        steps=[
            MacroStep(command="kp", params=["key1"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="macro_usage", params=["inner_macro", "key2"]),
            MacroStep(command="kp", params=["key1"]),
        ]
    )
    result = transformer.transform_definition(macro_def)
    assert result.startswith("(defmacro complex_macro (key1 key2)")
    assert "key1" in result
    assert "(delay 100)" in result
    assert "(macro inner_macro key2)" in result


def test_invalid_parameterized_macro(transformer):
    """Test handling of invalid parameterized macros."""
    get_error_manager().clear()

    # Macro with missing parameter
    macro_def = MacroDefinition(
        name="bad_param_macro",
        params=["key1"],
        steps=[
            MacroStep(command="kp", params=["key2"]),  # Using undefined parameter
        ]
    )
    result = transformer.transform_definition(macro_def)
    errors = get_error_manager().get_errors()
    
    assert any("Undefined parameter" in e.message for e in errors)
    assert "<unknown:kp>" in result or "key2" not in result


def test_invalid_nested_macro(transformer):
    """Test handling of invalid nested macros."""
    get_error_manager().clear()

    # Macro with invalid nested usage
    macro_def = MacroDefinition(
        name="bad_nested_macro",
        steps=[
            MacroStep(command="macro_usage", params=["non_existent_macro"]),
        ]
    )
    result = transformer.transform_definition(macro_def)
    errors = get_error_manager().get_errors()
    
    assert any("Unknown macro" in e.message for e in errors)
    assert "<unknown:macro_usage>" in result or "non_existent_macro" not in result 