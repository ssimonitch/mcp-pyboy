# MCP PyBoy MVP Implementation Roadmap

## Overview

This document provides a step-by-step implementation guide for building the MCP PyBoy Emulator Server MVP. Designed for solo development with Claude Code assistance, each task includes specific instructions for effective LLM collaboration.

## Progress Tracking

- **Total Tasks**: 24 (streamlined from original 45)
- **Estimated Time**: 2 weeks (solo developer)
- **Current Progress**: Phase 1 completed, Phase 2 ready to start

---

## Phase 1: Project Foundation (Days 1-2)

### Project Setup
- [x] **1.1** Create Python project structure
  - [x] Set up `pyproject.toml` with dependencies
  - [x] Create `src/` directory structure
  - [x] Initialize git repository
  - **Claude Code Tip**: "Create a new Python project with pyproject.toml using the dependencies from our technical architecture document"

- [x] **1.2** Set up development environment
  - [x] Install uv for fast dependency management
  - [x] Create virtual environment with .python-version
  - [x] Install core dependencies (PyBoy, MCP, etc.)
  - [x] Install development dependencies (pytest, black, ruff, mypy)
  - **Claude Code Tip**: "Help me set up a Python development environment for this project with proper dependency management"

- [x] **1.3** Complete project documentation and IDE setup
  - [x] Update README.md with comprehensive setup instructions
  - [x] Verify CLAUDE.md has complete uv workflow documentation
  - [x] Ensure all architecture documents are properly organized in docs/
  - [x] Configure VS Code settings for Black/Ruff integration
  - [x] Verify IDE extensions and toolchain integration
  - [x] Fix all formatting and linting issues
  - [x] Add py.typed marker for type checking
  - **Claude Code Tip**: "Update the README with detailed setup instructions and verify all IDE tooling works seamlessly"

- [x] **1.4** Establish development workflow
  - [x] Set up pre-commit hooks for automated quality checks
  - [x] Create comprehensive test directory structure
  - [x] Add test fixtures for mock PyBoy instances
  - [x] Create comprehensive test fixtures and conftest.py
  - [x] Implement mock PyBoy classes for testing
  - [x] Verify all dev tools work together (black, ruff, mypy, pytest)
  - [x] Test complete development workflow end-to-end
  - **Claude Code Tip**: "Create a robust development workflow with pre-commit hooks and comprehensive testing infrastructure"

---

## Phase 2: Core PyBoy Integration and Basic MCP Server (Days 3-5)

### Basic MCP Server Structure
- [x] **2.1** Create MCP server using FastMCP
  - [x] Create `src/mcp_pyboy/server.py` using FastMCP
  - [x] Set up basic server with health check tool
  - [x] Test MCP server connectivity via stdio
  - **Claude Code Tip**: "Create a basic FastMCP server with a simple health check tool to validate MCP connectivity"

### PyBoy Integration Foundation
- [ ] **2.2** Implement PyBoy wrapper class
  - [x] Create `src/mcp_pyboy/emulator.py` with PyBoy wrapper
  - [x] Implement basic emulator lifecycle (start, stop, load ROM)
  - [x] Add LLM-friendly error handling for common PyBoy issues
  - **Claude Code Tip**: "Create a PyBoy wrapper that handles emulator lifecycle and provides LLM-friendly error messages"

### Core Emulation Tools
- [ ] **2.3** Implement essential MCP tools
  - [ ] Implement `load_rom` tool with path validation
  - [ ] Implement `get_screen` tool (returns base64 screenshot)
  - [ ] Implement `press_button` tool with Game Boy button mapping
  - [ ] Test all tools work end-to-end with test ROMs
  - **Claude Code Tip**: "Create the three core tools that allow LLMs to load games, see the screen, and interact with controls"

### Basic Game Session Management
- [ ] **2.4** Create session management
  - [ ] Create singleton pattern for active game session
  - [ ] Add ROM validation and loading
  - [ ] Implement graceful session cleanup
  - **Claude Code Tip**: "Implement a simple session manager that maintains one active game session and handles ROM lifecycle"

---

## Phase 3: Enhanced Tools and Session Management (Days 6-8)

### Advanced Input Tools
- [ ] **3.1** Implement advanced input controls
  - [ ] Add input sequence and timing controls
  - [ ] Implement hold/release button functionality
  - [ ] Add frame-by-frame advancement (`tick` tool)
  - **Claude Code Tip**: "Build on the basic press_button tool to add sequence controls and precise timing for complex game interactions"

