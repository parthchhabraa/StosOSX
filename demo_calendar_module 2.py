#!/usr/bin/env python3
"""
Demo script for Calendar Module

Demonstrates calendar integration functionality including:
- Creating calendar events
- Database storage and retrieval
- Different event types (all-day, timed, recurring)
- Google Calendar integration setup
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.calendar_event import CalendarEvent
from core.database_manager import DatabaseManager
from services.google_calendar_service import GoogleCalendarService

def demo_calendar_events():
    """Demonstrate calendar event creation and management"""
    print("\n🗓️  Calendar Events Demo")
    print("=" * 50)
    
    # Initialize database
    db = DatabaseManager("data/demo_calendar.db")
    
    # Create sample events
    events = []
    
    # 1. Regular meeting
    meeting = CalendarEvent(
        title="Team Standup",
        description="Daily team synchronization meeting",
        location="Conference Room A",
        start_time=datetime.now() + timedelta(hours=1),
        end_time=datetime.now() + timedelta(hours=1, minutes=30)
    )
    meeting.add_reminder("popup", 15)
    meeting.add_reminder("email", 60)
    events.append(meeting)
    
    # 2. All-day event
    birthday = CalendarEvent(
        title="John's Birthday",
        description="Remember to wish John a happy birthday!",
        start_time=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        all_day=True
    )
    events.append(birthday)
    
    # 3. Study session
    study = CalendarEvent(
        title="Physics Study Session",
        description="Review thermodynamics and wave mechanics",
        location="Library - Study Room 3",
        start_time=datetime.now() + timedelta(days=1, hours=14),
        end_time=datetime.now() + timedelta(days=1, hours=16)
    )
    study.add_reminder("popup", 30)
    events.append(study)
    
    # 4. Exam
    exam = CalendarEvent(
        title="IIT-JEE Mock Test",
        description="Full-length practice test - Physics, Chemistry, Mathematics",
        location="Test Center",
        start_time=datetime.now() + timedelta(days=7, hours=9),
        end_time=datetime.now() + timedelta(days=7, hours=12)
    )
    exam.add_reminder("popup", 60)
    exam.add_reminder("email", 1440)  # 24 hours
    events.append(exam)
    
    # 5. Project deadline
    deadline = CalendarEvent(
        title="Science Project Submission",
        description="Submit renewable energy research project",
        start_time=datetime.now() + timedelta(days=14, hours=23, minutes=59),
        end_time=datetime.now() + timedelta(days=14, hours=23, minutes=59),
        all_day=False
    )
    deadline.add_reminder("popup", 60)
    deadline.add_reminder("popup", 1440)
    deadline.add_reminder("email", 10080)  # 1 week
    events.append(deadline)
    
    # Save events to database
    print("\n📝 Creating Events:")
    for event in events:
        success = db.create_calendar_event(event)
        status = "✓" if success else "✗"
        print(f"{status} {event.title}")
        print(f"   📅 {event.get_display_time()}")
        if event.location:
            print(f"   📍 {event.location}")
        if event.reminders:
            reminder_text = ", ".join([f"{r['minutes']}min {r['method']}" for r in event.reminders])
            print(f"   🔔 Reminders: {reminder_text}")
        print()
    
    return events

def demo_event_queries():
    """Demonstrate different event query capabilities"""
    print("\n🔍 Event Queries Demo")
    print("=" * 50)
    
    db = DatabaseManager("data/demo_calendar.db")
    
    # Get all events
    all_events = db.get_calendar_events()
    print(f"📊 Total events in database: {len(all_events)}")
    
    # Get upcoming events
    upcoming = db.get_upcoming_events(3)
    print(f"\n⏰ Next 3 upcoming events:")
    for i, event in enumerate(upcoming, 1):
        time_until = event.get_time_until_start()
        if time_until:
            if time_until.days > 0:
                time_str = f"in {time_until.days} days"
            elif time_until.seconds > 3600:
                hours = time_until.seconds // 3600
                time_str = f"in {hours} hours"
            else:
                minutes = time_until.seconds // 60
                time_str = f"in {minutes} minutes"
        else:
            time_str = "now or past"
        
        print(f"   {i}. {event.title} - {time_str}")
    
    # Get events for next week
    next_week_start = datetime.now()
    next_week_end = datetime.now() + timedelta(days=7)
    week_events = db.get_events_for_date_range(next_week_start, next_week_end)
    print(f"\n📅 Events in next 7 days: {len(week_events)}")
    for event in week_events:
        print(f"   • {event.title} - {event.start_time.strftime('%m/%d %I:%M %p') if event.start_time else 'No time'}")
    
    # Get events needing sync
    sync_events = db.get_calendar_events(needs_sync=True)
    print(f"\n🔄 Events needing sync: {len(sync_events)}")

def demo_google_calendar_setup():
    """Demonstrate Google Calendar integration setup"""
    print("\n🔗 Google Calendar Integration Demo")
    print("=" * 50)
    
    # Initialize Google Calendar service
    service = GoogleCalendarService()
    
    print("📋 Google Calendar Integration Status:")
    print(f"   • Service initialized: ✓")
    print(f"   • Authenticated: {'✓' if service.is_authenticated() else '✗'}")
    print(f"   • Connection test: {'✓' if service.test_connection() else '✗'}")
    
    if not service.is_authenticated():
        print("\n⚠️  Google Calendar Authentication Required")
        print("   To enable Google Calendar sync:")
        print("   1. Go to Google Cloud Console")
        print("   2. Create a new project or select existing")
        print("   3. Enable Google Calendar API")
        print("   4. Create OAuth 2.0 credentials")
        print("   5. Download credentials JSON file")
        print("   6. Place file at: config/google_credentials.json")
        print("   7. Run authentication flow")
    else:
        print("\n✓ Google Calendar is ready for synchronization")
        
        # Demonstrate calendar listing
        calendars = service.get_calendars()
        print(f"\n📚 Available calendars: {len(calendars)}")
        for cal in calendars[:3]:  # Show first 3
            print(f"   • {cal.get('summary', 'Unnamed')} ({cal.get('id', 'no-id')})")

def demo_event_timeline():
    """Demonstrate timeline view with events and tasks"""
    print("\n📈 Timeline View Demo")
    print("=" * 50)
    
    db = DatabaseManager("data/demo_calendar.db")
    
    # Get events and tasks for timeline
    events = db.get_upcoming_events(10)
    
    # Simulate some tasks (in real implementation, these would come from task manager)
    from models.task import Task, Priority
    
    sample_tasks = [
        Task(
            title="Complete Physics Assignment",
            description="Solve problems on electromagnetic induction",
            priority=Priority.HIGH,
            category="Physics",
            due_date=datetime.now() + timedelta(days=2, hours=18)
        ),
        Task(
            title="Review Chemistry Notes",
            description="Go through organic chemistry reactions",
            priority=Priority.MEDIUM,
            category="Chemistry", 
            due_date=datetime.now() + timedelta(days=5, hours=20)
        )
    ]
    
    # Combine and sort timeline items
    timeline_items = []
    
    for event in events:
        if event.start_time:
            timeline_items.append({
                'type': 'event',
                'title': event.title,
                'datetime': event.start_time,
                'description': event.description or event.location or ""
            })
    
    for task in sample_tasks:
        if task.due_date:
            timeline_items.append({
                'type': 'task',
                'title': task.title,
                'datetime': task.due_date,
                'description': f"{task.category} - {task.priority.value} priority"
            })
    
    # Sort by datetime
    timeline_items.sort(key=lambda x: x['datetime'])
    
    print("📋 Unified Timeline (Events + Tasks):")
    current_date = None
    
    for item in timeline_items[:8]:  # Show first 8 items
        item_date = item['datetime'].date()
        
        # Print date header if new date
        if current_date != item_date:
            current_date = item_date
            print(f"\n   📅 {item_date.strftime('%A, %B %d, %Y')}")
        
        # Print item
        icon = "🗓️" if item['type'] == 'event' else "📋"
        time_str = item['datetime'].strftime('%I:%M %p')
        print(f"      {icon} {time_str} - {item['title']}")
        if item['description']:
            print(f"         {item['description'][:60]}{'...' if len(item['description']) > 60 else ''}")

def demo_notifications():
    """Demonstrate notification system for events"""
    print("\n🔔 Notifications Demo")
    print("=" * 50)
    
    db = DatabaseManager("data/demo_calendar.db")
    upcoming_events = db.get_upcoming_events(5)
    
    print("⏰ Upcoming Event Notifications:")
    
    for event in upcoming_events:
        if not event.reminders:
            continue
            
        time_until = event.get_time_until_start()
        if not time_until:
            continue
        
        total_minutes = int(time_until.total_seconds() / 60)
        
        print(f"\n   📅 {event.title}")
        print(f"      Starts: {event.start_time.strftime('%I:%M %p on %B %d')}")
        
        for reminder in event.reminders:
            reminder_minutes = reminder['minutes']
            if total_minutes <= reminder_minutes:
                method_icon = "🔔" if reminder['method'] == 'popup' else "📧"
                print(f"      {method_icon} {reminder['method'].title()} reminder triggered!")
            else:
                time_to_reminder = total_minutes - reminder_minutes
                print(f"      ⏳ {reminder['method'].title()} reminder in {time_to_reminder} minutes")

def main():
    """Run calendar module demo"""
    print("🗓️  StosOS Calendar Module Demo")
    print("=" * 60)
    print("Demonstrating calendar integration functionality")
    
    try:
        # Clean up any existing demo database
        if os.path.exists("data/demo_calendar.db"):
            os.remove("data/demo_calendar.db")
        
        # Run demos
        events = demo_calendar_events()
        demo_event_queries()
        demo_google_calendar_setup()
        demo_event_timeline()
        demo_notifications()
        
        print("\n" + "=" * 60)
        print("✅ Calendar Module Demo Completed Successfully!")
        print("\nKey Features Demonstrated:")
        print("• ✓ Calendar event creation and management")
        print("• ✓ Database storage and querying")
        print("• ✓ Multiple event types (timed, all-day)")
        print("• ✓ Reminder system")
        print("• ✓ Google Calendar integration setup")
        print("• ✓ Timeline view with events and tasks")
        print("• ✓ Notification system")
        
        print(f"\n📊 Demo Statistics:")
        print(f"   • Events created: {len(events)}")
        print(f"   • Database operations: ✓")
        print(f"   • Google Calendar ready: {'✓' if os.path.exists('config/google_credentials.json') else 'Setup required'}")
        
        # Clean up demo database
        if os.path.exists("data/demo_calendar.db"):
            os.remove("data/demo_calendar.db")
            print("   • Demo cleanup: ✓")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())