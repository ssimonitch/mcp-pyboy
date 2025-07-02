# MCP PyBoy Project Instructions

## Overview

MCP server for Game Boy emulation via PyBoy, designed for LLM interaction.

## Key Conventions

- All async functions use type hints
- Docstrings follow Google style
- Error messages include recovery suggestions
- Tests use pytest with async support

## Common Tasks

- Run tests: `pytest tests/ -v`
- Format code: `black src/ tests/`
- Type check: `mypy src/`
- Start server: `python -m mcp_pyboy.server`

## Architecture Notes

- Single PyBoy instance per session (singleton pattern)
- Input commands queued to prevent race conditions
- Screen captures cached for 100ms to reduce CPU
- Markdown notes have 10KB limit per section

## Testing ROMs

Test ROMs located in `tests/fixtures/test_roms/`:

- `test_basic.gb`: Simple input/output test
- `test_menu.gb`: Menu navigation test
