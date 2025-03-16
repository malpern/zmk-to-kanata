"""Tests for real-world ZMK configurations.

This module contains end-to-end tests for real-world ZMK configurations
collected from actual users. These tests ensure that the converter works
correctly with a variety of keyboard layouts and configurations.
"""

import sys
import io


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
    
    # Set up sys.argv for the main function
    monkeypatch.setattr(sys, 'argv', ['converter', str(zmk_file), str(kanata_file)])
    
    # Run the converter
    from converter.main import main
    main()
    
    # Check that the conversion was successful
    assert kanata_file.exists()
    
    # Read the generated Kanata file
    kanata_content = kanata_file.read_text()
    
    # Verify the content
    assert ";; ZMK to Kanata Configuration" in kanata_content
    assert "(defvar tap-time 200)" in kanata_content
    assert "(defvar hold-time 250)" in kanata_content
    assert "(deflayer default" in kanata_content
    assert "(deflayer function" in kanata_content
    
    # Check for specific key mappings
    assert "esc" in kanata_content.lower()
    assert "tab" in kanata_content.lower()
    assert "lctrl" in kanata_content.lower()
    assert "lshft" in kanata_content.lower()
    assert "space" in kanata_content.lower()


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
    
    # Set up sys.argv for the main function
    monkeypatch.setattr(sys, 'argv', ['converter', str(zmk_file), str(kanata_file)])
    
    # Run the converter
    from converter.main import main
    main()
    
    # Check that the conversion was successful
    assert kanata_file.exists()
    
    # Read the generated Kanata file
    kanata_content = kanata_file.read_text()
    
    # Verify the content
    assert ";; ZMK to Kanata Configuration" in kanata_content
    assert "(defvar tap-time 200)" in kanata_content
    assert "(defvar hold-time 250)" in kanata_content
    assert "(deflayer default" in kanata_content
    assert "(deflayer function" in kanata_content
    
    # Check for specific Colemak key mappings
    # In Colemak, F is where D would be in QWERTY, etc.
    default_layer = kanata_content.split("(deflayer default")[1].split("(deflayer")[0]
    
    # Check that the Colemak layout is preserved
    assert "q w f p g" in default_layer.lower()
    assert "a r s t d" in default_layer.lower()


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
    
    # Set up sys.argv for the main function
    monkeypatch.setattr(sys, 'argv', ['converter', str(zmk_file), str(kanata_file)])
    
    # Run the converter
    from converter.main import main
    main()
    
    # Check that the conversion was successful
    assert kanata_file.exists()
    
    # Read the generated Kanata file
    kanata_content = kanata_file.read_text()
    
    # Verify the content
    assert ";; ZMK to Kanata Configuration" in kanata_content
    assert "(defvar tap-time 200)" in kanata_content
    assert "(defvar hold-time 250)" in kanata_content
    assert "(deflayer default" in kanata_content
    assert "(deflayer lower" in kanata_content
    assert "(deflayer raise" in kanata_content
    
    # Check for specific split keyboard features
    # Split keyboards often have thumb clusters and layer switching
    assert "lgui" in kanata_content.lower()
    assert "space" in kanata_content.lower()
    assert "ret" in kanata_content.lower() or "enter" in kanata_content.lower()
    
    # Check for layer switching
    lower_layer = kanata_content.split("(deflayer lower")[1].split("(deflayer")[0]
    raise_layer = kanata_content.split("(deflayer raise")[1].split(")")[0] if "(deflayer raise" in kanata_content else ""
    
    # Navigation keys in lower layer
    assert "left" in lower_layer.lower()
    assert "down" in lower_layer.lower()
    assert "up" in lower_layer.lower()
    assert "right" in lower_layer.lower()
    
    # Function keys in raise layer
    if raise_layer:
        assert "f1" in raise_layer.lower()
        assert "f2" in raise_layer.lower()
        assert "f12" in raise_layer.lower()


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
    
    # Set up sys.argv for the main function
    monkeypatch.setattr(sys, 'argv', ['converter', str(zmk_file), str(kanata_file)])
    
    # Run the converter
    from converter.main import main
    
    # Capture stderr to check for error message
    stderr_capture = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = stderr_capture
    
    try:
        main()
    except SystemExit:
        # The main function might exit due to the error
        pass
    finally:
        # Restore stderr
        sys.stderr = old_stderr
    
    # Check that the error message contains information about the unknown binding
    error_output = stderr_capture.getvalue()
    assert "Unknown binding: &hm" in error_output 