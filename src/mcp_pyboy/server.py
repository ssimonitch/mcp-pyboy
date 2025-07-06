"""
MCP PyBoy Server

Main entry point for the MCP server that enables LLM interaction with Game Boy emulation.
Uses FastMCP for high-level MCP protocol handling.
"""

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

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


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
