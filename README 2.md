# StosOS Desktop Environment

A custom desktop environment for Raspberry Pi 4 designed for productivity, smart home control, and AI assistance.

## Project Structure

```
stosos/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── setup_env.sh           # Environment setup script
├── README.md              # This file
├── core/                  # Core framework components
│   ├── __init__.py
│   ├── config_manager.py  # Configuration management
│   ├── base_module.py     # Base class for modules
│   └── logger.py          # Logging configuration
├── modules/               # Feature modules
│   └── __init__.py
├── services/              # External service integrations
│   └── __init__.py
├── assets/                # Images, sounds, fonts
├── config/                # Configuration files
├── logs/                  # Application logs
└── data/                  # SQLite database and user data
```

## Documentation

**📚 Complete Documentation Available in [`docs/`](docs/README.md)**

### Quick Start Guides
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Complete setup instructions for Raspberry Pi 4
- **[API Configuration](docs/API_CONFIGURATION.md)** - Configure Google Calendar, Spotify, and other services
- **[Voice Assistant Setup](docs/VOICE_ASSISTANT_SETUP.md)** - Set up AI-powered voice control
- **[User Manual](docs/USER_MANUAL.md)** - Complete feature reference and usage guide
- **[Troubleshooting Guide](docs/TROUBLESHOOTING_GUIDE.md)** - Solutions for common issues

### Quick Setup (Development)

For development and testing:

```bash
# 1. Clone and setup environment
cd stosos
chmod +x setup_env.sh
./setup_env.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run StosOS
python main.py
```

**For production installation, use the [Installation Guide](docs/INSTALLATION_GUIDE.md)**

## Development

### Adding New Modules

1. Create a new module class inheriting from `BaseModule`
2. Implement required abstract methods
3. Register the module in the main application

### Configuration

Configuration is managed through `core/config_manager.py`. Settings are stored in `config/stosos_config.json`.

### Logging

Logs are written to `logs/stosos.log` with rotation. Console output shows important messages.

## Requirements

- Python 3.8+
- Kivy framework
- SQLite3
- Various API libraries (see requirements.txt)

## Hardware Requirements

- Raspberry Pi 4
- 7-inch DSI touchscreen
- Microphone and speakers
- WiFi connection