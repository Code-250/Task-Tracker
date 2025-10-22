#!/usr/bin/env python3
"""
Test logistic map generation
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

from app.utils import generate_logistic_map

# Generate first 20 values
logistic_map = generate_logistic_map(20)

print("First 20 values of logistic map:")
print("x(0) = 0.1, r = 4.0")
print()

# Also calculate manually
x = 0.1
print(f"{'i':>3} {'x':>20} {'int(x*255)':>10} {'hex':>8} {'binary':>10}")
print("-" * 65)

for i in range(20):
    int_val = int(x * 255)
    print(f"{i:3d} {x:20.17f} {int_val:10d} {int_val:8x} {int_val:10b}")
    x = 4.0 * x * (1.0 - x)

print()
print("Values from generate_logistic_map():")
for i, val in enumerate(logistic_map[:20]):
    print(f"{i:3d}: {val:3d} = 0x{val:02x} = 0b{val:08b}")
