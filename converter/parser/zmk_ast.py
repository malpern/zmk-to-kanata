# -*- coding: utf-8 -*-
"""
ZMK AST data structures for macro parsing and transformation.
Implements ZMKMacroDefinition, ZMKMacroStep, ZMKDocument, ZMKBinding, ZMKMacrosBlock as per the new architecture.
"""
from dataclasses import dataclass, field
from typing import Any, List, Optional

# TODO: Import the centralized error manager when available
# from converter.error_handling import get_error_manager


@dataclass
class ZMKMacroStep:
    """Represents a single step in a ZMK macro."""

    action: str
    params: List[Any] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.action, str):
            # TODO: Log error via error manager
            raise TypeError("action must be a string")
        if not isinstance(self.params, list):
            # TODO: Log error via error manager
            raise TypeError("params must be a list")


@dataclass
class ZMKMacroDefinition:
    """Represents a macro definition in ZMK."""

    name: str
    steps: List[ZMKMacroStep] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str):
            # TODO: Log error via error manager
            raise TypeError("name must be a string")
        if not isinstance(self.steps, list):
            # TODO: Log error via error manager
            raise TypeError("steps must be a list of ZMKMacroStep")
        for step in self.steps:
            if not isinstance(step, ZMKMacroStep):
                # TODO: Log error via error manager
                raise TypeError("Each step must be a ZMKMacroStep")


@dataclass
class ZMKBinding:
    """Represents a binding in a ZMK macro or keymap."""

    binding_type: str
    value: Any

    def __post_init__(self):
        if not isinstance(self.binding_type, str):
            # TODO: Log error via error manager
            raise TypeError("binding_type must be a string")


@dataclass
class ZMKMacrosBlock:
    """Represents a block of macro definitions in ZMK."""

    macros: List[ZMKMacroDefinition] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.macros, list):
            # TODO: Log error via error manager
            raise TypeError("macros must be a list of ZMKMacroDefinition")
        for macro in self.macros:
            if not isinstance(macro, ZMKMacroDefinition):
                # TODO: Log error via error manager
                raise TypeError("Each macro must be a ZMKMacroDefinition")


@dataclass
class ZMKDocument:
    """Represents a full ZMK document (keymap, macros, etc.)."""

    macros_block: Optional[ZMKMacrosBlock] = None
    # Add other top-level fields as needed

    def __post_init__(self):
        if self.macros_block is not None and not isinstance(
            self.macros_block, ZMKMacrosBlock
        ):
            # TODO: Log error via error manager
            raise TypeError("macros_block must be a ZMKMacrosBlock or None")


# TODO: Integrate with centralized error manager for logging and validation
# TODO: Add any additional methods or integration points as required by the new architecture
