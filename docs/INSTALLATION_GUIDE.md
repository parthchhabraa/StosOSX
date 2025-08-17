# StosOS Installation Guide

## Overview

This guide will walk you through setting up StosOS on a Raspberry Pi 4 with a 7-inch DSI touchscreen. StosOS is designed to provide a comprehensive productivity and smart home control interface optimized for students and tech enthusiasts.

## Hardware Requirements

### Required Hardware
- **Raspberry Pi 4** (4GB RAM minimum, 8GB recommended)
- **7-inch DSI Touchscreen** (Official Raspberry Pi touchscreen or compatible)
- **MicroSD Card** (32GB minimum, Class 10 or better)
- **Power Supply** (Official Raspberry Pi 4 power supply recommended)
- **Micro HDMI Cable** (for initial setup if needed)

### Optional Hardware
- **USB Microphone** (for voice assistant functionality)
- **Speakers or 3.5mm Audio Output** (for audio feedback)
- **Case** (with touchscreen access and ventilation)

## Software Prerequisites

### Base System
- **Raspberry Pi OS** (Bullseye or newer, Desktop version recommended)
- **Python 3.9+** (included with Raspberry Pi OS)
- **Git** (for downloading StosOS)

## Step-by-Step Installation

### 1. Prepare Raspberry Pi OS

1. **Flash Raspberry Pi OS to SD Card**
   ```bash
   # Use Raspberry Pi Imager or flash manually
   # Enable SSH and WiFi during imaging if needed
   ```

2. **Boot and Initial Setup**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Install required system packages
   sudo apt install -y python3-pip python3-venv git curl
   ```

3. **Configure Touchscreen (if not auto-detected)**
   ```bash
   # Add to /boot/config.txt if needed
   echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/config.txt
   echo "dtoverlay=vc4-fkms-v3d" | sudo tee -a /boot/config.txt
   
   # Reboot to apply changes
   sudo reboot
   ```

### 2. Download and Install StosOS

1. **Clone StosOS Repository**
   ```bash
   cd /home/pi
   git clone https://github.com/parthchhabraa/stosos.git
   cd stosos
   ```

2. **Run Installation Script**
   ```bash
   # Make installation script executable
   chmod +x install.sh
   
   # Run installation (this will take 10-15 minutes)
   ./install.sh
   ```

3. **Verify Installation**
   ```bash
   # Check if virtual environment was created
   ls -la venv/
   
   # Test basic functionality
   source venv/bin/activate
   python -c "import kivy; print('Kivy installed successfully')"
   ```

### 3. Configure System Services

1. **Enable StosOS Auto-Start**
   ```bash
   # Copy service file
   sudo cp stosos.service /etc/systemd/system/
   
   # Enable service
   sudo systemctl enable stosos.service
   sudo systemctl daemon-reload
   ```

2. **Configure Display Settings**
   ```bash
   # Set display orientation (if needed)
   echo "display_rotate=2" | sudo tee -a /boot/config.txt
   
   # Configure touch calibration
   sudo apt install -y xinput-calibrator
   ```

### 4. Initial Configuration

1. **Run Setup Script**
   ```bash
   cd /home/pi/stosos
   source venv/bin/activate
   python setup_env.sh
   ```

2. **Configure Basic Settings**
   - Edit `config/stosos_config.json` with your preferences
   - Set timezone and locale settings
   - Configure network settings if needed

### 5. Test Installation

1. **Manual Test Run**
   ```bash
   cd /home/pi/stosos
   source venv/bin/activate
   python main.py
   ```

2. **Service Test**
   ```bash
   # Start service
   sudo systemctl start stosos.service
   
   # Check status
   sudo systemctl status stosos.service
   
   # View logs
   journalctl -u stosos.service -f
   ```

## Post-Installation Setup

### Display Configuration

1. **Screen Brightness**
   ```bash
   # Test brightness control
   echo 128 | sudo tee /sys/class/backlight/rpi_backlight/brightness
   ```

2. **Touch Calibration**
   ```bash
   # Run calibration if touch is inaccurate
   xinput_calibrator
   ```

### Audio Configuration

1. **Set Audio Output**
   ```bash
   # List audio devices
   aplay -l
   
   # Set default output (adjust card number as needed)
   sudo raspi-config
   # Navigate to Advanced Options > Audio > Force 3.5mm jack
   ```

2. **Test Audio**
   ```bash
   # Test speaker output
   speaker-test -t wav -c 2
   
   # Test microphone (if connected)
   arecord -d 5 test.wav && aplay test.wav
   ```

## Troubleshooting Installation Issues

### Common Issues

1. **Installation Script Fails**
   ```bash
   # Check Python version
   python3 --version
   
   # Ensure pip is updated
   python3 -m pip install --upgrade pip
   
   # Manual dependency installation
   pip3 install -r requirements.txt
   ```

2. **Touchscreen Not Working**
   ```bash
   # Check if touchscreen is detected
   dmesg | grep -i touch
   
   # Verify input devices
   cat /proc/bus/input/devices
   
   # Test touch events
   evtest
   ```

3. **Service Won't Start**
   ```bash
   # Check service logs
   journalctl -u stosos.service --no-pager
   
   # Verify file permissions
   ls -la /home/pi/stosos/main.py
   
   # Test manual start
   cd /home/pi/stosos && python main.py
   ```

4. **Performance Issues**
   ```bash
   # Check system resources
   htop
   
   # Monitor GPU memory
   vcgencmd get_mem gpu
   
   # Increase GPU memory split if needed
   sudo raspi-config
   # Advanced Options > Memory Split > 128
   ```

### Getting Help

- **Log Files**: Check `/home/pi/stosos/logs/stosos.log` for detailed error messages
- **System Logs**: Use `journalctl -u stosos.service` for service-related issues
- **Hardware Tests**: Run individual test scripts in the `stosos/` directory
- **Community Support**: Visit the StosOS GitHub repository for issues and discussions

## Next Steps

After successful installation:

1. **Configure API Keys** - See `API_CONFIGURATION.md`
2. **Set Up Voice Assistant** - See `VOICE_ASSISTANT_SETUP.md`
3. **Configure Smart Home** - See `USER_MANUAL.md`
4. **Customize Interface** - Edit configuration files as needed

## Security Considerations

- Change default passwords for any services
- Configure firewall if network access is enabled
- Keep system packages updated regularly
- Secure API keys and configuration files

---

**Installation Complete!** StosOS should now start automatically when your Raspberry Pi boots up.
