"""Keymap Model Module

This module contains the intermediate representation classes for our keymap
converter.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class GlobalSettings:
    """Global settings for the keymap."""
    tap_time: int
    hold_time: int


@dataclass
class KeyMapping:
    """Represents a single key mapping."""
    key: str

    def __eq__(self, other):
        if not isinstance(other, KeyMapping):
            return False
        return self.key == other.key


@dataclass
class Layer:
    """Represents a layer of key mappings."""
    name: str
    keys: List[List[KeyMapping]]


@dataclass
class KeymapConfig:
    """Top-level configuration containing all keymap data."""
    global_settings: GlobalSettings
    layers: List[Layer]