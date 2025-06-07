#!/bin/bash

# MyControl update script
# Pulls latest changes from git and restarts the application if changes are detected

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"
UPDATE_LOG="$LOGS_DIR/update.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$UPDATE_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$UPDATE_LOG"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$UPDATE_LOG"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$UPDATE_LOG"
}

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Change to script directory
cd "$SCRIPT_DIR"

log "Starting MyControl update process..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    error "Not in a git repository. Cannot update."
fi

# Get current commit hash
CURRENT_COMMIT=$(git rev-parse HEAD)
log "Current commit: $CURRENT_COMMIT"

# Fetch latest changes
log "Fetching latest changes from remote..."
if ! git fetch origin; then
    error "Failed to fetch from remote repository"
fi

# Get the latest commit hash from remote
LATEST_COMMIT=$(git rev-parse origin/main)
log "Latest remote commit: $LATEST_COMMIT"

# Check if there are changes
if [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ]; then
    info "No updates available. Application is already up to date."
    exit 0
fi

log "Updates detected! Proceeding with update..."

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    warn "Uncommitted changes detected. Stashing changes..."
    git stash push -m "Auto-stash before update $(date '+%Y-%m-%d %H:%M:%S')"
    STASHED=true
else
    STASHED=false
fi

# Pull the latest changes
log "Pulling latest changes..."
if ! git pull origin main; then
    error "Failed to pull changes from remote repository"
fi

# Get the new commit info
NEW_COMMIT=$(git rev-parse HEAD)
COMMIT_MESSAGE=$(git log --format="%s" -n 1 HEAD)
log "Updated to commit: $NEW_COMMIT"
log "Latest change: $COMMIT_MESSAGE"

# Update version information
log "Updating version information..."
if [ -d "venv" ]; then
    source venv/bin/activate
    python -c "from libs.version import write_version_file; write_version_file()" 2>/dev/null || true
else
    python -c "from libs.version import write_version_file; write_version_file()" 2>/dev/null || true
fi

# Apply stashed changes if any
if [ "$STASHED" = true ]; then
    log "Reapplying stashed changes..."
    if ! git stash pop; then
        warn "Failed to apply stashed changes. They remain in stash."
    fi
fi

# Check if requirements.txt changed and update dependencies
if git diff --name-only "$CURRENT_COMMIT" HEAD | grep -q "requirements.txt"; then
    log "requirements.txt changed. Updating dependencies..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install -r requirements.txt
    else
        warn "Virtual environment not found. Dependencies may need manual update."
    fi
fi

# Restart the application
log "Restarting MyControl application..."
if [ -f "./control.sh" ]; then
    ./control.sh restart
    if [ $? -eq 0 ]; then
        log "MyControl successfully updated and restarted!"
        log "Update completed: $CURRENT_COMMIT -> $NEW_COMMIT"
    else
        error "Failed to restart MyControl application"
    fi
else
    error "control.sh script not found. Cannot restart application."
fi
