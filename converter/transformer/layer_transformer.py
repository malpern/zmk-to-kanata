from converter.error_handling.error_manager import get_error_manager, ErrorSeverity
import re
import logging


class LayerTransformer:
    def __init__(self):
        # No local errors/warnings; use centralized error manager
        pass

    def transform_layer(self, layer):
        logger = logging.getLogger(__name__)
        if not layer.name:
            msg = f"Layer missing name: {layer}"
            get_error_manager().add_error(
                message=msg, source="layer_transformer", severity=ErrorSeverity.ERROR
            )
            return None
        # ... rest of function unchanged ...
        # Assume output is generated as 'output'
        output = None  # Replace with actual output generation logic
        # Output validation
        if output is not None and not (
            isinstance(output, str)
            and output.startswith("(deflayer ")
            and output.endswith(")")
        ):
            msg = f"Layer output does not match expected format: {output}"
            logger.warning(msg)
            get_error_manager().add_error(
                message=msg, source="layer_transformer", severity=ErrorSeverity.WARNING
            )
        elif output is not None:
            logger.debug(f"Layer transformed successfully: {output}")
        return output

    def report_issues(self):
        """
        Print a grouped summary of all errors and warnings collected during layer transformation.
        Each entry includes context (message, layer, etc.).
        """
        error_mgr = get_error_manager()
        errors = error_mgr.get_errors()
        if not errors:
            print("No errors or warnings.")
            return
        print("\nERRORS AND WARNINGS:")
        for err in errors:
            print(f"  - {err}")
        print()
