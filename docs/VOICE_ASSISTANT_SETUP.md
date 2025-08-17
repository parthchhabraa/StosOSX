# StosOS Voice Assistant Setup Guide

## Overview

The StosOS voice assistant provides hands-free control of your desktop environment using natural language processing. This guide covers setup, configuration, and customization of the voice assistant features.

## Prerequisites

### Hardware Requirements
- **USB Microphone** or **Built-in microphone** (USB recommended for better quality)
- **Speakers or Audio Output** (3.5mm jack, HDMI, or USB speakers)
- **Internet Connection** (for cloud-based AI processing)

### Software Requirements
- StosOS base installation completed
- Python dependencies installed (handled by installation script)
- Audio system configured and working

## Voice Assistant Components

### Core Components
1. **Wake Word Detection** - Always listening for activation phrase
2. **Speech Recognition** - Converts speech to text
3. **Natural Language Processing** - Understands intent and context
4. **Text-to-Speech** - Provides voice responses
5. **System Integration** - Controls StosOS modules and functions

### Supported Wake Words
- **"Stos"** (default) - Primary wake word
- **"Hey Stos"** - Alternative activation phrase
- **"Computer"** - Fallback option
- **Custom wake words** - Configurable in settings

## Step-by-Step Setup

### 1. Audio Hardware Configuration

1. **Connect Microphone**
   ```bash
   # List audio input devices
   arecord -l
   
   # Test microphone recording
   arecord -d 5 -f cd test.wav
   aplay test.wav
   ```

2. **Configure Audio Levels**
   ```bash
   # Install audio mixer
   sudo apt install alsa-utils
   
   # Open audio mixer
   alsamixer
   
   # Adjust microphone gain (use arrow keys)
   # Press F4 to switch to capture devices
   # Increase microphone level to 70-80%
   ```

3. **Set Default Audio Devices**
   ```bash
   # Create ALSA configuration
   nano ~/.asoundrc
   ```
   
   Add configuration:
   ```
   pcm.!default {
       type asym
       playback.pcm "plughw:0,0"
       capture.pcm "plughw:1,0"
   }
   ```

### 2. Voice Assistant Configuration

1. **Edit StosOS Configuration**
   ```bash
   nano /home/pi/stosos/config/stosos_config.json
   ```

2. **Voice Assistant Settings**
   ```json
   {
     "voice_assistant": {
       "enabled": true,
       "wake_word": "stos",
       "confidence_threshold": 0.7,
       "timeout_seconds": 5,
       "continuous_listening": true,
       "voice_feedback": true,
       "language": "en-US"
     },
     "speech_recognition": {
       "engine": "google",
       "api_key": "your_google_speech_api_key",
       "language": "en-US",
       "timeout": 5,
       "phrase_timeout": 1
     },
     "text_to_speech": {
       "engine": "pyttsx3",
       "voice_id": 0,
       "rate": 150,
       "volume": 0.8
     },
     "ai_processing": {
       "provider": "openai",
       "model": "gpt-3.5-turbo",
       "max_tokens": 150,
       "temperature": 0.7,
       "system_prompt": "You are Stos, a helpful desktop assistant."
     }
   }
   ```

### 3. Wake Word Training (Optional)

1. **Install Porcupine Wake Word Engine**
   ```bash
   cd /home/pi/stosos
   source venv/bin/activate
   pip install pvporcupine
   ```

2. **Train Custom Wake Word**
   ```bash
   # Use Picovoice Console to create custom wake word
   # Download .ppn file and place in config/wake_words/
   ```

3. **Configure Custom Wake Word**
   ```json
   {
     "wake_word_detection": {
       "engine": "porcupine",
       "keyword_paths": ["config/wake_words/stos.ppn"],
       "sensitivity": 0.5
     }
   }
   ```

### 4. Voice Commands Configuration

