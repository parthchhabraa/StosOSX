"""
Voice Assistant Module for StosOS

Provides voice interaction capabilities including:
- Speech recognition using SpeechRecognition library
- Text-to-speech functionality with pyttsx3 for human-like responses
- Wake word "stos" detection for hands-free activation
- Voice command parser and routing system to appropriate modules
- Voice feedback and confirmation for executed commands

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import logging
import threading
import time
import queue
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

import speech_recognition as sr
import pyttsx3
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation

from core.base_module import BaseModule
from ui.components import (
    StosOSButton, StosOSLabel, StosOSPanel, StosOSCard, 
    StosOSIconButton, StosOSLoadingOverlay
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class VoiceAssistantModule(BaseModule):
    """Voice Assistant Module for hands-free interaction"""
    
    def __init__(self):
        super().__init__(
            module_id="voice_assistant",
            display_name="Voice Assistant",
            icon="microphone"
        )
        
        # Voice processing components
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # Threading and control
        self.listening_thread = None
        self.wake_word_thread = None
        self.is_listening = False
        self.is_wake_word_active = False
        self.command_queue = queue.Queue()
        
        # Configuration
        self.wake_word = "stos"
        self.listening_timeout = 5.0
        self.phrase_timeout = 1.0
        
        # Module registry for command routing
        self.module_registry = {}
        
        # Voice assistant state
        self.assistant_active = False
        self.last_command_time = None
        
        # UI components
        self.screen = None
        self.status_label = None
        self.listening_indicator = None
        self.voice_button = None
        
    def initialize(self) -> bool:
        """Initialize the voice assistant module"""
        try:
            self.logger.info("Initializing Voice Assistant Module")
            
            # Initialize speech recognition
            if not self._initialize_speech_recognition():
                return False
            
            # Initialize text-to-speech
            if not self._initialize_tts():
                return False
            
            # Create UI
            self._create_ui()
            
            # Start wake word detection
            self._start_wake_word_detection()
            
            self._initialized = True
            self.logger.info("Voice Assistant Module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Voice Assistant Module: {e}")
            self.handle_error(e, "initialization")
            return False
    
    def _initialize_speech_recognition(self) -> bool:
        """Initialize speech recognition components"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Configure recognition settings
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            
            self.logger.info("Speech recognition initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
            return False
    
    def _initialize_tts(self) -> bool:
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)  # Words per minute
            self.tts_engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            
            self.logger.info("Text-to-speech initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            return False
    
    def _create_ui(self):
        """Create the voice assistant UI"""
        self.screen = Screen(name='voice_assistant')
        
        # Main layout
        main_layout = FloatLayout()
        
        # Background
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(*StosOSTheme.get_color('background'))
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        main_layout.bind(
            pos=lambda instance, value: setattr(self.bg_rect, 'pos', value),
            size=lambda instance, value: setattr(self.bg_rect, 'size', value)
        )
        
        # Content panel
        content_panel = StosOSPanel(
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(30)
        )
        
        # Title
        title_label = StosOSLabel(
            text="Voice Assistant",
            font_size=StosOSTheme.get_font_size('title'),
            size_hint_y=None,
            height=dp(60)
        )
        content_layout.add_widget(title_label)
        
        # Status display
        self.status_label = StosOSLabel(
            text="Ready for voice commands",
            font_size=StosOSTheme.get_font_size('body'),
            size_hint_y=None,
            height=dp(40)
        )
        content_layout.add_widget(self.status_label)
        
        # Listening indicator
        self.listening_indicator = StosOSCard(
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={'center_x': 0.5}
        )
        
        indicator_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        self.indicator_icon = StosOSLabel(
            text="🎤",
            font_size=dp(40),
            size_hint_y=None,
            height=dp(60)
        )
        
        self.indicator_text = StosOSLabel(
            text="Idle",
            font_size=StosOSTheme.get_font_size('caption'),
            size_hint_y=None,
            height=dp(30)
        )
        
        indicator_layout.add_widget(self.indicator_icon)
        indicator_layout.add_widget(self.indicator_text)
        self.listening_indicator.add_widget(indicator_layout)
        
        content_layout.add_widget(self.listening_indicator)
        
        # Voice activation button
        self.voice_button = StosOSButton(
            text="Activate Voice Assistant",
            size_hint=(None, None),
            size=(dp(250), dp(50)),
            pos_hint={'center_x': 0.5}
        )
        self.voice_button.bind(on_press=self._on_voice_button_press)
        content_layout.add_widget(self.voice_button)
        
        # Settings section
        settings_label = StosOSLabel(
            text="Settings",
            font_size=StosOSTheme.get_font_size('subtitle'),
            size_hint_y=None,
            height=dp(40)
        )
        content_layout.add_widget(settings_label)
        
        # Wake word display
        wake_word_label = StosOSLabel(
            text=f"Wake word: '{self.wake_word}'",
            font_size=StosOSTheme.get_font_size('body'),
            size_hint_y=None,
            height=dp(30)
        )
        content_layout.add_widget(wake_word_label)
        
        content_panel.add_widget(content_layout)
        main_layout.add_widget(content_panel)
        
        self.screen.add_widget(main_layout)
    
    def get_screen(self) -> Screen:
        """Get the voice assistant screen"""
        return self.screen
    
    def register_module(self, module_id: str, module: BaseModule):
        """Register a module for voice command routing"""
        self.module_registry[module_id] = module
        self.logger.debug(f"Registered module {module_id} for voice commands")
    
    def _start_wake_word_detection(self):
        """Start wake word detection in background thread"""
        if self.wake_word_thread and self.wake_word_thread.is_alive():
            return
        
        self.is_wake_word_active = True
        self.wake_word_thread = threading.Thread(
            target=self._wake_word_detection_loop,
            daemon=True
        )
        self.wake_word_thread.start()
        self.logger.info("Wake word detection started")
    
    def _wake_word_detection_loop(self):
        """Background loop for wake word detection"""
        while self.is_wake_word_active:
            try:
                if not self.is_listening:  # Only listen for wake word when not actively listening
                    with self.microphone as source:
                        # Listen for wake word with shorter timeout
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    try:
                        # Use faster recognition for wake word
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        
                        if self.wake_word.lower() in text.lower():
                            self.logger.info(f"Wake word '{self.wake_word}' detected")
                            Clock.schedule_once(lambda dt: self._activate_voice_assistant(), 0)
                    
                    except sr.UnknownValueError:
                        # No speech detected, continue listening
                        pass
                    except sr.RequestError as e:
                        self.logger.warning(f"Wake word recognition error: {e}")
                        time.sleep(1)  # Brief pause on error
                
                else:
                    time.sleep(0.1)  # Brief pause when actively listening
                    
            except sr.WaitTimeoutError:
                # Timeout is expected, continue loop
                pass
            except Exception as e:
                self.logger.error(f"Wake word detection error: {e}")
                time.sleep(1)  # Pause on error
    
    def _activate_voice_assistant(self):
        """Activate voice assistant for command listening"""
        if self.is_listening:
            return
        
        self.assistant_active = True
        self._update_ui_status("Listening...", "🔴")
        self.speak("Yes, how can I help you?")
        
        # Start listening for command
        self._start_command_listening()
    
    def _start_command_listening(self):
        """Start listening for voice commands"""
        if self.listening_thread and self.listening_thread.is_alive():
            return
        
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._command_listening_loop,
            daemon=True
        )
        self.listening_thread.start()
    
    def _command_listening_loop(self):
        """Listen for and process voice commands"""
        try:
            with self.microphone as source:
                # Listen for command with longer timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.listening_timeout, 
                    phrase_time_limit=10
                )
            
            try:
                # Recognize the command
                command = self.recognizer.recognize_google(audio, language='en-US')
                self.logger.info(f"Voice command received: {command}")
                
                # Process the command
                Clock.schedule_once(lambda dt: self._process_voice_command(command), 0)
                
            except sr.UnknownValueError:
                Clock.schedule_once(lambda dt: self._handle_no_speech(), 0)
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition error: {e}")
                Clock.schedule_once(lambda dt: self._handle_recognition_error(), 0)
        
        except sr.WaitTimeoutError:
            Clock.schedule_once(lambda dt: self._handle_listening_timeout(), 0)
        except Exception as e:
            self.logger.error(f"Command listening error: {e}")
            Clock.schedule_once(lambda dt: self._handle_listening_error(), 0)
        finally:
            self.is_listening = False
            Clock.schedule_once(lambda dt: self._deactivate_voice_assistant(), 0)
    
    def _process_voice_command(self, command: str):
        """Process and route voice commands"""
        try:
            self.last_command_time = datetime.now()
            command_lower = command.lower().strip()
            
            self.logger.info(f"Processing command: {command}")
            
            # Built-in commands
            if self._handle_builtin_commands(command_lower):
                return
            
            # Route to appropriate module
            if self._route_command_to_modules(command, command_lower):
                return
            
            # If no module handled the command
            self.speak("I'm sorry, I didn't understand that command. Please try again.")
            
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            self.speak("I encountered an error processing your command.")
    
    def _handle_builtin_commands(self, command: str) -> bool:
        """Handle built-in voice assistant commands"""
        
        # Time and date commands
        if any(word in command for word in ['time', 'clock']):
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            return True
        
        if any(word in command for word in ['date', 'today']):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {current_date}")
            return True
        
        # System commands
        if 'status' in command or 'how are you' in command:
            self.speak("All systems are running normally. How can I assist you?")
            return True
        
        if 'help' in command:
            self.speak("I can help you with tasks, calendar, smart home, music, and more. Just ask me what you need.")
            return True
        
        # Navigation commands
        if 'dashboard' in command or 'home' in command:
            self.speak("Opening dashboard")
            # TODO: Navigate to dashboard
            return True
        
        return False
    
    def _route_command_to_modules(self, original_command: str, command_lower: str) -> bool:
        """Route commands to appropriate modules"""
        
        # Task management commands
        if any(word in command_lower for word in ['task', 'todo', 'reminder']):
            if 'task_manager' in self.module_registry:
                handled = self.module_registry['task_manager'].handle_voice_command(original_command)
                if handled:
                    self.speak("Task command processed")
                    return True
        
        # Calendar commands
        if any(word in command_lower for word in ['calendar', 'schedule', 'appointment', 'meeting']):
            if 'calendar' in self.module_registry:
                handled = self.module_registry['calendar'].handle_voice_command(original_command)
                if handled:
                    self.speak("Calendar command processed")
                    return True
        
        # Smart home commands
        if any(word in command_lower for word in ['light', 'temperature', 'thermostat', 'device']):
            if 'smart_home' in self.module_registry:
                handled = self.module_registry['smart_home'].handle_voice_command(original_command)
                if handled:
                    self.speak("Smart home command processed")
                    return True
        
        # Music commands
        if any(word in command_lower for word in ['music', 'play', 'song', 'spotify', 'pause', 'skip']):
            if 'spotify_controller' in self.module_registry:
                handled = self.module_registry['spotify_controller'].handle_voice_command(original_command)
                if handled:
                    self.speak("Music command processed")
                    return True
        
        # Study tracker commands
        if any(word in command_lower for word in ['study', 'pomodoro', 'timer', 'session']):
            if 'study_tracker' in self.module_registry:
                handled = self.module_registry['study_tracker'].handle_voice_command(original_command)
                if handled:
                    self.speak("Study command processed")
                    return True
        
        # Idea board commands
        if any(word in command_lower for word in ['idea', 'note', 'remember']):
            if 'idea_board' in self.module_registry:
                handled = self.module_registry['idea_board'].handle_voice_command(original_command)
                if handled:
                    self.speak("Idea saved")
                    return True
        
        return False
    
    def speak(self, text: str):
        """Convert text to speech"""
        try:
            if self.tts_engine:
                self.logger.debug(f"Speaking: {text}")
                
                # Run TTS in separate thread to avoid blocking
                def tts_thread():
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        self.logger.error(f"TTS error: {e}")
                
                threading.Thread(target=tts_thread, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error in speak function: {e}")
    
    def _handle_no_speech(self):
        """Handle case when no speech was detected"""
        self.speak("I didn't hear anything. Please try again.")
        self._update_ui_status("No speech detected", "🎤")
    
    def _handle_recognition_error(self):
        """Handle speech recognition errors"""
        self.speak("I'm having trouble with speech recognition. Please try again.")
        self._update_ui_status("Recognition error", "⚠️")
    
    def _handle_listening_timeout(self):
        """Handle listening timeout"""
        self.speak("I didn't hear a command. Say 'Stos' to activate me again.")
        self._update_ui_status("Listening timeout", "⏰")
    
    def _handle_listening_error(self):
        """Handle general listening errors"""
        self.speak("I encountered an error while listening. Please try again.")
        self._update_ui_status("Listening error", "❌")
    
    def _deactivate_voice_assistant(self):
        """Deactivate voice assistant and return to wake word detection"""
        self.assistant_active = False
        self._update_ui_status("Ready for voice commands", "🎤")
    
    def _update_ui_status(self, status_text: str, icon: str):
        """Update UI status indicators"""
        if self.status_label:
            self.status_label.text = status_text
        
        if self.indicator_icon:
            self.indicator_icon.text = icon
        
        if self.indicator_text:
            self.indicator_text.text = "Active" if self.assistant_active else "Idle"
    
    def _on_voice_button_press(self, instance):
        """Handle voice activation button press"""
        if not self.is_listening:
            self._activate_voice_assistant()
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        self._update_ui_status("Ready for voice commands", "🎤")
    
    def on_deactivate(self):
        """Called when module becomes inactive"""
        super().on_deactivate()
        # Keep wake word detection running even when module is not visible
    
    def cleanup(self):
        """Cleanup voice assistant resources"""
        try:
            # Stop wake word detection
            self.is_wake_word_active = False
            self.is_listening = False
            
            # Wait for threads to finish
            if self.wake_word_thread and self.wake_word_thread.is_alive():
                self.wake_word_thread.join(timeout=2)
            
            if self.listening_thread and self.listening_thread.is_alive():
                self.listening_thread.join(timeout=2)
            
            # Cleanup TTS engine
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass
            
            super().cleanup()
            self.logger.info("Voice Assistant Module cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice assistant status"""
        base_status = super().get_status()
        base_status.update({
            "wake_word_active": self.is_wake_word_active,
            "listening": self.is_listening,
            "assistant_active": self.assistant_active,
            "wake_word": self.wake_word,
            "last_command": self.last_command_time.isoformat() if self.last_command_time else None,
            "registered_modules": list(self.module_registry.keys())
        })
        return base_status
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands directed to this module"""
        command_lower = command.lower()
        
        if 'activate' in command_lower or 'start listening' in command_lower:
            self._activate_voice_assistant()
            return True
        
        if 'stop listening' in command_lower or 'deactivate' in command_lower:
            self.is_listening = False
            self.speak("Voice assistant deactivated")
            return True
        
        return False