### Save State System
- [ ] **3.2** Implement save state functionality
  - [ ] Add save/load state tools
  - [ ] Implement state file management with validation
  - [ ] Create state persistence across tool calls
  - **Claude Code Tip**: "Create save state tools that allow LLMs to create checkpoints and experiment with different approaches"

### Enhanced Screen Capture
- [ ] **3.3** Add advanced screen features
  - [ ] Multiple output formats (base64, raw arrays)
  - [ ] Screen region extraction for analysis
  - [ ] Basic caching to reduce CPU usage
  - **Claude Code Tip**: "Enhance the basic get_screen tool with different formats and region selection for more sophisticated analysis"

### Input Queue System
- [ ] **3.4** Create robust input handling
  - [ ] Implement async input queue to prevent race conditions
  - [ ] Add input validation and timing controls
  - [ ] Handle input cancellation and error recovery
  - **Claude Code Tip**: "Create an input queue system that ensures button presses are processed safely without corrupting game state"

---

## Phase 4: Game-Specific Notebook System (Days 9-10)

### Game-Specific Notebook Implementation
- [ ] **4.1** Create notebook manager
  - [ ] Implement `src/mcp_pyboy/notebook.py` with game-specific storage
  - [ ] One notebook per ROM (identified by ROM hash)
  - [ ] Sections: Current Objectives, Progress Log, Important Discoveries, Strategy Notes
  - [ ] Auto-clear temporary notes when loading different ROM
  - **Claude Code Tip**: "Create a notebook system focused on helping LLMs remember objectives and progress, not observable game state"

### Notebook MCP Tools
- [ ] **4.2** Implement notebook tools
  - [ ] Add `save_notes` with section-based organization
  - [ ] Implement `get_notes` returning current game's relevant information
  - [ ] Create `update_objectives` for current goals management
  - [ ] Add `list_sections` showing available note categories
  - **Claude Code Tip**: "Create notebook tools that guide LLMs toward useful objective tracking rather than redundant state recording"

### Memory Guidance System
- [ ] **4.3** Add intelligent note filtering
  - [ ] Tool descriptions guide LLM on what to record vs. observe fresh
  - [ ] Validation prevents storing obviously visible information
  - [ ] Focus on decision-making context and non-obvious mechanics
  - [ ] Size limiting with feedback on what to include/exclude
  - **Claude Code Tip**: "Build validation that encourages useful memory while preventing redundant information storage"

---

## Phase 5: Integration and Testing (Days 11-12)

### End-to-End Testing
- [ ] **5.1** Create comprehensive integration tests
  - [ ] Integration tests using `tests/fixtures/test_roms/`
  - [ ] Test complete ROM loading → gameplay → note taking flow
  - [ ] Error handling validation with LLM-friendly messages
  - [ ] Notebook persistence testing across sessions
  - **Claude Code Tip**: "Create integration tests that simulate real LLM usage patterns and validate the complete system flow"

### CLI and Basic Documentation
- [ ] **5.2** Add command-line interface
  - [ ] Create `src/mcp_pyboy/cli.py` for easy server startup
  - [ ] Add configuration options and help text
  - [ ] Implement proper signal handling
  - **Claude Code Tip**: "Create a user-friendly CLI that makes it easy to start and configure the MCP server"

### Performance and Reliability
- [ ] **5.3** Optimize critical paths
  - [ ] Profile screen capture and input processing
  - [ ] Optimize memory usage and caching
  - [ ] Test concurrent operations and edge cases
  - **Claude Code Tip**: "Profile and optimize the performance bottlenecks while ensuring system reliability"

### Usage Documentation
- [ ] **5.4** Create usage examples
  - [ ] Write example MCP interactions
  - [ ] Document notebook best practices
  - [ ] Create basic troubleshooting guide
  - **Claude Code Tip**: "Generate usage examples that help users understand how to interact effectively with the MCP server"

---

## Phase 6: MVP Validation and Polish (Days 13-14)

### Real-World Testing
- [ ] **6.1** Test with actual Game Boy ROMs
  - [ ] Validate with classic games (Tetris, Pokemon, etc.)
  - [ ] Test edge cases and error conditions
  - [ ] Verify notebook system helps LLM maintain context effectively
  - **Claude Code Tip**: "Test the complete system with real Game Boy ROMs to validate MVP functionality and notebook effectiveness"

