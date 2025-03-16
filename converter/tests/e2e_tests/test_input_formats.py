"""End-to-end tests for handling different ZMK input formats."""

from converter.cli import main


def test_single_layer_keymap(temp_test_dir):
    """Test conversion of a simple single-layer keymap."""
    zmk_content = '''
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B &kp C
                &kp D &kp E &kp F
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'single_layer.dtsi'
    zmk_file.write_text(zmk_content)
    
    kanata_file = temp_test_dir / 'single_layer.kbd'
    
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    content = kanata_file.read_text()
    
    # Verify layer definition
    assert "(deflayer default" in content
    
    # Verify all keys are present and properly formatted
    keys = ["a", "b", "c", "d", "e", "f"]
    for key in keys:
        assert key in content.lower()
    
    # Verify proper indentation and structure
    lines = content.splitlines()
    assert lines[1].startswith("  ")  # Check indentation
    assert lines[-1] == ")"  # Check closing parenthesis


def test_multiple_layer_keymap(temp_test_dir):
    """Test conversion of a keymap with multiple layers."""
    zmk_content = '''
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &kp B
                &mo 1 &kp C
            >;
        };
        
        layer_1 {
            bindings = <
                &kp N1 &kp N2
                &trans &kp N3
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'multi_layer.dtsi'
    zmk_file.write_text(zmk_content)
    
    kanata_file = temp_test_dir / 'multi_layer.kbd'
    
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    content = kanata_file.read_text()
    
    # Verify default layer with layer switching
    assert "(deflayer default" in content
    assert "a b" in content.lower()
    assert "@layer1" in content  # Layer switching key
    assert "c" in content.lower()


def test_empty_layer_keymap(temp_test_dir):
    """Test handling of empty layers in keymap."""
    zmk_content = '''
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <
                &kp A &none
                &mo 1 &none
            >;
        };
        
        empty_layer {
            bindings = <
                &none &none
                &none &none
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'empty_layer.dtsi'
    zmk_file.write_text(zmk_content)
    
    kanata_file = temp_test_dir / 'empty_layer.kbd'
    
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    content = kanata_file.read_text()
    
    # Verify default layer with layer switching
    assert "(deflayer default" in content
    assert "a" in content.lower()
    assert "@layer1" in content  # Layer switching key
    
    # Verify empty layer exists
    assert "(deflayer empty" in content


def test_comments_and_whitespace(temp_test_dir):
    """Test handling of comments and whitespace in ZMK files."""
    zmk_content = '''
// This is a comment
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/* Multi-line
   comment */
/ {
    keymap {
        compatible = "zmk,keymap";
        
        // Layer comment
        default_layer {
            bindings = <
                // Row comment
                &kp A &kp B  // Inline comment
                
                &kp C &kp D
            >;
        };
    };
};
'''
    zmk_file = temp_test_dir / 'commented.dtsi'
    zmk_file.write_text(zmk_content)
    
    kanata_file = temp_test_dir / 'commented.kbd'
    
    exit_code = main([str(zmk_file), str(kanata_file)])
    assert exit_code == 0
    
    content = kanata_file.read_text()
    
    # Verify key mapping is correct despite comments/whitespace
    assert "(deflayer default" in content
    
    # Check key layout
    lines = content.splitlines()
    assert "a b" in lines[1].lower()
    assert "c d" in lines[2].lower()
    assert lines[-1] == ")"  # Proper closing 