"""
PyBoy Emulator Wrapper

Provides a high-level interface for PyBoy emulation with LLM-friendly error handling.
This module abstracts PyBoy's complexity and provides consistent error messages
that help LLMs understand and recover from common issues.
"""

import logging
from pathlib import Path
from typing import Any

from pyboy import PyBoy

logger = logging.getLogger(__name__)


class EmulatorError(Exception):
    """Base exception for emulator-related errors with LLM-friendly messages."""

    pass


class ROMError(EmulatorError):
    """ROM-related errors with specific guidance for LLMs."""

    pass


class EmulatorStateError(EmulatorError):
    """Emulator state-related errors with recovery suggestions."""

    pass


class PyBoyEmulator:
    """
    PyBoy emulator wrapper with LLM-friendly interface.

    Provides lifecycle management, error handling, and consistent state management
    for Game Boy emulation. Designed to give LLMs clear feedback on operations
    and suggest recovery actions when things go wrong.
    """

    def __init__(self, headless: bool = True) -> None:
        """
        Initialize PyBoy emulator wrapper.

        Args:
            headless: Run emulator without GUI window (default: True for LLM use)
        """
        self.headless = headless
        self.pyboy: PyBoy | None = None
        self.current_rom_path: Path | None = None
        self.is_running = False

        logger.info(f"PyBoy emulator wrapper initialized (headless={headless})")

    def start(self) -> None:
        """
        Start the emulator without loading a ROM.

        Raises:
            EmulatorStateError: If emulator is already running
        """
        if self.is_running:
            raise EmulatorStateError(
                "Emulator is already running. Use stop() first or load a ROM directly."
            )

        logger.info("Starting PyBoy emulator...")
        self.is_running = True

    def stop(self) -> None:
        """
        Stop the emulator and clean up resources.

        This method is safe to call multiple times and will handle cleanup
        gracefully even if the emulator is already stopped.
        """
        if self.pyboy is not None:
            try:
                self.pyboy.stop()
                logger.info("PyBoy emulator stopped")
            except Exception as e:
                logger.warning(f"Error stopping PyBoy: {e}")
            finally:
                self.pyboy = None

        self.current_rom_path = None
        self.is_running = False

    def load_rom(self, rom_path: str | Path) -> None:
        """
        Load a Game Boy ROM file into the emulator.

        Args:
            rom_path: Path to the ROM file (.gb or .gbc)

        Raises:
            ROMError: If ROM file is invalid or cannot be loaded
            EmulatorStateError: If emulator fails to initialize
        """
        rom_path = Path(rom_path)

        # Validate ROM file exists
        if not rom_path.exists():
            raise ROMError(
                f"ROM file not found: {rom_path}. "
                f"Check the file path and ensure the ROM file exists."
            )

        # Validate ROM file extension
        if rom_path.suffix.lower() not in {".gb", ".gbc"}:
            raise ROMError(
                f"Invalid ROM file extension: {rom_path.suffix}. "
                f"Only .gb and .gbc files are supported."
            )

        # Stop current emulator if running
        if self.pyboy is not None:
            self.stop()

        try:
            # Initialize PyBoy with the ROM
            logger.info(f"Loading ROM: {rom_path}")

            # Configure PyBoy based on headless mode
            if self.headless:
                self.pyboy = PyBoy(str(rom_path), window="null")
            else:
                self.pyboy = PyBoy(str(rom_path))

            self.current_rom_path = rom_path
            self.is_running = True

            logger.info(f"ROM loaded successfully: {rom_path.name}")

        except Exception as e:
            self.pyboy = None
            self.current_rom_path = None
            self.is_running = False

            # Convert PyBoy exceptions to LLM-friendly messages
            error_msg = str(e).lower()
            if "invalid rom" in error_msg or "corrupt" in error_msg:
                raise ROMError(
                    f"ROM file appears to be corrupted or invalid: {rom_path.name}. "
                    f"Try a different ROM file or verify the file isn't damaged."
                ) from e
            elif "permission" in error_msg or "access" in error_msg:
                raise ROMError(
                    f"Cannot access ROM file: {rom_path}. "
                    f"Check file permissions and ensure it's not in use by another program."
                ) from e
            else:
                raise EmulatorStateError(
                    f"Failed to initialize emulator with ROM: {e}. "
                    f"This might be a PyBoy compatibility issue or system resource problem."
                ) from e

    def get_rom_info(self) -> dict[str, Any]:
        """
        Get information about the currently loaded ROM.

        Returns:
            dict: ROM information including name, path, and status

        Raises:
            EmulatorStateError: If no ROM is loaded
        """
        if not self.is_running or self.current_rom_path is None:
            raise EmulatorStateError(
                "No ROM is currently loaded. Use load_rom() to load a ROM first."
            )

        return {
            "name": self.current_rom_path.name,
            "path": str(self.current_rom_path),
            "size": self.current_rom_path.stat().st_size,
            "extension": self.current_rom_path.suffix,
            "is_running": self.is_running,
        }

    def get_pyboy_instance(self) -> PyBoy:
        """
        Get the underlying PyBoy instance for direct access.

        Returns:
            PyBoy: The PyBoy emulator instance

        Raises:
            EmulatorStateError: If emulator is not running
        """
        if not self.is_running or self.pyboy is None:
            raise EmulatorStateError(
                "Emulator is not running. Use load_rom() to start emulation first."
            )

        return self.pyboy

    def is_ready(self) -> bool:
        """
        Check if the emulator is ready for operations.

        Returns:
            bool: True if emulator is running and ready
        """
        return self.is_running and self.pyboy is not None

    def __enter__(self) -> "PyBoyEmulator":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.stop()
