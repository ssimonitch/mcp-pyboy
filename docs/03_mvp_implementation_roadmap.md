# MCP PyBoy MVP Implementation Roadmap

## Overview

This document provides a step-by-step implementation guide for building the MCP PyBoy Emulator Server MVP. Designed for solo development with Claude Code assistance, each task includes specific instructions for effective LLM collaboration.

## Progress Tracking

- **Total Tasks**: 45
- **Estimated Time**: 2-3 weeks (solo developer)
- **Current Progress**: 2/45 completed

---

## Phase 1: Project Foundation (Days 1-2)

*Updated: Consolidated overlapping tasks 1.4 and 1.5 into streamlined workflow. VS Code configuration completed.*

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

- [ ] **1.3** Complete project documentation and IDE setup
  - [ ] Update README.md with comprehensive setup instructions
  - [ ] Verify CLAUDE.md has complete uv workflow documentation
  - [ ] Ensure all architecture documents are properly organized in docs/
  - [x] Configure VS Code settings for Black/Ruff integration
  - [ ] Verify IDE extensions and toolchain integration
  - **Claude Code Tip**: "Update the README with detailed setup instructions and verify all IDE tooling works seamlessly"

- [ ] **1.4** Establish development workflow
  - [ ] Set up pre-commit hooks for automated quality checks
  - [ ] Create comprehensive test directory structure
  - [ ] Add test fixtures for mock PyBoy instances
  - [ ] Verify all dev tools work together (black, ruff, mypy, pytest)
  - [ ] Test complete development workflow end-to-end
  - **Claude Code Tip**: "Create a robust development workflow with pre-commit hooks and comprehensive testing infrastructure"

---

## Phase 2: Core MCP Server (Days 3-5)

### Error System Foundation  
- [ ] **2.1** Implement custom exception hierarchy
  - [ ] Create `src/mcp_server/errors.py`
  - [ ] Define MCPError base class with LLM-friendly attributes
  - [ ] Implement specific exceptions (GameNotLoadedError, InvalidROMError, etc.)
  - **Claude Code Tip**: "Implement the error hierarchy from our error handling design document, focusing on LLM-friendly error messages"

### Registry System
- [ ] **2.2** Create tool registry foundation
  - [ ] Implement `src/mcp_server/registry.py`
  - [ ] Create ToolDefinition dataclass
  - [ ] Implement @mcp_tool decorator
  - [ ] Add parameter validation with JSON Schema
  - **Claude Code Tip**: "Implement the ToolRegistry class from our registry design document, starting with the core registration functionality"

- [ ] **2.3** Add tool discovery and management
  - [ ] Implement tool scanning functionality
  - [ ] Add tool lookup and validation methods
  - [ ] Create tool execution with error handling
  - **Claude Code Tip**: "Add the tool discovery and execution methods to the registry, ensuring proper error handling throughout"

### Protocol Layer
- [ ] **2.4** Implement JSON-RPC protocol handler
  - [ ] Create `src/mcp_server/protocol.py`
  - [ ] Implement JSONRPCRequest/Response classes
  - [ ] Add request parsing and validation
  - **Claude Code Tip**: "Implement the MCPProtocol class from our protocol design document, focusing on proper JSON-RPC 2.0 compliance"

- [ ] **2.5** Add stdio transport and message loop
  - [ ] Implement async stdio handling
  - [ ] Create message processing loop
  - [ ] Add comprehensive error boundary
  - **Claude Code Tip**: "Complete the protocol implementation with async stdio transport and the main message processing loop"

### MCP Server Integration
- [ ] **2.6** Create main server module
  - [ ] Implement `src/mcp_server/server.py`
  - [ ] Wire together protocol and registry
  - [ ] Add graceful startup/shutdown
  - **Claude Code Tip**: "Create the main MCP server that integrates protocol and registry, with proper async lifecycle management"

- [ ] **2.7** Test basic MCP functionality
  - [ ] Create simple test tools for validation
  - [ ] Test JSON-RPC request/response cycle
  - [ ] Verify error handling works correctly
  - **Claude Code Tip**: "Create comprehensive tests for the MCP server core functionality, focusing on the request/response cycle"

