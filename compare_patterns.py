#!/usr/bin/env python3
"""
Compare position and timing patterns between current and expected
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder

# Get expected matrix
expected_hex = "0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80"

def hex_to_bits(hex_string):
    hex_values = hex_string.split("0x")[1:]
    all_bits = []
    for i, hex_val in enumerate(hex_values):
        value = int(hex_val, 16)
        if i < len(hex_values) - 1:
            bits_in_chunk = 32
        else:
            bits_in_chunk = 21 * 21 - i * 32
        binary = format(value, f'0{bits_in_chunk}b')
        all_bits.extend([int(b) for b in binary])
    return all_bits

expected_bits = hex_to_bits(expected_hex)
expected_matrix = np.array(expected_bits[:441]).reshape(21, 21)

# Get current matrix (just patterns, no data)
encoder = QREncoder()
current_matrix, current_mask = encoder.create_qr_matrix(version=1)

print("Comparing patterns between current and expected...")
print("="*70)

# Compare position patterns
print("\n1. TOP-LEFT Position Pattern (rows 0-7, cols 0-7):")
tl_match = True
for i in range(8):
    for j in range(8):
        if current_matrix[i, j] != expected_matrix[i, j]:
            print(f"  DIFF at ({i},{j}): current={current_matrix[i,j]}, expected={expected_matrix[i,j]}")
            tl_match = False
if tl_match:
    print("  ✓ MATCH")

print("\n2. TOP-RIGHT Position Pattern (rows 0-7, cols 14-20):")
tr_match = True
for i in range(8):
    for j in range(14, 21):
        if current_matrix[i, j] != expected_matrix[i, j]:
            print(f"  DIFF at ({i},{j}): current={current_matrix[i,j]}, expected={expected_matrix[i,j]}")
            tr_match = False
if tr_match:
    print("  ✓ MATCH")

print("\n3. BOTTOM-LEFT Position Pattern (rows 14-20, cols 0-7):")
bl_match = True
for i in range(14, 21):
    for j in range(8):
        if current_matrix[i, j] != expected_matrix[i, j]:
            print(f"  DIFF at ({i},{j}): current={current_matrix[i,j]}, expected={expected_matrix[i,j]}")
            bl_match = False
if bl_match:
    print("  ✓ MATCH")

print("\n4. Horizontal Timing Pattern (row 6, cols 8-13):")
ht_match = True
for j in range(8, 14):
    if current_matrix[6, j] != expected_matrix[6, j]:
        print(f"  DIFF at (6,{j}): current={current_matrix[6,j]}, expected={expected_matrix[6,j]}")
        ht_match = False
if ht_match:
    print("  ✓ MATCH")

print("\n5. Vertical Timing Pattern (col 6, rows 8-13):")
vt_match = True
for i in range(8, 14):
    if current_matrix[i, 6] != expected_matrix[i, 6]:
        print(f"  DIFF at ({i},6): current={current_matrix[i,6]}, expected={expected_matrix[i,6]}")
        vt_match = False
if vt_match:
    print("  ✓ MATCH")

print("\n6. Mask Check:")
# Count data area positions
data_positions = []
for i in range(21):
    for j in range(21):
        if current_mask[i, j] == 0:
            data_positions.append((i, j))

print(f"  Total data area positions: {len(data_positions)}")
print(f"  Expected: ~{441 - 8*8*3 - 6*2} positions")

# Show first few data positions in zigzag order
print("\n7. First 20 data area positions (where payload will be filled):")
for idx, (i, j) in enumerate(data_positions[:20]):
    expected_val = expected_matrix[i, j]
    print(f"  {idx}: ({i:2d},{j:2d}) - expected value: {expected_val}")
