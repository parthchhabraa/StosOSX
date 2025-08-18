#!/usr/bin/env python3
"""
Verification script for StudyTracker module.

Demonstrates the study tracking functionality and creates sample data.
"""

import sys
import os
from datetime import datetime, timedelta, date
from pathlib import Path

# Add the parent directory to the path so we can import stosos modules
sys.path.insert(0, str(Path(__file__).parent))

from core.database_manager import DatabaseManager
from models.study_session import StudySession


def create_sample_study_data():
    """Create comprehensive sample study data"""
    print("Creating sample study data...")
    
    db_manager = DatabaseManager()
    sessions = []
    
    # Create sessions for the past 2 weeks to show streak and statistics
    base_date = datetime.now()
    
    subjects = ["Physics", "Mathematics", "Chemistry", "Biology"]
    
    for days_ago in range(14, 0, -1):  # 14 days ago to yesterday
        session_date = base_date - timedelta(days=days_ago)
        
        # Skip some days to create realistic gaps
        if days_ago in [13, 10, 6]:  # Skip these days
            continue
        
        # Create 1-3 sessions per day
        num_sessions = min(3, max(1, (15 - days_ago) // 4))  # More sessions as we get closer to today
        
        for session_num in range(num_sessions):
            subject = subjects[session_num % len(subjects)]
            
            # Vary session times and durations
            start_hour = 9 + (session_num * 3) + (days_ago % 2)  # Vary start times
            duration_minutes = 45 + (session_num * 15) + (days_ago % 30)  # 45-120 minutes
            
            start_time = session_date.replace(
                hour=start_hour, 
                minute=0, 
                second=0, 
                microsecond=0
            )
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            session = StudySession(
                subject=subject,
                start_time=start_time,
                end_time=end_time,
                notes=f"Day {15-days_ago} study session - {subject} concepts and practice"
            )
            
            sessions.append(session)
    
    # Add today's sessions (active learning)
    today = base_date
    
    # Morning Physics session
    physics_session = StudySession(
        subject="Physics",
        start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
        end_time=today.replace(hour=10, minute=45, second=0, microsecond=0),
        notes="Quantum mechanics - wave-particle duality and uncertainty principle"
    )
    sessions.append(physics_session)
    
    # Afternoon Math session
    math_session = StudySession(
        subject="Mathematics",
        start_time=today.replace(hour=14, minute=30, second=0, microsecond=0),
        end_time=today.replace(hour=16, minute=0, second=0, microsecond=0),
        notes="Calculus - integration techniques and applications"
    )
    sessions.append(math_session)
    
    # Save all sessions to database
    saved_count = 0
    for session in sessions:
        try:
            if db_manager.create_study_session(session):
                saved_count += 1
        except Exception as e:
            print(f"Error saving session: {e}")
    
    print(f"✓ Created {saved_count} sample study sessions")
    return sessions


def demonstrate_statistics():
    """Demonstrate statistics calculation"""
    print("\n=== Study Statistics Demo ===")
    
    db_manager = DatabaseManager()
    sessions = db_manager.get_study_sessions()
    
    if not sessions:
        print("No study sessions found. Creating sample data...")
        sessions = create_sample_study_data()
    
    # Import the stats class from our core test
    from test_study_tracker_core import StudyStats
    
    stats = StudyStats(sessions)
    
    # Today's statistics
    print("\n📊 Today's Study Statistics:")
    daily_stats = stats.get_daily_stats()
    print(f"  • Total study time: {daily_stats['total_minutes']} minutes ({daily_stats['total_minutes']//60}h {daily_stats['total_minutes']%60}m)")
    print(f"  • Number of sessions: {daily_stats['session_count']}")
    print(f"  • Subjects studied: {len(daily_stats['subject_breakdown'])}")
    
    if daily_stats['subject_breakdown']:
        print("  • Subject breakdown:")
        for subject, minutes in daily_stats['subject_breakdown'].items():
            hours = minutes // 60
            mins = minutes % 60
            print(f"    - {subject}: {hours}h {mins}m")
    
    # Weekly statistics
    print("\n📈 This Week's Study Statistics:")
    weekly_stats = stats.get_weekly_stats()
    print(f"  • Total study time: {weekly_stats['total_minutes']} minutes ({weekly_stats['total_minutes']//60}h {weekly_stats['total_minutes']%60}m)")
    print(f"  • Number of sessions: {weekly_stats['session_count']}")
    print(f"  • Daily average: {weekly_stats['average_daily_minutes']:.1f} minutes")
    
    if weekly_stats['subject_breakdown']:
        print("  • Subject breakdown:")
        for subject, minutes in weekly_stats['subject_breakdown'].items():
            hours = minutes // 60
            mins = minutes % 60
            percentage = (minutes / weekly_stats['total_minutes']) * 100 if weekly_stats['total_minutes'] > 0 else 0
            print(f"    - {subject}: {hours}h {mins}m ({percentage:.1f}%)")
    
    # Study streak
    print(f"\n🔥 Current Study Streak: {stats.get_streak_count()} days")
    
    # Subject-specific progress
    print("\n📚 Subject Progress (Last 7 Days):")
    subjects = set(session.subject for session in sessions)
    for subject in sorted(subjects):
        progress = stats.get_subject_progress(subject, days=7)
        if progress['total_minutes'] > 0:
            hours = progress['total_minutes'] // 60
            mins = progress['total_minutes'] % 60
            print(f"  • {subject}: {hours}h {mins}m across {progress['session_count']} sessions")
            print(f"    Average: {progress['average_daily_minutes']:.1f} minutes/day")


def demonstrate_pomodoro():
    """Demonstrate Pomodoro timer functionality"""
    print("\n=== Pomodoro Timer Demo ===")
    
    from test_study_tracker_core import PomodoroTimer
    
    def on_tick(remaining_time, is_work_session):
        session_type = "🍅 Work" if is_work_session else "☕ Break"
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        print(f"  {session_type}: {minutes:02d}:{seconds:02d} remaining")
    
    def on_complete(next_is_work, session_count):
        if next_is_work:
            print(f"  ✅ Break completed! Ready for work session #{session_count + 1}")
        else:
            session_type = "Long break" if session_count % 4 == 0 else "Short break"
            print(f"  ✅ Work session #{session_count} completed! Time for {session_type}")
    
    timer = PomodoroTimer(on_tick=on_tick, on_complete=on_complete)
    
    print(f"🍅 Pomodoro Timer initialized:")
    print(f"  • Work duration: {timer.work_duration // 60} minutes")
    print(f"  • Short break: {timer.short_break_duration // 60} minutes")
    print(f"  • Long break: {timer.long_break_duration // 60} minutes")
    print(f"  • Current time: {timer.get_formatted_time()}")
    print(f"  • Progress: {timer.get_progress():.1%}")
    
    # Simulate timer progression
    print("\n⏱️  Simulating timer progression:")
    
    # Simulate work session
    print("  Starting work session...")
    timer.start()
    
    # Simulate 10 minutes of work
    timer.current_time = timer.work_duration - (10 * 60)
    on_tick(timer.current_time, timer.is_work_session)
    print(f"  Progress after 10 minutes: {timer.get_progress():.1%}")
    
    # Simulate completion
    timer.current_time = 0
    timer._complete_session()
    
    print(f"  After completion: {timer.get_formatted_time()} ({timer.is_work_session and 'Work' or 'Break'})")


def demonstrate_goals():
    """Demonstrate study goals functionality"""
    print("\n=== Study Goals Demo ===")
    
    from test_study_tracker_core import StudyGoal, StudyStats
    
    # Create sample goals
    goals = [
        StudyGoal("Physics", 120),      # 2 hours daily
        StudyGoal("Mathematics", 90),   # 1.5 hours daily
        StudyGoal("Chemistry", 60),     # 1 hour daily
        StudyGoal("Biology", 45)        # 45 minutes daily
    ]
    
    print("🎯 Study Goals:")
    for goal in goals:
        print(f"  • {goal.subject}: {goal.daily_minutes} minutes/day ({goal.weekly_minutes} minutes/week)")
    
    # Check progress against goals
    db_manager = DatabaseManager()
    sessions = db_manager.get_study_sessions()
    
    if sessions:
        stats = StudyStats(sessions)
        daily_stats = stats.get_daily_stats()
        
        print(f"\n📊 Today's Progress vs Goals:")
        for goal in goals:
            actual_minutes = daily_stats['subject_breakdown'].get(goal.subject, 0)
            progress_percentage = (actual_minutes / goal.daily_minutes) * 100
            
            # Progress indicator
            if progress_percentage >= 100:
                status = "🎉 Goal achieved!"
            elif progress_percentage >= 80:
                status = "🔥 Almost there!"
            elif progress_percentage >= 50:
                status = "📈 Good progress"
            else:
                status = "⏰ Needs attention"
            
            hours = actual_minutes // 60
            mins = actual_minutes % 60
            target_hours = goal.daily_minutes // 60
            target_mins = goal.daily_minutes % 60
            
            print(f"  • {goal.subject}: {hours}h {mins}m / {target_hours}h {target_mins}m ({progress_percentage:.1f}%) {status}")


def demonstrate_session_management():
    """Demonstrate study session management"""
    print("\n=== Study Session Management Demo ===")
    
    # Create a new study session
    print("📚 Creating new study session...")
    session = StudySession(subject="Advanced Physics")
    print(f"  • Session ID: {session.id}")
    print(f"  • Subject: {session.subject}")
    print(f"  • Started at: {session.start_time.strftime('%H:%M:%S')}")
    print(f"  • Is active: {session.is_active}")
    print(f"  • Current duration: {session.get_formatted_duration()}")
    
    # Simulate some study time
    import time
    print("\n⏳ Simulating 2 seconds of study time...")
    time.sleep(2)
    
    print(f"  • Updated duration: {session.get_formatted_duration()}")
    
    # Add completed tasks
    print("\n✅ Adding completed tasks...")
    session.add_completed_task("task_physics_001")
    session.add_completed_task("task_physics_002")
    print(f"  • Completed tasks: {len(session.tasks_completed)}")
    print(f"  • Task IDs: {session.tasks_completed}")
    
    # End the session
    print("\n🏁 Ending study session...")
    session.end_session("Completed quantum mechanics problems and reviewed wave equations")
    print(f"  • Is active: {session.is_active}")
    print(f"  • Final duration: {session.get_formatted_duration()}")
    print(f"  • Notes: {session.notes}")
    
    # Save to database
    print("\n💾 Saving to database...")
    db_manager = DatabaseManager()
    if db_manager.create_study_session(session):
        print("  ✅ Session saved successfully")
        
        # Retrieve and verify
        retrieved = db_manager.get_study_session(session.id)
        if retrieved:
            print(f"  ✅ Session retrieved: {retrieved.subject} - {retrieved.get_formatted_duration()}")
        else:
            print("  ❌ Failed to retrieve session")
    else:
        print("  ❌ Failed to save session")


def main():
    """Main demonstration function"""
    print("🎓 StosOS Study Tracker Verification")
    print("=" * 50)
    
    try:
        # Demonstrate core functionality
        demonstrate_session_management()
        demonstrate_pomodoro()
        demonstrate_goals()
        demonstrate_statistics()
        
        print("\n" + "=" * 50)
        print("✅ Study Tracker verification completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  🍅 Pomodoro timer with work/break cycles")
        print("  📊 Comprehensive study statistics")
        print("  🎯 Goal setting and progress tracking")
        print("  📚 Study session management")
        print("  🔥 Study streak calculation")
        print("  💾 Database integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)