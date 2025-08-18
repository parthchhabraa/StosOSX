#!/usr/bin/env python3
"""
Debug test for task functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.task import Task, Priority

def test_task_creation():
    """Test basic task creation"""
    print("Testing task creation...")
    
    try:
        task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            category="Test",
            due_date=datetime.now() + timedelta(days=1),
            estimated_duration=60
        )
        
        print(f"✅ Task created: {task.title}")
        print(f"   Priority: {task.priority}")
        print(f"   Category: {task.category}")
        print(f"   Due date: {task.due_date}")
        print(f"   Completed: {task.completed}")
        print(f"   Is overdue: {task.is_overdue()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return False

def test_task_overdue():
    """Test overdue functionality"""
    print("\nTesting overdue functionality...")
    
    try:
        # Create overdue task
        overdue_task = Task(
            title="Overdue Task",
            due_date=datetime.now() - timedelta(days=1)
        )
        
        print(f"✅ Overdue task created: {overdue_task.title}")
        print(f"   Due date: {overdue_task.due_date}")
        print(f"   Is overdue: {overdue_task.is_overdue()}")
        
        # Create future task
        future_task = Task(
            title="Future Task",
            due_date=datetime.now() + timedelta(days=1)
        )
        
        print(f"✅ Future task created: {future_task.title}")
        print(f"   Due date: {future_task.due_date}")
        print(f"   Is overdue: {future_task.is_overdue()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing overdue: {e}")
        return False

def test_task_sorting():
    """Test task sorting"""
    print("\nTesting task sorting...")
    
    try:
        tasks = [
            Task(title="Task A", priority=Priority.LOW),
            Task(title="Task B", priority=Priority.HIGH),
            Task(title="Task C", priority=Priority.MEDIUM)
        ]
        
        print("Original order:")
        for i, task in enumerate(tasks):
            print(f"  {i}: {task.title} - {task.priority}")
        
        # Sort by priority
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_tasks = sorted(tasks, key=lambda t: priority_order[t.priority])
        
        print("Sorted by priority:")
        for i, task in enumerate(sorted_tasks):
            print(f"  {i}: {task.title} - {task.priority}")
        
        # Check if HIGH priority is first
        if sorted_tasks[0].priority == Priority.HIGH:
            print("✅ Priority sorting works correctly")
            return True
        else:
            print("❌ Priority sorting failed")
            return False
        
    except Exception as e:
        print(f"❌ Error testing sorting: {e}")
        return False

def test_statistics():
    """Test statistics calculation"""
    print("\nTesting statistics...")
    
    try:
        tasks = [
            Task(title="Task 1", completed=False),
            Task(title="Task 2", completed=True),
            Task(title="Task 3", completed=False, due_date=datetime.now() - timedelta(days=1))
        ]
        
        total = len(tasks)
        completed = len([t for t in tasks if t.completed])
        pending = total - completed
        overdue = len([t for t in tasks if t.is_overdue()])
        
        print(f"Total tasks: {total}")
        print(f"Completed tasks: {completed}")
        print(f"Pending tasks: {pending}")
        print(f"Overdue tasks: {overdue}")
        
        expected_stats = {
            "total": 3,
            "completed": 1,
            "pending": 2,
            "overdue": 1
        }
        
        actual_stats = {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue
        }
        
        if actual_stats == expected_stats:
            print("✅ Statistics calculation works correctly")
            return True
        else:
            print(f"❌ Statistics mismatch. Expected: {expected_stats}, Got: {actual_stats}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing statistics: {e}")
        return False

def main():
    """Run all debug tests"""
    print("Running Task Debug Tests...")
    print("=" * 40)
    
    tests = [
        test_task_creation,
        test_task_overdue,
        test_task_sorting,
        test_statistics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All debug tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)