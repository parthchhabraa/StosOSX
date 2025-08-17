"""
Idea data model for StosOS idea board system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Idea:
    """
    Idea model for capturing and organizing creative thoughts.
    
    Attributes:
        id: Unique identifier for the idea
        content: Main idea content/description
        tags: List of tags for categorization
        created_at: When the idea was created
        updated_at: When the idea was last modified
        attachments: List of file paths for attachments
    """
    content: str
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate idea data after initialization."""
        if not self.content.strip():
            raise ValueError("Idea content cannot be empty")
        
        # Ensure tags are lowercase and unique
        self.tags = list(set(tag.lower().strip() for tag in self.tags if tag.strip()))
        
        # Validate attachment paths
        for attachment in self.attachments:
            if not isinstance(attachment, str) or not attachment.strip():
                raise ValueError("Attachment paths must be non-empty strings")
    
    def to_dict(self) -> dict:
        """Convert idea to dictionary for database storage."""
        return {
            'id': self.id,
            'content': self.content,
            'tags': ','.join(self.tags),  # Store as comma-separated string
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'attachments': ','.join(self.attachments)  # Store as comma-separated string
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Idea':
        """Create idea from dictionary data."""
        # Handle datetime fields
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle list fields stored as comma-separated strings
        if data.get('tags'):
            data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        else:
            data['tags'] = []
        
        if data.get('attachments'):
            data['attachments'] = [att.strip() for att in data['attachments'].split(',') if att.strip()]
        else:
            data['attachments'] = []
        
        return cls(**data)
    
    def add_tag(self, tag: str):
        """Add a tag to the idea."""
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the idea."""
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def add_attachment(self, file_path: str):
        """Add an attachment to the idea."""
        if file_path.strip() and file_path not in self.attachments:
            self.attachments.append(file_path.strip())
            self.updated_at = datetime.now()
    
    def remove_attachment(self, file_path: str):
        """Remove an attachment from the idea."""
        if file_path in self.attachments:
            self.attachments.remove(file_path)
            self.updated_at = datetime.now()
    
    def update_content(self, new_content: str):
        """Update the idea content."""
        if not new_content.strip():
            raise ValueError("Idea content cannot be empty")
        self.content = new_content.strip()
        self.updated_at = datetime.now()
    
    def has_tag(self, tag: str) -> bool:
        """Check if the idea has a specific tag."""
        return tag.lower().strip() in self.tags