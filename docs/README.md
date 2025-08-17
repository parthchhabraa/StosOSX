# StosOS Documentation

Welcome to the comprehensive documentation for StosOS, your personalized desktop environment for productivity, learning, and smart home control.

## Documentation Overview

This documentation suite provides everything you need to install, configure, and use StosOS effectively. Whether you're setting up StosOS for the first time or looking to master advanced features, you'll find the information you need here.

## Quick Start Guide

**New to StosOS?** Follow this sequence:

1. **[Installation Guide](INSTALLATION_GUIDE.md)** - Set up StosOS on your Raspberry Pi 4
2. **[API Configuration](API_CONFIGURATION.md)** - Connect to Google, Spotify, and other services
3. **[Voice Assistant Setup](VOICE_ASSISTANT_SETUP.md)** - Configure voice control features
4. **[User Manual](USER_MANUAL.md)** - Learn to use all StosOS features

**Having Issues?** Check the **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)**

## Documentation Structure

### 📋 Setup and Configuration

#### [Installation Guide](INSTALLATION_GUIDE.md)
Complete step-by-step instructions for installing StosOS on Raspberry Pi 4 with 7-inch touchscreen.

**Contents:**
- Hardware requirements and compatibility
- Raspberry Pi OS preparation
- StosOS installation process
- System service configuration
- Initial setup and testing
- Post-installation optimization

**Who should read this:** First-time users, system administrators

#### [API Configuration Guide](API_CONFIGURATION.md)
Detailed instructions for obtaining and configuring API keys for all integrated services.

**Contents:**
- Google Calendar API setup
- Google Assistant SDK configuration
- Spotify Web API integration
- OpenAI API configuration (optional)
- Alexa Voice Service setup (optional)
- Security best practices
- Authentication troubleshooting

**Who should read this:** Users setting up external service integrations

#### [Voice Assistant Setup](VOICE_ASSISTANT_SETUP.md)
Comprehensive guide for configuring the AI-powered voice assistant.

**Contents:**
- Audio hardware configuration
- Wake word training and customization
- Voice command configuration
- AI integration (OpenAI/Ollama)
- Performance optimization
- Privacy and security settings

**Who should read this:** Users wanting voice control functionality

### 📖 Usage and Features

#### [User Manual](USER_MANUAL.md)
Complete reference for all StosOS features and functionality.

**Contents:**
- Interface navigation and basics
- Module-by-module feature guides
- Voice command reference
- Keyboard shortcuts
- Customization options
- Tips and best practices

**Who should read this:** All users, from beginners to advanced

### 🔧 Troubleshooting and Support

#### [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
Solutions for common hardware and software issues.

**Contents:**
- Installation and startup problems
- Display and touch issues
- Audio and microphone problems
- Network and API connectivity
- Performance optimization
- Hardware-specific issues
- Log analysis and debugging

**Who should read this:** Users experiencing issues, system administrators

## Feature Documentation Quick Reference

### Core Modules

| Module | Description | Key Features |
|--------|-------------|--------------|
| **Dashboard** | Central hub and navigation | Module tiles, status indicators, quick actions |
| **Calendar** | Google Calendar integration | Event management, multiple views, sync |
| **Task Manager** | To-do list and project tracking | Priorities, categories, analytics |
| **Idea Board** | Quick note capture and organization | Tags, search, export options |
| **Study Tracker** | Learning analytics and Pomodoro timer | Time tracking, goals, motivation |
| **Smart Home** | Device control and automation | Google/Alexa integration, scenes |
| **Spotify Controller** | Music playback and library | Device selection, voice control |
| **Voice Assistant** | AI-powered natural language control | Wake words, context awareness |

### System Features

