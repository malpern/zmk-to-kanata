"""Error handling package for ZMK to Kanata converter."""

from converter.error_handling.error_manager import (
    ConversionError,
    ErrorManager,
    ErrorSeverity,
    get_error_manager,
    set_error_manager,
)

__all__ = [
    "ConversionError",
    "ErrorManager",
    "ErrorSeverity",
    "get_error_manager",
    "set_error_manager",
]
