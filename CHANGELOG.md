# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-07-15

### Added
- Complete DTS-based parsing implementation
- Built-in ZMK header files:
  - `dt-bindings/zmk/matrix_transform.h`
  - `dt-bindings/zmk/keys.h`
  - `dt-bindings/zmk/behaviors.h`
- New AST-based parsing pipeline
- Comprehensive behavior transformers
- Cross-platform support for preprocessing
- Automatic matrix size detection
- Enhanced error messages with file/line context

### Changed
- Complete refactor to use DTS parsing
- Improved hold-tap configuration handling
- Updated layer behavior syntax
- Enhanced macro definition structure
- Standardized code formatting with Black
- Fixed all linter issues with Ruff

### Removed
- Old regex-based parsing system
- Obsolete test files
- Legacy parser implementations
- Deprecated code and documentation

### Fixed
- Include path resolution
- Hold-tap behavior transformation
- Layer switching syntax
- Macro sequence handling
- Test coverage and organization

## [1.0.0] - 2025-04-15

Initial release of the ZMK to Kanata converter.

### Features
- Basic ZMK keymap conversion
- Layer support
- Hold-tap behaviors
- Macro support
- Basic error handling

## [Unreleased]
- Kanata output now maps ZMK layer name `default_layer` to `default` for improved readability and Kanata compatibility.
- Introduced a manual review process for output validation. Findings are tracked in `MANUAL_REVIEW.md`. 