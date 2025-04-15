"""Module for transforming ZMK sticky-key behaviors to Kanata format."""

import logging
import re

from converter.error_handling.error_manager import get_error_manager, ErrorSeverity


class StickyKeyTransformer:
    """
    Transformer for ZMK sticky-key behaviors to Kanata format.

    Expected output format:
    (sticky-key <key>)

    Where:
    - key: the key that should be "sticky"
    """

    def __init__(self):
        """Initialize the transformer."""
        self.logger = logging.getLogger(__name__)

    def transform_binding(self, binding) -> str:
        """
        Transform a sticky-key binding to Kanata format.

        Args:
            binding: The sticky-key binding to transform.

        Returns:
            The Kanata sticky-key expression.
        """
        # Validate binding
        if not hasattr(binding, "key") or not binding.key:
            msg = "Invalid sticky-key binding: missing key"
            self.logger.error(msg)
            get_error_manager().add_error(
                message=msg,
                source="sticky_key_transformer",
                severity=ErrorSeverity.ERROR,
            )
            return "(sticky-key <invalid>)"

        # Transform key to lowercase
        key = binding.key.lower()

        # Create the Kanata expression
        result = f"(sticky-key {key})"
        self.logger.debug(f"Sticky-key transformed: {result}")

        # Validate output format
        if not re.match(r"\(sticky-key \S+\)", result):
            msg = f"Sticky-key output does not match expected format: {result}"
            self.logger.warning(msg)
            get_error_manager().add_error(
                message=msg,
                source="sticky_key_transformer",
                severity=ErrorSeverity.WARNING,
            )

        return result

    def report_issues(self):
        """
        Print a summary of all errors and warnings collected during sticky-key transformation.
        """
        error_mgr = get_error_manager()
        errors = error_mgr.get_errors()
        if not errors:
            print("No errors or warnings in sticky-key transformation.")
            return
        print("\nSTICKY-KEY TRANSFORMATION ISSUES:")
        for err in errors:
            if err.source == "sticky_key_transformer":
                print(f"  - {err}")
        print()
