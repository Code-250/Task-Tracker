#!/usr/bin/env python3
"""
Test if the expected output has NO logistic map encryption
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import generate_payload, matrix_to_hex_string

encoder = QREncoder()

# Test with "3l8k0L"
message = "3l8k0L"
version = encoder.select_version(message)
payload = generate_payload(message)
print(f"Payload: {payload}")

payload_bits = []
for byte_val in payload:
    for i in range(7, -1, -1):
        payload_bits.append((byte_val >> i) & 1)

# Create QR matrix
qr_matrix, mask = encoder.create_qr_matrix(version)
qr_matrix = encoder.zigzag_fill(qr_matrix, mask, payload_bits)

# Convert to hex WITHOUT logistic map
hex_no_logistic = matrix_to_hex_string(qr_matrix)

print(f"\nWithout logistic map:")
print(hex_no_logistic)

print(f"\nExpected:")
print("0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a")

print(f"\nWith logistic map (current):")
from app.utils import apply_logistic_encryption
encrypted = apply_logistic_encryption(qr_matrix)
hex_with_logistic = matrix_to_hex_string(encrypted)
print(hex_with_logistic)

if hex_no_logistic == "0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a":
    print("\n✓✓✓ MATCH! Expected output has NO logistic map! ✓✓✓")
else:
    print("\n✗ Still no match")

# Also check "CC Team"
print("\n" + "="*80)
print("Testing with 'CC Team'")
print("="*80)

message2 = "CC Team"
version2 = encoder.select_version(message2)
payload2 = generate_payload(message2)

payload_bits2 = []
for byte_val in payload2:
    for i in range(7, -1, -1):
        payload_bits2.append((byte_val >> i) & 1)

qr_matrix2, mask2 = encoder.create_qr_matrix(version2)
qr_matrix2 = encoder.zigzag_fill(qr_matrix2, mask2, payload_bits2)

hex_no_logistic2 = matrix_to_hex_string(qr_matrix2)
print(f"\nWithout logistic map:")
print(hex_no_logistic2)

print(f"\nExpected (from spec):")
print("0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a")

print(f"\nSpec says 'before logistic map':")
print("0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80")

print(f"\nOur 'before logistic map':")
print("0xfe07f4120xe0ae83750x75bbabaf0x5d41120b0xf95fc01e0x1180360x380f30160x13e12060...")

if hex_no_logistic2.startswith("0x66d92b800x5bc76d83"):
    print("\n✓✓✓ CC Team MATCH! No logistic map needed! ✓✓✓")
elif hex_no_logistic2.startswith("0xfe03fc120xd06e82bb"):
    print("\n✓ Matches 'before logistic map' from spec")
else:
    print("\n✗ No match")
