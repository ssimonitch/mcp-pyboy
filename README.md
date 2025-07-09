# MCP PyBoy Emulator Server

An MCP (Model Context Protocol) server that enables LLMs to interact with Game Boy games through PyBoy emulation.

## Overview

This server provides LLMs with the ability to:
- 🎮 Load and play Game Boy ROM files
- 🎯 Control games through button inputs and sequences
- 📸 Capture and analyze game screens
- 💾 Save and load game states
- 📝 Maintain persistent knowledge about games

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- A compatible LLM client that supports MCP protocol

## Installation

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### 2. Clone the repository

```bash
git clone https://github.com/yourusername/mcp-pyboy.git
cd mcp-pyboy
```

### 3. Set up the development environment

```bash
# Install all dependencies (creates .venv automatically)
uv sync

# Install with development dependencies
uv sync --extra dev
```

### 4. Verify installation

```bash
# Check the CLI works
uv run mcp-pyboy

# Run tests (when implemented)
uv run pytest
```

## Quick Start

### Running the Server

```bash
# Basic usage
uv run mcp-pyboy

# With options (coming soon)
uv run mcp-pyboy --roms-dir ./roms --log-level DEBUG
```

### Project Structure

```
mcp-pyboy/
├── src/mcp_server/          # Main package
│   ├── mcp_server/         # MCP protocol implementation
│   ├── game_session/       # PyBoy emulator wrapper
│   ├── notebook/           # Knowledge persistence
│   ├── handlers/           # MCP tool implementations
│   └── utils/              # Shared utilities
├── tests/                  # Test suite
├── docs/                   # Architecture documentation
├── roms/                   # ROM files directory
├── saves/                  # Save states directory
└── notebooks/              # Game knowledge storage
```

## Development

### Development Tools

This project uses modern Python development tools:

- **uv** - Fast dependency management
- **Black** - Code formatting (88 char line length)
- **Ruff** - Linting and import sorting
- **MyPy** - Static type checking
- **pytest** - Testing framework

### Common Development Commands

```bash
# Format code
uv run black src/ tests/

# Run linter
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Run tests
uv run pytest tests/ -v

# Install new dependency
uv add <package-name>

# Install dev dependency
uv add --dev <package-name>
```

### VS Code Integration

This project includes VS Code configuration for optimal development:
- `.vscode/settings.json` - Workspace settings with Black/Ruff integration
- `.vscode/extensions.json` - Recommended extensions

The configuration ensures:
- Black handles all formatting
- Ruff handles linting only (no formatting conflicts)
- Proper Python interpreter from virtual environment

## MCP Tools Available

Once fully implemented, the server will provide these tools:

### Emulation Control
- `load_rom` - Load a Game Boy ROM file
- `reset_game` - Reset the current game
- `set_emulation_speed` - Control game speed

### Input Control
- `press_button` - Press a Game Boy button
- `hold_button` - Hold a button down
- `release_button` - Release a held button
- `send_input_sequence` - Execute a sequence of inputs

### Screen and State
- `capture_screen` - Get current game screen
- `save_state` - Save current game state
- `load_state` - Load a saved state
- `list_states` - List available save states

### Knowledge Management
- `create_note` - Create a note about the game
- `update_note` - Update existing note
- `search_notes` - Search game knowledge
- `list_notes` - List all notes for current game

## Architecture

For detailed architecture documentation, see:
- [Project Design](docs/01_project_design.md)
- [Technical Architecture](docs/02_technical_architecture.md)
- [MVP Implementation Roadmap](docs/03_mvp_implementation_roadmap.md)

## Contributing

This project is under active development. See the [MVP Roadmap](docs/03_mvp_implementation_roadmap.md) for current progress and planned features.

## License

[License information to be added]

## Acknowledgments

- Built on [PyBoy](https://github.com/Baekalfen/PyBoy) - Game Boy emulator
- Uses [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- Developed with [Claude Code](https://claude.ai/code) assistance
