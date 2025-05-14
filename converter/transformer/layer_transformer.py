from .keycode_map import zmk_to_kanata


def _map_key(self, key: str) -> str:
    """Map a ZMK key to Kanata using the central mapping utility."""
    mapped = zmk_to_kanata(key)
    return mapped if mapped is not None else key
