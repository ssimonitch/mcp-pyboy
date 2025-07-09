"""
Integration tests for PyBoy emulator wrapper.

Tests the PyBoyEmulator class with real PyBoy instances using synthetic ROMs.
Focuses on testing our wrapper's logic, error handling, and LLM-friendly interface.
"""

from pathlib import Path

import pytest

from mcp_server.emulator import (
    EmulatorStateError,
    PyBoyEmulator,
    ROMError,
)
from tests.mcp_server.fixtures.rom_generation import create_test_rom_data


@pytest.fixture
def synthetic_rom(tmp_path: Path) -> Path:
    """Create a minimal valid GB ROM for testing."""
    rom_file = tmp_path / "test.gb"
    rom_data = create_test_rom_data(size_kb=32)
    rom_file.write_bytes(rom_data)
    return rom_file


@pytest.fixture
def invalid_rom(tmp_path: Path) -> Path:
    """Create an invalid ROM file for error testing."""
    rom_file = tmp_path / "invalid.gb"
    rom_file.write_bytes(b"INVALID ROM DATA")
    return rom_file


@pytest.fixture
def non_gb_file(tmp_path: Path) -> Path:
    """Create a non-GB file for extension testing."""
    file_path = tmp_path / "not_a_rom.txt"
    file_path.write_text("This is not a ROM file")
    return file_path


@pytest.mark.integration
class TestPyBoyEmulatorInitialization:
    """Test emulator initialization and configuration."""

    def test_init_headless_by_default(self):
        """Test that emulator initializes in headless mode by default."""
        emulator = PyBoyEmulator()
        assert emulator.headless is True
        assert emulator.pyboy is None
        assert emulator.current_rom_path is None
        assert emulator.is_running is False

    def test_init_with_gui_mode(self):
        """Test emulator initialization with GUI mode."""
        emulator = PyBoyEmulator(headless=False)
        assert emulator.headless is False
        assert not emulator.is_ready()


@pytest.mark.integration
class TestPyBoyEmulatorLifecycle:
    """Test emulator start/stop lifecycle."""

    def test_start_when_not_running(self):
        """Test starting emulator when not running."""
        emulator = PyBoyEmulator()
        emulator.start()
        assert emulator.is_running is True

    def test_start_when_already_running(self):
        """Test error when starting already running emulator."""
        emulator = PyBoyEmulator()
        emulator.start()

        with pytest.raises(EmulatorStateError) as exc_info:
            emulator.start()

        assert "already running" in str(exc_info.value)
        assert "stop() first" in str(exc_info.value)

    def test_stop_when_running(self, synthetic_rom):
        """Test stopping running emulator."""
        emulator = PyBoyEmulator()
        emulator.load_rom(synthetic_rom)

        assert emulator.is_running is True
        assert emulator.pyboy is not None

        emulator.stop()

        assert emulator.is_running is False
        assert emulator.pyboy is None
        assert emulator.current_rom_path is None

    def test_stop_when_not_running(self):
        """Test that stopping non-running emulator is safe."""
        emulator = PyBoyEmulator()
        # Should not raise any errors
        emulator.stop()
        assert emulator.is_running is False

    def test_multiple_stops_are_safe(self, synthetic_rom):
        """Test that calling stop multiple times is safe."""
        emulator = PyBoyEmulator()
        emulator.load_rom(synthetic_rom)

        # Stop multiple times
        emulator.stop()
        emulator.stop()
        emulator.stop()

        assert emulator.is_running is False


@pytest.mark.integration
@pytest.mark.emulator
class TestPyBoyEmulatorROMLoading:
    """Test ROM loading functionality."""

    def test_load_rom_success(self, synthetic_rom):
        """Test successful ROM loading with real PyBoy."""
        emulator = PyBoyEmulator()
        emulator.load_rom(synthetic_rom)

        assert emulator.is_running is True
        assert emulator.current_rom_path == synthetic_rom
        assert emulator.pyboy is not None
        assert emulator.is_ready() is True

        # Verify real PyBoy instance was created
        assert hasattr(emulator.pyboy, "tick")
        assert hasattr(emulator.pyboy, "screen")

        # Cleanup
        emulator.stop()

    def test_load_rom_with_gui_mode(self, synthetic_rom):
        """Test ROM loading in GUI mode (headless=False)."""
        emulator = PyBoyEmulator(headless=False)
        emulator.load_rom(synthetic_rom)

        assert emulator.is_running is True
        assert emulator.pyboy is not None

        # Cleanup
        emulator.stop()

    def test_load_rom_file_not_found(self):
        """Test error when ROM file doesn't exist."""
        emulator = PyBoyEmulator()

        with pytest.raises(ROMError) as exc_info:
            emulator.load_rom("nonexistent.gb")

        error_msg = str(exc_info.value)
        assert "not found" in error_msg
        assert "Check the file path" in error_msg

    def test_load_rom_invalid_extension(self, non_gb_file):
        """Test error when file has invalid extension."""
        emulator = PyBoyEmulator()

        with pytest.raises(ROMError) as exc_info:
            emulator.load_rom(non_gb_file)

        error_msg = str(exc_info.value)
        assert "Invalid ROM file extension" in error_msg
        assert ".gb and .gbc files are supported" in error_msg

    def test_load_rom_replaces_existing(self, synthetic_rom, tmp_path):
        """Test that loading a new ROM stops the previous one."""
        emulator = PyBoyEmulator()

        # Load first ROM
        emulator.load_rom(synthetic_rom)
        first_pyboy = emulator.pyboy

        # Create second ROM
        second_rom = tmp_path / "second.gb"
        second_rom.write_bytes(create_test_rom_data())

        # Load second ROM
        emulator.load_rom(second_rom)

        assert emulator.current_rom_path == second_rom
        assert emulator.pyboy != first_pyboy

        # Cleanup
        emulator.stop()

    def test_load_rom_with_invalid_data(self, invalid_rom):
        """Test handling of ROMs with invalid data."""
        emulator = PyBoyEmulator()

        # PyBoy should handle invalid ROM data gracefully
        # Our wrapper should catch and convert to LLM-friendly error
        with pytest.raises((ROMError, EmulatorStateError)):
            emulator.load_rom(invalid_rom)


