"""
MCP PyBoy Server

Main entry point for the MCP server that enables LLM interaction with Game Boy emulation.
Uses FastMCP for high-level MCP protocol handling.
"""

import base64
import logging
import sys
from typing import Any

import numpy as np
from mcp.server.fastmcp import FastMCP
from PIL import Image

from mcp_pyboy.session import SessionError, get_session_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create the MCP server instance
mcp = FastMCP("MCP PyBoy Server")


@mcp.tool()
async def health_check() -> str:
    """
    Check if the MCP server is running and responsive.

    This tool verifies that the MCP PyBoy server is operational and ready
    to handle Game Boy emulation requests. Use this to test connectivity
    and server status.

    Returns:
        str: Status message confirming server is running
    """
    logger.info("Health check requested")
    return "MCP PyBoy server is running and ready for Game Boy emulation"


@mcp.tool()
async def get_server_info() -> dict[str, Any]:
    """
    Get information about the MCP PyBoy server.

    Returns detailed information about the server capabilities,
    version, and current status.

    Returns:
        dict: Server information including version and capabilities
    """
    logger.info("Server info requested")
    return {
        "name": "MCP PyBoy Server",
        "version": "0.1.0",
        "description": "MCP server for Game Boy emulation via PyBoy",
        "capabilities": [
            "Game Boy ROM loading",
            "Screen capture",
            "Input control",
            "Save states",
            "Game-specific notes",
        ],
        "status": "running",
        "emulator": "PyBoy",
        "supported_formats": [".gb", ".gbc"],
    }


