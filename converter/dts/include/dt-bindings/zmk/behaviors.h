/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

/* Basic behaviors */
#define &kp 0x01
#define &mt 0x02
#define &lt 0x03
#define &mo 0x04
#define &to 0x05
#define &tog 0x06
#define &sk 0x07
#define &trans 0x08
#define &macro 0x09

/* Hold-tap configuration */
#define HOLD_TAP_FLAVOR_HOLD_PREFERRED 0
#define HOLD_TAP_FLAVOR_BALANCED 1
#define HOLD_TAP_FLAVOR_TAP_PREFERRED 2
#define HOLD_TAP_FLAVOR_TAP_UNLESS_INTERRUPTED 3

/* Timing parameters */
#define TAPPING_TERM_MS 200
#define QUICK_TAP_MS 125
#define GLOBAL_QUICK_TAP_MS 150

/* Layer behavior parameters */
#define DEFAULT_LAYER 0
#define MOMENTARY_LAYER 1
#define TOGGLE_LAYER 2 