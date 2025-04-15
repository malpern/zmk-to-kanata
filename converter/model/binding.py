"""Base binding module for keymap models."""


class Binding:
    """Base class for all key bindings."""

    def to_kanata(self) -> str:
        """Convert the binding to Kanata format.

        This method should be implemented by subclasses.

        Returns:
            A string representing the binding in Kanata format
        """
        raise NotImplementedError("Subclasses must implement to_kanata()")
