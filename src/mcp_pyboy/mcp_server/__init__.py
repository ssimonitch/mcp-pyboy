"""
MCP Server Core

JSON-RPC 2.0 protocol implementation with tool registry and error handling.
"""

from .errors import MCPError, ValidationError
from .protocol import MCPProtocol
from .registry import ToolRegistry, mcp_tool
from .server import MCPServer

__all__ = [
    "MCPServer",
    "MCPProtocol",
    "ToolRegistry",
    "mcp_tool",
    "MCPError",
    "ValidationError",
]
