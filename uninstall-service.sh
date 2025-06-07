#!/bin/bash

# My Lab Control systemd service uninstaller
# This script removes the My Lab Control systemd service

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

INSTALL_DIR="/opt/mylabcontrol"
SERVICE_NAME="mylabcontrol"
USER_NAME="mylabcontrol"

log "My Lab Control systemd service uninstaller"
echo ""

# Check if service exists
if ! systemctl list-unit-files | grep -q "^$SERVICE_NAME.service"; then
    warn "Service $SERVICE_NAME is not installed"
    exit 0
fi

# Confirm uninstall
warn "This will completely remove My Lab Control service and all its files"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Uninstall cancelled"
    exit 0
fi

# Stop and disable service
log "Stopping service..."
systemctl stop "$SERVICE_NAME" || true

log "Disabling service..."
systemctl disable "$SERVICE_NAME" || true

# Remove service file
log "Removing service file..."
rm -f "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
log "Reloading systemd daemon..."
systemctl daemon-reload

# Ask about removing files
read -p "Do you want to remove all application files from $INSTALL_DIR? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Removing application files..."
    rm -rf "$INSTALL_DIR"
else
    info "Application files preserved at: $INSTALL_DIR"
fi

# Ask about removing user
read -p "Do you want to remove the $USER_NAME user account? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Removing user account..."
    userdel "$USER_NAME" || true
else
    info "User account $USER_NAME preserved"
fi

echo ""
log "Uninstall completed successfully!"

# Reset systemd if needed
systemctl reset-failed || true