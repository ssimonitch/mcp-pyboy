# Hardware Test ROMs

This directory is for open-source Game Boy test ROMs that verify hardware behavior.

## Recommended Test ROMs

### CPU Tests
- **Blargg's CPU instruction tests** - Tests all CPU opcodes
  - Source: https://github.com/retrio/gb-test-roms
  - License: Open source
  
### PPU Tests  
- **dmg-acid2** - Comprehensive PPU rendering test
  - Source: https://github.com/mattcurrie/dmg-acid2
  - License: MIT

### Audio Tests
- **Blargg's Game Boy sound tests**
  - Tests all audio channels and features

## Installation
These ROMs are NOT included in the repository. To use them:

1. Download test ROMs from their source repositories
2. Place them in this directory
3. Run integration tests with `pytest tests/integration -v`

## Note
These test ROMs are optional. The test suite will skip integration tests
if the ROMs are not present. Unit tests use synthetic ROMs and do not
require these files.