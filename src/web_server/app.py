"""
FastAPI web server for MCP PyBoy debugging interface.

Provides a web UI for monitoring emulator state, viewing screen output,
and sending control inputs during development.
"""

import asyncio
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from time import time
from typing import Annotated, Any

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from mcp_server.server import get_screen, get_session_info, load_rom, press_button
from mcp_server.session import get_session_manager


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "MCP PyBoy Debugger"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    update_interval: float = 0.2
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"  # Load from .env file if it exists


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance. Only created once due to lru_cache."""
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]

# Configure logging with environment variable support
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


# Create FastAPI app with default title (will be shown in settings endpoint)
app = FastAPI(
    title="MCP PyBoy Debugger",
    description="Web debugging interface for MCP PyBoy emulator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Get the static files directory
STATIC_DIR = Path(__file__).parent.parent / "web_frontend"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# WebSocket connection manager
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        if not self.active_connections:
            return

        # Create tasks for parallel sending
        tasks = []
        connections_snapshot = self.active_connections.copy()

        for connection in connections_snapshot:
            task = asyncio.create_task(self._send_safe(connection, message))
            tasks.append(task)

        # Wait for all sends to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_safe(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send message: {e}")
            await self.disconnect(websocket)


manager = ConnectionManager()


@app.get("/")
async def get_index() -> FileResponse:
    """Serve the main debugging interface."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, settings: SettingsDep) -> None:
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    update_interval = settings.update_interval
    last_screen_hash = None

    try:
        # Start background task for updates
        async def send_updates() -> None:
            nonlocal last_screen_hash
            while True:
                try:
                    screen_data = await get_screen()
                    # Only send if screen changed
                    screen_hash = hash(str(screen_data))
                    if screen_hash != last_screen_hash:
                        session_info = await get_session_info()
                        message = {
                            "type": "update",
                            "screen": screen_data,
                            "session": session_info,
                            "timestamp": time(),
                        }
                        await websocket.send_text(json.dumps(message))
                        last_screen_hash = screen_hash

                    await asyncio.sleep(update_interval)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                    await asyncio.sleep(update_interval)

        # Start update task
        update_task = asyncio.create_task(send_updates())

        # Handle incoming messages
        while True:
            try:
                message = await websocket.receive_text()
                logger.info(f"Received message: {message}")
                # Handle client commands here
                # await handle_client_message(message)
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        if "update_task" in locals():
            update_task.cancel()
        await manager.disconnect(websocket)


class SessionInfoResponse(BaseModel):
    status: str
    rom_loaded: bool
    rom_path: str | None = None
    frame_count: int = 0
    timestamp: float


@app.get("/api/session", response_model=SessionInfoResponse)
async def api_get_session_info() -> SessionInfoResponse:
    """Get current session information."""
    session_info = await get_session_info()
    return SessionInfoResponse(**session_info)


class RomData(BaseModel):
    rom_path: str = Field(..., description="Path to the ROM file")


class LoadRomResponse(BaseModel):
    success: bool
    message: str
    rom_name: str
    rom_hash: str
    session_state: str
    timestamp: float


@app.post("/api/load-rom", response_model=LoadRomResponse)
async def api_load_rom(rom_data: RomData) -> LoadRomResponse:
    """Load a ROM file."""
    # Validate file exists
    if not Path(rom_data.rom_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ROM file not found"
        )

    result = await load_rom(rom_data.rom_path)
    # Broadcast update to all connected clients
    await manager.broadcast(
        {
            "type": "rom_loaded",
            "result": result,
            "timestamp": time(),
        }
    )

    # Add timestamp for consistency
    result["timestamp"] = time()
    return LoadRomResponse(**result)


class ButtonData(BaseModel):
    button: str = Field(..., description="Button to press")
    duration: int = Field(1, description="Duration of button press in seconds")


class ButtonResponse(BaseModel):
    success: bool
    message: str
    button: str
    duration: int
    timestamp: float


