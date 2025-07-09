// MCP PyBoy Debugger JavaScript

class PyBoyDebugger {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectInterval = null;
        this.lastScreenUpdate = 0;
        this.fpsCounter = 0;
        this.fpsLastTime = 0;
        
        this.initializeElements();
        this.setupEventListeners();
        this.connect();
        this.loadRomList();
    }

    initializeElements() {
        // UI Elements
        this.connectionIndicator = document.getElementById('connection-indicator');
        this.connectionText = document.getElementById('connection-text');
        this.canvas = document.getElementById('gameboy-screen');
        this.ctx = this.canvas.getContext('2d');
        this.screenOverlay = document.getElementById('screen-overlay');
        this.screenFps = document.getElementById('screen-fps');
        this.lastUpdate = document.getElementById('last-update');
        
        // ROM elements
        this.romList = document.getElementById('rom-list');
        this.refreshRomsBtn = document.getElementById('refresh-roms-btn');
        this.romInfo = document.getElementById('rom-info');
        this.selectedRom = null;
        
        // Session elements
        this.sessionState = document.getElementById('session-state');
        this.sessionFrames = document.getElementById('session-frames');
        this.sessionInputs = document.getElementById('session-inputs');
        this.sessionDuration = document.getElementById('session-duration');
        this.resetSessionBtn = document.getElementById('reset-session-btn');
        
        // Log elements
        this.debugLog = document.getElementById('debug-log');
        this.clearLogBtn = document.getElementById('clear-log-btn');
        this.autoScrollCheckbox = document.getElementById('auto-scroll');
        
        // Control buttons
        this.controlButtons = document.querySelectorAll('[data-button]');
        
        // Initialize canvas
        this.ctx.fillStyle = '#1a202c';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setupEventListeners() {
        // ROM controls
        this.refreshRomsBtn.addEventListener('click', () => this.loadRomList());
        
        // Session controls
        this.resetSessionBtn.addEventListener('click', () => this.resetSession());
        
        // Log controls
        this.clearLogBtn.addEventListener('click', () => this.clearLog());
        
        // Game Boy controls
        this.controlButtons.forEach(button => {
            button.addEventListener('click', () => {
                const buttonName = button.dataset.button;
                this.pressButton(buttonName);
                this.animateButtonPress(button);
            });
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.log('info', `Connecting to ${wsUrl}...`);
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus('connected', 'Connected');
                this.log('success', 'WebSocket connected');
                
                if (this.reconnectInterval) {
                    clearInterval(this.reconnectInterval);
                    this.reconnectInterval = null;
                }
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    this.log('error', `Failed to parse message: ${error.message}`);
                }
            };
            
            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected', 'Disconnected');
                this.log('warning', 'WebSocket disconnected');
                this.scheduleReconnect();
            };
            
            this.ws.onerror = (error) => {
                this.updateConnectionStatus('error', 'Error');
                this.log('error', `WebSocket error: ${error.message || 'Unknown error'}`);
            };
            
        } catch (error) {
            this.log('error', `Failed to create WebSocket: ${error.message}`);
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (!this.reconnectInterval) {
            this.reconnectInterval = setInterval(() => {
                this.log('info', 'Attempting to reconnect...');
                this.connect();
            }, 3000);
        }
    }

    updateConnectionStatus(status, text) {
        this.connectionIndicator.className = `status-${status}`;
        this.connectionText.textContent = text;
    }

    handleMessage(data) {
        switch (data.type) {
            case 'update':
                this.handleScreenUpdate(data.screen, data.session);
                break;
            case 'error':
                this.log('error', data.message);
                break;
            case 'rom_loaded':
                this.log('success', `ROM loaded: ${data.result.rom_name}`);
                this.updateRomInfo(data.result);
                break;
            case 'button_pressed':
                this.log('info', `Button ${data.button} pressed`);
                break;
            case 'session_reset':
                this.log('info', 'Session reset');
                this.updateSessionInfo({});
                break;
            default:
                this.log('info', `Unknown message type: ${data.type}`);
        }
    }

    handleScreenUpdate(screenData, sessionData) {
        if (screenData && screenData.success && screenData.image_base64) {
            this.updateScreen(screenData.image_base64);
            this.screenOverlay.style.display = 'none';
        } else {
            this.screenOverlay.style.display = 'block';
        }
        
        if (sessionData) {
            this.updateSessionInfo(sessionData);
        }
        
        this.updateFPS();
        this.lastUpdate.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    }

    updateScreen(base64Image) {
        const img = new Image();
        img.onload = () => {
            this.ctx.imageSmoothingEnabled = false;
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
        };
        img.src = `data:image/png;base64,${base64Image}`;
    }

    updateFPS() {
        const now = performance.now();
        if (this.fpsLastTime) {
            this.fpsCounter++;
            if (now - this.fpsLastTime >= 1000) {
                this.screenFps.textContent = `FPS: ${this.fpsCounter}`;
                this.fpsCounter = 0;
                this.fpsLastTime = now;
            }
        } else {
            this.fpsLastTime = now;
        }
    }

    updateSessionInfo(sessionData) {
        this.sessionState.textContent = sessionData.state || 'unknown';
        this.sessionFrames.textContent = sessionData.total_frames || '0';
        this.sessionInputs.textContent = sessionData.total_inputs || '0';
        
        if (sessionData.session_duration_seconds) {
            const duration = Math.round(sessionData.session_duration_seconds);
            this.sessionDuration.textContent = `${duration}s`;
        } else {
            this.sessionDuration.textContent = '0s';
        }
    }

    updateRomInfo(romData) {
        if (romData.success) {
            this.romInfo.innerHTML = `
                <div class="info-row">
                    <span class="label">Name:</span>
                    <span>${romData.rom_name}</span>
                </div>
                <div class="info-row">
                    <span class="label">State:</span>
                    <span>${romData.session_state}</span>
                </div>
                <div class="info-row">
                    <span class="label">Hash:</span>
                    <span>${romData.rom_hash || 'N/A'}</span>
                </div>
            `;
        }
    }

    async loadRomList() {
        try {
            this.romList.innerHTML = '<div class="rom-list-loading">Loading ROMs...</div>';
            
            const response = await fetch('/api/roms');
            if (!response.ok) {
                throw new Error('Failed to fetch ROM list');
            }
            
            const data = await response.json();
            this.displayRomList(data.roms);
            
        } catch (error) {
            this.log('error', `Failed to load ROM list: ${error.message}`);
            this.romList.innerHTML = '<div class="rom-list-empty">Failed to load ROM list</div>';
        }
    }
    
    displayRomList(roms) {
        if (roms.length === 0) {
            this.romList.innerHTML = '<div class="rom-list-empty">No ROMs found in /roms directory</div>';
            return;
        }
        
        this.romList.innerHTML = '';
        
        roms.forEach(rom => {
            const romItem = document.createElement('div');
            romItem.className = 'rom-item';
            romItem.dataset.path = rom.path;
            
            const sizeFormatted = this.formatFileSize(rom.size);
            
            romItem.innerHTML = `
                <div class="rom-name">${rom.name}</div>
                <div class="rom-details">
                    <span class="rom-extension">${rom.extension}</span>
                    <span class="rom-size">${sizeFormatted}</span>
                </div>
            `;
            
            romItem.addEventListener('click', () => this.selectRom(romItem, rom));
            
            this.romList.appendChild(romItem);
        });
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    selectRom(romItem, rom) {
        // Remove previous selection
        const previousSelected = this.romList.querySelector('.rom-item.selected');
        if (previousSelected) {
            previousSelected.classList.remove('selected');
        }
        
        // Select new ROM
        romItem.classList.add('selected');
        this.selectedRom = rom;
        
        // Load the ROM
        this.loadRom(rom.path);
    }

    async loadRom(romPath) {
        if (!romPath) {
            this.log('error', 'No ROM path provided');
            return;
        }
        
        try {
            this.log('info', `Loading ROM: ${romPath}`);
            const response = await fetch('/api/load-rom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ rom_path: romPath }),
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to load ROM');
            }
            
            const result = await response.json();
            this.log('success', `ROM loaded successfully: ${result.rom_name}`);
            
        } catch (error) {
            this.log('error', `Failed to load ROM: ${error.message}`);
        }
    }

    async pressButton(button, duration = 1) {
        try {
            const response = await fetch('/api/button', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ button: button, duration: duration }),
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to press button');
            }
            
        } catch (error) {
            this.log('error', `Failed to press button ${button}: ${error.message}`);
        }
    }

    async resetSession() {
        try {
            this.log('info', 'Resetting session...');
            const response = await fetch('/api/session/reset', {
                method: 'POST',
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to reset session');
            }
            
            this.log('success', 'Session reset successfully');
            
        } catch (error) {
            this.log('error', `Failed to reset session: ${error.message}`);
        }
    }

    animateButtonPress(button) {
        button.classList.add('btn-pressed');
        setTimeout(() => {
            button.classList.remove('btn-pressed');
        }, 150);
    }

    handleKeyDown(e) {
        const keyMap = {
            'ArrowUp': 'UP',
            'ArrowDown': 'DOWN',
            'ArrowLeft': 'LEFT',
            'ArrowRight': 'RIGHT',
            'KeyZ': 'A',
            'KeyX': 'B',
            'Enter': 'START',
            'ShiftRight': 'SELECT',
            'Space': 'SELECT'
        };
        
        const button = keyMap[e.code];
        if (button) {
            e.preventDefault();
            this.pressButton(button);
            
            // Find and animate the corresponding UI button
            const uiButton = document.querySelector(`[data-button="${button}"]`);
            if (uiButton) {
                this.animateButtonPress(uiButton);
            }
        }
    }

    handleKeyUp(e) {
        // Future: Handle button release
    }

    log(level, message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        logEntry.innerHTML = `
            <span class="timestamp">${timestamp}</span>
            <span class="message">${message}</span>
        `;
        
        this.debugLog.appendChild(logEntry);
        
        // Auto-scroll if enabled
        if (this.autoScrollCheckbox.checked) {
            this.debugLog.scrollTop = this.debugLog.scrollHeight;
        }
        
        // Limit log entries to prevent memory issues
        const entries = this.debugLog.children;
        if (entries.length > 100) {
            this.debugLog.removeChild(entries[0]);
        }
    }

    clearLog() {
        this.debugLog.innerHTML = '';
        this.log('info', 'Log cleared');
    }
}

// Initialize the debugger when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PyBoyDebugger();
});