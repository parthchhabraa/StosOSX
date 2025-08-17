# StosOS API Configuration Guide

## Overview

StosOS integrates with several external services to provide comprehensive functionality. This guide will walk you through obtaining and configuring API keys for each service.

## Required API Keys

### Google Services (Calendar, Assistant)
- **Google Calendar API** - For calendar integration
- **Google Assistant SDK** - For smart home control and voice commands

### Spotify API
- **Spotify Web API** - For music control and playback

### OpenAI API (Optional)
- **OpenAI API** - For advanced AI voice assistant capabilities

### Amazon Alexa (Optional)
- **Alexa Voice Service** - For Alexa device control

## Step-by-Step Configuration

### 1. Google Calendar API Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Name it "StosOS Integration" or similar

2. **Enable Calendar API**
   ```bash
   # Navigate to APIs & Services > Library
   # Search for "Google Calendar API"
   # Click "Enable"
   ```

3. **Create Credentials**
   - Go to "APIs & Services > Credentials"
   - Click "Create Credentials > OAuth 2.0 Client IDs"
   - Application type: "Desktop application"
   - Name: "StosOS Calendar Client"
   - Download the JSON file

4. **Configure StosOS**
   ```bash
   # Copy credentials file to StosOS config directory
   cp ~/Downloads/client_secret_*.json /home/pi/stosos/config/google_calendar_credentials.json
   
   # Update configuration
   nano /home/pi/stosos/config/stosos_config.json
   ```

   Add to config file:
   ```json
   {
     "google_calendar": {
       "credentials_file": "config/google_calendar_credentials.json",
       "scopes": ["https://www.googleapis.com/auth/calendar"],
       "enabled": true
     }
   }
   ```

### 2. Google Assistant SDK Setup

1. **Enable Assistant API**
   - In same Google Cloud project
   - Go to "APIs & Services > Library"
   - Search for "Google Assistant API"
   - Click "Enable"