@app.post("/api/button", response_model=ButtonResponse)
async def api_press_button(button_data: ButtonData) -> ButtonResponse:
    """Press a Game Boy button."""
    result = await press_button(button_data.button, button_data.duration)
    # Broadcast button press to all connected clients
    await manager.broadcast(
        {
            "type": "button_pressed",
            "button": button_data.button,
            "duration": button_data.duration,
            "result": result,
            "timestamp": time(),
        }
    )
    return ButtonResponse(
        **result, button=button_data.button, duration=button_data.duration
    )


class ScreenResponse(BaseModel):
    screen_data: str  # Base64 encoded image
    width: int
    height: int
    timestamp: float


@app.get("/api/screen", response_model=ScreenResponse)
async def api_get_screen() -> ScreenResponse:
    """Get current screen (fallback for non-WebSocket clients)."""
    screen_data = await get_screen()
    return ScreenResponse(**screen_data)


class SessionResetResponse(BaseModel):
    success: bool
    message: str
    timestamp: float


@app.post("/api/session/reset", response_model=SessionResetResponse)
async def api_reset_session() -> SessionResetResponse:
    """Reset the current session."""
    session_manager = get_session_manager()
    await session_manager.reset()

    timestamp = asyncio.get_event_loop().time()
    result = SessionResetResponse(
        success=True, message="Session reset successfully", timestamp=timestamp
    )

    # Broadcast reset to all connected clients
    await manager.broadcast(
        {
            "type": "session_reset",
            "result": result.model_dump(),
            "timestamp": timestamp,
        }
    )

    return result


class HealthResponse(BaseModel):
    status: str
    service: str
    connections: int


@app.get("/api/settings")
async def api_get_settings(settings: SettingsDep) -> dict[str, Any]:
    """Get current application settings (useful for debugging/monitoring)."""
    return {
        "app_name": settings.app_name,
        "host": settings.host,
        "port": settings.port,
        "update_interval": settings.update_interval,
        # Note: Don't expose sensitive settings like API keys
    }


class RomInfo(BaseModel):
    name: str
    path: str
    size: int
    extension: str


class RomListResponse(BaseModel):
    roms: list[RomInfo]
    total: int


@app.get("/api/roms", response_model=RomListResponse)
async def api_list_roms() -> RomListResponse:
    """List all available ROMs in the roms directory."""
    roms_dir = Path(__file__).parent.parent.parent / "roms"
    roms = []

    if roms_dir.exists() and roms_dir.is_dir():
        for rom_file in roms_dir.glob("*.gb"):
            try:
                stat = rom_file.stat()
                roms.append(
                    RomInfo(
                        name=rom_file.name,
                        path=str(rom_file),
                        size=stat.st_size,
                        extension=rom_file.suffix,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to read ROM file {rom_file}: {e}")

        # Also check for .gbc files
        for rom_file in roms_dir.glob("*.gbc"):
            try:
                stat = rom_file.stat()
                roms.append(
                    RomInfo(
                        name=rom_file.name,
                        path=str(rom_file),
                        size=stat.st_size,
                        extension=rom_file.suffix,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to read ROM file {rom_file}: {e}")

    # Sort by name
    roms.sort(key=lambda x: x.name.lower())

    return RomListResponse(roms=roms, total=len(roms))


@app.get("/api/health", response_model=HealthResponse)
async def api_health(settings: SettingsDep) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,  # Using settings from dependency injection
        connections=len(manager.active_connections),
    )


# Global exception handler for all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler that logs errors and returns a consistent 500 response.
    This eliminates the need for repetitive try-catch blocks in path operations.
    """
    # Extract the operation name from the request path for better logging
    operation_name = request.url.path.replace("/api/", "").replace("-", " ")

    logger.error(f"Error in {operation_name}: {exc}")

    # Return a consistent error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"},
    )


def main() -> None:
    """Run the debugging web server."""
    import uvicorn

    # Get settings once for startup
    settings = get_settings()

    logger.info("Starting MCP PyBoy Debugger...")
    logger.info(
        f"Web interface will be available at: http://{settings.host}:{settings.port}"
    )

    uvicorn.run(
        "web_server.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()
