from dataclasses import dataclass
from typing import Optional


@dataclass
class MacroBinding:
    """A binding in a macro."""
    action: Optional[str]
    behavior: Optional[str]
    param: Optional[str]
