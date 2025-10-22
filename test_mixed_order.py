#!/usr/bin/env python3
"""
Test mixed ordering: column-major logistic, row-major hex
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import generate_payload, generate_logistic_map

def apply_logistic_col_major(qr_matrix):
    """Apply logistic map in column-major order"""
    size = qr_matrix.shape[0]
    map_size = (size * size) // 8 + 1
    logistic_map = generate_logistic_map(map_size)

    # Flatten in COLUMN-major order
    qr_flat = qr_matrix.flatten(order='F')
    encrypted = qr_flat.copy()

    for i in range(map_size):
        logistic_byte = logistic_map[i]
        for bit_pos in range(8):
            qr_index = i * 8 + bit_pos
            if qr_index >= len(qr_flat):
                break
            logistic_bit = (logistic_byte >> bit_pos) & 1
            encrypted[qr_index] ^= logistic_bit

    # Reshape in COLUMN-major order
    return encrypted.reshape(size, size, order='F')

def matrix_to_hex_row_major(qr_matrix):
    """Convert in row-major order"""
    size = qr_matrix.shape[0]
    bits = qr_matrix.flatten(order='C')  # Row-major

    hex_strings = []
    for start_idx in range(0, len(bits), 32):
        chunk_size = min(32, len(bits) - start_idx)
        chunk = bits[start_idx:start_idx + chunk_size]
        value = 0
        for bit in chunk:
            value = (value << 1) | bit
        hex_strings.append("0x0" if value == 0 else f"0x{value:x}")

    return "".join(hex_strings)

encoder = QREncoder()
message = "CC Team"

version = encoder.select_version(message)
payload = generate_payload(message)
payload_bits = []
for byte_val in payload:
    for i in range(7, -1, -1):
        payload_bits.append((byte_val >> i) & 1)

qr_matrix, mask = encoder.create_qr_matrix(version)
qr_matrix = encoder.zigzag_fill(qr_matrix, mask, payload_bits)

# Apply logistic in column-major, convert hex in row-major
encrypted = apply_logistic_col_major(qr_matrix)
hex_result = matrix_to_hex_row_major(encrypted)

print(f"Column-major logistic, row-major hex:")
print(f"Result:   {hex_result[:50]}...")
print(f"Expected: 0x66d92b800x5bc76d830x121a7fa6...")

if hex_result.startswith("0x66d92b800x5bc76d83"):
    print("✓ MATCH FOUND!")
else:
    print("✗ No match")
