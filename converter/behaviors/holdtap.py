# NOTE: This file was previously archived as junk. Review for compliance with the new architecture and redundancy before further use.

"""Module for handling hold-tap behaviors in ZMK.

This is a compatibility module that re-exports from hold_tap.
"""

from converter.behaviors.hold_tap import HoldTapBinding


class HoldTapBehavior(HoldTapBinding):
    """Compatibility alias for HoldTapBinding."""
    pass 