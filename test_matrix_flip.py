#!/usr/bin/env python3
"""
Test different matrix orientations
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import apply_logistic_encryption, matrix_to_hex_string

encoder = QREncoder()
message = "CC Team"

# Generate QR matrix before encryption
version = encoder.select_version(message)
from app.utils import generate_payload
payload = generate_payload(message)
payload_bits = []
for byte_val in payload:
    for i in range(7, -1, -1):
        payload_bits.append((byte_val >> i) & 1)

qr_matrix, mask = encoder.create_qr_matrix(version)
qr_matrix = encoder.zigzag_fill(qr_matrix, mask, payload_bits)

print("Testing different matrix orientations:\n")

# Original
encrypted = apply_logistic_encryption(qr_matrix)
hex1 = matrix_to_hex_string(encrypted)
print(f"1. Original (row-major): {hex1[:50]}...")

# Transpose
encrypted_t = apply_logistic_encryption(qr_matrix.T)
hex2 = matrix_to_hex_string(encrypted_t)
print(f"2. Transposed: {hex2[:50]}...")

# Flip vertically
encrypted_v = apply_logistic_encryption(np.flipud(qr_matrix))
hex3 = matrix_to_hex_string(encrypted_v)
print(f"3. Flipped vertically: {hex3[:50]}...")

# Flip horizontally
encrypted_h = apply_logistic_encryption(np.fliplr(qr_matrix))
hex4 = matrix_to_hex_string(encrypted_h)
print(f"4. Flipped horizontally: {hex4[:50]}...")

# Rotate 90
encrypted_r90 = apply_logistic_encryption(np.rot90(qr_matrix))
hex5 = matrix_to_hex_string(encrypted_r90)
print(f"5. Rotated 90°: {hex5[:50]}...")

# Rotate 180
encrypted_r180 = apply_logistic_encryption(np.rot90(qr_matrix, 2))
hex6 = matrix_to_hex_string(encrypted_r180)
print(f"6. Rotated 180°: {hex6[:50]}...")

# Rotate 270
encrypted_r270 = apply_logistic_encryption(np.rot90(qr_matrix, 3))
hex7 = matrix_to_hex_string(encrypted_r270)
print(f"7. Rotated 270°: {hex7[:50]}...")

# Transpose then flip
encrypted_tf = apply_logistic_encryption(np.flipud(qr_matrix.T))
hex8 = matrix_to_hex_string(encrypted_tf)
print(f"8. Transpose+flip: {hex8[:50]}...")

print(f"\nExpected: 0x66d92b800x5bc76d830x121a7fa6...")
print("\nChecking for matches...")

expected_start = "0x66d92b800x5bc76d83"
for i, hex_val in enumerate([hex1, hex2, hex3, hex4, hex5, hex6, hex7, hex8], 1):
    if hex_val.startswith(expected_start):
        print(f"✓ MATCH FOUND: Option {i}")
