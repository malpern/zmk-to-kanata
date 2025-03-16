"""Data models for keyboard mapping.

TODO(tech-debt): This file duplicates functionality with model/keymap_model.py.
As a temporary solution, this file re-exports from the model directory version.
The model directory version is now the source of truth.

Future work:
1. Update all imports to use converter.model.keymap_model directly
2. Eventually remove this file

See plan.md Task 26 for full details.
"""

import warnings

# Re-export all symbols from model.keymap_model
from .model.keymap_model import (  # noqa: F401
    Binding,
    GlobalSettings,
    HoldTap,
    HoldTapBinding,
    KeyMapping,
    Layer,
    KeymapConfig,
)

# Define what symbols are available when using 'from keymap_model import *'
__all__ = [
    'Binding',
    'GlobalSettings',
    'HoldTap',
    'HoldTapBinding',
    'KeyMapping',
    'Layer',
    'KeymapConfig',
]

# Show deprecation warning when module is imported
warnings.warn(
    "Deprecated: Import from converter.model.keymap_model instead.",
    DeprecationWarning,
    stacklevel=2
) 