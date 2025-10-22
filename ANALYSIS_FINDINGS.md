# QR Code Algorithm Analysis Findings

## Summary

After extensive analysis and debugging, I've identified and fixed critical issues with position pattern placement in the QR code encoder. However, the test outputs suggest a non-standard algorithm implementation that requires clarification.

## Fixes Implemented

### 1. Position Pattern Placement ✓
**Issue**: Position patterns were being placed at `(0, size-8)` and `(size-8, 0)`
**Fix**: Changed to `(0, size-7)` and `(size-7, 0)` per QR specification

**For Version 1 (21×21)**:
- Before: (0,0), (0,13), (13,0)
- After: (0,0), (0,14), (14,0) ✓

**Pattern Sizing**:
- Top-left: Full 8×8 pattern (rows 0-7, cols 0-7)
- Top-right: 7×8 pattern (rows 0-7, cols 14-20) - no right border at edge
- Bottom-left: 8×7 pattern (rows 14-20, cols 0-7) - no bottom border at edge

### 2. Timing Pattern Range ✓
**Issue**: Timing patterns went from 8 to `size-8` (columns 8-12)
**Fix**: Changed to 8 to `size-7` (columns 8-13) to fill gap between patterns

## Verification

All structural patterns now match the QR specification exactly:

```
✓ Top-left position pattern (rows 0-7, cols 0-7)
✓ Top-right position pattern (rows 0-7, cols 14-20)
✓ Bottom-left position pattern (rows 14-20, cols 0-7)
✓ Horizontal timing pattern (row 6, cols 8-13)
✓ Vertical timing pattern (col 6, rows 8-13)
```

## Critical Discovery: Algorithm Discrepancy

### Expected Output Analysis

When reverse-engineering the expected test output for "CC Team":

**Expected Final Output (after logistic)**:
```
0x66d92b800x5bc76d830x121a7fa60x51c111870x3a5f3ca30x8be36f330xed0a23a0xa48e98780x33bf50de0x2e8700700x56a92d0a0xdece7a2e0x461175cd0xff122a
```

**Reversed Output (before logistic)**:
```
0x3ee3fc d20x106e723b0xf4b51b270xaec111070x1a57e0ce0xa80370x80efd2160x119d2030xfd80003a0x8f7840100xcef3ba000xe55005ee0x96c584120x1eca40
```

### Issue: Non-Standard Position Patterns

Visualizing the reversed matrix shows:

```
    012345678901234567890
 0:   █████ ███   ███████   <- NOT a standard position pattern!
 1: █  ██ █  █    █     █
 2: █ ███  ███  █   ███ █
 ...
```

**The expected output does NOT have standard QR position patterns!**

The patterns are filled with data, which means:
1. Either position patterns are NOT reserved during zigzag fill, OR
2. Position patterns are applied via XOR after filling, OR
3. The test outputs are from a different algorithm implementation

## Testing Conducted

### Hypothesis 1: No Masking
- Tested filling entire matrix without masking position pattern areas
- **Result**: Does not match expected output ✗

### Hypothesis 2: XOR After Fill
- Tested filling entire matrix, then XORing patterns on top
- **Result**: Does not match expected output ✗

### Hypothesis 3: Partial Masking
- Various combinations of masked/unmasked pattern areas
- **Result**: None match expected output ✗

## Zigzag Analysis

The zigzag fill order was verified to be correct:
- First 50 positions: All payload bits match expected values ✓
- Starting position 79: Mismatches begin
- Pattern: Differences occur when zigzag reaches the modified pattern areas

This confirms the zigzag algorithm itself is correct, but the pattern handling differs from the test outputs.

## Conclusion

**What's Correct**:
- Position pattern placement according to QR specification
- Timing pattern placement according to QR specification
- Zigzag fill algorithm
- Logistic map encryption
- Payload generation

**What's Unclear**:
- How position/timing patterns should interact with data fill
- Whether patterns should be reserved (masked) during fill
- Whether the test outputs use a non-standard variant

## Recommendation

To proceed, we need:
1. Access to the original algorithm specification document
2. A working reference implementation to compare against
3. Clarification on whether position patterns should be preserved during encoding
4. Additional test cases with known intermediate values

## Files for Review

Debug/analysis scripts created:
- `visualize_difference.py` - Bit-level comparison with expected output
- `reverse_logistic.py` - Decrypt expected outputs to see pre-encryption state
- `trace_zigzag.py` - Verify zigzag fill order
- `compare_patterns.py` - Verify pattern correctness
- `visualize_correct_expected.py` - Visualize reversed expected matrix

All scripts confirm that:
1. Our patterns are correct per specification
2. Expected outputs use a different pattern handling approach
