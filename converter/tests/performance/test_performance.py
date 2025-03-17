"""Performance tests for the ZMK to Kanata converter."""

import tempfile
import time
from pathlib import Path
from textwrap import dedent

from converter.parser.zmk_parser import ZMKParser
from converter.transformer.kanata_transformer import KanataTransformer
from converter.zmk_to_kanata import convert_zmk_to_kanata


def generate_large_keymap(num_layers=10, keys_per_layer=200):
    """Generate a large keymap for performance testing."""
    keymap = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";
    """)

    # Generate layers
    for i in range(num_layers):
        layer_name = f"layer_{i}" if i > 0 else "default_layer"
        keymap += f"""
                {layer_name} {{
                    bindings = <
        """

        # Generate keys in the layer (in rows of 10)
        rows = keys_per_layer // 10
        for row in range(rows):
            line = "                        "
            for col in range(10):
                if row % 5 == 0:
                    # Add some complex bindings
                    if col % 3 == 0:
                        line += f"&lt {i+1} A "
                    elif col % 3 == 1:
                        line += "&mt LSHIFT B "
                    else:
                        line += "&kp C "
                elif row % 5 == 1:
                    # Add some layer keys
                    if col % 3 == 0:
                        line += f"&mo {(i+1) % num_layers} "
                    elif col % 3 == 1:
                        line += f"&tog {(i+2) % num_layers} "
                    else:
                        line += f"&to {(i+3) % num_layers} "
                else:
                    # Add regular keys
                    line += f"&kp K{row}{col} "
            keymap += line + "\n"

        keymap += """                    >;
                };
        """

    keymap += """
            };
        };
    """

    return keymap


def test_parser_performance_small():
    """Test parser performance with a small keymap."""
    content = dedent("""
        / {
            keymap {
                compatible = "zmk,keymap";

                default_layer {
                    bindings = <
                        &kp A &kp B &kp C
                        &kp D &kp E &kp F
                    >;
                };

                layer_1 {
                    bindings = <
                        &kp X &kp Y &kp Z
                        &kp U &kp V &kp W
                    >;
                };
            };
        };
    """)

    parser = ZMKParser()

    # Benchmark parsing
    start_time = time.time()
    result = parser.parse(content)
    end_time = time.time()

    parse_time = end_time - start_time
    print(f"Small keymap parse time: {parse_time:.6f} seconds")

    assert parse_time < 0.05  # Should be very fast for small keymaps
    assert len(result["layers"]) == 2
    assert len(result["layers"][0].bindings) == 6


def test_parser_performance_large():
    """Test parser performance with a large keymap."""
    content = generate_large_keymap(num_layers=5, keys_per_layer=100)

    parser = ZMKParser()

    # Benchmark parsing
    start_time = time.time()
    result = parser.parse(content)
    end_time = time.time()

    parse_time = end_time - start_time
    print(f"Large keymap parse time: {parse_time:.6f} seconds")

    # For 5 layers with 100 keys each, parse time should be reasonable
    assert parse_time < 1.0  # This threshold may need adjustment
    assert len(result["layers"]) == 5
    assert len(result["layers"][0].bindings) == 100


def test_transformer_performance():
    """Test transformer performance."""
    # Generate a moderate-sized keymap
    content = generate_large_keymap(num_layers=3, keys_per_layer=50)

    parser = ZMKParser()
    transformer = KanataTransformer()

    # Parse first
    parse_result = parser.parse(content)

    # Benchmark transformation
    start_time = time.time()
    kanata_config = transformer.transform(parse_result)
    end_time = time.time()

    transform_time = end_time - start_time
    print(f"Transform time: {transform_time:.6f} seconds")

    # Transformation should be reasonably fast
    assert transform_time < 0.5  # This threshold may need adjustment
    assert "(deflayer default" in kanata_config
    assert "(deflayer layer_1" in kanata_config
    assert "(deflayer layer_2" in kanata_config


def test_end_to_end_performance():
    """Test end-to-end conversion performance."""
    content = generate_large_keymap(num_layers=4, keys_per_layer=60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temporary input and output files
        input_file = Path(tmpdir) / "large.zmk"
        output_file = Path(tmpdir) / "large.kbd"

        # Write input content
        with open(input_file, "w") as f:
            f.write(content)

        # Benchmark total conversion
        start_time = time.time()
        result = convert_zmk_to_kanata(input_file, output_file)
        end_time = time.time()

        total_time = end_time - start_time
        print(f"End-to-end conversion time: {total_time:.6f} seconds")

        # End-to-end conversion should be reasonably fast
        assert result is True
        assert output_file.exists()
        assert total_time < 2.0  # This threshold may need adjustment

        # Check output file size
        output_size = output_file.stat().st_size
        print(f"Output file size: {output_size} bytes")

        # Should have generated a non-trivial output
        assert output_size > 1000


def test_memory_usage():
    """Test memory usage during conversion of a very large keymap."""
    try:
        import psutil
        import os

        # Create a very large keymap for memory testing
        content = generate_large_keymap(num_layers=10, keys_per_layer=200)

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB

        # Parse and transform
        parser = ZMKParser()
        transformer = KanataTransformer()
        parse_result = parser.parse(content)
        # Transform the parse result (used to measure memory consumption)
        transformer.transform(parse_result)

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        memory_used = final_memory - initial_memory

        print(f"Initial memory: {initial_memory:.2f} MB")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory used: {memory_used:.2f} MB")

        # Memory usage should be reasonable
        assert memory_used < 50  # 50 MB is a reasonable limit for a large keymap

    except ImportError:
        print("psutil not available, skipping memory usage test")
        # Skip the test if psutil is not available
