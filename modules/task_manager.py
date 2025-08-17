"""
Task Management Module for StosOS

Provides comprehensive task management functionality including:
- CRUD operations for tasks
- Priority system (HIGH, MEDIUM, LOW)
- Category organization
- Task list UI with filtering, sorting, and search
- Task completion tracking and statistics
- Notification system for approaching deadlines

Requirements: 2.1, 2.2, 2.4, 2.5
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.metrics import dp

from core.base_module import BaseModule
from core.database_manager import DatabaseManager
from models.task import Task, Priority
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class TaskCard(StosOSCard):
    """Individual task card component"""
    
    def __init__(self, task: Task, on_edit: Callable = None, on_delete: Callable = None, 
                 on_toggle_complete: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.task = task
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle_complete = on_toggle_complete
        
        self.size_hint_y = None
        self.height = dp(120)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the task card UI"""
        # Main content layout
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Left side - task info
        info_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'))
        
        # Title and priority
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        
        # Task title
        title_label = StosOSLabel(
            text=self.task.title,
            label_type="title" if not self.task.completed else "body",
            color=StosOSTheme.get_color('text_primary') if not self.task.completed 
                  else StosOSTheme.get_color('text_disabled'),
            size_hint_x=0.7
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_layout.add_widget(title_label)
        
        # Priority indicator
        priority_color = self._get_priority_color()
        priority_label = StosOSLabel(
            text=f"[{self.task.priority.value}]",
            color=priority_color,
            size_hint_x=0.3,
            halign='right'
        )
        priority_label.bind(size=priority_label.setter('text_size'))
        title_layout.add_widget(priority_label)
        
        info_layout.add_widget(title_layout)
        
        # Description
        if self.task.description:
            desc_label = StosOSLabel(
                text=self.task.description,
                color=StosOSTheme.get_color('text_secondary'),
                font_size=StosOSTheme.get_font_size('caption'),
                size_hint_y=None,
                height=dp(40),
                text_size=(None, None)
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            info_layout.add_widget(desc_label)
        
        # Category and due date
        meta_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
        
        # Category
        category_label = StosOSLabel(
            text=f"📁 {self.task.category}",
            color=StosOSTheme.get_color('accent_tertiary'),
            font_size=StosOSTheme.get_font_size('caption'),
            size_hint_x=0.5
        )
        meta_layout.add_widget(category_label)
        
        # Due date
        if self.task.due_date:
            due_text, due_color = self._get_due_date_info()
            due_label = StosOSLabel(
                text=due_text,
                color=due_color,
                font_size=StosOSTheme.get_font_size('caption'),
                size_hint_x=0.5,
                halign='right'
            )
            due_label.bind(size=due_label.setter('text_size'))
            meta_layout.add_widget(due_label)
        
        info_layout.add_widget(meta_layout)
        
        content_layout.add_widget(info_layout)
        
        # Right side - action buttons
        actions_layout = BoxLayout(
            orientation='vertical', 
            size_hint_x=None, 
            width=dp(80),
            spacing=StosOSTheme.get_spacing('xs')
        )
        
        # Complete toggle button
        complete_btn = StosOSToggleButton(
            text="✓" if self.task.completed else "○",
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            button_type="accent" if self.task.completed else "secondary"
        )
        complete_btn.is_toggled = self.task.completed
        complete_btn.bind(on_press=self._on_toggle_complete)
        actions_layout.add_widget(complete_btn)
        
        # Edit button
        edit_btn = StosOSIconButton(
            icon="✏",
            size=(dp(35), dp(35)),
            button_type="secondary"
        )
        edit_btn.bind(on_press=self._on_edit)
        actions_layout.add_widget(edit_btn)
        
        # Delete button
        delete_btn = StosOSIconButton(
            icon="🗑",
            size=(dp(35), dp(35)),
            button_type="danger"
        )
        delete_btn.bind(on_press=self._on_delete)
        actions_layout.add_widget(delete_btn)
        
        content_layout.add_widget(actions_layout)
        
        self.add_widget(content_layout)
    
    def _get_priority_color(self):
        """Get color for priority indicator"""
        if self.task.priority == Priority.HIGH:
            return StosOSTheme.get_color('error')
        elif self.task.priority == Priority.MEDIUM:
            return StosOSTheme.get_color('warning')
        else:
            return StosOSTheme.get_color('info')
    
    def _get_due_date_info(self):
        """Get due date text and color based on urgency"""
        if not self.task.due_date:
            return "", StosOSTheme.get_color('text_secondary')
        
        now = datetime.now()
        time_diff = self.task.due_date - now
        
        if time_diff.total_seconds() < 0:
            # Overdue
            return f"⚠ Overdue", StosOSTheme.get_color('error')
        elif time_diff.total_seconds() < 86400:  # Less than 24 hours
            hours = int(time_diff.total_seconds() / 3600)
            return f"🕐 {hours}h left", StosOSTheme.get_color('warning')
        elif time_diff.days < 7:
            return f"📅 {time_diff.days}d left", StosOSTheme.get_color('accent_secondary')
        else:
            return f"📅 {self.task.due_date.strftime('%m/%d')}", StosOSTheme.get_color('text_secondary')
    
    def _on_toggle_complete(self, *args):
        """Handle task completion toggle"""
        if self.on_toggle_complete:
            self.on_toggle_complete(self.task)
    
    def _on_edit(self, *args):
        """Handle edit button press"""
        if self.on_edit:
            self.on_edit(self.task)
    
    def _on_delete(self, *args):
        """Handle delete button press"""
        if self.on_delete:
            self.on_delete(self.task)


class TaskFormPopup(StosOSPopup):
    """Popup for creating/editing tasks"""
    
    def __init__(self, task: Task = None, on_save: Callable = None, **kwargs):
        self.task = task
        self.on_save = on_save
        self.is_editing = task is not None
        
        title = "Edit Task" if self.is_editing else "New Task"
        super().__init__(
            title=title,
            size_hint=(0.8, 0.7),
            auto_dismiss=False,
            **kwargs
        )
        
        self._build_form()
    
    def _build_form(self):
        """Build the task form"""
        form_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Title input
        self.title_input = StosOSTextInput(
            placeholder="Task title",
            text=self.task.title if self.is_editing else "",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        form_layout.add_widget(StosOSLabel(text="Title:", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.title_input)
        
        # Description input
        self.description_input = StosOSTextInput(
            placeholder="Task description (optional)",
            text=self.task.description if self.is_editing else "",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        form_layout.add_widget(StosOSLabel(text="Description:", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.description_input)
        
        # Priority and category row
        row_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'),
                              size_hint_y=None, height=StosOSTheme.get_dimension('input_height'))
        
        # Priority selection
        priority_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        priority_layout.add_widget(StosOSLabel(text="Priority:", size_hint_y=None, height=dp(25)))
        
        self.priority_buttons = {}
        priority_btn_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('xs'))
        
        for priority in Priority:
            btn = StosOSToggleButton(
                text=priority.value,
                size_hint_x=1/3,
                button_type="accent" if priority == Priority.HIGH else "secondary"
            )
            btn.bind(on_press=lambda x, p=priority: self._select_priority(p))
            self.priority_buttons[priority] = btn
            priority_btn_layout.add_widget(btn)
        
        # Set initial priority
        if self.is_editing:
            self.priority_buttons[self.task.priority].set_state(True)
        else:
            self.priority_buttons[Priority.MEDIUM].set_state(True)
        
        priority_layout.add_widget(priority_btn_layout)
        row_layout.add_widget(priority_layout)
        
        # Category input
        category_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        category_layout.add_widget(StosOSLabel(text="Category:", size_hint_y=None, height=dp(25)))
        
        self.category_input = StosOSTextInput(
            placeholder="e.g., Physics, Math",
            text=self.task.category if self.is_editing else "General"
        )
        category_layout.add_widget(self.category_input)
        row_layout.add_widget(category_layout)
        
        form_layout.add_widget(row_layout)
        
        # Due date input
        self.due_date_input = StosOSTextInput(
            placeholder="YYYY-MM-DD HH:MM (optional)",
            text=self.task.due_date.strftime('%Y-%m-%d %H:%M') if self.is_editing and self.task.due_date else "",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        form_layout.add_widget(StosOSLabel(text="Due Date:", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.due_date_input)
        
        # Estimated duration
        self.duration_input = StosOSTextInput(
            placeholder="Minutes",
            text=str(self.task.estimated_duration) if self.is_editing else "30",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        form_layout.add_widget(StosOSLabel(text="Estimated Duration (minutes):", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.duration_input)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'),
                                 size_hint_y=None, height=StosOSTheme.get_dimension('button_height'))
        
        cancel_btn = StosOSButton(
            text="Cancel",
            button_type="secondary",
            size_hint_x=0.5
        )
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)
        
        save_btn = StosOSButton(
            text="Save",
            button_type="accent",
            size_hint_x=0.5
        )
        save_btn.bind(on_press=self._save_task)
        button_layout.add_widget(save_btn)
        
        form_layout.add_widget(button_layout)
        
        self.content = form_layout
    
    def _select_priority(self, priority: Priority):
        """Handle priority selection"""
        # Deselect all other priorities
        for p, btn in self.priority_buttons.items():
            if p != priority:
                btn.set_state(False)
    
    def _save_task(self, *args):
        """Save the task"""
        try:
            # Validate title
            title = self.title_input.text.strip()
            if not title:
                # Show error - title required
                return
            
            # Get selected priority
            selected_priority = Priority.MEDIUM
            for priority, btn in self.priority_buttons.items():
                if btn.is_toggled:
                    selected_priority = priority
                    break
            
            # Parse due date
            due_date = None
            if self.due_date_input.text.strip():
                try:
                    due_date = datetime.strptime(self.due_date_input.text.strip(), '%Y-%m-%d %H:%M')
                except ValueError:
                    try:
                        due_date = datetime.strptime(self.due_date_input.text.strip(), '%Y-%m-%d')
                    except ValueError:
                        # Invalid date format - could show error
                        pass
            
            # Parse duration
            try:
                duration = int(self.duration_input.text.strip())
            except ValueError:
                duration = 30
            
            # Create or update task
            if self.is_editing:
                self.task.title = title
                self.task.description = self.description_input.text.strip()
                self.task.priority = selected_priority
                self.task.category = self.category_input.text.strip() or "General"
                self.task.due_date = due_date
                self.task.estimated_duration = duration
            else:
                self.task = Task(
                    title=title,
                    description=self.description_input.text.strip(),
                    priority=selected_priority,
                    category=self.category_input.text.strip() or "General",
                    due_date=due_date,
                    estimated_duration=duration
                )
            
            # Call save callback
            if self.on_save:
                self.on_save(self.task)
            
            self.dismiss()
            
        except Exception as e:
            logging.error(f"Error saving task: {e}")


class TaskManager(BaseModule):
    """
    Task Management Module
    
    Provides comprehensive task management functionality including CRUD operations,
    priority system, filtering, sorting, search, and deadline notifications.
    """
    
    def __init__(self):
        super().__init__(
            module_id="task_manager",
            display_name="Task Manager",
            icon="📋"
        )
        
        self.db_manager = None
        self.tasks = []
        self.filtered_tasks = []
        self.current_filter = {"category": None, "completed": None, "priority": None}
        self.current_sort = "created_at"
        self.search_term = ""
        
        # UI components
        self.task_list_layout = None
        self.stats_panel = None
        self.filter_panel = None
        self.search_input = None
        
        # Notification tracking
        self.notification_timer = None
    
    def initialize(self) -> bool:
        """Initialize the task manager module"""
        try:
            self.db_manager = DatabaseManager()
            self._load_tasks()
            self._start_notification_timer()
            self._initialized = True
            self.logger.info("Task Manager module initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Task Manager: {e}")
            self.handle_error(e, "initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Get the task manager screen"""
        if self.screen_widget is None:
            self.screen_widget = Screen(name=self.module_id)
            self._build_ui()
        return self.screen_widget
    
    def _build_ui(self):
        """Build the task manager UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Header with title and add button
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        title_label = StosOSLabel(
            text="📋 Task Manager",
            label_type="title",
            size_hint_x=0.7
        )
        header_layout.add_widget(title_label)
        
        add_btn = StosOSButton(
            text="+ New Task",
            button_type="accent",
            size_hint_x=0.3
        )
        add_btn.bind(on_press=self._show_new_task_form)
        header_layout.add_widget(add_btn)
        
        main_layout.add_widget(header_layout)
        
        # Statistics panel
        self._build_stats_panel()
        main_layout.add_widget(self.stats_panel)
        
        # Search and filter panel
        self._build_filter_panel()
        main_layout.add_widget(self.filter_panel)
        
        # Task list
        self._build_task_list()
        main_layout.add_widget(self.task_list_layout)
        
        self.screen_widget.add_widget(main_layout)
    
    def _build_stats_panel(self):
        """Build the statistics panel"""
        self.stats_panel = StosOSPanel(
            title="Statistics",
            size_hint_y=None,
            height=dp(100)
        )
        
        stats_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Total tasks
        total_label = StosOSLabel(
            text="Total: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(total_label)
        
        # Completed tasks
        completed_label = StosOSLabel(
            text="Completed: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(completed_label)
        
        # Pending tasks
        pending_label = StosOSLabel(
            text="Pending: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(pending_label)
        
        # Overdue tasks
        overdue_label = StosOSLabel(
            text="Overdue: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(overdue_label)
        
        self.stats_panel.add_widget(stats_layout)
        
        # Store references for updates
        self.stats_labels = {
            'total': total_label,
            'completed': completed_label,
            'pending': pending_label,
            'overdue': overdue_label
        }
    
    def _build_filter_panel(self):
        """Build the search and filter panel"""
        self.filter_panel = StosOSPanel(
            title="Search & Filter",
            size_hint_y=None,
            height=dp(120)
        )
        
        filter_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Search input
        self.search_input = StosOSTextInput(
            placeholder="Search tasks...",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        self.search_input.bind(text=self._on_search_text_change)
        filter_layout.add_widget(self.search_input)
        
        # Filter buttons row
        filter_buttons_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('xs'))
        
        # Category filter
        self.category_filter_btn = StosOSToggleButton(text="All Categories")
        self.category_filter_btn.bind(on_press=self._show_category_filter)
        filter_buttons_layout.add_widget(self.category_filter_btn)
        
        # Status filter
        self.status_filter_btn = StosOSToggleButton(text="All Status")
        self.status_filter_btn.bind(on_press=self._show_status_filter)
        filter_buttons_layout.add_widget(self.status_filter_btn)
        
        # Priority filter
        self.priority_filter_btn = StosOSToggleButton(text="All Priorities")
        self.priority_filter_btn.bind(on_press=self._show_priority_filter)
        filter_buttons_layout.add_widget(self.priority_filter_btn)
        
        # Sort button
        self.sort_btn = StosOSButton(text="Sort: Date", button_type="secondary")
        self.sort_btn.bind(on_press=self._show_sort_options)
        filter_buttons_layout.add_widget(self.sort_btn)
        
        filter_layout.add_widget(filter_buttons_layout)
        
        self.filter_panel.add_widget(filter_layout)
    
    def _build_task_list(self):
        """Build the scrollable task list"""
        self.task_list_layout = StosOSScrollView()
        
        self.task_container = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None
        )
        self.task_container.bind(minimum_height=self.task_container.setter('height'))
        
        self.task_list_layout.add_widget(self.task_container)
        
        # Initial task list population
        self._refresh_task_list()    

    def _load_tasks(self):
        """Load tasks from database"""
        try:
            self.tasks = self.db_manager.get_tasks()
            self._apply_filters_and_sort()
            self.logger.debug(f"Loaded {len(self.tasks)} tasks")
        except Exception as e:
            self.logger.error(f"Failed to load tasks: {e}")
            self.tasks = []
            self.filtered_tasks = []
    
    def _apply_filters_and_sort(self):
        """Apply current filters and sorting to task list"""
        # Start with all tasks
        filtered = self.tasks[:]
        
        # Apply search filter
        if self.search_term:
            filtered = [
                task for task in filtered
                if self.search_term.lower() in task.title.lower() or
                   self.search_term.lower() in task.description.lower() or
                   self.search_term.lower() in task.category.lower()
            ]
        
        # Apply category filter
        if self.current_filter["category"]:
            filtered = [task for task in filtered if task.category == self.current_filter["category"]]
        
        # Apply completion status filter
        if self.current_filter["completed"] is not None:
            filtered = [task for task in filtered if task.completed == self.current_filter["completed"]]
        
        # Apply priority filter
        if self.current_filter["priority"]:
            filtered = [task for task in filtered if task.priority == self.current_filter["priority"]]
        
        # Apply sorting
        if self.current_sort == "created_at":
            filtered.sort(key=lambda t: t.created_at, reverse=True)
        elif self.current_sort == "due_date":
            # Sort by due date, putting None values at the end
            filtered.sort(key=lambda t: t.due_date or datetime.max)
        elif self.current_sort == "priority":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            filtered.sort(key=lambda t: priority_order[t.priority])
        elif self.current_sort == "title":
            filtered.sort(key=lambda t: t.title.lower())
        
        self.filtered_tasks = filtered
    
    def _refresh_task_list(self):
        """Refresh the task list UI"""
        # Clear existing task cards
        self.task_container.clear_widgets()
        
        # Add task cards
        for task in self.filtered_tasks:
            task_card = TaskCard(
                task=task,
                on_edit=self._edit_task,
                on_delete=self._delete_task,
                on_toggle_complete=self._toggle_task_completion
            )
            self.task_container.add_widget(task_card)
        
        # Show empty state if no tasks
        if not self.filtered_tasks:
            empty_label = StosOSLabel(
                text="No tasks found" if self.search_term or any(self.current_filter.values()) 
                      else "No tasks yet. Create your first task!",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.task_container.add_widget(empty_label)
        
        # Update statistics
        self._update_statistics()
    
    def _update_statistics(self):
        """Update the statistics panel"""
        if not hasattr(self, 'stats_labels'):
            return
        
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        overdue_tasks = len([t for t in self.tasks if t.is_overdue()])
        
        self.stats_labels['total'].text = f"Total: {total_tasks}"
        self.stats_labels['completed'].text = f"Completed: {completed_tasks}"
        self.stats_labels['pending'].text = f"Pending: {pending_tasks}"
        self.stats_labels['overdue'].text = f"Overdue: {overdue_tasks}"
        
        # Color overdue count red if > 0
        if overdue_tasks > 0:
            self.stats_labels['overdue'].color = StosOSTheme.get_color('error')
        else:
            self.stats_labels['overdue'].color = StosOSTheme.get_color('text_secondary')
    
    def _on_search_text_change(self, instance, text):
        """Handle search text change"""
        self.search_term = text.strip()
        self._apply_filters_and_sort()
        self._refresh_task_list()
    
    def _show_new_task_form(self, *args):
        """Show form for creating new task"""
        popup = TaskFormPopup(on_save=self._save_new_task)
        popup.open_with_animation()
    
    def _save_new_task(self, task: Task):
        """Save new task to database"""
        try:
            if self.db_manager.create_task(task):
                self.tasks.append(task)
                self._apply_filters_and_sort()
                self._refresh_task_list()
                self.logger.info(f"Created new task: {task.title}")
            else:
                self.logger.error("Failed to save new task to database")
        except Exception as e:
            self.logger.error(f"Error saving new task: {e}")
            self.handle_error(e, "save_new_task")
    
    def _edit_task(self, task: Task):
        """Show form for editing existing task"""
        popup = TaskFormPopup(task=task, on_save=self._save_edited_task)
        popup.open_with_animation()
    
    def _save_edited_task(self, task: Task):
        """Save edited task to database"""
        try:
            if self.db_manager.update_task(task):
                self._apply_filters_and_sort()
                self._refresh_task_list()
                self.logger.info(f"Updated task: {task.title}")
            else:
                self.logger.error("Failed to update task in database")
        except Exception as e:
            self.logger.error(f"Error updating task: {e}")
            self.handle_error(e, "save_edited_task")
    
    def _delete_task(self, task: Task):
        """Delete task with confirmation"""
        def confirm_delete():
            try:
                if self.db_manager.delete_task(task.id):
                    self.tasks = [t for t in self.tasks if t.id != task.id]
                    self._apply_filters_and_sort()
                    self._refresh_task_list()
                    self.logger.info(f"Deleted task: {task.title}")
                else:
                    self.logger.error("Failed to delete task from database")
            except Exception as e:
                self.logger.error(f"Error deleting task: {e}")
                self.handle_error(e, "delete_task")
        
        # Show confirmation popup
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        message = StosOSLabel(
            text=f"Are you sure you want to delete '{task.title}'?",
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        content.add_widget(message)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        cancel_btn = StosOSButton(text="Cancel", button_type="secondary")
        delete_btn = StosOSButton(text="Delete", button_type="danger")
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)
        content.add_widget(button_layout)
        
        popup = StosOSPopup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        delete_btn.bind(on_press=lambda x: (confirm_delete(), popup.dismiss()))
        
        popup.open_with_animation()
    
    def _toggle_task_completion(self, task: Task):
        """Toggle task completion status"""
        try:
            task.completed = not task.completed
            if self.db_manager.update_task(task):
                self._apply_filters_and_sort()
                self._refresh_task_list()
                status = "completed" if task.completed else "reopened"
                self.logger.info(f"Task {status}: {task.title}")
            else:
                # Revert on failure
                task.completed = not task.completed
                self.logger.error("Failed to update task completion status")
        except Exception as e:
            self.logger.error(f"Error toggling task completion: {e}")
            self.handle_error(e, "toggle_completion")
    
    def _show_category_filter(self, *args):
        """Show category filter options"""
        categories = list(set(task.category for task in self.tasks))
        categories.sort()
        
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # All categories option
        all_btn = StosOSButton(
            text="All Categories",
            button_type="accent" if not self.current_filter["category"] else "secondary"
        )
        all_btn.bind(on_press=lambda x: self._apply_category_filter(None))
        content.add_widget(all_btn)
        
        # Individual categories
        for category in categories:
            btn = StosOSButton(
                text=category,
                button_type="accent" if self.current_filter["category"] == category else "secondary"
            )
            btn.bind(on_press=lambda x, c=category: self._apply_category_filter(c))
            content.add_widget(btn)
        
        popup = StosOSPopup(
            title="Filter by Category",
            content=content,
            size_hint=(0.5, 0.6)
        )
        popup.open_with_animation()
    
    def _apply_category_filter(self, category: Optional[str]):
        """Apply category filter"""
        self.current_filter["category"] = category
        self.category_filter_btn.text = category or "All Categories"
        self._apply_filters_and_sort()
        self._refresh_task_list()
    
    def _show_status_filter(self, *args):
        """Show status filter options"""
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        options = [
            ("All Status", None),
            ("Pending", False),
            ("Completed", True)
        ]
        
        for text, status in options:
            btn = StosOSButton(
                text=text,
                button_type="accent" if self.current_filter["completed"] == status else "secondary"
            )
            btn.bind(on_press=lambda x, s=status: self._apply_status_filter(s))
            content.add_widget(btn)
        
        popup = StosOSPopup(
            title="Filter by Status",
            content=content,
            size_hint=(0.4, 0.4)
        )
        popup.open_with_animation()
    
    def _apply_status_filter(self, completed: Optional[bool]):
        """Apply status filter"""
        self.current_filter["completed"] = completed
        if completed is None:
            self.status_filter_btn.text = "All Status"
        elif completed:
            self.status_filter_btn.text = "Completed"
        else:
            self.status_filter_btn.text = "Pending"
        
        self._apply_filters_and_sort()
        self._refresh_task_list()
    
    def _show_priority_filter(self, *args):
        """Show priority filter options"""
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # All priorities option
        all_btn = StosOSButton(
            text="All Priorities",
            button_type="accent" if not self.current_filter["priority"] else "secondary"
        )
        all_btn.bind(on_press=lambda x: self._apply_priority_filter(None))
        content.add_widget(all_btn)
        
        # Individual priorities
        for priority in Priority:
            btn = StosOSButton(
                text=priority.value,
                button_type="accent" if self.current_filter["priority"] == priority else "secondary"
            )
            btn.bind(on_press=lambda x, p=priority: self._apply_priority_filter(p))
            content.add_widget(btn)
        
        popup = StosOSPopup(
            title="Filter by Priority",
            content=content,
            size_hint=(0.4, 0.5)
        )
        popup.open_with_animation()
    
    def _apply_priority_filter(self, priority: Optional[Priority]):
        """Apply priority filter"""
        self.current_filter["priority"] = priority
        self.priority_filter_btn.text = priority.value if priority else "All Priorities"
        self._apply_filters_and_sort()
        self._refresh_task_list()
    
    def _show_sort_options(self, *args):
        """Show sorting options"""
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        sort_options = [
            ("Date Created", "created_at"),
            ("Due Date", "due_date"),
            ("Priority", "priority"),
            ("Title", "title")
        ]
        
        for text, sort_key in sort_options:
            btn = StosOSButton(
                text=text,
                button_type="accent" if self.current_sort == sort_key else "secondary"
            )
            btn.bind(on_press=lambda x, s=sort_key: self._apply_sort(s))
            content.add_widget(btn)
        
        popup = StosOSPopup(
            title="Sort Tasks",
            content=content,
            size_hint=(0.4, 0.5)
        )
        popup.open_with_animation()
    
    def _apply_sort(self, sort_key: str):
        """Apply sorting"""
        self.current_sort = sort_key
        sort_names = {
            "created_at": "Date",
            "due_date": "Due Date",
            "priority": "Priority",
            "title": "Title"
        }
        self.sort_btn.text = f"Sort: {sort_names[sort_key]}"
        self._apply_filters_and_sort()
        self._refresh_task_list()
    
    def _start_notification_timer(self):
        """Start timer for checking deadline notifications"""
        # Check for approaching deadlines every 5 minutes
        self.notification_timer = Clock.schedule_interval(self._check_deadline_notifications, 300)
    
    def _check_deadline_notifications(self, dt):
        """Check for tasks with approaching deadlines"""
        try:
            now = datetime.now()
            notification_threshold = now + timedelta(hours=24)  # 24 hours ahead
            
            approaching_tasks = []
            for task in self.tasks:
                if (not task.completed and task.due_date and 
                    now < task.due_date <= notification_threshold):
                    approaching_tasks.append(task)
            
            if approaching_tasks:
                self._show_deadline_notifications(approaching_tasks)
                
        except Exception as e:
            self.logger.error(f"Error checking deadline notifications: {e}")
    
    def _show_deadline_notifications(self, tasks: List[Task]):
        """Show notifications for tasks with approaching deadlines"""
        if not tasks:
            return
        
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        title_label = StosOSLabel(
            text=f"⚠ {len(tasks)} task(s) due soon:",
            color=StosOSTheme.get_color('warning'),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(title_label)
        
        # List approaching tasks
        for task in tasks[:5]:  # Show max 5 tasks
            time_left = task.due_date - datetime.now()
            hours_left = int(time_left.total_seconds() / 3600)
            
            task_label = StosOSLabel(
                text=f"• {task.title} ({hours_left}h left)",
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(task_label)
        
        if len(tasks) > 5:
            more_label = StosOSLabel(
                text=f"... and {len(tasks) - 5} more",
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(more_label)
        
        # OK button
        ok_btn = StosOSButton(
            text="OK",
            button_type="accent",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height')
        )
        content.add_widget(ok_btn)
        
        popup = StosOSPopup(
            title="Deadline Alert",
            content=content,
            size_hint=(0.6, 0.5),
            auto_dismiss=False
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open_with_animation()
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands for task management"""
        command_lower = command.lower()
        
        try:
            if "create task" in command_lower or "new task" in command_lower:
                self._show_new_task_form()
                return True
            elif "show tasks" in command_lower or "list tasks" in command_lower:
                # Already showing tasks, maybe refresh
                self._load_tasks()
                return True
            elif "completed tasks" in command_lower:
                self._apply_status_filter(True)
                return True
            elif "pending tasks" in command_lower:
                self._apply_status_filter(False)
                return True
            elif "high priority" in command_lower:
                self._apply_priority_filter(Priority.HIGH)
                return True
            elif "search" in command_lower:
                # Extract search term after "search"
                search_start = command_lower.find("search") + 6
                search_term = command[search_start:].strip()
                if search_term:
                    self.search_input.text = search_term
                return True
            
        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current module status"""
        base_status = super().get_status()
        
        task_stats = {
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks if t.completed]),
            "overdue_tasks": len([t for t in self.tasks if t.is_overdue()]),
            "current_filter": self.current_filter.copy(),
            "current_sort": self.current_sort,
            "search_term": self.search_term
        }
        
        base_status.update(task_stats)
        return base_status
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        # Refresh tasks when activated
        self._load_tasks()
    
    def cleanup(self):
        """Cleanup module resources"""
        if self.notification_timer:
            self.notification_timer.cancel()
            self.notification_timer = None
        
        if self.db_manager:
            self.db_manager.close_connections()
        
        super().cleanup()