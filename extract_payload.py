#!/usr/bin/env python3
"""
Try to extract payload from reversed matrix using different patterns
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.utils import generate_logistic_map

# Expected hex for "3l8k0L"
expected_hex = "0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a"

# Known correct payload
expected_payload_bytes = [6, 51, 0, 108, 0, 56, 1, 107, 1, 48, 0, 76, 1]
expected_payload_bits = []
for byte_val in expected_payload_bytes:
    for i in range(7, -1, -1):
        expected_payload_bits.append((byte_val >> i) & 1)

print(f"Expected payload bits (first 32): {expected_payload_bits[:32]}")
print(f"Total payload bits: {len(expected_payload_bits)}")

# Convert hex to bits
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

encrypted_bits = hex_to_bits(expected_hex)

# Reverse logistic map
logistic_map = generate_logistic_map(56)

def reverse_logistic(bits, logistic_map):
    decrypted = bits[:]
    for i in range(len(logistic_map)):
        logistic_byte = logistic_map[i]
        for bit_pos in range(8):
            bit_index = i * 8 + bit_pos
            if bit_index >= len(decrypted):
                break
            logistic_bit = (logistic_byte >> bit_pos) & 1
            decrypted[bit_index] ^= logistic_bit
    return decrypted

decrypted_bits = reverse_logistic(encrypted_bits, logistic_map)

# Convert to matrix and try to extract payload
print("\n" + "="*80)
print("EXTRACTING PAYLOAD - TRYING DIFFERENT APPROACHES")
print("="*80)

# Create a simple mask (just for data areas, ignoring exact patterns)
def create_simple_mask():
    mask = np.zeros((21, 21), dtype=int)
    # Position patterns
    for row, col in [(0, 0), (0, 13), (13, 0)]:
        mask[row:row + 8, col:col + 8] = 1
    # Timing patterns
    mask[6, :] = 1
    mask[:, 6] = 1
    return mask

mask = create_simple_mask()

# Try extracting with my zigzag pattern
def extract_my_zigzag(matrix, mask):
    """Extract using my zigzag implementation"""
    size = 21
    bits = []
    col = size - 1
    going_up = True

    while col > 0:
        col_right = col
        col_left = col - 1

        if going_up:
            rows = range(size - 1, -1, -1)
        else:
            rows = range(0, size)

        for row in rows:
            for c in [col_right, col_left]:
                if c == 6:
                    continue
                if mask[row, c] == 0:
                    bits.append(int(matrix[row, c]))

        col -= 2
        if col == 5:
            pass
        else:
            going_up = not going_up

    return bits

# Try row-major matrix
matrix_row = np.array(decrypted_bits[:441]).reshape(21, 21, order='C')
extracted_row = extract_my_zigzag(matrix_row, mask)
print(f"\n--- Row-major matrix, my zigzag ---")
print(f"First 104 bits: {extracted_row[:104]}")
print(f"Expected bits:  {expected_payload_bits}")
print(f"Match: {extracted_row[:104] == expected_payload_bits}")

# Try column-major matrix
matrix_col = np.array(decrypted_bits[:441]).reshape(21, 21, order='F')
extracted_col = extract_my_zigzag(matrix_col, mask)
print(f"\n--- Column-major matrix, my zigzag ---")
print(f"First 104 bits: {extracted_col[:104]}")
print(f"Match: {extracted_col[:104] == expected_payload_bits}")

# Try simple left-to-right, top-to-bottom extraction
def extract_simple(matrix, mask):
    """Simple row-by-row extraction"""
    bits = []
    for row in range(21):
        for col in range(21):
            if mask[row, col] == 0:
                bits.append(int(matrix[row, col]))
    return bits

extracted_simple_row = extract_simple(matrix_row, mask)
print(f"\n--- Row-major matrix, simple row-by-row ---")
print(f"First 104 bits: {extracted_simple_row[:104]}")
print(f"Match: {extracted_simple_row[:104] == expected_payload_bits}")

extracted_simple_col = extract_simple(matrix_col, mask)
print(f"\n--- Column-major matrix, simple row-by-row ---")
print(f"First 104 bits: {extracted_simple_col[:104]}")
print(f"Match: {extracted_simple_col[:104] == expected_payload_bits}")

# Try extracting column by column
def extract_column_by_column(matrix, mask):
    """Extract column by column"""
    bits = []
    for col in range(21):
        for row in range(21):
            if mask[row, col] == 0:
                bits.append(int(matrix[row, col]))
    return bits

extracted_colwise_row = extract_column_by_column(matrix_row, mask)
print(f"\n--- Row-major matrix, column-by-column ---")
print(f"First 104 bits: {extracted_colwise_row[:104]}")
print(f"Match: {extracted_colwise_row[:104] == expected_payload_bits}")

extracted_colwise_col = extract_column_by_column(matrix_col, mask)
print(f"\n--- Column-major matrix, column-by-column ---")
print(f"First 104 bits: {extracted_colwise_col[:104]}")
print(f"Match: {extracted_colwise_col[:104] == expected_payload_bits}")

print("\n" + "="*80)
print("CHECKING IF PAYLOAD BYTES MATCH")
print("="*80)

def bits_to_bytes(bits):
    """Convert bit list to byte list"""
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) == 8:
            byte_val = 0
            for bit in byte_bits:
                byte_val = (byte_val << 1) | bit
            bytes_list.append(byte_val)
    return bytes_list

# Check each extraction
for name, bits in [
    ("Row/My zigzag", extracted_row),
    ("Col/My zigzag", extracted_col),
    ("Row/Simple", extracted_simple_row),
    ("Col/Simple", extracted_simple_col),
    ("Row/ColWise", extracted_colwise_row),
    ("Col/ColWise", extracted_colwise_col),
]:
    payload_bytes = bits_to_bytes(bits[:104])
    print(f"\n{name}:")
    print(f"  Got:      {payload_bytes}")
    print(f"  Expected: {expected_payload_bytes}")
    if payload_bytes == expected_payload_bytes:
        print(f"  ✓✓✓ MATCH FOUND! ✓✓✓")
