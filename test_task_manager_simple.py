#!/usr/bin/env python3
"""
Simple test script for Task Manager core functionality

Tests the task management logic without UI dependencies:
- Task model operations
- Database CRUD operations
- Filtering and sorting logic
- Statistics calculation
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.task import Task, Priority
from core.database_manager import DatabaseManager


class TaskManagerCore:
    """Core task management functionality without UI dependencies"""
    
    def __init__(self):
        self.db_manager = None
        self.tasks = []
        self.filtered_tasks = []
        self.current_filter = {"category": None, "completed": None, "priority": None}
        self.current_sort = "created_at"
        self.search_term = ""
    
    def initialize(self, db_manager):
        """Initialize with database manager"""
        self.db_manager = db_manager
        self.load_tasks()
        return True
    
    def load_tasks(self):
        """Load tasks from database"""
        if self.db_manager:
            self.tasks = self.db_manager.get_tasks()
            self.apply_filters_and_sort()
    
    def apply_filters_and_sort(self):
        """Apply current filters and sorting to task list"""
        # Start with all tasks
        filtered = self.tasks[:]
        
        # Apply search filter
        if self.search_term:
            filtered = [
                task for task in filtered
                if self.search_term.lower() in task.title.lower() or
                   self.search_term.lower() in task.description.lower() or
                   self.search_term.lower() in task.category.lower()
            ]
        
        # Apply category filter
        if self.current_filter["category"]:
            filtered = [task for task in filtered if task.category == self.current_filter["category"]]
        
        # Apply completion status filter
        if self.current_filter["completed"] is not None:
            filtered = [task for task in filtered if task.completed == self.current_filter["completed"]]
        
        # Apply priority filter
        if self.current_filter["priority"]:
            filtered = [task for task in filtered if task.priority == self.current_filter["priority"]]
        
        # Apply sorting
        if self.current_sort == "created_at":
            filtered.sort(key=lambda t: t.created_at, reverse=True)
        elif self.current_sort == "due_date":
            # Sort by due date, putting None values at the end
            filtered.sort(key=lambda t: t.due_date or datetime.max)
        elif self.current_sort == "priority":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            filtered.sort(key=lambda t: priority_order[t.priority])
        elif self.current_sort == "title":
            filtered.sort(key=lambda t: t.title.lower())
        
        self.filtered_tasks = filtered
    
    def create_task(self, task):
        """Create a new task"""
        if self.db_manager and self.db_manager.create_task(task):
            self.tasks.append(task)
            self.apply_filters_and_sort()
            return True
        return False
    
    def update_task(self, task):
        """Update an existing task"""
        if self.db_manager and self.db_manager.update_task(task):
            self.apply_filters_and_sort()
            return True
        return False
    
    def delete_task(self, task_id):
        """Delete a task"""
        if self.db_manager and self.db_manager.delete_task(task_id):
            self.tasks = [t for t in self.tasks if t.id != task_id]
            self.apply_filters_and_sort()
            return True
        return False
    
    def toggle_task_completion(self, task):
        """Toggle task completion status"""
        task.completed = not task.completed
        return self.update_task(task)
    
    def get_statistics(self):
        """Get task statistics"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        overdue_tasks = len([t for t in self.tasks if t.is_overdue()])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks
        }
    
    def get_approaching_deadlines(self, hours_ahead=24):
        """Get tasks with approaching deadlines"""
        now = datetime.now()
        threshold = now + timedelta(hours=hours_ahead)
        
        approaching = []
        for task in self.tasks:
            if (not task.completed and task.due_date and 
                now < task.due_date <= threshold):
                approaching.append(task)
        
        return approaching
    
    def handle_voice_command(self, command):
        """Handle voice commands"""
        command_lower = command.lower()
        
        if "completed tasks" in command_lower:
            self.current_filter["completed"] = True
            self.apply_filters_and_sort()
            return True
        elif "pending tasks" in command_lower:
            self.current_filter["completed"] = False
            self.apply_filters_and_sort()
            return True
        elif "high priority" in command_lower:
            self.current_filter["priority"] = Priority.HIGH
            self.apply_filters_and_sort()
            return True
        elif "search" in command_lower:
            # Extract search term after "search"
            search_start = command_lower.find("search") + 6
            search_term = command[search_start:].strip()
            if search_term:
                self.search_term = search_term
                self.apply_filters_and_sort()
            return True
        
        return False


