# Test ROMs

This directory contains test ROM files for testing the MCP PyBoy server.

## Mock ROMs

The test suite uses mock ROM data created programmatically. These mock ROMs:

- Have valid Game Boy ROM headers
- Are minimal in size (32KB by default)
- Contain test patterns for validation
- Don't require actual game content

## Real ROMs

If you need to test with real ROM files:

1. Place them in this directory
2. Use only ROMs you own legally
3. Common homebrew test ROMs:
   - `hello-world.gb` - Simple "Hello World" display
   - `input-test.gb` - Button input testing
   - `screen-test.gb` - Screen capture testing

## File Types

- `.gb` - Original Game Boy ROMs
- `.gbc` - Game Boy Color ROMs (limited support)
- `.sav` - Save files (not ROMs, but related)

## Usage in Tests

```python
# Using mock ROM data
from tests.fixtures.mock_pyboy import create_test_rom_data

rom_data = create_test_rom_data(size_kb=32)

# Using real ROM files (if available)
rom_path = "tests/fixtures/test_roms/hello-world.gb"
```

## Important Notes

- Never commit copyrighted ROM files to version control
- Use mock data for automated testing
- Real ROMs only for manual testing and development
- All test ROMs should be public domain or homebrew
