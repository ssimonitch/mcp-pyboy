"""
Test ROM generation and fixtures for emulator testing.

This module provides utilities for creating synthetic Game Boy ROM files
for testing without requiring actual ROM files or copyright concerns.
"""


def create_test_rom_data(size_kb: int = 32) -> bytes:
    """
    Create synthetic Game Boy ROM data for testing.

    Generates a minimal but valid Game Boy ROM with proper header structure,
    checksums, and padding. Safe to use in CI/CD and no copyright concerns.

    Args:
        size_kb: Size of ROM in KB (default: 32KB)

    Returns:
        bytes: Valid Game Boy ROM data

    ROM Structure:
    - 0x100-0x103: Entry point (JP instruction)
    - 0x104-0x133: Nintendo logo (simplified)
    - 0x134-0x143: Game title (16 bytes)
    - 0x147: Cartridge type (ROM ONLY)
    - 0x148: ROM size indicator
    - 0x149: RAM size indicator
    - 0x14D: Header checksum

    Note: PyBoy outputs screen data in RGBA format (144x160x4)
    """
    # Nintendo Game Boy ROM header (0x150 bytes)
    header = bytearray(0x150)

    # Entry point - JP instruction to 0x0150
    header[0x100:0x104] = [0x00, 0xC3, 0x50, 0x01]

    # Simplified Nintendo logo (real logo is copyrighted)
    # Using a pattern that passes basic validation
    header[0x104:0x134] = [0xCE, 0xED] * 24

    # Game title (up to 16 characters, null-padded)
    title = b"TEST ROM\x00\x00\x00\x00\x00\x00\x00\x00"
    header[0x134:0x144] = title[:16]

    # Cartridge type: 0x00 = ROM ONLY (no MBC)
    header[0x147] = 0x00

    # ROM size: 0x00 = 32KB, 0x01 = 64KB, etc.
    if size_kb <= 32:
        header[0x148] = 0x00
    elif size_kb <= 64:
        header[0x148] = 0x01
    elif size_kb <= 128:
        header[0x148] = 0x02
    elif size_kb <= 256:
        header[0x148] = 0x03
    else:
        header[0x148] = 0x04  # 512KB

    # RAM size: 0x00 = None
    header[0x149] = 0x00

    # Calculate header checksum (sum of bytes 0x134-0x14C)
    checksum = 0
    for byte in header[0x134:0x14D]:
        checksum = (checksum - byte - 1) & 0xFF
    header[0x14D] = checksum

    # Pad to requested size
    total_size = size_kb * 1024
    if total_size < len(header):
        total_size = len(header)

    rom_data = bytes(header) + b"\x00" * (total_size - len(header))

    return rom_data


def create_test_rom_with_title(title: str, size_kb: int = 32) -> bytes:
    """
    Create a test ROM with a custom title.

    Args:
        title: Game title (up to 16 characters)
        size_kb: Size of ROM in KB

    Returns:
        bytes: Valid Game Boy ROM data with custom title
    """
    rom_data = bytearray(create_test_rom_data(size_kb))

    # Update title
    title_bytes = title.encode("ascii")[:16].ljust(16, b"\x00")
    rom_data[0x134:0x144] = title_bytes

    # Recalculate checksum
    checksum = 0
    for byte in rom_data[0x134:0x14D]:
        checksum = (checksum - byte - 1) & 0xFF
    rom_data[0x14D] = checksum

    return bytes(rom_data)


def create_corrupted_rom_data(size_kb: int = 32) -> bytes:
    """
    Create intentionally corrupted ROM data for error testing.

    Args:
        size_kb: Size of ROM in KB

    Returns:
        bytes: Invalid ROM data that should trigger PyBoy errors
    """
    # Create ROM filled with invalid data
    total_size = size_kb * 1024
    return (b"CORRUPTED ROM DATA" * (total_size // 18 + 1))[:total_size]


def create_minimal_valid_rom() -> bytes:
    """
    Create the smallest possible valid Game Boy ROM.

    Returns:
        bytes: Minimal 32KB ROM for fast testing
    """
    return create_test_rom_data(size_kb=32)


# Pytest fixtures for easier use in tests
def pytest_test_rom_data():
    """Pytest fixture for test ROM data."""
    return create_test_rom_data()


def pytest_custom_rom_data():
    """Pytest fixture for custom ROM data."""
    return create_test_rom_with_title("PYTEST ROM")
