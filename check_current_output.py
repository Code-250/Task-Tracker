#!/usr/bin/env python3
"""
Check the current output with updated encoder
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import matrix_to_hex_string

# Create encoder
encoder = QREncoder()

# Test message
message = "CC Team"

# Encode without final encryption (before logistic map)
version = encoder.select_version(message)
payload = []
length = len(message)
payload.append(length)
for char in message:
    char_byte = ord(char)
    # Error correction bit
    ec_bit = 0
    for i in range(8):
        ec_bit ^= (char_byte >> i) & 1
    payload.append(char_byte)
    payload.append(ec_bit)

# Convert to bits
payload_bits = []
for byte_val in payload:
    for i in range(7, -1, -1):
        payload_bits.append((byte_val >> i) & 1)

# Create matrix
qr_matrix, mask = encoder.create_qr_matrix(version)

# Zigzag fill
qr_matrix = encoder.zigzag_fill(qr_matrix, mask, payload_bits)

# Convert to hex (before logistic map)
hex_before = matrix_to_hex_string(qr_matrix)

print("Message:", message)
print("\nBefore logistic map:")
print(hex_before)
print("\nExpected (from spec):")
print("0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80")

# Visualize the matrix
print("\n" + "="*60)
print("QR Matrix (before logistic map)")
print("="*60)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        print("█" if qr_matrix[i, j] else " ", end="")
    print()

# Also show the mask
print("\n" + "="*60)
print("Mask (# = reserved, . = data area)")
print("="*60)
print("    " + "".join([str(i%10) for i in range(21)]))
for i in range(21):
    print(f"{i:2d}: ", end="")
    for j in range(21):
        print("#" if mask[i, j] else ".", end="")
    print()
