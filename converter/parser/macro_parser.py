"""Parser module for ZMK macro behavior."""

from typing import Dict, List, Optional

from ..behaviors.macro import (
    MacroActivationMode,
    MacroBehavior,
    MacroBinding,
    is_macro_binding,
)


class MacroParser:
    """Parser for ZMK macro behavior and bindings."""

    def __init__(self):
        self.behaviors: Dict[str, MacroBehavior] = {}
        self.activation_mode = MacroActivationMode.TAP  # Default mode

    def parse_behavior(
        self,
        name: str,
        config: dict
    ) -> Optional[MacroBehavior]:
        """Parse a macro behavior configuration."""
        if config.get('compatible') in [
            'zmk,behavior-macro',
            'zmk,behavior-macro-one-param',
            'zmk,behavior-macro-two-param'
        ]:
            # Determine binding cells based on compatible value
            binding_cells = 0
            if config.get('compatible') == 'zmk,behavior-macro-one-param':
                binding_cells = 1
            elif config.get('compatible') == 'zmk,behavior-macro-two-param':
                binding_cells = 2

            # Parse wait-ms and tap-ms
            wait_ms = int(config.get('wait-ms', 15))
            tap_ms = int(config.get('tap-ms', 30))

            # Create the behavior (bindings will be parsed separately)
            behavior = MacroBehavior(
                name=name,
                wait_ms=wait_ms,
                tap_ms=tap_ms,
                binding_cells=binding_cells
            )
            
            self.behaviors[name] = behavior
            return behavior
        
        return None

    def parse_bindings(
        self,
        behavior: MacroBehavior,
        bindings_str: str
    ) -> None:
        """Parse the bindings list for a macro behavior."""
        # Split the bindings string into individual bindings
        bindings = []
        
        # Remove outer brackets and split by commas
        bindings_str = bindings_str.strip('<>').strip()
        binding_parts = bindings_str.split(',')
        
        for part in binding_parts:
            part = part.strip()
            if not part:
                continue
                
            # Check for macro control behaviors
            if '&macro_tap' in part:
                self.activation_mode = MacroActivationMode.TAP
                # Extract the behaviors after &macro_tap
                behaviors = self._extract_behaviors_after_control(
                    part, '&macro_tap'
                )
                bindings.extend(behaviors)
            elif '&macro_press' in part:
                self.activation_mode = MacroActivationMode.PRESS
                # Extract the behaviors after &macro_press
                behaviors = self._extract_behaviors_after_control(
                    part, '&macro_press'
                )
                bindings.extend(behaviors)
            elif '&macro_release' in part:
                self.activation_mode = MacroActivationMode.RELEASE
                # Extract the behaviors after &macro_release
                behaviors = self._extract_behaviors_after_control(
                    part, '&macro_release'
                )
                bindings.extend(behaviors)
            else:
                # Regular binding
                bindings.append(part)
        
        # Store the parsed bindings in the behavior
        behavior.bindings = bindings

    def _extract_behaviors_after_control(
        self,
        part: str,
        control: str
    ) -> List[str]:
        """Extract behaviors after a macro control behavior."""
        # Remove the control part
        behaviors_str = part.replace(control, '').strip()
        
        # Split by whitespace to get individual behaviors
        return [b.strip() for b in behaviors_str.split() if b.strip()]

    def parse_binding(self, binding_str: str) -> Optional[MacroBinding]:
        """Parse a macro binding string."""
        if not is_macro_binding(binding_str):
            return None

        try:
            return MacroBinding.from_zmk(binding_str, self.behaviors)
        except (ValueError, KeyError):
            # If we can't parse it as a macro binding, return None
            return None 