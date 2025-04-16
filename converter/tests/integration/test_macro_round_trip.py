"""Integration tests for macro round-trip conversion."""
import pytest
from converter.parser.macro_parser import MacroDefinition, MacroStep, MacroUsage
from converter.transformer.macro_transformer import MacroTransformer
from converter.parser.macro_parser import parse_macro_definition, parse_macro_usage


@pytest.fixture
def transformer():
    """Create a MacroTransformer instance."""
    return MacroTransformer()


def test_round_trip_basic_macro(transformer):
    """Test round-trip conversion of a basic macro."""
    # Original macro definition
    original_def = MacroDefinition(
        name="test_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="kp", params=["B"]),
        ]
    )
    
    # Convert to Kanata format
    kanata_def = transformer.transform_definition(original_def)
    
    # Parse back to ZMK format
    parsed_def = parse_macro_definition(kanata_def)
    
    # Compare original and parsed definitions
    assert parsed_def.name == original_def.name
    assert len(parsed_def.steps) == len(original_def.steps)
    assert parsed_def.steps[0].command == original_def.steps[0].command
    assert parsed_def.steps[0].params == original_def.steps[0].params
    assert parsed_def.steps[1].command == original_def.steps[1].command
    assert parsed_def.steps[1].params == original_def.steps[1].params
    assert parsed_def.steps[2].command == original_def.steps[2].command
    assert parsed_def.steps[2].params == original_def.steps[2].params


def test_round_trip_parameterized_macro(transformer):
    """Test round-trip conversion of a parameterized macro."""
    # Original macro definition
    original_def = MacroDefinition(
        name="param_macro",
        params=["key1", "key2"],
        steps=[
            MacroStep(command="kp", params=["key1"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="kp", params=["key2"]),
        ]
    )
    
    # Convert to Kanata format
    kanata_def = transformer.transform_definition(original_def)
    
    # Parse back to ZMK format
    parsed_def = parse_macro_definition(kanata_def)
    
    # Compare original and parsed definitions
    assert parsed_def.name == original_def.name
    assert parsed_def.params == original_def.params
    assert len(parsed_def.steps) == len(original_def.steps)
    for i in range(len(original_def.steps)):
        assert parsed_def.steps[i].command == original_def.steps[i].command
        assert parsed_def.steps[i].params == original_def.steps[i].params


def test_round_trip_nested_macro(transformer):
    """Test round-trip conversion of a nested macro."""
    # Original macro definition
    original_def = MacroDefinition(
        name="nested_macro",
        steps=[
            MacroStep(command="kp", params=["A"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="macro_usage", params=["inner_macro"]),
            MacroStep(command="kp", params=["B"]),
        ]
    )
    
    # Convert to Kanata format
    kanata_def = transformer.transform_definition(original_def)
    
    # Parse back to ZMK format
    parsed_def = parse_macro_definition(kanata_def)
    
    # Compare original and parsed definitions
    assert parsed_def.name == original_def.name
    assert len(parsed_def.steps) == len(original_def.steps)
    for i in range(len(original_def.steps)):
        assert parsed_def.steps[i].command == original_def.steps[i].command
        assert parsed_def.steps[i].params == original_def.steps[i].params


def test_round_trip_macro_usage(transformer):
    """Test round-trip conversion of macro usages."""
    # Original macro usage
    original_usage = MacroUsage(name="test_macro", params=["A", "B"])
    
    # Convert to Kanata format
    kanata_usage = transformer.transform_usage(original_usage)
    
    # Parse back to ZMK format
    parsed_usage = parse_macro_usage(kanata_usage)
    
    # Compare original and parsed usages
    assert parsed_usage.name == original_usage.name
    assert parsed_usage.params == original_usage.params


def test_round_trip_complex_macro(transformer):
    """Test round-trip conversion of a complex macro with parameters and nesting."""
    # Original macro definition
    original_def = MacroDefinition(
        name="complex_macro",
        params=["key1", "key2"],
        steps=[
            MacroStep(command="kp", params=["key1"]),
            MacroStep(command="macro_wait_time", params=["100"]),
            MacroStep(command="macro_usage", params=["inner_macro", "key2"]),
            MacroStep(command="kp", params=["key1"]),
        ]
    )
    
    # Convert to Kanata format
    kanata_def = transformer.transform_definition(original_def)
    
    # Parse back to ZMK format
    parsed_def = parse_macro_definition(kanata_def)
    
    # Compare original and parsed definitions
    assert parsed_def.name == original_def.name
    assert parsed_def.params == original_def.params
    assert len(parsed_def.steps) == len(original_def.steps)
    for i in range(len(original_def.steps)):
        assert parsed_def.steps[i].command == original_def.steps[i].command
        assert parsed_def.steps[i].params == original_def.steps[i].params 