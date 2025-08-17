#!/usr/bin/env python3
"""
Task Manager Module Demo

Demonstrates the task management functionality in a simple console interface.
This shows how the TaskManager module can be integrated into the main StosOS application.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.task import Task, Priority
from core.database_manager import DatabaseManager


class TaskManagerDemo:
    """Console-based demo of task management functionality"""
    
    def __init__(self):
        self.db_manager = DatabaseManager("data/demo_tasks.db")
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from database"""
        self.tasks = self.db_manager.get_tasks()
        print(f"📋 Loaded {len(self.tasks)} tasks from database")
    
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("📋 StosOS Task Manager Demo")
        print("=" * 50)
        print("1. 📝 Create New Task")
        print("2. 📋 List All Tasks")
        print("3. 🔍 Filter Tasks")
        print("4. ✅ Toggle Task Completion")
        print("5. ✏️  Edit Task")
        print("6. 🗑️  Delete Task")
        print("7. 📊 Show Statistics")
        print("8. ⚠️  Check Approaching Deadlines")
        print("9. 🎤 Voice Command Demo")
        print("0. 🚪 Exit")
        print("=" * 50)
    
    def create_task(self):
        """Create a new task"""
        print("\n📝 Creating New Task")
        print("-" * 30)
        
        title = input("Task title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
        
        description = input("Description (optional): ").strip()
        
        print("Priority levels: 1=HIGH, 2=MEDIUM, 3=LOW")
        priority_choice = input("Priority (1-3, default=2): ").strip() or "2"
        priority_map = {"1": Priority.HIGH, "2": Priority.MEDIUM, "3": Priority.LOW}
        priority = priority_map.get(priority_choice, Priority.MEDIUM)
        
        category = input("Category (default=General): ").strip() or "General"
        
        due_date_str = input("Due date (YYYY-MM-DD HH:MM, optional): ").strip()
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                except ValueError:
                    print("⚠️ Invalid date format, skipping due date")
        
        duration_str = input("Estimated duration in minutes (default=30): ").strip() or "30"
        try:
            duration = int(duration_str)
        except ValueError:
            duration = 30
        
        # Create task
        task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            estimated_duration=duration
        )
        
        if self.db_manager.create_task(task):
            self.tasks.append(task)
            print(f"✅ Task '{title}' created successfully!")
        else:
            print("❌ Failed to create task")
    
    def list_tasks(self):
        """List all tasks"""
        print("\n📋 All Tasks")
        print("-" * 50)
        
        if not self.tasks:
            print("No tasks found. Create your first task!")
            return
        
        for i, task in enumerate(self.tasks, 1):
            status = "✅" if task.completed else "⏳"
            priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[task.priority.value]
            
            print(f"{i:2d}. {status} {task.title}")
            print(f"    {priority_icon} {task.priority.value} | 📁 {task.category}")
            
            if task.description:
                print(f"    📝 {task.description}")
            
            if task.due_date:
                due_status = "⚠️ OVERDUE" if task.is_overdue() else "📅"
                print(f"    {due_status} Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
            
            print(f"    ⏱️ Est. {task.estimated_duration} minutes")
            print()
    
    def filter_tasks(self):
        """Filter tasks by various criteria"""
        print("\n🔍 Filter Tasks")
        print("-" * 30)
        print("1. By Category")
        print("2. By Priority")
        print("3. By Completion Status")
        print("4. Search by Text")
        
        choice = input("Choose filter (1-4): ").strip()
        
        filtered_tasks = []
        
        if choice == "1":
            categories = list(set(task.category for task in self.tasks))
            print(f"Available categories: {', '.join(categories)}")
            category = input("Enter category: ").strip()
            filtered_tasks = [t for t in self.tasks if t.category.lower() == category.lower()]
        
        elif choice == "2":
            print("Priorities: HIGH, MEDIUM, LOW")
            priority_str = input("Enter priority: ").strip().upper()
            try:
                priority = Priority(priority_str)
                filtered_tasks = [t for t in self.tasks if t.priority == priority]
            except ValueError:
                print("❌ Invalid priority")
                return
        
        elif choice == "3":
            status = input("Show completed tasks? (y/n): ").strip().lower() == 'y'
            filtered_tasks = [t for t in self.tasks if t.completed == status]
        
        elif choice == "4":
            search_term = input("Enter search term: ").strip().lower()
            filtered_tasks = [
                t for t in self.tasks
                if search_term in t.title.lower() or
                   search_term in t.description.lower() or
                   search_term in t.category.lower()
            ]
        
        else:
            print("❌ Invalid choice")
            return
        
        print(f"\n🔍 Found {len(filtered_tasks)} matching tasks:")
        if filtered_tasks:
            # Temporarily replace tasks for display
            original_tasks = self.tasks
            self.tasks = filtered_tasks
            self.list_tasks()
            self.tasks = original_tasks
        else:
            print("No matching tasks found.")
    
    def toggle_completion(self):
        """Toggle task completion status"""
        if not self.tasks:
            print("No tasks available")
            return
        
        print("\n✅ Toggle Task Completion")
        print("-" * 30)
        
        # Show numbered list
        for i, task in enumerate(self.tasks, 1):
            status = "✅" if task.completed else "⏳"
            print(f"{i:2d}. {status} {task.title}")
        
        try:
            choice = int(input("\nEnter task number: ")) - 1
            if 0 <= choice < len(self.tasks):
                task = self.tasks[choice]
                task.completed = not task.completed
                
                if self.db_manager.update_task(task):
                    status = "completed" if task.completed else "reopened"
                    print(f"✅ Task '{task.title}' {status}!")
                else:
                    # Revert on failure
                    task.completed = not task.completed
                    print("❌ Failed to update task")
            else:
                print("❌ Invalid task number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def show_statistics(self):
        """Show task statistics"""
        print("\n📊 Task Statistics")
        print("-" * 30)
        
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.completed])
        pending = total - completed
        overdue = len([t for t in self.tasks if t.is_overdue()])
        
        print(f"📋 Total Tasks: {total}")
        print(f"✅ Completed: {completed}")
        print(f"⏳ Pending: {pending}")
        print(f"⚠️ Overdue: {overdue}")
        
        if total > 0:
            completion_rate = (completed / total) * 100
            print(f"📈 Completion Rate: {completion_rate:.1f}%")
        
        # Category breakdown
        categories = {}
        for task in self.tasks:
            categories[task.category] = categories.get(task.category, 0) + 1
        
        if categories:
            print(f"\n📁 Tasks by Category:")
            for category, count in sorted(categories.items()):
                print(f"   {category}: {count}")
        
        # Priority breakdown
        priorities = {p: 0 for p in Priority}
        for task in self.tasks:
            priorities[task.priority] += 1
        
        print(f"\n🎯 Tasks by Priority:")
        for priority, count in priorities.items():
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[priority.value]
            print(f"   {icon} {priority.value}: {count}")
    
    def check_deadlines(self):
        """Check for approaching deadlines"""
        print("\n⚠️ Approaching Deadlines")
        print("-" * 30)
        
        now = datetime.now()
        threshold = now + timedelta(hours=24)
        
        approaching = []
        for task in self.tasks:
            if (not task.completed and task.due_date and 
                now < task.due_date <= threshold):
                approaching.append(task)
        
        if not approaching:
            print("✅ No tasks due in the next 24 hours")
            return
        
        print(f"⚠️ {len(approaching)} task(s) due soon:")
        for task in approaching:
            time_left = task.due_date - now
            hours_left = int(time_left.total_seconds() / 3600)
            print(f"   • {task.title} ({hours_left}h left)")
    
    def voice_command_demo(self):
        """Demonstrate voice command handling"""
        print("\n🎤 Voice Command Demo")
        print("-" * 30)
        print("Try these voice commands:")
        print("- 'show completed tasks'")
        print("- 'show pending tasks'")
        print("- 'show high priority tasks'")
        print("- 'search physics'")
        
        command = input("\nEnter voice command: ").strip()
        
        if self.handle_voice_command(command):
            print("✅ Voice command processed successfully!")
        else:
            print("❌ Voice command not recognized")
    
    def handle_voice_command(self, command):
        """Handle voice commands"""
        command_lower = command.lower()
        
        if "completed tasks" in command_lower:
            completed_tasks = [t for t in self.tasks if t.completed]
            print(f"Found {len(completed_tasks)} completed tasks")
            return True
        elif "pending tasks" in command_lower:
            pending_tasks = [t for t in self.tasks if not t.completed]
            print(f"Found {len(pending_tasks)} pending tasks")
            return True
        elif "high priority" in command_lower:
            high_priority_tasks = [t for t in self.tasks if t.priority == Priority.HIGH]
            print(f"Found {len(high_priority_tasks)} high priority tasks")
            return True
        elif "search" in command_lower:
            search_start = command_lower.find("search") + 6
            search_term = command[search_start:].strip()
            if search_term:
                results = [
                    t for t in self.tasks
                    if search_term.lower() in t.title.lower() or
                       search_term.lower() in t.description.lower()
                ]
                print(f"Found {len(results)} tasks matching '{search_term}'")
                return True
        
        return False
    
    def run(self):
        """Run the demo"""
        print("🚀 Welcome to StosOS Task Manager Demo!")
        
        # Create some sample tasks if database is empty
        if not self.tasks:
            print("📝 Creating sample tasks...")
            sample_tasks = [
                Task(
                    title="Study Physics - Mechanics",
                    description="Review Newton's laws and kinematics",
                    priority=Priority.HIGH,
                    category="Physics",
                    due_date=datetime.now() + timedelta(days=1),
                    estimated_duration=120
                ),
                Task(
                    title="Math Assignment - Calculus",
                    description="Complete integration problems",
                    priority=Priority.MEDIUM,
                    category="Math",
                    due_date=datetime.now() + timedelta(days=3),
                    estimated_duration=90
                ),
                Task(
                    title="Chemistry Lab Report",
                    description="Write report on acid-base titration",
                    priority=Priority.LOW,
                    category="Chemistry",
                    estimated_duration=60,
                    completed=True
                )
            ]
            
            for task in sample_tasks:
                if self.db_manager.create_task(task):
                    self.tasks.append(task)
            
            print(f"✅ Created {len(sample_tasks)} sample tasks")
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self.create_task()
            elif choice == "2":
                self.list_tasks()
            elif choice == "3":
                self.filter_tasks()
            elif choice == "4":
                self.toggle_completion()
            elif choice == "5":
                print("✏️ Edit functionality would open task form in full UI")
            elif choice == "6":
                print("🗑️ Delete functionality would show confirmation dialog in full UI")
            elif choice == "7":
                self.show_statistics()
            elif choice == "8":
                self.check_deadlines()
            elif choice == "9":
                self.voice_command_demo()
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")


def main():
    """Main function"""
    try:
        demo = TaskManagerDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)