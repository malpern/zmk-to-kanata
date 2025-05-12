"""Error handling module for DTS parsing and processing.

This module provides custom error classes and utilities for handling
errors that occur during DTS parsing and processing.
"""

from typing import Optional, Any


class DtsError(Exception):
    """Base class for DTS-related errors."""

    def __init__(
        self,
        message: str,
        file: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        context: Optional[str] = None,
        help_text: Optional[str] = None,
        node: Optional[Any] = None,
    ):
        """Initialize the error with detailed information.

        Args:
            message: The error message
            file: The file where the error occurred
            line: The line number where the error occurred
            column: The column number where the error occurred
            context: Additional context about the error
            help_text: Helpful text for fixing the error
            node: The DTS node where the error occurred (if applicable)
        """
        self.file = file
        self.line = line
        self.column = column
        self.context = context
        self.help_text = help_text
        self.node = node

        # Build the full error message
        full_message = message
        if file:
            full_message = f"{file}: {full_message}"
        if line:
            full_message = f"{full_message} at line {line}"
            if column:
                full_message = f"{full_message}, column {column}"

        if context:
            full_message = f"{full_message}\n\n{context}"
        if help_text:
            full_message = f"{full_message}\n\nHelp: {help_text}"

        super().__init__(full_message)


class DtsParseError(DtsError):
    """Error raised during DTS parsing."""

    def __init__(self, *args, **kwargs):
        """Initialize with parse-specific help text."""
        if "help_text" not in kwargs:
            kwargs["help_text"] = self._get_parse_help(kwargs.get("message", ""))
        super().__init__(*args, **kwargs)

    def _get_parse_help(self, message: str) -> str:
        """Get parse-specific help text based on the error message."""
        help_texts = {
            "unexpected token": (
                "Check for syntax errors like missing semicolons, "
                "unmatched braces, or invalid property values."
            ),
            "unterminated string": (
                "A string literal is missing its closing quote. "
                "Make sure all strings are properly terminated."
            ),
            "invalid property value": (
                "Property values must be strings, integers, arrays, "
                "or references. Check the value format."
            ),
            "duplicate node label": (
                "Node labels must be unique within a DTS file. "
                "Rename one of the duplicate labels."
            ),
            "invalid reference": (
                "Node references must point to existing labels. "
                "Check that the referenced label is defined."
            ),
        }

        for key, text in help_texts.items():
            if key.lower() in message.lower():
                return text

        return "Check the DTS syntax and ensure it follows the specification."


class DtsValidationError(DtsError):
    """Error raised during DTS validation."""

    def __init__(self, *args, **kwargs):
        """Initialize with validation-specific help text."""
        if "help_text" not in kwargs:
            kwargs["help_text"] = self._get_validation_help(kwargs.get("message", ""))
        super().__init__(*args, **kwargs)

    def _get_validation_help(self, message: str) -> str:
        """Get validation-specific help text based on the error message."""
        help_texts = {
            "missing required property": (
                "The node is missing a required property. "
                "Check the device binding documentation for required properties."
            ),
            "invalid property type": (
                "The property value has the wrong type. "
                "Check the device binding documentation for expected types."
            ),
            "incompatible node": (
                "The node's compatible string doesn't match any known binding. "
                "Check for typos and ensure the binding is available."
            ),
            "invalid binding cells": (
                "The number of binding cells doesn't match the specification. "
                "Check #binding-cells and the binding documentation."
            ),
        }

        for key, text in help_texts.items():
            if key.lower() in message.lower():
                return text

        return "Check that the DTS content matches the device binding requirements."


class DtsExtractError(DtsError):
    """Error raised during data extraction from DTS."""

    def __init__(self, *args, **kwargs):
        """Initialize with extraction-specific help text."""
        if "help_text" not in kwargs:
            kwargs["help_text"] = self._get_extraction_help(kwargs.get("message", ""))
        super().__init__(*args, **kwargs)

    def _get_extraction_help(self, message: str) -> str:
        """Get extraction-specific help text based on the error message."""
        help_texts = {
            "missing keymap node": (
                "Could not find a keymap node. "
                'Ensure there\'s a node with compatible = "zmk,keymap".'
            ),
            "invalid layer definition": (
                "Layer definition is invalid. "
                "Check that bindings are properly formatted arrays."
            ),
            "unknown behavior": (
                "Referenced an undefined behavior. "
                "Make sure all behaviors are defined before use."
            ),
            "invalid binding format": (
                "Binding format is incorrect. "
                "Check the ZMK documentation for proper binding syntax."
            ),
        }

        for key, text in help_texts.items():
            if key.lower() in message.lower():
                return text

        return "Check that the DTS content follows the ZMK keymap specification."


def format_error_context(
    content: str, line: int, column: int, context_lines: int = 2
) -> str:
    """Format error context with line numbers and pointer.

    Args:
        content: The file content
        line: The error line number (1-based)
        column: The error column number (1-based)
        context_lines: Number of lines to show before and after

    Returns:
        Formatted context string with line numbers and error pointer
    """
    lines = content.splitlines()
    start = max(0, line - context_lines - 1)
    end = min(len(lines), line + context_lines)

    # Calculate line number width
    width = len(str(end))

    # Build context string
    context = []
    for i in range(start, end):
        line_num = str(i + 1).rjust(width)
        if i == line - 1:  # Error line
            context.append(f"{line_num} | {lines[i]}")
            context.append(" " * width + " | " + " " * (column - 1) + "^")
        else:
            context.append(f"{line_num} | {lines[i]}")

    return "\n".join(context)
