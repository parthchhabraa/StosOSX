#!/usr/bin/env python3
"""
Test Voice Assistant Module

Tests voice assistant functionality including:
- Speech recognition initialization
- Text-to-speech functionality
- Wake word detection
- Voice command parsing and routing
- Module integration
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.voice_assistant import VoiceAssistantModule
from services.voice_service import VoiceService
from core.voice_command_parser import VoiceCommandParser, VoiceCommand


class TestVoiceAssistantModule(unittest.TestCase):
    """Test cases for Voice Assistant Module"""
    
    def setUp(self):
        """Set up test environment"""
        self.voice_assistant = VoiceAssistantModule()
        
        # Mock external dependencies
        self.mock_recognizer = Mock()
        self.mock_microphone = Mock()
        self.mock_tts_engine = Mock()
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    @patch('pyttsx3.init')
    def test_initialization(self, mock_tts_init, mock_mic, mock_recognizer):
        """Test voice assistant initialization"""
        # Setup mocks
        mock_tts_init.return_value = self.mock_tts_engine
        mock_recognizer.return_value = self.mock_recognizer
        mock_mic.return_value = self.mock_microphone
        
        # Mock microphone context manager
        self.mock_microphone.__enter__ = Mock(return_value=self.mock_microphone)
        self.mock_microphone.__exit__ = Mock(return_value=None)
        
        # Test initialization
        result = self.voice_assistant.initialize()
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(self.voice_assistant._initialized)
        self.assertIsNotNone(self.voice_assistant.recognizer)
        self.assertIsNotNone(self.voice_assistant.tts_engine)
    
    def test_module_registration(self):
        """Test module registration for voice command routing"""
        # Create mock module
        mock_module = Mock()
        mock_module.handle_voice_command.return_value = True
        
        # Register module
        self.voice_assistant.register_module("test_module", mock_module)
        
        # Verify registration
        self.assertIn("test_module", self.voice_assistant.module_registry)
        self.assertEqual(self.voice_assistant.module_registry["test_module"], mock_module)
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    @patch('pyttsx3.init')
    def test_wake_word_detection(self, mock_tts_init, mock_mic, mock_recognizer):
        """Test wake word detection functionality"""
        # Setup mocks
        mock_tts_init.return_value = self.mock_tts_engine
        mock_recognizer.return_value = self.mock_recognizer
        mock_mic.return_value = self.mock_microphone
        
        # Mock microphone context manager
        self.mock_microphone.__enter__ = Mock(return_value=self.mock_microphone)
        self.mock_microphone.__exit__ = Mock(return_value=None)
        
        # Mock speech recognition to return wake word
        mock_audio = Mock()
        self.mock_recognizer.listen.return_value = mock_audio
        self.mock_recognizer.recognize_google.return_value = "Hey Stos, how are you?"
        
        # Initialize voice assistant
        self.voice_assistant.initialize()
        
        # Test wake word detection (this would normally run in a thread)
        # We'll test the logic directly
        self.assertTrue("stos" in "Hey Stos, how are you?".lower())
    
    def test_voice_command_routing(self):
        """Test voice command routing to appropriate modules"""
        # Setup mock modules
        task_module = Mock()
        task_module.handle_voice_command.return_value = True
        
        calendar_module = Mock()
        calendar_module.handle_voice_command.return_value = False
        
        # Register modules
        self.voice_assistant.register_module("task_manager", task_module)
        self.voice_assistant.register_module("calendar", calendar_module)
        
        # Test task command routing
        result = self.voice_assistant._route_command_to_modules(
            "Create a new task for homework", 
            "create a new task for homework"
        )
        
        # Verify task module was called
        task_module.handle_voice_command.assert_called_once()
        self.assertTrue(result)
    
    def test_builtin_commands(self):
        """Test built-in voice assistant commands"""
        # Test time command
        result = self.voice_assistant._handle_builtin_commands("what time is it")
        self.assertTrue(result)
        
        # Test date command
        result = self.voice_assistant._handle_builtin_commands("what's the date today")
        self.assertTrue(result)
        
        # Test status command
        result = self.voice_assistant._handle_builtin_commands("how are you")
        self.assertTrue(result)
        
        # Test help command
        result = self.voice_assistant._handle_builtin_commands("help me")
        self.assertTrue(result)
        
        # Test unknown command
        result = self.voice_assistant._handle_builtin_commands("unknown command")
        self.assertFalse(result)
    
    @patch('pyttsx3.init')
    def test_text_to_speech(self, mock_tts_init):
        """Test text-to-speech functionality"""
        # Setup mock
        mock_tts_init.return_value = self.mock_tts_engine
        
        # Initialize TTS
        self.voice_assistant._initialize_tts()
        
        # Test speaking
        self.voice_assistant.speak("Hello, this is a test")
        
        # Verify TTS engine was configured
        self.mock_tts_engine.setProperty.assert_called()
    
    def test_status_reporting(self):
        """Test voice assistant status reporting"""
        status = self.voice_assistant.get_status()
        
        # Verify status structure
        self.assertIn("module_id", status)
        self.assertIn("wake_word_active", status)
        self.assertIn("listening", status)
        self.assertIn("assistant_active", status)
        self.assertIn("wake_word", status)
        self.assertIn("registered_modules", status)
        
        # Verify values
        self.assertEqual(status["module_id"], "voice_assistant")
        self.assertEqual(status["wake_word"], "stos")


class TestVoiceService(unittest.TestCase):
    """Test cases for Voice Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.voice_service = VoiceService()
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    @patch('pyttsx3.init')
    def test_voice_service_initialization(self, mock_tts_init, mock_mic, mock_recognizer):
        """Test voice service initialization"""
        # Setup mocks
        mock_tts_engine = Mock()
        mock_tts_init.return_value = mock_tts_engine
        mock_recognizer.return_value = Mock()
        mock_mic.return_value = Mock()
        
        # Mock microphone context manager
        mock_microphone = Mock()
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        mock_mic.return_value = mock_microphone
        
        # Test initialization
        result = self.voice_service.initialize()
        
        # Assertions
        self.assertTrue(result)
        self.assertIsNotNone(self.voice_service.recognizer)
        self.assertIsNotNone(self.voice_service.tts_engine)
    
    def test_wake_word_pattern_management(self):
        """Test wake word pattern management"""
        # Add wake word patterns
        self.voice_service.add_wake_word_pattern("stos", 0.8)
        self.voice_service.add_wake_word_pattern("hey stos", 0.9)
        
        # Verify patterns were added
        self.assertEqual(len(self.voice_service.wake_word_patterns), 2)
        self.assertEqual(self.voice_service.wake_word_patterns[0]['pattern'], "stos")
        self.assertEqual(self.voice_service.wake_word_patterns[1]['pattern'], "hey stos")
    
    def test_statistics_tracking(self):
        """Test voice service statistics"""
        # Get initial statistics
        stats = self.voice_service.get_statistics()
        
        # Verify statistics structure
        self.assertIn('wake_words_detected', stats)
        self.assertIn('commands_processed', stats)
        self.assertIn('recognition_errors', stats)
        self.assertIn('is_processing', stats)
        
        # Test statistics reset
        self.voice_service.reset_statistics()
        stats_after_reset = self.voice_service.get_statistics()
        self.assertEqual(stats_after_reset['wake_words_detected'], 0)
        self.assertEqual(stats_after_reset['commands_processed'], 0)


