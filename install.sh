#!/bin/bash

# StosOS Installation Script for Raspberry Pi OS
# This script sets up StosOS as a desktop environment extension

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Dynamic user detection
STOSOS_USER="$USER"
STOSOS_HOME="$HOME"
STOSOS_DIR="$STOSOS_HOME/stosos"
VENV_DIR="$STOSOS_DIR/venv"
SERVICE_NAME="stosos"

# Logging
LOG_FILE="$HOME/stosos_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    StosOS Installer                          ║"
    echo "║              Raspberry Pi Desktop Environment                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
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

check_requirements() {
    print_step "Checking system requirements"
    
    # Check system type
    if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        print_info "Detected Raspberry Pi - will apply Pi-specific optimizations"
    else
        print_info "Detected non-Pi system - using generic optimizations"
    fi
    
    # User detection (now dynamic)
    print_info "Installing for user: $STOSOS_USER"
    print_info "Home directory: $STOSOS_HOME"
    
    # Check for required commands
    for cmd in python3 pip3 git systemctl; do
        if ! command -v "$cmd" &> /dev/null; then
            print_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Check Python version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    python_check=$(python3 -c "import sys; print('OK' if sys.version_info >= (3, 8) else 'FAIL')")
    if [ "$python_check" != "OK" ]; then
        print_error "Python 3.8 or higher required. Found: $python_version"
        exit 1
    fi
    
    print_info "System requirements check passed"
}

install_system_dependencies() {
    print_step "Installing system dependencies"
    
    # Update package list
    sudo apt update
    
    # Install required system packages
    sudo apt install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        build-essential \
        bc \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        libtiff5-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        pkg-config \
        libgl1-mesa-dev \
        libgles2-mesa-dev \
        libegl1-mesa-dev \
        libdrm-dev \
        libxss1 \
        libgconf-2-4 \
        libxtst6 \
        libxrandr2 \
        libasound2-dev \
        libpulse-dev \
        libsndfile1-dev \
        portaudio19-dev \
        espeak \
        espeak-data \
        libespeak1 \
        libespeak-dev \
        festival \
        festvox-kallpc16k \
        sqlite3 \
        bc
        
    print_info "System dependencies installed"
}

setup_python_environment() {
    print_step "Setting up Python virtual environment"
    
    # Create virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_info "Created virtual environment at $VENV_DIR"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    if [ -f "$STOSOS_DIR/requirements.txt" ]; then
        pip install -r "$STOSOS_DIR/requirements.txt"
        print_info "Installed Python dependencies from requirements.txt"
    else
        # Install core dependencies manually
        pip install \
            kivy[base] \
            kivymd \
            requests \
            google-auth \
            google-auth-oauthlib \
            google-auth-httplib2 \
            google-api-python-client \
            spotipy \
            speechrecognition \
            pyttsx3 \
            pyaudio \
            psutil \
            schedule \
            python-dateutil \
            pillow
        print_info "Installed core Python dependencies"
    fi
}

setup_directories() {
    print_step "Setting up directories and permissions"
    
    # Create necessary directories
    mkdir -p "$STOSOS_DIR"/{data,logs,config,assets}
    
    # Set proper permissions
    chmod 755 "$STOSOS_DIR"
    chmod 755 "$STOSOS_DIR"/{data,logs,config,assets}
    
    # Create log file
    touch "$STOSOS_DIR/logs/stosos.log"
    chmod 644 "$STOSOS_DIR/logs/stosos.log"
    
    print_info "Directories created and permissions set"
}

setup_systemd_service() {
    print_step "Setting up systemd service"
    
    # Create user systemd directory
    mkdir -p "$STOSOS_HOME/.config/systemd/user"
    
    # Generate service file dynamically
    cat > "$STOSOS_HOME/.config/systemd/user/stosos.service" << EOF
[Unit]
Description=StosOS Desktop Environment
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=$STOSOS_USER
Group=$STOSOS_USER
WorkingDirectory=$STOSOS_DIR
Environment=DISPLAY=:0
Environment=PULSE_RUNTIME_PATH=/run/user/$(id -u)/pulse
ExecStart=$VENV_DIR/bin/python $STOSOS_DIR/main.py
ExecStop=/bin/kill -TERM \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=1G
CPUQuota=80%

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$STOSOS_DIR/data $STOSOS_DIR/logs $STOSOS_DIR/config

[Install]
WantedBy=graphical-session.target
EOF
    
    # Reload systemd and enable service
    systemctl --user daemon-reload
    systemctl --user enable stosos.service
    
    print_info "Systemd service generated and enabled"
}

setup_audio() {
    print_step "Configuring audio system"
    
    # Add user to audio group
    sudo usermod -a -G audio "$STOSOS_USER"
    
    # Configure PulseAudio for user session
    if [ ! -f "$STOSOS_HOME/.config/pulse/client.conf" ]; then
        mkdir -p "$STOSOS_HOME/.config/pulse"
        echo "autospawn = yes" > "$STOSOS_HOME/.config/pulse/client.conf"
        echo "daemon-binary = /usr/bin/pulseaudio" >> "$STOSOS_HOME/.config/pulse/client.conf"
    fi
    
    print_info "Audio system configured"
}

