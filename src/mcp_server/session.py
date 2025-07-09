"""
Session Management for MCP PyBoy Server

Provides singleton game session management with proper lifecycle control,
error recovery, and state tracking for reliable emulator operation.
"""

import asyncio
import hashlib
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .emulator import EmulatorStateError, PyBoyEmulator, ROMError

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Possible states for a game session."""

    IDLE = "idle"  # No ROM loaded
    LOADING = "loading"  # ROM is being loaded
    RUNNING = "running"  # ROM loaded and running
    PAUSED = "paused"  # ROM loaded but paused
    ERROR = "error"  # Error state, needs recovery
    CRASHED = "crashed"  # Emulator crashed, needs restart


class SessionError(Exception):
    """Session-related errors with LLM-friendly messages."""

    pass


class GameSession:
    """
    Manages a single game session with state tracking and recovery.

    Provides lifecycle management, crash recovery, and session health monitoring
    to ensure reliable emulator operation across MCP tool calls.
    """

    def __init__(self) -> None:
        """Initialize a new game session."""
        self._emulator: PyBoyEmulator | None = None
        self._state = SessionState.IDLE
        self._current_rom_path: Path | None = None
        self._current_rom_hash: str | None = None
        self._session_start_time: float | None = None
        self._last_activity_time: float | None = None
        self._error_message: str | None = None
        self._lock = asyncio.Lock()

        # Session metrics
        self._total_frames = 0
        self._total_inputs = 0
        self._crash_count = 0

        logger.info("Game session initialized")

    @property
    def state(self) -> SessionState:
        """Get current session state."""
        return self._state

    @property
    def is_active(self) -> bool:
        """Check if session has an active ROM."""
        return self._state in (SessionState.RUNNING, SessionState.PAUSED)

    @property
    def rom_hash(self) -> str | None:
        """Get hash of current ROM for identification."""
        return self._current_rom_hash

    async def load_rom(self, rom_path: str | Path) -> dict[str, Any]:
        """
        Load a ROM with proper state management and error recovery.

        Args:
            rom_path: Path to the ROM file

        Returns:
            dict: Session information after loading

        Raises:
            SessionError: If loading fails
        """
        async with self._lock:
            rom_path = Path(rom_path)
            logger.info(f"Loading ROM: {rom_path}")

            # Reset any error state
            self._error_message = None

            # Set loading state
            self._state = SessionState.LOADING

            try:
                # Validate ROM file exists first
                if not rom_path.exists():
                    raise ROMError(
                        f"ROM file not found: {rom_path}. "
                        f"Check the file path and ensure the ROM file exists."
                    )

                # Calculate ROM hash for identification
                rom_hash = self._calculate_rom_hash(rom_path)

                # Create new emulator if needed or ROM changed
                if self._emulator is None or rom_hash != self._current_rom_hash:
                    if self._emulator:
                        logger.info("Stopping previous emulator instance")
                        self._emulator.stop()

                    self._emulator = PyBoyEmulator(headless=True)

                # Load the ROM
                self._emulator.load_rom(rom_path)

                # Update session state
                self._current_rom_path = rom_path
                self._current_rom_hash = rom_hash
                self._state = SessionState.RUNNING
                self._session_start_time = time.time()
                self._last_activity_time = time.time()
                self._total_frames = 0
                self._total_inputs = 0

                logger.info(f"ROM loaded successfully: {rom_path.name}")

                return {
                    "success": True,
                    "rom_name": rom_path.name,
                    "rom_hash": rom_hash,
                    "session_state": self._state.value,
                    "message": f"ROM '{rom_path.name}' loaded and running",
                }

            except (ROMError, EmulatorStateError) as e:
                self._state = SessionState.ERROR
                self._error_message = str(e)
                logger.error(f"Failed to load ROM: {e}")
                raise SessionError(f"Failed to load ROM: {e}") from e
            except Exception as e:
                self._state = SessionState.CRASHED
                self._error_message = f"Unexpected error: {e}"
                self._crash_count += 1
                logger.error(f"Session crashed while loading ROM: {e}")
                raise SessionError(
                    f"Session crashed while loading ROM. Try again or restart the server. Error: {e}"
                ) from e

    async def ensure_running(self) -> None:
        """
        Ensure session is in running state, attempting recovery if needed.

        Raises:
            SessionError: If session cannot be restored to running state
        """
        if self._state == SessionState.RUNNING:
            return

        if self._state == SessionState.PAUSED:
            await self.resume()
            return

        if self._state == SessionState.IDLE:
            raise SessionError("No ROM is loaded. Use load_rom() to load a game first.")

        if self._state == SessionState.LOADING:
            raise SessionError(
                "ROM is still loading. Please wait a moment and try again."
            )

        if self._state == SessionState.ERROR:
            raise SessionError(
                f"Session is in error state: {self._error_message}. "
                f"Try loading the ROM again or restart the server."
            )

        if self._state == SessionState.CRASHED:
            # Attempt recovery
            if self._current_rom_path:
                logger.warning("Attempting to recover crashed session...")
                try:
                    await self.load_rom(self._current_rom_path)
                    logger.info("Session recovered successfully")
                except Exception as e:
                    raise SessionError(
                        f"Failed to recover crashed session: {e}. "
                        f"Server restart may be required."
                    ) from e
            else:
                raise SessionError(
                    "Session crashed with no ROM to recover. "
                    "Load a new ROM to continue."
                )

    async def get_emulator(self) -> PyBoyEmulator:
        """
        Get the emulator instance, ensuring session is running.

        Returns:
            PyBoyEmulator: The active emulator instance

        Raises:
            SessionError: If emulator is not available
        """
        await self.ensure_running()

        if not self._emulator or not self._emulator.is_ready():
            raise SessionError(
                "Emulator is not ready. This shouldn't happen - please report this issue."
            )

        self._last_activity_time = time.time()
        return self._emulator

    async def pause(self) -> None:
        """Pause the current session."""
        async with self._lock:
            if self._state == SessionState.RUNNING:
                self._state = SessionState.PAUSED
                logger.info("Session paused")

    async def resume(self) -> None:
        """Resume a paused session."""
        async with self._lock:
            if self._state == SessionState.PAUSED:
                self._state = SessionState.RUNNING
                logger.info("Session resumed")

    async def stop(self) -> None:
        """Stop the session and clean up resources."""
        async with self._lock:
            if self._emulator:
                try:
                    self._emulator.stop()
                except Exception as e:
                    logger.warning(f"Error stopping emulator: {e}")
                finally:
                    self._emulator = None

            self._state = SessionState.IDLE
            self._current_rom_path = None
            self._current_rom_hash = None
            self._session_start_time = None
            self._error_message = None

            logger.info("Session stopped")

    async def get_info(self) -> dict[str, Any]:
        """Get detailed session information."""
        info: dict[str, Any] = {
            "state": self._state.value,
            "has_rom": self._current_rom_path is not None,
            "error_message": self._error_message,
            "crash_count": self._crash_count,
        }

        if self._current_rom_path:
            info.update(
                {
                    "rom_name": self._current_rom_path.name,
                    "rom_path": str(self._current_rom_path),
                    "rom_hash": self._current_rom_hash,
                }
            )

        if self._session_start_time:
            session_duration = time.time() - self._session_start_time
            idle_time = (
                time.time() - self._last_activity_time
                if self._last_activity_time
                else 0
            )

            info.update(
                {
                    "session_duration_seconds": round(session_duration, 2),
                    "idle_time_seconds": round(idle_time, 2),
                    "total_frames": self._total_frames,
                    "total_inputs": self._total_inputs,
                }
            )

        return info

    def record_frame_advance(self, frames: int = 1) -> None:
        """Record frame advancement for metrics."""
        self._total_frames += frames
        self._last_activity_time = time.time()

    def record_input(self) -> None:
        """Record input for metrics."""
        self._total_inputs += 1
        self._last_activity_time = time.time()

    def _calculate_rom_hash(self, rom_path: Path) -> str:
        """Calculate SHA256 hash of ROM file for identification."""
        sha256_hash = hashlib.sha256()
        with open(rom_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]  # First 16 chars for brevity


class SessionManager:
    """
    Singleton manager for game sessions.

    Ensures only one active game session exists and provides
    centralized access to session operations.
    """

    _instance: Optional["SessionManager"] = None
    _session: GameSession | None = None

    def __new__(cls) -> "SessionManager":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._session = GameSession()
        return cls._instance

    @property
    def session(self) -> GameSession:
        """Get the current game session."""
        if self._session is None:
            self._session = GameSession()
        return self._session

    async def reset(self) -> None:
        """Reset the session manager, stopping any active session."""
        if self._session:
            await self._session.stop()
        self._session = GameSession()
        logger.info("Session manager reset")


# Global session manager instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
