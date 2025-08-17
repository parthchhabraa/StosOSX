"""
Test suite for StosOS database functionality.

Tests all data models and database operations to ensure proper
functionality and error handling.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from core.database_manager import DatabaseManager
from models import Task, Idea, StudySession, SmartDevice, Priority, DeviceType, Platform


class TestDataModels:
    """Test data model classes."""
    
    def test_task_creation(self):
        """Test Task model creation and validation."""
        task = Task(
            title="Study Physics",
            description="Complete chapter 1",
            priority=Priority.HIGH,
            category="Physics",
            estimated_duration=60
        )
        
        assert task.title == "Study Physics"
        assert task.priority == Priority.HIGH
        assert task.estimated_duration == 60
        assert not task.completed
        assert task.id is not None
        assert task.created_at is not None
    
    def test_task_validation(self):
        """Test Task model validation."""
        # Empty title should raise error
        with pytest.raises(ValueError):
            Task(title="")
        
        # Negative duration should raise error
        with pytest.raises(ValueError):
            Task(title="Test", estimated_duration=-1)
    
    def test_task_serialization(self):
        """Test Task to_dict and from_dict methods."""
        original_task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.MEDIUM,
            category="Test"
        )
        
        # Convert to dict and back
        task_dict = original_task.to_dict()
        restored_task = Task.from_dict(task_dict)
        
        assert restored_task.title == original_task.title
        assert restored_task.priority == original_task.priority
        assert restored_task.id == original_task.id
    
    def test_idea_creation(self):
        """Test Idea model creation and validation."""
        idea = Idea(
            content="Great idea for project",
            tags=["project", "innovation"],
            attachments=["file1.txt", "file2.pdf"]
        )
        
        assert idea.content == "Great idea for project"
        assert "project" in idea.tags
        assert "innovation" in idea.tags
        assert len(idea.attachments) == 2
        assert idea.id is not None
    
    def test_idea_tag_management(self):
        """Test Idea tag operations."""
        idea = Idea(content="Test idea")
        
        # Add tags
        idea.add_tag("new-tag")
        assert "new-tag" in idea.tags
        
        # Remove tags
        idea.remove_tag("new-tag")
        assert "new-tag" not in idea.tags
        
        # Check tag existence
        idea.add_tag("test")
        assert idea.has_tag("test")
        assert idea.has_tag("TEST")  # Case insensitive
    
    def test_study_session_creation(self):
        """Test StudySession model creation."""
        session = StudySession(
            subject="Mathematics",
            notes="Completed algebra problems"
        )
        
        assert session.subject == "Mathematics"
        assert session.is_active  # No end time set
        assert session.duration >= 0  # Should calculate current duration
    
    def test_study_session_completion(self):
        """Test StudySession end functionality."""
        session = StudySession(subject="Physics")
        
        # End the session
        session.end_session("Good progress made")
        
        assert not session.is_active
        assert session.notes == "Good progress made"
        assert session.end_time is not None
    
    def test_smart_device_creation(self):
        """Test SmartDevice model creation."""
        device = SmartDevice(
            name="Living Room Light",
            device_type=DeviceType.LIGHT,
            platform=Platform.GOOGLE,
            capabilities=["on_off", "brightness"],
            room="Living Room"
        )
        
        assert device.name == "Living Room Light"
        assert device.device_type == DeviceType.LIGHT
        assert device.has_capability("on_off")
        assert device.is_controllable()


class TestDatabaseManager:
    """Test DatabaseManager functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        db_manager = DatabaseManager(db_path)
        yield db_manager
        db_manager.close_connections()
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_database_initialization(self, temp_db):
        """Test database schema creation."""
        # Database should be initialized without errors
        stats = temp_db.get_database_stats()
        
        # All tables should exist and be empty
        assert 'tasks' in stats
        assert 'ideas' in stats
        assert 'study_sessions' in stats
        assert 'smart_devices' in stats
        assert 'settings' in stats
    
    def test_task_crud_operations(self, temp_db):
        """Test Task CRUD operations."""
        # Create task
        task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            category="Testing"
        )
        
        # Create
        assert temp_db.create_task(task)
        
        # Read
        retrieved_task = temp_db.get_task(task.id)
        assert retrieved_task is not None
        assert retrieved_task.title == task.title
        assert retrieved_task.priority == task.priority
        
        # Update
        task.title = "Updated Task"
        task.completed = True
        assert temp_db.update_task(task)
        
        updated_task = temp_db.get_task(task.id)
        assert updated_task.title == "Updated Task"
        assert updated_task.completed
        
        # Delete
        assert temp_db.delete_task(task.id)
        deleted_task = temp_db.get_task(task.id)
        assert deleted_task is None
    
    def test_task_filtering(self, temp_db):
        """Test Task filtering functionality."""
        # Create multiple tasks
        tasks = [
            Task(title="Physics Task", category="Physics", completed=False),
            Task(title="Math Task", category="Math", completed=True),
            Task(title="Physics Task 2", category="Physics", completed=False)
        ]
        
        for task in tasks:
            temp_db.create_task(task)
        
        # Filter by category
        physics_tasks = temp_db.get_tasks(category="Physics")
        assert len(physics_tasks) == 2
        
        # Filter by completion status
        completed_tasks = temp_db.get_tasks(completed=True)
        assert len(completed_tasks) == 1
        assert completed_tasks[0].title == "Math Task"
        
        # Filter by both
        incomplete_physics = temp_db.get_tasks(category="Physics", completed=False)
        assert len(incomplete_physics) == 2
    
    def test_idea_crud_operations(self, temp_db):
        """Test Idea CRUD operations."""
        # Create idea
        idea = Idea(
            content="Test idea content",
            tags=["test", "idea"],
            attachments=["file.txt"]
        )
        
        # Create
        assert temp_db.create_idea(idea)
        
        # Read
        retrieved_idea = temp_db.get_idea(idea.id)
        assert retrieved_idea is not None
        assert retrieved_idea.content == idea.content
        assert "test" in retrieved_idea.tags
        
        # Update
        idea.content = "Updated idea content"
        idea.add_tag("updated")
        assert temp_db.update_idea(idea)
        
        updated_idea = temp_db.get_idea(idea.id)
        assert updated_idea.content == "Updated idea content"
        assert "updated" in updated_idea.tags
        
        # Delete
        assert temp_db.delete_idea(idea.id)
        deleted_idea = temp_db.get_idea(idea.id)
        assert deleted_idea is None
    
    def test_study_session_crud_operations(self, temp_db):
        """Test StudySession CRUD operations."""
        # Create session
        session = StudySession(
            subject="Physics",
            notes="Initial notes"
        )
        
        # Create
        assert temp_db.create_study_session(session)
        
        # Read
        retrieved_session = temp_db.get_study_session(session.id)
        assert retrieved_session is not None
        assert retrieved_session.subject == session.subject
        
        # Update
        session.end_session("Session completed")
        assert temp_db.update_study_session(session)
        
        updated_session = temp_db.get_study_session(session.id)
        assert not updated_session.is_active
        assert updated_session.notes == "Session completed"
        
        # Delete
        assert temp_db.delete_study_session(session.id)
        deleted_session = temp_db.get_study_session(session.id)
        assert deleted_session is None
    
    def test_smart_device_crud_operations(self, temp_db):
        """Test SmartDevice CRUD operations."""
        # Create device
        device = SmartDevice(
            name="Test Light",
            device_type=DeviceType.LIGHT,
            platform=Platform.GOOGLE,
            room="Test Room"
        )
        
        # Create
        assert temp_db.create_smart_device(device)
        
        # Read
        retrieved_device = temp_db.get_smart_device(device.id)
        assert retrieved_device is not None
        assert retrieved_device.name == device.name
        assert retrieved_device.device_type == device.device_type
        
        # Update
        device.name = "Updated Light"
        device.set_online_status(False)
        assert temp_db.update_smart_device(device)
        
        updated_device = temp_db.get_smart_device(device.id)
        assert updated_device.name == "Updated Light"
        assert not updated_device.is_online
        
        # Delete
        assert temp_db.delete_smart_device(device.id)
        deleted_device = temp_db.get_smart_device(device.id)
        assert deleted_device is None
    
    def test_settings_operations(self, temp_db):
        """Test settings operations."""
        # Set setting
        assert temp_db.set_setting("test_key", "test_value")
        
        # Get setting
        value = temp_db.get_setting("test_key")
        assert value == "test_value"
        
        # Get non-existent setting with default
        default_value = temp_db.get_setting("non_existent", "default")
        assert default_value == "default"
        
        # Update setting
        assert temp_db.set_setting("test_key", "updated_value")
        updated_value = temp_db.get_setting("test_key")
        assert updated_value == "updated_value"
        
        # Delete setting
        assert temp_db.delete_setting("test_key")
        deleted_value = temp_db.get_setting("test_key")
        assert deleted_value is None
    
    def test_database_stats(self, temp_db):
        """Test database statistics."""
        # Add some data
        task = Task(title="Test Task")
        idea = Idea(content="Test Idea")
        
        temp_db.create_task(task)
        temp_db.create_idea(idea)
        
        # Get stats
        stats = temp_db.get_database_stats()
        
        assert stats['tasks'] == 1
        assert stats['ideas'] == 1
        assert stats['study_sessions'] == 0
        assert stats['smart_devices'] == 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])