"""
Test fixtures and helpers for PyBoy emulator testing.

Provides utilities for creating test emulators with real PyBoy instances
and synthetic ROMs for integration testing.
"""

from pathlib import Path

import pytest

from mcp_server.emulator import PyBoyEmulator
from tests.mcp_server.fixtures.rom_generation import (
    create_corrupted_rom_data,
    create_test_rom_data,
    create_test_rom_with_title,
)


def create_emulator_with_rom(
    tmp_path: Path,
    headless: bool = True,
    rom_name: str = "test.gb",
    rom_title: str = "TEST ROM",
    size_kb: int = 32,
) -> tuple[PyBoyEmulator, Path]:
    """
    Create an emulator with a synthetic test ROM loaded using real PyBoy.

    Args:
        tmp_path: Pytest tmp_path fixture
        headless: Whether to run in headless mode (default: True)
        rom_name: Name for the test ROM file
        rom_title: Title to embed in the ROM
        size_kb: Size of ROM in KB

    Returns:
        tuple of (emulator, rom_path)
    """
    # Create synthetic ROM
    rom_path = tmp_path / rom_name
    if rom_title == "TEST ROM":
        rom_data = create_test_rom_data(size_kb=size_kb)
    else:
        rom_data = create_test_rom_with_title(rom_title, size_kb=size_kb)
    rom_path.write_bytes(rom_data)

    # Create emulator and load ROM with real PyBoy
    emulator = PyBoyEmulator(headless=headless)
    emulator.load_rom(rom_path)

    return emulator, rom_path


def assert_llm_friendly_error(exc: Exception, *expected_substrings: str) -> None:
    """
    Assert that an error message is LLM-friendly with actionable guidance.

    Args:
        exc: The exception to check
        expected_substrings: Strings that should appear in the error message
    """
    error_msg = str(exc)

    # Check that error is not too technical
    assert not error_msg.startswith("Traceback"), "Error should not include traceback"
    assert "at 0x" not in error_msg, "Error should not include memory addresses"

    # Check for expected content
    for substring in expected_substrings:
        assert substring in error_msg, f"Error should contain '{substring}'"

    # Check for actionable suggestions (should contain guidance words)
    suggestion_words = ["try", "check", "ensure", "use", "verify", "should", "must"]
    has_suggestion = any(word in error_msg.lower() for word in suggestion_words)
    assert has_suggestion, "Error should contain actionable suggestions"


def create_rom_file(
    path: Path, valid: bool = True, size_kb: int = 32, title: str = "TEST ROM"
) -> Path:
    """
    Create various ROM test scenarios.

    Args:
        path: Path where ROM should be created
        valid: Whether to create a valid ROM (True) or corrupted ROM (False)
        size_kb: Size of ROM in KB
        title: Game title to embed

    Returns:
        Path to created ROM
    """
    if valid:
        if title == "TEST ROM":
            rom_data = create_test_rom_data(size_kb=size_kb)
        else:
            rom_data = create_test_rom_with_title(title, size_kb=size_kb)
    else:
        rom_data = create_corrupted_rom_data(size_kb=size_kb)

    path.write_bytes(rom_data)
    return path


@pytest.fixture
def emulator_with_rom(tmp_path):
    """Pytest fixture that provides an emulator with ROM loaded using real PyBoy."""
    emulator, rom_path = create_emulator_with_rom(tmp_path)
    yield emulator, rom_path
    # Cleanup
    emulator.stop()


@pytest.fixture
def clean_emulator():
    """Pytest fixture for a clean PyBoyEmulator instance."""
    emulator = PyBoyEmulator()
    yield emulator
    # Cleanup
    emulator.stop()


class EmulatorTestHelper:
    """Helper class for common emulator testing patterns."""

    @staticmethod
    def assert_emulator_stopped(emulator: PyBoyEmulator) -> None:
        """Assert that emulator is in stopped state."""
        assert not emulator.is_running
        assert emulator.pyboy is None
        assert emulator.current_rom_path is None
        assert not emulator.is_ready()

    @staticmethod
    def assert_emulator_running(emulator: PyBoyEmulator, rom_path: Path) -> None:
        """Assert that emulator is running with given ROM."""
        assert emulator.is_running
        assert emulator.pyboy is not None
        assert emulator.current_rom_path == rom_path
        assert emulator.is_ready()

    @staticmethod
    def assert_real_pyboy_instance(pyboy) -> None:
        """Assert that object is a real PyBoy instance."""
        # Check for key PyBoy methods and attributes
        assert hasattr(pyboy, "tick"), "Should have tick method"
        assert hasattr(pyboy, "screen"), "Should have screen attribute"
        assert hasattr(pyboy, "button"), "Should have button method"
        assert hasattr(pyboy, "stop"), "Should have stop method"

        # Check screen has proper structure
        assert hasattr(pyboy.screen, "ndarray"), "Screen should have ndarray property"
        screen_data = pyboy.screen.ndarray
        assert screen_data.shape == (
            144,
            160,
            4,
        ), "Screen should be Game Boy dimensions (RGBA)"

    @staticmethod
    def create_rom_scenarios(tmp_path: Path) -> dict[str, Path]:
        """Create various ROM test scenarios for comprehensive testing."""
        return {
            "valid_32kb": create_rom_file(
                tmp_path / "valid.gb", valid=True, size_kb=32
            ),
            "valid_64kb": create_rom_file(
                tmp_path / "large.gb", valid=True, size_kb=64
            ),
            "corrupted": create_rom_file(
                tmp_path / "corrupt.gb", valid=False, size_kb=32
            ),
            "gbc_file": create_rom_file(tmp_path / "color.gbc", valid=True, size_kb=32),
            "custom_title": create_rom_file(
                tmp_path / "pokemon.gb", valid=True, title="POKEMON RED"
            ),
        }

    @staticmethod
    def test_basic_emulation_cycle(emulator: PyBoyEmulator) -> None:
        """Test a basic emulation cycle to verify PyBoy integration."""
        pyboy = emulator.get_pyboy_instance()

        # Test frame advancement
        pyboy.tick(5)  # Advance 5 frames

        # Test input
        pyboy.button("a")  # Press A button
        pyboy.tick(1)  # Process one frame

        # Test screen capture
        screen = pyboy.screen.ndarray
        assert screen is not None
        assert screen.shape == (144, 160, 4)  # RGBA format
