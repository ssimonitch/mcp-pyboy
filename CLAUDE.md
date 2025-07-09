# MCP PyBoy Project Instructions

## Overview

MCP server for Game Boy emulation via PyBoy, designed for LLM interaction.

## Development Environment

This project uses **uv** for fast Python dependency management.

### Setup Commands

```bash
# Install all dependencies (creates .venv automatically)
uv sync

# Install with development dependencies
uv sync --extra dev

# Run commands in virtual environment
uv run <command>

# Activate virtual environment manually (optional)
source .venv/bin/activate
```

## Key Conventions

- All async functions use type hints
- Docstrings follow Google style
- Error messages include recovery suggestions
- Tests use pytest with async support
- Python 3.10+ required

## Common Tasks

- Run tests: `uv run test` (or `uv run pytest tests/ -v`)
- Format code: `uv run format` (or `uv run black src/ tests/`)
- Type check: `uv run typecheck` (or `uv run mypy src/`)
- Lint code: `uv run lint` (or `uv run ruff check src/ tests/`)
- Start MCP server: `uv run python src/mcp_server/server.py`
- Test MCP server: `uv run mcp dev src/mcp_server/server.py` (development mode)
- Install for Claude Desktop: `uv run mcp install src/mcp_server/server.py --name "PyBoy Dev"`
- Start web API server: `uv run web-server` (or `uv run python src/web_server/app.py`)
- Install new dependency: `uv add <package-name>`
- Install dev dependency: `uv add --dev <package-name>`

## Architecture Notes

### MCP Server Design
- Uses FastMCP for high-level MCP protocol handling
- Tools exposed via stdio transport for LLM integration
- Async/await patterns throughout for emulator interaction
- LLM-friendly error messages with recovery suggestions

### Game Session Management
- Single PyBoy instance per session (singleton pattern)
- Input commands queued to prevent race conditions
- Screen captures cached to reduce CPU usage
- Session state persists across tool calls

### Notebook System
- Game-specific notebooks (one per ROM, identified by hash)
- Focused on objectives, progress, and non-obvious discoveries
- Size limits per section to prevent bloat
- Automatic validation against redundant information

## Testing ROMs

Test ROMs for automated testing located in `tests/mcp_server/fixtures/test_roms/`:
- Small, lightweight ROMs for unit and integration testing
- No copyright concerns for CI/CD pipelines

Game ROMs for manual testing stored in `@roms/` directory:
- Classic Game Boy ROMs for real-world validation
- Used for LLM integration testing and demos

## MCP Development Guidelines

### Tool Implementation Patterns

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP PyBoy Server")

@mcp.tool()
async def example_tool(param: str) -> str:
    """Tool description for LLM - be specific about what it does."""
    try:
        # Implementation with proper error handling
        return result
    except SpecificError as e:
        # LLM-friendly error with recovery suggestions
        raise ValueError(f"Could not complete action: {e}. Try checking X or Y.")
```

### Error Handling Best Practices
- Use LLM-friendly error messages that suggest corrective actions
- Include context about what the LLM should try differently
- Validate parameters early with helpful feedback
- Handle emulator-specific errors gracefully

### Async/Await Patterns
- All emulator interactions must be async
- Use proper async context managers for resource cleanup
- Handle concurrent tool calls safely with session locks

### Testing MCP Tools
```bash
# Test server connectivity
uv run mcp dev src/mcp_server/server.py

# Run integration tests with test ROMs
uv run pytest tests/mcp_server/integration/ -v

# Test with Claude Desktop (install server locally)
uv run mcp install src/mcp_server/server.py --name "PyBoy Dev"
```

### Notebook System Guidelines
- **Store**: Current objectives, progress checkpoints, strategy discoveries
- **Don't Store**: Observable game state, basic controls, obvious information
- **Validate**: Size limits, redundancy checks, relevance to gameplay
- **Structure**: Sections for Objectives, Progress, Discoveries, Strategy Notes

## Git Repository Guidelines

### Git Operations Policy

**CRITICAL**: Never perform git operations without explicit user permission:

- ❌ `git add` - Do not stage files automatically
- ❌ `git commit` - Do not create commits automatically
- ❌ `git push` - Do not push to remote repositories
- ❌ `git merge` - Do not merge branches automatically
- ❌ Any other git operations that modify repository state

**Required**: Always ask for explicit permission before any git operations:
- "Should I add these files to git and create a commit?"
- "Would you like me to commit these changes?"
- "Do you want me to push these changes to the remote repository?"

### Allowed Git Operations

✅ **Read-only operations** (no permission needed):
- `git status` - Check repository status
- `git log` - View commit history
- `git diff` - Show file differences
- `git branch` - List branches

## MCP Feature Implementation Guidelines

### Tool Development Priority Rules

- **CORE FUNCTIONALITY FIRST**: Implement basic tool functionality before advanced features
- **LLM-FRIENDLY DESIGN**: Focus on clear tool descriptions and helpful error messages
- **ASYNC BY DEFAULT**: All emulator interactions must be async/await
- **ERROR RECOVERY**: Provide actionable guidance when tools fail

### MCP Tool Implementation Workflow

1. **Tool Function**: Create the core tool function with proper typing
2. **Parameter Validation**: Add input validation with LLM-friendly error messages
3. **Emulator Integration**: Connect to PyBoy session with proper error handling
4. **Response Formatting**: Return data in LLM-consumable format
5. **Tests**: Create unit and integration tests
6. **Documentation**: Update tool descriptions and examples
7. **Registration**: Register tool with FastMCP server
8. **Integration Testing**: Test with actual MCP client (Claude Desktop)

### Tool Design Best Practices

- **Descriptive Names**: Use clear, action-oriented tool names
- **Comprehensive Docstrings**: Help LLMs understand tool purpose and usage
- **Parameter Validation**: Validate early with helpful error messages
- **Consistent Return Types**: Use predictable response formats
- **Error Context**: Include guidance for what to try when tools fail

### Session Management Patterns

- **Singleton Sessions**: Maintain one active PyBoy session
- **State Persistence**: Preserve game state across tool calls
- **Resource Cleanup**: Properly close sessions on server shutdown
- **Thread Safety**: Use locks for concurrent tool access

## Workflow Guidelines

### Task Completion Protocol

- **Complete Before Moving On**: When finishing a todo item, always summarize the work done and confirm with the user before proceeding to the next task
- **Get Approval**: Wait for explicit user approval before starting the next todo item
- **Document Updates**: When asked to update documentation, focus ONLY on the documentation update - do not make other code changes unless explicitly requested

### Progress Summary Requirements

When completing a todo item:
1. Summarize what was implemented
2. Highlight key design decisions
3. Note any issues or considerations
4. Request approval to proceed to the next task
