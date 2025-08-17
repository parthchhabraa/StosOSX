"""
Calendar Event Model for StosOS

Represents calendar events from Google Calendar API with local storage support.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4


@dataclass
class CalendarEvent:
    """
    Calendar event data model
    
    Represents a calendar event with all necessary fields for Google Calendar integration
    and local storage.
    """
    
    # Core fields
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    location: str = ""
    
    # Time fields
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: bool = False
    timezone: str = "UTC"
    
    # Google Calendar specific fields
    google_event_id: Optional[str] = None
    calendar_id: str = "primary"
    
    # Recurrence and reminders
    recurrence: List[str] = field(default_factory=list)
    reminders: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attendees and organizer
    attendees: List[Dict[str, Any]] = field(default_factory=list)
    organizer: Dict[str, Any] = field(default_factory=dict)
    
    # Status and visibility
    status: str = "confirmed"  # confirmed, tentative, cancelled
    visibility: str = "default"  # default, public, private
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_synced: Optional[datetime] = None
    
    # Local flags
    is_local_only: bool = False  # True if event exists only locally
    needs_sync: bool = False     # True if event needs to be synced to Google
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure end_time is set if not provided
        if self.start_time and not self.end_time:
            if self.all_day:
                self.end_time = self.start_time + timedelta(days=1)
            else:
                self.end_time = self.start_time + timedelta(hours=1)
    
    @property
    def duration_minutes(self) -> int:
        """Get event duration in minutes"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return 0
    
    @property
    def is_today(self) -> bool:
        """Check if event is today"""
        if not self.start_time:
            return False
        today = datetime.now().date()
        return self.start_time.date() == today
    
    @property
    def is_upcoming(self) -> bool:
        """Check if event is in the future"""
        if not self.start_time:
            return False
        return self.start_time > datetime.now()
    
    @property
    def is_past(self) -> bool:
        """Check if event is in the past"""
        if not self.end_time:
            return False
        return self.end_time < datetime.now()
    
    @property
    def is_current(self) -> bool:
        """Check if event is currently happening"""
        if not self.start_time or not self.end_time:
            return False
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    
    def get_time_until_start(self) -> Optional[timedelta]:
        """Get time until event starts"""
        if not self.start_time:
            return None
        now = datetime.now()
        if self.start_time > now:
            return self.start_time - now
        return None
    
    def get_display_time(self) -> str:
        """Get formatted display time for the event"""
        if not self.start_time:
            return "No time set"
        
        if self.all_day:
            if self.start_time.date() == self.end_time.date():
                return f"All day - {self.start_time.strftime('%B %d, %Y')}"
            else:
                return f"All day - {self.start_time.strftime('%B %d')} to {self.end_time.strftime('%B %d, %Y')}"
        else:
            start_str = self.start_time.strftime('%I:%M %p')
            end_str = self.end_time.strftime('%I:%M %p')
            date_str = self.start_time.strftime('%B %d, %Y')
            
            if self.start_time.date() == self.end_time.date():
                return f"{start_str} - {end_str}, {date_str}"
            else:
                end_date_str = self.end_time.strftime('%B %d, %Y')
                return f"{start_str} {date_str} - {end_str} {end_date_str}"
    
    def add_reminder(self, method: str = "popup", minutes_before: int = 15):
        """Add a reminder to the event"""
        reminder = {
            "method": method,  # popup, email, sms
            "minutes": minutes_before
        }
        if reminder not in self.reminders:
            self.reminders.append(reminder)
            self.needs_sync = True
    
    def remove_reminder(self, method: str, minutes_before: int):
        """Remove a specific reminder"""
        reminder = {"method": method, "minutes": minutes_before}
        if reminder in self.reminders:
            self.reminders.remove(reminder)
            self.needs_sync = True
    
    def add_attendee(self, email: str, name: str = "", response_status: str = "needsAction"):
        """Add an attendee to the event"""
        attendee = {
            "email": email,
            "displayName": name or email,
            "responseStatus": response_status  # needsAction, declined, tentative, accepted
        }
        
        # Check if attendee already exists
        for existing in self.attendees:
            if existing.get("email") == email:
                existing.update(attendee)
                self.needs_sync = True
                return
        
        self.attendees.append(attendee)
        self.needs_sync = True
    
    def remove_attendee(self, email: str):
        """Remove an attendee from the event"""
        self.attendees = [a for a in self.attendees if a.get("email") != email]
        self.needs_sync = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for database storage"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "all_day": self.all_day,
            "timezone": self.timezone,
            "google_event_id": self.google_event_id,
            "calendar_id": self.calendar_id,
            "recurrence": json.dumps(self.recurrence),
            "reminders": json.dumps(self.reminders),
            "attendees": json.dumps(self.attendees),
            "organizer": json.dumps(self.organizer),
            "status": self.status,
            "visibility": self.visibility,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_synced": self.last_synced.isoformat() if self.last_synced else None,
            "is_local_only": self.is_local_only,
            "needs_sync": self.needs_sync
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalendarEvent':
        """Create event from dictionary (database row)"""
        # Parse datetime fields
        start_time = datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None
        end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
        last_synced = datetime.fromisoformat(data["last_synced"]) if data.get("last_synced") else None
        
        # Parse JSON fields
        recurrence = json.loads(data.get("recurrence", "[]"))
        reminders = json.loads(data.get("reminders", "[]"))
        attendees = json.loads(data.get("attendees", "[]"))
        organizer = json.loads(data.get("organizer", "{}"))
        
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            location=data.get("location", ""),
            start_time=start_time,
            end_time=end_time,
            all_day=data.get("all_day", False),
            timezone=data.get("timezone", "UTC"),
            google_event_id=data.get("google_event_id"),
            calendar_id=data.get("calendar_id", "primary"),
            recurrence=recurrence,
            reminders=reminders,
            attendees=attendees,
            organizer=organizer,
            status=data.get("status", "confirmed"),
            visibility=data.get("visibility", "default"),
            created_at=created_at,
            updated_at=updated_at,
            last_synced=last_synced,
            is_local_only=data.get("is_local_only", False),
            needs_sync=data.get("needs_sync", False)
        )
    
    @classmethod
    def from_google_event(cls, google_event: Dict[str, Any], calendar_id: str = "primary") -> 'CalendarEvent':
        """Create event from Google Calendar API response"""
        # Parse start and end times
        start_time = None
        end_time = None
        all_day = False
        
        if "start" in google_event:
            if "dateTime" in google_event["start"]:
                start_time = datetime.fromisoformat(google_event["start"]["dateTime"].replace('Z', '+00:00'))
            elif "date" in google_event["start"]:
                start_time = datetime.fromisoformat(google_event["start"]["date"])
                all_day = True
        
        if "end" in google_event:
            if "dateTime" in google_event["end"]:
                end_time = datetime.fromisoformat(google_event["end"]["dateTime"].replace('Z', '+00:00'))
            elif "date" in google_event["end"]:
                end_time = datetime.fromisoformat(google_event["end"]["date"])
        
        # Parse reminders
        reminders = []
        if "reminders" in google_event and google_event["reminders"].get("useDefault"):
            reminders.append({"method": "popup", "minutes": 15})
        elif "reminders" in google_event and "overrides" in google_event["reminders"]:
            for override in google_event["reminders"]["overrides"]:
                reminders.append({
                    "method": override.get("method", "popup"),
                    "minutes": override.get("minutes", 15)
                })
        
        # Parse attendees
        attendees = []
        if "attendees" in google_event:
            for attendee in google_event["attendees"]:
                attendees.append({
                    "email": attendee.get("email", ""),
                    "displayName": attendee.get("displayName", ""),
                    "responseStatus": attendee.get("responseStatus", "needsAction")
                })
        
        # Parse organizer
        organizer = {}
        if "organizer" in google_event:
            organizer = {
                "email": google_event["organizer"].get("email", ""),
                "displayName": google_event["organizer"].get("displayName", "")
            }
        
        # Parse recurrence
        recurrence = google_event.get("recurrence", [])
        
        return cls(
            id=str(uuid4()),  # Generate new local ID
            title=google_event.get("summary", "Untitled Event"),
            description=google_event.get("description", ""),
            location=google_event.get("location", ""),
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
            timezone=google_event.get("start", {}).get("timeZone", "UTC"),
            google_event_id=google_event.get("id"),
            calendar_id=calendar_id,
            recurrence=recurrence,
            reminders=reminders,
            attendees=attendees,
            organizer=organizer,
            status=google_event.get("status", "confirmed"),
            visibility=google_event.get("visibility", "default"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_synced=datetime.now(),
            is_local_only=False,
            needs_sync=False
        )
    
    def to_google_event(self) -> Dict[str, Any]:
        """Convert event to Google Calendar API format"""
        google_event = {
            "summary": self.title,
            "description": self.description,
            "location": self.location,
            "status": self.status,
            "visibility": self.visibility
        }
        
        # Add time information
        if self.start_time:
            if self.all_day:
                google_event["start"] = {"date": self.start_time.date().isoformat()}
                google_event["end"] = {"date": self.end_time.date().isoformat()}
            else:
                google_event["start"] = {
                    "dateTime": self.start_time.isoformat(),
                    "timeZone": self.timezone
                }
                google_event["end"] = {
                    "dateTime": self.end_time.isoformat(),
                    "timeZone": self.timezone
                }
        
        # Add reminders
        if self.reminders:
            google_event["reminders"] = {
                "useDefault": False,
                "overrides": [
                    {"method": r["method"], "minutes": r["minutes"]}
                    for r in self.reminders
                ]
            }
        
        # Add attendees
        if self.attendees:
            google_event["attendees"] = self.attendees
        
        # Add recurrence
        if self.recurrence:
            google_event["recurrence"] = self.recurrence
        
        # Add Google event ID if updating existing event
        if self.google_event_id:
            google_event["id"] = self.google_event_id
        
        return google_event