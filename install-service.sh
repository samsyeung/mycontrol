#!/bin/bash

# My Lab Control systemd service installer
# This script helps install My Lab Control as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/mylabcontrol.service"
INSTALL_DIR="/opt/mylabcontrol"
SERVICE_NAME="mylabcontrol"
USER_NAME="mylabcontrol"
GROUP_NAME="mylabcontrol"

log "My Lab Control systemd service installer"
echo ""

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    error "Service file not found: $SERVICE_FILE"
fi

# Check if already installed
if systemctl list-unit-files | grep -q "^$SERVICE_NAME.service"; then
    warn "Service $SERVICE_NAME is already installed"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Installation cancelled"
        exit 0
    fi
    
    log "Stopping existing service..."
    systemctl stop "$SERVICE_NAME" || true
    systemctl disable "$SERVICE_NAME" || true
fi

# Create user and group
if ! id "$USER_NAME" &>/dev/null; then
    log "Creating user: $USER_NAME"
    useradd --system --home-dir "$INSTALL_DIR" --shell /bin/bash --comment "My Lab Control Service" "$USER_NAME"
else
    info "User $USER_NAME already exists"
fi

# Create installation directory
log "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy application files
log "Copying application files..."
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

# Set ownership
log "Setting file ownership..."
chown -R "$USER_NAME:$GROUP_NAME" "$INSTALL_DIR"

# Make scripts executable
chmod +x "$INSTALL_DIR/control.sh"
chmod +x "$INSTALL_DIR/update.sh" 2>/dev/null || true

# Check if config exists
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    if [ -f "$INSTALL_DIR/config.json.example" ]; then
        warn "config.json not found. You need to create it before starting the service."
        info "Example configuration is available at: $INSTALL_DIR/config.json.example"
        info "Copy and edit it: sudo cp $INSTALL_DIR/config.json.example $INSTALL_DIR/config.json"
        info "Then edit: sudo nano $INSTALL_DIR/config.json"
    else
        warn "No configuration file or example found"
    fi
fi

# Install systemd service
log "Installing systemd service..."
cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
log "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
log "Enabling service..."
systemctl enable "$SERVICE_NAME"

echo ""
log "Installation completed successfully!"
echo ""
info "Next steps:"
echo "  1. Create/edit configuration: sudo nano $INSTALL_DIR/config.json"
echo "  2. Start the service: sudo systemctl start $SERVICE_NAME"
echo "  3. Check status: sudo systemctl status $SERVICE_NAME"
echo "  4. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
info "Service management commands:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo "  Disable: sudo systemctl disable $SERVICE_NAME"
echo ""

# Ask if user wants to create config now
if [ ! -f "$INSTALL_DIR/config.json" ] && [ -f "$INSTALL_DIR/config.json.example" ]; then
    read -p "Do you want to copy the example config now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$INSTALL_DIR/config.json.example" "$INSTALL_DIR/config.json"
        chown "$USER_NAME:$GROUP_NAME" "$INSTALL_DIR/config.json"
        info "Example config copied to $INSTALL_DIR/config.json"
        info "Please edit it with your actual server details before starting the service"
    fi
fi

log "Installation script completed"