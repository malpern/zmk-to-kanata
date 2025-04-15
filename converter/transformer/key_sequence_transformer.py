"""Module for transforming ZMK key-sequence behaviors to Kanata format."""

import logging
import re
from typing import List

from converter.error_handling.error_manager import get_error_manager, ErrorSeverity


class KeySequenceTransformer:
    """
    Transformer for ZMK key-sequence behaviors to Kanata format.

    Expected output format:
    (tap-dance <timeout_ms> <key1> <key2> ... <keyn>)

    Where:
    - timeout_ms: The timeout in milliseconds
    - key1, key2, ..., keyn: The keys in the sequence
    """

    def __init__(self, timeout_ms=200):
        """
        Initialize the transformer.

        Args:
            timeout_ms: The timeout in milliseconds for the tap-dance behavior
        """
        self.timeout_ms = timeout_ms
        self.logger = logging.getLogger(__name__)

    def transform_binding(self, binding) -> str:
        """
        Transform a key-sequence binding to Kanata format.

        Args:
            binding: The key-sequence binding to transform

        Returns:
            The Kanata tap-dance expression
        """
        # Validate binding
        if not hasattr(binding, "keys") or not binding.keys:
            msg = "Invalid key-sequence binding: missing keys"
            self.logger.error(msg)
            get_error_manager().add_error(
                message=msg,
                source="key_sequence_transformer",
                severity=ErrorSeverity.ERROR,
            )
            return "(tap-dance <invalid>)"

        # Transform keys to lowercase
        keys = [key.lower() for key in binding.keys]

        # Create the Kanata expression
        result = f"(tap-dance {self.timeout_ms} {' '.join(keys)})"
        self.logger.debug(f"Key-sequence transformed: {result}")

        # Validate output format
        if not re.match(r"\(tap-dance \d+ (\S+ )*\S+\)", result):
            msg = f"Key-sequence output does not match expected format: {result}"
            self.logger.warning(msg)
            get_error_manager().add_error(
                message=msg,
                source="key_sequence_transformer",
                severity=ErrorSeverity.WARNING,
            )

        return result

    def report_issues(self):
        """
        Print a summary of all errors and warnings collected during key-sequence transformation.
        """
        error_mgr = get_error_manager()
        errors = error_mgr.get_errors()
        if not errors:
            print("No errors or warnings in key-sequence transformation.")
            return
        print("\nKEY-SEQUENCE TRANSFORMATION ISSUES:")
        for err in errors:
            if err.source == "key_sequence_transformer":
                print(f"  - {err}")
        print()