2. **Create Device Registration**
   - Go to [Actions Console](https://console.actions.google.com/)
   - Create new project or use existing
   - Go to "Device registration"
   - Register new device model

3. **Download Credentials**
   ```bash
   # Download device credentials JSON
   # Place in StosOS config directory
   cp ~/Downloads/device_credentials.json /home/pi/stosos/config/google_assistant_credentials.json
   ```

4. **Configure StosOS**
   ```json
   {
     "google_assistant": {
       "credentials_file": "config/google_assistant_credentials.json",
       "device_model_id": "your-project-stosos-device",
       "device_id": "stosos-pi-001",
       "enabled": true
     }
   }
   ```

### 3. Spotify API Setup

1. **Create Spotify App**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Log in with your Spotify account
   - Click "Create an App"
   - Name: "StosOS Controller"
   - Description: "Personal desktop environment music control"

2. **Configure App Settings**
   - Add Redirect URI: `http://localhost:8080/callback`
   - Note down Client ID and Client Secret

3. **Configure StosOS**
   ```json
   {
     "spotify": {
       "client_id": "your_spotify_client_id",
       "client_secret": "your_spotify_client_secret",
       "redirect_uri": "http://localhost:8080/callback",
       "scope": "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private",
       "enabled": true
     }
   }
   ```

### 4. OpenAI API Setup (Optional)

1. **Get API Key**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create account or log in
   - Go to "API Keys" section
   - Create new secret key

2. **Configure StosOS**
   ```json
   {
     "openai": {
       "api_key": "sk-your-openai-api-key",
       "model": "gpt-3.5-turbo",
       "max_tokens": 150,
       "temperature": 0.7,
       "enabled": true
     }
   }
   ```

### 5. Alexa Voice Service Setup (Optional)

1. **Create Amazon Developer Account**
   - Go to [Amazon Developer Console](https://developer.amazon.com/)
   - Create account or log in

2. **Create AVS Device**
   - Go to "Alexa Voice Service"
   - Create new product
   - Product Type: "Device with Alexa Built-in"
   - Note down Product ID, Client ID, and Client Secret

3. **Configure StosOS**
   ```json
   {
     "alexa": {
       "client_id": "your_alexa_client_id",
       "client_secret": "your_alexa_client_secret",
       "product_id": "your_product_id",
       "redirect_uri": "http://localhost:3000/callback",
       "enabled": true
     }
   }
   ```

## Complete Configuration File Example

Here's a complete `stosos_config.json` file with all services configured:

```json
{
  "system": {
    "debug_mode": false,
    "log_level": "INFO",
    "auto_start_modules": ["dashboard", "calendar", "tasks", "smart_home"],
    "theme": "dark",
    "language": "en"
  },
  "display": {
    "brightness_levels": [20, 50, 100],
    "idle_timeout_seconds": 30,
    "sleep_timeout_seconds": 60,
    "wake_on_touch": true
  },
  "audio": {
    "input_device": "default",
    "output_device": "default",
    "volume": 70,
    "voice_feedback": true
  },
  "google_calendar": {
    "credentials_file": "config/google_calendar_credentials.json",
    "scopes": ["https://www.googleapis.com/auth/calendar"],
    "enabled": true,
    "sync_interval_minutes": 15
  },
  "google_assistant": {
    "credentials_file": "config/google_assistant_credentials.json",
    "device_model_id": "your-project-stosos-device",
    "device_id": "stosos-pi-001",
    "enabled": true,
    "wake_word": "hey google"
  },
  "spotify": {
    "client_id": "your_spotify_client_id",
    "client_secret": "your_spotify_client_secret",
    "redirect_uri": "http://localhost:8080/callback",
    "scope": "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private",
    "enabled": true,
    "default_device": "alexa_speaker"
  },
  "openai": {
    "api_key": "sk-your-openai-api-key",
    "model": "gpt-3.5-turbo",
    "max_tokens": 150,
    "temperature": 0.7,
    "enabled": true
  },
  "alexa": {
    "client_id": "your_alexa_client_id",
    "client_secret": "your_alexa_client_secret",
    "product_id": "your_product_id",
    "redirect_uri": "http://localhost:3000/callback",
    "enabled": false
  },
  "voice_assistant": {
    "wake_word": "stos",
    "confidence_threshold": 0.7,
    "timeout_seconds": 5,
    "enabled": true
  },
  "modules": {
    "calendar": {"enabled": true, "default_view": "week"},
    "tasks": {"enabled": true, "auto_save": true},
    "idea_board": {"enabled": true, "auto_backup": true},
    "study_tracker": {"enabled": true, "pomodoro_duration": 25},
    "smart_home": {"enabled": true, "auto_discover": true},
    "spotify": {"enabled": true, "show_album_art": true}
  }
}
```

## Authentication Process

### First-Time Setup

1. **Start StosOS**
   ```bash
   cd /home/pi/stosos
   python main.py
   ```

2. **Complete OAuth Flows**
   - Google services will open browser windows for authentication
   - Spotify will require login and permission approval
   - Follow on-screen instructions for each service

3. **Verify Connections**
   - Check StosOS dashboard for service status indicators
   - Test each module to ensure API connections work
   - Review logs for any authentication errors

### Token Management

- **Automatic Refresh**: Most tokens refresh automatically
- **Manual Refresh**: Use StosOS settings panel if needed
- **Token Storage**: Tokens stored securely in `config/tokens/` directory

## Security Best Practices

### API Key Security
```bash
# Set proper file permissions
chmod 600 /home/pi/stosos/config/stosos_config.json
chmod 600 /home/pi/stosos/config/*.json

# Create backup of configuration
cp /home/pi/stosos/config/stosos_config.json /home/pi/stosos/config/stosos_config.json.backup
```

### Network Security
- Use HTTPS for all API communications
- Keep API keys private and never commit to version control
- Regularly rotate API keys when possible
- Monitor API usage for unusual activity

## Troubleshooting API Issues

### Common Problems

1. **Authentication Failures**
   ```bash
   # Check credentials file exists and is readable
   ls -la /home/pi/stosos/config/
   
   # Verify JSON syntax
   python -m json.tool /home/pi/stosos/config/stosos_config.json
   
   # Check StosOS logs
   tail -f /home/pi/stosos/logs/stosos.log
   ```

2. **Rate Limiting**
   - Reduce API call frequency in configuration
   - Implement caching where appropriate
   - Monitor API quotas in respective dashboards

3. **Network Issues**
   ```bash
   # Test internet connectivity
   ping google.com
   
   # Test specific API endpoints
   curl -I https://www.googleapis.com/calendar/v3/
   curl -I https://api.spotify.com/v1/
   ```

### Testing API Connections

```bash
# Test individual services
cd /home/pi/stosos
source venv/bin/activate

# Test Google Calendar
python -c "from services.google_calendar_service import GoogleCalendarService; print('Calendar API working')"

# Test Spotify
python -c "from services.spotify_service import SpotifyService; print('Spotify API working')"
```

## API Usage Monitoring

### Built-in Monitoring
- StosOS includes API usage tracking
- View statistics in Settings > API Status
- Monitor rate limits and quotas

### External Monitoring
- Check Google Cloud Console for API usage
- Monitor Spotify Developer Dashboard
- Review OpenAI usage dashboard

---

**Configuration Complete!** All API services should now be properly configured and ready to use with StosOS.