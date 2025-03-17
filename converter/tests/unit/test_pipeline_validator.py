"""Unit tests for the pipeline validator module."""

import tempfile
from pathlib import Path

import pytest

from converter.model.keymap_model import Layer, KeyMapping
from converter.validation.pipeline_validator import PipelineValidator


@pytest.fixture
def sample_zmk_input():
    """Return a sample ZMK input string."""
    return """
/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp A &kp B &kp C
                &kp D &kp E &kp F
            >;
        };

        layer_1 {
            bindings = <
                &kp X &kp Y &kp Z
                &kp U &kp V &kp W
            >;
        };
    };
};
"""


@pytest.fixture
def sample_kanata_output():
    """Return a sample Kanata output string."""
    return """
;; ZMK to Kanata Configuration
;; Generated automatically - DO NOT EDIT

(deflayer default
  A B C
  D E F
)

(deflayer layer_1
  X Y Z
  U V W
)
"""


@pytest.fixture
def sample_ir():
    """Return a sample intermediate representation."""
    return {
        "layers": [
            Layer(
                name="default",
                bindings=[
                    KeyMapping(key="A", position=0),
                    KeyMapping(key="B", position=1),
                    KeyMapping(key="C", position=2),
                    KeyMapping(key="D", position=3),
                    KeyMapping(key="E", position=4),
                    KeyMapping(key="F", position=5),
                ]
            ),
            Layer(
                name="layer_1",
                bindings=[
                    KeyMapping(key="X", position=0),
                    KeyMapping(key="Y", position=1),
                    KeyMapping(key="Z", position=2),
                    KeyMapping(key="U", position=3),
                    KeyMapping(key="V", position=4),
                    KeyMapping(key="W", position=5),
                ]
            )
        ],
        "global_settings": {
            "tap_time": 200,
            "hold_time": 250
        }
    }


def test_validate_input_valid(sample_zmk_input):
    """Test validating a valid ZMK input."""
    validator = PipelineValidator()
    valid, errors = validator.validate_input(sample_zmk_input)

    assert valid is True
    assert len(errors) == 0


def test_validate_input_invalid():
    """Test validating an invalid ZMK input."""
    validator = PipelineValidator()

    # Missing compatible statement
    invalid_input = """
    / {
        keymap {
            default_layer {
                bindings = <
                    &kp A &kp B
                >;
            };
        };
    };
    """
    valid, errors = validator.validate_input(invalid_input)

    assert valid is False
    assert len(errors) > 0
    assert any("compatible" in error for error in errors)


def test_validate_input_unbalanced_braces():
    """Test validating ZMK input with unbalanced braces."""
    validator = PipelineValidator()

    invalid_input = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp A &kp B
                >;
            }; // Missing closing brace
        };
    """
    valid, errors = validator.validate_input(invalid_input)

    assert valid is False
    assert any("Unbalanced braces" in error for error in errors)


def test_validate_intermediate_representation(sample_ir):
    """Test validating a valid intermediate representation."""
    validator = PipelineValidator()
    valid, errors = validator.validate_intermediate_representation(sample_ir)

    assert valid is True
    assert len(errors) == 0


def test_validate_intermediate_representation_invalid():
    """Test validating an invalid intermediate representation."""
    validator = PipelineValidator()

    # Missing layers
    invalid_ir = {
        "global_settings": {
            "tap_time": 200,
            "hold_time": 250
        }
    }

    valid, errors = validator.validate_intermediate_representation(invalid_ir)

    assert valid is False
    assert len(errors) > 0
    assert any("No layers" in error for error in errors)


def test_validate_output_valid(sample_kanata_output):
    """Test validating a valid Kanata output."""
    validator = PipelineValidator()
    valid, errors = validator.validate_output(sample_kanata_output)

    assert valid is True
    assert len(errors) == 0


def test_validate_output_invalid():
    """Test validating an invalid Kanata output."""
    validator = PipelineValidator()

    # Missing default layer
    invalid_output = """
    ;; ZMK to Kanata Configuration

    (deflayer some_layer
      A B C
    )
    """
    valid, errors = validator.validate_output(invalid_output)

    assert valid is False
    assert any("default layer" in error for error in errors)


def test_validate_pipeline(sample_zmk_input, sample_ir, sample_kanata_output):
    """Test validating the complete pipeline."""
    validator = PipelineValidator()
    result = validator.validate_pipeline(
        sample_zmk_input, sample_ir, sample_kanata_output
    )

    assert result["valid"] is True
    assert result["input_valid"] is True
    assert result["ir_valid"] is True
    assert result["output_valid"] is True
    assert len(result["input_errors"]) == 0
    assert len(result["ir_errors"]) == 0
    assert len(result["output_errors"]) == 0


def test_validate_files():
    """Test validating input and output files."""
    validator = PipelineValidator()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "test.zmk"
        output_file = Path(tmpdir) / "test.kbd"

        with open(input_file, "w") as f:
            f.write("""
/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp A &kp B
            >;
        };
    };
};
            """)

        with open(output_file, "w") as f:
            f.write("""
;; ZMK to Kanata Configuration

(deflayer default
  A B
)
            """)

        result = validator.validate_files(input_file, output_file)

        assert result["valid"] is True
        assert result["input_valid"] is True
        assert result["output_valid"] is True


def test_validate_files_missing_file():
    """Test validating with a missing file."""
    validator = PipelineValidator()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "nonexistent.zmk"
        output_file = Path(tmpdir) / "test.kbd"

        # Create only the output file
        with open(output_file, "w") as f:
            f.write("(deflayer default)\n")

        result = validator.validate_files(input_file, output_file)

        assert result["valid"] is False
        assert "File not found" in result["errors"][0]
