"""
Simple test to verify data models work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Task, Idea, StudySession, SmartDevice, Priority, DeviceType, Platform
from datetime import datetime


def test_task_model():
    """Test Task model basic functionality."""
    print("Testing Task model...")
    
    # Create task
    task = Task(
        title="Study Physics",
        description="Complete chapter 1",
        priority=Priority.HIGH,
        category="Physics"
    )
    
    print(f"Created task: {task.title}")
    print(f"Priority: {task.priority}")
    print(f"ID: {task.id}")
    
    # Test serialization
    task_dict = task.to_dict()
    restored_task = Task.from_dict(task_dict)
    
    assert restored_task.title == task.title
    assert restored_task.priority == task.priority
    print("✓ Task serialization works")
    
    # Test completion
    task.mark_completed()
    assert task.completed
    print("✓ Task completion works")


def test_idea_model():
    """Test Idea model basic functionality."""
    print("\nTesting Idea model...")
    
    # Create idea
    idea = Idea(
        content="Great project idea",
        tags=["project", "innovation"]
    )
    
    print(f"Created idea: {idea.content}")
    print(f"Tags: {idea.tags}")
    
    # Test tag management
    idea.add_tag("new-tag")
    assert "new-tag" in idea.tags
    print("✓ Tag addition works")
    
    # Test serialization
    idea_dict = idea.to_dict()
    restored_idea = Idea.from_dict(idea_dict)
    
    assert restored_idea.content == idea.content
    assert set(restored_idea.tags) == set(idea.tags)
    print("✓ Idea serialization works")


def test_study_session_model():
    """Test StudySession model basic functionality."""
    print("\nTesting StudySession model...")
    
    # Create session
    session = StudySession(
        subject="Mathematics",
        notes="Working on algebra"
    )
    
    print(f"Created session: {session.subject}")
    print(f"Is active: {session.is_active}")
    print(f"Duration: {session.duration} minutes")
    
    # Test ending session
    session.end_session("Completed successfully")
    assert not session.is_active
    assert session.notes == "Completed successfully"
    print("✓ Session completion works")
    
    # Test serialization
    session_dict = session.to_dict()
    restored_session = StudySession.from_dict(session_dict)
    
    assert restored_session.subject == session.subject
    print("✓ StudySession serialization works")


def test_smart_device_model():
    """Test SmartDevice model basic functionality."""
    print("\nTesting SmartDevice model...")
    
    # Create device
    device = SmartDevice(
        name="Living Room Light",
        device_type=DeviceType.LIGHT,
        platform=Platform.GOOGLE,
        capabilities=["on_off", "brightness"],
        room="Living Room"
    )
    
    print(f"Created device: {device.name}")
    print(f"Type: {device.device_type}")
    print(f"Capabilities: {device.capabilities}")
    
    # Test capabilities
    assert device.has_capability("on_off")
    assert device.is_controllable()
    print("✓ Device capabilities work")
    
    # Test status updates
    device.update_status({"brightness": 80, "on": True})
    assert device.get_status_value("brightness") == 80
    print("✓ Status updates work")
    
    # Test serialization
    device_dict = device.to_dict()
    restored_device = SmartDevice.from_dict(device_dict)
    
    assert restored_device.name == device.name
    assert restored_device.device_type == device.device_type
    print("✓ SmartDevice serialization works")


if __name__ == "__main__":
    print("Running StosOS Data Models Tests")
    print("=" * 40)
    
    try:
        test_task_model()
        test_idea_model()
        test_study_session_model()
        test_smart_device_model()
        
        print("\n" + "=" * 40)
        print("✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)