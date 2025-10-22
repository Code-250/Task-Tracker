#!/usr/bin/env python3
"""
Debug encoder - output before logistic map encryption
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

# Encode without final encryption
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
print("\nPayload bytes:", payload)
print("\nBefore logistic map:")
print(hex_before)
print("\nExpected (from spec):")
print("0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80")

# Now do full encoding with logistic map
full_result = encoder.encode(message)
print("\nAfter logistic map:")
print(full_result)
print("\nExpected (from user's test):")
print("0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a")
