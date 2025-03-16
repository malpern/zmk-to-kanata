"""End-to-end tests for macro support."""

from converter.cli import main


def test_basic_macro_conversion(tmp_path):
    """Test converting a ZMK file with a basic macro to Kanata format."""
    # Create a temporary ZMK file with a macro
    zmk_content = """
    / {
        behaviors {
            simple_macro: simple_macro {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                bindings = <&kp A &kp B &kp C>;
            };
        };

        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &simple_macro &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    zmk_file = tmp_path / "test_macro.keymap"
    zmk_file.write_text(zmk_content)

    # Create a temporary output file
    output_file = tmp_path / "test_macro.kbd"

    # Run the converter
    args = [str(zmk_file), str(output_file)]
    exit_code = main(args)

    # Check that the conversion was successful
    assert exit_code == 0
    assert output_file.exists()

    # Read the output file
    kanata_content = output_file.read_text()

    # Check that the macro is defined in the output
    assert "(defmacro simple_macro" in kanata_content
    assert "tap a" in kanata_content
    assert "tap b" in kanata_content
    assert "tap c" in kanata_content

    # Check that the macro is referenced in the keymap
    assert "(macro simple_macro)" in kanata_content


def test_complex_macro_conversion(tmp_path):
    """Test converting a ZMK file with a complex macro to Kanata format."""
    # Create a temporary ZMK file with a complex macro
    zmk_content = """
    / {
        behaviors {
            complex_macro: complex_macro {
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                wait-ms = <20>;
                tap-ms = <40>;
                bindings = <
                    &macro_press &kp LSHIFT
                    &kp A
                    &macro_release &kp LSHIFT
                    &macro_wait_time 50
                    &kp B &kp C
                >;
            };
        };

        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &complex_macro &kp B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    zmk_file = tmp_path / "test_complex_macro.keymap"
    zmk_file.write_text(zmk_content)

    # Create a temporary output file
    output_file = tmp_path / "test_complex_macro.kbd"

    # Run the converter
    args = [str(zmk_file), str(output_file)]
    exit_code = main(args)

    # Check that the conversion was successful
    assert exit_code == 0
    assert output_file.exists()

    # Read the output file
    kanata_content = output_file.read_text()

    # Check that the macro is defined in the output
    assert "(defmacro complex_macro" in kanata_content
    assert "press lsft" in kanata_content
    assert "press a" in kanata_content
    assert "release lsft" in kanata_content
    assert "delay 50" in kanata_content
    assert "tap b" in kanata_content
    assert "tap c" in kanata_content

    # Check that the macro is referenced in the keymap
    assert "(macro complex_macro)" in kanata_content


def test_parameterized_macro_conversion(tmp_path):
    """Test converting a ZMK file with a parameterized macro to Kanata format."""
    # Create a temporary ZMK file with a parameterized macro
    zmk_content = """
    / {
        behaviors {
            param_macro: param_macro {
                compatible = "zmk,behavior-macro-one-param";
                #binding-cells = <1>;
                bindings = <&kp MACRO_PLACEHOLDER>;
            };
        };

        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &param_macro A &param_macro B &kp C
                    &kp D &kp E &kp F
                >;
            };
        };
    };
    """

    zmk_file = tmp_path / "test_param_macro.keymap"
    zmk_file.write_text(zmk_content)

    # Create a temporary output file
    output_file = tmp_path / "test_param_macro.kbd"

    # Run the converter
    args = [str(zmk_file), str(output_file)]
    exit_code = main(args)

    # Check that the conversion was successful
    assert exit_code == 0
    assert output_file.exists()

    # Read the output file
    kanata_content = output_file.read_text()

    # Check that the macro is defined in the output
    assert "(defmacro param_macro" in kanata_content

    # Check that the macro is referenced in the keymap
    assert "(macro param_macro)" in kanata_content
