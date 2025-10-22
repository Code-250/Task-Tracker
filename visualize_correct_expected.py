#!/usr/bin/env python3
"""
Visualize the CORRECT expected matrix (before logistic)
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.utils import generate_logistic_map

# Expected AFTER logistic map
expected_after = "0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a"

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

# Decode expected after
after_bits = hex_to_bits(expected_after)

# Generate logistic map
map_size = (21 * 21) // 8 + 1
logistic_map = generate_logistic_map(map_size)

# Reverse the encryption
before_bits = list(after_bits)
for i in range(map_size):
    logistic_byte = logistic_map[i]
    for bit_pos in range(8):
        qr_index = i * 8 + bit_pos
        if qr_index >= len(before_bits):
            break
        logistic_bit = (logistic_byte >> bit_pos) & 1
        before_bits[qr_index] ^= logistic_bit

# Create matrix
expected_matrix = np.array(before_bits[:441]).reshape(21, 21)

print("CORRECT Expected Matrix (before logistic, from reversing expected output):")
print("="*70)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

print("\nFirst row values:")
print("Col:", " ".join([f"{i:2d}" for i in range(21)]))
print("Val:", " ".join([f" {expected_matrix[0, i]}" for i in range(21)]))
print()

print("Checking position patterns:")
print("\nTop-left (rows 0-7, cols 0-7):")
for i in range(8):
    for j in range(8):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()

print("\nTop-right (rows 0-7, cols 14-20):")
for i in range(8):
    for j in range(14, 21):
        print("█" if expected_matrix[i, j] else " ", end="")
    print()
