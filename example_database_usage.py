"""
Example usage of StosOS database system.

This script demonstrates how to use the database manager and data models
for typical StosOS operations.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment to prevent Kivy window creation
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'

from core.database_manager import DatabaseManager
from models import Task, Idea, StudySession, SmartDevice, Priority, DeviceType, Platform


def demonstrate_task_management():
    """Demonstrate task management functionality."""
    print("=== Task Management Demo ===")
    
    db = DatabaseManager("data/example_stosos.db")
    
    # Create some sample tasks
    tasks = [
        Task(
            title="Complete Physics Chapter 1",
            description="Study mechanics and motion",
            priority=Priority.HIGH,
            category="Physics",
            due_date=datetime.now() + timedelta(days=3),
            estimated_duration=120
        ),
        Task(
            title="Solve Math Problems",
            description="Practice calculus integration",
            priority=Priority.MEDIUM,
            category="Mathematics",
            due_date=datetime.now() + timedelta(days=1),
            estimated_duration=90
        ),
        Task(
            title="Chemistry Lab Report",
            description="Write report on organic synthesis",
            priority=Priority.LOW,
            category="Chemistry",
            due_date=datetime.now() + timedelta(days=7),
            estimated_duration=60
        )
    ]
    
    # Add tasks to database
    print("\nAdding tasks to database...")
    for task in tasks:
        if db.create_task(task):
            print(f"✓ Added: {task.title}")
        else:
            print(f"❌ Failed to add: {task.title}")
    
    # Retrieve and display tasks
    print("\nAll tasks:")
    all_tasks = db.get_tasks()
    for task in all_tasks:
        status = "✅" if task.completed else "⏳"
        print(f"  {status} {task.title} ({task.priority.value}) - Due: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'No due date'}")
    
    # Filter tasks by category
    print("\nPhysics tasks:")
    physics_tasks = db.get_tasks(category="Physics")
    for task in physics_tasks:
        print(f"  • {task.title}")
    
    # Complete a task
    if all_tasks:
        task_to_complete = all_tasks[0]
        task_to_complete.mark_completed()
        db.update_task(task_to_complete)
        print(f"\n✅ Completed task: {task_to_complete.title}")
    
    db.close_connections()


def demonstrate_idea_management():
    """Demonstrate idea management functionality."""
    print("\n=== Idea Management Demo ===")
    
    db = DatabaseManager("data/example_stosos.db")
    
    # Create some sample ideas
    ideas = [
        Idea(
            content="Create a mobile app for tracking study habits with gamification elements",
            tags=["app", "study", "gamification", "mobile"]
        ),
        Idea(
            content="Build a smart home automation system using Raspberry Pi and voice control",
            tags=["iot", "automation", "raspberry-pi", "voice"]
        ),
        Idea(
            content="Develop an AI-powered physics problem solver that explains step-by-step solutions",
            tags=["ai", "physics", "education", "solver"]
        )
    ]
    
    # Add ideas to database
    print("\nAdding ideas to database...")
    for idea in ideas:
        if db.create_idea(idea):
            print(f"✓ Added idea: {idea.content[:50]}...")
        else:
            print(f"❌ Failed to add idea")
    
    # Retrieve and display ideas
    print("\nAll ideas:")
    all_ideas = db.get_ideas()
    for i, idea in enumerate(all_ideas, 1):
        print(f"  {i}. {idea.content}")
        print(f"     Tags: {', '.join(idea.tags)}")
        print(f"     Created: {idea.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Search ideas by tag
    print("\nIdeas tagged with 'ai':")
    ai_ideas = db.get_ideas(tag="ai")
    for idea in ai_ideas:
        print(f"  • {idea.content}")
    
    # Update an idea
    if all_ideas:
        idea_to_update = all_ideas[0]
        idea_to_update.add_tag("innovative")
        idea_to_update.update_content(idea_to_update.content + " - This could be revolutionary!")
        db.update_idea(idea_to_update)
        print(f"\n📝 Updated idea with new tag and content")
    
    db.close_connections()


def demonstrate_study_tracking():
    """Demonstrate study session tracking."""
    print("\n=== Study Session Tracking Demo ===")
    
    db = DatabaseManager("data/example_stosos.db")
    
    # Create some sample study sessions
    sessions = [
        StudySession(
            subject="Physics",
            start_time=datetime.now() - timedelta(hours=2),
            notes="Studied Newton's laws and worked on practice problems"
        ),
        StudySession(
            subject="Mathematics",
            start_time=datetime.now() - timedelta(hours=4),
            notes="Practiced integration techniques and solved calculus problems"
        )
    ]
    
    # End the sessions (simulate completed study sessions)
    sessions[0].end_session("Great progress on mechanics concepts")
    sessions[1].end_session("Mastered integration by parts")
    
    # Add sessions to database
    print("\nAdding study sessions to database...")
    for session in sessions:
        if db.create_study_session(session):
            print(f"✓ Added session: {session.subject} ({session.get_formatted_duration()})")
        else:
            print(f"❌ Failed to add session")
    
    # Retrieve and display sessions
    print("\nAll study sessions:")
    all_sessions = db.get_study_sessions()
    total_time = 0
    for session in all_sessions:
        print(f"  📚 {session.subject}: {session.get_formatted_duration()}")
        print(f"     Started: {session.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"     Notes: {session.notes}")
        total_time += session.duration
    
    print(f"\nTotal study time: {total_time // 60}h {total_time % 60}m")
    
    # Filter sessions by subject
    print("\nPhysics study sessions:")
    physics_sessions = db.get_study_sessions(subject="Physics")
    for session in physics_sessions:
        print(f"  • {session.get_formatted_duration()} - {session.notes}")
    
    db.close_connections()


def demonstrate_smart_home_devices():
    """Demonstrate smart home device management."""
    print("\n=== Smart Home Device Management Demo ===")
    
    db = DatabaseManager("data/example_stosos.db")
    
    # Create some sample smart devices
    devices = [
        SmartDevice(
            name="Living Room Light",
            device_type=DeviceType.LIGHT,
            platform=Platform.GOOGLE,
            capabilities=["on_off", "brightness", "color"],
            room="Living Room"
        ),
        SmartDevice(
            name="Bedroom Thermostat",
            device_type=DeviceType.THERMOSTAT,
            platform=Platform.ALEXA,
            capabilities=["temperature", "schedule"],
            room="Bedroom"
        ),
        SmartDevice(
            name="Kitchen Speaker",
            device_type=DeviceType.SPEAKER,
            platform=Platform.GOOGLE,
            capabilities=["play", "pause", "volume", "spotify"],
            room="Kitchen"
        )
    ]
    
    # Set initial status for devices
    devices[0].update_status({"on": True, "brightness": 80, "color": "warm_white"})
    devices[1].update_status({"temperature": 22, "target": 24, "mode": "heat"})
    devices[2].update_status({"playing": False, "volume": 50, "source": "spotify"})
    
    # Add devices to database
    print("\nAdding smart devices to database...")
    for device in devices:
        if db.create_smart_device(device):
            print(f"✓ Added device: {device.name} ({device.device_type.value})")
        else:
            print(f"❌ Failed to add device")
    
    # Retrieve and display devices
    print("\nAll smart devices:")
    all_devices = db.get_smart_devices()
    for device in all_devices:
        status_icon = "🟢" if device.is_online else "🔴"
        print(f"  {status_icon} {device.name} ({device.room})")
        print(f"     Type: {device.device_type.value} | Platform: {device.platform.value}")
        print(f"     Capabilities: {', '.join(device.capabilities)}")
        if device.status:
            print(f"     Status: {device.status}")
    
    # Filter devices by room
    print("\nLiving Room devices:")
    living_room_devices = db.get_smart_devices(room="Living Room")
    for device in living_room_devices:
        print(f"  • {device.name} - {device.device_type.value}")
    
    # Update device status
    if all_devices:
        device_to_update = all_devices[0]
        device_to_update.update_status({"brightness": 100})
        db.update_smart_device(device_to_update)
        print(f"\n💡 Updated {device_to_update.name} brightness to 100%")
    
    db.close_connections()


def demonstrate_settings_management():
    """Demonstrate application settings management."""
    print("\n=== Settings Management Demo ===")
    
    db = DatabaseManager("data/example_stosos.db")
    
    # Set some application settings
    settings = {
        "theme": "dark",
        "voice_assistant_enabled": "true",
        "power_save_timeout": "60",
        "default_study_duration": "25",
        "spotify_device_id": "living_room_speaker",
        "google_calendar_sync": "true"
    }
    
    print("\nSetting application preferences...")
    for key, value in settings.items():
        if db.set_setting(key, value):
            print(f"✓ Set {key}: {value}")
        else:
            print(f"❌ Failed to set {key}")
    
    # Retrieve and display settings
    print("\nCurrent settings:")
    for key in settings.keys():
        value = db.get_setting(key)
        print(f"  {key}: {value}")
    
    # Demonstrate default values
    print("\nTesting default values:")
    non_existent = db.get_setting("non_existent_setting", "default_value")
    print(f"  non_existent_setting: {non_existent}")
    
    # Update a setting
    db.set_setting("theme", "light")
    updated_theme = db.get_setting("theme")
    print(f"\n🎨 Updated theme setting: {updated_theme}")
    
    db.close_connections()


def show_database_statistics():
    """Show database statistics."""
    print("\n=== Database Statistics ===")
    
    db = DatabaseManager("data/example_stosos.db")
    
    stats = db.get_database_stats()
    
    print("\nDatabase contents:")
    for table, count in stats.items():
        print(f"  {table}: {count} records")
    
    total_records = sum(stats.values())
    print(f"\nTotal records: {total_records}")
    
    db.close_connections()


if __name__ == "__main__":
    print("StosOS Database System Usage Example")
    print("=" * 50)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        # Run all demonstrations
        demonstrate_task_management()
        demonstrate_idea_management()
        demonstrate_study_tracking()
        demonstrate_smart_home_devices()
        demonstrate_settings_management()
        show_database_statistics()
        
        print("\n" + "=" * 50)
        print("🎉 Database system demonstration completed successfully!")
        print("Check the 'data/example_stosos.db' file to see the stored data.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)