setup_display() {
    print_step "Configuring display settings"
    
    # Only configure Pi-specific settings on Raspberry Pi
    if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        print_info "Applying Raspberry Pi display optimizations"
        
        # Enable GPU memory split for better graphics performance
        if [ -f /boot/config.txt ] && ! grep -q "gpu_mem=128" /boot/config.txt; then
            echo "gpu_mem=128" | sudo tee -a /boot/config.txt
            print_info "GPU memory split configured"
        fi
        
        # Enable OpenGL driver
        if [ -f /boot/config.txt ] && ! grep -q "dtoverlay=vc4-kms-v3d" /boot/config.txt; then
            echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/config.txt
            print_info "OpenGL driver enabled"
        fi
    else
        print_info "Non-Pi system detected - skipping Pi-specific display configuration"
    fi
    
    print_info "Display settings configured"
}

create_desktop_entry() {
    print_step "Creating desktop entry"
    
    # Create desktop entry for manual launch
    cat > "$STOSOS_HOME/.local/share/applications/stosos.desktop" << EOF
[Desktop Entry]
Name=StosOS
Comment=StosOS Desktop Environment
Exec=$VENV_DIR/bin/python $STOSOS_DIR/main.py
Icon=$STOSOS_DIR/assets/stosos-icon.png
Terminal=false
Type=Application
Categories=System;
StartupNotify=true
EOF
    
    chmod +x "$STOSOS_HOME/.local/share/applications/stosos.desktop"
    print_info "Desktop entry created"
}

setup_autostart() {
    print_step "Setting up autostart"
    
    # Create autostart directory
    mkdir -p "$STOSOS_HOME/.config/autostart"
    
    # Create autostart entry
    cat > "$STOSOS_HOME/.config/autostart/stosos.desktop" << EOF
[Desktop Entry]
Type=Application
Name=StosOS
Exec=systemctl --user start stosos.service
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
    
    print_info "Autostart configured"
}

create_update_script() {
    print_step "Creating update script"
    
    cat > "$STOSOS_DIR/update.sh" << 'EOF'
#!/bin/bash

# StosOS Update Script

set -e

STOSOS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$STOSOS_DIR/venv"

echo "Updating StosOS..."

# Stop service if running
if systemctl --user is-active --quiet stosos; then
    echo "Stopping StosOS service..."
    systemctl --user stop stosos
    SERVICE_WAS_RUNNING=true
else
    SERVICE_WAS_RUNNING=false
fi

# Backup current installation
BACKUP_DIR="$HOME/stosos_backup_$(date +%Y%m%d_%H%M%S)"
echo "Creating backup at $BACKUP_DIR..."
cp -r "$STOSOS_DIR" "$BACKUP_DIR"

# Update from git if available
if [ -d "$STOSOS_DIR/.git" ]; then
    echo "Updating from git repository..."
    cd "$STOSOS_DIR"
    git pull origin main
else
    echo "No git repository found. Manual update required."
fi

# Update Python dependencies
echo "Updating Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade -r "$STOSOS_DIR/requirements.txt"

# Reload systemd configuration
echo "Reloading systemd configuration..."
systemctl --user daemon-reload

# Restart service if it was running
if [ "$SERVICE_WAS_RUNNING" = true ]; then
    echo "Restarting StosOS service..."
    systemctl --user start stosos
fi

echo "Update completed successfully!"
echo "Backup available at: $BACKUP_DIR"
EOF
    
    chmod +x "$STOSOS_DIR/update.sh"
    print_info "Update script created"
}

run_tests() {
    print_step "Running basic tests"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Test Python imports
    python3 -c "
import sys
sys.path.insert(0, '$STOSOS_DIR')
try:
    from core.config_manager import ConfigManager
    from core.logger import Logger
    from core.system_manager import SystemManager
    print('✓ Core modules import successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    # Test service file syntax
    systemctl --user --dry-run enable stosos.service
    
    print_info "Basic tests passed"
}

cleanup() {
    print_step "Cleaning up temporary files"
    
    # Remove any temporary files
    rm -f "$HOME"/stosos_*.tmp
    
    print_info "Cleanup completed"
}

print_completion_message() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 Installation Completed!                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo "StosOS has been successfully installed!"
    echo
    echo "Next steps:"
    echo "1. Reboot your Raspberry Pi to apply display settings"
    echo "2. StosOS will start automatically after reboot"
    echo "3. Configure API keys in: $STOSOS_DIR/config/stosos_config.json"
    echo
    echo "Manual control:"
    echo "  Start:   systemctl --user start stosos"
    echo "  Stop:    systemctl --user stop stosos"
    echo "  Status:  systemctl --user status stosos"
    echo "  Update:  $STOSOS_DIR/update.sh"
    echo
    echo "Logs: $STOSOS_DIR/logs/stosos.log"
    echo "Installation log: $LOG_FILE"
    echo
}

# Main installation flow
main() {
    print_header
    
    log "Starting StosOS installation"
    
    check_requirements
    install_system_dependencies
    setup_directories
    setup_python_environment
    setup_systemd_service
    setup_audio
    setup_display
    create_desktop_entry
    setup_autostart
    create_update_script
    run_tests
    cleanup
    
    print_completion_message
    
    log "Installation completed successfully"
}

# Run main function
main "$@"