@pytest.mark.integration
class TestPyBoyEmulatorInfo:
    """Test ROM info retrieval."""

    def test_get_rom_info_success(self, synthetic_rom):
        """Test getting ROM info when loaded."""
        emulator = PyBoyEmulator()
        emulator.load_rom(synthetic_rom)

        info = emulator.get_rom_info()

        assert info["name"] == "test.gb"
        assert info["path"] == str(synthetic_rom)
        assert info["size"] == 32 * 1024  # 32KB
        assert info["extension"] == ".gb"
        assert info["is_running"] is True

        # Cleanup
        emulator.stop()

    def test_get_rom_info_no_rom_loaded(self):
        """Test error when getting info with no ROM."""
        emulator = PyBoyEmulator()

        with pytest.raises(EmulatorStateError) as exc_info:
            emulator.get_rom_info()

        error_msg = str(exc_info.value)
        assert "No ROM is currently loaded" in error_msg
        assert "load_rom()" in error_msg


@pytest.mark.integration
@pytest.mark.emulator
class TestPyBoyEmulatorAccess:
    """Test PyBoy instance access."""

    def test_get_pyboy_instance_success(self, synthetic_rom):
        """Test getting PyBoy instance when running."""
        emulator = PyBoyEmulator()
        emulator.load_rom(synthetic_rom)

        pyboy = emulator.get_pyboy_instance()
        assert pyboy is not None

        # Verify it's a real PyBoy instance
        assert hasattr(pyboy, "tick")
        assert hasattr(pyboy, "screen")
        assert hasattr(pyboy, "button")

        # Cleanup
        emulator.stop()

    def test_get_pyboy_instance_not_running(self):
        """Test error when getting instance with no emulator."""
        emulator = PyBoyEmulator()

        with pytest.raises(EmulatorStateError) as exc_info:
            emulator.get_pyboy_instance()

        error_msg = str(exc_info.value)
        assert "Emulator is not running" in error_msg
        assert "load_rom()" in error_msg


@pytest.mark.integration
class TestPyBoyEmulatorContextManager:
    """Test context manager functionality."""

    def test_context_manager_cleanup(self, synthetic_rom):
        """Test that context manager cleans up resources."""
        with PyBoyEmulator() as emulator:
            emulator.load_rom(synthetic_rom)
            assert emulator.is_running is True

        # After exiting context, emulator should be stopped
        assert emulator.is_running is False
        assert emulator.pyboy is None

    def test_context_manager_with_exception(self, synthetic_rom):
        """Test cleanup even when exception occurs."""
        emulator = PyBoyEmulator()

        with pytest.raises(ValueError):
            with emulator:
                emulator.load_rom(synthetic_rom)
                raise ValueError("Test exception")

        # Cleanup should still happen
        assert emulator.is_running is False


@pytest.mark.unit
class TestLLMFriendlyErrors:
    """Test that errors are LLM-friendly with actionable suggestions."""

    def test_rom_not_found_suggestion(self):
        """Test helpful suggestion for missing ROM."""
        emulator = PyBoyEmulator()

        with pytest.raises(ROMError) as exc_info:
            emulator.load_rom("/fake/path/game.gb")

        error_msg = str(exc_info.value)
        # Should contain actionable suggestion
        assert "Check the file path" in error_msg
        assert "ensure the ROM file exists" in error_msg

    def test_invalid_extension_suggestion(self, non_gb_file):
        """Test helpful suggestion for invalid file types."""
        emulator = PyBoyEmulator()

        with pytest.raises(ROMError) as exc_info:
            emulator.load_rom(non_gb_file)

        error_msg = str(exc_info.value)
        assert "Invalid ROM file extension" in error_msg
        assert ".gb and .gbc files are supported" in error_msg


@pytest.mark.integration
@pytest.mark.emulator
@pytest.mark.slow
class TestPyBoyIntegration:
    """Test integration with real PyBoy functionality."""

    def test_pyboy_basic_operations(self, synthetic_rom):
        """Test basic PyBoy operations work through our wrapper."""
        emulator = PyBoyEmulator()
        emulator.load_rom(synthetic_rom)

        pyboy = emulator.get_pyboy_instance()

        # Test basic PyBoy operations
        pyboy.tick()  # Should not raise

        # Test screen access
        assert hasattr(pyboy.screen, "ndarray")
        screen_data = pyboy.screen.ndarray
        assert screen_data.shape == (144, 160, 4)  # Game Boy screen dimensions (RGBA)

        # Test button input
        pyboy.button("a")  # Should not raise

        # Cleanup
        emulator.stop()

    def test_headless_mode_works(self, synthetic_rom):
        """Test that headless mode works correctly."""
        emulator = PyBoyEmulator(headless=True)
        emulator.load_rom(synthetic_rom)

        # Should create PyBoy instance successfully
        assert emulator.pyboy is not None
        assert emulator.is_ready() is True

        # Basic operations should work
        emulator.pyboy.tick()
        screen = emulator.pyboy.screen.ndarray
        assert screen is not None

        # Cleanup
        emulator.stop()