### LLM Integration Testing
- [ ] **6.2** Validate actual LLM interactions
  - [ ] Test actual Claude interactions via Claude Desktop
  - [ ] Validate tool discovery and usage patterns
  - [ ] Check error message clarity and recovery guidance
  - [ ] Test notebook system prevents redundant information storage
  - **Claude Code Tip**: "Test the actual LLM integration by simulating realistic Claude interactions with the MCP server"

### Packaging and Distribution
- [ ] **6.3** Create installation package
  - [ ] Set up PyPI-ready package structure
  - [ ] Create installation and setup documentation
  - [ ] Add example configuration files
  - [ ] Test installation process end-to-end
  - **Claude Code Tip**: "Create a professional Python package with proper setup for PyPI distribution"

### Final Documentation Review
- [ ] **6.4** Polish documentation and examples
  - [ ] Update all documentation for accuracy
  - [ ] Create quick start guide with notebook usage examples
  - [ ] Add API reference documentation
  - [ ] Include troubleshooting guide for common issues
  - **Claude Code Tip**: "Review and update all project documentation to ensure it's accurate and helpful for end users"

---

## Claude Code Collaboration Best Practices

### Effective Prompting Strategies
```markdown
# Good Prompts for Claude Code:
- "Implement the ToolRegistry class from our registry design document, focusing on the core registration functionality"
- "Add comprehensive error handling to this function based on our error handling chain document"
- "Create unit tests for this module that cover edge cases and error conditions"

# Less Effective Prompts:
- "Make this better"
- "Fix the bugs"
- "Add more features"
```

### File Organization Tips
1. **Keep related code together** - Claude Code works better with focused, cohesive modules
2. **Use descriptive file/function names** - Helps Claude understand context quickly
3. **Add comprehensive docstrings** - Claude uses these to understand intent
4. **Reference architecture documents** - Always mention which design document applies

### Testing Strategy
1. **Start with unit tests** - Easier for Claude to implement and validate
2. **Use fixtures for complex setup** - Allows Claude to focus on test logic
3. **Test error cases explicitly** - Critical for MCP server reliability
4. **Create integration tests last** - Once individual components are stable

### Debugging with Claude
1. **Provide error messages and stack traces** - Complete context helps debugging
2. **Share relevant code sections** - Don't expect Claude to remember everything
3. **Ask for specific improvements** - "Make this error message more LLM-friendly"
4. **Use Claude for code review** - "Review this implementation for potential issues"

---

## Success Criteria for MVP

### Core Functionality
- [ ] **Load and play Game Boy ROMs successfully**
- [ ] **LLM can discover and use all MCP tools**
- [ ] **Error handling provides LLM-friendly actionable feedback**
- [ ] **Game-specific notebook system helps LLM track objectives across sessions**
- [ ] **Screen capture works with base64 output for LLM vision**
- [ ] **Input controls respond accurately with proper timing**
- [ ] **Save states allow experimentation and checkpointing**

### LLM Integration Quality
- [ ] **FastMCP server properly exposes tools via stdio transport**
- [ ] **Tool descriptions guide effective LLM usage**
- [ ] **Notebook system prevents redundant information storage**
- [ ] **Error messages suggest corrective actions**
- [ ] **All tools validate parameters and provide helpful feedback**

### Technical Quality
- [ ] **All tests pass with solid coverage**
- [ ] **Code follows style guidelines (Black, Ruff)**
- [ ] **Type checking passes (MyPy)**
- [ ] **No memory leaks during extended gameplay**
- [ ] **Emulation runs smoothly without performance issues**

### Documentation Quality
- [ ] **README provides clear setup instructions**
- [ ] **API documentation covers all MCP tools**
- [ ] **Examples demonstrate effective LLM usage patterns**
- [ ] **Notebook best practices guide LLM behavior**

---

## Next Steps After MVP

Once MVP is complete, consider these enhancements:
- Web frontend for human monitoring/takeover
- Advanced screen analysis tools
- Multi-emulator support (GBA, NES)
- Cloud save synchronization
- Performance optimizations
- Additional Game Boy features (sound, etc.)

**Remember**: The goal is a working, demonstrable MVP that showcases the core concept. Perfect is the enemy of done!
