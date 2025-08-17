"""
Task data model for StosOS task management system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class Priority(Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Task:
    """
    Task model for managing study tasks and assignments.
    
    Attributes:
        id: Unique identifier for the task
        title: Task title/name
        description: Detailed task description
        priority: Task priority level (HIGH, MEDIUM, LOW)
        category: Task category (e.g., Physics, Chemistry, Math)
        due_date: When the task is due
        created_at: When the task was created
        completed: Whether the task is completed
        estimated_duration: Estimated time to complete in minutes
    """
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    category: str = "General"
    due_date: Optional[datetime] = None
    completed: bool = False
    estimated_duration: int = 30  # minutes
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")
        
        if self.estimated_duration <= 0:
            raise ValueError("Estimated duration must be positive")
        
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for database storage."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'category': self.category,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'completed': self.completed,
            'estimated_duration': self.estimated_duration
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary data."""
        # Handle datetime fields
        if data.get('due_date'):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Handle priority enum
        if data.get('priority'):
            data['priority'] = Priority(data['priority'])
        
        return cls(**data)
    
    def mark_completed(self):
        """Mark the task as completed."""
        self.completed = True
    
    def mark_incomplete(self):
        """Mark the task as incomplete."""
        self.completed = False
    
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.due_date or self.completed:
            return False
        return datetime.now() > self.due_date