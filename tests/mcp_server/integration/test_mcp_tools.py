"""
Integration tests for MCP tools.

Tests the MCP server tools using synthetic ROMs to verify the complete
tool workflow from ROM loading to screen capture and button presses.
"""

from pathlib import Path

import pytest

from mcp_server.server import get_screen, load_rom, press_button
from mcp_server.session import get_session_manager
from tests.mcp_server.fixtures.rom_generation import create_test_rom_data


@pytest.fixture
def synthetic_rom(tmp_path: Path) -> Path:
    """Create a minimal valid GB ROM for testing."""
    rom_file = tmp_path / "test.gb"
    rom_data = create_test_rom_data(size_kb=32)
    rom_file.write_bytes(rom_data)
    return rom_file


@pytest.fixture(autouse=True)
async def clean_session():
    """Clean up session state before each test."""
    yield
    # Clean up after test
    try:
        session_manager = get_session_manager()
        await session_manager.session.stop()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.mark.integration
@pytest.mark.emulator
class TestMCPTools:
    """Test MCP tools integration."""

    @pytest.mark.asyncio
    async def test_load_rom_tool(self, synthetic_rom: Path) -> None:
        """Test the load_rom MCP tool."""
        result = await load_rom(str(synthetic_rom))

        assert result["success"] is True
        assert "loaded" in result["message"]
        assert result["rom_name"] == "test.gb"
        assert result["session_state"] == "running"

    @pytest.mark.asyncio
    async def test_get_screen_tool(self, synthetic_rom: Path) -> None:
        """Test the get_screen MCP tool."""
        # First load a ROM
        await load_rom(str(synthetic_rom))

        # Then capture screen
        result = await get_screen()

        assert result["success"] is True
        assert "Screen captured successfully" in result["message"]
        assert "image_base64" in result
        assert result["image_format"] == "PNG"
        assert result["dimensions"]["width"] == 160
        assert result["dimensions"]["height"] == 144

    @pytest.mark.asyncio
    async def test_press_button_tool(self, synthetic_rom: Path) -> None:
        """Test the press_button MCP tool."""
        # First load a ROM
        await load_rom(str(synthetic_rom))

        # Then press a button
        result = await press_button("A", 1)

        assert result["success"] is True
        assert "Button 'A' pressed for 1 frames" in result["message"]
        assert result["button"] == "A"
        assert result["duration"] == 1
        assert result["frames_advanced"] == 1

    @pytest.mark.asyncio
    async def test_complete_workflow(self, synthetic_rom: Path) -> None:
        """Test complete workflow: load ROM, capture screen, press button."""
        # Load ROM
        load_result = await load_rom(str(synthetic_rom))
        assert load_result["success"] is True

        # Capture initial screen
        screen_result = await get_screen()
        assert screen_result["success"] is True
        initial_screen = screen_result["image_base64"]

        # Press button
        button_result = await press_button("A", 1)
        assert button_result["success"] is True

        # Capture screen again (should be different after button press)
        screen_result2 = await get_screen()
        assert screen_result2["success"] is True
        final_screen = screen_result2["image_base64"]

        # Note: Screens might be the same if ROM doesn't respond to input,
        # but the important thing is that all operations succeeded
        assert isinstance(initial_screen, str)
        assert isinstance(final_screen, str)

    @pytest.mark.asyncio
    async def test_error_handling_no_rom(self) -> None:
        """Test error handling when no ROM is loaded."""
        with pytest.raises(ValueError, match="No ROM is loaded"):
            await get_screen()

        with pytest.raises(ValueError, match="No ROM is loaded"):
            await press_button("A", 1)

    @pytest.mark.asyncio
    async def test_invalid_button_name(self, synthetic_rom: Path) -> None:
        """Test error handling for invalid button names."""
        await load_rom(str(synthetic_rom))

        with pytest.raises(ValueError, match="Invalid button 'INVALID'"):
            await press_button("INVALID", 1)

    @pytest.mark.asyncio
    async def test_invalid_button_duration(self, synthetic_rom: Path) -> None:
        """Test error handling for invalid button duration."""
        await load_rom(str(synthetic_rom))

        with pytest.raises(ValueError, match="Duration must be at least 1 frame"):
            await press_button("A", 0)

        with pytest.raises(ValueError, match="Duration cannot exceed 60 frames"):
            await press_button("A", 61)

    @pytest.mark.asyncio
    async def test_invalid_rom_path(self) -> None:
        """Test error handling for invalid ROM path."""
        with pytest.raises(ValueError, match="ROM file not found"):
            await load_rom("/nonexistent/path.gb")
