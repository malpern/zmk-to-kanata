"""Tests for real-world ZMK configurations.

This module contains end-to-end tests for real-world ZMK configurations
collected from actual users. These tests ensure that the converter works
correctly with a variety of keyboard layouts and configurations.
"""

import io
import sys
import pytest
from converter.main import main  # Import the main entry point


@pytest.mark.e2e
def test_qwerty_standard_layout(tmp_path, monkeypatch):
    """Test conversion of a standard QWERTY layout."""
    # Setup test files
    zmk_file = tmp_path / "qwerty_standard.dtsi"
    kanata_file = tmp_path / "qwerty_standard.kbd"

    # Standard QWERTY layout with basic layers
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp ESC   &kp N1 &kp N2 &kp N3 &kp N4 &kp N5 &kp N6 &kp N7 &kp N8 &kp N9
                    &kp N0 &kp MINUS &kp EQUAL &kp BSPC
                    &kp TAB   &kp Q  &kp W  &kp E  &kp R  &kp T  &kp Y  &kp U  &kp I  &kp O
                    &kp P  &kp LBKT  &kp RBKT  &kp BSLH
                    &kp LCTRL &kp A  &kp S  &kp D  &kp F  &kp G  &kp H  &kp J  &kp K  &kp L
                    &kp SEMI &kp SQT  &kp RET
                    &kp LSHFT &kp Z  &kp X  &kp C  &kp V  &kp B  &kp N  &kp M  &kp COMMA
                    &kp DOT &kp FSLH &kp RSHFT
                    &kp LCTRL &kp LGUI &kp LALT &kp SPACE &kp RALT &kp RGUI &mo 1 &kp RCTRL
                >;
            };

            function_layer {
                bindings = <
                    &kp GRAVE &kp F1 &kp F2 &kp F3 &kp F4 &kp F5 &kp F6 &kp F7 &kp F8 &kp F9
                    &kp F10 &kp F11 &kp F12 &kp DEL
                    &trans    &trans &trans &trans &trans &trans &trans &trans &trans &trans
                    &trans  &trans  &trans  &trans
                    &trans    &trans &trans &trans &trans &trans &kp LEFT &kp DOWN &kp UP
                    &kp RIGHT &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans &trans &trans &trans
                    &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv for main: input file and -o output file
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    # Run the main function and assert exit code 0
    exit_code = main()
    assert exit_code == 0
    assert kanata_file.exists()
    # Add basic content check
    content = kanata_file.read_text()
    assert "(deflayer default" in content
    assert "q w e r t" in content.lower()


@pytest.mark.e2e
def test_colemak_layout(tmp_path, monkeypatch):
    """Test conversion of a Colemak layout."""
    # Setup test files
    zmk_file = tmp_path / "colemak.dtsi"
    kanata_file = tmp_path / "colemak.kbd"

    # Colemak layout
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp ESC   &kp N1 &kp N2 &kp N3 &kp N4 &kp N5 &kp N6 &kp N7 &kp N8 &kp N9
                    &kp N0 &kp MINUS &kp EQUAL &kp BSPC
                    &kp TAB   &kp Q  &kp W  &kp F  &kp P  &kp G  &kp J  &kp L  &kp U  &kp Y
                    &kp SEMI &kp LBKT &kp RBKT &kp BSLH
                    &kp LCTRL &kp A  &kp R  &kp S  &kp T  &kp D  &kp H  &kp N  &kp E  &kp I
                    &kp O  &kp SQT   &kp RET
                    &kp LSHFT &kp Z  &kp X  &kp C  &kp V  &kp B  &kp K  &kp M  &kp COMMA
                    &kp DOT &kp FSLH &kp RSHFT
                    &kp LCTRL &kp LGUI &kp LALT &kp SPACE &kp RALT &kp RGUI &mo 1 &kp RCTRL
                >;
            };

            function_layer {
                bindings = <
                    &kp GRAVE &kp F1 &kp F2 &kp F3 &kp F4 &kp F5 &kp F6 &kp F7 &kp F8 &kp F9
                    &kp F10 &kp F11 &kp F12 &kp DEL
                    &trans    &trans &trans &trans &trans &trans &trans &trans &trans &trans
                    &trans  &trans  &trans  &trans
                    &trans    &trans &trans &trans &trans &trans &kp LEFT &kp DOWN &kp UP
                    &kp RIGHT &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans &trans &trans &trans
                    &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    exit_code = main()
    assert exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(deflayer default" in content
    assert "q w f p g" in content.lower()  # Check colemak keys


@pytest.mark.e2e
def test_split_keyboard_layout(tmp_path, monkeypatch):
    """Test conversion of a split keyboard layout."""
    # Setup test files
    zmk_file = tmp_path / "split_keyboard.dtsi"
    kanata_file = tmp_path / "split_keyboard.kbd"

    # Split keyboard layout (e.g., Corne, Lily58, etc.)
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp TAB   &kp Q &kp W &kp E &kp R &kp T   &kp Y &kp U  &kp I     &kp O   &kp P    &kp BSPC
                    &kp LCTRL &kp A &kp S &kp D &kp F &kp G   &kp H &kp J  &kp K     &kp L   &kp SEMI &kp SQT
                    &kp LSHFT &kp Z &kp X &kp C &kp V &kp B   &kp N &kp M  &kp COMMA &kp DOT &kp FSLH &kp RSHFT
                                    &kp LGUI &mo 1 &kp SPACE   &kp RET &mo 2 &kp RALT
                >;
            };

            lower_layer {
                bindings = <
                    &kp ESC   &kp N1   &kp N2 &kp N3   &kp N4   &kp N5
                    &kp N6   &kp N7   &kp N8 &kp N9    &kp N0   &kp DEL
                    &kp LCTRL &kp LGUI &trans &kp LALT &kp LSHFT &trans
                    &kp LEFT &kp DOWN &kp UP &kp RIGHT &trans   &trans
                    &trans    &trans   &trans &trans   &trans   &trans
                    &trans   &trans   &trans &trans    &trans   &trans
                                       &trans &trans   &trans
                                       &trans   &trans   &trans
                >;
            };

            raise_layer {
                bindings = <
                    &kp GRAVE &kp F1 &kp F2 &kp F3 &kp F4 &kp F5
                    &kp F6 &kp F7 &kp F8 &kp F9 &kp F10 &kp F11
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans  &kp F12
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans  &trans
                                     &trans &trans &trans
                                     &trans &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    exit_code = main()
    assert exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(deflayer default" in content
    # Check some keys expected in a split layout example
    assert "a s d f" in content.lower()
    assert "j k l semi" in content.lower()


@pytest.mark.e2e
def test_ergonomic_layout_with_homerow_mods(tmp_path, monkeypatch):
    """Test conversion of an ergonomic layout with homerow mods."""
    # Setup test files
    zmk_file = tmp_path / "ergonomic_homerow.dtsi"
    kanata_file = tmp_path / "ergonomic_homerow.kbd"

    # Ergonomic layout with homerow mods
    # Note: This test is expected to fail with the current implementation
    # because the converter doesn't support the &hm behavior directly.
    # In a real-world scenario, users would need to define these in ZMK
    # and then manually adjust the Kanata config.
    zmk_content = """
    / {
        behaviors {
            hm: homerow_mods {
                compatible = "zmk,behavior-hold-tap";
                #binding-cells = <2>;
                tapping-term-ms = <200>;
                quick-tap-ms = <0>;
                flavor = "tap-preferred";
                bindings = <&kp>, <&kp>;
            };
        };

        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp TAB   &kp Q &kp W &kp E &kp R &kp T   &kp Y &kp U  &kp I     &kp O   &kp P    &kp BSPC
                    &kp ESC   &hm LGUI A &hm LALT S &hm LCTRL D &hm LSHFT F &kp G
                    &kp H &hm RSHFT J  &hm RCTRL K &hm RALT L &hm RGUI SEMI &kp SQT
                    &kp LSHFT &kp Z &kp X &kp C &kp V &kp B   &kp N &kp M  &kp COMMA &kp DOT &kp FSLH &kp RSHFT
                                    &kp LGUI &mo 1 &kp SPACE   &kp RET &mo 2 &kp RALT
                >;
            };

            lower_layer {
                bindings = <
                    &kp ESC   &kp N1   &kp N2 &kp N3   &kp N4   &kp N5
                    &kp N6   &kp N7   &kp N8 &kp N9    &kp N0   &kp DEL
                    &kp LCTRL &kp LGUI &trans &kp LALT &kp LSHFT &trans
                    &kp LEFT &kp DOWN &kp UP &kp RIGHT &trans   &trans
                    &trans    &trans   &trans &trans   &trans   &trans
                    &trans   &trans   &trans &trans    &trans   &trans
                                       &trans &trans   &trans
                                       &trans   &trans   &trans
                >;
            };

            raise_layer {
                bindings = <
                    &kp GRAVE &kp F1 &kp F2 &kp F3 &kp F4 &kp F5
                    &kp F6 &kp F7 &kp F8 &kp F9 &kp F10 &kp F11
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans  &kp F12
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans  &trans
                                     &trans &trans &trans
                                     &trans &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    # Run and capture stderr as before, but expect exit code 0 now
    stderr_capture = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = stderr_capture
    exit_code = 99  # Initialize with a non-zero value
    try:
        exit_code = main()
        # Check if output file exists
        assert kanata_file.exists()
        content = kanata_file.read_text()
        # Check for alias definitions and usage
        assert "(defalias hm_" in content  # Check homerow mod alias definition
        assert "@hm_lctl_s" in content  # Check alias usage
    finally:
        sys.stderr = old_stderr
        error_output = stderr_capture.getvalue()
        print(f"STDERR output:\n{error_output}")

    assert exit_code == 0


@pytest.mark.e2e
def test_ben_vallack_cradio_layout(tmp_path, monkeypatch):
    """Test conversion of Ben Vallack's Cradio (Ferris Sweep) layout.

    This test uses a real-world ZMK configuration from Ben Vallack's GitHub repository.
    The layout features a 34-key split keyboard with custom behaviors, combos, and
    multiple layers.

    Source: https://github.com/benvallack/zmk-config
    """
    # Setup test files
    zmk_file = tmp_path / "ben_vallack_cradio.dtsi"
    kanata_file = tmp_path / "ben_vallack_cradio.kbd"

    # Ben Vallack's Cradio layout (simplified for testing)
    zmk_content = """
    / {
        behaviors {
            hm: homerow_mods {
                compatible = "zmk,behavior-hold-tap";
                label = "HOMEROW_MODS";
                #binding-cells = <2>;
                tapping-term-ms = <200>;
                quick_tap_ms = <0>;
                flavor = "tap-preferred";
                bindings = <&kp>, <&kp>;
            };
            hs: homerow_shifts {
                compatible = "zmk,behavior-hold-tap";
                label = "HOMEROW_SHIFTS";
                #binding-cells = <2>;
                tapping-term-ms = <150>;
                quick_tap_ms = <0>;
                flavor = "balanced";
                bindings = <&kp>, <&kp>;
            };
            td: tapdance {
                compatible = "zmk,behavior-hold-tap";
                label = "TAPDANCE";
                #binding-cells = <2>;
                tapping-term-ms = <150>;
                quick_tap_ms = <0>;
                flavor = "tap-preferred";
                bindings = <&kp>, <&kp>;
            };
        };

        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp TAB &kp C &kp L &kp M &trans
                    &trans &kp F  &kp U    &kp Z  &kp BKSP
                    &kp I &hm LCTL S &hm LALT R &hm LGUI T &trans
                    &trans  &hm RGUI N &hm RALT K &hm RCTL A &kp O
                    &hs LSHIFT Q &kp V &kp W &kp D &mt LC(LS(LALT)) SPC
                    &kp E &kp H  &kp Y &td EXCL DOT &hs RSHIFT X
                                    &mt LC(LS(LALT)) SPC &trans
                                    &trans &kp E
                >;
            };

            left_layer {
                bindings = <
                    &trans  &kp ATSN   &td LC(LG(LS(N4))) LS(N3) &kp DLLR &trans
                    &trans &kp LS(COMMA) &kp LS(DOT) &kp CARET &trans
                    &kp TAB &hm LCTL EQUAL &hm LALT LA(RBKT) &hm LGUI LA(LS(RBKT)) &trans
                    &trans &hm RGUI LBRC &hm RALT RBRC &hm RCTL PIPE &kp AMPS
                    &hs LSHIFT TILDE &kp GRAVE &kp LA(LBKT) &kp LA(LS(LBKT)) &to 0
                    &to 2 &kp LPRN &kp RPRN &kp RBKT &kp RSHIFT
                                    &to 0 &trans
                                    &trans &to 2
                >;
            };

            right_layer {
                bindings = <
                    &trans &kp C_PP &kp C_PREV &kp C_NEXT &trans
                    &trans &kp N7 &kp N8 &kp N9 &trans
                    &kp TAB &trans &hm LALT C_VOL_DN &hm LGUI C_VOL_UP &trans
                    &trans &hm RGUI N4 &kp N5 &kp N6 &kp EQUAL
                    &hs LSHIFT PRCNT &kp PRCNT &kp SLASH &kp STAR &to 0
                    &trans &kp N1 &kp N2 &td DOT N3 &kp MINUS
                                    &to 0 &trans
                                    &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    stderr_capture = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = stderr_capture
    exit_code = 99
    try:
        exit_code = main()
        assert kanata_file.exists()
        content = kanata_file.read_text()
        assert "(deflayer default_layer" in content
        assert "(deflayer left_layer" in content
        assert "(deflayer right_layer" in content
        assert "(defalias hm_" in content
        assert "(defalias hs_" in content
        assert "(defalias td_" in content
    finally:
        sys.stderr = old_stderr
        error_output = stderr_capture.getvalue()
        print(f"STDERR output:\n{error_output}")

    assert exit_code == 0


@pytest.mark.e2e
def test_dvorak_layout(tmp_path, monkeypatch):
    """Test conversion of a Dvorak layout."""
    # Setup test files
    zmk_file = tmp_path / "dvorak.dtsi"
    kanata_file = tmp_path / "dvorak.kbd"

    # Dvorak layout
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp ESC   &kp N1 &kp N2 &kp N3 &kp N4 &kp N5
                    &kp N6 &kp N7 &kp N8 &kp N9 &kp N0 &kp BSPC
                    &kp TAB   &kp APOS &kp COMMA &kp DOT &kp P &kp Y
                    &kp F &kp G &kp C &kp R &kp L &kp BSLH
                    &kp LCTRL &kp A &kp O &kp E &kp U &kp I
                    &kp D &kp H &kp T &kp N &kp S &kp MINUS
                    &kp LSHFT &kp SEMI &kp Q &kp J &kp K &kp X
                    &kp B &kp M &kp W &kp V &kp Z &kp RSHFT
                    &kp LGUI &kp LALT &mo 1 &kp SPACE &mo 2 &kp RALT
                >;
            };

            lower_layer {
                bindings = <
                    &kp GRAVE &kp F1 &kp F2 &kp F3 &kp F4 &kp F5
                    &kp F6 &kp F7 &kp F8 &kp F9 &kp F10 &kp DEL
                    &trans    &kp F11 &kp F12 &trans &trans &trans
                    &trans &trans &trans &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans
                    &kp LEFT &kp DOWN &kp UP &kp RIGHT &trans &trans
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans
                >;
            };

            raise_layer {
                bindings = <
                    &kp TILDE &kp EXCL &kp AT &kp HASH &kp DLLR &kp PRCNT
                    &kp CARET &kp AMPS &kp STAR &kp LPAR &kp RPAR &kp DEL
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans
                    &kp LBRC &kp RBRC &kp LBKT &kp RBKT &kp EQUAL &kp PLUS
                    &trans    &trans &trans &trans &trans &trans
                    &trans &trans &trans &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    exit_code = main()
    assert exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(deflayer default_layer" in content
    assert "(deflayer lower_layer" in content
    assert "(deflayer raise_layer" in content
    assert "' , . p y" in content.lower()  # Check dvorak keys


@pytest.mark.e2e
def test_ergonomic_kyria_layout(tmp_path, monkeypatch):
    """Test conversion of an ergonomic Kyria layout.

    The Kyria is a popular ergonomic split keyboard with thumb clusters
    and a columnar staggered layout. This test verifies that the converter
    correctly handles the unique layout and features of ergonomic keyboards.
    """
    # Setup test files
    zmk_file = tmp_path / "kyria_ergonomic.dtsi"
    kanata_file = tmp_path / "kyria_ergonomic.kbd"

    # Kyria ergonomic layout
    zmk_content = """
    / {
        keymap {
            compatible = "zmk,keymap";

            default_layer {
                bindings = <
                    &kp TAB   &kp Q &kp W &kp E &kp R &kp T                 &kp Y &kp U  &kp I     &kp O   &kp P    &kp BSPC
                    &kp ESC   &kp A &kp S &kp D &kp F &kp G                 &kp H &kp J  &kp K     &kp L   &kp SEMI &kp SQT
                    &kp LSHFT &kp Z &kp X &kp C &kp V &kp B &kp LBKT     &kp RBKT &kp N &kp M  &kp COMMA &kp DOT &kp FSLH &kp RSHFT
                                 &kp LGUI &kp LALT &kp LCTRL &kp SPACE   &kp RET &mo 1 &mo 2 &kp RALT
                >;
            };

            lower_layer {
                bindings = <
                    &kp GRAVE &kp N1 &kp N2 &kp N3 &kp N4 &kp N5           &kp N6 &kp N7 &kp N8 &kp N9 &kp N0 &kp DEL
                    &trans    &trans &trans &trans &trans &trans           &kp LEFT &kp DOWN &kp UP &kp RIGHT &trans &trans
                    &trans    &trans &trans &trans &trans &trans &trans  &trans &trans &trans &trans &trans &trans &trans
                                 &trans &trans &trans &trans              &trans &trans &trans &trans
                >;
            };

            raise_layer {
                bindings = <
                    &kp F1    &kp F2 &kp F3 &kp F4 &kp F5 &kp F6           &kp F7 &kp F8 &kp F9 &kp F10 &kp F11 &kp F12
                    &trans    &trans &trans &trans &trans &trans           &trans &trans &trans &trans &trans &trans
                    &trans    &trans &trans &trans &trans &trans &trans  &trans &trans &trans &trans &trans &trans &trans
                                 &trans &trans &trans &trans              &trans &trans &trans &trans
                >;
            };
        };
    };
    """

    # Write the ZMK content to the file
    zmk_file.write_text(zmk_content)

    # Correctly set sys.argv
    args = ["converter_script_name", str(zmk_file), "-o", str(kanata_file)]
    monkeypatch.setattr(sys, "argv", args)

    exit_code = main()
    assert exit_code == 0
    assert kanata_file.exists()
    content = kanata_file.read_text()
    assert "(deflayer default_layer" in content
    assert "(deflayer lower_layer" in content
    assert "(deflayer raise_layer" in content
    # Check some kyria layout specifics
    assert "q w e r t" in content.lower()
    assert "y u i o p" in content.lower()
