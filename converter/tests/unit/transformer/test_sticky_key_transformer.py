"""Unit tests for the sticky key transformer module."""
import pytest
from converter.transformer.sticky_key_transformer import StickyKeyTransformer

class SimpleBinding:
    def __init__(self, key):
        self.key = key

@pytest.fixture
def transformer():
    """Create a StickyKeyTransformer instance."""
    return StickyKeyTransformer()

def test_basic_sticky_key_transformations(transformer):
    """Test basic sticky key transformations."""
    assert transformer.transform_binding(SimpleBinding("LSHIFT")) == "(sticky-key lshift)"
    assert transformer.transform_binding(SimpleBinding("RSHIFT")) == "(sticky-key rshift)"
    assert transformer.transform_binding(SimpleBinding("LCTRL")) == "(sticky-key lctrl)"

def test_modifier_combinations(transformer):
    """Test sticky key transformations with different modifiers."""
    assert transformer.transform_binding(SimpleBinding("LSHIFT")) == "(sticky-key lshift)"
    assert transformer.transform_binding(SimpleBinding("RSHIFT")) == "(sticky-key rshift)"
    assert transformer.transform_binding(SimpleBinding("LCTRL")) == "(sticky-key lctrl)"
    assert transformer.transform_binding(SimpleBinding("RCTRL")) == "(sticky-key rctrl)"
    assert transformer.transform_binding(SimpleBinding("LALT")) == "(sticky-key lalt)"
    assert transformer.transform_binding(SimpleBinding("RALT")) == "(sticky-key ralt)"
    assert transformer.transform_binding(SimpleBinding("LGUI")) == "(sticky-key lgui)"
    assert transformer.transform_binding(SimpleBinding("RGUI")) == "(sticky-key rgui)"

def test_special_key_sticky_transformations(transformer):
    """Test sticky key transformations with special keys."""
    assert transformer.transform_binding(SimpleBinding("F1")) == "(sticky-key f1)"
    assert transformer.transform_binding(SimpleBinding("PG_UP")) == "(sticky-key pg_up)"
    assert transformer.transform_binding(SimpleBinding("C_MUTE")) == "(sticky-key c_mute)"

def test_layer_sticky_transformations(transformer):
    """Test sticky key transformations with layer switches."""
    assert transformer.transform_binding(SimpleBinding("mo 1")) == "(sticky-key mo 1)"
    assert transformer.transform_binding(SimpleBinding("trans")) == "(sticky-key trans)"

def test_timing_parameter_transformations(transformer):
    """Test sticky key transformations with timing parameters."""
    assert transformer.transform_binding(SimpleBinding("LSHIFT")) == "(sticky-key lshift)"
    assert transformer.transform_binding(SimpleBinding("LCTRL")) == "(sticky-key lctrl)"

def test_basic_key_sticky_transformations(transformer):
    """Test sticky key transformations with basic keys."""
    assert transformer.transform_binding(SimpleBinding("A")) == "(sticky-key a)"
    assert transformer.transform_binding(SimpleBinding("B")) == "(sticky-key b)"
    assert transformer.transform_binding(SimpleBinding("N1")) == "(sticky-key n1)"
    assert transformer.transform_binding(SimpleBinding("N0")) == "(sticky-key n0)"
    assert transformer.transform_binding(SimpleBinding("KP_N7")) == "(sticky-key kp_n7)"
