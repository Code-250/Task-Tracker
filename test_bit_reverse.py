#!/usr/bin/env python3
"""
Test reversing bit order within bytes/integers
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import apply_logistic_encryption, generate_payload

def matrix_to_hex_reversed_bits(qr_matrix):
    """Convert with reversed bit order within each byte"""
    size = qr_matrix.shape[0]
    bits = qr_matrix.flatten(order='C')  # Row-major

    hex_strings = []
    num_bits = len(bits)

    for start_idx in range(0, num_bits, 32):
        chunk_size = min(32, num_bits - start_idx)
        chunk = bits[start_idx:start_idx + chunk_size]

        # Reverse bits within each 8-bit group
        reversed_chunk = []
        for i in range(0, len(chunk), 8):
            byte_bits = chunk[i:i+8]
            # Reverse this byte
            reversed_chunk.extend(byte_bits[::-1] if len(byte_bits) == 8 else byte_bits)

        # Convert to integer (big endian)
        value = 0
        for bit in reversed_chunk:
            value = (value << 1) | bit

        if value == 0:
            hex_strings.append("0x0")
        else:
            hex_strings.append(f"0x{value:x}")

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
encrypted = apply_logistic_encryption(qr_matrix)

hex_reversed = matrix_to_hex_reversed_bits(encrypted)

print(f"With reversed bits: {hex_reversed[:50]}...")
print(f"Expected:           0x66d92b800x5bc76d830x121a7fa6...")

if hex_reversed.startswith("0x66d92b800x5bc76d83"):
    print("✓ MATCH!")
else:
    print("✗ No match")
