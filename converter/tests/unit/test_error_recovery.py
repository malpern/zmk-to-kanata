"""Tests for the error recovery manager."""

from converter.error_recovery import ErrorRecoveryManager
from converter.model.keymap_model import Layer, KeyMapping


def test_handle_invalid_binding():
    """Test handling of invalid bindings."""
    manager = ErrorRecoveryManager()
    result = manager.handle_invalid_binding("invalid", 1)

    assert isinstance(result, KeyMapping)
    assert result.key == "unknown"

    errors = manager.get_error_summary()
    assert errors["total_errors"] == 1
    assert errors["error_types"] == {"invalid_binding": 1}
    assert errors["errors"][0]["type"] == "invalid_binding"
    assert errors["errors"][0]["line"] == "invalid"
    assert errors["errors"][0]["line_number"] == 1


def test_handle_invalid_layer():
    """Test handling of invalid layers."""
    manager = ErrorRecoveryManager()
    result = manager.handle_invalid_layer("content", "test", 1)

    assert isinstance(result, Layer)
    assert result.name == "test"
    assert result.bindings == []

    errors = manager.get_error_summary()
    assert errors["total_errors"] == 1
    assert errors["error_types"] == {"invalid_layer": 1}
    assert errors["errors"][0]["type"] == "invalid_layer"
    assert errors["errors"][0]["content"] == "content"
    assert errors["errors"][0]["name"] == "test"
    assert errors["errors"][0]["line_number"] == 1


def test_multiple_errors():
    """Test handling multiple errors."""
    manager = ErrorRecoveryManager()
    manager.handle_invalid_binding("invalid1", 1)
    manager.handle_invalid_binding("invalid2", 2)
    manager.handle_invalid_layer("content", "test", 3)

    errors = manager.get_error_summary()
    assert errors["total_errors"] == 3
    assert errors["error_types"] == {
        "invalid_binding": 2,
        "invalid_layer": 1
    }
    assert len(errors["errors"]) == 3


def test_no_errors():
    """Test when no errors have occurred."""
    manager = ErrorRecoveryManager()

    errors = manager.get_error_summary()
    assert errors["total_errors"] == 0
    assert errors["error_types"] == {}
    assert errors["errors"] == []
    assert not manager.has_errors()


def test_has_errors():
    """Test error detection."""
    manager = ErrorRecoveryManager()
    assert not manager.has_errors()

    manager.handle_invalid_binding("invalid", 1)
    assert manager.has_errors()


def test_error_summary_structure():
    """Test error summary structure."""
    manager = ErrorRecoveryManager()
    manager.handle_invalid_binding("invalid", 1)

    summary = manager.get_error_summary()
    assert set(summary.keys()) == {
        "errors",
        "total_errors",
        "error_types"
    }
    assert isinstance(summary["errors"], list)
    assert isinstance(summary["total_errors"], int)
    assert isinstance(summary["error_types"], dict)
