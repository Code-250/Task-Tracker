"""
QR Code Encoder Implementation
"""
import numpy as np
from typing import Tuple
from app.utils import (
    generate_position_pattern,
    generate_alignment_pattern,
    generate_timing_patterns,
    generate_payload,
    apply_logistic_encryption,
    matrix_to_hex_string,
    get_padding_sequence
)


class QREncoder:
    """
    QR Code Encoder for simplified QR codes
    """

    def __init__(self):
        self.position_pattern = generate_position_pattern()
        self.alignment_pattern = generate_alignment_pattern()

    def select_version(self, message: str) -> int:
        """
        Select QR code version based on message length
        Version 1: length <= 13
        Version 2: length 14-22
        """
        length = len(message)
        if length <= 13:
            return 1
        elif length <= 22:
            return 2
        else:
            raise ValueError(f"Message too long: {length} chars (max 22)")

    def create_qr_matrix(self, version: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create QR matrix with structural patterns
        Returns: (qr_matrix, mask) where mask indicates reserved positions
        """
        size = 21 if version == 1 else 25
        qr = np.zeros((size, size), dtype=int)
        mask = np.zeros((size, size), dtype=int)  # 1 = reserved, 0 = available

        # Add position detection patterns (3 corners)
        positions = [(0, 0), (0, size - 8), (size - 8, 0)]
        for row, col in positions:
            qr[row:row + 8, col:col + 8] = self.position_pattern
            mask[row:row + 8, col:col + 8] = 1

        # Add timing patterns (row 6 and column 6)
        h_timing, v_timing = generate_timing_patterns(version)

        # Horizontal timing (row 6), skip position patterns
        for col in range(8, size - 8):
            qr[6, col] = h_timing[col]
            mask[6, col] = 1

        # Vertical timing (column 6), skip position patterns
        for row in range(8, size - 8):
            qr[row, 6] = v_timing[row]
            mask[row, 6] = 1

        # Add alignment pattern (version 2 only)
        if version == 2:
            # Center at (18, 18)
            align_row, align_col = 18 - 2, 18 - 2  # Top-left corner
            qr[align_row:align_row + 5, align_col:align_col + 5] = self.alignment_pattern
            mask[align_row:align_row + 5, align_col:align_col + 5] = 1

        return qr, mask

    def zigzag_fill(self, qr: np.ndarray, mask: np.ndarray, payload_bits: list) -> np.ndarray:
        """
        Fill payload into QR matrix using zigzag pattern

        Rules:
        1. Start from bottom-right
        2. Process columns in pairs from right to left
        3. Within each pair, fill (right_col, left_col) alternating for each row
        4. Direction alternates: up for first pair, down for second pair, etc.
        5. Skip row 6 and column 6 (timing patterns)
        6. Skip alignment block in version 2
        """
        size = qr.shape[0]
        payload_idx = 0
        padding = get_padding_sequence()
        padding_idx = 0

        def get_next_bit():
            """Get next bit from payload or padding"""
            nonlocal payload_idx, padding_idx
            if payload_idx < len(payload_bits):
                bit = payload_bits[payload_idx]
                payload_idx += 1
                return bit
            else:
                bit = padding[padding_idx % len(padding)]
                padding_idx += 1
                return bit

        # Start from rightmost column
        col = size - 1
        going_up = True

        # Zigzag fill: process column pairs from right to left
        while col > 0:
            # Get the two columns in this pair
            col_right = col
            col_left = col - 1

            # Determine row range based on direction
            if going_up:
                rows = range(size - 1, -1, -1)  # Bottom to top
            else:
                rows = range(0, size)  # Top to bottom

            # Fill the column pair
            for row in rows:
                # Fill right column first, then left column
                for c in [col_right, col_left]:
                    # Skip timing column
                    if c == 6:
                        continue

                    # Skip if reserved (position pattern, timing, alignment)
                    if mask[row, c] == 0:
                        qr[row, c] = get_next_bit()

            # Move to next column pair (2 columns to the left)
            col -= 2

            # Special case: if we just processed column 7 and are about to hit column 5
            # (skipping column 6), don't toggle direction
            if col == 5:
                # Column 6 was skipped, don't toggle
                pass
            else:
                # Alternate direction for next column pair
                going_up = not going_up

        return qr

    def encode(self, message: str) -> str:
        """
        Encode message to QR code hex string

        Steps:
        1. Select version
        2. Generate payload
        3. Create QR matrix with patterns
        4. Fill payload using zigzag
        5. Apply logistic map encryption
        6. Convert to hex string
        """
        # Step 1: Select version
        version = self.select_version(message)

        # Step 2: Generate payload
        payload = generate_payload(message)

        # Convert payload to bits
        payload_bits = []
        for byte_val in payload:
            # Convert to 8-bit binary
            for i in range(7, -1, -1):
                payload_bits.append((byte_val >> i) & 1)

        # Step 3: Create QR matrix with structural patterns
        qr_matrix, mask = self.create_qr_matrix(version)

        # Step 4: Zigzag fill
        qr_matrix = self.zigzag_fill(qr_matrix, mask, payload_bits)

        # Step 5: Apply logistic map encryption
        encrypted_qr = apply_logistic_encryption(qr_matrix)

        # Step 6: Convert to hex string
        hex_string = matrix_to_hex_string(encrypted_qr)

        return hex_string


# Convenience function
def encode_message(message: str) -> str:
    """
    Encode a message to QR code hex string
    """
    encoder = QREncoder()
    return encoder.encode(message)
