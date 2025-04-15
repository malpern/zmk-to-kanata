#!/usr/bin/env python
"""Patch the GlobalSettings class to handle no-arg initialization."""

# Import the original GlobalSettings class
from converter.model.keymap_model import GlobalSettings

# Store the original class
OriginalGlobalSettings = GlobalSettings


# Create a new class that handles no-arg init
class PatchedGlobalSettings:
    def __new__(cls, tap_time=200, hold_time=250):
        # Use the original class with default values
        return OriginalGlobalSettings(tap_time=tap_time, hold_time=hold_time)


# Patch the module
import converter.model.keymap_model

converter.model.keymap_model.GlobalSettings = PatchedGlobalSettings

print("GlobalSettings patched successfully. You can now run the converter.")
