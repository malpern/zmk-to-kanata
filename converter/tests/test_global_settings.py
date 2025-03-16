"""Global Settings Tests

Tests for parsing global settings from ZMK keymap files.
"""
import pytest
from pathlib import Path
import tempfile

from converter.model.keymap_model import GlobalSettings, KeymapConfig
from converter.parser.zmk_parser import ZMKParser, ParserError


def test_default_global_settings():
    """Test that default global settings are used when none are specified."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.keymap') as f:
        f.write("""
/ {
    keymap {
        default_layer {
            bindings = <&kp A>;
        };
    };
};
        """)
        f.flush()
        
        parser = ZMKParser()
        config = parser.parse(Path(f.name))
        
        assert config.global_settings.tap_time == 200
        assert config.global_settings.hold_time == 250


def test_custom_global_settings():
    """Test parsing custom global settings."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.keymap') as f:
        f.write("""
/ {
    tap-time = <300>;
    hold-time = <400>;
    keymap {
        default_layer {
            bindings = <&kp A>;
        };
    };
};
        """)
        f.flush()
        
        parser = ZMKParser()
        config = parser.parse(Path(f.name))
        
        assert config.global_settings.tap_time == 300
        assert config.global_settings.hold_time == 400


def test_partial_global_settings():
    """Test parsing when only some global settings are specified."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.keymap') as f:
        f.write("""
/ {
    tap-time = <300>;
    keymap {
        default_layer {
            bindings = <&kp A>;
        };
    };
};
        """)
        f.flush()
        
        parser = ZMKParser()
        config = parser.parse(Path(f.name))
        
        assert config.global_settings.tap_time == 300
        assert config.global_settings.hold_time == 250  # Default value


def test_invalid_global_settings():
    """Test handling of invalid global settings."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.keymap') as f:
        f.write("""
/ {
    tap-time = <invalid>;
    keymap {
        default_layer {
            bindings = <&kp A>;
        };
    };
};
        """)
        f.flush()
        
        parser = ZMKParser()
        with pytest.raises(ParserError) as exc_info:
            parser.parse(Path(f.name))
        
        assert "Invalid tap-time setting" in str(exc_info.value)


def test_malformed_global_settings():
    """Test handling of malformed global settings."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.keymap') as f:
        f.write("""
/ {
    tap-time = 200;  # Missing angle brackets
    keymap {
        default_layer {
            bindings = <&kp A>;
        };
    };
};
        """)
        f.flush()
        
        parser = ZMKParser()
        with pytest.raises(ParserError) as exc_info:
            parser.parse(Path(f.name))
        
        assert "Invalid tap-time setting" in str(exc_info.value) 