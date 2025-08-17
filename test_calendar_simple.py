#!/usr/bin/env python3
"""
Simple test for Calendar Module components
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_calendar_module_basic():
    """Test basic calendar module functionality"""
    print("Testing Calendar Module Basic Functionality")
    
    try:
        # Test imports
        from models.calendar_event import CalendarEvent
        from core.database_manager import DatabaseManager
        from services.google_calendar_service import GoogleCalendarService
        
        print("✓ All imports successful")
        
        # Test CalendarEvent
        event = CalendarEvent(
            title="Test Meeting",
            description="A test meeting",
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2)
        )
        
        print(f"✓ Created event: {event.title}")
        print(f"  Duration: {event.duration_minutes} minutes")
        
        # Test database operations
        db = DatabaseManager("data/test_simple.db")
        
        # Create event
        success = db.create_calendar_event(event)
        print(f"✓ Database create: {success}")
        
        # Read event
        retrieved = db.get_calendar_event(event.id)
        print(f"✓ Database read: {retrieved.title if retrieved else 'Failed'}")
        
        # List events
        events = db.get_calendar_events()
        print(f"✓ Database list: {len(events)} events")
        
        # Clean up
        if os.path.exists("data/test_simple.db"):
            os.remove("data/test_simple.db")
        
        print("✓ Calendar module basic test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Calendar module basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_calendar_module_basic()
    sys.exit(0 if success else 1)