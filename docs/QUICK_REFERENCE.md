# StosOS Quick Reference Card

## Essential Voice Commands

### System Navigation
```
"Stos, open calendar"
"Stos, show my tasks"
"Stos, go to dashboard"
"Stos, open settings"
```

### Task Management
```
"Stos, add task: Study physics chapter 5"
"Stos, what are my tasks for today?"
"Stos, mark task as complete"
"Stos, show high priority tasks"
```

### Calendar Control
```
"Stos, what's my next meeting?"
"Stos, add event: Math exam tomorrow at 10 AM"
"Stos, show today's schedule"
```

### Smart Home Control
```
"Stos, turn on the lights"
"Stos, set temperature to 22 degrees"
"Stos, activate study mode"
```

### Music Control
```
"Stos, play some jazz music"
"Stos, skip this song"
"Stos, play my study playlist"
"Stos, turn up the volume"
```

## Common Troubleshooting

### StosOS Won't Start
```bash
# Check service status
sudo systemctl status stosos.service

# View logs
tail -f /home/pi/stosos/logs/stosos.log

# Manual start for debugging
cd /home/pi/stosos && python main.py
```

### Touch Not Working
```bash
# Check touch device
cat /proc/bus/input/devices | grep -i touch

# Calibrate touchscreen
xinput_calibrator
```

### Audio Issues
```bash
# Test microphone
arecord -d 5 test.wav && aplay test.wav

# Test speakers
speaker-test -t wav -c 2

# Check audio mixer
alsamixer
```

### API Connection Problems
```bash
# Test internet
ping google.com

# Check API credentials
python -m json.tool /home/pi/stosos/config/stosos_config.json

# Reset API tokens
rm -rf /home/pi/stosos/config/tokens/*
```

## File Locations

### Configuration
- Main config: `/home/pi/stosos/config/stosos_config.json`
- API credentials: `/home/pi/stosos/config/*.json`
- Service file: `/etc/systemd/system/stosos.service`

### Logs
- Main log: `/home/pi/stosos/logs/stosos.log`
- System log: `journalctl -u stosos.service`

### Data
- Database: `/home/pi/stosos/data/stosos.db`
- User data: `/home/pi/stosos/data/`

## System Commands

### Service Management
```bash
# Start/stop/restart StosOS
sudo systemctl start stosos.service
sudo systemctl stop stosos.service
sudo systemctl restart stosos.service

# Enable/disable auto-start
sudo systemctl enable stosos.service
sudo systemctl disable stosos.service
```

### System Monitoring
```bash
# Check system resources
htop
free -h
df -h

# Monitor temperature
vcgencmd measure_temp

# Check GPU memory
vcgencmd get_mem gpu
```

### Audio Configuration
```bash
# List audio devices
arecord -l  # Input devices
aplay -l    # Output devices

# Audio mixer
alsamixer

# PulseAudio control
pactl list short sinks
pactl list short sources
```

## Emergency Recovery

### Safe Mode Boot
1. Edit `/boot/cmdline.txt`
2. Add: `systemd.unit=multi-user.target`
3. Reboot to console mode
4. Disable StosOS: `sudo systemctl disable stosos.service`

### Factory Reset
```bash
# Backup data
cp -r /home/pi/stosos/data /home/pi/stosos_backup

# Reset configuration
cd /home/pi/stosos
git checkout -- config/stosos_config.json
rm -rf config/tokens/*
rm -rf data/stosos.db

# Reinstall
./install.sh --force-reinstall
```

## Performance Optimization

### Memory Management
```bash
# Clear system caches
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Increase swap
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup && sudo dphys-swapfile swapon
```

### Display Optimization
```bash
# Increase GPU memory
sudo raspi-config
# Advanced Options > Memory Split > 128

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

## Keyboard Shortcuts

### Global
- `Ctrl + H`: Dashboard
- `Ctrl + 1-6`: Switch modules
- `Ctrl + S`: Settings
- `F11`: Fullscreen
- `Ctrl + Space`: Voice assistant

### Module Specific
- `N`: New item (task/event/idea)
- `Space`: Complete/toggle
- `Del`: Delete selected
- `F`: Filter/search
- `Esc`: Cancel/back

---

**Need More Help?** Check the [Complete Documentation](README.md) or [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)