---

## Phase 3: Game Session Management (Days 6-8)

### PyBoy Integration
- [ ] **3.1** Create emulator wrapper
  - [ ] Implement `src/game_session/emulator.py`
  - [ ] Wrap PyBoy with error handling
  - [ ] Add screen capture functionality
  - **Claude Code Tip**: "Create a PyBoy wrapper class that handles emulator lifecycle and provides safe access to game state"

- [ ] **3.2** Implement input management
  - [ ] Create `src/game_session/input_queue.py`
  - [ ] Add thread-safe input queuing
  - [ ] Implement button press with timing
  - **Claude Code Tip**: "Implement an async input queue system that prevents race conditions in button presses"

### Session Management
- [ ] **3.3** Create session manager
  - [ ] Implement `src/game_session/manager.py`
  - [ ] Add singleton session management
  - [ ] Handle ROM loading and validation
  - **Claude Code Tip**: "Create a session manager that maintains exactly one active game session and handles ROM lifecycle"

- [ ] **3.4** Add state management
  - [ ] Implement `src/game_session/state.py`
  - [ ] Add save state creation and loading
  - [ ] Handle state file management
  - **Claude Code Tip**: "Implement save state management with proper file handling and error recovery"

### Screen Capture System
- [ ] **3.5** Implement screen capture
  - [ ] Create `src/game_session/screen_capture.py`
  - [ ] Add multiple output formats (base64, array)
  - [ ] Implement caching for performance
  - **Claude Code Tip**: "Create an efficient screen capture system with caching and multiple output formats for LLM consumption"

---

## Phase 4: Core MCP Tools (Days 9-11)

### ROM Management Tools
- [ ] **4.1** Implement ROM loading tools
  - [ ] Create `src/handlers/emulation.py`
  - [ ] Add `load_rom` tool with validation
  - [ ] Add `list_roms` discovery tool
  - **Claude Code Tip**: "Implement ROM management tools using our handler registration patterns, focusing on proper path validation"

- [ ] **4.2** Add emulation control tools
  - [ ] Implement `reset_game` tool
  - [ ] Add `set_emulation_speed` tool
  - [ ] Create `get_session_status` tool
  - **Claude Code Tip**: "Add emulation control tools that provide LLMs with game state management capabilities"

### Input Control Tools
- [ ] **4.3** Create basic input tools
  - [ ] Create `src/handlers/input.py`
  - [ ] Implement `press_button` tool
  - [ ] Add `tick` tool for frame advancement
  - **Claude Code Tip**: "Implement the core input tools that allow LLMs to control the Game Boy, ensuring proper timing and validation"

- [ ] **4.4** Add advanced input tools
  - [ ] Implement `send_input_sequence` tool
  - [ ] Add `hold_button` and `release_button` tools
  - [ ] Create input validation and queuing
  - **Claude Code Tip**: "Add advanced input tools for complex game interactions, with comprehensive parameter validation"

### Screen and State Tools
- [ ] **4.5** Implement screen capture tools
  - [ ] Create `src/handlers/screen.py`
  - [ ] Add `get_screen` tool with format options
  - [ ] Implement `get_game_area` for analysis
  - **Claude Code Tip**: "Create screen capture tools that provide LLMs with visual game state in multiple useful formats"

- [ ] **4.6** Add save state tools
  - [ ] Create `src/handlers/state.py`
  - [ ] Implement `save_state` and `load_state` tools
  - [ ] Add state file management and validation
  - **Claude Code Tip**: "Implement save state tools with proper file management and error handling for game state persistence"

---

## Phase 5: Notebook System (Days 12-13)

### Notebook Implementation
- [ ] **5.1** Create notebook manager
  - [ ] Implement `src/notebook/notebook.py`
  - [ ] Create NotebookManager class with internal helpers
  - [ ] Add markdown section parsing and generation
  - **Claude Code Tip**: "Implement the simplified notebook system using our single-class approach with internal markdown handling"

