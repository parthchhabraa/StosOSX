# StosOS Troubleshooting Guide

## Overview

This guide provides solutions for common hardware and software issues you may encounter while using StosOS. Issues are organized by category with step-by-step resolution procedures.

## Quick Diagnostic Commands

### System Health Check
```bash
# Run comprehensive system check
cd /home/pi/stosos
python system_diagnostics.py

# Check service status
sudo systemctl status stosos.service

# View recent logs
tail -n 50 /home/pi/stosos/logs/stosos.log

# Check system resources
htop
df -h
free -h
```

## Installation and Startup Issues

### StosOS Won't Start

**Symptoms:**
- Black screen after boot
- Service fails to start
- Python errors during startup

**Solutions:**

1. **Check Service Status**
   ```bash
   sudo systemctl status stosos.service
   journalctl -u stosos.service --no-pager -n 50
   ```

2. **Verify Installation**
   ```bash
   cd /home/pi/stosos
   ls -la main.py
   source venv/bin/activate
   python --version
   pip list | grep kivy
   ```

3. **Manual Start Test**
   ```bash
   cd /home/pi/stosos
   source venv/bin/activate
   python main.py
   ```

4. **Fix Common Issues**
   ```bash
   # Fix permissions
   sudo chown -R pi:pi /home/pi/stosos
   chmod +x /home/pi/stosos/main.py
   
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   
   # Reset configuration
   cp config/stosos_config.json.backup config/stosos_config.json
   ```

### Installation Script Fails

**Symptoms:**
- Script exits with errors
- Missing dependencies
- Permission denied errors

**Solutions:**

1. **Update System First**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv git
   ```

2. **Manual Installation**
   ```bash
   cd /home/pi/stosos
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Fix Permission Issues**
   ```bash
   sudo chown -R pi:pi /home/pi/stosos
   chmod +x install.sh setup_env.sh
   ```

## Display and Touch Issues

### Touchscreen Not Responding

**Symptoms:**
- Touch input not detected
- Inaccurate touch coordinates
- Intermittent touch response

**Solutions:**

1. **Check Touch Device Detection**
   ```bash
   # List input devices
   cat /proc/bus/input/devices | grep -A 5 -B 5 -i touch
   
   # Test touch events
   sudo apt install evtest
   sudo evtest
   # Select touch device and test touch input
   ```

2. **Calibrate Touchscreen**
   ```bash
   sudo apt install xinput-calibrator
   xinput_calibrator
   
   # Follow on-screen instructions
   # Copy calibration data to /etc/X11/xorg.conf.d/99-calibration.conf
   ```

3. **Check Display Configuration**
   ```bash
   # Verify display settings in /boot/config.txt
   grep -E "(dtoverlay|display)" /boot/config.txt
   
   # Common touchscreen overlays:
   # dtoverlay=vc4-kms-v3d
   # dtoverlay=vc4-fkms-v3d
   ```

4. **Restart Display Service**
   ```bash
   sudo systemctl restart lightdm
   # Or reboot if necessary
   sudo reboot
   ```

### Display Issues

**Symptoms:**
- Blank screen
- Wrong orientation
- Poor image quality
- Flickering display

**Solutions:**

1. **Check Display Connection**
   ```bash
   # Verify display detection
   tvservice -l
   vcgencmd display_power
   
   # Test HDMI output
   tvservice -s
   ```

2. **Fix Display Orientation**
   ```bash
   # Edit boot configuration
   sudo nano /boot/config.txt
   
   # Add rotation setting:
   display_rotate=0  # Normal
   display_rotate=1  # 90 degrees
   display_rotate=2  # 180 degrees
   display_rotate=3  # 270 degrees
   ```

3. **Adjust Display Settings**
   ```bash
   # Increase GPU memory
   sudo raspi-config
   # Advanced Options > Memory Split > 128
   
   # Force specific resolution
   echo "hdmi_force_hotplug=1" | sudo tee -a /boot/config.txt
   echo "hdmi_group=2" | sudo tee -a /boot/config.txt
   echo "hdmi_mode=87" | sudo tee -a /boot/config.txt
   ```

### Brightness Control Not Working

