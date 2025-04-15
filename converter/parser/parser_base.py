# NOTE: This file was previously archived as junk. Review for compliance with the new architecture and redundancy before further use.

"""Base parser module for ZMK configuration parsing.

This module provides the base class for all parsers in the ZMK to Kanata converter.
"""

from abc import ABC, abstractmethod


class ParserBase(ABC):
    """Base class for all parsers in the ZMK to Kanata converter."""
    
    @abstractmethod
    def parse(self, content: str) -> dict:
        """Parse the content and return a dictionary of parsed data.
        
        Args:
            content: The content to parse
            
        Returns:
            A dictionary of parsed data
        """
        pass 