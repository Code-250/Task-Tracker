#!/usr/bin/env python3
"""
Visualize the bit differences between our output and expected
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np

# Our output (before logistic map)
our_hex = "0xfe07f4120xe0ae83750x75bbabaf0x5d41120b0xfabfc01e0x385120xc80483960x58b212070x25807f3a0xe0889170x5c00ba850x35d088e00xb645fd120x1a80"

# Expected (from spec's "before logistic map" example)
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

our_bits = hex_to_bits(our_hex)
expected_bits = hex_to_bits(expected_hex)

print(f"Our bits: {len(our_bits)}")
print(f"Expected bits: {len(expected_bits)}")

# Find differences
differences = []
for i in range(min(len(our_bits), len(expected_bits))):
    if our_bits[i] != expected_bits[i]:
        differences.append(i)

print(f"\nTotal differences: {len(differences)}")
print(f"First 20 differences at bit positions: {differences[:20]}")

# Convert to row,col positions
print("\nDifferences as (row, col) in 21x21 matrix:")
for i, bit_pos in enumerate(differences[:30]):
    row = bit_pos // 21
    col = bit_pos % 21
    print(f"  Bit {bit_pos}: row={row}, col={col}, our={our_bits[bit_pos]}, expected={expected_bits[bit_pos]}")

# Visualize both matrices
our_matrix = np.array(our_bits[:441]).reshape(21, 21)
expected_matrix = np.array(expected_bits[:441]).reshape(21, 21)
diff_matrix = np.array([1 if our_bits[i] != expected_bits[i] else 0 for i in range(441)]).reshape(21, 21)

print("\n" + "="*80)
print("OUR MATRIX")
print("="*80)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        print("█" if our_matrix[i, j] else " ", end="")
    print()

print("\n" + "="*80)
print("EXPECTED MATRIX")
print("="*80)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

print("\n" + "="*80)
print("DIFFERENCE MATRIX (X = different)")
print("="*80)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        if diff_matrix[i, j]:
            print("X", end="")
        elif our_matrix[i, j]:
            print("█", end="")
        else:
            print(" ", end="")
    print()

# Check if differences are in specific areas
position_pattern_diffs = 0
timing_pattern_diffs = 0
data_area_diffs = 0

for diff_pos in differences:
    row = diff_pos // 21
    col = diff_pos % 21

    # Check if in position patterns
    if ((row < 8 and col < 8) or (row < 8 and col >= 13) or (row >= 13 and col < 8)):
        position_pattern_diffs += 1
    # Check if in timing patterns
    elif row == 6 or col == 6:
        timing_pattern_diffs += 1
    else:
        data_area_diffs += 1

print(f"\nDifferences by area:")
print(f"  Position patterns: {position_pattern_diffs}")
print(f"  Timing patterns: {timing_pattern_diffs}")
print(f"  Data area: {data_area_diffs}")
