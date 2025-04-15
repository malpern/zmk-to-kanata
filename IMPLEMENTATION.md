# ZMK to Kanata Converter Implementation Plan

This document outlines our plan to overhaul the ZMK to Kanata converter, eliminating the Ben Vallack workaround and fixing underlying parser and transformer issues.

## Project Goals

1. Create a unified conversion pipeline that can handle all ZMK configurations including Ben Vallack's
2. Standardize output format following Kanata's Lisp-like syntax
3. Improve error handling and validation throughout the codebase
4. Align tests with implementation
5. Remove the need for special case workarounds

## Phase 1: Assessment and Setup

- [x] Identify key divergences between tests and implementation (sticky key transformer issues)
- [x] Align sticky key transformer tests with implementation
- [x] Review Ben Vallack's ZMK configuration format to identify parser failure points
  - Complex nested behaviors need special handling (homerow mods, tap-dance)
  - Custom behavior definitions with non-standard declarations
  - Nested C-style syntax with parentheses needs recursive parsing
  - Multiple arguments to behaviors and modifiers
- [x] Document standard output format for all behavior transformers
  - Sticky key: `(sticky-key key)`
  - Hold-tap: `(tap-hold timeout timeout-msecs tap-binding hold-binding)`
  - Layer toggle: `(layer-toggle layer-num)`
- [x] Create unit tests for Ben Vallack's ZMK configuration format
- [x] Design token-based parsing strategy for ZMK
  - [x] Implement lexer class to tokenize ZMK files
  - [x] Create lexer unit tests
  - [ ] Design AST data structures for ZMK configuration

## Phase 2: Parser Refactoring

- [x] Implement new token-based lexer for ZMK configuration files
- [ ] Create recursive parser for nested modifier combinations
- [ ] Implement ability to parse and handle custom behaviors in ZMK
- [ ] Create binding parser that properly handles complex combinations
- [ ] Add robust error recovery mechanisms
- [ ] Implement layer and keymap parsing
- [ ] Add support for parenthesized expressions for modifiers
- [ ] Create comprehensive test suite for parser edge cases

## Phase 3: Transformer Standardization

- [ ] Update all transformers to follow standardized output format
- [ ] Ensure consistent structure for all transformers
- [ ] Implement proper handling of nested bindings
- [ ] Fix ZMK to Kanata type mapping
- [ ] Add validation for all transformer outputs

## Phase 4: Error Handling & Recovery

- [ ] Implement robust error recovery for parsing failures
- [ ] Add detailed error messages with line numbers and context
- [ ] Create validation for all input and output types
- [ ] Add fallback mechanisms for unknown bindings
- [ ] Implement logging and warning systems for partial conversions

## Phase 5: Integration & Testing

- [ ] Consolidate conversion pipeline into a single system
- [ ] Remove special case handling and workarounds
- [ ] Integrate the new parser with existing transformers
- [ ] Create end-to-end tests for complex real-world configurations
- [ ] Test with Ben Vallack's configuration
- [ ] Benchmark performance with large configuration files

## Phase 6: Documentation & Cleanup

- [ ] Update documentation to reflect new parsing approach
- [ ] Add examples for common conversion cases
- [ ] Cleanup deprecated code
- [ ] Ensure consistent coding style
- [ ] Final refactoring and optimization pass

## Current Progress

The lexer component is now complete with robust tokenization capabilities:
- Token types for all ZMK syntax elements
- Source location tracking for precise error reporting
- Comprehensive test suite for all token types
- Proper handling of whitespace, comments, and structural elements
- Support for keywords, identifiers, numbers, and strings

Next steps:
1. Design and implement the AST (Abstract Syntax Tree) data structures for ZMK
2. Implement the recursive parser using the token stream from the lexer
3. Create specialized parsers for bindings, behaviors, and keymap sections

## Progress Tracking

| Phase | Component | Status | Notes |
|-------|-----------|--------|-------|
| 1 | Identify key divergences | Complete | Sticky key syntax differences identified |
| 1 | Align sticky key tests | Complete | Updated tests to match implementation |
| 1 | Review Ben Vallack config | Complete | Identified key parsing challenges (see below) |
| 1 | Analyze macro parser | Complete | Identified critical issues (see below) |
| 1 | Document transformer formats | Complete | Defined standard formats for all transformers (see below) |
| 1 | Create Ben Vallack tests | Complete | Created tests for parsing Ben Vallack's config features |
| 2 | ZMK Parser Overhaul | In Progress | Starting with token-based parser architecture |
| 2 | Macro Parser Refactoring | Not Started | |
| 2 | Binding Parser Improvements | Not Started | |
| 3 | Standardize Transformer Output | Not Started | |
| 3 | Behavior Transformers | Not Started | |
| 4 | Implement Error Recovery | Not Started | |
| 4 | Validation Improvements | Not Started | |
| 5 | Unified Conversion Pipeline | Not Started | |
| 5 | Test Alignment | Not Started | |
| 6 | Documentation | Not Started | |
| 6 | Code Cleanup | Not Started | |

## Key Issues & Decisions

### Parser Issues
- Macro parser needs significant refactoring (marked with skip in tests)
- ZMK parser fails on nested layers ("Nested layers are not supported")
- Binding parser has issues with nested binding formats

