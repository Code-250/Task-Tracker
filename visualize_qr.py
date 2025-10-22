#!/usr/bin/env python3
"""
Visualize QR code structure
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

import numpy as np
from app.qr_encoder import QREncoder

# Create encoder
encoder = QREncoder()

# Create a Version 1 QR matrix
qr_matrix, mask = encoder.create_qr_matrix(version=1)

print("QR Matrix Structure (Version 1, 21x21)")
print("Legend: # = pattern/reserved, . = data area")
print()

# Print column numbers
print("    ", end="")
for col in range(21):
    print(f"{col%10}", end="")
print()

for row in range(21):
    print(f"{row:2d}: ", end="")
    for col in range(21):
        if mask[row, col] == 1:
            print("#", end="")
        else:
            print(".", end="")
    print()

print("\nNow let's see the first few positions that get filled in zigzag order:")

# Simulate zigzag fill
size = 21
col = size - 1
going_up = True
fill_order = []

while col > 0 and len(fill_order) < 50:
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
                fill_order.append((row, c))
                if len(fill_order) >= 50:
                    break
        if len(fill_order) >= 50:
            break

    col -= 2
    if col == 5:
        pass
    else:
        going_up = not going_up

print("\nFirst 50 positions filled (row, col):")
for i, (r, c) in enumerate(fill_order[:50]):
    if i % 5 == 0:
        print()
    print(f"{i:2d}:({r:2d},{c:2d})", end="  ")
print("\n")
