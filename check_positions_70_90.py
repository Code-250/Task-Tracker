#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')
import numpy as np
from app.qr_encoder import QREncoder

expected_hex = '0xfe03fc120xd06e82bb0x74b5dba70x2ec111070xfaafe00e0x8a05170x492f60x599912030x7d80003a0xff889100x4c00ba050x35d088ee0x964504120x1fca80'

def hex_to_bits(hex_string):
    hex_values = hex_string.split('0x')[1:]
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

encoder = QREncoder()
_, mask = encoder.create_qr_matrix(version=1)

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

message = 'CC Team'
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

print("Zigzag positions 70-90:")
print("="*70)
print(f"{'Idx':<5} {'Pos':>10} {'Payload':>10} {'Expected':>10} {'Match':>8}")
print("-"*70)
for idx in range(70, min(90, len(zigzag_order))):
    row, col, expected_val = zigzag_order[idx]
    if idx < len(payload_bits):
        payload_val = payload_bits[idx]
    else:
        payload_val = "?"
    match = "✓" if payload_val == expected_val else "✗"
    print(f"{idx:<5} ({row:2d},{col:2d})  {payload_val:>10}  {expected_val:>10}  {match:>8}")
