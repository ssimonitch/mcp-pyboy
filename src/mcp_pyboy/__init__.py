"""
MCP PyBoy Emulator Server

An MCP server that enables LLMs to interact with Game Boy games through PyBoy emulation,
featuring minimal knowledge persistence, human handoff capabilities, and real-time monitoring.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .mcp_server.server import MCPServer
from .game_session.manager import GameSessionManager
from .notebook.notebook import NotebookManager

__all__ = [
    "MCPServer",
    "GameSessionManager", 
    "NotebookManager",
]