@mcp.tool()
async def load_rom(rom_path: str) -> dict[str, Any]:
    """
    Load a Game Boy ROM file into the emulator.

    This tool loads a Game Boy ROM file (.gb or .gbc) and starts emulation.
    If another ROM is already loaded, it will be replaced. The ROM file must
    exist and be a valid Game Boy ROM.

    Args:
        rom_path: Path to the ROM file to load (.gb or .gbc extension required)

    Returns:
        dict: Information about the loaded ROM including name, size, and status

    Raises:
        Error if ROM file doesn't exist, has invalid extension, or cannot be loaded
    """
    logger.info(f"Loading ROM: {rom_path}")

    try:
        session_manager = get_session_manager()
        result = await session_manager.session.load_rom(rom_path)

        logger.info(f"ROM loaded successfully: {result['rom_name']}")
        return result

    except SessionError as e:
        logger.error(f"Session error: {e}")
        raise ValueError(str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error loading ROM: {e}")
        raise ValueError(
            f"Failed to load ROM: {e}. Please check the file path and try again."
        ) from e


@mcp.tool()
async def get_screen() -> dict[str, Any]:
    """
    Capture the current Game Boy screen as a base64-encoded image.

    This tool captures the current state of the Game Boy screen and returns it
    as a base64-encoded PNG image. The LLM can use this to see what's happening
    in the game and make decisions about next actions.

    Returns:
        dict: Screen capture data including base64 image and dimensions

    Raises:
        Error if no ROM is loaded or screen capture fails
    """
    logger.info("Capturing screen...")

    try:
        session_manager = get_session_manager()
        emulator = await session_manager.session.get_emulator()
        pyboy = emulator.get_pyboy_instance()

        # Get screen data as numpy array (144x160x4 RGBA)
        screen_array = pyboy.screen.ndarray

        # Convert RGBA to RGB (remove alpha channel)
        if screen_array.shape[2] == 4:
            screen_rgb = screen_array[:, :, :3]
        else:
            screen_rgb = screen_array

        # Convert numpy array to PIL Image
        image = Image.fromarray(screen_rgb.astype(np.uint8))

        # Convert to base64 PNG
        from io import BytesIO

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        logger.info(f"Screen captured successfully ({image.size[0]}x{image.size[1]})")

        return {
            "success": True,
            "message": "Screen captured successfully",
            "image_base64": image_base64,
            "image_format": "PNG",
            "dimensions": {"width": image.size[0], "height": image.size[1]},
            "original_dimensions": {"width": 160, "height": 144},
        }

    except SessionError as e:
        logger.error(f"Session error: {e}")
        raise ValueError(str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error capturing screen: {e}")
        raise ValueError(
            f"Failed to capture screen: {e}. Make sure a ROM is loaded and try again."
        ) from e


@mcp.tool()
async def get_session_info() -> dict[str, Any]:
    """
    Get detailed information about the current game session.

    This tool provides information about the session state, loaded ROM,
    performance metrics, and any error conditions. Use this to understand
    the current state of the emulator and debug issues.

    Returns:
        dict: Comprehensive session information including state, ROM details, and metrics
    """
    logger.info("Getting session information")

    try:
        session_manager = get_session_manager()
        session_info = await session_manager.session.get_info()

        logger.info(f"Session info retrieved: state={session_info['state']}")
        return session_info

    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        # Return partial info even on error
        return {
            "state": "unknown",
            "error": str(e),
            "message": "Failed to retrieve complete session information",
        }


@mcp.tool()
async def press_button(button: str, duration: int = 1) -> dict[str, Any]:
    """
    Press a Game Boy button for a specified duration.

    This tool simulates pressing a Game Boy button and advances the emulation
    by the specified number of frames. Valid buttons are the standard Game Boy
    controls: A, B, START, SELECT, UP, DOWN, LEFT, RIGHT.

    Args:
        button: Button to press (A, B, START, SELECT, UP, DOWN, LEFT, RIGHT)
        duration: Number of frames to hold the button (default: 1)

    Returns:
        dict: Information about the button press and resulting state

    Raises:
        Error if invalid button name, no ROM loaded, or button press fails
    """
    logger.info(f"Pressing button: {button} for {duration} frames")

    # Valid Game Boy buttons (case insensitive)
    valid_buttons = {
        "A": "a",
        "B": "b",
        "START": "start",
        "SELECT": "select",
        "UP": "up",
        "DOWN": "down",
        "LEFT": "left",
        "RIGHT": "right",
    }

    button_upper = button.upper()

    if button_upper not in valid_buttons:
        raise ValueError(
            f"Invalid button '{button}'. Valid buttons are: {', '.join(valid_buttons.keys())}"
        )

    if duration < 1:
        raise ValueError("Duration must be at least 1 frame")

    if duration > 60:  # Limit to 1 second at 60 FPS
        raise ValueError("Duration cannot exceed 60 frames (1 second)")

    try:
        session_manager = get_session_manager()
        emulator = await session_manager.session.get_emulator()
        pyboy = emulator.get_pyboy_instance()
        pyboy_button = valid_buttons[button_upper]

        # Press and hold button for specified duration
        for frame in range(duration):
            pyboy.button_press(pyboy_button)
            pyboy.tick()

            # Release button on last frame
            if frame == duration - 1:
                pyboy.button_release(pyboy_button)

        # Record metrics
        session_manager.session.record_frame_advance(duration)
        session_manager.session.record_input()

        logger.info(f"Button {button} pressed successfully for {duration} frames")

        return {
            "success": True,
            "message": f"Button '{button}' pressed for {duration} frames",
            "button": button_upper,
            "duration": duration,
            "frames_advanced": duration,
        }

    except SessionError as e:
        logger.error(f"Session error: {e}")
        raise ValueError(str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error pressing button: {e}")
        raise ValueError(
            f"Failed to press button: {e}. Make sure a ROM is loaded and try again."
        ) from e


async def main() -> None:
    """Main server entry point with proper error handling."""
    try:
        logger.info("Starting MCP PyBoy server...")
        # Run the server using stdio transport for MCP protocol
        await mcp.run_stdio_async()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        # Clean up session on shutdown
        try:
            session_manager = get_session_manager()
            await session_manager.session.stop()
            logger.info("Session cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
