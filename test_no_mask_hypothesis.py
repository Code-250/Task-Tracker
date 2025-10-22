#!/usr/bin/env python3
"""
Test hypothesis: zigzag fills entire matrix without masking, then patterns are XORed
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import generate_position_pattern, generate_timing_patterns, matrix_to_hex_string

# Create encoder
encoder = QREncoder()
message = "CC Team"

# Get payload
version = encoder.select_version(message)
payload = []
length = len(message)
payload.append(length)
for char in message:
    char_byte = ord(char)
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

print(f"Payload: {len(payload_bits)} bits")
print(f"Payload: {payload}")

# Create EMPTY matrix with NO mask (everything is data area)
size = 21
qr_matrix = np.zeros((size, size), dtype=int)
mask = np.zeros((size, size), dtype=int)  # ALL zeros = all data area!

# Zigzag fill without any masking
qr_matrix = encoder.zigzag_fill(qr_matrix, mask, payload_bits)

# Convert to hex
hex_output = matrix_to_hex_string(qr_matrix)

print(f"\nAfter zigzag (no masking):")
print(hex_output)

# Now XOR position patterns on top
position_pattern = generate_position_pattern()

# Top-left
qr_matrix[0:8, 0:8] ^= position_pattern

# Top-right (7 columns)
top_right_pattern = position_pattern[:, :7]
qr_matrix[0:8, size-7:size] ^= top_right_pattern

# Bottom-left (7 rows)
bottom_left_pattern = position_pattern[:7, :]
qr_matrix[size-7:size, 0:8] ^= bottom_left_pattern

# XOR timing patterns
h_timing, v_timing = generate_timing_patterns(version)
for col in range(8, size - 7):
    qr_matrix[6, col] ^= h_timing[col]
for row in range(8, size - 7):
    qr_matrix[row, 6] ^= v_timing[row]

# Convert to hex
hex_after_xor = matrix_to_hex_string(qr_matrix)

print(f"\nAfter XOR with patterns:")
print(hex_after_xor)

print(f"\nCorrect expected (before logistic):")
print("0x3ee3fcd20x106e723b0xf4b51b270xaec111070x1a57e0ce0xa80370x80efd2160x119d2030xfd80003a0x8f7840100xcef3ba000xe55005ee0x96c584120x1eca40")

print(f"\nMatch? {hex_after_xor == '0x3ee3fcd20x106e723b0xf4b51b270xaec111070x1a57e0ce0xa80370x80efd2160x119d2030xfd80003a0x8f7840100xcef3ba000xe55005ee0x96c584120x1eca40'}")
