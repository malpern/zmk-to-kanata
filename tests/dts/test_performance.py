"""Performance tests for the DTS-based ZMK parser."""

import pytest
import time
import statistics
from pathlib import Path
from converter.dts.preprocessor import DtsPreprocessor
from converter.dts.parser import DtsParser
from converter.dts.extractor import KeymapExtractor
from converter.transformer.kanata_transformer import KanataTransformer


def measure_time(func, *args, **kwargs):
    """Measure the execution time of a function."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return result, end_time - start_time


@pytest.fixture
def sample_keymap_path():
    """Path to a sample keymap file for performance testing."""
    return str(Path(__file__).parent.parent / "fixtures" / "dts" / "complex_keymap.zmk")


def test_preprocessor_performance(sample_keymap_path):
    """Test the performance of the preprocessor."""
    preprocessor = DtsPreprocessor()

    # Run multiple times to get stable measurements
    times = []
    for _ in range(10):
        _, duration = measure_time(preprocessor.preprocess, sample_keymap_path)
        times.append(duration)

    # Calculate statistics
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    # Log results
    print("\nPreprocessor Performance:")
    print(f"Mean time: {mean_time:.4f} seconds")
    print(f"Standard deviation: {std_dev:.4f} seconds")

    # Assert reasonable performance
    assert mean_time < 0.5  # Should process in under 500ms


def test_parser_performance(sample_keymap_path):
    """Test the performance of the parser."""
    preprocessor = DtsPreprocessor()
    parser = DtsParser()

    # Preprocess once
    content = preprocessor.preprocess(sample_keymap_path)

    # Run multiple times to get stable measurements
    times = []
    for _ in range(10):
        _, duration = measure_time(parser.parse, content)
        times.append(duration)

    # Calculate statistics
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    # Log results
    print("\nParser Performance:")
    print(f"Mean time: {mean_time:.4f} seconds")
    print(f"Standard deviation: {std_dev:.4f} seconds")

    # Assert reasonable performance
    assert mean_time < 0.1  # Should parse in under 100ms


def test_extractor_performance(sample_keymap_path):
    """Test the performance of the extractor."""
    preprocessor = DtsPreprocessor()
    parser = DtsParser()
    extractor = KeymapExtractor()

    # Preprocess and parse once
    content = preprocessor.preprocess(sample_keymap_path)
    ast = parser.parse(content)

    # Run multiple times to get stable measurements
    times = []
    for _ in range(10):
        _, duration = measure_time(extractor.extract, ast)
        times.append(duration)

    # Calculate statistics
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    # Log results
    print("\nExtractor Performance:")
    print(f"Mean time: {mean_time:.4f} seconds")
    print(f"Standard deviation: {std_dev:.4f} seconds")

    # Assert reasonable performance
    assert mean_time < 0.1  # Should extract in under 100ms


def test_full_pipeline_performance(sample_keymap_path):
    """Test the performance of the full conversion pipeline."""
    preprocessor = DtsPreprocessor()
    parser = DtsParser()
    extractor = KeymapExtractor()
    transformer = KanataTransformer()

    def run_pipeline():
        content = preprocessor.preprocess(sample_keymap_path)
        ast = parser.parse(content)
        config = extractor.extract(ast)
        return transformer.transform(config)

    # Run multiple times to get stable measurements
    times = []
    for _ in range(10):
        _, duration = measure_time(run_pipeline)
        times.append(duration)

    # Calculate statistics
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    # Log results
    print("\nFull Pipeline Performance:")
    print(f"Mean time: {mean_time:.4f} seconds")
    print(f"Standard deviation: {std_dev:.4f} seconds")

    # Assert reasonable performance
    assert mean_time < 1.0  # Should complete in under 1 second
