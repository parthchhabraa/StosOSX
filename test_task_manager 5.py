#!/usr/bin/env python3
"""
Test script for Task Manager Module

Tests the task management functionality including:
- CRUD operations
- Priority system
- Filtering and sorting
- Statistics calculation
- Voice command handling
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with absolute imports to avoid relative import issues
try:
    from models.task import Task, Priority
    from core.database_manager import DatabaseManager
    # For testing, we'll create a simplified version that doesn't depend on UI
    from core.base_module import BaseModule
except ImportError as e:
    print(f"Import error: {e}")
    print("Running in test mode with mocked dependencies...")
    
    # Mock the dependencies for testing
    class BaseModule:
        def __init__(self, module_id, display_name, icon=""):
            self.module_id = module_id
            self.display_name = display_name
            self.icon = icon
            self._initialized = False
            self._active = False
        
        def initialize(self):
            return True
        
        def get_status(self):
            return {"module_id": self.module_id}
        
        def handle_error(self, error, context):
            pass
        
        def on_activate(self):
            self._active = True
        
        def cleanup(self):
            self._initialized = False


class TestTaskManager(unittest.TestCase):
    """Test cases for TaskManager module"""
    
    def setUp(self):
        """Set up test environment"""
        self.task_manager = TaskManager()
        
        # Mock database manager to avoid actual database operations
        self.mock_db = Mock(spec=DatabaseManager)
        self.task_manager.db_manager = self.mock_db
        
        # Sample tasks for testing
        self.sample_tasks = [
            Task(
                title="Study Physics",
                description="Review mechanics chapter",
                priority=Priority.HIGH,
                category="Physics",
                due_date=datetime.now() + timedelta(days=1),
                estimated_duration=120
            ),
            Task(
                title="Math Assignment",
                description="Complete calculus problems",
                priority=Priority.MEDIUM,
                category="Math",
                due_date=datetime.now() + timedelta(days=3),
                estimated_duration=90
            ),
            Task(
                title="Chemistry Lab Report",
                description="Write lab report for experiment",
                priority=Priority.LOW,
                category="Chemistry",
                due_date=datetime.now() - timedelta(days=1),  # Overdue
                estimated_duration=60,
                completed=True
            )
        ]
    
    def test_initialization(self):
        """Test module initialization"""
        # Mock successful database initialization
        self.mock_db.get_tasks.return_value = self.sample_tasks
        
        result = self.task_manager.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.task_manager._initialized)
        self.assertEqual(len(self.task_manager.tasks), 3)
    
    def test_load_tasks(self):
        """Test loading tasks from database"""
        self.mock_db.get_tasks.return_value = self.sample_tasks
        
        self.task_manager._load_tasks()
        
        self.assertEqual(len(self.task_manager.tasks), 3)
        self.mock_db.get_tasks.assert_called_once()
    
    def test_filter_by_category(self):
        """Test filtering tasks by category"""
        self.task_manager.tasks = self.sample_tasks
        
        # Filter by Physics
        self.task_manager.current_filter["category"] = "Physics"
        self.task_manager._apply_filters_and_sort()
        
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        self.assertEqual(self.task_manager.filtered_tasks[0].category, "Physics")
    
    def test_filter_by_completion_status(self):
        """Test filtering tasks by completion status"""
        self.task_manager.tasks = self.sample_tasks
        
        # Filter by completed tasks
        self.task_manager.current_filter["completed"] = True
        self.task_manager._apply_filters_and_sort()
        
        completed_tasks = [t for t in self.task_manager.filtered_tasks if t.completed]
        self.assertEqual(len(completed_tasks), len(self.task_manager.filtered_tasks))
        
        # Filter by pending tasks
        self.task_manager.current_filter["completed"] = False
        self.task_manager._apply_filters_and_sort()
        
        pending_tasks = [t for t in self.task_manager.filtered_tasks if not t.completed]
        self.assertEqual(len(pending_tasks), len(self.task_manager.filtered_tasks))
    
    def test_filter_by_priority(self):
        """Test filtering tasks by priority"""
        self.task_manager.tasks = self.sample_tasks
        
        # Filter by HIGH priority
        self.task_manager.current_filter["priority"] = Priority.HIGH
        self.task_manager._apply_filters_and_sort()
        
        high_priority_tasks = [t for t in self.task_manager.filtered_tasks 
                              if t.priority == Priority.HIGH]
        self.assertEqual(len(high_priority_tasks), len(self.task_manager.filtered_tasks))
    
    def test_search_functionality(self):
        """Test search functionality"""
        self.task_manager.tasks = self.sample_tasks
        
        # Search by title
        self.task_manager.search_term = "physics"
        self.task_manager._apply_filters_and_sort()
        
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        self.assertIn("Physics", self.task_manager.filtered_tasks[0].title)
        
        # Search by description
        self.task_manager.search_term = "calculus"
        self.task_manager._apply_filters_and_sort()
        
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        self.assertIn("calculus", self.task_manager.filtered_tasks[0].description)
    
    def test_sorting(self):
        """Test task sorting functionality"""
        self.task_manager.tasks = self.sample_tasks
        
        # Sort by priority
        self.task_manager.current_sort = "priority"
        self.task_manager._apply_filters_and_sort()
        
        # HIGH priority should come first
        self.assertEqual(self.task_manager.filtered_tasks[0].priority, Priority.HIGH)
        
        # Sort by due date
        self.task_manager.current_sort = "due_date"
        self.task_manager._apply_filters_and_sort()
        
        # Overdue task should come first
        self.assertTrue(self.task_manager.filtered_tasks[0].is_overdue())
    
    def test_save_new_task(self):
        """Test saving new task"""
        self.mock_db.create_task.return_value = True
        
        new_task = Task(
            title="New Test Task",
            description="Test description",
            priority=Priority.MEDIUM,
            category="Test"
        )
        
        initial_count = len(self.task_manager.tasks)
        self.task_manager._save_new_task(new_task)
        
        self.mock_db.create_task.assert_called_once_with(new_task)
        self.assertEqual(len(self.task_manager.tasks), initial_count + 1)
    
    def test_toggle_task_completion(self):
        """Test toggling task completion"""
        self.mock_db.update_task.return_value = True
        
        task = self.sample_tasks[0]  # Initially not completed
        initial_status = task.completed
        
        self.task_manager._toggle_task_completion(task)
        
        self.assertEqual(task.completed, not initial_status)
        self.mock_db.update_task.assert_called_once_with(task)
    
    def test_voice_command_handling(self):
        """Test voice command handling"""
        # Test create task command
        result = self.task_manager.handle_voice_command("create new task")
        self.assertTrue(result)
        
        # Test show tasks command
        self.mock_db.get_tasks.return_value = self.sample_tasks
        result = self.task_manager.handle_voice_command("show tasks")
        self.assertTrue(result)
        
        # Test filter commands
        result = self.task_manager.handle_voice_command("show completed tasks")
        self.assertTrue(result)
        self.assertEqual(self.task_manager.current_filter["completed"], True)
        
        result = self.task_manager.handle_voice_command("show high priority tasks")
        self.assertTrue(result)
        self.assertEqual(self.task_manager.current_filter["priority"], Priority.HIGH)
        
        # Test search command
        result = self.task_manager.handle_voice_command("search physics")
        self.assertTrue(result)
        
        # Test unrecognized command
        result = self.task_manager.handle_voice_command("unknown command")
        self.assertFalse(result)
    
    def test_statistics_calculation(self):
        """Test statistics calculation"""
        self.task_manager.tasks = self.sample_tasks
        
        status = self.task_manager.get_status()
        
        self.assertEqual(status["total_tasks"], 3)
        self.assertEqual(status["completed_tasks"], 1)
        self.assertEqual(status["overdue_tasks"], 1)
    
    def test_deadline_notifications(self):
        """Test deadline notification system"""
        # Create task due in 12 hours (should trigger notification)
        upcoming_task = Task(
            title="Upcoming Task",
            description="Due soon",
            priority=Priority.HIGH,
            category="Test",
            due_date=datetime.now() + timedelta(hours=12)
        )
        
        self.task_manager.tasks = [upcoming_task]
        
        # Mock the notification display
        with patch.object(self.task_manager, '_show_deadline_notifications') as mock_notify:
            self.task_manager._check_deadline_notifications(None)
            mock_notify.assert_called_once()
    
    def test_get_screen(self):
        """Test getting the module screen"""
        screen = self.task_manager.get_screen()
        
        self.assertIsNotNone(screen)
        self.assertEqual(screen.name, "task_manager")
    
    def test_cleanup(self):
        """Test module cleanup"""
        # Set up notification timer
        self.task_manager.notification_timer = Mock()
        
        self.task_manager.cleanup()
        
        self.task_manager.notification_timer.cancel.assert_called_once()
        self.assertFalse(self.task_manager._initialized)


class TestTaskManagerIntegration(unittest.TestCase):
    """Integration tests with real database"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Use in-memory database for testing
        self.task_manager = TaskManager()
        self.task_manager.db_manager = DatabaseManager(":memory:")
        self.task_manager.initialize()
    
    def test_full_task_lifecycle(self):
        """Test complete task lifecycle"""
        # Create task
        task = Task(
            title="Integration Test Task",
            description="Test task for integration testing",
            priority=Priority.HIGH,
            category="Testing",
            due_date=datetime.now() + timedelta(days=2),
            estimated_duration=60
        )
        
        # Save task
        self.task_manager._save_new_task(task)
        self.assertEqual(len(self.task_manager.tasks), 1)
        
        # Update task
        task.description = "Updated description"
        self.task_manager._save_edited_task(task)
        
        # Verify update
        updated_task = self.task_manager.db_manager.get_task(task.id)
        self.assertEqual(updated_task.description, "Updated description")
        
        # Toggle completion
        self.task_manager._toggle_task_completion(task)
        self.assertTrue(task.completed)
        
        # Delete task
        initial_count = len(self.task_manager.tasks)
        # Note: We can't easily test the UI confirmation dialog in unit tests
        # So we'll test the database operation directly
        result = self.task_manager.db_manager.delete_task(task.id)
        self.assertTrue(result)
    
    def test_filtering_and_sorting_integration(self):
        """Test filtering and sorting with real data"""
        # Create multiple tasks
        tasks = [
            Task(title="Task A", priority=Priority.HIGH, category="Cat1"),
            Task(title="Task B", priority=Priority.LOW, category="Cat2"),
            Task(title="Task C", priority=Priority.MEDIUM, category="Cat1", completed=True)
        ]
        
        for task in tasks:
            self.task_manager._save_new_task(task)
        
        # Test category filtering
        self.task_manager.current_filter["category"] = "Cat1"
        self.task_manager._apply_filters_and_sort()
        self.assertEqual(len(self.task_manager.filtered_tasks), 2)
        
        # Test completion filtering
        self.task_manager.current_filter = {"category": None, "completed": True, "priority": None}
        self.task_manager._apply_filters_and_sort()
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        
        # Test priority sorting
        self.task_manager.current_filter = {"category": None, "completed": None, "priority": None}
        self.task_manager.current_sort = "priority"
        self.task_manager._apply_filters_and_sort()
        
        # HIGH priority should be first
        self.assertEqual(self.task_manager.filtered_tasks[0].priority, Priority.HIGH)


def run_tests():
    """Run all tests"""
    print("Running Task Manager Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManagerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)