class TestTaskManagerCore(unittest.TestCase):
    """Test cases for TaskManager core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.task_manager = TaskManagerCore()
        
        # Mock database manager
        self.mock_db = Mock(spec=DatabaseManager)
        
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
        """Test core initialization"""
        self.mock_db.get_tasks.return_value = self.sample_tasks
        
        result = self.task_manager.initialize(self.mock_db)
        
        self.assertTrue(result)
        self.assertEqual(len(self.task_manager.tasks), 3)
        self.mock_db.get_tasks.assert_called_once()
    
    def test_filter_by_category(self):
        """Test filtering tasks by category"""
        self.task_manager.tasks = self.sample_tasks
        
        # Filter by Physics
        self.task_manager.current_filter["category"] = "Physics"
        self.task_manager.apply_filters_and_sort()
        
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        self.assertEqual(self.task_manager.filtered_tasks[0].category, "Physics")
    
    def test_filter_by_completion_status(self):
        """Test filtering tasks by completion status"""
        self.task_manager.tasks = self.sample_tasks
        
        # Filter by completed tasks
        self.task_manager.current_filter["completed"] = True
        self.task_manager.apply_filters_and_sort()
        
        completed_tasks = [t for t in self.task_manager.filtered_tasks if t.completed]
        self.assertEqual(len(completed_tasks), len(self.task_manager.filtered_tasks))
        
        # Filter by pending tasks
        self.task_manager.current_filter["completed"] = False
        self.task_manager.apply_filters_and_sort()
        
        pending_tasks = [t for t in self.task_manager.filtered_tasks if not t.completed]
        self.assertEqual(len(pending_tasks), len(self.task_manager.filtered_tasks))
    
    def test_filter_by_priority(self):
        """Test filtering tasks by priority"""
        self.task_manager.tasks = self.sample_tasks
        
        # Filter by HIGH priority
        self.task_manager.current_filter["priority"] = Priority.HIGH
        self.task_manager.apply_filters_and_sort()
        
        high_priority_tasks = [t for t in self.task_manager.filtered_tasks 
                              if t.priority == Priority.HIGH]
        self.assertEqual(len(high_priority_tasks), len(self.task_manager.filtered_tasks))
    
    def test_search_functionality(self):
        """Test search functionality"""
        self.task_manager.tasks = self.sample_tasks
        
        # Search by title
        self.task_manager.search_term = "physics"
        self.task_manager.apply_filters_and_sort()
        
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        self.assertIn("Physics", self.task_manager.filtered_tasks[0].title)
        
        # Search by description
        self.task_manager.search_term = "calculus"
        self.task_manager.apply_filters_and_sort()
        
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        self.assertIn("calculus", self.task_manager.filtered_tasks[0].description)
    
    def test_sorting(self):
        """Test task sorting functionality"""
        self.task_manager.tasks = self.sample_tasks
        
        # Sort by priority
        self.task_manager.current_sort = "priority"
        self.task_manager.apply_filters_and_sort()
        
        # HIGH priority should come first
        self.assertEqual(self.task_manager.filtered_tasks[0].priority, Priority.HIGH)
        
        # Sort by due date
        self.task_manager.current_sort = "due_date"
        self.task_manager.apply_filters_and_sort()
        
        # Overdue task should come first
        self.assertTrue(self.task_manager.filtered_tasks[0].is_overdue())
    
    def test_create_task(self):
        """Test creating new task"""
        self.mock_db.create_task.return_value = True
        self.task_manager.db_manager = self.mock_db
        
        new_task = Task(
            title="New Test Task",
            description="Test description",
            priority=Priority.MEDIUM,
            category="Test"
        )
        
        initial_count = len(self.task_manager.tasks)
        result = self.task_manager.create_task(new_task)
        
        self.assertTrue(result)
        self.mock_db.create_task.assert_called_once_with(new_task)
        self.assertEqual(len(self.task_manager.tasks), initial_count + 1)
    
    def test_update_task(self):
        """Test updating existing task"""
        self.mock_db.update_task.return_value = True
        self.task_manager.db_manager = self.mock_db
        self.task_manager.tasks = self.sample_tasks
        
        task = self.sample_tasks[0]
        task.title = "Updated Title"
        
        result = self.task_manager.update_task(task)
        
        self.assertTrue(result)
        self.mock_db.update_task.assert_called_once_with(task)
    
    def test_delete_task(self):
        """Test deleting task"""
        self.mock_db.delete_task.return_value = True
        self.task_manager.db_manager = self.mock_db
        self.task_manager.tasks = self.sample_tasks[:]
        
        task_id = self.sample_tasks[0].id
        initial_count = len(self.task_manager.tasks)
        
        result = self.task_manager.delete_task(task_id)
        
        self.assertTrue(result)
        self.mock_db.delete_task.assert_called_once_with(task_id)
        self.assertEqual(len(self.task_manager.tasks), initial_count - 1)
    
    def test_toggle_completion(self):
        """Test toggling task completion"""
        self.mock_db.update_task.return_value = True
        self.task_manager.db_manager = self.mock_db
        
        task = self.sample_tasks[0]  # Initially not completed
        initial_status = task.completed
        
        result = self.task_manager.toggle_task_completion(task)
        
        self.assertTrue(result)
        self.assertEqual(task.completed, not initial_status)
        self.mock_db.update_task.assert_called_once_with(task)
    
    def test_statistics(self):
        """Test statistics calculation"""
        self.task_manager.tasks = self.sample_tasks
        
        stats = self.task_manager.get_statistics()
        
        self.assertEqual(stats["total_tasks"], 3)
        self.assertEqual(stats["completed_tasks"], 1)
        self.assertEqual(stats["pending_tasks"], 2)
        self.assertEqual(stats["overdue_tasks"], 1)
    
    def test_approaching_deadlines(self):
        """Test approaching deadlines detection"""
        self.task_manager.tasks = self.sample_tasks
        
        # Should find the task due in 1 day
        approaching = self.task_manager.get_approaching_deadlines(48)  # 48 hours
        
        self.assertEqual(len(approaching), 1)
        self.assertEqual(approaching[0].title, "Study Physics")
    
    def test_voice_commands(self):
        """Test voice command handling"""
        self.task_manager.tasks = self.sample_tasks
        
        # Test completed tasks filter
        result = self.task_manager.handle_voice_command("show completed tasks")
        self.assertTrue(result)
        self.assertEqual(self.task_manager.current_filter["completed"], True)
        
        # Test pending tasks filter
        result = self.task_manager.handle_voice_command("show pending tasks")
        self.assertTrue(result)
        self.assertEqual(self.task_manager.current_filter["completed"], False)
        
        # Test high priority filter
        result = self.task_manager.handle_voice_command("show high priority tasks")
        self.assertTrue(result)
        self.assertEqual(self.task_manager.current_filter["priority"], Priority.HIGH)
        
        # Test search command
        result = self.task_manager.handle_voice_command("search physics")
        self.assertTrue(result)
        self.assertEqual(self.task_manager.search_term, "physics")
        
        # Test unrecognized command
        result = self.task_manager.handle_voice_command("unknown command")
        self.assertFalse(result)


class TestTaskManagerIntegration(unittest.TestCase):
    """Integration tests with real database"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Use in-memory database for testing
        self.task_manager = TaskManagerCore()
        self.db_manager = DatabaseManager(":memory:")
        self.task_manager.initialize(self.db_manager)
    
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
        result = self.task_manager.create_task(task)
        self.assertTrue(result)
        self.assertEqual(len(self.task_manager.tasks), 1)
        
        # Update task
        task.description = "Updated description"
        result = self.task_manager.update_task(task)
        self.assertTrue(result)
        
        # Verify update
        updated_task = self.db_manager.get_task(task.id)
        self.assertEqual(updated_task.description, "Updated description")
        
        # Toggle completion
        result = self.task_manager.toggle_task_completion(task)
        self.assertTrue(result)
        self.assertTrue(task.completed)
        
        # Delete task
        result = self.task_manager.delete_task(task.id)
        self.assertTrue(result)
        self.assertEqual(len(self.task_manager.tasks), 0)
    
    def test_filtering_and_sorting_integration(self):
        """Test filtering and sorting with real data"""
        # Create multiple tasks
        tasks = [
            Task(title="Task A", priority=Priority.HIGH, category="Cat1"),
            Task(title="Task B", priority=Priority.LOW, category="Cat2"),
            Task(title="Task C", priority=Priority.MEDIUM, category="Cat1", completed=True)
        ]
        
        for task in tasks:
            self.task_manager.create_task(task)
        
        # Test category filtering
        self.task_manager.current_filter["category"] = "Cat1"
        self.task_manager.apply_filters_and_sort()
        self.assertEqual(len(self.task_manager.filtered_tasks), 2)
        
        # Test completion filtering
        self.task_manager.current_filter = {"category": None, "completed": True, "priority": None}
        self.task_manager.apply_filters_and_sort()
        self.assertEqual(len(self.task_manager.filtered_tasks), 1)
        
        # Test priority sorting
        self.task_manager.current_filter = {"category": None, "completed": None, "priority": None}
        self.task_manager.current_sort = "priority"
        self.task_manager.apply_filters_and_sort()
        
        # HIGH priority should be first
        self.assertEqual(self.task_manager.filtered_tasks[0].priority, Priority.HIGH)


def run_tests():
    """Run all tests"""
    print("Running Task Manager Core Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManagerCore))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManagerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)