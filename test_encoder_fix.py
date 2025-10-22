#!/usr/bin/env python3
"""
Test the QR encoder with the reference examples
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

from app.qr_encoder import encode_message

# Test cases from specification
test_cases = [
    ("CC Team", "0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a"),
    ("CC Team is awesome!", "0x66ede8530xb3b981a10xed18e4040xa4a0026c0xd039db570x21976f0d0xed168440xfdce22bf0xd67e47ec0x2171a0600x2a1a95010x875f3f480x78347f130x886ccc430xc90f439a0x331f54900x7bbcbf030x20d731250xc555223e0x15858"),
]

print("Testing QR Encoder with reference examples")
print("=" * 80)

for message, expected in test_cases:
    print(f"\nTest: '{message}'")
    result = encode_message(message)
    print(f"Result:   {result}")
    print(f"Expected: {expected}")

    if result == expected:
        print("✓ PASS")
    else:
        print("✗ FAIL")
        # Show differences
        if len(result) != len(expected):
            print(f"  Length mismatch: {len(result)} vs {len(expected)}")

        # Compare hex values
        result_parts = result.split('0x')[1:]
        expected_parts = expected.split('0x')[1:]

        for i, (r, e) in enumerate(zip(result_parts, expected_parts)):
            if r != e:
                print(f"  Diff at position {i}: 0x{r} vs 0x{e}")

print("\n" + "=" * 80)
