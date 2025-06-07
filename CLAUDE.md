# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development and Running
```bash
# Start the application (recommended)
./control.sh start

# Stop the application
./control.sh stop

# Restart the application
./control.sh restart

# Check application status
./control.sh status

# View application logs
./control.sh logs

# Manual startup (alternative)
python app.py

# Install dependencies manually
pip install -r requirements.txt
```

### Configuration
```bash
# Create configuration from template
cp config.json.example config.json
# Edit config.json with actual server details
```

## Architecture

**MyControl** is a Flask-based web application for monitoring and managing homelab infrastructure through a centralized dashboard.

### Core Technology Stack
- **Flask 2.3.3**: Web framework with RESTful API
- **asyncssh**: Asynchronous SSH connections for host communication
- **Python 3.11+**: Runtime with asyncio for concurrent operations
- **JSON Configuration**: Host and service configuration management

### Application Structure

**Main Application** (`app.py`):
- Flask web server with comprehensive REST API
- Global terminal manager for SSH/nvtop sessions
- Deduplicating logging handler to prevent log spam
- Async operation support for non-blocking host communication

**Modular Libraries** (`libs/` directory):
- `power_management.py`: IPMI control via ipmitool (lanplus protocol)
- `ssh_utils.py`: Async SSH operations with parallel execution
- `terminal_management.py`: Web-based SSH/nvtop terminals via ttyd
- `gpu_management.py`: nvidia-smi integration and Docker container management
- `network_utils.py`: Ping-based connectivity monitoring
- `grafana_utils.py`: Dashboard integration utilities
- `config_utils.py`: Configuration loading and host lookup

### Key Features
- **Power Management**: Remote IPMI power control and status monitoring
- **Host Monitoring**: Real-time uptime, connectivity, and system status
- **GPU Monitoring**: nvidia-smi summary and topology visualization
- **Docker Management**: Container status monitoring and control
- **Web Terminals**: Browser-based SSH and nvtop access via ttyd
- **Dashboard Integration**: Embedded Grafana charts

### Security Model
- **Remote terminal access**: ttyd services bound to 0.0.0.0 for remote browser connectivity
- **Manual authentication**: No stored SSH credentials
- **Configuration protection**: config.json excluded from version control
- **Process isolation**: Background daemon with proper PID management

### API Architecture
- **Monitoring**: `/api/status`, `/api/uptime/<hostname>`, `/api/ping/<hostname>`
- **Power Control**: `/api/power-on/<hostname>`
- **Terminal Management**: `/api/ssh-terminal/<hostname>`, `/api/nvtop-terminal/<hostname>`
- **Infrastructure**: `/api/gpu-info/<hostname>`, `/api/docker-info/<hostname>`

### Process Management
The `control.sh` script provides:
- Automated virtual environment creation and management
- Background process management with PID tracking
- Log rotation (10MB max, 5 backups)
- Port configuration extraction from config.json

### Configuration System
- **JSON-based** with `config.json.example` template
- **Multi-host support** with individual IPMI/SSH credentials
- **Configurable timeouts** for SSH and network operations
- **Tool path configuration** for ipmitool, nvtop, sshpass, ttyd
- **Remote access configuration** with `local_hostname` for terminal URLs
- **Optional Grafana integration** with dashboard URL configuration

### Dependencies
- **Required**: Flask, asyncssh, ipmitool
- **Optional**: ttyd (web terminals), sshpass (password SSH), nvtop (GPU monitoring)
- **Runtime**: Python 3.11+ with virtual environment support