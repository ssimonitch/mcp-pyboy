"""Utility functions for development scripts."""

from pathlib import Path


def find_project_root() -> Path:
    """
    Find project root by looking for pyproject.toml.

    Returns:
        Path to project root directory.

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found.
    """
    start_path = Path(__file__).parent

    current = start_path
    while current != current.parent:  # Stop at filesystem root
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent

    raise FileNotFoundError("Could not find pyproject.toml in any parent directory")
