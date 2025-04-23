/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

/**
 * @brief Macro for defining a matrix transform entry
 * @param row Row number
 * @param col Column number
 */
#define RC(row, col) ((row) << 8 | (col))
#define MATRIX_ROW(row) ((row) << 8)
#define MATRIX_COL(col) (col)
#define GET_ROW(matrix_index) ((matrix_index) >> 8)
#define GET_COL(matrix_index) ((matrix_index) & 0xFF) 