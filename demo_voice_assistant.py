#!/usr/bin/env python3
"""
Voice Assistant Demo for StosOS

Demonstrates voice assistant functionality including:
- Speech recognition and text-to-speech
- Wake word detection
- Voice command parsing and routing
- Interactive voice interface
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.voice_assistant import VoiceAssistantModule
from services.voice_service import VoiceService, voice_service
from core.voice_command_parser import VoiceCommandParser, voice_command_parser
from core.base_module import BaseModule


class MockTaskManager(BaseModule):
    """Mock task manager for demo purposes"""
    
    def __init__(self):
        super().__init__("task_manager", "Task Manager", "task")
        self.tasks = []
    
    def initialize(self) -> bool:
        return True
    
    def get_screen(self):
        return None
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle task-related voice commands"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['create', 'add', 'new']):
            # Extract task from command
            if 'task' in command_lower:
                task_text = command.split('task')[-1].strip()
            else:
                task_text = command
            
            self.tasks.append(task_text)
            print(f"✓ Task created: {task_text}")
            return True
        
        elif any(word in command_lower for word in ['show', 'list']):
            if self.tasks:
                print("📋 Your tasks:")
                for i, task in enumerate(self.tasks, 1):
                    print(f"  {i}. {task}")
            else:
                print("📋 No tasks found")
            return True
        
        elif any(word in command_lower for word in ['complete', 'done']):
            if self.tasks:
                completed_task = self.tasks.pop(0)
                print(f"✅ Completed task: {completed_task}")
            else:
                print("📋 No tasks to complete")
            return True
        
        return False


class MockCalendarModule(BaseModule):
    """Mock calendar module for demo purposes"""
    
    def __init__(self):
        super().__init__("calendar", "Calendar", "calendar")
        self.events = []
    
    def initialize(self) -> bool:
        return True
    
    def get_screen(self):
        return None
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle calendar-related voice commands"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['schedule', 'create', 'add']):
            # Extract event from command
            if 'meeting' in command_lower:
                event_text = command.split('meeting')[-1].strip()
                event_text = f"Meeting {event_text}"
            else:
                event_text = command
            
            self.events.append(event_text)
            print(f"📅 Event scheduled: {event_text}")
            return True
        
        elif any(word in command_lower for word in ['show', 'calendar', 'schedule']):
            if self.events:
                print("📅 Your schedule:")
                for i, event in enumerate(self.events, 1):
                    print(f"  {i}. {event}")
            else:
                print("📅 No events scheduled")
            return True
        
        return False


class MockSmartHomeModule(BaseModule):
    """Mock smart home module for demo purposes"""
    
    def __init__(self):
        super().__init__("smart_home", "Smart Home", "home")
        self.devices = {
            'living room light': {'status': 'off', 'brightness': 50},
            'bedroom light': {'status': 'off', 'brightness': 75},
            'thermostat': {'temperature': 70, 'mode': 'auto'}
        }
    
    def initialize(self) -> bool:
        return True
    
    def get_screen(self):
        return None
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle smart home voice commands"""
        command_lower = command.lower()
        
        if 'light' in command_lower:
            # Find which light
            device_name = None
            for device in self.devices:
                if any(word in command_lower for word in device.split()):
                    device_name = device
                    break
            
            if not device_name:
                device_name = 'living room light'  # Default
            
            if 'on' in command_lower:
                self.devices[device_name]['status'] = 'on'
                print(f"💡 Turned on {device_name}")
                return True
            elif 'off' in command_lower:
                self.devices[device_name]['status'] = 'off'
                print(f"💡 Turned off {device_name}")
                return True
        
        elif 'temperature' in command_lower:
            # Extract temperature
            import re
            temp_match = re.search(r'(\d+)', command)
            if temp_match:
                temp = int(temp_match.group(1))
                self.devices['thermostat']['temperature'] = temp
                print(f"🌡️ Set temperature to {temp}°F")
                return True
        
        elif 'status' in command_lower or 'devices' in command_lower:
            print("🏠 Smart home status:")
            for device, info in self.devices.items():
                if 'light' in device:
                    print(f"  💡 {device}: {info['status']} ({info['brightness']}%)")
                elif 'thermostat' in device:
                    print(f"  🌡️ {device}: {info['temperature']}°F ({info['mode']})")
            return True
        
        return False


def demo_voice_command_parser():
    """Demonstrate voice command parsing"""
    print("\n" + "=" * 50)
    print("VOICE COMMAND PARSER DEMO")
    print("=" * 50)
    
    test_commands = [
        "Create a new task to study physics",
        "Show my tasks",
        "Schedule a meeting with professor",
        "Turn on the living room light",
        "Play some music",
        "Start a study session",
        "Save this idea: use AI for homework",
        "What time is it",
        "Set temperature to 72"
    ]
    
    for command_text in test_commands:
        print(f"\nInput: '{command_text}'")
        
        command = voice_command_parser.parse_command(command_text)
        
        if command:
            print(f"  Intent: {command.intent}")
            print(f"  Module: {command.module}")
            print(f"  Action: {command.action}")
            print(f"  Confidence: {command.confidence:.2f}")
            if command.parameters:
                print(f"  Parameters: {command.parameters}")
        else:
            print("  ❌ Could not parse command")


