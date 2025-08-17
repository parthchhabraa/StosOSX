#!/bin/bash

# StosOS Update Script
# Updates StosOS to the latest version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STOSOS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$STOSOS_DIR/venv"
BACKUP_DIR="$HOME/stosos_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$HOME/stosos_update.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
    log "STEP: $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log "INFO: $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "ERROR: $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    StosOS Updater                           ║"
    echo "║                 Update to Latest Version                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_prerequisites() {
    print_step "Checking prerequisites"
    
    # Check if we're in the right directory
    if [ ! -f "$STOSOS_DIR/main.py" ]; then
        print_error "Not in StosOS directory or main.py not found"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        exit 1
    fi
    
    # Check for required commands
    for cmd in python3 git systemctl; do
        if ! command -v "$cmd" &> /dev/null; then
            print_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    print_info "Prerequisites check passed"
}

get_current_version() {
    if [ -f "$STOSOS_DIR/VERSION" ]; then
        cat "$STOSOS_DIR/VERSION"
    else
        echo "unknown"
    fi
}

stop_service() {
    print_step "Stopping StosOS service"
    
    SERVICE_WAS_RUNNING=false
    
    # Check if service is running
    if systemctl --user is-active --quiet stosos 2>/dev/null; then
        print_info "Stopping StosOS service..."
        systemctl --user stop stosos
        SERVICE_WAS_RUNNING=true
        
        # Wait for service to stop
        sleep 3
        
        if systemctl --user is-active --quiet stosos 2>/dev/null; then
            print_warning "Service still running, forcing stop..."
            systemctl --user kill stosos
            sleep 2
        fi
    else
        print_info "StosOS service is not running"
    fi
}

create_backup() {
    print_step "Creating backup"
    
    print_info "Creating backup at $BACKUP_DIR..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Copy important files and directories
    cp -r "$STOSOS_DIR"/{core,modules,ui,models,services} "$BACKUP_DIR/" 2>/dev/null || true
    cp "$STOSOS_DIR"/{main.py,VERSION,requirements.txt,*.service} "$BACKUP_DIR/" 2>/dev/null || true
    
    # Copy configuration and data (but not logs)
    cp -r "$STOSOS_DIR/config" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "$STOSOS_DIR/data" "$BACKUP_DIR/" 2>/dev/null || true
    
    print_info "Backup created successfully"
}

