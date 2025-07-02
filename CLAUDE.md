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

## Feature Implementation System Guidelines

### Feature Implementation Priority Rules

- IMMEDIATE EXECUTION: Launch parallel Tasks immediately upon feature requests
- NO CLARIFICATION: Skip asking what type of implementation unless absolutely critical
- PARALLEL BY DEFAULT: Always use 7-parallel-Task method for efficiency

### Parallel Feature Implementation Workflow

1. **Component**: Create main component file
2. **Styles**: Create component styles/CSS
3. **Tests**: Create test files
4. **Types**: Create type definitions
5. **Hooks**: Create custom hooks/utilities
6. **Integration**: Update routing, imports, exports
7. **Remaining**: Update package.json, documentation, configuration files
8. **Review and Validation**: Coordinate integration, run tests, verify build, check for conflicts

### Context Optimization Rules

- Strip out all comments when reading code files for analysis
- Each task handles ONLY specified files or file types
- Task 7 combines small config/doc updates to prevent over-splitting

### Feature Implementation Guidelines

- **CRITICAL**: Make MINIMAL CHANGES to existing patterns and structures
- **CRITICAL**: Preserve existing naming conventions and file organization
- Follow project's established architecture and component patterns
- Use existing utility functions and avoid duplicating functionality
