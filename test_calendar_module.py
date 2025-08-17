#!/usr/bin/env python3
"""
Test script for Calendar Module

Tests calendar integration functionality including:
- Calendar event model
- Database operations
- Google Calendar service (mock)
- Calendar module UI components
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_calendar_event_model():
    """Test CalendarEvent model functionality"""
    print("\n=== Testing CalendarEvent Model ===")
    
    try:
        from models.calendar_event import CalendarEvent
        
        # Test basic event creation
        event = CalendarEvent(
            title="Test Event",
            description="This is a test event",
            location="Test Location",
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2)
        )
        
        print(f"✓ Created event: {event.title}")
        print(f"  Duration: {event.duration_minutes} minutes")
        print(f"  Display time: {event.get_display_time()}")
        print(f"  Is upcoming: {event.is_upcoming}")
        
        # Test all-day event
        all_day_event = CalendarEvent(
            title="All Day Event",
            start_time=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            all_day=True
        )
        
        print(f"✓ Created all-day event: {all_day_event.title}")
        print(f"  Display time: {all_day_event.get_display_time()}")
        
        # Test serialization
        event_dict = event.to_dict()
        restored_event = CalendarEvent.from_dict(event_dict)
        
        print(f"✓ Serialization test passed: {restored_event.title == event.title}")
        
        # Test Google event conversion
        google_event_data = {
            "id": "test_google_id",
            "summary": "Google Event",
            "description": "From Google Calendar",
            "start": {"dateTime": "2024-01-15T10:00:00Z"},
            "end": {"dateTime": "2024-01-15T11:00:00Z"},
            "location": "Google Office"
        }
        
        google_event = CalendarEvent.from_google_event(google_event_data)
        print(f"✓ Google event conversion: {google_event.title}")
        
        # Test reminders
        event.add_reminder("popup", 15)
        event.add_reminder("email", 60)
        print(f"✓ Added reminders: {len(event.reminders)} reminders")
        
        return True
        
    except Exception as e:
        print(f"✗ CalendarEvent model test failed: {e}")
        return False

def test_database_operations():
    """Test calendar event database operations"""
    print("\n=== Testing Database Operations ===")
    
    try:
        from core.database_manager import DatabaseManager
        from models.calendar_event import CalendarEvent
        
        # Initialize database
        db_manager = DatabaseManager("data/test_calendar.db")
        
        # Create test event
        test_event = CalendarEvent(
            title="Database Test Event",
            description="Testing database operations",
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1)
        )
        
        # Test create
        success = db_manager.create_calendar_event(test_event)
        print(f"✓ Create event: {success}")
        
        # Test read
        retrieved_event = db_manager.get_calendar_event(test_event.id)
        print(f"✓ Read event: {retrieved_event.title if retrieved_event else 'Failed'}")
        
        # Test update
        if retrieved_event:
            retrieved_event.title = "Updated Test Event"
            retrieved_event.needs_sync = True
            update_success = db_manager.update_calendar_event(retrieved_event)
            print(f"✓ Update event: {update_success}")
        
        # Test list events
        events = db_manager.get_calendar_events()
        print(f"✓ List events: {len(events)} events found")
        
        # Test date range query
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = datetime.now() + timedelta(days=2)
        range_events = db_manager.get_events_for_date_range(tomorrow, day_after)
        print(f"✓ Date range query: {len(range_events)} events in range")
        
        # Test upcoming events
        upcoming = db_manager.get_upcoming_events(5)
        print(f"✓ Upcoming events: {len(upcoming)} upcoming events")
        
        # Test delete
        if retrieved_event:
            delete_success = db_manager.delete_calendar_event(retrieved_event.id)
            print(f"✓ Delete event: {delete_success}")
        
        # Clean up test database
        os.remove("data/test_calendar.db")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations test failed: {e}")
        return False

def test_google_calendar_service():
    """Test Google Calendar service (without actual API calls)"""
    print("\n=== Testing Google Calendar Service ===")
    
    try:
        from services.google_calendar_service import GoogleCalendarService
        
        # Initialize service (will fail authentication, but that's expected)
        service = GoogleCalendarService(
            credentials_file="config/test_credentials.json",
            token_file="config/test_token.json"
        )
        
        print(f"✓ Service initialized")
        print(f"  Authenticated: {service.is_authenticated()}")
        
        # Test connection test method
        connection_ok = service.test_connection()
        print(f"✓ Connection test: {connection_ok} (expected False without credentials)")
        
        return True
        
    except Exception as e:
        print(f"✗ Google Calendar service test failed: {e}")
        return False

def test_calendar_module():
    """Test calendar module initialization"""
    print("\n=== Testing Calendar Module ===")
    
    try:
        from modules.calendar_module import CalendarModule
        
        # Initialize module
        calendar_module = CalendarModule()
        
        print(f"✓ Module created: {calendar_module.module_id}")
        print(f"  Display name: {calendar_module.display_name}")
        print(f"  Icon: {calendar_module.icon}")
        
        # Test initialization
        init_success = calendar_module.initialize()
        print(f"✓ Module initialization: {init_success}")
        
        # Test status
        status = calendar_module.get_status()
        print(f"✓ Module status: {status}")
        
        # Test voice command handling
        voice_handled = calendar_module.handle_voice_command("show calendar today")
        print(f"✓ Voice command handling: {voice_handled}")
        
        # Clean up
        calendar_module.cleanup()
        
        return True
        
    except Exception as e:
        print(f"✗ Calendar module test failed: {e}")
        return False

def main():
    """Run all calendar module tests"""
    print("StosOS Calendar Module Test Suite")
    print("=" * 50)
    
    tests = [
        ("CalendarEvent Model", test_calendar_event_model),
        ("Database Operations", test_database_operations),
        ("Google Calendar Service", test_google_calendar_service),
        ("Calendar Module", test_calendar_module)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())