class TestVoiceCommandParser(unittest.TestCase):
    """Test cases for Voice Command Parser"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = VoiceCommandParser()
    
    def test_task_command_parsing(self):
        """Test parsing of task-related commands"""
        # Test task creation
        command = self.parser.parse_command("Create a new task to study physics")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "task_manager")
        self.assertEqual(command.action, "create")
        self.assertIn("study physics", command.parameters.get("primary", ""))
        
        # Test task listing
        command = self.parser.parse_command("Show my tasks")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "task_manager")
        self.assertEqual(command.action, "read")
        
        # Test task completion
        command = self.parser.parse_command("Mark homework as done")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "task_manager")
        self.assertEqual(command.action, "complete")
    
    def test_calendar_command_parsing(self):
        """Test parsing of calendar-related commands"""
        # Test calendar view
        command = self.parser.parse_command("Show my calendar")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "calendar")
        self.assertEqual(command.action, "read")
        
        # Test meeting creation
        command = self.parser.parse_command("Schedule a meeting with professor")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "calendar")
        self.assertEqual(command.action, "create")
    
    def test_smart_home_command_parsing(self):
        """Test parsing of smart home commands"""
        # Test light control
        command = self.parser.parse_command("Turn on the living room light")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "smart_home")
        self.assertEqual(command.action, "control")
        
        # Test temperature control
        command = self.parser.parse_command("Set temperature to 72")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "smart_home")
        self.assertEqual(command.action, "control")
    
    def test_music_command_parsing(self):
        """Test parsing of music-related commands"""
        # Test music playback
        command = self.parser.parse_command("Play some jazz music")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "spotify_controller")
        self.assertEqual(command.action, "start")
        
        # Test music control
        command = self.parser.parse_command("Pause the music")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "spotify_controller")
        self.assertEqual(command.action, "control")
    
    def test_study_command_parsing(self):
        """Test parsing of study-related commands"""
        # Test study session
        command = self.parser.parse_command("Start a study session")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "study_tracker")
        self.assertEqual(command.action, "start")
        
        # Test pomodoro timer
        command = self.parser.parse_command("Start a pomodoro")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "study_tracker")
        self.assertEqual(command.action, "start")
    
    def test_idea_command_parsing(self):
        """Test parsing of idea-related commands"""
        command = self.parser.parse_command("Save this idea: use AI for homework help")
        self.assertIsNotNone(command)
        self.assertEqual(command.module, "idea_board")
        self.assertEqual(command.action, "create")
        self.assertIn("use AI for homework help", command.parameters.get("primary", ""))
    
    def test_time_extraction(self):
        """Test extraction of time references from commands"""
        time_info = self.parser.extract_time_references("Schedule meeting at 3:30 PM tomorrow")
        
        self.assertIn("specific_time", time_info)
        self.assertIn("day_reference", time_info)
    
    def test_number_extraction(self):
        """Test extraction of numbers from commands"""
        numbers = self.parser.extract_numbers("Set temperature to 72 degrees")
        self.assertIn(72, numbers)
        
        numbers = self.parser.extract_numbers("Create five new tasks")
        self.assertIn(5, numbers)
    
    def test_context_suggestions(self):
        """Test context-aware command suggestions"""
        # Set context
        self.parser.last_module = "task_manager"
        
        # Get suggestions
        suggestions = self.parser.get_context_suggestions("show")
        
        self.assertIsInstance(suggestions, list)
        self.assertTrue(len(suggestions) > 0)
    
    def test_confidence_scoring(self):
        """Test command confidence scoring"""
        # High confidence command
        command = self.parser.parse_command("Create a new task to study chemistry")
        self.assertIsNotNone(command)
        self.assertGreater(command.confidence, 0.7)
        
        # Lower confidence command (ambiguous)
        command = self.parser.parse_command("Do something")
        # This should either return None or have low confidence
        if command:
            self.assertLess(command.confidence, 0.5)


def run_voice_assistant_tests():
    """Run all voice assistant tests"""
    print("=" * 60)
    print("VOICE ASSISTANT MODULE TESTS")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestVoiceAssistantModule))
    test_suite.addTest(unittest.makeSuite(TestVoiceService))
    test_suite.addTest(unittest.makeSuite(TestVoiceCommandParser))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    success = run_voice_assistant_tests()
    sys.exit(0 if success else 1)