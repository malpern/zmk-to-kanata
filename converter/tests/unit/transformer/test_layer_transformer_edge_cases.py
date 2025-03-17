"""Edge case tests for the layer transformer module."""
import pytest
from converter.layer_transformer import LayerTransformer
from converter.model.keymap_model import Layer, KeyMapping
from converter.behaviors.key_sequence import KeySequenceBinding


@pytest.fixture
def transformer():
    """Create a LayerTransformer instance."""
    return LayerTransformer()


def test_empty_layer_transformation(transformer):
    """Test transforming an empty layer."""
    layer = Layer(name="empty", bindings=[])
    result = transformer.transform_layer(layer)
    assert "(deflayer empty" in result
    assert len(result.split()) == 2  # Only contains deflayer and name


def test_layer_with_empty_bindings(transformer):
    """Test layer with empty/None bindings."""
    layer = Layer(
        name="test",
        bindings=[None, KeyMapping(key="A"), None, KeyMapping(key="B")]
    )
    result = transformer.transform_layer(layer)
    assert "(deflayer test" in result
    assert "_ a _ b" in result


def test_complex_key_sequences(transformer):
    """Test complex key sequence transformations."""
    # Test empty sequence
    empty_seq = KeySequenceBinding(keys=[])
    assert transformer.transform_binding(empty_seq) == "(chord)"

    # Test sequence with duplicates
    dup_seq = KeySequenceBinding(keys=["A", "A", "B", "B"])
    assert transformer.transform_binding(dup_seq) == "(chord a a b b)"

    # Test sequence with mixed case
    mixed_seq = KeySequenceBinding(keys=["a", "B", "c"])
    assert transformer.transform_binding(mixed_seq) == "(chord a b c)"


def test_invalid_key_mappings(transformer):
    """Test handling of invalid key mappings."""
    # Test empty key
    assert transformer.transform_binding(KeyMapping(key="")) == "_"

    # Test None key
    assert transformer.transform_binding(KeyMapping(key=None)) == "_"

    # Test whitespace key
    assert transformer.transform_binding(KeyMapping(key="   ")) == "_"

    # Test invalid characters
    assert transformer.transform_binding(
        KeyMapping(key="!@#$%")
    ) == "unknown !@#$%"


def test_layer_name_edge_cases(transformer):
    """Test layer name edge cases."""
    # Test empty name
    layer = Layer(name="", bindings=[KeyMapping(key="A")])
    result = transformer.transform_layer(layer)
    assert "(deflayer" in result
    assert "a" in result

    # Test name with spaces
    layer = Layer(name="test layer", bindings=[KeyMapping(key="A")])
    result = transformer.transform_layer(layer)
    assert "(deflayer test_layer" in result

    # Test name with special characters
    layer = Layer(name="test!@#$", bindings=[KeyMapping(key="A")])
    result = transformer.transform_layer(layer)
    assert "(deflayer test" in result


def test_nested_matrix_transformations(transformer):
    """Test nested matrix transformations."""
    # Test nested empty lists
    matrix = [[[], []], [[], []]]
    result = transformer.transform_bindings_matrix(matrix)
    assert all(isinstance(row, list) for row in result)
    assert all(all(item == "_" for item in row) for row in result)

    # Test irregular matrix
    matrix = [
        [KeyMapping(key="A")],
        [KeyMapping(key="B"), KeyMapping(key="C")],
        []
    ]
    result = transformer.transform_bindings_matrix(matrix)
    assert len(result) == 3
    assert result[0] == ["a"]
    assert result[1] == ["b", "c"]
    assert result[2] == []


def test_special_character_transformations(transformer):
    """Test transformations with special characters."""
    # Test Unicode characters
    assert transformer.transform_binding(
        KeyMapping(key="é")
    ) == "unknown é"

    # Test escape characters
    assert transformer.transform_binding(
        KeyMapping(key="\t")
    ) == "unknown \\t"

    # Test quotation marks
    assert transformer.transform_binding(
        KeyMapping(key='"test"')
    ) == 'unknown "test"'
