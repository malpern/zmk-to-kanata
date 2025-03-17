"""End-to-end tests for the full ZMK to Kanata conversion pipeline."""

import tempfile
from pathlib import Path
from textwrap import dedent

from converter.main import main
from converter.zmk_to_kanata import convert_zmk_to_kanata


def test_basic_conversion_pipeline():
    """Test basic end-to-end conversion pipeline.

    Uses the main CLI entrypoint for complete pipeline testing.
    """
    zmk_content = dedent("""
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
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "input.zmk"
        output_file = Path(tmpdir) / "output.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        exit_code = main([str(input_file), str(output_file)])

        # Verify success
        assert exit_code == 0
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        assert "A B C" in kanata_content
        assert "D E F" in kanata_content


def test_complex_binding_conversion():
    """Test end-to-end conversion with complex bindings."""
    zmk_content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &lt 1 A &mt LSHIFT B &kp C
                        &mo 2 &tog 3 &to 1
                    >;
                };

                layer_1 {
                    bindings = <
                        &kp X &kp Y &kp Z
                        &trans &trans &trans
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "input.zmk"
        output_file = Path(tmpdir) / "output.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        result = convert_zmk_to_kanata(input_file, output_file)

        # Verify success
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        assert "(deflayer layer_1" in kanata_content
        assert "lt(1,A) mt(LSHIFT,B) C" in kanata_content
        assert "mo(2) tog(3) to(1)" in kanata_content
        assert "X Y Z" in kanata_content
        assert "_" in kanata_content  # trans should be converted to _


def test_macro_conversion():
    """Test end-to-end conversion with macros."""
    zmk_content = dedent("""
        / {
            macros {
                test_macro: test_macro {
                    label = "test macro";
                    compatible = "zmk,behavior-macro";
                    #binding-cells = <0>;
                    bindings = <&kp A &kp B &kp C>;
                };

                param_macro: param_macro {
                    label = "parameterized macro";
                    compatible = "zmk,behavior-macro-two-param";
                    #binding-cells = <2>;
                    bindings = <&macro_param_1to1>, <&macro_param_2to1>;
                };
            };

            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &test_macro &param_macro 1 2 &kp C
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "input.zmk"
        output_file = Path(tmpdir) / "output.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        result = convert_zmk_to_kanata(input_file, output_file)

        # Verify success
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(defmacro test_macro" in kanata_content
        assert "(defmacro param_macro" in kanata_content
        assert "(deflayer default" in kanata_content
        assert "@test_macro @param_macro(1,2) C" in kanata_content


def test_error_recovery():
    """Test end-to-end conversion with error recovery."""
    zmk_content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A &invalid B &kp C
                        &lt INVALID D &kp E &kp F
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "input.zmk"
        output_file = Path(tmpdir) / "output.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion with error recovery
        result = convert_zmk_to_kanata(
            input_file,
            output_file,
            recover_errors=True
        )

        # Verify success despite errors
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        # Replace unknown with XX for easier assertion
        content_normalized = kanata_content.replace("unknown", "XX")
        assert "A XX C" in content_normalized
        assert "XX E F" in content_normalized


def test_multiple_layer_conversion():
    """Test end-to-end conversion with multiple layers."""
    zmk_content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A &kp B &kp C
                    >;
                };

                nav_layer {
                    bindings = <
                        &kp LEFT &kp DOWN &kp RIGHT
                    >;
                };

                sym_layer {
                    bindings = <
                        &kp EXCL &kp AT &kp HASH
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "input.zmk"
        output_file = Path(tmpdir) / "output.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        result = convert_zmk_to_kanata(input_file, output_file)

        # Verify success
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        assert "(deflayer nav_layer" in kanata_content
        assert "(deflayer sym_layer" in kanata_content
        assert "A B C" in kanata_content
        assert "left down right" in kanata_content.lower()
        assert "! @ #" in kanata_content


def test_global_settings():
    """Test end-to-end conversion with global settings."""
    zmk_content = dedent("""
        / {
            chosen {
                zmk,matrix_transform = &default_transform;
            };

            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A &kp B &kp C
                    >;
                };
            };
        };
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "input.zmk"
        output_file = Path(tmpdir) / "output.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(zmk_content)

        # Run the conversion
        result = convert_zmk_to_kanata(input_file, output_file)

        # Verify success
        assert result is True
        assert output_file.exists()

        # Check output content
        with open(output_file, "r") as f:
            kanata_content = f.read()

        # Verify output has expected elements
        assert "(deflayer default" in kanata_content
        assert "A B C" in kanata_content
