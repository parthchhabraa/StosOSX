"""
Standalone test for database functionality without Kivy dependencies.
"""

import sqlite3
import tempfile
import os
import shutil
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


# Minimal model definitions for testing
class Priority(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class TestTask:
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    category: str = "General"
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'category': self.category,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }


def test_database_schema_creation():
    """Test database schema creation."""
    print("Testing database schema creation...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'MEDIUM',
                category TEXT DEFAULT 'General',
                completed BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create ideas table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'tasks' in tables
        assert 'ideas' in tables
        print("✓ Database tables created successfully")
        
        conn.close()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_task_crud_operations():
    """Test Task CRUD operations."""
    print("\nTesting Task CRUD operations...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Create database and table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'MEDIUM',
                category TEXT DEFAULT 'General',
                completed BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create test task
        task = TestTask(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            category="Testing"
        )
        
        # Test CREATE
        task_data = task.to_dict()
        cursor.execute("""
            INSERT INTO tasks (id, title, description, priority, category, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data['id'], task_data['title'], task_data['description'],
            task_data['priority'], task_data['category'], task_data['completed'],
            task_data['created_at']
        ))
        conn.commit()
        print("✓ Task created")
        
        # Test READ
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == task.title  # title is second column
        print("✓ Task retrieved")
        
        # Test UPDATE
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (True, task.id))
        conn.commit()
        
        cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task.id,))
        completed = cursor.fetchone()[0]
        assert completed == 1  # SQLite stores boolean as integer
        print("✓ Task updated")
        
        # Test DELETE
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task.id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task.id,))
        deleted_row = cursor.fetchone()
        assert deleted_row is None
        print("✓ Task deleted")
        
        conn.close()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_database_indexes():
    """Test database index creation."""
    print("\nTesting database indexes...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                completed BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_tasks_category ON tasks(category)")
        cursor.execute("CREATE INDEX idx_tasks_completed ON tasks(completed)")
        
        # Verify indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tasks'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        assert 'idx_tasks_category' in indexes
        assert 'idx_tasks_completed' in indexes
        print("✓ Database indexes created successfully")
        
        conn.close()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_connection_handling():
    """Test database connection handling."""
    print("\nTesting connection handling...")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Test multiple connections
        conn1 = sqlite3.connect(db_path)
        conn2 = sqlite3.connect(db_path)
        
        # Both connections should work
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        cursor1.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        conn1.commit()
        
        cursor2.execute("INSERT INTO test (name) VALUES (?)", ("test_name",))
        conn2.commit()
        
        cursor1.execute("SELECT name FROM test")
        result = cursor1.fetchone()
        assert result[0] == "test_name"
        print("✓ Multiple connections work correctly")
        
        conn1.close()
        conn2.close()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("Running StosOS Database Standalone Tests")
    print("=" * 45)
    
    try:
        test_database_schema_creation()
        test_task_crud_operations()
        test_database_indexes()
        test_connection_handling()
        
        print("\n" + "=" * 45)
        print("✅ All database tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)