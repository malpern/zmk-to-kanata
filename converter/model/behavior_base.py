from dataclasses import dataclass, field


@dataclass
class Behavior:
    """Base class for behaviors."""

    name: str
    type: str = field(init=False, default="")

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this behavior."""
        return {
            "name": self.name,
            "type": self.type,
        }
