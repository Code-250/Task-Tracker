"""
QR Code Decoder Implementation
"""
import numpy as np
from typing import Tuple, Optional, List
from app.utils import (
    generate_position_pattern,
    reverse_logistic_encryption,
    hex_string_to_matrix,
)


class QRDecoder:
    """
    QR Code Decoder for simplified QR codes
    """

    def __init__(self):
        self.position_pattern = generate_position_pattern()

    def find_position_patterns(self, matrix: np.ndarray) -> List[Tuple[int, int]]:
        """
        Find all position detection patterns (8x8) in the matrix
        Returns list of (row, col) positions of top-left corner
        """
        positions = []
        rows, cols = matrix.shape

        for r in range(rows - 7):
            for c in range(cols - 7):
                # Extract 8x8 block
                block = matrix[r:r + 8, c:c + 8]

                # Check if it matches position pattern
                if np.array_equal(block, self.position_pattern):
                    positions.append((r, c))

        return positions

    def determine_qr_location_and_rotation(self, positions: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
        """
        Determine QR code version, location, and rotation from position patterns

        Standard orientation:
        - Version 1 (21x21): patterns at (0,0), (0,13), (13,0)
        - Version 2 (25x25): patterns at (0,0), (0,17), (17,0)

        Returns: (top_left_row, top_left_col, version, rotation_degrees)
        """
        if len(positions) != 3:
            raise ValueError(f"Expected 3 position patterns, found {len(positions)}")

        # Sort positions by row, then col
        sorted_pos = sorted(positions)

        # Calculate distances between patterns
        pos1, pos2, pos3 = sorted_pos

        # Determine version based on spacing
        # Version 1: distance 13, Version 2: distance 17
        dist1 = abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])
        dist2 = abs(pos3[0] - pos1[0]) + abs(pos3[1] - pos1[1])
        dist3 = abs(pos3[0] - pos2[0]) + abs(pos3[1] - pos2[1])

        max_dist = max(dist1, dist2, dist3)

        if max_dist <= 15:  # Around 13
            version = 1
            size = 21
        else:  # Around 17 or more
            version = 2
            size = 25

        # Determine rotation based on pattern arrangement
        # Standard: top-left (0,0), top-right (0, size-8), bottom-left (size-8, 0)

        # Find which pattern is top-left in standard orientation
        # Look for the pattern that forms a right angle with the other two

        def get_rotation(p1, p2, p3):
            """Determine rotation from three pattern positions"""
            # Sort by row first, then col
            all_p = [p1, p2, p3]

            # Find top-left (min row, min col)
            top_left = min(all_p, key=lambda p: (p[0], p[1]))

            # Find if second pattern is to the right or below
            others = [p for p in all_p if p != top_left]

            # Check arrangement
            if top_left[0] < min(others, key=lambda p: p[0])[0]:
                # Top-left is in the top row
                if top_left[1] < min(others, key=lambda p: p[1])[1]:
                    # Standard orientation (0 degrees)
                    return 0
                else:
                    # 90 degrees
                    return 90
            else:
                # Top-left is not in the top row
                if top_left[1] < min(others, key=lambda p: p[1])[1]:
                    # 270 degrees
                    return 270
                else:
                    # 180 degrees
                    return 180

        # Determine actual top-left corner and rotation
        # Analyze the pattern configuration
        rows = [p[0] for p in positions]
        cols = [p[1] for p in positions]

        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        # Find which pattern is at each corner
        top_left_pattern = None
        rotation = 0

        # Check each possible rotation
        for pos in positions:
            # Count how many patterns are aligned with this one
            same_row = sum(1 for p in positions if abs(p[0] - pos[0]) < 2)
            same_col = sum(1 for p in positions if abs(p[1] - pos[1]) < 2)

            # Top-left corner should have one pattern in same row and one in same col
            if same_row == 2 and same_col == 1:
                # This is likely top-left in current orientation
                if pos[0] == min_row and pos[1] == min_col:
                    rotation = 0
                    top_left_pattern = pos
                elif pos[0] == min_row and pos[1] == max_col:
                    rotation = 90
                    top_left_pattern = (min_row, max_col - size + 8)
                elif pos[0] == max_row and pos[1] == max_col:
                    rotation = 180
                    top_left_pattern = (max_row - size + 8, max_col - size + 8)
                elif pos[0] == max_row and pos[1] == min_col:
                    rotation = 270
                    top_left_pattern = (max_row - size + 8, min_col)
                break
            elif same_row == 1 and same_col == 2:
                # This is likely top-left in current orientation
                if pos[0] == min_row and pos[1] == min_col:
                    rotation = 0
                    top_left_pattern = pos
                elif pos[0] == min_row and pos[1] == max_col:
                    rotation = 90
                    top_left_pattern = (min_row, max_col - size + 8)
                elif pos[0] == max_row and pos[1] == max_col:
                    rotation = 180
                    top_left_pattern = (max_row - size + 8, max_col - size + 8)
                elif pos[0] == max_row and pos[1] == min_col:
                    rotation = 270
                    top_left_pattern = (max_row - size + 8, min_col)
                break

        # If still not found, use simple approach
        if top_left_pattern is None:
            # Just use the minimum row/col position
            top_left_pattern = (min_row, min_col)
            rotation = 0

        return top_left_pattern[0], top_left_pattern[1], version, rotation

    def extract_and_rotate_qr(self, matrix: np.ndarray, row: int, col: int, version: int, rotation: int) -> np.ndarray:
        """
        Extract QR code from matrix and rotate to standard orientation
        """
        size = 21 if version == 1 else 25

        # Extract QR region
        qr = matrix[row:row + size, col:col + size].copy()

        # Rotate to standard orientation
        if rotation == 90:
            qr = np.rot90(qr, k=3)  # Rotate 270 degrees clockwise = 90 counter-clockwise
        elif rotation == 180:
            qr = np.rot90(qr, k=2)
        elif rotation == 270:
            qr = np.rot90(qr, k=1)

        return qr

    def extract_payload_zigzag(self, qr: np.ndarray, mask: np.ndarray) -> List[int]:
        """
        Extract payload bits from QR matrix using reverse zigzag
        Must match the encoding zigzag pattern exactly
        """
        size = qr.shape[0]
        bits = []

        # Start from rightmost column
        col = size - 1
        going_up = True

        # Zigzag extraction: process column pairs from right to left
        while col > 0:
            # Get the two columns in this pair
            col_right = col
            col_left = col - 1

            # Determine row range based on direction
            if going_up:
                rows = range(size - 1, -1, -1)  # Bottom to top
            else:
                rows = range(0, size)  # Top to bottom

            # Extract from the column pair
            for row in rows:
                # Extract right column first, then left column
                for c in [col_right, col_left]:
                    # Skip timing column
                    if c == 6:
                        continue

                    # Extract if not reserved
                    if mask[row, c] == 0:
                        bits.append(int(qr[row, c]))

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

        return bits

    def parse_payload(self, bits: List[int]) -> str:
        """
        Parse payload bits to extract message

        Format: [length_byte][char1_byte][ec1_byte][char2_byte][ec2_byte]...
        """
        if len(bits) < 8:
            raise ValueError("Insufficient bits for payload")

        # Extract length byte
        length_bits = bits[0:8]
        length = 0
        for bit in length_bits:
            length = (length << 1) | bit

        # Extract message characters and error correction bytes
        message_chars = []
        bit_idx = 8

        for _ in range(length):
            if bit_idx + 16 > len(bits):
                raise ValueError("Insufficient bits for message")

            # Extract character byte
            char_bits = bits[bit_idx:bit_idx + 8]
            char_val = 0
            for bit in char_bits:
                char_val = (char_val << 1) | bit

            # Extract error correction byte (skip for now, can verify later)
            ec_bits = bits[bit_idx + 8:bit_idx + 16]

            message_chars.append(chr(char_val))
            bit_idx += 16

        return ''.join(message_chars)

    def create_mask_for_version(self, version: int) -> np.ndarray:
        """
        Create mask for reserved positions in QR code
        """
        size = 21 if version == 1 else 25
        mask = np.zeros((size, size), dtype=int)

        # Position patterns (3 corners)
        positions = [(0, 0), (0, size - 8), (size - 8, 0)]
        for row, col in positions:
            mask[row:row + 8, col:col + 8] = 1

        # Timing patterns
        for i in range(8, size - 8):
            mask[6, i] = 1
            mask[i, 6] = 1

        # Alignment pattern (version 2 only)
        if version == 2:
            mask[16:21, 16:21] = 1  # 5x5 centered at (18, 18)

        return mask

    def decode(self, hex_string: str) -> str:
        """
        Decode QR code hex string to original message

        Steps:
        1. Parse hex string to 32x32 matrix
        2. Find position patterns
        3. Determine QR location, version, and rotation
        4. Extract and rotate QR code
        5. Reverse logistic map encryption
        6. Extract payload via zigzag
        7. Parse payload to get message
        """
        # Step 1: Parse hex to matrix
        matrix_32 = hex_string_to_matrix(hex_string, 32)

        # Step 2: Find position patterns
        positions = self.find_position_patterns(matrix_32)

        if len(positions) != 3:
            raise ValueError(f"Could not find exactly 3 position patterns (found {len(positions)})")

        # Step 3: Determine location and rotation
        row, col, version, rotation = self.determine_qr_location_and_rotation(positions)

        # Step 4: Extract and rotate
        qr_encrypted = self.extract_and_rotate_qr(matrix_32, row, col, version, rotation)

        # Step 5: Reverse logistic map
        qr_decrypted = reverse_logistic_encryption(qr_encrypted)

        # Step 6: Create mask and extract payload
        mask = self.create_mask_for_version(version)
        payload_bits = self.extract_payload_zigzag(qr_decrypted, mask)

        # Step 7: Parse payload
        message = self.parse_payload(payload_bits)

        return message


# Convenience function
def decode_qr(hex_string: str) -> str:
    """
    Decode a QR code hex string to original message
    """
    decoder = QRDecoder()
    return decoder.decode(hex_string)
