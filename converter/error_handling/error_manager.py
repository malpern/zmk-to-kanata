"""Error handling module for the ZMK to Kanata converter."""

from enum import Enum
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class ErrorManager:
    """Manages error handling and reporting."""

    _instance: Optional["ErrorManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._errors: List[dict] = []
        return cls._instance

    def add_error(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[dict] = None,
    ) -> None:
        """Add an error to the error manager.

        Args:
            message: The error message
            severity: The severity level of the error
            context: Optional context information about the error
        """
        error = {
            "message": message,
            "severity": severity,
            "context": context or {},
        }
        self._errors.append(error)

        # Log the error
        if severity == ErrorSeverity.WARNING:
            logger.warning(message)
        elif severity == ErrorSeverity.ERROR:
            logger.error(message)
        else:
            logger.critical(message)

    def get_errors(self) -> List[dict]:
        """Get all errors.

        Returns:
            List of error dictionaries
        """
        return self._errors

    def clear(self) -> None:
        """Clear all errors."""
        self._errors = []

    def has_errors(self) -> bool:
        """Check if there are any errors.

        Returns:
            True if there are errors, False otherwise
        """
        return bool(self._errors)

    def get_error_summary(self) -> str:
        """Get a summary of all errors.

        Returns:
            A string containing all error messages
        """
        if not self._errors:
            return "No errors"

        summary = []
        for error in self._errors:
            severity = error["severity"].value.upper()
            message = error["message"]
            summary.append(f"{severity}: {message}")

        return "\n".join(summary)


def get_error_manager() -> ErrorManager:
    """Get the singleton error manager instance.

    Returns:
        The ErrorManager instance
    """
    return ErrorManager()
