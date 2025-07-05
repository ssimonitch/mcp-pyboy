"""
Example test to verify testing infrastructure works correctly.

This test file demonstrates the testing setup and can be used to verify
that all test dependencies and fixtures are working properly.
"""

from pathlib import Path

import pytest

from tests.fixtures.mock_pyboy import create_mock_pyboy, create_test_rom_data


class TestInfrastructure:
    """Test the testing infrastructure itself."""

    def test_pytest_works(self):
        """Basic test to ensure pytest is working."""
        assert True

    def test_async_support(self):
        """Test that async test support is working."""
        import asyncio

        async def async_operation():
            await asyncio.sleep(0.001)
            return "success"

        # Run async operation
        result = asyncio.run(async_operation())
        assert result == "success"

    def test_temp_dir_fixture(self, temp_dir):
        """Test that temp_dir fixture works."""
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_mock_pyboy_fixture(self, mock_pyboy):
        """Test that mock_pyboy fixture works."""
        assert hasattr(mock_pyboy, "tick")
        assert hasattr(mock_pyboy, "cartridge_title")
        assert mock_pyboy.cartridge_title == "Test Game"

    def test_mock_rom_path_fixture(self, mock_rom_path):
        """Test that mock_rom_path fixture works."""
        assert isinstance(mock_rom_path, Path)
        assert mock_rom_path.exists()
        assert mock_rom_path.suffix == ".gb"

    def test_sample_mcp_request_fixture(self, sample_mcp_request):
        """Test that MCP request fixture works."""
        assert "jsonrpc" in sample_mcp_request
        assert sample_mcp_request["jsonrpc"] == "2.0"
        assert "method" in sample_mcp_request


class TestMockPyBoy:
    """Test the mock PyBoy implementation."""

    def test_mock_pyboy_creation(self):
        """Test creating a mock PyBoy instance."""
        pyboy = create_mock_pyboy()
        assert pyboy.cartridge_title == "Test Game"
        assert pyboy.is_running is True
        assert pyboy.tick_count == 0

    def test_mock_pyboy_tick(self):
        """Test PyBoy tick functionality."""
        pyboy = create_mock_pyboy()
        initial_count = pyboy.tick_count

        pyboy.tick()
        assert pyboy.tick_count == initial_count + 1

    def test_mock_pyboy_buttons(self):
        """Test PyBoy button functionality."""
        pyboy = create_mock_pyboy()

        # Test button press
        pyboy.button_press("a")
        assert pyboy.button_states["a"] is True

        # Test button release
        pyboy.button_release("a")
        assert pyboy.button_states["a"] is False

        # Test invalid button
        with pytest.raises(ValueError):
            pyboy.button_press("invalid_button")

    def test_mock_pyboy_screen(self):
        """Test PyBoy screen functionality."""
        pyboy = create_mock_pyboy()

        # Test screen image
        image = pyboy.screen_image()
        assert image.size == (160, 144)

        # Test screen array
        array = pyboy.screen_ndarray()
        assert array.shape == (144, 160, 3)

    def test_mock_pyboy_reset(self):
        """Test PyBoy reset functionality."""
        pyboy = create_mock_pyboy()

        # Make some changes
        pyboy.tick()
        pyboy.button_press("a")

        # Reset
        pyboy.reset()

        # Verify reset state
        assert pyboy.tick_count == 0
        assert len(pyboy.button_states) == 0


class TestROMData:
    """Test ROM data creation and validation."""

    def test_create_test_rom_data(self):
        """Test creating test ROM data."""
        rom_data = create_test_rom_data(size_kb=32)

        # Check size
        assert len(rom_data) == 32 * 1024

        # Check header format
        assert rom_data[0x100:0x104] == bytes([0x00, 0xC3, 0x50, 0x01])

        # Check title area
        title_start = rom_data[0x134:0x144]
        assert title_start.startswith(b"TEST ROM")

    def test_different_rom_sizes(self):
        """Test creating ROMs of different sizes."""
        for size_kb in [32, 64, 128, 256]:
            rom_data = create_test_rom_data(size_kb=size_kb)
            assert len(rom_data) == size_kb * 1024


@pytest.mark.asyncio
class TestAsyncFixtures:
    """Test async fixtures and operations."""

    async def test_mock_mcp_server_fixture(self, mock_mcp_server):
        """Test async MCP server fixture."""
        assert hasattr(mock_mcp_server, "start")
        assert hasattr(mock_mcp_server, "stop")
        assert hasattr(mock_mcp_server, "handle_request")

        # Test that these are async mocks
        await mock_mcp_server.start()
        await mock_mcp_server.stop()

    async def test_mock_game_session_fixture(self, mock_game_session):
        """Test async game session fixture."""
        assert mock_game_session.game_loaded is True
        assert mock_game_session.current_rom == "test_game.gb"

        # Test async methods
        await mock_game_session.load_rom("test.gb")
        await mock_game_session.capture_screen()


# Mark some tests for different categories
@pytest.mark.unit
class TestUnitCategory:
    """Tests marked as unit tests."""

    def test_unit_marked_test(self):
        """A test specifically marked as a unit test."""
        assert True


@pytest.mark.integration
class TestIntegrationCategory:
    """Tests marked as integration tests."""

    def test_integration_marked_test(self):
        """A test specifically marked as an integration test."""
        assert True


@pytest.mark.slow
class TestSlowCategory:
    """Tests marked as slow tests."""

    def test_slow_marked_test(self):
        """A test specifically marked as slow."""
        import time

        time.sleep(0.1)  # Simulate slow operation
        assert True