1. **System Commands**
   ```json
   {
     "voice_commands": {
       "system": {
         "open_calendar": ["open calendar", "show calendar", "calendar"],
         "open_tasks": ["open tasks", "show tasks", "task manager"],
         "open_ideas": ["open ideas", "idea board", "show ideas"],
         "open_study": ["study tracker", "open study", "study time"],
         "open_smart_home": ["smart home", "home control", "devices"],
         "open_spotify": ["open spotify", "music", "play music"],
         "go_home": ["go home", "main menu", "dashboard"],
         "sleep_display": ["sleep", "turn off screen", "display off"],
         "wake_display": ["wake up", "turn on screen", "display on"]
       },
       "calendar": {
         "add_event": ["add event", "create event", "schedule"],
         "next_event": ["next event", "what's next", "upcoming"],
         "today_schedule": ["today's schedule", "what's today", "agenda"]
       },
       "tasks": {
         "add_task": ["add task", "create task", "new task"],
         "complete_task": ["complete task", "finish task", "done"],
         "list_tasks": ["list tasks", "show tasks", "what tasks"]
       },
       "smart_home": {
         "lights_on": ["lights on", "turn on lights"],
         "lights_off": ["lights off", "turn off lights"],
         "set_temperature": ["set temperature", "change temperature"],
         "play_music": ["play music on", "start music"]
       }
     }
   }
   ```

### 5. AI Integration Setup

1. **OpenAI Configuration**
   ```json
   {
     "openai": {
       "api_key": "sk-your-openai-api-key",
       "model": "gpt-3.5-turbo",
       "system_prompt": "You are Stos, a helpful desktop assistant for a student preparing for IIT-JEE. You can control calendar, tasks, smart home devices, and provide study assistance. Keep responses concise and helpful.",
       "max_tokens": 150,
       "temperature": 0.7
     }
   }
   ```

2. **Local AI Alternative (Ollama)**
   ```bash
   # Install Ollama for local AI processing
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a lightweight model
   ollama pull llama2:7b-chat
   ```

   Configuration:
   ```json
   {
     "ai_processing": {
       "provider": "ollama",
       "model": "llama2:7b-chat",
       "base_url": "http://localhost:11434",
       "system_prompt": "You are Stos, a helpful desktop assistant."
     }
   }
   ```

## Voice Assistant Usage

### Basic Commands

1. **Activation**
   - Say "Stos" or configured wake word
   - Wait for confirmation beep or visual indicator
   - Speak your command clearly

2. **System Navigation**
   ```
   "Stos, open calendar"
   "Stos, show my tasks"
   "Stos, go to smart home"
   "Stos, open study tracker"
   ```

3. **Task Management**
   ```
   "Stos, add task: Study physics chapter 5"
   "Stos, what are my tasks for today?"
   "Stos, mark task as complete"
   ```

4. **Calendar Control**
   ```
   "Stos, what's my next meeting?"
   "Stos, add event: Math exam tomorrow at 10 AM"
   "Stos, show today's schedule"
   ```

5. **Smart Home Control**
   ```
   "Stos, turn on the lights"
   "Stos, set temperature to 22 degrees"
   "Stos, play music in the living room"
   ```

### Advanced Commands

1. **Study Assistance**
   ```
   "Stos, start a 25-minute study session"
   "Stos, what's the formula for kinetic energy?"
   "Stos, remind me to take a break in 30 minutes"
   ```

2. **Information Queries**
   ```
   "Stos, what's the weather today?"
   "Stos, define photosynthesis"
   "Stos, convert 100 fahrenheit to celsius"
   ```

3. **System Control**
   ```
   "Stos, increase brightness"
   "Stos, turn off the display"
   "Stos, what's my system status?"
   ```

## Customization Options

### Voice Personality

1. **Modify System Prompt**
   ```json
   {
     "ai_processing": {
       "system_prompt": "You are Stos, a witty and encouraging study companion. Use casual language and provide motivational responses. Always be supportive of the user's IIT-JEE preparation goals."
     }
   }
   ```