**Symptoms:**
- Cannot adjust brightness
- Brightness stuck at maximum
- Power management not working

**Solutions:**

1. **Check Backlight Control**
   ```bash
   # List backlight devices
   ls /sys/class/backlight/
   
   # Test brightness control
   echo 128 | sudo tee /sys/class/backlight/rpi_backlight/brightness
   
   # Check current brightness
   cat /sys/class/backlight/rpi_backlight/brightness
   ```

2. **Fix Permissions**
   ```bash
   # Add user to video group
   sudo usermod -a -G video pi
   
   # Create udev rule for brightness control
   sudo nano /etc/udev/rules.d/99-backlight.rules
   ```
   
   Add:
   ```
   SUBSYSTEM=="backlight", KERNEL=="rpi_backlight", RUN+="/bin/chmod 666 /sys/class/backlight/rpi_backlight/brightness"
   ```

3. **Restart Services**
   ```bash
   sudo udevadm control --reload-rules
   sudo systemctl restart stosos.service
   ```

## Audio Issues

### Microphone Not Working

**Symptoms:**
- No audio input detected
- Poor audio quality
- Voice assistant not responding

**Solutions:**

1. **Check Audio Devices**
   ```bash
   # List audio input devices
   arecord -l
   
   # Test microphone recording
   arecord -d 5 -f cd test.wav
   aplay test.wav
   
   # Check USB devices
   lsusb | grep -i audio
   ```

2. **Configure Audio Input**
   ```bash
   # Install audio tools
   sudo apt install alsa-utils pulseaudio
   
   # Open audio mixer
   alsamixer
   # Press F4 for capture devices
   # Increase microphone level to 70-80%
   ```

3. **Fix Audio Permissions**
   ```bash
   # Add user to audio group
   sudo usermod -a -G audio pi
   
   # Restart audio service
   sudo systemctl restart alsa-state
   pulseaudio --kill && pulseaudio --start
   ```

### Speaker/Audio Output Issues

**Symptoms:**
- No sound output
- Distorted audio
- Wrong audio device selected

**Solutions:**

1. **Check Audio Output**
   ```bash
   # List audio output devices
   aplay -l
   
   # Test speaker output
   speaker-test -t wav -c 2
   
   # Check volume levels
   alsamixer
   ```

2. **Configure Audio Output**
   ```bash
   # Force audio to 3.5mm jack
   sudo raspi-config
   # Advanced Options > Audio > Force 3.5mm jack
   
   # Or force HDMI audio
   # Advanced Options > Audio > Force HDMI
   ```

3. **Fix Audio Routing**
   ```bash
   # Check PulseAudio status
   pulseaudio --check -v
   
   # List audio sinks
   pactl list short sinks
   
   # Set default sink
   pactl set-default-sink alsa_output.platform-bcm2835_audio.analog-stereo
   ```

## Network and API Issues

### Internet Connection Problems

**Symptoms:**
- API services not working
- Cannot sync calendar
- Voice assistant offline

**Solutions:**

1. **Check Network Connection**
   ```bash
   # Test internet connectivity
   ping -c 4 google.com
   
   # Check WiFi status
   iwconfig wlan0
   
   # View network configuration
   ip addr show
   ```

2. **Fix WiFi Issues**
   ```bash
   # Restart network service
   sudo systemctl restart networking
   
   # Reconfigure WiFi
   sudo raspi-config
   # Network Options > Wi-fi
   
   # Manual WiFi configuration
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   ```

3. **DNS Issues**
   ```bash
   # Test DNS resolution
   nslookup google.com
   
   # Use different DNS servers
   echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
   echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
   ```

### API Authentication Failures

**Symptoms:**
- "Authentication failed" errors
- Services showing as disconnected
- Token expired messages

**Solutions:**

1. **Check API Credentials**
   ```bash
   # Verify configuration file
   python -m json.tool /home/pi/stosos/config/stosos_config.json
   
   # Check credential files exist
   ls -la /home/pi/stosos/config/*.json
   ```

2. **Refresh API Tokens**
   ```bash
   # Delete existing tokens
   rm -rf /home/pi/stosos/config/tokens/*
   
   # Restart StosOS to re-authenticate
   sudo systemctl restart stosos.service
   ```

