#!/usr/bin/env python3
"""
Decode expected hex to matrix
"""
import numpy as np

# Expected (before logistic map)
expected_hex = "0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80"

def hex_to_bits(hex_string):
    hex_values = hex_string.split("0x")[1:]
    all_bits = []
    for i, hex_val in enumerate(hex_values):
        value = int(hex_val, 16)
        # Determine bits
        if i < len(hex_values) - 1:
            bits_in_chunk = 32
        else:
            bits_in_chunk = 21 * 21 - i * 32
        binary = format(value, f'0{bits_in_chunk}b')
        all_bits.extend([int(b) for b in binary])
    return all_bits

expected_bits = hex_to_bits(expected_hex)
expected_matrix = np.array(expected_bits[:441]).reshape(21, 21)

print("Expected Matrix (from hex)")
print("="*60)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

# Check position patterns
print("\n" + "="*60)
print("Position Pattern Analysis")
print("="*60)

# Top-left (should be at 0:8, 0:8)
print("\nTop-left (rows 0-7, cols 0-7):")
for i in range(8):
    for j in range(8):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

# Top-right (should be at 0:8, 14:21)
print("\nTop-right (rows 0-7, cols 14-20):")
for i in range(8):
    for j in range(14, 21):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

# Bottom-left (should be at 14:21, 0:8)
print("\nBottom-left (rows 14-20, cols 0-7):")
for i in range(14, 21):
    for j in range(8):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

# Check row 6 and column 6 (timing patterns)
print("\nTiming pattern (row 6, cols 8-13):")
for j in range(8, 14):
    print(f"Col {j}: {expected_matrix[6, j]}")

print("\nTiming pattern (col 6, rows 8-13):")
for i in range(8, 14):
    print(f"Row {i}: {expected_matrix[i, 6]}")