| Feature | Description | Documentation Section |
|---------|-------------|----------------------|
| **Power Management** | Display dimming and sleep modes | [User Manual - Power Management](USER_MANUAL.md#power-management) |
| **Touch Interface** | Optimized for 7-inch touchscreen | [User Manual - Navigation](USER_MANUAL.md#navigation-basics) |
| **Voice Control** | Hands-free operation | [Voice Assistant Setup](VOICE_ASSISTANT_SETUP.md) |
| **API Integration** | External service connections | [API Configuration](API_CONFIGURATION.md) |
| **Theme System** | Dark/light themes and customization | [User Manual - Settings](USER_MANUAL.md#system-settings) |

## Common Use Cases

### For Students (IIT-JEE Preparation)

**Recommended Reading Order:**
1. [Installation Guide](INSTALLATION_GUIDE.md) - Basic setup
2. [API Configuration](API_CONFIGURATION.md) - Google Calendar integration
3. [User Manual - Study Tracker](USER_MANUAL.md#study-tracker) - Learning analytics
4. [User Manual - Task Manager](USER_MANUAL.md#task-manager) - Assignment tracking
5. [Voice Assistant Setup](VOICE_ASSISTANT_SETUP.md) - Hands-free study assistance

**Key Features:**
- Pomodoro timer for focused study sessions
- Calendar integration for exam schedules
- Task management for assignments and deadlines
- Idea board for quick note-taking
- Voice assistant for hands-free operation

### For Smart Home Enthusiasts

**Recommended Reading Order:**
1. [Installation Guide](INSTALLATION_GUIDE.md) - System setup
2. [API Configuration](API_CONFIGURATION.md) - Google/Alexa integration
3. [User Manual - Smart Home](USER_MANUAL.md#smart-home-control) - Device control
4. [Voice Assistant Setup](VOICE_ASSISTANT_SETUP.md) - Voice commands

**Key Features:**
- Unified device control interface
- Scene management and automation
- Voice-activated device control
- Real-time status monitoring

### For Productivity Users

**Recommended Reading Order:**
1. [Installation Guide](INSTALLATION_GUIDE.md) - Basic setup
2. [API Configuration](API_CONFIGURATION.md) - Service integrations
3. [User Manual - Calendar](USER_MANUAL.md#calendar-module) - Schedule management
4. [User Manual - Task Manager](USER_MANUAL.md#task-manager) - Project tracking
5. [User Manual - Idea Board](USER_MANUAL.md#idea-board) - Note organization

**Key Features:**
- Integrated calendar and task management
- Quick idea capture and organization
- Cross-module search and filtering
- Analytics and progress tracking

## Technical Specifications

### System Requirements

- **Hardware:** Raspberry Pi 4 (4GB+ RAM recommended)
- **Display:** 7-inch DSI touchscreen (800x480 minimum)
- **Storage:** 32GB+ microSD card (Class 10 or better)
- **Network:** WiFi or Ethernet connection
- **Audio:** USB microphone and speakers (optional)

### Software Dependencies

- **Operating System:** Raspberry Pi OS (Bullseye or newer)
- **Python:** 3.9+ with pip and venv
- **Framework:** Kivy for UI, SQLite for data storage
- **Services:** systemd for auto-start, ALSA/PulseAudio for audio

### API Integrations

- **Google Calendar API:** Event synchronization
- **Google Assistant SDK:** Smart home control
- **Spotify Web API:** Music playback control
- **OpenAI API:** Advanced AI capabilities (optional)
- **Alexa Voice Service:** Amazon device control (optional)

## Getting Help and Support

### Self-Help Resources

1. **Check the Troubleshooting Guide** - Most common issues are covered
2. **Review Log Files** - Located in `/home/pi/stosos/logs/`
3. **Test Individual Components** - Use provided test scripts
4. **Verify Configuration** - Check JSON syntax and API credentials

### Community Support

- **GitHub Repository:** Report bugs and request features
- **Documentation Updates:** Contribute improvements and corrections
- **Community Forum:** Share tips and ask questions
- **Example Configurations:** Find working setups for your use case

### Reporting Issues

When reporting issues, please include:

1. **System Information:**
   ```bash
   uname -a
   cat /etc/os-release
   python3 --version
   ```

2. **StosOS Version:**
   ```bash
   cd /home/pi/stosos
   git log --oneline -1
   ```

3. **Relevant Logs:**
   ```bash
   tail -50 /home/pi/stosos/logs/stosos.log
   journalctl -u stosos.service --since "1 hour ago"
   ```

4. **Configuration Details:**
   - Hardware setup (Pi model, display, peripherals)
   - Enabled modules and API integrations
   - Any custom configuration changes

## Documentation Maintenance

This documentation is actively maintained and updated. Version information:

- **Last Updated:** [Current Date]
- **StosOS Version:** Compatible with v1.0+
- **Documentation Version:** 1.0

### Contributing to Documentation

We welcome contributions to improve this documentation:

1. **Corrections:** Fix typos, errors, or outdated information
2. **Additions:** Add missing information or new use cases
3. **Examples:** Provide configuration examples and screenshots
4. **Translations:** Help translate documentation to other languages

---

## Quick Navigation

**🚀 Getting Started:**
- [Installation Guide](INSTALLATION_GUIDE.md)
- [API Configuration](API_CONFIGURATION.md)
- [Voice Assistant Setup](VOICE_ASSISTANT_SETUP.md)

**📚 Learning StosOS:**
- [User Manual](USER_MANUAL.md)
- [Feature Overview](#feature-documentation-quick-reference)
- [Common Use Cases](#common-use-cases)

**🔧 Need Help:**
- [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- [Getting Support](#getting-help-and-support)
- [Technical Specifications](#technical-specifications)

---

**Welcome to StosOS!** We hope this documentation helps you get the most out of your personalized desktop environment. If you have questions or suggestions, don't hesitate to reach out to the community.