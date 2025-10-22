#!/usr/bin/env python3
"""
Reverse engineer the expected output to find the correct zigzag and logistic map
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.utils import generate_logistic_map, generate_payload

# Expected output for "3l8k0L"
expected_hex = "0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a"

# Known correct payload for "3l8k0L"
expected_payload = [6, 51, 0, 108, 0, 56, 1, 107, 1, 48, 0, 76, 1]
print(f"Expected payload: {expected_payload}")

# Convert expected hex to bits
def hex_string_to_bits(hex_string):
    """Convert hex string to bit array"""
    hex_values = hex_string.split("0x")[1:]
    all_bits = []

    for i, hex_val in enumerate(hex_values):
        value = int(hex_val, 16)

        # Determine bit count (last chunk might be shorter)
        if i < len(hex_values) - 1:
            bits_in_chunk = 32
        else:
            # Last chunk - calculate based on total needed
            total_bits = 21 * 21  # Version 1
            bits_so_far = i * 32
            bits_in_chunk = total_bits - bits_so_far

        binary = format(value, f'0{bits_in_chunk}b')
        all_bits.extend([int(b) for b in binary])

    return all_bits

expected_bits = hex_string_to_bits(expected_hex)
print(f"Total bits: {len(expected_bits)}")
print(f"Expected for 21x21: {21*21}")

# Convert to matrix (try both row-major and column-major)
def bits_to_matrix(bits, size, order='C'):
    """Convert bits to matrix"""
    return np.array(bits[:size*size]).reshape(size, size, order=order)

# Try row-major
matrix_row_major = bits_to_matrix(expected_bits, 21, order='C')
print("\n=== Matrix from hex (row-major) ===")
print("First row:", matrix_row_major[0, :10])

# Try column-major
matrix_col_major = bits_to_matrix(expected_bits, 21, order='F')
print("\n=== Matrix from hex (column-major) ===")
print("First column:", matrix_col_major[:10, 0])

print("\n" + "="*80)
print("REVERSING LOGISTIC MAP ENCRYPTION")
print("="*80)

# Generate logistic map
logistic_map = generate_logistic_map(56)
print(f"\nLogistic map (first 10): {logistic_map[:10]}")

def reverse_logistic_encryption(encrypted_bits, logistic_map, order='C'):
    """Reverse logistic map encryption"""
    decrypted = encrypted_bits.copy()

    for i in range(len(logistic_map)):
        logistic_byte = logistic_map[i]

        for bit_pos in range(8):
            bit_index = i * 8 + bit_pos
            if bit_index >= len(decrypted):
                break

            # Try normal bit order
            logistic_bit = (logistic_byte >> bit_pos) & 1
            decrypted[bit_index] ^= logistic_bit

    return decrypted

# Try reversing with row-major order
print("\n--- Trying ROW-MAJOR order ---")
decrypted_row = reverse_logistic_encryption(expected_bits, logistic_map, 'C')
decrypted_matrix_row = np.array(decrypted_row[:441]).reshape(21, 21, order='C')

# Convert to hex to see what we get
def matrix_to_hex(matrix, order='C'):
    bits = matrix.flatten(order=order)
    hex_strings = []
    for start_idx in range(0, len(bits), 32):
        chunk_size = min(32, len(bits) - start_idx)
        chunk = bits[start_idx:start_idx + chunk_size]
        value = 0
        for bit in chunk:
            value = (value << 1) | bit
        hex_strings.append("0x0" if value == 0 else f"0x{value:x}")
    return "".join(hex_strings)

hex_after_decrypt_row = matrix_to_hex(decrypted_matrix_row, 'C')
print(f"After decrypt (row): {hex_after_decrypt_row[:80]}...")

# Try reversing with column-major order
print("\n--- Trying COLUMN-MAJOR order ---")
decrypted_col = reverse_logistic_encryption(expected_bits, logistic_map, 'F')
decrypted_matrix_col = np.array(decrypted_col[:441]).reshape(21, 21, order='F')
hex_after_decrypt_col = matrix_to_hex(decrypted_matrix_col, 'C')
print(f"After decrypt (col): {hex_after_decrypt_col[:80]}...")

# What we expect to see after decryption (before logistic map)
print("\n--- What we produced (before logistic map) ---")
print("0xfe07f4120xe0ae83750x75bbabaf0x5d41120b0xf95fc01e0x1180360x380f30160x13e12060...")

print("\n" + "="*80)
print("ANALYZING DECRYPTED MATRIX")
print("="*80)

# Visualize the decrypted matrix
def print_matrix(matrix, title):
    print(f"\n{title}")
    print("    " + "".join([str(i%10) for i in range(21)]))
    for i in range(21):
        print(f"{i:2d}: ", end="")
        for j in range(21):
            print("█" if matrix[i, j] else " ", end="")
        print()

print_matrix(decrypted_matrix_row, "Decrypted Matrix (Row-major)")

# Check if position patterns are visible
print("\n--- Checking for position patterns ---")
# Position patterns should be at (0,0), (0,13), (13,0)
top_left = decrypted_matrix_row[0:8, 0:8]
print("Top-left 8x8:")
print(top_left)

print("\n" + "="*80)
print("TRYING DIFFERENT LOGISTIC MAP BIT ORDERINGS")
print("="*80)

def reverse_logistic_with_bit_order(encrypted_bits, logistic_map, reverse_bits=False):
    """Reverse logistic map with different bit orderings"""
    decrypted = encrypted_bits[:]

    for i in range(len(logistic_map)):
        logistic_byte = logistic_map[i]

        for bit_pos in range(8):
            bit_index = i * 8 + bit_pos
            if bit_index >= len(decrypted):
                break

            # Try reversed bit order
            if reverse_bits:
                logistic_bit = (logistic_byte >> (7 - bit_pos)) & 1
            else:
                logistic_bit = (logistic_byte >> bit_pos) & 1

            decrypted[bit_index] ^= logistic_bit

    return decrypted

print("\n--- With REVERSED bit order (MSB first) ---")
decrypted_rev = reverse_logistic_with_bit_order(expected_bits, logistic_map, reverse_bits=True)
decrypted_matrix_rev = np.array(decrypted_rev[:441]).reshape(21, 21, order='C')
hex_after_decrypt_rev = matrix_to_hex(decrypted_matrix_rev, 'C')
print(f"After decrypt (reversed): {hex_after_decrypt_rev[:80]}...")

# Compare with what we expect
print("\n--- COMPARISON ---")
print(f"Expected (our output):    0xfe07f4120xe0ae83750x75bbabaf...")
print(f"Got (row-major):          {hex_after_decrypt_row[:50]}...")
print(f"Got (col-major):          {hex_after_decrypt_col[:50]}...")
print(f"Got (reversed bits):      {hex_after_decrypt_rev[:50]}...")
