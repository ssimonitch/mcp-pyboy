"""
Command Line Interface for MCP PyBoy Server

Provides easy startup and configuration options for the MCP server.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
import structlog

from .mcp_server.server import MCPServer
from .utils.config import Config
from .utils.logging import setup_logging


@click.command()
@click.option(
    "--config", 
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file"
)
@click.option(
    "--roms-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default="roms",
    help="Directory containing ROM files (default: ./roms)"
)
@click.option(
    "--saves-dir", 
    type=click.Path(file_okay=False, path_type=Path),
    default="saves",
    help="Directory for save states (default: ./saves)"
)
@click.option(
    "--notebooks-dir",
    type=click.Path(file_okay=False, path_type=Path), 
    default="notebooks",
    help="Directory for game notebooks (default: ./notebooks)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level (default: INFO)"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose logging"
)
@click.version_option()
def main(
    config: Optional[Path] = None,
    roms_dir: Path = Path("roms"),
    saves_dir: Path = Path("saves"), 
    notebooks_dir: Path = Path("notebooks"),
    log_level: str = "INFO",
    debug: bool = False,
) -> None:
    """
    Start the MCP PyBoy Emulator Server.
    
    This server enables LLMs to interact with Game Boy games through the MCP protocol.
    """
    # Set up logging
    if debug:
        log_level = "DEBUG"
    
    setup_logging(level=log_level, debug=debug)
    logger = structlog.get_logger()
    
    # Load configuration
    try:
        app_config = Config.load(config) if config else Config()
        
        # Override with command line arguments
        app_config.roms_dir = roms_dir
        app_config.saves_dir = saves_dir  
        app_config.notebooks_dir = notebooks_dir
        app_config.log_level = log_level
        app_config.debug = debug
        
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        sys.exit(1)
    
    # Create required directories
    try:
        roms_dir.mkdir(exist_ok=True)
        saves_dir.mkdir(exist_ok=True)
        notebooks_dir.mkdir(exist_ok=True)
        logger.info("Created directories", roms=str(roms_dir), saves=str(saves_dir), notebooks=str(notebooks_dir))
    except Exception as e:
        logger.error("Failed to create directories", error=str(e))
        sys.exit(1)
    
    # Start the server
    logger.info("Starting MCP PyBoy server", config=app_config.dict())
    
    try:
        asyncio.run(run_server(app_config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)


async def run_server(config: Config) -> None:
    """Run the MCP server with the given configuration."""
    logger = structlog.get_logger()
    
    try:
        # Create and start the MCP server
        server = MCPServer(config)
        await server.start()
        
        logger.info("MCP PyBoy server started successfully")
        
        # Keep the server running
        await server.wait_for_shutdown()
        
    except Exception as e:
        logger.error("Failed to start server", error=str(e))
        raise
    finally:
        logger.info("MCP PyBoy server stopped")


if __name__ == "__main__":
    main()