#!/usr/bin/env python3
"""
Trace all data positions
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder
from app.utils import get_padding_sequence

# Get expected matrix
expected_hex = "0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80"

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

expected_bits = hex_to_bits(expected_hex)
expected_matrix = np.array(expected_bits[:441]).reshape(21, 21)

# Get mask
encoder = QREncoder()
_, mask = encoder.create_qr_matrix(version=1)

# Simulate zigzag fill order
size = 21
col = size - 1
going_up = True
zigzag_order = []

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
                expected_val = expected_matrix[row, c]
                zigzag_order.append((row, c, expected_val))

    col -= 2
    if col == 5:
        pass
    else:
        going_up = not going_up

# Get payload
message = "CC Team"
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

payload_bits = []
for byte_val in payload:
    for i in range(7, -1, -1):
        payload_bits.append((byte_val >> i) & 1)

print(f"Payload: {len(payload_bits)} bits")
print(f"Total data positions: {len(zigzag_order)}")
print(f"Padding needed: {len(zigzag_order) - len(payload_bits)} bits")

# Get padding
padding = get_padding_sequence()
padding_bits = []
padding_idx = 0
for _ in range(len(zigzag_order) - len(payload_bits)):
    byte_val = padding[padding_idx % len(padding)]
    for i in range(7, -1, -1):
        padding_bits.append((byte_val >> i) & 1)
        if len(padding_bits) >= len(zigzag_order) - len(payload_bits):
            break
    if len(padding_bits) >= len(zigzag_order) - len(payload_bits):
        break
    padding_idx += 1

# Combine payload and padding
all_bits = payload_bits + padding_bits

# Compare
mismatches = []
for idx, (row, col, expected_val) in enumerate(zigzag_order):
    if idx < len(all_bits):
        our_val = all_bits[idx]
        if our_val != expected_val:
            mismatches.append((idx, row, col, our_val, expected_val))

print(f"\nTotal mismatches: {len(mismatches)}")

if len(mismatches) > 0:
    print(f"\nFirst 20 mismatches:")
    print("="*80)
    print(f"{'Idx':<5} {'Pos':>10} {'Our':>5} {'Expected':>10} {'Stage':>15}")
    print("-"*80)
    for idx, row, col, our_val, expected_val in mismatches[:20]:
        stage = "payload" if idx < len(payload_bits) else "padding"
        print(f"{idx:<5} ({row:2d},{col:2d})  {our_val:>5}  {expected_val:>10}  {stage:>15}")

    # Check if mismatches are concentrated in certain areas
    payload_mismatches = sum(1 for idx, _, _, _, _ in mismatches if idx < len(payload_bits))
    padding_mismatches = len(mismatches) - payload_mismatches

    print(f"\nPayload mismatches: {payload_mismatches}/{len(payload_bits)}")
    print(f"Padding mismatches: {padding_mismatches}/{len(zigzag_order) - len(payload_bits)}")
else:
    print("\n✓ ALL BITS MATCH!")

# Show what padding sequence we're using
print(f"\nPadding sequence: {padding}")
print(f"Padding bits (first 50): {padding_bits[:50]}")