- [ ] **5.2** Add file operations and safety
  - [ ] Implement atomic file writes
  - [ ] Add backup and rollback functionality
  - [ ] Create directory management for games
  - **Claude Code Tip**: "Add robust file operations to the notebook system with atomic writes and proper error recovery"

### Notebook Tools
- [ ] **5.3** Create notebook MCP tools
  - [ ] Add `save_notes` tool with section management
  - [ ] Implement `get_notes` tool with format options
  - [ ] Create `list_note_sections` and `delete_notes` tools
  - **Claude Code Tip**: "Implement the notebook MCP tools using our handler registration patterns, ensuring proper integration with the notebook manager"

- [ ] **5.4** Add size limits and validation
  - [ ] Implement section size limits
  - [ ] Add content validation
  - [ ] Create cleanup suggestions for oversized notebooks
  - **Claude Code Tip**: "Add size limiting and validation to prevent notebook bloat while providing helpful feedback to LLMs"

---

## Phase 6: Integration and Testing (Days 14-15)

### System Integration
- [ ] **6.1** Create comprehensive integration tests
  - [ ] Test complete ROM loading → gameplay → note taking flow
  - [ ] Validate error handling across all components
  - [ ] Test concurrent operations and edge cases
  - **Claude Code Tip**: "Create integration tests that simulate real LLM usage patterns and validate the complete system flow"

- [ ] **6.2** Add command-line interface
  - [ ] Create `src/cli.py` for easy server startup
  - [ ] Add configuration options and help text
  - [ ] Implement proper signal handling
  - **Claude Code Tip**: "Create a user-friendly CLI that makes it easy to start and configure the MCP server"

### Documentation and Examples
- [ ] **6.3** Create usage examples
  - [ ] Write example MCP interactions
  - [ ] Document common LLM usage patterns
  - [ ] Create troubleshooting guide
  - **Claude Code Tip**: "Generate comprehensive usage examples and documentation that help users understand how to interact with the MCP server"

- [ ] **6.4** Performance optimization
  - [ ] Profile critical paths (screen capture, input processing)
  - [ ] Optimize memory usage and caching
  - [ ] Add performance monitoring
  - **Claude Code Tip**: "Help me profile and optimize the performance bottlenecks in the MCP server"

---

## Phase 7: MVP Validation (Days 16-17)

### End-to-End Testing
- [ ] **7.1** Test with real Game Boy ROMs
  - [ ] Validate with classic games (Tetris, Pokemon, etc.)
  - [ ] Test edge cases and error conditions
  - [ ] Verify notebook persistence across sessions
  - **Claude Code Tip**: "Help me create comprehensive end-to-end tests using real Game Boy ROMs to validate MVP functionality"

- [ ] **7.2** LLM integration testing
  - [ ] Test actual Claude interactions
  - [ ] Validate tool discovery and usage
  - [ ] Check error message clarity and recovery
  - **Claude Code Tip**: "Help me test the actual LLM integration by simulating realistic Claude interactions with the MCP server"

### Polish and Documentation
- [ ] **7.3** Create installation package
  - [ ] Set up PyPI-ready package structure
  - [ ] Create installation and setup documentation
  - [ ] Add example configuration files
  - **Claude Code Tip**: "Help me create a professional Python package with proper setup.py/pyproject.toml for PyPI distribution"

- [ ] **7.4** Final documentation review
  - [ ] Update all documentation for accuracy
  - [ ] Create quick start guide
  - [ ] Add API reference documentation
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
- [ ] **Error handling provides actionable feedback**
- [ ] **Notebook system persists knowledge across sessions**
- [ ] **Screen capture works in multiple formats**
- [ ] **Input controls respond accurately**

### Technical Quality
- [ ] **All tests pass with >90% coverage**
- [ ] **Code follows style guidelines (Black, Ruff)**
- [ ] **Type checking passes (MyPy)**
- [ ] **No memory leaks during extended use**
- [ ] **Performance meets basic requirements (60fps emulation)**

### Documentation Quality
- [ ] **README provides clear setup instructions**
- [ ] **API documentation is complete**
- [ ] **Examples demonstrate real usage**
- [ ] **Troubleshooting guide covers common issues**

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