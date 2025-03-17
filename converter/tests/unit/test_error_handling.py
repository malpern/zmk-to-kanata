"""Unit tests for the error handling module."""

import pytest
from unittest.mock import patch, MagicMock

from converter.error_handling import (
    ConversionError,
    ErrorManager,
    ErrorSeverity,
    get_error_manager,
    set_error_manager,
)


def test_error_severity_order():
    """Test that error severity levels are correctly ordered."""
    assert ErrorSeverity.DEBUG.value < ErrorSeverity.INFO.value
    assert ErrorSeverity.INFO.value < ErrorSeverity.WARNING.value
    assert ErrorSeverity.WARNING.value < ErrorSeverity.ERROR.value
    assert ErrorSeverity.ERROR.value < ErrorSeverity.CRITICAL.value


def test_conversion_error_str():
    """Test string representation of ConversionError."""
    # Error with only required fields
    error = ConversionError(
        message="Test error message",
        source="test_module",
        severity=ErrorSeverity.ERROR
    )
    assert str(error) == "ERROR: [test_module] - Test error message"

    # Error with line number
    error_with_line = ConversionError(
        message="Test error with line",
        source="test_module",
        severity=ErrorSeverity.WARNING,
        line_number=42
    )
    expected_line_error = (
        "WARNING: [test_module] at line 42 - Test error with line"
    )
    assert str(error_with_line) == expected_line_error

    # Error with line and column
    error_with_loc = ConversionError(
        message="Test error with location",
        source="test_module",
        severity=ErrorSeverity.ERROR,
        line_number=10,
        column=5
    )
    expected_loc_error = (
        "ERROR: [test_module] at line 10, column 5 - Test error with location"
    )
    assert str(error_with_loc) == expected_loc_error


def test_conversion_error_to_dict():
    """Test conversion of ConversionError to dictionary."""
    error = ConversionError(
        message="Test error",
        source="test_module",
        severity=ErrorSeverity.ERROR,
        line_number=42,
        column=5,
        context={"file": "test.zmk"},
        traceback_info="Traceback info"
    )

    error_dict = error.to_dict()
    assert error_dict["message"] == "Test error"
    assert error_dict["source"] == "test_module"
    assert error_dict["severity"] == "ERROR"
    assert error_dict["line_number"] == 42
    assert error_dict["column"] == 5
    assert error_dict["context"] == {"file": "test.zmk"}
    assert error_dict["traceback"] == "Traceback info"


def test_error_manager_add_error():
    """Test adding errors to ErrorManager."""
    manager = ErrorManager()

    # Add errors with different severities
    manager.add_error(
        message="Debug message",
        source="test",
        severity=ErrorSeverity.DEBUG
    )

    manager.add_error(
        message="Info message",
        source="test",
        severity=ErrorSeverity.INFO
    )

    manager.add_error(
        message="Warning message",
        source="test",
        severity=ErrorSeverity.WARNING
    )

    # Verify errors were added
    assert len(manager.errors) == 3
    assert manager.errors[0].message == "Debug message"
    assert manager.errors[1].message == "Info message"
    assert manager.errors[2].message == "Warning message"


def test_error_manager_has_errors():
    """Test checking for errors by severity."""
    manager = ErrorManager()

    # Add errors with different severities
    manager.add_error(
        message="Debug message",
        source="test",
        severity=ErrorSeverity.DEBUG
    )

    manager.add_error(
        message="Warning message",
        source="test",
        severity=ErrorSeverity.WARNING
    )

    # Check error presence by severity
    assert manager.has_errors(ErrorSeverity.DEBUG)
    assert manager.has_errors(ErrorSeverity.WARNING)
    # No errors at this level
    assert not manager.has_errors(ErrorSeverity.ERROR)


def test_error_manager_get_errors():
    """Test getting errors filtered by severity."""
    manager = ErrorManager()

    # Add errors with different severities
    manager.add_error(
        message="Debug message",
        source="test",
        severity=ErrorSeverity.DEBUG
    )

    manager.add_error(
        message="Info message",
        source="test",
        severity=ErrorSeverity.INFO
    )

    manager.add_error(
        message="Warning message",
        source="test",
        severity=ErrorSeverity.WARNING
    )

    manager.add_error(
        message="Error message",
        source="test",
        severity=ErrorSeverity.ERROR
    )

    # Get errors with different severity filters
    all_errors = manager.get_errors()
    assert len(all_errors) == 4

    warnings_up = manager.get_errors(ErrorSeverity.WARNING)
    assert len(warnings_up) == 2
    # Check that all errors have at least WARNING severity
    has_min_severity = all(
        e.severity.value >= ErrorSeverity.WARNING.value
        for e in warnings_up
    )
    assert has_min_severity

    errors_only = manager.get_errors(ErrorSeverity.ERROR)
    assert len(errors_only) == 1
    assert errors_only[0].message == "Error message"


def test_error_manager_clear():
    """Test clearing errors."""
    manager = ErrorManager()

    # Add some errors
    manager.add_error(
        message="Test error",
        source="test",
        severity=ErrorSeverity.ERROR
    )

    assert len(manager.errors) == 1

    # Clear errors
    manager.clear()

    assert len(manager.errors) == 0


