"""Performance tests for the ZMK to Kanata conversion pipeline."""
import time
import pytest
from converter.zmk_parser import ZMKParser
from converter.layer_transformer import LayerTransformer
from converter.holdtap_transformer import HoldTapTransformer
from converter.macro_transformer import MacroTransformer
from converter.sticky_key_transformer import StickyKeyTransformer


@pytest.fixture
def parser():
    """Create a ZMKParser instance."""
    return ZMKParser()


@pytest.fixture
def transformers():
    """Create instances of all transformers."""
    return {
        'layer': LayerTransformer(),
        'holdtap': HoldTapTransformer(),
        'macro': MacroTransformer(),
        'sticky': StickyKeyTransformer()
    }


def generate_large_layer(size):
    """Generate a large layer with specified number of bindings."""
    bindings = ' '.join(['&kp A'] * size)
    return f"""
    / {{
        keymap {{
            compatible = "zmk,keymap";
            default_layer {{
                bindings = <
                    {bindings}
                >;
            }};
        }};
    }};
    """


def generate_complex_macros(count):
    """Generate multiple complex macro definitions."""
    macro_template = """
            macro_{i}: macro_{i} {{
                compatible = "zmk,behavior-macro";
                bindings = <
                    &kp A &kp B
                    &macro_wait_time 50
                    &kp C &kp D
                    &macro_tap_time 30
                    &kp E &kp F
                >;
            }};"""

    macros = '\n'.join(macro_template.format(i=i) for i in range(count))

    return f"""
    / {{
        macros {{
            {macros}
        }};
        keymap {{
            compatible = "zmk,keymap";
            default_layer {{
                bindings = <
                    {' '.join(f'&macro_{i}' for i in range(count))}
                >;
            }};
        }};
    }};
    """


def measure_execution_time(func):
    """Measure execution time of a function."""
    start_time = time.time()
    result = func()
    end_time = time.time()
    return result, (end_time - start_time) * 1000  # Convert to milliseconds


def test_large_layer_performance(parser, transformers):
    """Test performance with large layers."""
    sizes = [100, 500, 1000]
    results = []

    for size in sizes:
        zmk_input = generate_large_layer(size)

        # Measure parsing time
        _, parse_time = measure_execution_time(
            lambda: parser.parse_layers(zmk_input)
        )

        # Measure transformation time
        layers = parser.parse_layers(zmk_input)
        _, transform_time = measure_execution_time(
            lambda: transformers['layer'].transform_layers(layers)
        )

        results.append({
            'size': size,
            'parse_time': parse_time,
            'transform_time': transform_time
        })

    # Verify performance scales reasonably
    for i in range(1, len(results)):
        size_ratio = results[i]['size'] / results[i-1]['size']
        time_ratio = results[i]['parse_time'] / results[i-1]['parse_time']

        # Time should scale sub-linearly or linearly with size
        size = results[i]['size']
        msg = f"Performance degraded significantly at size {size}"
        assert time_ratio <= size_ratio * 1.5, msg


def test_complex_macro_performance(parser, transformers):
    """Test performance with complex macro definitions."""
    counts = [10, 50, 100]
    results = []

    for count in counts:
        zmk_input = generate_complex_macros(count)

        # Measure parsing time
        _, parse_time = measure_execution_time(
            lambda: parser.parse_layers(zmk_input)
        )

        # Measure transformation time
        layers = parser.parse_layers(zmk_input)
        _, transform_time = measure_execution_time(
            lambda: transformers['macro'].transform_macros(layers)
        )

        results.append({
            'count': count,
            'parse_time': parse_time,
            'transform_time': transform_time
        })

    # Verify performance scales reasonably
    for i in range(1, len(results)):
        count_ratio = results[i]['count'] / results[i-1]['count']
        time_ratio = results[i]['parse_time'] / results[i-1]['parse_time']

        # Time should scale sub-linearly or linearly with count
        count = results[i]['count']
        msg = f"Performance degraded significantly at count {count}"
        assert time_ratio <= count_ratio * 1.5, msg


def test_mixed_behavior_performance(parser, transformers):
    """Test performance with mixed behaviors in a single layer."""
    zmk_input = """
    / {
        macros {
            test_macro: test_macro {
                compatible = "zmk,behavior-macro";
                bindings = <&kp A &kp B>;
            };
        };
        keymap {
            compatible = "zmk,keymap";
            default_layer {
                bindings = <
                    &kp A
                    &ht LSHIFT B
                    &test_macro
                    &sk LCTRL
                    &mo 1
                >;
            };
            layer_1 {
                bindings = <
                    &kp C
                    &ht LALT D
                    &test_macro
                    &sk LGUI
                    &trans
                >;
            };
        };
    };
    """

    # Measure total pipeline performance
    def process_pipeline():
        layers = parser.parse_layers(zmk_input)
        for transformer in transformers.values():
            if hasattr(transformer, 'transform_layers'):
                transformer.transform_layers(layers)
            if hasattr(transformer, 'transform_macros'):
                transformer.transform_macros(layers)

    _, total_time = measure_execution_time(process_pipeline)

    # Verify reasonable performance for mixed behaviors
    assert total_time < 100, (
        f"Mixed behavior processing took too long: {total_time:.2f}ms"
    )


def test_memory_usage(parser, transformers):
    """Test memory usage with large configurations."""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Generate and process a large configuration
    zmk_input = generate_large_layer(5000)
    layers = parser.parse_layers(zmk_input)
    transformers['layer'].transform_layers(layers)

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    # Verify reasonable memory usage
    assert memory_increase < 100, (
        f"Memory usage increased significantly: {memory_increase:.2f}MB"
    )