### Transformer Inconsistencies
- Different formats used by different transformers (e.g., `@layer1` vs `(layer-while-held 1)`)
- Macro transformer output doesn't match expected format
- Inconsistent handling of empty bindings

### Error Handling
- Inconsistent error recovery strategies
- Missing error context (line numbers, file positions)
- Unclear error messages

### Ben Vallack Config Parsing Challenges
After reviewing Ben Vallack's ZMK configuration, we've identified these specific parsing challenges:

1. **Custom behavior definitions:**
   - Custom homerow mods: `hm: homerow_mods`
   - Custom shift behavior: `hs: homerow_shifts`
   - Custom tapdance: `td: tapdance`

2. **Complex binding patterns:**
   - Homerow mods with multiple arguments: `&hm LCTL S`
   - Tap-dance with multiple keys: `&td EXCL DOT`
   - Mod-tap with complex modifiers: `&mt LC(LS(LALT)) SPC`

3. **Nested modifier combinations:**
   - Control+Shift+Alt: `LC(LS(LALT))`
   - Alt+Shift+RightBracket: `LA(LS(RBKT))`

4. **Layer transitions:**
   - Direct layer switching: `&to 0`, `&to 2`

5. **Non-standard key references:**
   - At sign: `ATSN` (instead of standard AT)
   - Custom symbols and references

### Macro Parser Issues
After analyzing the macro parser code, we've identified these critical issues that require refactoring:

1. **State Management Problems:**
   - Inconsistent state transitions between parsing blocks, macros, and bindings
   - Lack of proper nesting validation
   - Missing state cleanup after errors

2. **Parameter Parsing Flaws:**
   - Simplistic string splitting fails on complex parameters
   - Particularly problematic with nested commands (line 80: warning about skipping invalid macro steps)
   - Cannot properly handle nested &kp commands inside macro_tap/press/release

3. **Line-by-Line Processing Limitations:**
   - Current approach cannot handle macro definitions spanning multiple lines with complex syntax
   - No lookahead/lookbehind for context-aware parsing
   - Reliance on line format rather than token-based parsing

4. **Error Handling Weaknesses:**
   - Inconsistent error reporting
   - Missing contextual information for error location
   - Insufficient recovery mechanics

5. **Architectural Issues:**
   - Mixing of parsing macro *definitions* with parsing macro *usages* in bindings
   - Multiple unclear responsibility boundaries
   - Commenting out of important methods suggests unclear architecture

### Standardized Transformer Output Formats
Based on our analysis of the current code, we've defined these standard formats for all transformers:

1. **Sticky Key Format:**
   - Standard Format: `(sticky-key key)`
   - Examples: 
     - `(sticky-key lsft)` for shift
     - `(sticky-key _)` for empty key
     - `(sticky-key <invalid>)` for invalid key

2. **Hold-Tap Format:**
   - Mod-Tap: `(tap-hold timeout timeout key modifier)`
     - Example: `(tap-hold 200 200 a lsft)` for a/shift
   - Layer-Tap: `(layer-while-held layer key)`
     - Example: `(layer-while-held 1 a)` for layer 1 on hold, 'a' on tap

3. **Layer Format:**
   - Layer Definition: `(deflayer name key1 key2 key3...)`
   - Layer Reference: `(layer-while-held layer)`
   - Transparent Key: `_` (underscore)

4. **Macro Format:**
   - Macro Definition: `(defmacro name key1 key2...)`
   - Macro Usage: `(macro key1 key2...)`
   - Timed Commands: `(macro key1 (wait 30) key2)`

5. **Key Sequence Format:**
   - Standard Format: `(chord key1 key2...)`
   - Example: `(chord lsft a)` for shift+a

6. **Homerow Mods Format:**
   - Standard Format: `(tap-hold timeout timeout key modifier)`
   - Example: `(tap-hold 200 200 s lctl)` for s/ctrl on home row

7. **Empty/Invalid Key Handling:**
   - Empty: `_` (underscore)
   - Invalid: Return the key as-is with proper error logging

## Parser Refactoring Approach

We'll approach the parser refactoring systematically, using a new token-based architecture rather than line-by-line processing:

1. **Tokenization Phase:**
   - Create lexer to convert input stream into tokens
   - Define token types for all ZMK syntax components
   - Add source location tracking for better error reporting

2. **Parsing Phase:**
   - Implement recursive descent parser
   - Use context-aware state management
   - Create parsers for specific constructs (behaviors, bindings, layers)

3. **Validation Phase:**
   - Check cross-references between layers and behaviors
   - Validate binding parameters
   - Verify consistency across the configuration

4. **Error Recovery:**
   - Synchronize on structure boundaries
   - Continue parsing after errors when possible
   - Collect all errors rather than failing on first error

We'll implement these components one at a time, starting with a basic token lexer and parser for the ZMK file structure. Each component will have focused unit tests to ensure it handles the specific challenges we've identified.

## Next Steps

1. ~~Analyze Ben Vallack's ZMK configuration to identify specific parser issues~~ (Complete)
2. ~~Analyze the macro parser issues~~ (Complete)
3. ~~Document expected output formats for all transformer types~~ (Complete)
4. ~~Create unit tests for Ben Vallack's config format~~ (Complete)
5. Begin implementing the new ZMK parser architecture with token-based approach 