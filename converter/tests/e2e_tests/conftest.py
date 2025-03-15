"""Test fixtures for end-to-end testing."""

import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files.
    
    This fixture provides a clean temporary directory for each test,
    which is automatically cleaned up after the test completes.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_zmk_file(temp_test_dir):
    """Create a simple ZMK keymap file for testing."""
    content = '''/*
 * Copyright (c) 2023 The ZMK Contributors
 * SPDX-License-Identifier: MIT
 */

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
#include <dt-bindings/zmk/bt.h>
#include <dt-bindings/zmk/outputs.h>

/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            // -------------------------
            // | A | B | C |
            // | X | Y | Z |
            // -------------------------
            label = "BASE";
            bindings = <
                &kp A &kp B &kp C
                &kp X &kp Y &kp Z
            >;
        };

        nav_layer {
            // -------------------------
            // | - | ↑ | - |
            // | ← | ↓ | → |
            // -------------------------
            label = "NAV";
            bindings = <
                &trans &kp UP &trans
                &kp LEFT &kp DOWN &kp RIGHT
            >;
        };
    };
};
'''
    file_path = temp_test_dir / "test_keymap.dtsi"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path

@pytest.fixture
def expected_kanata_output():
    """Return expected Kanata configuration for the sample ZMK file."""
    return '''
(defsrc
  a b c
  x y z)

(deflayer default
  a b c
  x y z)

(deflayer nav
  _ up _
  left down right)
'''

@pytest.fixture
def cli_runner():
    """Fixture for running CLI commands."""
    def run(args):
        from converter.main import main
        try:
            return main(args)
        except SystemExit as e:
            return e.code
    return run 