def test_error_manager_get_error_report():
    """Test generating error reports."""
    manager = ErrorManager()

    # Add errors from different sources
    manager.add_error(
        message="Parser error 1",
        source="parser",
        severity=ErrorSeverity.ERROR
    )

    manager.add_error(
        message="Parser error 2",
        source="parser",
        severity=ErrorSeverity.ERROR
    )

    manager.add_error(
        message="Validator warning",
        source="validator",
        severity=ErrorSeverity.WARNING
    )

    # Generate report
    report = manager.get_error_report()

    assert report["total_errors"] == 3
    assert report["severity_counts"]["ERROR"] == 2
    assert report["severity_counts"]["WARNING"] == 1
    assert len(report["errors_by_source"]["parser"]) == 2
    assert len(report["errors_by_source"]["validator"]) == 1

    # Filter report by severity
    error_report = manager.get_error_report(ErrorSeverity.ERROR)
    assert error_report["total_errors"] == 2
    assert error_report["severity_counts"]["ERROR"] == 2
    assert "validator" not in error_report["errors_by_source"]


def test_error_manager_format_error_message():
    """Test formatting error messages."""
    manager = ErrorManager()

    # Basic message
    basic = manager.format_error_message(
        message="Invalid key",
        error_type="Syntax"
    )
    assert basic == "Syntax Error: Invalid key"

    # Message with location
    with_location = manager.format_error_message(
        message="Missing semicolon",
        error_type="Syntax",
        location="line 42"
    )
    assert with_location == "Syntax Error: Missing semicolon (at line 42)"

    # Message with suggestion
    with_suggestion = manager.format_error_message(
        message="Unknown binding",
        error_type="Binding",
        location="line 10",
        suggestion="Check for typos in the binding name"
    )
    expected = (
        "Binding Error: Unknown binding (at line 10)\n"
        "Suggestion: Check for typos in the binding name"
    )
    assert with_suggestion == expected


@patch('logging.Logger')
def test_error_manager_log_error(mock_logger):
    """Test that errors are logged correctly based on severity."""
    # Create a mock logger
    mock_logger_instance = MagicMock()

    # Create error manager with the mock logger
    manager = ErrorManager()
    manager.logger = mock_logger_instance

    # Create errors of different severities
    debug_error = ConversionError(
        message="Debug message",
        source="test",
        severity=ErrorSeverity.DEBUG
    )

    info_error = ConversionError(
        message="Info message",
        source="test",
        severity=ErrorSeverity.INFO
    )

    warning_error = ConversionError(
        message="Warning message",
        source="test",
        severity=ErrorSeverity.WARNING
    )

    error_error = ConversionError(
        message="Error message",
        source="test",
        severity=ErrorSeverity.ERROR
    )

    critical_error = ConversionError(
        message="Critical message",
        source="test",
        severity=ErrorSeverity.CRITICAL
    )

    # Log the errors
    manager._log_error(debug_error)
    manager._log_error(info_error)
    manager._log_error(warning_error)
    manager._log_error(error_error)
    manager._log_error(critical_error)

    # Verify that the correct logging methods were called
    mock_logger_instance.debug.assert_called_once()
    mock_logger_instance.info.assert_called_once()
    mock_logger_instance.warning.assert_called_once()
    mock_logger_instance.error.assert_called_once()
    mock_logger_instance.critical.assert_called_once()


def test_global_error_manager():
    """Test the global error manager functions."""
    # Get the default global error manager
    default_manager = get_error_manager()
    assert isinstance(default_manager, ErrorManager)

    # Create a new manager
    new_manager = ErrorManager(verbose=True)

    # Set as global manager
    set_error_manager(new_manager)

    # Verify it was set
    assert get_error_manager() is new_manager
    assert get_error_manager() is not default_manager


def test_error_manager_raise_immediately():
    """Test that errors can be raised immediately when needed."""
    manager = ErrorManager()

    # Add an error with raise_immediately=True
    with pytest.raises(Exception) as excinfo:
        manager.add_error(
            message="Critical failure",
            source="test",
            severity=ErrorSeverity.ERROR,
            raise_immediately=True
        )

    assert "Critical failure" in str(excinfo.value)

    # Add a low-severity error with raise_immediately=True (shouldn't raise)
    try:
        manager.add_error(
            message="Debug info",
            source="test",
            severity=ErrorSeverity.DEBUG,
            raise_immediately=True
        )
    except Exception:
        pytest.fail("Low severity error should not raise an exception")


def test_error_manager_with_exception():
    """Test adding an error with an exception object."""
    manager = ErrorManager(verbose=True)

    try:
        # Cause an exception
        1 / 0
    except Exception as e:
        # Add the error with the exception
        manager.add_error(
            message="Division error",
            source="test",
            severity=ErrorSeverity.ERROR,
            exception=e
        )

    # Check that the error was added with traceback info
    assert len(manager.errors) == 1
    assert manager.errors[0].message == "Division error"
    assert manager.errors[0].traceback_info is not None
    assert "ZeroDivisionError" in manager.errors[0].traceback_info
