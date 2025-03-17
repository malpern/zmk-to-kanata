# Key Mapping and Validation

This document describes how keys are mapped and validated in the ZMK to Kanata converter.

## Key Categories

Keys are organized into the following categories:

- **Letters**: A-Z
- **Numbers**: N0-N9 (or just 0-9)
- **Function Keys**: F1-F24
- **Navigation Keys**: LEFT, RIGHT, UP, DOWN, HOME, END, PG_UP, PG_DN, INS, DEL
- **Editing Keys**: ENTER/RET, ESC, BSPC, DEL, TAB, SPACE/SPC, CAPS
- **Modifier Keys**: LSHIFT, RSHIFT, LCTRL, RCTRL, LALT, RALT, LGUI/LWIN, RGUI/RWIN
- **Punctuation Keys**: GRAVE, MINUS, EQUAL, LBKT, RBKT, BSLH, SEMI, APOS, COMMA, DOT, FSLH
- **Symbol Keys**: EXCL, AT, HASH, DLLR, PRCNT, CARET, AMPS, STAR, LPAR, RPAR, PLUS, UNDER, PIPE, TILDE
- **Media Keys**: C_MUTE, C_VOL_UP, C_VOL_DN, C_PP, C_NEXT, C_PREV, C_STOP, C_EJECT
- **Numpad Keys**: KP_N0-KP_N9, KP_SLASH, KP_MULTIPLY, KP_MINUS, KP_PLUS, KP_ENTER, KP_DOT
- **International Keys**: INT1-INT9
- **Language Keys**: LANG1-LANG9

## Special Keys

- **NONE**: No-op key (does nothing)
- **TRANS**: Transparent key (passes through to lower layer)

## Layer Keys

Layer keys use the following format:
- `mo <layer>`: Momentary layer switch (active while held)
- `to <layer>`: To layer (switches to layer)

Layer numbers must be non-negative integers.

## Key Validation

All keys are validated before being converted to Kanata format. The validation ensures:

1. The key is not empty
2. The key belongs to a known category or is a special key
3. Layer numbers are valid
4. Function key numbers are within range (1-24)

Invalid keys will raise a `KeyValidationError` with a descriptive message.

## ZMK to Kanata Conversion

Keys are converted to Kanata format according to these rules:

1. Special keys:
   - `TRANS` → `_`
   - `NONE` → `none`

2. Layer keys:
   - `mo 0` → `(layer-while-held 0)`
   - `to 1` → `(layer-switch 1)`

3. Modifier keys:
   - `LSHIFT` → `lsft`
   - `RCTRL` → `rctl`
   - `LGUI/LWIN` → `lmet`
   - etc.

4. Regular keys:
   - Letters are converted to lowercase
   - Numbers have the 'N' prefix removed
   - Function keys are converted to lowercase

## Best Practices

1. Use consistent key names within your keymap
2. Prefer standard key names over aliases
3. Use layer numbers sequentially starting from 0
4. Test key combinations before deploying
5. Handle validation errors gracefully in your application

## Error Handling

The key validator will raise a `KeyValidationError` when:

1. An empty key is provided
2. An unknown key is used
3. A layer number is invalid
4. A function key number is out of range
5. A key format is incorrect

Always catch and handle these errors appropriately in your application. 