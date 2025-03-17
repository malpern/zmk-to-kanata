"""Error recovery wrapper for parsers."""

from typing import Any, Dict, Optional, Type
import logging

from converter.error_recovery import ErrorRecoveryManager
from converter.model.keymap_model import Layer, KeyMapping
from converter.parser.parser_base import ParserError


class ParserErrorRecoveryWrapper:
    """Wrapper that adds error recovery to any parser."""

    def __init__(self, parser_class: Type[Any]):
        """Initialize the wrapper.

        Args:
            parser_class: The parser class to wrap
        """
        self.parser = parser_class()
        self.error_manager = ErrorRecoveryManager()
        self.logger = logging.getLogger(__name__)

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse content with error recovery.

        Args:
            content: The content to parse

        Returns:
            Dict[str, Any]: The parsed content
        """
        try:
            return self.parser.parse(content)
        except ParserError as e:
            self.logger.error(f"Parser error: {e}")
            # Create empty result with error info
            return {
                "layers": [],
                "error": str(e),
                "recovered": False
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                "layers": [],
                "error": str(e),
                "recovered": False
            }

    def parse_binding(
        self,
        line: str,
        line_number: Optional[int] = None
    ) -> Optional[KeyMapping]:
        """Parse a binding with error recovery.

        Args:
            line: The line to parse
            line_number: Optional line number for error reporting

        Returns:
            Optional[KeyMapping]: The parsed binding or None
        """
        try:
            return self.parser.parse_binding(line)
        except ValueError as e:
            self.logger.warning(
                f"Line {line_number}: Invalid binding: {e}"
            )
            return self.error_manager.handle_invalid_binding(
                line,
                line_number
            )
        except Exception as e:
            self.logger.error(
                f"Line {line_number}: Unexpected error parsing binding: {e}"
            )
            return self.error_manager.handle_invalid_binding(
                line,
                line_number
            )

    def parse_layer(
        self,
        content: str,
        name: str,
        line_number: Optional[int] = None
    ) -> Optional[Layer]:
        """Parse a layer with error recovery.

        Args:
            content: The layer content to parse
            name: The layer name
            line_number: Optional line number for error reporting

        Returns:
            Optional[Layer]: The parsed layer or None
        """
        try:
            return self.parser.parse_layer(content, name)
        except ValueError as e:
            self.logger.warning(
                f"Line {line_number}: Invalid layer {name}: {e}"
            )
            return self.error_manager.handle_invalid_layer(
                content,
                name,
                line_number
            )
        except Exception as e:
            msg = f"Line {line_number}: Unexpected error parsing layer "
            msg += f"{name}: {e}"
            self.logger.error(msg)
            return self.error_manager.handle_invalid_layer(
                content,
                name,
                line_number
            )

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors encountered during parsing.

        Returns:
            Dict[str, Any]: Error summary
        """
        return self.error_manager.get_error_summary()

    def has_errors(self) -> bool:
        """Check if any errors occurred during parsing.

        Returns:
            bool: True if errors occurred
        """
        return self.error_manager.has_errors()
