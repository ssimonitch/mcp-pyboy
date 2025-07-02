# MCP PyBoy Emulator Server

An MCP (Model Context Protocol) server that enables LLMs to interact with Game Boy games through PyBoy emulation.

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

### Quick Start

```bash
# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run the server
uv run mcp-pyboy
```

## Features (MVP)

- Load and control Game Boy ROMs
- Screen capture and analysis
- Input simulation (button presses, sequences)
- Game state management (save/load states)
- Persistent knowledge system for games

## Development

- Python 3.10+
- Fast dependency management with uv
- Code formatting with Black
- Linting with Ruff
- Type checking with MyPy
- Testing with pytest

## Project Status

🚧 **Under Development** - This is an MVP implementation following a structured roadmap.