2. **Response Style Settings**
   ```json
   {
     "voice_personality": {
       "formality": "casual",
       "enthusiasm": "high",
       "verbosity": "concise",
       "humor": "light"
     }
   }
   ```

### Custom Voice Commands

1. **Add Personal Commands**
   ```json
   {
     "custom_commands": {
       "study_mode": {
         "phrases": ["study mode", "focus time", "concentration mode"],
         "actions": [
           "set_brightness:30",
           "enable_do_not_disturb",
           "open_study_tracker",
           "start_pomodoro_timer"
         ]
       },
       "break_time": {
         "phrases": ["break time", "take a break", "rest mode"],
         "actions": [
           "pause_study_timer",
           "play_relaxing_music",
           "show_motivational_quote"
         ]
       }
     }
   }
   ```

### Voice Training

1. **Improve Recognition Accuracy**
   ```bash
   # Record voice samples for better recognition
   cd /home/pi/stosos/config/voice_training
   
   # Record wake word samples (10-15 samples recommended)
   python record_wake_word_samples.py
   
   # Train personalized model
   python train_voice_model.py
   ```

## Troubleshooting Voice Assistant

### Common Issues

1. **Microphone Not Working**
   ```bash
   # Check microphone detection
   lsusb | grep -i audio
   arecord -l
   
   # Test microphone
   arecord -d 3 -f cd test.wav && aplay test.wav
   
   # Check permissions
   groups $USER | grep audio
   sudo usermod -a -G audio $USER
   ```

2. **Wake Word Not Detected**
   ```bash
   # Check wake word sensitivity
   # Lower values = more sensitive
   # Higher values = less sensitive
   
   # Test wake word detection
   cd /home/pi/stosos
   python test_wake_word.py
   ```

3. **Poor Speech Recognition**
   ```bash
   # Check internet connection
   ping google.com
   
   # Test speech recognition directly
   python test_speech_recognition.py
   
   # Adjust microphone gain
   alsamixer
   ```

4. **No Voice Response**
   ```bash
   # Check speakers/audio output
   speaker-test -t wav -c 2
   
   # Test text-to-speech
   python test_tts.py
   
   # Check audio routing
   pactl list short sinks
   ```

### Performance Optimization

1. **Reduce Latency**
   ```json
   {
     "performance": {
       "wake_word_buffer_size": 512,
       "speech_timeout": 3,
       "processing_timeout": 5,
       "cache_responses": true
     }
   }
   ```

2. **Memory Management**
   ```json
   {
     "memory_optimization": {
       "unload_unused_models": true,
       "model_cache_size": 100,
       "garbage_collect_interval": 300
     }
   }
   ```

### Debug Mode

1. **Enable Verbose Logging**
   ```json
   {
     "voice_assistant": {
       "debug_mode": true,
       "log_audio": true,
       "log_recognition": true,
       "log_responses": true
     }
   }
   ```

2. **Monitor Voice Assistant**
   ```bash
   # Watch voice assistant logs
   tail -f /home/pi/stosos/logs/voice_assistant.log
   
   # Monitor system resources
   htop
   
   # Check audio levels
   alsamixer
   ```

## Privacy and Security

### Data Handling
- **Local Processing**: Use Ollama for offline AI processing
- **Audio Storage**: Configure whether to store audio samples
- **Cloud Services**: Understand data policies of cloud providers

### Security Settings
```json
{
  "privacy": {
    "store_audio_samples": false,
    "encrypt_voice_data": true,
    "local_processing_only": false,
    "delete_logs_after_days": 7
  }
}
```

## Advanced Features

### Multi-Language Support
```json
{
  "languages": {
    "primary": "en-US",
    "secondary": "hi-IN",
    "auto_detect": true
  }
}
```

### Voice Shortcuts
```json
{
  "voice_shortcuts": {
    "quick_note": "Stos, note",
    "emergency_help": "Stos, help",
    "system_status": "Stos, status"
  }
}
```

---

**Voice Assistant Setup Complete!** You can now control StosOS using natural voice commands. Say "Stos" followed by your command to get started.