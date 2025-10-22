#!/usr/bin/env python3
"""
Reverse the logistic map from expected output to get "before logistic" state
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

def bits_to_hex(bits):
    hex_strings = []
    for start_idx in range(0, len(bits), 32):
        chunk_size = min(32, len(bits) - start_idx)
        chunk = bits[start_idx:start_idx + chunk_size]
        value = 0
        for bit in chunk:
            value = (value << 1) | bit
        hex_strings.append("0x0" if value == 0 else f"0x{value:x}")
    return "".join(hex_strings)

# Decode expected after
after_bits = hex_to_bits(expected_after)
print(f"Total bits: {len(after_bits)}")

# Generate logistic map
map_size = (21 * 21) // 8 + 1
logistic_map = generate_logistic_map(map_size)
print(f"Logistic map size: {map_size}")
print(f"First 15 logistic values: {logistic_map[:15]}")

# Reverse the encryption (XOR is self-inverse)
before_bits = list(after_bits)
for i in range(map_size):
    logistic_byte = logistic_map[i]
    for bit_pos in range(8):
        qr_index = i * 8 + bit_pos
        if qr_index >= len(before_bits):
            break
        logistic_bit = (logistic_byte >> bit_pos) & 1
        before_bits[qr_index] ^= logistic_bit

# Convert to hex
before_hex = bits_to_hex(before_bits)

print(f"\nReversed 'before logistic' hex:")
print(before_hex)
print(f"\nPreviously assumed 'before logistic' (from old script):")
print("0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80")

print(f"\nAre they the same? {before_hex == '0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80'}")

# Decode the matrix
before_matrix = np.array(before_bits[:441]).reshape(21, 21)

print("\nReversed matrix row 1, column 13:")
print(f"Value: {before_matrix[1, 13]}")
