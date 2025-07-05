"""
Mock PyBoy instances and test fixtures for emulator testing.

This module provides mock implementations of PyBoy classes and methods
for testing without requiring actual ROM files or SDL dependencies.
"""

import numpy as np
from PIL import Image


class MockPyBoy:
    """Mock PyBoy instance for testing."""

    def __init__(self, rom_path: str = "test_rom.gb"):
        self.rom_path = rom_path
        self.cartridge_title = "Test Game"
        self.is_running = True
        self._tick_count = 0
        self._screen_buffer = np.zeros((144, 160, 3), dtype=np.uint8)
        self._button_states: dict[str, bool] = {}

    def tick(self) -> None:
        """Simulate one frame tick."""
        self._tick_count += 1

    def reset(self) -> None:
        """Reset the emulator state."""
        self._tick_count = 0
        self._button_states.clear()

    def stop(self) -> None:
        """Stop the emulator."""
        self.is_running = False

    def button_press(self, button: str) -> None:
        """Simulate button press."""
        valid_buttons = ["a", "b", "select", "start", "up", "down", "left", "right"]
        if button.lower() not in valid_buttons:
            raise ValueError(f"Invalid button: {button}")
        self._button_states[button.lower()] = True

    def button_release(self, button: str) -> None:
        """Simulate button release."""
        valid_buttons = ["a", "b", "select", "start", "up", "down", "left", "right"]
        if button.lower() not in valid_buttons:
            raise ValueError(f"Invalid button: {button}")
        self._button_states[button.lower()] = False

    def send_input(self, input_data: list[str]) -> None:
        """Simulate input sequence."""
        for button in input_data:
            self.button_press(button)
            self.tick()
            self.button_release(button)

    def screen_image(self) -> Image.Image:
        """Return a mock screen image."""
        # Create a simple test pattern
        image_array = np.random.randint(0, 255, (144, 160, 3), dtype=np.uint8)
        return Image.fromarray(image_array)

    def screen_ndarray(self) -> np.ndarray:
        """Return screen as numpy array."""
        return self._screen_buffer

    def save_state(self, file_path: str) -> None:
        """Save current state to file."""
        # Mock save state - just write some dummy data
        with open(file_path, "wb") as f:
            f.write(b"MOCK_SAVE_STATE_DATA" + str(self._tick_count).encode())

    def load_state(self, file_path: str) -> None:
        """Load state from file."""
        # Mock load state - just verify file exists
        with open(file_path, "rb") as f:
            data = f.read()
            if not data.startswith(b"MOCK_SAVE_STATE_DATA"):
                raise ValueError("Invalid save state file")

    def get_memory_value(self, address: int) -> int:
        """Get memory value at address."""
        return address % 256  # Mock value based on address

    def set_memory_value(self, address: int, value: int) -> None:
        """Set memory value at address."""
        pass  # Mock implementation

    @property
    def tick_count(self) -> int:
        """Get current tick count."""
        return self._tick_count

    @property
    def button_states(self) -> dict[str, bool]:
        """Get current button states."""
        return self._button_states.copy()


class MockGameWindowPlugin:
    """Mock game window plugin for PyBoy."""

    def __init__(self):
        self.enabled = True

    def post_tick(self) -> None:
        """Called after each tick."""
        pass

    def window_title(self) -> str:
        """Get window title."""
        return "Mock Game Window"


def create_mock_pyboy(rom_path: str = "test_rom.gb", **kwargs) -> MockPyBoy:
    """Create a configured mock PyBoy instance."""
    mock_pyboy = MockPyBoy(rom_path)

    # Apply any additional configuration
    for key, value in kwargs.items():
        if hasattr(mock_pyboy, key):
            setattr(mock_pyboy, key, value)

    return mock_pyboy


def create_test_rom_data(size_kb: int = 32) -> bytes:
    """Create mock ROM data for testing."""
    # Nintendo Game Boy ROM header
    header = bytearray(0x150)

    # Entry point (usually JP instruction)
    header[0x100:0x104] = [0x00, 0xC3, 0x50, 0x01]

    # Nintendo logo (simplified)
    header[0x104:0x134] = [0xCE, 0xED] * 24

    # Title (up to 16 characters)
    title = b"TEST ROM\x00\x00\x00\x00\x00\x00\x00\x00"
    header[0x134:0x144] = title[:16]

    # Cartridge type (0x00 = ROM ONLY)
    header[0x147] = 0x00

    # ROM size (0x00 = 32KB)
    header[0x148] = 0x00

    # RAM size (0x00 = None)
    header[0x149] = 0x00

    # Calculate header checksum
    checksum = 0
    for byte in header[0x134:0x14D]:
        checksum = (checksum - byte - 1) & 0xFF
    header[0x14D] = checksum

    # Pad to requested size
    total_size = size_kb * 1024
    rom_data = bytes(header) + b"\x00" * (total_size - len(header))

    return rom_data


def create_mock_save_state() -> bytes:
    """Create mock save state data."""
    return b"MOCK_SAVE_STATE_DATA" + b"\x00" * 1000


# Pytest fixtures for easier use in tests
def pytest_mock_pyboy():
    """Pytest fixture for mock PyBoy."""
    return create_mock_pyboy()


def pytest_test_rom_data():
    """Pytest fixture for test ROM data."""
    return create_test_rom_data()
