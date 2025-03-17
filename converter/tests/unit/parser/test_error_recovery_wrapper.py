"""Tests for the error recovery wrapper."""

from unittest.mock import Mock, patch

from converter.parser.error_recovery_wrapper import ParserErrorRecoveryWrapper
from converter.parser.parser_base import ParserError
from converter.model.keymap_model import Layer, KeyMapping


def test_parse_success():
    """Test successful parsing."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser
    mock_parser.parse.return_value = {"layers": []}

    wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
    result = wrapper.parse("content")

    assert result == {"layers": []}
    mock_parser.parse.assert_called_once_with("content")


def test_parse_parser_error():
    """Test handling of parser errors."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser
    mock_parser.parse.side_effect = ParserError("Test error")

    wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
    result = wrapper.parse("content")

    assert result == {
        "layers": [],
        "error": "Test error",
        "recovered": False
    }


def test_parse_binding_success():
    """Test successful binding parsing."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser
    mock_binding = KeyMapping("test")
    mock_parser.parse_binding.return_value = mock_binding

    wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
    result = wrapper.parse_binding("&kp A", 1)

    assert result == mock_binding
    mock_parser.parse_binding.assert_called_once_with("&kp A")


def test_parse_binding_value_error():
    """Test handling of invalid bindings."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser
    mock_parser.parse_binding.side_effect = ValueError("Invalid binding")

    with patch(
        "converter.error_recovery.ErrorRecoveryManager"
    ) as mock_manager:
        mock_manager.return_value.handle_invalid_binding.return_value = None
        wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
        result = wrapper.parse_binding("invalid", 1)

        assert result is None
        mock_manager.return_value.handle_invalid_binding.\
            assert_called_once_with("invalid", 1)


def test_parse_layer_success():
    """Test successful layer parsing."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser
    mock_layer = Layer("test", [])
    mock_parser.parse_layer.return_value = mock_layer

    wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
    result = wrapper.parse_layer("content", "test", 1)

    assert result == mock_layer
    mock_parser.parse_layer.assert_called_once_with("content", "test")


def test_parse_layer_value_error():
    """Test handling of invalid layers."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser
    mock_parser.parse_layer.side_effect = ValueError("Invalid layer")

    with patch(
        "converter.error_recovery.ErrorRecoveryManager"
    ) as mock_manager:
        mock_manager.return_value.handle_invalid_layer.return_value = None
        wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
        result = wrapper.parse_layer("content", "test", 1)

        assert result is None
        mock_manager.return_value.handle_invalid_layer.\
            assert_called_once_with("content", "test", 1)


def test_error_summary():
    """Test getting error summary."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser

    with patch(
        "converter.error_recovery.ErrorRecoveryManager"
    ) as mock_manager:
        mock_manager.return_value.get_error_summary.return_value = {
            "errors": []
        }
        wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
        result = wrapper.get_error_summary()

        assert result == {"errors": []}
        mock_manager.return_value.get_error_summary.assert_called_once()


def test_has_errors():
    """Test checking for errors."""
    mock_parser_class = Mock()
    mock_parser = Mock()
    mock_parser_class.return_value = mock_parser

    with patch(
        "converter.error_recovery.ErrorRecoveryManager"
    ) as mock_manager:
        mock_manager.return_value.has_errors.return_value = False
        wrapper = ParserErrorRecoveryWrapper(mock_parser_class)
        result = wrapper.has_errors()

        assert result is False
        mock_manager.return_value.has_errors.assert_called_once()
