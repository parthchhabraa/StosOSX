"""
Simple test to verify database manager works correctly.
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database_manager import DatabaseManager
from models import Task, Idea, StudySession, SmartDevice, Priority, DeviceType, Platform


def test_database_initialization():
    """Test database initialization and schema creation."""
    print("Testing database initialization...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        db = DatabaseManager(db_path)
        
        # Check that database file was created
        assert os.path.exists(db_path)
        print("✓ Database file created")
        
        # Check database stats
        stats = db.get_database_stats()
        assert 'tasks' in stats
        assert 'ideas' in stats
        assert 'study_sessions' in stats
        assert 'smart_devices' in stats
        print("✓ Database tables created")
        
        db.close_connections()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_task_operations():
    """Test Task CRUD operations."""
    print("\nTesting Task CRUD operations...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        db = DatabaseManager(db_path)
        
        # Create task
        task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            category="Testing"
        )
        
        # Test CREATE
        assert db.create_task(task)
        print("✓ Task created")
        
        # Test READ
        retrieved_task = db.get_task(task.id)
        assert retrieved_task is not None
        assert retrieved_task.title == task.title
        print("✓ Task retrieved")
        
        # Test UPDATE
        task.title = "Updated Task"
        task.completed = True
        assert db.update_task(task)
        
        updated_task = db.get_task(task.id)
        assert updated_task.title == "Updated Task"
        assert updated_task.completed
        print("✓ Task updated")
        
        # Test DELETE
        assert db.delete_task(task.id)
        deleted_task = db.get_task(task.id)
        assert deleted_task is None
        print("✓ Task deleted")
        
        db.close_connections()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_idea_operations():
    """Test Idea CRUD operations."""
    print("\nTesting Idea CRUD operations...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        db = DatabaseManager(db_path)
        
        # Create idea
        idea = Idea(
            content="Test idea content",
            tags=["test", "idea"]
        )
        
        # Test CREATE
        assert db.create_idea(idea)
        print("✓ Idea created")
        
        # Test READ
        retrieved_idea = db.get_idea(idea.id)
        assert retrieved_idea is not None
        assert retrieved_idea.content == idea.content
        print("✓ Idea retrieved")
        
        # Test filtering
        ideas = db.get_ideas(tag="test")
        assert len(ideas) == 1
        print("✓ Idea filtering works")
        
        db.close_connections()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_settings_operations():
    """Test settings operations."""
    print("\nTesting settings operations...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        db = DatabaseManager(db_path)
        
        # Test setting creation
        assert db.set_setting("test_key", "test_value")
        print("✓ Setting created")
        
        # Test setting retrieval
        value = db.get_setting("test_key")
        assert value == "test_value"
        print("✓ Setting retrieved")
        
        # Test default value
        default_value = db.get_setting("non_existent", "default")
        assert default_value == "default"
        print("✓ Default value works")
        
        db.close_connections()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("Running StosOS Database Manager Tests")
    print("=" * 45)
    
    try:
        test_database_initialization()
        test_task_operations()
        test_idea_operations()
        test_settings_operations()
        
        print("\n" + "=" * 45)
        print("✅ All database tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)