import pytest
from converter.parser.zmk_parser_new import ZMKParserNew, ParseError
from converter.parser.zmk_ast import (
    ZMKDocument,
    ZMKBehaviorsBlock,
    ZMKBehaviorDefinition,
    ZMKParameter,
    ZMKKeymapBlock,
    ZMKLayerDefinition,
    ZMKBinding,
    ZMKBindingParameter,
    ZMKModifierExpression,
    ZMKMacrosBlock,
    ZMKMacroDefinition,
    ZMKMacroStep,
    ZMKCombosBlock,
    ZMKComboDefinition,
    ZMKConditionalLayersBlock,
    ZMKConditionalLayerDefinition,
)


class TestZMKParserNew:
    """Tests for the ZMKParserNew class."""

    # --- Recreated Tests Start ---
    def test_parse_empty_document(self):
        """Test parsing the simplest valid ZMK structure: / { };"""
        source = "/ { };"
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert isinstance(document, ZMKDocument)
        assert document.behaviors is None
        assert document.keymap is None
        assert document.macros is None
        assert document.combos is None
        assert document.conditional_layers is None
        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

    def test_parse_simple_behaviors(self):
        """Test parsing a simple behaviors block with one definition."""
        source = """
        / {
            behaviors {
                kp: key_press {
                    bindings = <&kp>; // Example simplified param for testing
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.behaviors is not None
        assert isinstance(document.behaviors, ZMKBehaviorsBlock)
        assert "kp" in document.behaviors.behaviors

        behavior = document.behaviors.behaviors["kp"]
        assert isinstance(behavior, ZMKBehaviorDefinition)
        assert behavior.name == "kp"
        assert behavior.behavior_type == "key_press"
        assert len(behavior.parameters) == 1

        param = behavior.parameters[0]
        assert isinstance(param, ZMKParameter)
        assert param.name == "bindings"
        # Note: _parse_simple_angle_bracket_parameter returns raw string
        assert param.value == "<&kp>"

    def test_parse_simple_keymap(self):
        """Test parsing a simple keymap block with one layer and basic bindings."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                base_layer {
                    bindings = <&kp A &kp B &kp C>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.keymap is not None
        assert isinstance(document.keymap, ZMKKeymapBlock)
        assert "base_layer" in document.keymap.layers

        layer = document.keymap.layers["base_layer"]
        assert isinstance(layer, ZMKLayerDefinition)
        assert layer.name == "base_layer"
        assert len(layer.bindings) == 3
        assert layer.bindings[0].behavior == "kp"
        assert layer.bindings[0].params[0].value == "A"
        assert layer.bindings[2].behavior == "kp"
        assert layer.bindings[2].params[0].value == "C"

    def test_parse_simple_macros(self):
        """Test parsing a simple macros block with label, compatible, and steps."""
        source = """
        / {
            macros {
                my_macro: macro {
                    label = "MY_MACRO_LABEL";
                    compatible = "zmk,behavior-macro";
                    bindings = <&kp A &macro_tap B>; // Note: param parsing is basic
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.macros is not None
        assert isinstance(document.macros, ZMKMacrosBlock)
        assert "my_macro" in document.macros.macros

        macro = document.macros.macros["my_macro"]
        assert isinstance(macro, ZMKMacroDefinition)
        assert macro.name == "my_macro"
        assert macro.label == "MY_MACRO_LABEL"
        assert macro.compatible == "zmk,behavior-macro"
        assert len(macro.steps) == 2
        assert macro.steps[0].action == "kp"
        assert macro.steps[0].param == "A"
        assert macro.steps[1].action == "macro_tap"
        assert macro.steps[1].param == "B"  # Basic param parsing check

    def test_parse_simple_combos(self):
        """Test parsing a simple combos block with one combo definition."""
        source = """
        / {
            combos {
                compatible = "zmk,combos";
                my_combo {
                    timeout-ms = <50>;
                    key-positions = <0 1>;
                    bindings = <&kp ENTER>;
                    layers = <0 2>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.combos is not None
        assert isinstance(document.combos, ZMKCombosBlock)
        assert "my_combo" in document.combos.combos

        combo = document.combos.combos["my_combo"]
        assert isinstance(combo, ZMKComboDefinition)
        assert combo.name == "my_combo"
        assert combo.timeout_ms == 50
        assert combo.key_positions == [0, 1]
        assert len(combo.bindings) == 1
        assert combo.bindings[0].behavior == "kp"
        assert combo.bindings[0].params[0].value == "ENTER"
        assert combo.layers == [0, 2]

    # --- Recreated Tests End ---

    # Assuming this was the last correctly parsed method before the break
    def test_parse_simple_conditional_layers(self):
        """Test parsing a simple conditional_layers block."""
        # Minimal content needed for context, original was likely more complete
        source = """
        / {
            conditional_layers {
                compatible = "zmk,conditional-layers";
                tri_layer {
                    if-layers = <1 2>;
                    then-layer = <3>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)
        from converter.parser.zmk_ast import (
            ZMKConditionalLayersBlock,
        )  # Keep import local if needed

        assert not parser.errors
        assert document.conditional_layers is not None
        assert "tri_layer" in document.conditional_layers.conditional_layers
        cond_layer = document.conditional_layers.conditional_layers["tri_layer"]
        assert cond_layer.if_layers == [1, 2]
        assert cond_layer.then_layer == 3

    def test_parse_keymap_multiple_layers(self):
        """Test parsing a keymap block with multiple layer definitions."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                base_layer {
                    bindings = <&kp A &kp B>;
                };
                nav_layer {
                    bindings = <&kp UP &kp DOWN>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.keymap is not None
        assert isinstance(document.keymap, ZMKKeymapBlock)
        assert len(document.keymap.layers) == 2
        assert "base_layer" in document.keymap.layers
        assert "nav_layer" in document.keymap.layers

        base_layer = document.keymap.layers["base_layer"]
        assert isinstance(base_layer, ZMKLayerDefinition)
        assert len(base_layer.bindings) == 2
        assert base_layer.bindings[0].behavior == "kp"
        assert base_layer.bindings[0].params[0].value == "A"

        nav_layer = document.keymap.layers["nav_layer"]
        assert isinstance(nav_layer, ZMKLayerDefinition)
        assert len(nav_layer.bindings) == 2
        assert nav_layer.bindings[0].behavior == "kp"
        assert nav_layer.bindings[0].params[0].value == "UP"

    def test_parse_keymap_complex_bindings(self):
        """Test parsing keymap bindings with mod-tap and modifier functions."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                complex_layer {
                    bindings = <&mt LCTL A  &kp LC(A) &kp RA(LS(N))>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.keymap is not None
        assert "complex_layer" in document.keymap.layers
        layer = document.keymap.layers["complex_layer"]
        assert len(layer.bindings) == 3

        # Test &mt LCTL A
        binding_mt = layer.bindings[0]
        assert binding_mt.behavior == "mt"
        assert len(binding_mt.params) == 2
        assert binding_mt.params[0].value == "LCTL"
        assert binding_mt.params[1].value == "A"

        # Test &kp LC(A)
        binding_lc = layer.bindings[1]
        assert binding_lc.behavior == "kp"
        assert len(binding_lc.params) == 1
        param_lc = binding_lc.params[0]
        assert isinstance(param_lc.value, ZMKModifierExpression)
        assert param_lc.value.modifier == "LC"
        assert len(param_lc.value.params) == 1
        assert param_lc.value.params[0] == "A"

        # Test &kp RA(LS(N))
        binding_ra_ls = layer.bindings[2]
        assert binding_ra_ls.behavior == "kp"
        assert len(binding_ra_ls.params) == 1
        param_ra_ls = binding_ra_ls.params[0]
        assert isinstance(param_ra_ls.value, ZMKModifierExpression)
        assert param_ra_ls.value.modifier == "RA"
        assert len(param_ra_ls.value.params) == 1
        nested_ls = param_ra_ls.value.params[0]
        assert isinstance(nested_ls, ZMKModifierExpression)
        assert nested_ls.modifier == "LS"
        assert len(nested_ls.params) == 1
        assert nested_ls.params[0] == "N"

    def test_parse_custom_behavior(self):
        """Test parsing a custom behavior definition like hm: homerow_mods {...}."""
        source = """
        / {
            behaviors {
                hm: homerow_mods {
                    tapping-term-ms = <200>;
                    bindings = <&kp A &kp B>; // Include bindings param
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.behaviors is not None
        assert "hm" in document.behaviors.behaviors

        behavior = document.behaviors.behaviors["hm"]
        assert isinstance(behavior, ZMKBehaviorDefinition)
        assert behavior.name == "hm"
        assert behavior.behavior_type == "homerow_mods"
        assert len(behavior.parameters) == 2

        param1 = behavior.parameters[0]
        assert param1.name == "tapping-term-ms"
        assert (
            param1.value == "<200>"
        )  # _parse_simple_angle_bracket_parameter returns raw string

        param2 = behavior.parameters[1]
        assert param2.name == "bindings"
        assert param2.value == "<&kp A &kp B>"

    def test_parse_syntax_errors(self):
        """Test parsing input with common syntax errors."""
        # Error 1: Missing semicolon after behavior parameter
        source_missing_semicolon = """
        / {
            behaviors {
                kp: key_press {
                    bindings = <&kp> // Missing semicolon here
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source_missing_semicolon)

        assert (
            len(parser.errors) >= 1
        ), "Expected at least one parse error for missing semicolon"
        # Check the first error message specifically
        first_error = parser.errors[0]
        assert isinstance(first_error, ParseError)
        assert "Expected SEMICOLON, got CLOSE_BRACE" in first_error.message
        assert first_error.location is not None
        # Location check depends heavily on exact token/line numbers,
        # might need adjustment based on lexer details. Example:
        # assert first_error.location.line == 6

        # Error 2: Missing closing brace (Example - more tests can be added)
        source_missing_brace = """
        / {
            behaviors {
                kp: key_press {
                    bindings = <&kp>;
                }; // Missing closing brace for behaviors block
            // Missing closing brace for root block
        """
        parser.errors = []  # Reset errors for next parse
        parser.parse(source_missing_brace)

        assert len(parser.errors) >= 1, "Expected errors for missing closing braces"
        # Check for EOF or unexpected token error
        assert any(
            "Expected CLOSE_BRACE" in e.message or "Unexpected end of file" in e.message
            for e in parser.errors
        )

    def test_parse_comments_whitespace(self):
        """Test parsing input with comments and varied whitespace."""
        source = """
        / { // Start root
            /* Multi-line
               comment */
            keymap { 
                compatible = "zmk,keymap"; // Compatible string
                
                layer_with_space_name { // Layer definition
                    bindings = < &kp A 
                                 &kp B // Another comment 
                               >; // End bindings
                }; /* End layer */
            } 
        } // End root
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert not parser.errors, f"Parser errors: {parser.errors}"
        assert not parser.warnings, f"Parser warnings: {parser.warnings}"

        assert document.keymap is not None
        assert "layer_with_space_name" in document.keymap.layers
        layer = document.keymap.layers["layer_with_space_name"]
        assert len(layer.bindings) == 2
        assert layer.bindings[0].behavior == "kp"
        assert layer.bindings[0].params[0].value == "A"
        assert layer.bindings[1].behavior == "kp"
        assert layer.bindings[1].params[0].value == "B"

    # TODO: Add tests for edge cases (comments, whitespace variations)
