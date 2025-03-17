"""Parser for complex ZMK binding formats."""

from typing import Optional, List
from dataclasses import dataclass
import re

from converter.error_handling import (
    ErrorManager,
    ErrorSeverity,
    get_error_manager,
)
from converter.model.keymap_model import KeyMapping
from converter.validation.key_validator import validate_key
from converter.behaviors.holdtap import HoldTapBehavior
from converter.behaviors.layer import LayerBehavior
from converter.behaviors.macro import MacroBehavior
from converter.behaviors.sticky_key import StickyKeyBehavior
from converter.behaviors.key_sequence import KeySequenceBehavior
from converter.behaviors.homerow_mods import HomeRowModBehavior, is_homerow_mod_binding


@dataclass
class BindingComponent:
    """Component of a complex binding."""
    behavior: str
    params: List[str]


class BindingParseError(Exception):
    """Exception raised for binding parsing errors."""
    def __init__(self, message: str, binding: str):
        self.binding = binding
        super().__init__(message)


class BindingParser:
    """Parser for ZMK binding formats."""

    # Valid behavior patterns
    BEHAVIORS = {
        'kp': {'params': 1},    # Key press
        'lt': {'params': 2},    # Layer-tap
        'mt': {'params': 2},    # Mod-tap
        'sk': {'params': 1},    # Sticky key
        'mo': {'params': 1},    # Momentary layer
        'to': {'params': 1},    # To layer
        'tog': {'params': 1},   # Toggle layer
        'trans': {'params': 0}  # Transparent
    }

    def __init__(self, error_manager: Optional[ErrorManager] = None):
        """Initialize the binding parser.

        Args:
            error_manager: Optional error manager for reporting issues
        """
        self.nested_depth = 0
        self.max_nested_depth = 2
        self.error_manager = error_manager or get_error_manager()

    def parse(
        self,
        binding: str,
        line_number: Optional[int] = None
    ) -> KeyMapping:
        """Parse a ZMK binding into a KeyMapping.

        Args:
            binding: The binding string to parse
            line_number: Optional line number for error reporting

        Returns:
            A KeyMapping object representing the parsed binding

        Raises:
            BindingParseError: If the binding cannot be parsed
        """
        self.nested_depth = 0
        
        # Handle homerow mods
        if is_homerow_mod_binding(binding):
            return self._parse_homerow_mod(binding, line_number)
            
        # Handle nested bindings
        if binding.startswith("&"):
            return self._parse_nested_binding(binding, line_number)
            
        # Handle simple bindings
        return self._parse_simple_binding(binding, line_number)

    def _parse_nested_binding(
        self,
        binding: str,
        line_number: Optional[int] = None
    ) -> KeyMapping:
        """Parse a nested binding like 'mt(MOD_LCTL A)'.

        Args:
            binding: The binding string to parse
            line_number: Optional line number for error reporting

        Returns:
            KeyMapping representing the nested binding

        Raises:
            BindingParseError: If the nested binding format is invalid
        """
        self.nested_depth += 1
        if self.nested_depth > self.max_nested_depth:
            self._report_error(
                message=(
                    f"Exceeded maximum nesting depth of "
                    f"{self.max_nested_depth}"
                ),
                binding=binding,
                line_number=line_number,
                raise_immediately=True
            )

        try:
            # Extract behavior and parameters
            match = re.match(r'(\w+)\s*\((.*)\)', binding)
            if not match:
                self._report_error(
                    message="Invalid nested binding format",
                    binding=binding,
                    line_number=line_number,
                    raise_immediately=True
                )

            behavior, param_str = match.groups()

            # Handle recursive parsing of parameters
            params = []
            param_depth = 0
            current_param = ""

            for char in param_str:
                if char == '(' and param_depth == 0:
                    param_depth += 1
                    current_param += char
                elif char == ')' and param_depth == 1:
                    param_depth -= 1
                    current_param += char
                elif char == ')':
                    param_depth -= 1
                    current_param += char
                elif char == '(':
                    param_depth += 1
                    current_param += char
                elif char.isspace() and param_depth == 0 and current_param:
                    params.append(current_param.strip())
                    current_param = ""
                else:
                    current_param += char

            if current_param:
                params.append(current_param.strip())

            # Validate behavior and parameters
            self._validate_behavior(behavior, params, binding, line_number)

            # Process parameters recursively if needed
            processed_params = []
            for param in params:
                if '(' in param:
                    # Recursive parse for nested behaviors
                    processed_param = self._parse_nested_binding(
                        param, line_number
                    )
                    processed_params.append(processed_param)
                else:
                    processed_params.append(param)

            # Create KeyMapping based on behavior type
            if behavior == 'mt':  # Mod-tap
                if len(processed_params) != 2:
                    self._report_error(
                        message=(
                            f"Mod-tap requires 2 parameters, "
                            f"got {len(processed_params)}"
                        ),
                        binding=binding,
                        line_number=line_number,
                        raise_immediately=True
                    )
                mod, key = processed_params
                return KeyMapping(key=key, modifiers=[mod])

            # Default for other behaviors
            return KeyMapping(
                key=f"{behavior}({','.join(str(p) for p in processed_params)})"
            )

        finally:
            self.nested_depth -= 1

    def _parse_simple_binding(
        self,
        binding: str,
        line_number: Optional[int] = None
    ) -> KeyMapping:
        """Parse a simple binding like 'kp A'.

        Args:
            binding: The binding string to parse
            line_number: Optional line number for error reporting

        Returns:
            KeyMapping representing the simple binding

        Raises:
            BindingParseError: If the binding format is invalid
        """
        parts = binding.split()

        if not parts:
            self._report_error(
                message="Empty binding parts",
                binding=binding,
                line_number=line_number,
                raise_immediately=True
            )

        behavior = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        # Validate the behavior and parameters
        self._validate_behavior(behavior, params, binding, line_number)

        # Handle different behavior types
        if behavior == 'kp':  # Key press
            if not params:
                self._report_error(
                    message="Key press requires a key parameter",
                    binding=binding,
                    line_number=line_number,
                    raise_immediately=True
                )
            key = params[0]
            try:
                validate_key(key)
                return KeyMapping(key=key)
            except Exception as e:
                self._report_error(
                    message=f"Invalid key '{key}': {e}",
                    binding=binding,
                    line_number=line_number,
                    raise_immediately=True
                )

        if behavior in ['mo', 'to', 'tog']:  # Layer behaviors
            if not params:
                self._report_error(
                    message=(
                        f"Layer behavior '{behavior}' requires "
                        f"a layer parameter"
                    ),
                    binding=binding,
                    line_number=line_number,
                    raise_immediately=True
                )
            return KeyMapping(key=f"{behavior}({params[0]})")

        if behavior == 'trans':  # Transparent
            return KeyMapping(key="trans")

        # Default case
        return KeyMapping(
            key=f"{behavior}({','.join(params) if params else ''})"
        )

    def _validate_behavior(
        self,
        behavior: str,
        params: List[str],
        binding: str,
        line_number: Optional[int] = None
    ) -> None:
        """Validate a behavior and its parameters.

        Args:
            behavior: The behavior to validate
            params: List of parameters
            binding: The original binding string (for error reporting)
            line_number: Optional line number for error reporting

        Raises:
            BindingParseError: If the behavior or parameters are invalid
        """
        if behavior not in self.BEHAVIORS:
            self._report_error(
                message=f"Unknown behavior '{behavior}'",
                binding=binding,
                line_number=line_number,
                raise_immediately=True
            )

        expected_params = self.BEHAVIORS[behavior]['params']
        if len(params) != expected_params:
            self._report_error(
                message=(
                    f"Behavior '{behavior}' expects {expected_params} "
                    f"parameters, got {len(params)}"
                ),
                binding=binding,
                line_number=line_number,
                raise_immediately=True
            )

    def _report_error(
        self,
        message: str,
        binding: str,
        line_number: Optional[int] = None,
        raise_immediately: bool = False
    ) -> None:
        """Report a binding parse error using the error manager.

        Args:
            message: Error message
            binding: The binding string that caused the error
            line_number: Optional line number where the error occurred
            raise_immediately: Whether to raise the error immediately

        Raises:
            BindingParseError: If raise_immediately is True
        """
        context = {"binding": binding}

        self.error_manager.add_error(
            message=message,
            source="binding_parser",
            severity=ErrorSeverity.ERROR,
            line_number=line_number,
            context=context,
            raise_immediately=raise_immediately
        )

        if raise_immediately:
            raise BindingParseError(message, binding)

    def _parse_homerow_mod(self, binding: str, line_number: Optional[int] = None) -> KeyMapping:
        """Parse a homerow mod binding.
        
        Args:
            binding: The binding string to parse
            line_number: Optional line number for error reporting
            
        Returns:
            A KeyMapping object representing the parsed binding
            
        Raises:
            BindingParseError: If the binding cannot be parsed
        """
        parts = binding.split(maxsplit=2)
        if len(parts) != 3:
            self._report_error(
                message=f"Invalid homerow mod format: {binding}",
                binding=binding,
                line_number=line_number,
                raise_immediately=True
            )
            
        _, mod, key = parts
        
        # Create a homerow mod behavior
        behavior = HomeRowModBehavior(mod=mod, key=key)
        
        # Create a key mapping with the homerow mod behavior
        return KeyMapping(key=key, homerow_mod=behavior)
