# MCP PyBoy Emulator Server - Project Design Document

## Executive Summary
Design and implement an MCP server that enables LLMs to interact with Game Boy games through PyBoy emulation, featuring minimal knowledge persistence, human handoff capabilities, and a web frontend for monitoring.

## Core Architecture

### System Components
1. **MCP Server Core**: JSON-RPC 2.0 server with PyBoy integration
2. **Game Session Manager**: Handles emulator instances and state synchronization
3. **Notebook System**: Simple markdown-based knowledge persistence with size limits
4. **Web Frontend**: Real-time monitoring and human takeover interface
5. **State Synchronization Engine**: WebSocket-based coordination between LLM and human

### Technology Stack
- **Backend**: Python 3.9+, PyBoy, FastAPI/WebSocket
- **Persistence**: Markdown files organized by game
- **Frontend**: HTML/CSS/JS with WebSocket client
- **MCP Protocol**: JSON-RPC 2.0 over stdio transport

## MCP Tool Interface Design

### Core Emulation Control
- `load_rom(rom_path)`: Initialize game session with specified ROM
- `list_roms(directory?)`: Discover available ROM files in specified or default directory
- `tick(count=1, render=True)`: Advance emulation by specified frames
- `set_speed(target_speed)`: Control emulation speed (0=unlimited, 1=normal, up to 5x)
- `stop_emulation(save=True)`: Halt emulator, optionally saving current state
- `reset_game()`: Reset the current game to initial state

### Input Control
- `press_button(button, delay=1)`: Press and auto-release button with timing
- `hold_button(button)`: Press and hold button (use with release_button)
- `release_button(button)`: Release previously held button
- `send_input_sequence(buttons, delays)`: Execute complex input sequences

### State & Screen Capture
- `get_screen()`: Capture current screen as image
- `get_game_area()`: Get simplified screen matrix for ML analysis
- `save_state(slot_name)`: Create named save state
- `load_state(slot_name)`: Restore named save state

### Notebook System (Game-Agnostic Knowledge)
- `save_notes(section, content)`: Update specific markdown section
- `get_notes(section?)`: Retrieve specific section or entire notes file
- `list_note_sections()`: List all available markdown sections
- `delete_notes(section)`: Remove a specific section

### Session Management Tools
- `get_session_status()`: Check emulator state and human control status
- `request_human_help(reason)`: Trigger human intervention
- `resume_ai_control()`: Return control to LLM

## Knowledge Persistence Design

### Notebook Architecture
- **Storage**: Single markdown file per game in game-specific directories
- **Organization**: Structured using markdown headings (## Controls, ## Objectives, etc.)
- **Size Limits**: Character limits per section to prevent bloat
- **Game Identification**: Directories named by ROM hash or sanitized game title

### Directory Structure
```
notebooks/
├── pokemon-blue/
│   └── notes.md
└── [other-games]/
    └── notes.md
```

### Example LLM Notebook Content
```markdown
# Pokemon Blue - Session Notes

## Controls Discovered
- A: Confirm/Interact
- B: Cancel/Back
- Start: Menu
- Select: ???

## Current Objective
Find the Pokemon Center in Pallet Town to heal starter Pokemon.

## Key Discoveries
- Tall grass contains wild Pokemon
- Pokemon have types that affect battle effectiveness
- Need to visit Professor Oak first

## Failed Strategies
- Tried to leave town immediately - blocked by Oak's assistant
- Attempted to catch Pokemon without Pokeballs - impossible

## Map Knowledge
- Pallet Town: Starting location, has Professor Oak's lab
- Route 1: North of Pallet Town, leads to Viridian City
```

### Benefits of Markdown Format
- **LLM-Native**: LLMs are extensively trained on markdown syntax
- **Human-Readable**: Easy to inspect and manually edit if needed
- **Natural Structure**: Headings provide clear organization
- **Flexible Content**: Supports lists, emphasis, code blocks naturally
- **Size Control**: Can enforce character limits per section

## Web Frontend Architecture

### Core Features
- Real-time screen display with WebSocket updates
- Game control panel for human intervention
- Knowledge viewer showing LLM's markdown notes
- Session handoff controls with state synchronization

### Human Takeover Flow
1. LLM requests help via `request_human_help(reason)`
2. Frontend displays notification with context and current state
3. Human takes control through web interface
4. Game state remains synchronized during transition
5. Human returns control via `resume_ai_control()`

## Implementation Roadmap

### Phase 1: MVP Core (2-3 weeks)
- Basic MCP server with PyBoy integration
- Essential game control tools (load_rom, tick, press_button, get_screen)
- Simple markdown notebook system with section management
- Command-line testing interface

### Phase 2: Enhanced Control (1 week)
- Complete input control tools (sequences, hold/release)
- Save state management
- ROM discovery functionality
- Speed and timing controls

### Phase 3: Web Frontend (2-3 weeks)
- Build real-time monitoring interface
- Implement human takeover mechanism
- Add WebSocket state synchronization
- Markdown knowledge visualization

### Phase 4: Advanced Features (Future)
- Sprite extraction and labeling tools
- Advanced memory inspection capabilities
- Performance optimization
- Multi-session knowledge aggregation

## Project Structure
```
mcp-pyboy/
├── src/
│   ├── mcp_server/          # Core MCP server implementation
│   ├── game_session/        # PyBoy integration and session management
│   ├── notebook/            # Notebook system code (manages MD files)
│   ├── frontend/            # Web interface and WebSocket handlers
│   └── utils/               # Shared utilities and helpers
├── tests/                   # Test suites
├── docs/                    # API documentation and design documents
├── examples/                # Usage examples and ROM tests
├── roms/                    # Game ROM storage directory
├── saves/                   # Game save states
├── notebooks/               # LLM knowledge files organized by game
│   ├── pokemon-blue/        # Game-specific directory
│   │   └── notes.md         # Single markdown file per game
│   └── harvest-moon/
│       └── notes.md
└── requirements.txt         # Python dependencies
```

## Key Design Benefits
- **Discovery-Oriented**: LLM learns game mechanics through experimentation
- **Frame-Precise Control**: `tick()` enables detailed game interaction
- **LLM-Friendly Persistence**: Markdown format natural for LLM use
- **Human Collaboration**: Seamless handoff when LLM needs assistance
- **Game-Agnostic**: Works with any Game Boy ROM without pre-coded mechanics
- **Size-Controlled**: Section-based limits prevent knowledge bloat
- **Organized Storage**: Clear directory structure for multi-game support

This design enables genuine discovery-based learning while providing practical persistence and human collaboration capabilities through familiar markdown formatting.