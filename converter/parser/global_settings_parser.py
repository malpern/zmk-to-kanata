"""Global settings parser module for ZMK keymaps."""

import logging
import re
from typing import Optional

from converter.model.keymap_model import GlobalSettings

logger = logging.getLogger(__name__)


class GlobalSettingsParser:
    """Parser for ZMK global settings."""

    def __init__(self):
        """Initialize the parser."""
        self.tap_time: Optional[int] = None
        self.hold_time: Optional[int] = None

    def parse_setting(self, line: str) -> None:
        """Parse a global setting line.

        Args:
            line: The line containing the setting.

        Raises:
            ValueError: If the setting is invalid or malformed.
        """
        line = line.strip()
        setting_match = re.match(r"^(\w+(?:-\w+)*)\s*=\s*<(\d+)>;$", line)

        if not setting_match:
            if "tap-time" in line:
                raise ValueError("Invalid tap-time setting")
            elif "hold-time" in line:
                raise ValueError("Invalid hold-time setting")
            else:
                raise ValueError(f"Invalid setting format: {line}")

        setting_name = setting_match.group(1)
        try:
            value = int(setting_match.group(2))
            if value <= 0:
                raise ValueError(
                    f"Invalid {setting_name} setting: value must be positive"
                )

            if setting_name == "tap-time":
                self.tap_time = value
            elif setting_name == "hold-time":
                self.hold_time = value
            else:
                raise ValueError(f"Unknown setting: {setting_name}")
        except ValueError as e:
            if "tap-time" in line:
                raise ValueError("Invalid tap-time setting") from e
            elif "hold-time" in line:
                raise ValueError("Invalid hold-time setting") from e
            else:
                raise e

    def finish(self) -> GlobalSettings:
        """Create a GlobalSettings object with the parsed values.

        Returns:
            A GlobalSettings object with the parsed values, using defaults
            for any unset values.
        """
        return GlobalSettings(
            tap_time=self.tap_time if self.tap_time is not None else 200,
            hold_time=self.hold_time if self.hold_time is not None else 250,
        )
