import logging
from typing import Any

from converter.behaviors.key_sequence import KeySequenceBinding
from converter.error_handling import ErrorSeverity, get_error_manager


class KeySequenceTransformer:
    """Transformer for ZMK key sequence behaviors to Kanata format."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_manager = get_error_manager()

    def transform_binding(self, binding: Any) -> str:
        """
        Transform a key sequence binding to Kanata S-expression.
        Args:
            binding: KeySequenceBinding or compatible object
        Returns:
            str: Kanata S-expression for the key sequence
        """
        # Accept KeySequenceBinding or compatible object
        if not hasattr(binding, "keys") or not isinstance(binding, KeySequenceBinding):
            self.error_manager.add_error(
                message=f"Invalid binding type for key sequence: {type(binding)}",
                source="key_sequence_transformer",
                severity=ErrorSeverity.ERROR,
            )
            self.logger.error(f"Invalid binding type: {type(binding)}")
            return "(chord)"

        # Validate keys
        if not binding.keys or not isinstance(binding.keys, list):
            self.error_manager.add_error(
                message="Key sequence binding has no keys or keys is not a list.",
                source="key_sequence_transformer",
                severity=ErrorSeverity.WARNING,
            )
            self.logger.warning(
                "Key sequence binding has no keys or keys is not a list."
            )
            return "(chord)"

        # Validate each key
        for k in binding.keys:
            if not isinstance(k, str) or not k.strip():
                self.error_manager.add_error(
                    message=f"Invalid key in key sequence: {k}",
                    source="key_sequence_transformer",
                    severity=ErrorSeverity.WARNING,
                )
                self.logger.warning(f"Invalid key in key sequence: {k}")

        # Use the data contract's to_kanata method for output
        try:
            expr = binding.to_kanata()
        except Exception as e:
            self.error_manager.add_error(
                message=f"Error converting key sequence to Kanata: {e}",
                source="key_sequence_transformer",
                severity=ErrorSeverity.ERROR,
                exception=e,
            )
            self.logger.error(f"Error converting key sequence to Kanata: {e}")
            expr = "(chord)"

        return expr
