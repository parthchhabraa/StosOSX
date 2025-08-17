"""
Study session data model for StosOS study tracking system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
import uuid


@dataclass
class StudySession:
    """
    Study session model for tracking study time and progress.
    
    Attributes:
        id: Unique identifier for the session
        subject: Subject being studied (e.g., Physics, Chemistry, Math)
        start_time: When the study session started
        end_time: When the study session ended (None if ongoing)
        duration: Session duration in minutes
        tasks_completed: List of task IDs completed during session
        notes: Additional notes about the session
    """
    subject: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    tasks_completed: List[str] = field(default_factory=list)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate study session data after initialization."""
        if not self.subject.strip():
            raise ValueError("Subject cannot be empty")
        
        if self.end_time and self.end_time < self.start_time:
            raise ValueError("End time cannot be before start time")
    
    @property
    def duration(self) -> int:
        """Calculate session duration in minutes."""
        if not self.end_time:
            # Session is ongoing
            return int((datetime.now() - self.start_time).total_seconds() / 60)
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @property
    def is_active(self) -> bool:
        """Check if the study session is currently active."""
        return self.end_time is None
    
    def to_dict(self) -> dict:
        """Convert study session to dictionary for database storage."""
        return {
            'id': self.id,
            'subject': self.subject,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'tasks_completed': ','.join(self.tasks_completed),  # Store as comma-separated string
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudySession':
        """Create study session from dictionary data."""
        # Handle datetime fields
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        
        # Handle tasks_completed list
        if data.get('tasks_completed'):
            data['tasks_completed'] = [task.strip() for task in data['tasks_completed'].split(',') if task.strip()]
        else:
            data['tasks_completed'] = []
        
        # Remove duration from data as it's a calculated property
        data.pop('duration', None)
        
        return cls(**data)
    
    def end_session(self, notes: str = ""):
        """End the study session."""
        if self.end_time:
            raise ValueError("Session is already ended")
        
        self.end_time = datetime.now()
        if notes:
            self.notes = notes
    
    def add_completed_task(self, task_id: str):
        """Add a completed task to the session."""
        if task_id and task_id not in self.tasks_completed:
            self.tasks_completed.append(task_id)
    
    def remove_completed_task(self, task_id: str):
        """Remove a completed task from the session."""
        if task_id in self.tasks_completed:
            self.tasks_completed.remove(task_id)
    
    def extend_session(self, minutes: int):
        """Extend an active session by specified minutes."""
        if not self.is_active:
            raise ValueError("Cannot extend an ended session")
        
        # This is conceptual - in practice, the user would just continue studying
        # and the duration would be calculated based on the actual end time
        pass
    
    def get_formatted_duration(self) -> str:
        """Get formatted duration string (e.g., '1h 30m')."""
        total_minutes = self.duration
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"