"""
Utility functions for QR code generation and processing
"""
import numpy as np
from typing import List, Tuple


def generate_position_pattern() -> np.ndarray:
    """
    Generate the 8x8 position detection pattern
    Pattern is 7x7 with 1-pixel white separator
    """
    pattern = np.zeros((8, 8), dtype=int)

    # Outer 7x7 black border
    pattern[0:7, 0] = 1
    pattern[0:7, 6] = 1
    pattern[0, 0:7] = 1
    pattern[6, 0:7] = 1

    # Inner 3x3 black square
    pattern[2:5, 2:5] = 1

    # White separator (8th row and column are already 0)
    return pattern


def generate_alignment_pattern() -> np.ndarray:
    """
    Generate the 5x5 alignment pattern
    """
    pattern = np.ones((5, 5), dtype=int)
    # White ring
    pattern[1:4, 1:4] = 0
    # Black center
    pattern[2, 2] = 1
    return pattern


def generate_timing_patterns(version: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate timing patterns for row 6 and column 6
    Returns: (horizontal_timing, vertical_timing)
    """
    size = 21 if version == 1 else 25

    # Horizontal timing pattern (row 6)
    h_timing = np.array([1 if i % 2 == 0 else 0 for i in range(size)])

    # Vertical timing pattern (column 6)
    v_timing = np.array([1 if i % 2 == 0 else 0 for i in range(size)])

    return h_timing, v_timing


def calculate_error_correction_bit(byte_value: int) -> int:
    """
    Calculate error correction bit by XORing all 8 bits
    """
    xor_result = 0
    for i in range(8):
        xor_result ^= (byte_value >> i) & 1
    return xor_result


def generate_payload(message: str) -> List[int]:
    """
    Generate payload with format: [length][char1][ec1][char2][ec2]...
    """
    payload = []

    # First byte: message length
    length = len(message)
    payload.append(length)

    # For each character, add the character byte and its error correction byte
    for char in message:
        char_byte = ord(char)
        ec_bit = calculate_error_correction_bit(char_byte)
        payload.append(char_byte)
        payload.append(ec_bit)  # EC bit padded to full byte

    return payload


def generate_logistic_map(size: int) -> List[int]:
    """
    Generate logistic map with x(n+1) = r*x(n)*(1-x(n))
    x(0) = 0.1, r = 4.0
    Size should be (QR_size^2 / 8) + 1

    IMPORTANT: Use double precision floating point
    """
    logistic_map = []
    x = 0.1  # Initial value (as double)
    r = 4.0  # Parameter

    for _ in range(size):
        # Convert to integer [0, 255] using floor
        logistic_map.append(int(x * 255))
        # Update x using logistic map formula
        x = r * x * (1.0 - x)

    return logistic_map


def apply_logistic_encryption(qr_matrix: np.ndarray) -> np.ndarray:
    """
    Apply logistic map encryption to QR code
    Each byte in logistic map XORs with 8 bits of QR code

    Important: MSB of QR 8-bit group XORs with LSB of logistic map byte
    """
    size = qr_matrix.shape[0]
    map_size = (size * size) // 8 + 1
    logistic_map = generate_logistic_map(map_size)

    # Flatten QR matrix to 1D array in ROW-MAJOR order for logistic map
    qr_flat = qr_matrix.flatten(order='C')  # Row-major (C order)

    # Apply XOR
    encrypted = qr_flat.copy()
    for i in range(map_size):
        logistic_byte = logistic_map[i]

        # XOR 8 bits at a time
        for bit_pos in range(8):
            qr_index = i * 8 + bit_pos
            if qr_index >= len(qr_flat):
                break

            # Extract bit from logistic map byte
            # bit_pos 0 → logistic bit 0 (LSB), bit_pos 7 → logistic bit 7 (MSB)
            logistic_bit = (logistic_byte >> bit_pos) & 1

            # XOR with QR bit
            encrypted[qr_index] ^= logistic_bit

    # Reshape back to matrix in ROW-MAJOR order
    return encrypted.reshape(size, size, order='C')


def reverse_logistic_encryption(qr_matrix: np.ndarray) -> np.ndarray:
    """
    Reverse logistic map encryption (XOR is self-inverse)
    """
    return apply_logistic_encryption(qr_matrix)


def matrix_to_hex_string(qr_matrix: np.ndarray) -> str:
    """
    Convert QR matrix to hex string format
    Read row by row (row-major order), pack into 32-bit integers (big endian)
    Format: 0x[hex] with lowercase, remove leading zeros
    Special case: 0x0 for zero
    """
    size = qr_matrix.shape[0]
    # Flatten in row-major order (C order)
    bits = qr_matrix.flatten(order='C')

    hex_strings = []
    num_bits = len(bits)

    # Process 32 bits at a time
    for start_idx in range(0, num_bits, 32):
        # Get up to 32 bits
        chunk_size = min(32, num_bits - start_idx)
        chunk = bits[start_idx:start_idx + chunk_size]

        # Convert to integer (big endian - first bit is MSB)
        value = 0
        for bit in chunk:
            value = (value << 1) | bit

        # Format as hex
        if value == 0:
            hex_strings.append("0x0")
        else:
            hex_strings.append(f"0x{value:x}")

    return "".join(hex_strings)


def hex_string_to_matrix(hex_string: str, size: int) -> np.ndarray:
    """
    Convert hex string to matrix
    """
    # Remove all 0x prefixes and concatenate
    hex_values = hex_string.split("0x")[1:]  # Skip first empty element

    # Convert each hex value to binary
    all_bits = []
    for i, hex_val in enumerate(hex_values):
        value = int(hex_val, 16)

        # Determine number of bits for this chunk
        # Last chunk might have fewer than 32 bits
        total_bits_needed = size * size
        bits_so_far = i * 32
        bits_in_chunk = min(32, total_bits_needed - bits_so_far)

        # Convert to binary with proper bit count
        binary = format(value, f'0{bits_in_chunk}b')
        all_bits.extend([int(b) for b in binary])

    # Convert to matrix in row-major order (C order)
    matrix = np.array(all_bits[:size*size]).reshape(size, size, order='C')
    return matrix


def get_padding_sequence() -> List[int]:
    """
    Get the padding sequence: 11101100 00010001 (repeated)
    Returns as list of bits
    """
    return [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]
