"""
Voice Service for StosOS

Provides low-level voice processing capabilities:
- Advanced wake word detection
- Speech recognition optimization
- Audio preprocessing and noise reduction
- Voice activity detection
"""

import logging
import threading
import time
import queue
import numpy as np
from typing import Optional, Callable, Dict, Any
from datetime import datetime

import speech_recognition as sr
import pyttsx3


class VoiceService:
    """Low-level voice processing service"""
    
    def __init__(self):
        self.logger = logging.getLogger("stosos.services.voice")
        
        # Audio components
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # Wake word detection
        self.wake_word_callback = None
        self.wake_word_sensitivity = 0.7
        self.wake_word_patterns = []
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False
        
        # Configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.energy_threshold = 300
        self.dynamic_energy_adjustment = True
        
        # Statistics
        self.stats = {
            'wake_words_detected': 0,
            'commands_processed': 0,
            'recognition_errors': 0,
            'last_activity': None
        }
    
    def initialize(self) -> bool:
        """Initialize voice service components"""
        try:
            self.logger.info("Initializing Voice Service")
            
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configure recognizer
            self._configure_recognizer()
            
            # Initialize TTS
            self._initialize_tts()
            
            # Start audio processing
            self._start_audio_processing()
            
            self.logger.info("Voice Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Voice Service: {e}")
            return False
    
    def _configure_recognizer(self):
        """Configure speech recognizer settings"""
        try:
            # Adjust for ambient noise
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Set recognition parameters
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.dynamic_energy_adjustment
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.5
            
            self.logger.info(f"Recognizer configured - Energy threshold: {self.recognizer.energy_threshold}")
            
        except Exception as e:
            self.logger.error(f"Failed to configure recognizer: {e}")
            raise
    
    def _initialize_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            if voices:
                # Try to find a good voice
                selected_voice = None
                
                # Prefer female voices
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['female', 'woman', 'zira', 'hazel']):
                        selected_voice = voice
                        break
                
                # If no female voice, use first available
                if not selected_voice:
                    selected_voice = voices[0]
                
                self.tts_engine.setProperty('voice', selected_voice.id)
                self.logger.info(f"Selected TTS voice: {selected_voice.name}")
            
            # Configure speech parameters
            self.tts_engine.setProperty('rate', 180)  # Words per minute
            self.tts_engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            raise
    
    def _start_audio_processing(self):
        """Start background audio processing thread"""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(
            target=self._audio_processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        self.logger.info("Audio processing started")
    
    def _audio_processing_loop(self):
        """Main audio processing loop"""
        while self.is_processing:
            try:
                # Process queued audio data
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get_nowait()
                    self._process_audio_chunk(audio_data)
                else:
                    time.sleep(0.01)  # Small delay to prevent busy waiting
                    
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
                time.sleep(0.1)
    
    def _process_audio_chunk(self, audio_data):
        """Process individual audio chunk"""
        try:
            # Placeholder for advanced audio processing
            # Could include:
            # - Noise reduction
            # - Voice activity detection
            # - Audio feature extraction
            # - Wake word pattern matching
            
            pass
            
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
    
    def set_wake_word_callback(self, callback: Callable[[str], None]):
        """Set callback function for wake word detection"""
        self.wake_word_callback = callback
        self.logger.debug("Wake word callback registered")
    
    def add_wake_word_pattern(self, pattern: str, sensitivity: float = 0.7):
        """Add wake word pattern for detection"""
        self.wake_word_patterns.append({
            'pattern': pattern.lower(),
            'sensitivity': sensitivity,
            'added_at': datetime.now()
        })
        self.logger.info(f"Added wake word pattern: {pattern}")
    
    def listen_for_wake_word(self, timeout: float = 1.0) -> Optional[str]:
        """Listen for wake word with timeout"""
        try:
            with self.microphone as source:
                # Listen with short timeout for wake word detection
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language='en-US')
            
            # Check for wake word patterns
            text_lower = text.lower()
            for pattern_info in self.wake_word_patterns:
                pattern = pattern_info['pattern']
                if pattern in text_lower:
                    self.stats['wake_words_detected'] += 1
                    self.stats['last_activity'] = datetime.now()
                    self.logger.info(f"Wake word detected: {pattern}")
                    
                    if self.wake_word_callback:
                        self.wake_word_callback(pattern)
                    
                    return pattern
            
            return None
            
        except sr.WaitTimeoutError:
            # Timeout is expected for wake word detection
            return None
        except sr.UnknownValueError:
            # No speech detected
            return None
        except sr.RequestError as e:
            self.logger.warning(f"Wake word recognition error: {e}")
            self.stats['recognition_errors'] += 1
            return None
        except Exception as e:
            self.logger.error(f"Wake word detection error: {e}")
            return None
    
    def listen_for_command(self, timeout: float = 5.0, phrase_limit: float = 10.0) -> Optional[str]:
        """Listen for voice command with longer timeout"""
        try:
            with self.microphone as source:
                # Listen for command with longer timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_limit
                )
            
            # Recognize the command
            command = self.recognizer.recognize_google(audio, language='en-US')
            
            self.stats['commands_processed'] += 1
            self.stats['last_activity'] = datetime.now()
            self.logger.info(f"Command recognized: {command}")
            
            return command
            
        except sr.WaitTimeoutError:
            self.logger.debug("Command listening timeout")
            return None
        except sr.UnknownValueError:
            self.logger.debug("No speech understood")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Command recognition error: {e}")
            self.stats['recognition_errors'] += 1
            return None
        except Exception as e:
            self.logger.error(f"Command listening error: {e}")
            return None
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """Convert text to speech"""
        try:
            if not self.tts_engine:
                self.logger.warning("TTS engine not initialized")
                return False
            
            self.logger.debug(f"Speaking: {text}")
            
            def tts_worker():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    self.logger.error(f"TTS playback error: {e}")
            
            if blocking:
                tts_worker()
            else:
                # Run in separate thread
                tts_thread = threading.Thread(target=tts_worker, daemon=True)
                tts_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            return False
    
    def adjust_sensitivity(self, sensitivity: float):
        """Adjust wake word detection sensitivity"""
        self.wake_word_sensitivity = max(0.1, min(1.0, sensitivity))
        self.logger.info(f"Wake word sensitivity adjusted to {self.wake_word_sensitivity}")
    
    def calibrate_microphone(self, duration: float = 2.0):
        """Recalibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.logger.info(f"Recalibrating microphone for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            
            self.logger.info(f"Microphone recalibrated - New energy threshold: {self.recognizer.energy_threshold}")
            return True
            
        except Exception as e:
            self.logger.error(f"Microphone calibration error: {e}")
            return False
    
    def get_audio_level(self) -> float:
        """Get current audio input level"""
        try:
            with self.microphone as source:
                # Quick sample to get audio level
                audio = self.recognizer.listen(source, timeout=0.1, phrase_time_limit=0.1)
                # This is a simplified approach - in practice you'd analyze the audio data
                return min(1.0, self.recognizer.energy_threshold / 1000.0)
        except:
            return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get voice service statistics"""
        return {
            **self.stats,
            'energy_threshold': self.recognizer.energy_threshold if self.recognizer else 0,
            'wake_word_sensitivity': self.wake_word_sensitivity,
            'wake_word_patterns': len(self.wake_word_patterns),
            'is_processing': self.is_processing
        }
    
    def reset_statistics(self):
        """Reset voice service statistics"""
        self.stats = {
            'wake_words_detected': 0,
            'commands_processed': 0,
            'recognition_errors': 0,
            'last_activity': None
        }
        self.logger.info("Voice service statistics reset")
    
    def shutdown(self):
        """Shutdown voice service"""
        try:
            self.logger.info("Shutting down Voice Service")
            
            # Stop audio processing
            self.is_processing = False
            
            # Wait for processing thread to finish
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2)
            
            # Stop TTS engine
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass
            
            self.logger.info("Voice Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during voice service shutdown: {e}")


# Global voice service instance
voice_service = VoiceService()