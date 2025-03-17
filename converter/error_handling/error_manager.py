"""Error management module for ZMK to Kanata converter.

This module provides centralized error handling for all components
of the ZMK to Kanata converter.
"""

import logging
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


@dataclass
class ConversionError:
    """Represents an error that occurred during conversion."""
    message: str
    source: str
    severity: ErrorSeverity
    line_number: Optional[int] = None
    column: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    traceback_info: Optional[str] = None

    def __str__(self) -> str:
        """Convert the error to a string representation."""
        location = ""
        if self.line_number is not None:
            location = f" at line {self.line_number}"
            if self.column is not None:
                location += f", column {self.column}"

        return (
            f"{self.severity.name}: [{self.source}]{location} - {self.message}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        return {
            "message": self.message,
            "source": self.source,
            "severity": self.severity.name,
            "line_number": self.line_number,
            "column": self.column,
            "context": self.context,
            "traceback": self.traceback_info
        }


class ErrorManager:
    """Centralized error manager for the ZMK to Kanata converter."""

    def __init__(self, verbose: bool = False):
        """Initialize the error manager.

        Args:
            verbose: Whether to log detailed error information
        """
        self.errors: List[ConversionError] = []
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Configure minimum severity level for raising exceptions
        self.raise_threshold = ErrorSeverity.ERROR

    def add_error(
        self,
        message: str,
        source: str,
        severity: ErrorSeverity,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        raise_immediately: bool = False
    ) -> None:
        """Add an error to the error manager.

        Args:
            message: The error message
            source: The source of the error (e.g., module name)
            severity: The severity of the error
            line_number: Optional line number where the error occurred
            column: Optional column where the error occurred
            context: Optional context dictionary with additional information
            exception: Optional exception object that caused the error
            raise_immediately: Whether to raise the error immediately

        Raises:
            Exception: If severity >= raise_threshold and raise_immediately
                is True
        """
        # Get traceback if exception is provided
        traceback_info = None
        if exception and self.verbose:
            traceback_info = "".join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))

        # Create error object
        error = ConversionError(
            message=message,
            source=source,
            severity=severity,
            line_number=line_number,
            column=column,
            context=context,
            traceback_info=traceback_info
        )

        # Add to the list of errors
        self.errors.append(error)

        # Log the error based on severity
        self._log_error(error)

        # Raise immediately if requested and severity is high enough
        if raise_immediately and severity.value >= self.raise_threshold.value:
            raise Exception(str(error))

    def _log_error(self, error: ConversionError) -> None:
        """Log an error based on its severity.

        Args:
            error: The error to log
        """
        message = str(error)

        if error.severity == ErrorSeverity.DEBUG:
            self.logger.debug(message)
        elif error.severity == ErrorSeverity.INFO:
            self.logger.info(message)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(message)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(message)
        elif error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(message)

    def has_errors(
        self, min_severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> bool:
        """Check if there are any errors with at least the specified severity.

        Args:
            min_severity: The minimum severity to check for

        Returns:
            True if there are errors with at least the specified severity
        """
        return any(
            error.severity.value >= min_severity.value for error in self.errors
        )

    def get_errors(
        self, min_severity: Optional[ErrorSeverity] = None
    ) -> List[ConversionError]:
        """Get all errors with at least the specified severity.

        Args:
            min_severity: The minimum severity to filter by

        Returns:
            List of errors with at least the specified severity
        """
        if min_severity is None:
            return self.errors

        return [
            error for error in self.errors
            if error.severity.value >= min_severity.value
        ]

    def get_error_report(
        self, min_severity: Optional[ErrorSeverity] = None
    ) -> Dict[str, Any]:
        """Generate a report of all errors.

        Args:
            min_severity: The minimum severity to include in the report

        Returns:
            Dictionary containing error statistics and error details
        """
        filtered_errors = self.get_errors(min_severity)

        # Count errors by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            count = sum(1 for e in filtered_errors if e.severity == severity)
            severity_counts[severity.name] = count

        # Group errors by source
        errors_by_source = {}
        for error in filtered_errors:
            if error.source not in errors_by_source:
                errors_by_source[error.source] = []
            errors_by_source[error.source].append(error.to_dict())

        return {
            "total_errors": len(filtered_errors),
            "severity_counts": severity_counts,
            "errors_by_source": errors_by_source
        }

    def clear(self) -> None:
        """Clear all errors."""
        self.errors = []

    def format_error_message(
        self,
        message: str,
        error_type: str,
        location: Optional[str] = None,
        suggestion: Optional[str] = None
    ) -> str:
        """Format an error message with consistent structure.

        Args:
            message: The base error message
            error_type: The type of error
            location: Optional location information
            suggestion: Optional suggestion for fixing the error

        Returns:
            Formatted error message
        """
        formatted = f"{error_type} Error: {message}"

        if location:
            formatted += f" (at {location})"

        if suggestion:
            formatted += f"\nSuggestion: {suggestion}"

        return formatted


# Global error manager instance
global_error_manager = ErrorManager()


def get_error_manager() -> ErrorManager:
    """Get the global error manager instance.

    Returns:
        The global error manager
    """
    return global_error_manager


def set_error_manager(manager: ErrorManager) -> None:
    """Set the global error manager instance.

    Args:
        manager: The error manager to set as global
    """
    global global_error_manager
    global_error_manager = manager