def demo_voice_assistant_integration():
    """Demonstrate voice assistant with mock modules"""
    print("\n" + "=" * 50)
    print("VOICE ASSISTANT INTEGRATION DEMO")
    print("=" * 50)
    
    try:
        # Create voice assistant
        voice_assistant = VoiceAssistantModule()
        
        # Create mock modules
        task_manager = MockTaskManager()
        calendar_module = MockCalendarModule()
        smart_home = MockSmartHomeModule()
        
        # Initialize modules
        task_manager.initialize()
        calendar_module.initialize()
        smart_home.initialize()
        
        # Register modules with voice assistant
        voice_assistant.register_module("task_manager", task_manager)
        voice_assistant.register_module("calendar", calendar_module)
        voice_assistant.register_module("smart_home", smart_home)
        
        print("✓ Voice assistant and modules initialized")
        print("✓ Modules registered for voice commands")
        
        # Test voice command routing
        test_commands = [
            "Create a task to review chemistry notes",
            "Show my tasks",
            "Schedule a meeting with study group tomorrow",
            "Turn on the bedroom light",
            "Set temperature to 75",
            "Show smart home status",
            "What time is it"
        ]
        
        print("\nTesting voice command routing:")
        print("-" * 30)
        
        for command in test_commands:
            print(f"\n🎤 Voice command: '{command}'")
            
            # Parse command
            parsed_command = voice_command_parser.parse_command(command)
            
            if parsed_command:
                print(f"   Parsed as: {parsed_command.intent} -> {parsed_command.module}")
                
                # Route to appropriate module or handle built-in
                if voice_assistant._handle_builtin_commands(command.lower()):
                    print("   ✓ Handled by built-in commands")
                elif voice_assistant._route_command_to_modules(command, command.lower()):
                    print("   ✓ Routed to module successfully")
                else:
                    print("   ❌ No module could handle this command")
            else:
                print("   ❌ Could not parse command")
        
        # Show final status
        print("\n" + "-" * 30)
        print("Final Status:")
        print(f"Tasks: {len(task_manager.tasks)} items")
        print(f"Events: {len(calendar_module.events)} scheduled")
        print(f"Smart devices: {len(smart_home.devices)} configured")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


def demo_text_to_speech():
    """Demonstrate text-to-speech functionality"""
    print("\n" + "=" * 50)
    print("TEXT-TO-SPEECH DEMO")
    print("=" * 50)
    
    try:
        # Initialize voice service
        if voice_service.initialize():
            print("✓ Voice service initialized")
            
            # Test TTS
            test_phrases = [
                "Hello! I am your StosOS voice assistant.",
                "I can help you with tasks, calendar, smart home, and more.",
                "Voice assistant is ready for commands.",
                "All systems are running normally."
            ]
            
            print("\nTesting text-to-speech:")
            for i, phrase in enumerate(test_phrases, 1):
                print(f"{i}. Speaking: '{phrase}'")
                voice_service.speak(phrase, blocking=True)
                time.sleep(0.5)
            
            print("✓ Text-to-speech demo completed")
        else:
            print("❌ Failed to initialize voice service")
            
    except Exception as e:
        print(f"❌ TTS demo error: {e}")


def interactive_demo():
    """Interactive voice assistant demo"""
    print("\n" + "=" * 50)
    print("INTERACTIVE VOICE ASSISTANT DEMO")
    print("=" * 50)
    
    print("This demo simulates voice interaction without actual speech recognition.")
    print("You can type commands as if you were speaking them.")
    print("\nAvailable commands:")
    print("- Task commands: 'create task to...', 'show tasks', 'complete task'")
    print("- Calendar: 'schedule meeting...', 'show calendar'")
    print("- Smart home: 'turn on light', 'set temperature to 72'")
    print("- System: 'what time is it', 'help', 'status'")
    print("- Type 'quit' to exit")
    
    # Setup
    voice_assistant = VoiceAssistantModule()
    task_manager = MockTaskManager()
    calendar_module = MockCalendarModule()
    smart_home = MockSmartHomeModule()
    
    # Initialize
    task_manager.initialize()
    calendar_module.initialize()
    smart_home.initialize()
    
    voice_assistant.register_module("task_manager", task_manager)
    voice_assistant.register_module("calendar", calendar_module)
    voice_assistant.register_module("smart_home", smart_home)
    
    print("\n🎤 Voice Assistant ready! (Type your commands)")
    
    while True:
        try:
            # Get user input (simulating voice command)
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print(f"🎤 Processing: '{user_input}'")
            
            # Process command
            if voice_assistant._handle_builtin_commands(user_input.lower()):
                print("🤖 [Built-in command handled]")
            elif voice_assistant._route_command_to_modules(user_input, user_input.lower()):
                print("🤖 [Command routed to module]")
            else:
                print("🤖 I'm sorry, I didn't understand that command.")
                
                # Suggest alternatives
                suggestions = voice_command_parser.get_context_suggestions(user_input)
                if suggestions:
                    print("💡 Try one of these:")
                    for suggestion in suggestions[:3]:
                        print(f"   - {suggestion}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main demo function"""
    print("StosOS Voice Assistant Demo")
    print("=" * 60)
    
    demos = [
        ("1", "Voice Command Parser", demo_voice_command_parser),
        ("2", "Voice Assistant Integration", demo_voice_assistant_integration),
        ("3", "Text-to-Speech (requires audio)", demo_text_to_speech),
        ("4", "Interactive Demo", interactive_demo),
        ("5", "Run All Demos", None)
    ]
    
    print("\nAvailable demos:")
    for code, name, _ in demos:
        print(f"  {code}. {name}")
    
    choice = input("\nSelect demo (1-5): ").strip()
    
    if choice == "1":
        demo_voice_command_parser()
    elif choice == "2":
        demo_voice_assistant_integration()
    elif choice == "3":
        demo_text_to_speech()
    elif choice == "4":
        interactive_demo()
    elif choice == "5":
        demo_voice_command_parser()
        demo_voice_assistant_integration()
        print("\nSkipping TTS demo (requires audio hardware)")
        interactive_demo()
    else:
        print("Invalid choice. Running command parser demo...")
        demo_voice_command_parser()


if __name__ == "__main__":
    main()