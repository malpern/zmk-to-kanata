import os
import subprocess
import difflib
import pytest

REAL_WORLD_DIR = "tests/fixtures/real_world"
GOLDEN_SUFFIX = ".golden.kanata"
KANATA_SUFFIX = ".out.kanata"


def zmk_files():
    """Yield all .keymap and .dtsi files in the real world test directory."""
    for fname in os.listdir(REAL_WORLD_DIR):
        if fname.endswith(".keymap") or fname.endswith(".dtsi"):
            yield os.path.join(REAL_WORLD_DIR, fname)


def find_kanata_outputs():
    for fname in os.listdir(REAL_WORLD_DIR):
        if fname.endswith(KANATA_SUFFIX):
            yield os.path.join(REAL_WORLD_DIR, fname)


@pytest.fixture(scope="module")
def generated_outputs(tmp_path_factory):
    """
    Generate Kanata outputs for all ZMK files in a temp directory.
    Returns a dict mapping input file to output file path.
    """
    tmp_path = tmp_path_factory.mktemp("kanata_regression")
    outputs = {}
    for zmk_file in zmk_files():
        out_file = tmp_path / (os.path.basename(zmk_file) + KANATA_SUFFIX)
        subprocess.run(
            [
                "python",
                "-m",
                "converter.main",
                zmk_file,
                "-o",
                str(out_file),
            ],
            check=True,
        )
        outputs[zmk_file] = out_file
    return outputs


@pytest.mark.parametrize("zmk_file", list(zmk_files()))
def test_golden_regression(zmk_file, generated_outputs):
    """
    Compare freshly generated output to golden file, if present.
    """
    out_file = generated_outputs[zmk_file]
    golden_file = zmk_file + GOLDEN_SUFFIX
    if not os.path.exists(golden_file):
        pytest.skip(f"No golden file for {zmk_file}")
    with open(out_file) as f1, open(golden_file) as f2:
        out_lines = f1.readlines()
        golden_lines = f2.readlines()
    diff = list(difflib.unified_diff(golden_lines, out_lines, lineterm=""))
    assert not diff, (
        f"Output differs from golden for {zmk_file}:\n" + "\n".join(diff)
    )


@pytest.mark.parametrize("out_file", list(find_kanata_outputs()))
def test_no_unsupported_features(out_file):
    with open(out_file) as f:
        for i, line in enumerate(f, 1):
            if line.strip().startswith("; unsupported:") or line.strip().startswith("; <err:"):
                pytest.fail(f"{out_file}:{i} contains unsupported feature: {line.strip()}")


@pytest.mark.parametrize("out_file", list(find_kanata_outputs()))
def test_no_long_lines_in_kanata_outputs(out_file):
    with open(out_file) as f:
        for i, line in enumerate(f, 1):
            assert len(line.rstrip("\n")) <= 79, f"{out_file}:{i} line too long"


@pytest.mark.parametrize("zmk_file", list(zmk_files()))
def test_no_unsupported_features(zmk_file, generated_outputs):
    """
    Fail if any line in the generated output contains an unsupported feature or error.
    """
    out_file = generated_outputs[zmk_file]
    with open(out_file) as f:
        for i, line in enumerate(f, 1):
            if (
                line.strip().startswith("; unsupported:")
                or line.strip().startswith("; <err:")
            ):
                pytest.fail(
                    f"{out_file}:{i} contains unsupported feature: "
                    f"{line.strip()}"
                )


@pytest.mark.parametrize("zmk_file", list(zmk_files()))
def test_no_long_lines_in_kanata_outputs(zmk_file, generated_outputs):
    """
    Fail if any line in the generated output exceeds 79 characters.
    """
    out_file = generated_outputs[zmk_file]
    with open(out_file) as f:
        for i, line in enumerate(f, 1):
            assert (
                len(line.rstrip("\n")) <= 79
            ), f"{out_file}:{i} line too long" 