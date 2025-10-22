#!/usr/bin/env python3
"""
Test specific message from user's test cases
"""
import sys
sys.path.insert(0, '/home/user/Task-Tracker/qr-service')

from app.qr_encoder import encode_message

# Test one of the user's test cases
message = "3l8k0L"
result = encode_message(message)

print(f"Message: {message}")
print(f"Result:")
print(f"Cumulonimbus,587764054854")
print(result)
print()
print(f"Expected:")
print(f"Cumulonimbus,587764054854")
print(f"0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a")