3. **Test API Connections**
   ```bash
   cd /home/pi/stosos
   source venv/bin/activate
   
   # Test Google Calendar
   python -c "from services.google_calendar_service import GoogleCalendarService; print('Calendar OK')"
   
   # Test Spotify
   python -c "from services.spotify_service import SpotifyService; print('Spotify OK')"
   ```

## Performance Issues

### System Running Slowly

**Symptoms:**
- Laggy interface
- Slow module switching
- High CPU/memory usage

**Solutions:**

1. **Check System Resources**
   ```bash
   # Monitor system performance
   htop
   
   # Check memory usage
   free -h
   
   # Check disk space
   df -h
   
   # Monitor GPU memory
   vcgencmd get_mem gpu
   ```

2. **Optimize Performance**
   ```bash
   # Increase GPU memory split
   sudo raspi-config
   # Advanced Options > Memory Split > 128
   
   # Disable unnecessary services
   sudo systemctl disable bluetooth
   sudo systemctl disable cups
   
   # Clean up system
   sudo apt autoremove
   sudo apt autoclean
   ```

3. **StosOS Performance Tuning**
   ```json
   // Edit config/stosos_config.json
   {
     "performance": {
       "animation_quality": "medium",
       "cache_size": 50,
       "lazy_loading": true,
       "background_sync": false
     }
   }
   ```

### Memory Issues

**Symptoms:**
- Out of memory errors
- System freezing
- Modules crashing

**Solutions:**

1. **Monitor Memory Usage**
   ```bash
   # Check memory by process
   ps aux --sort=-%mem | head -10
   
   # Monitor StosOS memory usage
   pgrep -f stosos | xargs ps -o pid,ppid,cmd,%mem,%cpu
   ```

2. **Increase Swap Space**
   ```bash
   # Check current swap
   swapon --show
   
   # Increase swap size
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Change CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

3. **Memory Optimization**
   ```bash
   # Clear system caches
   sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
   
   # Restart StosOS
   sudo systemctl restart stosos.service
   ```

## Module-Specific Issues

### Calendar Module Problems

**Symptoms:**
- Events not syncing
- Cannot create events
- Calendar shows as offline

**Solutions:**

1. **Check Google Calendar API**
   ```bash
   # Test API connection
   cd /home/pi/stosos
   python test_calendar_simple.py
   
   # Check credentials
   ls -la config/google_calendar_credentials.json
   ```

2. **Re-authenticate Google Calendar**
   ```bash
   # Remove existing tokens
   rm -f config/tokens/calendar_token.json
   
   # Restart StosOS to re-authenticate
   sudo systemctl restart stosos.service
   ```

### Task Manager Issues

**Symptoms:**
- Tasks not saving
- Database errors
- Task list not loading

**Solutions:**

1. **Check Database**
   ```bash
   # Test database connection
   cd /home/pi/stosos
   python test_database_simple.py
   
   # Check database file
   ls -la data/stosos.db
   sqlite3 data/stosos.db ".tables"
   ```

2. **Reset Database**
   ```bash
   # Backup existing data
   cp data/stosos.db data/stosos.db.backup
   
   # Recreate database
   python -c "from core.database_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
   ```

### Smart Home Module Issues

**Symptoms:**
- Devices not discovered
- Cannot control devices
- Connection timeouts

**Solutions:**

1. **Check Device Discovery**
   ```bash
   # Test Google Assistant connection
   cd /home/pi/stosos
   python test_smart_home_simple.py
   
   # Check network connectivity to devices
   ping your-smart-device-ip
   ```

2. **Re-authenticate Smart Home Services**
   ```bash
   # Remove tokens
   rm -f config/tokens/google_assistant_token.json
   rm -f config/tokens/alexa_token.json
   
   # Restart service
   sudo systemctl restart stosos.service
   ```

## Hardware-Specific Issues

### Raspberry Pi 4 Overheating

**Symptoms:**
- System throttling
- Performance degradation
- Thermal warnings

**Solutions:**

1. **Monitor Temperature**
   ```bash
   # Check CPU temperature
   vcgencmd measure_temp
   
   # Monitor thermal throttling
   vcgencmd get_throttled
   
   # Continuous monitoring
   watch -n 1 vcgencmd measure_temp
   ```

2. **Cooling Solutions**
   ```bash
   # Check for thermal throttling
   dmesg | grep -i thermal
   
   # Reduce CPU frequency if needed
   echo "arm_freq=1200" | sudo tee -a /boot/config.txt
   
   # Enable fan control (if fan installed)
   echo "dtoverlay=gpio-fan,gpiopin=14,temp=65000" | sudo tee -a /boot/config.txt
   ```

### Power Supply Issues

**Symptoms:**
- Random reboots
- USB devices disconnecting
- Under-voltage warnings

**Solutions:**

1. **Check Power Supply**
   ```bash
   # Monitor power status
   vcgencmd get_throttled
   
   # Check for under-voltage
   dmesg | grep -i voltage
   
   # View power supply info
   cat /sys/devices/platform/rpi_hwmon/hwmon/hwmon*/in0_lcrit_alarm
   ```

2. **Power Optimization**
   ```bash
   # Disable unnecessary features
   echo "dtoverlay=disable-wifi" | sudo tee -a /boot/config.txt
   echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
   
   # Reduce GPU memory if not needed
   echo "gpu_mem=64" | sudo tee -a /boot/config.txt
   ```

## Log Analysis and Debugging

### StosOS Logs

**Log Locations:**
- Main log: `/home/pi/stosos/logs/stosos.log`
- System log: `journalctl -u stosos.service`
- Module logs: `/home/pi/stosos/logs/modules/`

**Common Log Analysis:**
```bash
# View recent errors
grep -i error /home/pi/stosos/logs/stosos.log | tail -20

