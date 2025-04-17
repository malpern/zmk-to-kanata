"""Advanced tests for the macro transformer module."""

import pytest

from converter.error_handling.error_manager import get_error_manager
from converter.parser.macro_parser import (
    MacroDefinition,
    MacroStep,
    MacroUsage,
)
from converter.transformer.macro_transformer import MacroTransformer


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_parameterized_macro_definition(transformer):
    """Test handling of parameterized macro definitions."""
    get_error_manager().clear()

    # Macro with parameter
    macro_def = MacroDefinition(
        name="param_macro",
        params=["key1"],
        steps=[
            MacroStep(command="kp", params=["key1"]),  # Using param
        ],
    )
    result = transformer.transform_definition(macro_def)
    errors = get_error_manager().get_errors()

    assert not errors
    assert "param_macro" in result


def test_parameterized_macro_usage(transformer):
    """Test handling of parameterized macro usages."""
    get_error_manager().clear()

    # Register macro first
    macro_def = MacroDefinition(
        name="param_macro",
        params=["key1"],
        steps=[
            MacroStep(command="kp", params=["key1"]),
        ],
    )
    transformer.transform_definition(macro_def)

    # Use macro with parameter
    macro_usage = MacroUsage(
        name="param_macro",
        params=["A"],
    )
    result = transformer.transform_usage(macro_usage)
    errors = get_error_manager().get_errors()

    assert not errors
    assert "param_macro" in result
    assert "A" in result


def test_nested_macro_definition(transformer):
    """Test handling of nested macro definitions."""
    get_error_manager().clear()

    # Register inner macro first
    inner_macro = MacroDefinition(
        name="inner_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
        ],
    )
    transformer.transform_definition(inner_macro)

    # Macro using another macro
    outer_macro = MacroDefinition(
        name="outer_macro",
        steps=[
            MacroStep(command="macro_usage", params=["inner_macro"]),
        ],
    )
    result = transformer.transform_definition(outer_macro)
    errors = get_error_manager().get_errors()

    assert not errors
    assert "outer_macro" in result
    assert "inner_macro" in result


def test_nested_macro_usage(transformer):
    """Test handling of nested macro usages."""
    get_error_manager().clear()

    # Register both macros first
    inner_macro = MacroDefinition(
        name="inner_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
        ],
    )
    transformer.transform_definition(inner_macro)

    outer_macro = MacroDefinition(
        name="outer_macro",
        steps=[
            MacroStep(command="macro_usage", params=["inner_macro"]),
        ],
    )
    transformer.transform_definition(outer_macro)

    # Use outer macro
    macro_usage = MacroUsage(
        name="outer_macro",
        params=[],
    )
    result = transformer.transform_usage(macro_usage)
    errors = get_error_manager().get_errors()

    assert not errors
    assert "outer_macro" in result
    assert "inner_macro" in result


def test_parameterized_nested_macro(transformer):
    """Test handling of parameterized nested macros."""
    get_error_manager().clear()

    # Register both macros first
    inner_macro = MacroDefinition(
        name="inner_macro",
        params=["key1"],
        steps=[
            MacroStep(command="kp", params=["key1"]),
        ],
    )
    transformer.transform_definition(inner_macro)

    outer_macro = MacroDefinition(
        name="outer_macro",
        params=["key1"],
        steps=[
            MacroStep(command="macro_usage", params=["inner_macro", "key1"]),
        ],
    )
    transformer.transform_definition(outer_macro)

    # Use outer macro with parameter
    macro_usage = MacroUsage(
        name="outer_macro",
        params=["A"],
    )
    result = transformer.transform_usage(macro_usage)
    errors = get_error_manager().get_errors()

    assert not errors
    assert "outer_macro" in result
    assert "inner_macro" in result
    assert "A" in result


def test_invalid_parameterized_macro(transformer):
    """Test handling of invalid parameterized macros."""
    get_error_manager().clear()

    # Macro with missing parameter
    macro_def = MacroDefinition(
        name="bad_param_macro",
        params=["key1"],
        steps=[
            MacroStep(command="kp", params=["key2"]),  # Using undefined parameter
        ],
    )
    result = transformer.transform_definition(macro_def)
    errors = get_error_manager().get_errors()

    assert any("Undefined parameter" in e["message"] for e in errors)
    assert "<unknown:kp>" in result or "key2" not in result


def test_invalid_nested_macro(transformer):
    """Test handling of invalid nested macros."""
    get_error_manager().clear()

    # Macro with invalid nested usage
    macro_def = MacroDefinition(
        name="bad_nested_macro",
        steps=[
            MacroStep(command="macro_usage", params=["non_existent_macro"]),
        ],
    )
    result = transformer.transform_definition(macro_def)
    errors = get_error_manager().get_errors()

    assert any("Unknown macro" in e["message"] for e in errors)
    assert "<unknown:macro_usage>" in result or "non_existent_macro" not in result
