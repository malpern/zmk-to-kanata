import logging
from abc import ABC, abstractmethod

from converter.error_recovery import ErrorRecoveryManager
from converter.parser.parser_error import ParserError


class ParserBase(ABC):
    """
    Abstract base class for all ZMK to Kanata parsers.
    Provides standard interface, error handling, and logging.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_manager = ErrorRecoveryManager()

    @abstractmethod
    def parse(self, *args, **kwargs):
        """
        Parse input and return the parsed representation.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("parse() must be implemented by subclasses.")

    def parse_binding(self, *args, **kwargs):
        """
        Optionally parse a single binding. Subclasses may override.
        """
        raise NotImplementedError(
            "parse_binding() not implemented for this parser."
        )

    def parse_layer(self, *args, **kwargs):
        """
        Optionally parse a single layer. Subclasses may override.
        """
        raise NotImplementedError(
            "parse_layer() not implemented for this parser."
        )

    def get_error_summary(self):
        """
        Return a summary of errors encountered during parsing.
        """
        return self.error_manager.get_error_summary()

    def has_errors(self):
        """
        Return True if any errors were encountered during parsing.
        """
        return self.error_manager.has_errors()


# Re-export ParserError for legacy imports
__all__ = ["ParserBase", "ParserError"]