# Monitor live logs
tail -f /home/pi/stosos/logs/stosos.log

# Search for specific issues
grep -i "authentication\|connection\|timeout" /home/pi/stosos/logs/stosos.log
```

### System Logs

```bash
# View system messages
dmesg | tail -50

# Check service logs
journalctl -u stosos.service --since "1 hour ago"

# Monitor system logs
journalctl -f
```

### Debug Mode

Enable debug mode for detailed logging:

```json
{
  "system": {
    "debug_mode": true,
    "log_level": "DEBUG",
    "verbose_logging": true
  }
}
```

## Recovery Procedures

### Safe Mode Boot

1. **Boot to Console**
   ```bash
   # Edit boot parameters
   sudo nano /boot/cmdline.txt
   # Add: systemd.unit=multi-user.target
   ```

2. **Disable StosOS Auto-start**
   ```bash
   sudo systemctl disable stosos.service
   ```

3. **Manual Troubleshooting**
   ```bash
   cd /home/pi/stosos
   source venv/bin/activate
   python main.py --debug
   ```

### Factory Reset

1. **Backup Important Data**
   ```bash
   cp -r /home/pi/stosos/data /home/pi/stosos_backup
   cp /home/pi/stosos/config/stosos_config.json /home/pi/stosos_backup/
   ```

2. **Reset Configuration**
   ```bash
   cd /home/pi/stosos
   git checkout -- config/stosos_config.json
   rm -rf config/tokens/*
   rm -rf data/stosos.db
   ```

3. **Reinstall StosOS**
   ```bash
   ./install.sh --force-reinstall
   ```

## Getting Additional Help

### Diagnostic Information Collection

Before seeking help, collect this information:

```bash
# System information
uname -a
cat /etc/os-release
vcgencmd version

# Hardware information
lscpu
lsusb
lsblk

# StosOS information
cd /home/pi/stosos
git log --oneline -5
pip list | grep -E "(kivy|pygame|requests)"

# Recent logs
tail -50 /home/pi/stosos/logs/stosos.log > stosos_debug.log
journalctl -u stosos.service --since "1 hour ago" > system_debug.log
```

### Support Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check latest documentation updates
- **Community Forum**: Ask questions and share solutions
- **Log Analysis**: Include relevant log excerpts when reporting issues

---

**Remember**: Most issues can be resolved by checking logs, verifying configuration, and ensuring all dependencies are properly installed. When in doubt, try restarting the StosOS service or rebooting the system.