update_from_git() {
    print_step "Updating from git repository"
    
    if [ ! -d "$STOSOS_DIR/.git" ]; then
        print_warning "No git repository found. Skipping git update."
        return 0
    fi
    
    # Save current branch
    CURRENT_BRANCH=$(git -C "$STOSOS_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    
    print_info "Current branch: $CURRENT_BRANCH"
    
    # Fetch latest changes
    print_info "Fetching latest changes..."
    git -C "$STOSOS_DIR" fetch origin
    
    # Check if there are updates
    LOCAL_COMMIT=$(git -C "$STOSOS_DIR" rev-parse HEAD)
    REMOTE_COMMIT=$(git -C "$STOSOS_DIR" rev-parse "origin/$CURRENT_BRANCH")
    
    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        print_info "Already up to date"
        return 0
    fi
    
    # Pull updates
    print_info "Pulling updates..."
    git -C "$STOSOS_DIR" pull origin "$CURRENT_BRANCH"
    
    print_info "Git update completed"
}

update_dependencies() {
    print_step "Updating Python dependencies"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Update dependencies from requirements.txt
    if [ -f "$STOSOS_DIR/requirements.txt" ]; then
        print_info "Installing updated dependencies..."
        pip install --upgrade -r "$STOSOS_DIR/requirements.txt"
    else
        print_warning "requirements.txt not found, skipping dependency update"
    fi
    
    print_info "Dependencies updated"
}

update_systemd_service() {
    print_step "Updating systemd service"
    
    # Copy updated service file if it exists
    if [ -f "$STOSOS_DIR/stosos.service" ]; then
        print_info "Updating systemd service file..."
        
        # Create user systemd directory if it doesn't exist
        mkdir -p "$HOME/.config/systemd/user"
        
        # Copy service file
        cp "$STOSOS_DIR/stosos.service" "$HOME/.config/systemd/user/"
        
        # Update paths in service file
        sed -i "s|/home/pi/stosos|$STOSOS_DIR|g" "$HOME/.config/systemd/user/stosos.service"
        sed -i "s|User=pi|User=$USER|g" "$HOME/.config/systemd/user/stosos.service"
        
        # Reload systemd
        systemctl --user daemon-reload
        
        print_info "Systemd service updated"
    else
        print_warning "Service file not found, skipping service update"
    fi
}

run_post_update_tasks() {
    print_step "Running post-update tasks"
    
    # Run any database migrations or setup tasks
    if [ -f "$STOSOS_DIR/migrate.py" ]; then
        print_info "Running database migrations..."
        source "$VENV_DIR/bin/activate"
        python "$STOSOS_DIR/migrate.py"
    fi
    
    # Update file permissions
    chmod +x "$STOSOS_DIR"/*.sh 2>/dev/null || true
    
    print_info "Post-update tasks completed"
}

start_service() {
    print_step "Starting StosOS service"
    
    if [ "$SERVICE_WAS_RUNNING" = true ]; then
        print_info "Restarting StosOS service..."
        systemctl --user start stosos
        
        # Wait a moment and check if service started successfully
        sleep 3
        
        if systemctl --user is-active --quiet stosos; then
            print_info "StosOS service started successfully"
        else
            print_error "Failed to start StosOS service"
            print_info "Check logs with: journalctl --user -u stosos -f"
            return 1
        fi
    else
        print_info "Service was not running before update, not starting automatically"
    fi
}

cleanup() {
    print_step "Cleaning up"
    
    # Remove temporary files
    rm -f "$HOME"/stosos_*.tmp 2>/dev/null || true
    
    print_info "Cleanup completed"
}

rollback() {
    print_error "Update failed, attempting rollback..."
    
    if [ -d "$BACKUP_DIR" ]; then
        print_info "Restoring from backup: $BACKUP_DIR"
        
        # Stop service if running
        systemctl --user stop stosos 2>/dev/null || true
        
        # Restore files (excluding venv, data, logs)
        for item in core modules ui models services main.py VERSION requirements.txt *.service; do
            if [ -e "$BACKUP_DIR/$item" ]; then
                rm -rf "$STOSOS_DIR/$item" 2>/dev/null || true
                cp -r "$BACKUP_DIR/$item" "$STOSOS_DIR/"
            fi
        done
        
        # Restore config if it doesn't exist
        if [ ! -d "$STOSOS_DIR/config" ] && [ -d "$BACKUP_DIR/config" ]; then
            cp -r "$BACKUP_DIR/config" "$STOSOS_DIR/"
        fi
        
        # Reload systemd and restart service if it was running
        systemctl --user daemon-reload
        if [ "$SERVICE_WAS_RUNNING" = true ]; then
            systemctl --user start stosos
        fi
        
        print_info "Rollback completed"
    else
        print_error "No backup found for rollback"
    fi
}

print_completion_message() {
    NEW_VERSION=$(get_current_version)
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   Update Completed!                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo "StosOS has been successfully updated!"
    echo "Version: $NEW_VERSION"
    echo
    echo "Backup location: $BACKUP_DIR"
    echo "Update log: $LOG_FILE"
    echo
    echo "Service status:"
    systemctl --user status stosos --no-pager -l || true
    echo
}

# Main update flow
main() {
    print_header
    
    OLD_VERSION=$(get_current_version)
    log "Starting StosOS update from version $OLD_VERSION"
    
    # Set trap for cleanup on error
    trap 'rollback; exit 1' ERR
    
    check_prerequisites
    stop_service
    create_backup
    update_from_git
    update_dependencies
    update_systemd_service
    run_post_update_tasks
    start_service
    cleanup
    
    print_completion_message
    
    log "Update completed successfully"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "StosOS Update Script"
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --no-service   Don't manage systemd service"
        echo "  --backup-only  Only create backup, don't update"
        echo ""
        exit 0
        ;;
    --no-service)
        SERVICE_WAS_RUNNING=false
        ;;
    --backup-only)
        print_header
        check_prerequisites
        create_backup
        print_info "Backup created at: $BACKUP_DIR"
        exit 0
        ;;
esac

# Run main function
main "$@"