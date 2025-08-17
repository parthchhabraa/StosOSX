"""
Voice Command Parser for StosOS

Provides natural language processing for voice commands:
- Command intent recognition
- Parameter extraction
- Module routing
- Context awareness
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class VoiceCommand:
    """Structured voice command representation"""
    original_text: str
    intent: str
    module: str
    action: str
    parameters: Dict[str, Any]
    confidence: float
    timestamp: datetime


class VoiceCommandParser:
    """Natural language parser for voice commands"""
    
    def __init__(self):
        self.logger = logging.getLogger("stosos.core.voice_parser")
        
        # Command patterns and intents
        self.command_patterns = self._initialize_command_patterns()
        self.module_keywords = self._initialize_module_keywords()
        self.action_keywords = self._initialize_action_keywords()
        
        # Context tracking
        self.last_module = None
        self.conversation_context = []
        self.user_preferences = {}
    
    def _initialize_command_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize command patterns for intent recognition"""
        return {
            # Task management patterns
            'task_create': [
                {'pattern': r'(?:create|add|make|new)\s+(?:a\s+)?task\s+(.+)', 'confidence': 0.9},
                {'pattern': r'remind me to\s+(.+)', 'confidence': 0.8},
                {'pattern': r'i need to\s+(.+)', 'confidence': 0.7},
                {'pattern': r'add\s+(.+)\s+to\s+(?:my\s+)?(?:tasks?|todo)', 'confidence': 0.8}
            ],
            'task_list': [
                {'pattern': r'(?:show|list|what are)\s+(?:my\s+)?tasks?', 'confidence': 0.9},
                {'pattern': r'what do i need to do', 'confidence': 0.8},
                {'pattern': r'what\'s on my todo', 'confidence': 0.8}
            ],
            'task_complete': [
                {'pattern': r'(?:complete|finish|done with)\s+task\s+(.+)', 'confidence': 0.9},
                {'pattern': r'mark\s+(.+)\s+as\s+(?:done|complete)', 'confidence': 0.8},
                {'pattern': r'i (?:finished|completed)\s+(.+)', 'confidence': 0.7}
            ],
            
            # Calendar patterns
            'calendar_view': [
                {'pattern': r'(?:show|open|check)\s+(?:my\s+)?calendar', 'confidence': 0.9},
                {'pattern': r'what\'s (?:on\s+)?my schedule', 'confidence': 0.8},
                {'pattern': r'do i have any (?:meetings|appointments)', 'confidence': 0.8}
            ],
            'calendar_create': [
                {'pattern': r'(?:schedule|create|add)\s+(?:a\s+)?(?:meeting|appointment)\s+(.+)', 'confidence': 0.9},
                {'pattern': r'book\s+(.+)', 'confidence': 0.7},
                {'pattern': r'i have (?:a\s+)?(?:meeting|appointment)\s+(.+)', 'confidence': 0.8}
            ],
            
            # Smart home patterns
            'light_control': [
                {'pattern': r'(?:turn\s+)?(?:on|off)\s+(?:the\s+)?(.+)\s+light', 'confidence': 0.9},
                {'pattern': r'(?:dim|brighten)\s+(?:the\s+)?(.+)', 'confidence': 0.8},
                {'pattern': r'set\s+(.+)\s+to\s+(\d+)(?:\s+percent)?', 'confidence': 0.8}
            ],
            'temperature_control': [
                {'pattern': r'set\s+(?:the\s+)?temperature\s+to\s+(\d+)', 'confidence': 0.9},
                {'pattern': r'make it\s+(warmer|cooler|hotter|colder)', 'confidence': 0.8},
                {'pattern': r'(?:turn\s+)?(?:on|off)\s+(?:the\s+)?(?:heat|ac|air)', 'confidence': 0.8}
            ],
            
            # Music patterns
            'music_play': [
                {'pattern': r'play\s+(.+)', 'confidence': 0.8},
                {'pattern': r'put on\s+(.+)', 'confidence': 0.7},
                {'pattern': r'i want to hear\s+(.+)', 'confidence': 0.7}
            ],
            'music_control': [
                {'pattern': r'(?:pause|stop)\s+(?:the\s+)?music', 'confidence': 0.9},
                {'pattern': r'(?:skip|next)\s+(?:song|track)', 'confidence': 0.9},
                {'pattern': r'(?:previous|back|last)\s+(?:song|track)', 'confidence': 0.9},
                {'pattern': r'(?:turn\s+)?(?:up|down)\s+(?:the\s+)?volume', 'confidence': 0.8}
            ],
            
            # Study patterns
            'study_start': [
                {'pattern': r'start\s+(?:a\s+)?(?:study\s+)?session', 'confidence': 0.9},
                {'pattern': r'begin\s+studying\s+(.+)', 'confidence': 0.8},
                {'pattern': r'i want to study\s+(.+)', 'confidence': 0.8}
            ],
            'pomodoro_start': [
                {'pattern': r'start\s+(?:a\s+)?pomodoro', 'confidence': 0.9},
                {'pattern': r'begin\s+(?:a\s+)?(?:25\s+minute\s+)?timer', 'confidence': 0.8}
            ],
            
            # Idea patterns
            'idea_save': [
                {'pattern': r'(?:save|remember|note)\s+(?:this\s+)?idea\s*:\s*(.+)', 'confidence': 0.9},
                {'pattern': r'i have an idea\s*:\s*(.+)', 'confidence': 0.8},
                {'pattern': r'write down\s+(.+)', 'confidence': 0.7}
            ],
            
            # Navigation patterns
            'navigate': [
                {'pattern': r'(?:go to|open|show)\s+(?:the\s+)?(.+)', 'confidence': 0.8},
                {'pattern': r'switch to\s+(.+)', 'confidence': 0.8},
                {'pattern': r'take me to\s+(.+)', 'confidence': 0.7}
            ],
            
            # System patterns
            'system_status': [
                {'pattern': r'(?:how are you|status|system status)', 'confidence': 0.9},
                {'pattern': r'what\'s your status', 'confidence': 0.8}
            ],
            'help': [
                {'pattern': r'help', 'confidence': 0.9},
                {'pattern': r'what can you do', 'confidence': 0.8},
                {'pattern': r'how do i\s+(.+)', 'confidence': 0.7}
            ]
        }
    
    def _initialize_module_keywords(self) -> Dict[str, List[str]]:
        """Initialize module keyword mappings"""
        return {
            'task_manager': ['task', 'todo', 'reminder', 'assignment', 'homework'],
            'calendar': ['calendar', 'schedule', 'meeting', 'appointment', 'event'],
            'smart_home': ['light', 'temperature', 'thermostat', 'device', 'home'],
            'spotify_controller': ['music', 'song', 'play', 'spotify', 'playlist', 'album'],
            'study_tracker': ['study', 'session', 'pomodoro', 'timer', 'focus'],
            'idea_board': ['idea', 'note', 'thought', 'remember', 'write'],
            'dashboard': ['dashboard', 'home', 'main', 'overview'],
            'voice_assistant': ['voice', 'assistant', 'listen', 'speak']
        }
    
    def _initialize_action_keywords(self) -> Dict[str, List[str]]:
        """Initialize action keyword mappings"""
        return {
            'create': ['create', 'add', 'make', 'new', 'schedule', 'book'],
            'read': ['show', 'list', 'display', 'view', 'check', 'what'],
            'update': ['update', 'change', 'modify', 'edit', 'set'],
            'delete': ['delete', 'remove', 'cancel', 'clear'],
            'complete': ['complete', 'finish', 'done', 'mark'],
            'start': ['start', 'begin', 'launch', 'open'],
            'stop': ['stop', 'pause', 'end', 'close'],
            'control': ['turn', 'switch', 'adjust', 'control'],
            'navigate': ['go', 'switch', 'open', 'show']
        }
    
    def parse_command(self, text: str) -> Optional[VoiceCommand]:
        """Parse voice command text into structured command"""
        try:
            text = text.strip().lower()
            self.logger.debug(f"Parsing command: {text}")
            
            # Find best matching pattern
            best_match = self._find_best_pattern_match(text)
            
            if not best_match:
                self.logger.debug("No pattern match found")
                return None
            
            intent = best_match['intent']
            confidence = best_match['confidence']
            parameters = best_match['parameters']
            
            # Determine target module
            module = self._determine_target_module(text, intent)
            
            # Determine action
            action = self._determine_action(intent, text)
            
            # Create structured command
            command = VoiceCommand(
                original_text=text,
                intent=intent,
                module=module,
                action=action,
                parameters=parameters,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
            # Update context
            self._update_context(command)
            
            self.logger.info(f"Parsed command - Intent: {intent}, Module: {module}, Action: {action}")
            return command
            
        except Exception as e:
            self.logger.error(f"Error parsing command: {e}")
            return None
    
    def _find_best_pattern_match(self, text: str) -> Optional[Dict[str, Any]]:
        """Find the best matching pattern for the command"""
        best_match = None
        best_confidence = 0.0
        
        for intent, patterns in self.command_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                base_confidence = pattern_info['confidence']
                
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Extract parameters from match groups
                    parameters = {}
                    if match.groups():
                        parameters['primary'] = match.group(1).strip()
                        if len(match.groups()) > 1:
                            parameters['secondary'] = match.group(2).strip()
                    
                    # Adjust confidence based on match quality
                    confidence = self._calculate_match_confidence(text, pattern, base_confidence)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            'intent': intent,
                            'confidence': confidence,
                            'parameters': parameters,
                            'pattern': pattern
                        }
        
        return best_match
    
    def _calculate_match_confidence(self, text: str, pattern: str, base_confidence: float) -> float:
        """Calculate confidence score for pattern match"""
        # Start with base confidence
        confidence = base_confidence
        
        # Adjust based on text length and pattern coverage
        pattern_words = len(re.findall(r'\w+', pattern))
        text_words = len(text.split())
        
        if text_words > 0:
            coverage = min(1.0, pattern_words / text_words)
            confidence *= (0.7 + 0.3 * coverage)
        
        # Boost confidence for exact keyword matches
        for module, keywords in self.module_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    confidence *= 1.1
                    break
        
        return min(1.0, confidence)
    
    def _determine_target_module(self, text: str, intent: str) -> str:
        """Determine which module should handle the command"""
        
        # Check for explicit module keywords
        module_scores = {}
        
        for module, keywords in self.module_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            
            if score > 0:
                module_scores[module] = score
        
        # If we have module keyword matches, use the highest scoring one
        if module_scores:
            return max(module_scores, key=module_scores.get)
        
        # Fall back to intent-based routing
        intent_module_map = {
            'task_create': 'task_manager',
            'task_list': 'task_manager',
            'task_complete': 'task_manager',
            'calendar_view': 'calendar',
            'calendar_create': 'calendar',
            'light_control': 'smart_home',
            'temperature_control': 'smart_home',
            'music_play': 'spotify_controller',
            'music_control': 'spotify_controller',
            'study_start': 'study_tracker',
            'pomodoro_start': 'study_tracker',
            'idea_save': 'idea_board',
            'navigate': 'dashboard',
            'system_status': 'voice_assistant',
            'help': 'voice_assistant'
        }
        
        return intent_module_map.get(intent, 'voice_assistant')
    
    def _determine_action(self, intent: str, text: str) -> str:
        """Determine the action to perform"""
        
        # Check for explicit action keywords
        for action, keywords in self.action_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return action
        
        # Fall back to intent-based action mapping
        intent_action_map = {
            'task_create': 'create',
            'task_list': 'read',
            'task_complete': 'complete',
            'calendar_view': 'read',
            'calendar_create': 'create',
            'light_control': 'control',
            'temperature_control': 'control',
            'music_play': 'start',
            'music_control': 'control',
            'study_start': 'start',
            'pomodoro_start': 'start',
            'idea_save': 'create',
            'navigate': 'navigate',
            'system_status': 'read',
            'help': 'read'
        }
        
        return intent_action_map.get(intent, 'unknown')
    
    def _update_context(self, command: VoiceCommand):
        """Update conversation context"""
        self.last_module = command.module
        
        # Keep last 5 commands for context
        self.conversation_context.append(command)
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)
    
    def get_context_suggestions(self, text: str) -> List[str]:
        """Get context-aware command suggestions"""
        suggestions = []
        
        # Based on last module used
        if self.last_module:
            module_suggestions = {
                'task_manager': [
                    "Show my tasks",
                    "Create a new task",
                    "Mark task as complete"
                ],
                'calendar': [
                    "Show my calendar",
                    "Schedule a meeting",
                    "What's my next appointment"
                ],
                'smart_home': [
                    "Turn on the lights",
                    "Set temperature to 72",
                    "Show device status"
                ],
                'spotify_controller': [
                    "Play music",
                    "Pause music",
                    "Skip to next song"
                ]
            }
            
            suggestions.extend(module_suggestions.get(self.last_module, []))
        
        # Based on partial text match
        if len(text) > 2:
            for intent, patterns in self.command_patterns.items():
                for pattern_info in patterns:
                    # Simple suggestion based on pattern keywords
                    pattern_words = re.findall(r'\w+', pattern_info['pattern'])
                    if any(word.startswith(text.lower()) for word in pattern_words):
                        suggestions.append(f"Try: {pattern_info['pattern']}")
                        break
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def extract_time_references(self, text: str) -> Dict[str, Any]:
        """Extract time references from command text"""
        time_info = {}
        
        # Time patterns
        time_patterns = {
            'specific_time': r'(?:at\s+)?(\d{1,2}):?(\d{2})?\s*(am|pm)?',
            'relative_time': r'in\s+(\d+)\s+(minutes?|hours?|days?)',
            'day_reference': r'(today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            'date_reference': r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?'
        }
        
        for time_type, pattern in time_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_info[time_type] = match.groups()
        
        return time_info
    
    def extract_numbers(self, text: str) -> List[int]:
        """Extract numbers from command text"""
        # Find digit numbers
        numbers = re.findall(r'\d+', text)
        
        # Convert word numbers
        word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
        }
        
        words = text.lower().split()
        for word in words:
            if word in word_to_num:
                numbers.append(str(word_to_num[word]))
        
        return [int(num) for num in numbers]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parser statistics"""
        return {
            'commands_parsed': len(self.conversation_context),
            'last_module': self.last_module,
            'context_length': len(self.conversation_context),
            'patterns_loaded': sum(len(patterns) for patterns in self.command_patterns.values()),
            'modules_registered': len(self.module_keywords)
        }


# Global parser instance
voice_command_parser = VoiceCommandParser()