# ZMK to Kanata Test Structure Improvements

## Current Issues

1. **Disorganized Test Structure**
   - Mixed test types (unit, integration, e2e)
   - Overlapping test coverage
   - Unclear test boundaries
   - Empty/minimal test files

2. **Coverage Gaps**
   - Limited error handling tests
   - Incomplete state machine transition testing
   - Missing edge cases for layer interactions
   - Insufficient macro timing tests

3. **Test Isolation Problems**
   - Potential shared state issues
   - Unclear separation between parser/transformer tests
   - Possible test interdependencies

4. **Missing Infrastructure**
   - Limited test fixtures
   - No common test utilities
   - Inconsistent mocking strategy

## Implementation Plan

### Phase 1: Test Organization (Week 1)

1. **Create New Directory Structure**
   ```
   converter/tests/
   ├── unit/
   │   ├── parser/
   │   │   ├── test_layer_parser.py
   │   │   ├── test_macro_parser.py
   │   │   └── test_taphold_parser.py
   │   ├── transformer/
   │   │   ├── test_layer_transformer.py
   │   │   └── test_macro_transformer.py
   │   └── behaviors/
   │       └── test_key_behaviors.py
   ├── integration/
   │   ├── parser_transformer/
   │   │   ├── test_layer_integration.py
   │   │   └── test_macro_integration.py
   │   └── end_to_end/
   │       ├── test_basic_keymap.py
   │       └── test_complex_keymap.py
   ├── fixtures/
   │   ├── keymap_fixtures.py
   │   ├── parser_fixtures.py
   │   └── transformer_fixtures.py
   └── utils/
       ├── test_helpers.py
       └── mock_factories.py
   ```

2. **Migrate Existing Tests**
   - [ ] Move unit tests to appropriate directories
   - [ ] Consolidate duplicate test files
   - [ ] Remove empty test files
   - [ ] Update import paths

### Phase 2: Test Infrastructure (Week 2)

1. **Create Test Fixtures**
   ```python
   # fixtures/parser_fixtures.py
   @pytest.fixture
   def basic_layer_parser():
       return LayerParser(clean_state=True)

   @pytest.fixture
   def complex_keymap():
       return load_test_keymap('complex_keymap.kbd')
   ```

2. **Implement Test Utilities**
   - [ ] Parser state helpers
   - [ ] Keymap generators
   - [ ] Assertion helpers
   - [ ] Mock factories

3. **Add Common Test Patterns**
   - [ ] Standard setup/teardown
   - [ ] State verification
   - [ ] Error checking

### Phase 3: Coverage Improvements (Week 3)

1. **Error Handling Tests**
   - [ ] Invalid syntax cases
   - [ ] State transition errors
   - [ ] Resource handling errors
   - [ ] Recovery scenarios

2. **State Machine Testing**
   ```python
   @pytest.mark.parametrize("initial_state,input_token,expected_state", [
       (ParserState.IDLE, "layer", ParserState.LAYER_START),
       (ParserState.LAYER_START, "{", ParserState.IN_LAYER),
       # ... more state transitions
   ])
   def test_parser_state_transitions(initial_state, input_token, expected_state):
       parser = LayerParser()
       parser.state = initial_state
       parser.process_token(input_token)
       assert parser.state == expected_state
   ```

3. **Edge Cases**
   - [ ] Complex layer interactions
   - [ ] Nested macro definitions
   - [ ] Unicode handling
   - [ ] Resource limits

### Phase 4: Test Isolation (Week 4)

1. **State Management**
   - [ ] Implement parser reset mechanism
   - [ ] Clear shared resources between tests
   - [ ] Isolate file system operations

2. **Mock Strategy**
   - [ ] Define mockable interfaces
   - [ ] Create mock factories
   - [ ] Document mocking patterns

3. **Test Independence**
   - [ ] Remove test ordering dependencies
   - [ ] Isolate integration tests
   - [ ] Containerize e2e tests

## Success Metrics

1. **Coverage Goals**
   - 90% line coverage
   - 85% branch coverage
   - 100% coverage of error paths

2. **Test Quality**
   - No flaky tests
   - < 500ms per test
   - Clear failure messages

3. **Maintenance**
   - Documented test patterns
   - Automated test organization checks
   - Regular test cleanup tasks

## Next Steps

1. Begin with Phase 1 directory restructure
2. Create basic fixtures and utilities
3. Migrate existing tests to new structure
4. Add new test cases incrementally

## Notes

- Keep existing tests working during migration
- Document all test patterns and conventions
- Add CI checks for test organization
- Regular progress reviews and adjustments 