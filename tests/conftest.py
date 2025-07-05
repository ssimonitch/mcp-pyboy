"""
Pytest configuration and shared fixtures for MCP PyBoy tests.

This module provides common test fixtures and configuration for testing
the MCP PyBoy Emulator Server components.
"""

import asyncio
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "emulator: Tests requiring PyBoy emulator")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_rom_path(temp_dir: Path) -> Path:
    """Create a mock ROM file for testing."""
    rom_path = temp_dir / "test_game.gb"
    # Create a minimal mock ROM file
    rom_path.write_bytes(b"\x00" * 32768)  # 32KB minimal ROM
    return rom_path


@pytest.fixture
def mock_pyboy():
    """Create a mock PyBoy instance for testing."""
    mock = MagicMock()

    # Mock basic PyBoy methods
    mock.cartridge_title = "Test Game"
    mock.tick.return_value = None
    mock.reset.return_value = None
    mock.screen_image.return_value = MagicMock()

    # Mock button methods
    mock.send_input.return_value = None
    mock.button_press.return_value = None
    mock.button_release.return_value = None

    # Mock save state methods
    mock.save_state.return_value = b"mock_save_state"
    mock.load_state.return_value = None

    return mock


@pytest.fixture
async def mock_mcp_server():
    """Create a mock MCP server instance for testing."""
    mock_server = AsyncMock()

    # Mock server methods
    mock_server.start = AsyncMock()
    mock_server.stop = AsyncMock()
    mock_server.handle_request = AsyncMock()

    return mock_server


@pytest.fixture
def sample_mcp_request():
    """Provide a sample MCP request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "press_button", "arguments": {"button": "a"}},
    }


@pytest.fixture
def sample_mcp_response():
    """Provide a sample MCP response for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "Button 'a' pressed successfully"}]
        },
    }


@pytest.fixture
async def mock_game_session(mock_pyboy):
    """Create a mock game session for testing."""
    session = AsyncMock()

    # Mock session properties
    session.game_loaded = True
    session.current_rom = "test_game.gb"
    session.emulator = mock_pyboy

    # Mock session methods
    session.load_rom = AsyncMock()
    session.reset_game = AsyncMock()
    session.save_state = AsyncMock()
    session.load_state = AsyncMock()
    session.capture_screen = AsyncMock()

    return session


@pytest.fixture
def mock_notebook_manager():
    """Create a mock notebook manager for testing."""
    manager = AsyncMock()

    # Mock notebook methods
    manager.create_note = AsyncMock()
    manager.update_note = AsyncMock()
    manager.get_note = AsyncMock()
    manager.search_notes = AsyncMock()
    manager.list_notes = AsyncMock()
    manager.delete_note = AsyncMock()

    return manager


# Test ROM fixtures for different scenarios
@pytest.fixture
def test_roms_dir(temp_dir: Path) -> Path:
    """Create a directory with test ROM files."""
    roms_dir = temp_dir / "roms"
    roms_dir.mkdir()

    # Create test ROM files
    (roms_dir / "tetris.gb").write_bytes(b"\x00" * 32768)
    (roms_dir / "pokemon.gb").write_bytes(b"\x00" * 1048576)  # 1MB ROM
    (roms_dir / "invalid.gb").write_bytes(b"\x00" * 100)  # Too small

    return roms_dir


@pytest.fixture
def test_saves_dir(temp_dir: Path) -> Path:
    """Create a directory for save states."""
    saves_dir = temp_dir / "saves"
    saves_dir.mkdir()
    return saves_dir


@pytest.fixture
def test_notebooks_dir(temp_dir: Path) -> Path:
    """Create a directory for game notebooks."""
    notebooks_dir = temp_dir / "notebooks"
    notebooks_dir.mkdir()
    return notebooks_dir


# Configuration fixtures
@pytest.fixture
def test_config(test_roms_dir: Path, test_saves_dir: Path, test_notebooks_dir: Path):
    """Create a test configuration object."""
    from unittest.mock import MagicMock

    config = MagicMock()
    config.roms_dir = test_roms_dir
    config.saves_dir = test_saves_dir
    config.notebooks_dir = test_notebooks_dir
    config.log_level = "DEBUG"
    config.debug = True

    return config
