# Synthetic Test ROMs

This directory contains programmatically generated ROM files used for unit testing.

## Purpose
- Fast CI/CD builds (no external downloads)
- Predictable behavior for assertions
- No copyright concerns
- Minimal size (KB not MB)

## Usage
Synthetic ROMs are generated on-the-fly by test fixtures using the 
`create_test_rom_data()` function from `tests/fixtures/mock_pyboy.py`.

These ROMs contain:
- Valid Game Boy header structure
- Correct checksums
- Minimal program code
- Configurable size

## Note
Do not commit actual ROM files to this directory. They should be 
generated dynamically during test runs.