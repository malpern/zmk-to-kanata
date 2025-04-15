"""Unit tests for the new ZMK parser."""

import pytest
from converter.parser.zmk_parser_new import ZMKParserNew
from converter.parser.zmk_lexer import ZMKLexer


class TestZMKParserNew:
    """Tests for the new ZMK parser."""

    def test_parse_empty_document(self):
        """Test parsing an empty ZMK document."""
        source = """
        / {
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.behaviors is None
        assert document.keymap is None
        assert document.macros is None
        assert document.combos is None
        assert document.conditional_layers is None

    def test_parse_minimal_behaviors_block(self):
        """Test parsing a minimal behaviors block."""
        source = """
        / {
            behaviors {
                hm: homerow_mods {
                    compatible = "zmk,behavior-hold-tap";
                    tapping-term-ms = <200>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.behaviors is not None
        assert len(document.behaviors.behaviors) == 1
        assert "hm" in document.behaviors.behaviors

        behavior = document.behaviors.behaviors["hm"]
        assert behavior.name == "hm"
        assert behavior.behavior_type == "homerow_mods"
        assert len(behavior.parameters) == 2

        # Check specific parameters
        param_dict = {p.name: p.value for p in behavior.parameters}
        assert param_dict["compatible"] == '"zmk,behavior-hold-tap"'
        assert param_dict["tapping-term-ms"] == "<200>"

    def test_parse_full_behaviors_block(self):
        """Test parsing a full behaviors block."""
        source = """
        / {
            behaviors {
                hm: homerow_mods {
                    compatible = "zmk,behavior-hold-tap";
                    label = "HOMEROW_MODS";
                    #binding-cells = <2>;
                    tapping-term-ms = <200>;
                    quick_tap_ms = <0>;
                    flavor = "tap-preferred";
                    bindings = <&kp>, <&kp>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.behaviors is not None
        assert len(document.behaviors.behaviors) == 1
        assert "hm" in document.behaviors.behaviors

        behavior = document.behaviors.behaviors["hm"]
        assert behavior.name == "hm"
        assert behavior.behavior_type == "homerow_mods"
        assert len(behavior.parameters) == 7

        # Check some specific parameters
        param_dict = {p.name: p.value for p in behavior.parameters}
        assert param_dict["compatible"] == '"zmk,behavior-hold-tap"'
        assert param_dict["label"] == '"HOMEROW_MODS"'
        assert param_dict["tapping-term-ms"] == "<200>"

    def test_parse_keymap_block(self):
        """Test parsing a keymap block."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                
                default_layer {
                    bindings = <
                        &kp TAB &kp Q &kp W &kp E &kp R &kp T
                        &kp A &kp S &kp D &kp F &kp G
                    >;
                };
                
                lower_layer {
                    bindings = <
                        &kp EXCL &kp AT &kp HASH &kp DLLR &kp PRCNT &kp CARET
                        &kp N1 &kp N2 &kp N3 &kp N4 &kp N5
                    >;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.keymap is not None
        assert len(document.keymap.layers) == 2
        assert "default_layer" in document.keymap.layers
        assert "lower_layer" in document.keymap.layers

        default_layer = document.keymap.layers["default_layer"]
        assert default_layer.name == "default_layer"
        assert len(default_layer.bindings) == 11

        assert default_layer.bindings[0].behavior == "kp"
        assert default_layer.bindings[0].params[0].value == "TAB"

        lower_layer = document.keymap.layers["lower_layer"]
        assert lower_layer.name == "lower_layer"
        assert len(lower_layer.bindings) == 11

        assert lower_layer.bindings[0].behavior == "kp"
        assert lower_layer.bindings[0].params[0].value == "EXCL"

    def test_parse_complex_binding(self):
        """Test parsing complex bindings with modifiers."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                
                default_layer {
                    bindings = <
                        &mt LCTRL ESC &kp Q
                        &kp LC(LS(LALT)) &mt LC(LS(LALT)) SPC
                    >;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.keymap is not None
        assert len(document.keymap.layers) == 1

        layer = document.keymap.layers["default_layer"]
        assert len(layer.bindings) == 4

        # Check mod-tap binding
        binding = layer.bindings[0]
        assert binding.behavior == "mt"
        assert len(binding.params) == 2
        assert binding.params[0].value == "LCTRL"
        assert binding.params[1].value == "ESC"

        # Check complex modifier binding
        binding = layer.bindings[2]
        assert binding.behavior == "kp"
        assert len(binding.params) == 1

        # First parameter should be a ZMKModifierExpression
        modifier = binding.params[0].value
        assert hasattr(modifier, "modifier")
        assert modifier.modifier == "LC"
        assert len(modifier.params) == 1

        # The nested parameter should also be a ZMKModifierExpression
        nested_mod = modifier.params[0]
        assert hasattr(nested_mod, "modifier")
        assert nested_mod.modifier == "LS"
        assert len(nested_mod.params) == 1
        assert nested_mod.params[0] == "LALT"

        # Check combined complex binding
        binding = layer.bindings[3]
        assert binding.behavior == "mt"
        assert len(binding.params) == 2

        # First parameter should be a ZMKModifierExpression
        modifier = binding.params[0].value
        assert hasattr(modifier, "modifier")
        assert modifier.modifier == "LC"
        assert len(modifier.params) == 1

        # The nested parameter should also be a ZMKModifierExpression
        nested_mod = modifier.params[0]
        assert hasattr(nested_mod, "modifier")
        assert nested_mod.modifier == "LS"
        assert len(nested_mod.params) == 1
        assert nested_mod.params[0] == "LALT"

        # The second parameter should be a simple string
        assert binding.params[1].value == "SPC"

    def test_parse_macros_block(self):
        """Test parsing a macros block."""
        source = """
        / {
            macros {
                zed_em_kay: macro {
                    label = "ZM_MACRO";
                    compatible = "zmk,behavior-macro";
                    #binding-cells = <0>;
                    bindings = <&kp Z &kp M &kp K>;
                };
                
                shift_macro: macro {
                    bindings = <&macro_press &kp LSHFT>, <&kp H &kp E &kp Y>, <&macro_release &kp LSHFT>;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.macros is not None
        assert len(document.macros.macros) == 2
        assert "zed_em_kay" in document.macros.macros
        assert "shift_macro" in document.macros.macros

        macro = document.macros.macros["zed_em_kay"]
        assert macro.name == "zed_em_kay"
        assert len(macro.steps) == 3
        assert macro.steps[0].action == "kp"
        assert macro.steps[0].param == "Z"

        macro = document.macros.macros["shift_macro"]
        assert macro.name == "shift_macro"
        assert len(macro.steps) == 5  # macro_press, H, E, Y, macro_release
        assert macro.steps[0].action == "macro_press"
        assert macro.steps[0].param == "LSHFT"
        assert macro.steps[4].action == "macro_release"
        assert macro.steps[4].param == "LSHFT"

    def test_parse_ben_vallack_style_binding(self):
        """Test parsing Ben Vallack style homerow mod bindings."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                
                default_layer {
                    bindings = <
                        &hm LCTL S &hm LALT R &td EXCL DOT &to 2
                    >;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.keymap is not None
        assert len(document.keymap.layers) == 1

        layer = document.keymap.layers["default_layer"]
        assert len(layer.bindings) == 4

        # Check homerow mod binding
        binding = layer.bindings[0]
        assert binding.behavior == "hm"
        assert len(binding.params) == 2
        assert binding.params[0].value == "LCTL"
        assert binding.params[1].value == "S"

        # Check tap-dance binding
        binding = layer.bindings[2]
        assert binding.behavior == "td"
        assert len(binding.params) == 2
        assert binding.params[0].value == "EXCL"
        assert binding.params[1].value == "DOT"

        # Check layer-to binding
        binding = layer.bindings[3]
        assert binding.behavior == "to"
        assert len(binding.params) == 1
        assert binding.params[0].value == "2"

    def test_error_recovery(self):
        """Test parser error recovery."""
        source = """
        / {
            behaviors {
                invalid_behavior: {  // Missing behavior type
                    compatible = "zmk,behavior-hold-tap";
                };
                
                valid_behavior: hold_tap {
                    compatible = "zmk,behavior-hold-tap";
                    tapping-term-ms = <200>;
                };
            };
            
            keymap {
                compatible = "zmk,keymap";
                
                default_layer {
                    bindings = <
                        &kp A &kp B
                    >;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        # Despite errors, we should still get a parsed document
        assert document is not None
        assert document.behaviors is not None
        assert document.keymap is not None

        # Check that we recovered and parsed the valid behavior
        assert "valid_behavior" in document.behaviors.behaviors

        # Check that we have at least one error
        assert len(parser.errors) > 0

    def test_empty_modifier_expressions(self):
        """Test parsing empty modifier expressions like LC()."""
        source = """
        / {
            keymap {
                compatible = "zmk,keymap";
                
                default_layer {
                    bindings = <
                        &kp LC() &kp LS(LBKT)
                    >;
                };
            };
        };
        """
        parser = ZMKParserNew()
        document = parser.parse(source)

        assert document is not None
        assert document.keymap is not None

        layer = document.keymap.layers["default_layer"]
        assert len(layer.bindings) == 2

        # Check empty modifier expression
        binding = layer.bindings[0]
        assert binding.behavior == "kp"
        assert len(binding.params) == 1

        modifier = binding.params[0].value
        assert hasattr(modifier, "modifier")
        assert modifier.modifier == "LC"
        assert len(modifier.params) == 0

        # Check non-empty modifier expression
        binding = layer.bindings[1]
        assert binding.behavior == "kp"
        assert len(binding.params) == 1

        modifier = binding.params[0].value
        assert hasattr(modifier, "modifier")
        assert modifier.modifier == "LS"
        assert len(modifier.params) == 1
        assert modifier.params[0] == "LBKT"
