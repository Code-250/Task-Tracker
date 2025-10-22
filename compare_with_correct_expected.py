#!/usr/bin/env python3
"""
Compare our output with the CORRECT expected output
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

from app.qr_encoder import encode_message

# Test cases
test_cases = [
    ("CC Team", "0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a"),
    ("CC Team is awesome!", "0x66ede8530xb3b981a10xed18e4040xa4a0026c0xd039db570x21976f0d0xed168440xfdce22bf0xd67e47ec0x2171a0600x2a1a95010x875f3f480x78347f130x886ccc430xc90f439a0x331f54900x7bbcbf030x20d731250xc555223e0x15858"),
]

print("Testing QR Encoder with CORRECTED understanding:")
print("="*80)

for message, expected in test_cases:
    print(f"\nTest: '{message}'")
    result = encode_message(message)
    print(f"Result:   {result}")
    print(f"Expected: {expected}")

    if result == expected:
        print("✓✓✓ PASS ✓✓✓")
    else:
        print("✗ FAIL")

        # Show first difference
        if len(result) != len(expected):
            print(f"  Length mismatch: {len(result)} vs {len(expected)}")

        result_parts = result.split('0x')[1:]
        expected_parts = expected.split('0x')[1:]

        first_diff = None
        for i, (r, e) in enumerate(zip(result_parts, expected_parts)):
            if r != e:
                if first_diff is None:
                    first_diff = i
                    print(f"  First diff at chunk {i}: 0x{r} vs 0x{e}")
                    # Show in binary
                    r_int = int(r, 16)
                    e_int = int(e, 16)
                    r_bin = format(r_int, 'b').zfill(32)
                    e_bin = format(e_int, 'b').zfill(32)
                    print(f"    Result:   0b{r_bin}")
                    print(f"    Expected: 0b{e_bin}")
                    # Show which bits differ
                    diffs = [i for i, (rb, eb) in enumerate(zip(r_bin, e_bin)) if rb != eb]
                    print(f"    Diff bits: {diffs} (total: {len(diffs)})")
                    break

print("\n" + "="*80)
