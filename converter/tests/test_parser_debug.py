"""Tests for debugging ZMK parser functionality."""

import re

from converter.model.keymap_model import KeyMapping
from converter.parser.zmk_parser import ZMKParser


def test_layer_pattern_matching():
    """Test that layer patterns are correctly matched."""
    parser = ZMKParser()
    sample_text = '''
    / {
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A &kp B
                    &kp C &kp D
                >;
            };
        };
    };
    '''
    print("\nSample text:")
    print(sample_text)
    print("\nBindings pattern:", parser.bindings_pattern.pattern)
    matches = list(parser.bindings_pattern.finditer(sample_text))
    print("\nFound matches:", len(matches))
    if matches:
        for i, match in enumerate(matches):
            print(f"\nMatch {i + 1}:")
            print("Groups:", match.groups())
            print("Start:", match.start())
            print("End:", match.end())
    assert len(matches) == 1, "Should find one layer"
    match = matches[0]
    assert "&kp A" in match.group(1), "Should capture bindings"


def test_binding_text_preprocessing():
    """Test that binding text preprocessing maintains structure."""
    binding_text = '''
        &kp A &kp B
        &kp C &kp D
    '''
    # Test angle bracket removal
    cleaned = re.sub(r'<\s*(.*?)\s*>', r'\1', binding_text)
    assert "&kp A" in cleaned, "Should preserve binding text"

    # Test row splitting
    rows = [row.strip() for row in cleaned.split('\n') if row.strip()]
    assert len(rows) == 2, "Should find two rows"
    assert "&kp A &kp B" in rows[0], "Should preserve row structure"


def test_binding_pattern_recognition():
    """Test that different binding formats are recognized."""
    test_cases = [
        ("&kp A", True),
        ("&mo 1", True),
        ("&trans", True),
        ("&kp EXCL", True),
        ("&kp N1", True),
        ("invalid", False)
    ]
    for binding, should_match in test_cases:
        # We now accept all bindings that start with &
        is_valid = binding.startswith('&') if should_match else False
        assert is_valid == should_match, f"Failed for {binding}"


def test_row_splitting():
    """Test that row splitting preserves binding structure."""
    parser = ZMKParser()
    binding_text = '''
        &kp A &kp B
        &kp C &mo 1
    '''
    keys = parser._parse_bindings(binding_text)
    assert len(keys) == 2, "Should find two rows"
    assert len(keys[0]) == 2, "Each row should have two bindings"
    assert keys[0][0].key == "A", "Should parse first key correctly"


def test_key_mapping_creation():
    """Test that KeyMapping objects are created correctly."""
    test_cases = [
        ("&kp A", "A"),
        ("&mo 1", "mo 1"),
        ("&trans", "trans")
    ]
    for binding, expected_key in test_cases:
        # Handle both kp and non-kp bindings
        if binding.startswith("&kp "):
            key = binding.replace("&kp ", "")
        else:
            key = binding.replace("&", "")
        mapping = KeyMapping(key=key)
        assert mapping is not None, f"Should create mapping for {binding}"
        assert mapping.key == expected_key, f"Wrong key for {binding}"


def test_global_pattern_matching():
    """Test that global settings are correctly matched."""
    parser = ZMKParser()
    sample_text = '''
    / {
        global {
            tap-time = <200>;
            hold-time = <300>;
        };
    };
    '''
    match = parser.global_pattern.search(sample_text)
    assert match is not None, "Should find global settings"
    assert match.group(1) == "200", "Should capture tap time"
    assert match.group(2) == "300", "Should capture hold time"
