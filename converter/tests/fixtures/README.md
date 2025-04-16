# Test Fixtures

This directory contains test fixtures used for testing the ZMK to Kanata converter.

## Directory Structure

- `zmk/`: Contains ZMK keymap configuration files (`.dtsi`)
  - Used as input files for testing the converter
  - Includes various test cases and edge cases
  - Named with pattern `testN.dtsi` where N is a number

- `kanata/`: Contains Kanata configuration files (`.kbd`)
  - Used as expected output files for testing the converter
  - Corresponds to the ZMK input files
  - Named with pattern `testN.kbd` where N is a number

## Usage

These files are primarily used in end-to-end tests to verify the converter's functionality. While most tests create temporary files dynamically, these fixtures can be used for:

1. Manual testing and debugging
2. Complex test cases that are better maintained as separate files
3. Regression testing with real-world examples
4. Documentation of supported features and edge cases
