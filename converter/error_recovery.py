"""Error recovery module for handling conversion failures gracefully."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import logging

from converter.model.keymap_model import KeyMapping, Layer


@dataclass
class ConversionError:
    """Represents an error that occurred during conversion."""
    error_type: str
    message: str
    line_number: Optional[int] = None
    context: Dict = field(default_factory=dict)


class ErrorRecoveryManager:
    """Manages error recovery during keymap conversion."""

    def __init__(self):
        """Initialize the error recovery manager."""
        self.errors: List[ConversionError] = []
        self.recovery_actions = 0
        self.logger = logging.getLogger(__name__)

    def handle_invalid_key(
        self,
        key: str,
        line_number: Optional[int] = None
    ) -> KeyMapping:
        """Handle an invalid key by converting it to a safe fallback.

        Args:
            key: The invalid key
            line_number: Optional line number where the error occurred

        Returns:
            KeyMapping: A safe fallback key mapping
        """
        self.errors.append(ConversionError(
            error_type="invalid_key",
            message=f"Invalid key '{key}' converted to NONE",
            line_number=line_number,
            context={"original_key": key}
        ))
        self.recovery_actions += 1
        self.logger.warning(
            f"Line {line_number}: Invalid key '{key}' converted to NONE"
        )
        return KeyMapping(key="NONE")

    def handle_invalid_layer(
        self,
        content: str,
        name: str,
        line_number: Optional[int] = None
    ) -> Layer:
        """Handle an invalid layer by creating an empty layer.

        Args:
            content: The invalid layer content
            name: The layer name
            line_number: Optional line number where the error occurred

        Returns:
            Layer: An empty layer as fallback
        """
        self.errors.append(ConversionError(
            error_type="invalid_layer",
            message=f"Invalid layer '{name}' - created empty layer",
            line_number=line_number,
            context={"layer_name": name, "content": content}
        ))
        self.recovery_actions += 1
        self.logger.error(
            f"Line {line_number}: Invalid layer '{name}' - "
            "created empty layer"
        )
        return Layer(name=name, bindings=[])

    def handle_invalid_macro(
        self,
        macro_name: str,
        line_number: Optional[int] = None,
        context: Optional[Dict] = None
    ) -> KeyMapping:
        """Handle an invalid macro by converting to a safe fallback.

        Args:
            macro_name: The invalid macro name
            line_number: Optional line number where the error occurred
            context: Optional additional context about the error

        Returns:
            KeyMapping: A safe fallback key mapping
        """
        error_context = context or {}
        error_context["original_macro"] = macro_name

        self.errors.append(ConversionError(
            error_type="invalid_macro",
            message=f"Invalid macro '{macro_name}' converted to NONE",
            line_number=line_number,
            context=error_context
        ))
        self.recovery_actions += 1
        self.logger.warning(
            f"Line {line_number}: Invalid macro '{macro_name}' "
            "converted to NONE"
        )
        return KeyMapping(key="NONE")

    def handle_invalid_binding(
        self,
        binding_str: str,
        line_number: Optional[int] = None,
        context: Optional[Dict] = None
    ) -> KeyMapping:
        """Handle an invalid binding by converting to a safe fallback.

        Args:
            binding_str: The invalid binding string
            line_number: Optional line number where the error occurred
            context: Optional additional context about the error

        Returns:
            KeyMapping: A safe fallback key mapping
        """
        error_context = context or {}
        error_context["original_binding"] = binding_str

        # Determine error type based on context
        error_type = "invalid_binding"
        if "nested_error" in error_context:
            error_type = "invalid_nested_binding"
        elif "behavior_error" in error_context:
            error_type = "invalid_behavior"
        elif "param_error" in error_context:
            error_type = "invalid_parameter"

        self.errors.append(ConversionError(
            error_type=error_type,
            message=self._format_binding_error(binding_str, error_context),
            line_number=line_number,
            context=error_context
        ))
        self.recovery_actions += 1

        # Log with appropriate level and context
        if error_type == "invalid_nested_binding":
            self.logger.error(
                f"Line {line_number}: Invalid nested binding "
                f"'{binding_str}' - {error_context.get('nested_error', '')}"
            )
        else:
            msg = self._format_binding_error(binding_str, error_context)
            self.logger.warning(f"Line {line_number}: {msg}")

        return KeyMapping(key="unknown")

    def _format_binding_error(
        self,
        binding: str,
        context: Dict
    ) -> str:
        """Format a binding error message with context.

        Args:
            binding: The invalid binding
            context: Error context

        Returns:
            str: Formatted error message
        """
        if "nested_error" in context:
            return (
                f"Invalid nested binding '{binding}' - "
                f"{context['nested_error']}"
            )
        if "behavior_error" in context:
            return (
                f"Invalid behavior in binding '{binding}' - "
                f"{context['behavior_error']}"
            )
        if "param_error" in context:
            return (
                f"Invalid parameter in binding '{binding}' - "
                f"{context['param_error']}"
            )
        return f"Invalid binding '{binding}' converted to unknown"

    def handle_invalid_timing(
        self,
        timing_value: int,
        timing_type: str,
        line_number: Optional[int] = None
    ) -> int:
        """Handle invalid timing values by converting to safe defaults.

        Args:
            timing_value: The invalid timing value
            timing_type: The type of timing (wait/tap)
            line_number: Optional line number where the error occurred

        Returns:
            int: A safe fallback timing value
        """
        default_value = 200 if timing_type == "tap" else 100
        self.errors.append(ConversionError(
            error_type="invalid_timing",
            message=(
                f"Invalid {timing_type} time {timing_value}ms "
                f"converted to {default_value}ms"
            ),
            line_number=line_number,
            context={
                "original_value": timing_value,
                "timing_type": timing_type
            }
        ))
        self.recovery_actions += 1
        self.logger.warning(
            f"Line {line_number}: Invalid {timing_type} time {timing_value}ms "
            f"converted to {default_value}ms"
        )
        return default_value

    def handle_invalid_nested_behavior(
        self,
        outer: str,
        inner: str,
        line_number: Optional[int] = None
    ) -> KeyMapping:
        """Handle invalid nested behaviors by converting to a safe fallback.

        Args:
            outer: The outer behavior
            inner: The inner behavior
            line_number: Optional line number where the error occurred

        Returns:
            KeyMapping: A safe fallback key mapping
        """
        self.errors.append(ConversionError(
            error_type="invalid_nested_behavior",
            message=(
                f"Invalid nesting of '{inner}' inside '{outer}' "
                "converted to NONE"
            ),
            line_number=line_number,
            context={"outer": outer, "inner": inner}
        ))
        self.recovery_actions += 1
        self.logger.warning(
            f"Line {line_number}: Invalid nesting of '{inner}' inside "
            f"'{outer}' converted to NONE"
        )
        return KeyMapping(key="NONE")

    def handle_layer_parse_error(
        self,
        layer_name: str,
        error: Exception,
        line_number: Optional[int] = None
    ) -> Layer:
        """Handle layer parsing errors by creating an empty layer.

        Args:
            layer_name: The name of the layer that failed to parse
            error: The exception that occurred
            line_number: Optional line number where the error occurred

        Returns:
            Layer: An empty layer as fallback
        """
        self.errors.append(ConversionError(
            error_type="layer_parse_error",
            message=(
                f"Failed to parse layer '{layer_name}': {str(error)}. "
                "Created empty layer."
            ),
            line_number=line_number,
            context={"layer_name": layer_name, "error": str(error)}
        ))
        self.recovery_actions += 1
        self.logger.error(
            f"Line {line_number}: Failed to parse layer '{layer_name}': "
            f"{str(error)}. Created empty layer."
        )
        return Layer(layer_name, bindings=[])

    def get_error_summary(self) -> Dict:
        """Get a summary of all errors.

        Returns:
            Dict: Error summary with counts and details
        """
        error_types = {}
        for error in self.errors:
            error_types[error.error_type] = (
                error_types.get(error.error_type, 0) + 1
            )

        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "errors": [
                {
                    "type": e.error_type,
                    "message": e.message,
                    "line_number": e.line_number,
                    "context": e.context
                }
                for e in self.errors
            ]
        }

    def has_errors(self) -> bool:
        """Check if any errors occurred during conversion.

        Returns:
            bool: True if errors occurred, False otherwise
        """
        return len(self.errors) > 0
