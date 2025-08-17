"""
Database manager for StosOS local SQLite database.

Handles database connections, schema creation, and CRUD operations
for all data models with proper error handling and connection pooling.
"""

import sqlite3
import threading
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from models import Task, Idea, StudySession, SmartDevice
from models.calendar_event import CalendarEvent


class DatabaseManager:
    """
    Manages SQLite database connections and operations for StosOS.
    
    Features:
    - Connection pooling with thread safety
    - Automatic schema creation and migration
    - CRUD operations for all data models
    - Error handling and recovery
    - Transaction management
    """
    
    def __init__(self, db_path: str = "data/stosos.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._local = threading.local()
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize database schema
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign key constraints
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database operations with automatic transaction handling."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            cursor.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self.get_cursor() as cursor:
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT NOT NULL DEFAULT 'MEDIUM',
                    category TEXT DEFAULT 'General',
                    due_date TEXT,
                    created_at TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    estimated_duration INTEGER DEFAULT 30
                )
            """)
            
            # Ideas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ideas (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    attachments TEXT DEFAULT ''
                )
            """)
            
            # Study sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER,
                    tasks_completed TEXT DEFAULT '',
                    notes TEXT DEFAULT ''
                )
            """)
            
            # Smart devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS smart_devices (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    status TEXT DEFAULT '{}',
                    capabilities TEXT DEFAULT '',
                    room TEXT DEFAULT 'Unknown',
                    is_online BOOLEAN DEFAULT TRUE,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Calendar events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    location TEXT DEFAULT '',
                    start_time TEXT,
                    end_time TEXT,
                    all_day BOOLEAN DEFAULT FALSE,
                    timezone TEXT DEFAULT 'UTC',
                    google_event_id TEXT,
                    calendar_id TEXT DEFAULT 'primary',
                    recurrence TEXT DEFAULT '[]',
                    reminders TEXT DEFAULT '[]',
                    attendees TEXT DEFAULT '[]',
                    organizer TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'confirmed',
                    visibility TEXT DEFAULT 'default',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_synced TEXT,
                    is_local_only BOOLEAN DEFAULT FALSE,
                    needs_sync BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Settings table for application configuration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_created_at ON ideas(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_subject ON study_sessions(subject)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_start_time ON study_sessions(start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_smart_devices_room ON smart_devices(room)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_smart_devices_type ON smart_devices(device_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_start_time ON calendar_events(start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_calendar_id ON calendar_events(calendar_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_google_id ON calendar_events(google_event_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_needs_sync ON calendar_events(needs_sync)")
    
    # Task CRUD operations
    def create_task(self, task: Task) -> bool:
        """Create a new task in the database."""
        try:
            with self.get_cursor() as cursor:
                data = task.to_dict()
                cursor.execute("""
                    INSERT INTO tasks (id, title, description, priority, category, 
                                     due_date, created_at, completed, estimated_duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['title'], data['description'], data['priority'],
                    data['category'], data['due_date'], data['created_at'],
                    data['completed'], data['estimated_duration']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if row:
                    return Task.from_dict(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    def get_tasks(self, category: str = None, completed: bool = None) -> List[Task]:
        """Retrieve tasks with optional filtering."""
        try:
            with self.get_cursor() as cursor:
                query = "SELECT * FROM tasks WHERE 1=1"
                params = []
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if completed is not None:
                    query += " AND completed = ?"
                    params.append(completed)
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [Task.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get tasks: {e}")
            return []
    
    def update_task(self, task: Task) -> bool:
        """Update an existing task."""
        try:
            with self.get_cursor() as cursor:
                data = task.to_dict()
                cursor.execute("""
                    UPDATE tasks SET title=?, description=?, priority=?, category=?,
                                   due_date=?, completed=?, estimated_duration=?
                    WHERE id=?
                """, (
                    data['title'], data['description'], data['priority'],
                    data['category'], data['due_date'], data['completed'],
                    data['estimated_duration'], data['id']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to update task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete task {task_id}: {e}")
            return False 
   # Idea CRUD operations
    def create_idea(self, idea: Idea) -> bool:
        """Create a new idea in the database."""
        try:
            with self.get_cursor() as cursor:
                data = idea.to_dict()
                cursor.execute("""
                    INSERT INTO ideas (id, content, tags, created_at, updated_at, attachments)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['content'], data['tags'],
                    data['created_at'], data['updated_at'], data['attachments']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create idea: {e}")
            return False
    
    def get_idea(self, idea_id: str) -> Optional[Idea]:
        """Retrieve an idea by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
                row = cursor.fetchone()
                if row:
                    return Idea.from_dict(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Failed to get idea {idea_id}: {e}")
            return None
    
    def get_ideas(self, tag: str = None, search_term: str = None) -> List[Idea]:
        """Retrieve ideas with optional filtering."""
        try:
            with self.get_cursor() as cursor:
                query = "SELECT * FROM ideas WHERE 1=1"
                params = []
                
                if tag:
                    query += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
                
                if search_term:
                    query += " AND content LIKE ?"
                    params.append(f"%{search_term}%")
                
                query += " ORDER BY updated_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [Idea.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get ideas: {e}")
            return []
    
    def update_idea(self, idea: Idea) -> bool:
        """Update an existing idea."""
        try:
            with self.get_cursor() as cursor:
                data = idea.to_dict()
                cursor.execute("""
                    UPDATE ideas SET content=?, tags=?, updated_at=?, attachments=?
                    WHERE id=?
                """, (
                    data['content'], data['tags'], data['updated_at'],
                    data['attachments'], data['id']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to update idea: {e}")
            return False
    
    def delete_idea(self, idea_id: str) -> bool:
        """Delete an idea by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete idea {idea_id}: {e}")
            return False
    
    # Study Session CRUD operations
    def create_study_session(self, session: StudySession) -> bool:
        """Create a new study session in the database."""
        try:
            with self.get_cursor() as cursor:
                data = session.to_dict()
                cursor.execute("""
                    INSERT INTO study_sessions (id, subject, start_time, end_time,
                                              duration, tasks_completed, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['subject'], data['start_time'], data['end_time'],
                    data['duration'], data['tasks_completed'], data['notes']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create study session: {e}")
            return False
    
    def get_study_session(self, session_id: str) -> Optional[StudySession]:
        """Retrieve a study session by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,))
                row = cursor.fetchone()
                if row:
                    return StudySession.from_dict(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Failed to get study session {session_id}: {e}")
            return None
    
    def get_study_sessions(self, subject: str = None, date_from: datetime = None, 
                          date_to: datetime = None) -> List[StudySession]:
        """Retrieve study sessions with optional filtering."""
        try:
            with self.get_cursor() as cursor:
                query = "SELECT * FROM study_sessions WHERE 1=1"
                params = []
                
                if subject:
                    query += " AND subject = ?"
                    params.append(subject)
                
                if date_from:
                    query += " AND start_time >= ?"
                    params.append(date_from.isoformat())
                
                if date_to:
                    query += " AND start_time <= ?"
                    params.append(date_to.isoformat())
                
                query += " ORDER BY start_time DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [StudySession.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get study sessions: {e}")
            return []
    
    def update_study_session(self, session: StudySession) -> bool:
        """Update an existing study session."""
        try:
            with self.get_cursor() as cursor:
                data = session.to_dict()
                cursor.execute("""
                    UPDATE study_sessions SET subject=?, start_time=?, end_time=?,
                                            duration=?, tasks_completed=?, notes=?
                    WHERE id=?
                """, (
                    data['subject'], data['start_time'], data['end_time'],
                    data['duration'], data['tasks_completed'], data['notes'], data['id']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to update study session: {e}")
            return False
    
    def delete_study_session(self, session_id: str) -> bool:
        """Delete a study session by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM study_sessions WHERE id = ?", (session_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete study session {session_id}: {e}")
            return False
    
    # Smart Device CRUD operations
    def create_smart_device(self, device: SmartDevice) -> bool:
        """Create a new smart device in the database."""
        try:
            with self.get_cursor() as cursor:
                data = device.to_dict()
                cursor.execute("""
                    INSERT INTO smart_devices (id, name, device_type, platform, status,
                                             capabilities, room, is_online, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['name'], data['device_type'], data['platform'],
                    data['status'], data['capabilities'], data['room'],
                    data['is_online'], data['last_updated']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create smart device: {e}")
            return False
    
    def get_smart_device(self, device_id: str) -> Optional[SmartDevice]:
        """Retrieve a smart device by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM smart_devices WHERE id = ?", (device_id,))
                row = cursor.fetchone()
                if row:
                    return SmartDevice.from_dict(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Failed to get smart device {device_id}: {e}")
            return None
    
    def get_smart_devices(self, room: str = None, device_type: str = None, 
                         platform: str = None) -> List[SmartDevice]:
        """Retrieve smart devices with optional filtering."""
        try:
            with self.get_cursor() as cursor:
                query = "SELECT * FROM smart_devices WHERE 1=1"
                params = []
                
                if room:
                    query += " AND room = ?"
                    params.append(room)
                
                if device_type:
                    query += " AND device_type = ?"
                    params.append(device_type)
                
                if platform:
                    query += " AND platform = ?"
                    params.append(platform)
                
                query += " ORDER BY name"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [SmartDevice.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get smart devices: {e}")
            return []
    
    def update_smart_device(self, device: SmartDevice) -> bool:
        """Update an existing smart device."""
        try:
            with self.get_cursor() as cursor:
                data = device.to_dict()
                cursor.execute("""
                    UPDATE smart_devices SET name=?, device_type=?, platform=?, status=?,
                                           capabilities=?, room=?, is_online=?, last_updated=?
                    WHERE id=?
                """, (
                    data['name'], data['device_type'], data['platform'], data['status'],
                    data['capabilities'], data['room'], data['is_online'],
                    data['last_updated'], data['id']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to update smart device: {e}")
            return False
    
    def delete_smart_device(self, device_id: str) -> bool:
        """Delete a smart device by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM smart_devices WHERE id = ?", (device_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete smart device {device_id}: {e}")
            return False
    
    # Settings operations
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting value by key."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return row['value']
                return default
        except Exception as e:
            self.logger.error(f"Failed to get setting {key}: {e}")
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value, datetime.now().isoformat()))
            return True
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {e}")
            return False
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting by key."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete setting {key}: {e}")
            return False
    
    # Calendar Event CRUD operations
    def create_calendar_event(self, event: CalendarEvent) -> bool:
        """Create a new calendar event in the database."""
        try:
            with self.get_cursor() as cursor:
                data = event.to_dict()
                cursor.execute("""
                    INSERT INTO calendar_events (
                        id, title, description, location, start_time, end_time, all_day,
                        timezone, google_event_id, calendar_id, recurrence, reminders,
                        attendees, organizer, status, visibility, created_at, updated_at,
                        last_synced, is_local_only, needs_sync
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'], data['title'], data['description'], data['location'],
                    data['start_time'], data['end_time'], data['all_day'], data['timezone'],
                    data['google_event_id'], data['calendar_id'], data['recurrence'],
                    data['reminders'], data['attendees'], data['organizer'], data['status'],
                    data['visibility'], data['created_at'], data['updated_at'],
                    data['last_synced'], data['is_local_only'], data['needs_sync']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create calendar event: {e}")
            return False
    
    def get_calendar_event(self, event_id: str) -> Optional[CalendarEvent]:
        """Retrieve a calendar event by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
                row = cursor.fetchone()
                if row:
                    return CalendarEvent.from_dict(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Failed to get calendar event {event_id}: {e}")
            return None
    
    def get_calendar_event_by_google_id(self, google_event_id: str) -> Optional[CalendarEvent]:
        """Retrieve a calendar event by Google event ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM calendar_events WHERE google_event_id = ?", (google_event_id,))
                row = cursor.fetchone()
                if row:
                    return CalendarEvent.from_dict(dict(row))
            return None
        except Exception as e:
            self.logger.error(f"Failed to get calendar event by Google ID {google_event_id}: {e}")
            return None
    
    def get_calendar_events(self, calendar_id: str = None, date_from: datetime = None, 
                           date_to: datetime = None, needs_sync: bool = None) -> List[CalendarEvent]:
        """Retrieve calendar events with optional filtering."""
        try:
            with self.get_cursor() as cursor:
                query = "SELECT * FROM calendar_events WHERE 1=1"
                params = []
                
                if calendar_id:
                    query += " AND calendar_id = ?"
                    params.append(calendar_id)
                
                if date_from:
                    query += " AND start_time >= ?"
                    params.append(date_from.isoformat())
                
                if date_to:
                    query += " AND start_time <= ?"
                    params.append(date_to.isoformat())
                
                if needs_sync is not None:
                    query += " AND needs_sync = ?"
                    params.append(needs_sync)
                
                query += " ORDER BY start_time ASC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [CalendarEvent.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get calendar events: {e}")
            return []
    
    def update_calendar_event(self, event: CalendarEvent) -> bool:
        """Update an existing calendar event."""
        try:
            with self.get_cursor() as cursor:
                data = event.to_dict()
                cursor.execute("""
                    UPDATE calendar_events SET 
                        title=?, description=?, location=?, start_time=?, end_time=?, all_day=?,
                        timezone=?, google_event_id=?, calendar_id=?, recurrence=?, reminders=?,
                        attendees=?, organizer=?, status=?, visibility=?, updated_at=?,
                        last_synced=?, is_local_only=?, needs_sync=?
                    WHERE id=?
                """, (
                    data['title'], data['description'], data['location'], data['start_time'],
                    data['end_time'], data['all_day'], data['timezone'], data['google_event_id'],
                    data['calendar_id'], data['recurrence'], data['reminders'], data['attendees'],
                    data['organizer'], data['status'], data['visibility'], data['updated_at'],
                    data['last_synced'], data['is_local_only'], data['needs_sync'], data['id']
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to update calendar event: {e}")
            return False
    
    def delete_calendar_event(self, event_id: str) -> bool:
        """Delete a calendar event by ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete calendar event {event_id}: {e}")
            return False
    
    def get_events_for_date_range(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get all events within a specific date range."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM calendar_events 
                    WHERE (start_time >= ? AND start_time <= ?) 
                       OR (end_time >= ? AND end_time <= ?)
                       OR (start_time <= ? AND end_time >= ?)
                    ORDER BY start_time ASC
                """, (
                    start_date.isoformat(), end_date.isoformat(),
                    start_date.isoformat(), end_date.isoformat(),
                    start_date.isoformat(), end_date.isoformat()
                ))
                rows = cursor.fetchall()
                return [CalendarEvent.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get events for date range: {e}")
            return []
    
    def get_upcoming_events(self, limit: int = 10) -> List[CalendarEvent]:
        """Get upcoming events starting from now."""
        try:
            now = datetime.now()
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM calendar_events 
                    WHERE start_time >= ? 
                    ORDER BY start_time ASC 
                    LIMIT ?
                """, (now.isoformat(), limit))
                rows = cursor.fetchall()
                return [CalendarEvent.from_dict(dict(row)) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get upcoming events: {e}")
            return []
    
    def mark_events_for_sync(self, event_ids: List[str]) -> bool:
        """Mark multiple events as needing sync."""
        try:
            with self.get_cursor() as cursor:
                placeholders = ','.join(['?' for _ in event_ids])
                cursor.execute(f"""
                    UPDATE calendar_events 
                    SET needs_sync = TRUE, updated_at = ?
                    WHERE id IN ({placeholders})
                """, [datetime.now().isoformat()] + event_ids)
            return True
        except Exception as e:
            self.logger.error(f"Failed to mark events for sync: {e}")
            return False

    # Utility methods
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        try:
            with self.get_cursor() as cursor:
                stats = {}
                
                # Count records in each table
                for table in ['tasks', 'ideas', 'study_sessions', 'smart_devices', 'calendar_events', 'settings']:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[table] = cursor.fetchone()['count']
                
                return stats
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def close_connections(self):
        """Close all database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False