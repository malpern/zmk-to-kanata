# ZMK to Kanata Converter Implementation Details

## Current Status (July 2025)

The converter has been completely refactored to use a robust DTS-based parsing approach. Current status:

- ✅ DTS parser implementation complete
- ✅ Local ZMK header files added
- ✅ All linter issues fixed
- ✅ Code formatting standardized with Black
- ✅ Documentation updated

## Architecture Overview

### 1. DTS Processing Pipeline

```
Input ZMK File
     ↓
DTS Preprocessor (cpp)
     ↓
DTS Parser (AST)
     ↓
Keymap Extractor
     ↓
Behavior Transformers
     ↓
Kanata Output
```

### 2. Key Components

1. **DTS Preprocessor** (`converter/dts/preprocessor.py`)
   - Handles C preprocessor integration
   - Manages include paths and header files
   - Preserves DTS directives during processing
   - Handles matrix size detection
   - Platform-specific command handling

2. **AST Implementation** (`converter/dts/ast.py`)
   - Clean node and property classes
   - Efficient label mapping
   - Reference resolution
   - Tree traversal utilities

3. **DTS Parser** (`converter/dts/parser.py`)
   - Tokenization and parsing
   - Property value handling
   - Node body parsing
   - Error recovery and reporting

4. **Behavior Transformers**
   - HoldTap transformer with flavor support
   - Layer transformer for switching behaviors
   - Macro transformer for key sequences
   - Sticky key transformer

## Implementation Details

### 1. DTS Preprocessing

The preprocessor handles ZMK files in multiple stages:
1. Directive preservation
2. C preprocessing
3. Directive restoration
4. Matrix transform handling

Key features:
- Built-in ZMK header files
- Cross-platform support
- Robust error handling
- Proper include path resolution

### 2. AST Structure

The AST is built using three main classes:
1. `DtsProperty`: Represents node properties
2. `DtsNode`: Represents tree nodes
3. `DtsRoot`: Manages the complete tree

Features:
- Efficient label mapping
- Reference resolution
- Tree traversal
- Property type handling

### 3. Behavior Handling

Each behavior type has a dedicated transformer:

1. **HoldTap Transformer**
   - Flavor mapping
   - Timing configuration
   - Advanced features (quick-tap, etc.)

2. **Layer Transformer**
   - Layer switching behaviors
   - Transparent key handling
   - Layer state management

3. **Macro Transformer**
   - Key sequence parsing
   - Timing control
   - Complex combinations

## Testing Strategy

1. **Unit Tests**
   - Parser component testing
   - AST validation
   - Transformer verification
   - Property handling

2. **Integration Tests**
   - End-to-end conversion
   - Real-world configurations
   - Error handling scenarios

3. **Performance Tests**
   - Large file handling
   - Memory usage
   - Processing speed

## Code Quality

1. **Linting and Formatting**
   - Black for code formatting
   - Ruff for linting
   - Type hints throughout
   - Comprehensive docstrings

2. **Error Handling**
   - Contextual error messages
   - Proper error propagation
   - Recovery mechanisms
   - Debug logging

## Future Improvements

1. **Performance Optimization**
   - Caching for repeated operations
   - Memory usage optimization
   - Parallel processing where applicable

2. **Feature Additions**
   - Support for more ZMK behaviors
   - Additional transformation options
   - Custom behavior definitions

3. **Documentation**
   - API reference documentation
   - More usage examples
   - Troubleshooting guide

## Progress Tracking

| Component                | Status    | Notes                                    |
|-------------------------|-----------|------------------------------------------|
| DTS Parser              | ✅ Complete| All tests passing                        |
| AST Implementation      | ✅ Complete| Clean and efficient                      |
| Preprocessor            | ✅ Complete| Cross-platform support working           |
| HoldTap Transformer     | ✅ Complete| All features implemented                 |
| Layer Transformer       | ✅ Complete| Switching behaviors working              |
| Macro Transformer       | ✅ Complete| Sequence handling working                |
| Documentation          | ✅ Complete| Updated for DTS approach                |
| Test Coverage          | ✅ Complete| All components tested                    |

## Next Steps

1. **Performance Optimization**
   - Profile large file processing
   - Identify bottlenecks
   - Implement optimizations

2. **Feature Expansion**
   - Additional ZMK behaviors
   - Custom behavior support
   - Advanced configuration options

3. **User Experience**
   - Improved error messages
   - Better debugging tools
   - More examples and guides