"""
User Notification System for StosOS
Provides user-friendly error notifications and recovery instructions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp

from ui.components import StosOSButton, StosOSLabel, StosOSPanel
from ui.theme import StosOSTheme


class NotificationType(Enum):
    """Types of notifications"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
    RECOVERY = "recovery"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Notification:
    """Individual notification object"""
    
    def __init__(self, title: str, message: str, 
                 notification_type: NotificationType = NotificationType.INFO,
                 priority: NotificationPriority = NotificationPriority.MEDIUM,
                 actions: Optional[List[Dict[str, Any]]] = None,
                 auto_dismiss: bool = True,
                 dismiss_timeout: int = 10):
        
        self.id = f"notif_{datetime.now().timestamp()}"
        self.title = title
        self.message = message
        self.type = notification_type
        self.priority = priority
        self.actions = actions or []
        self.auto_dismiss = auto_dismiss
        self.dismiss_timeout = dismiss_timeout
        self.created_at = datetime.now()
        self.dismissed = False
        self.popup_widget = None


class NotificationManager:
    """Manages user notifications and error recovery instructions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_notifications: List[Notification] = []
        self.notification_history: List[Notification] = []
        self.max_history = 100
        
        # UI callbacks
        self.ui_callbacks: List[Callable] = []
        
        # Notification queue for high-priority items
        self.notification_queue: List[Notification] = []
        
        # Rate limiting
        self.last_notification_times: Dict[str, datetime] = {}
        self.rate_limit_seconds = 5
    
    def show_error_notification(self, error_info: Dict[str, Any]) -> None:
        """Show user-friendly error notification"""
        
        severity = error_info.get('severity', 'medium')
        module_id = error_info.get('module_id', '')
        error_message = error_info.get('error_message', 'Unknown error')
        context = error_info.get('context', '')
        suggested_actions = error_info.get('suggested_actions', [])
        requires_action = error_info.get('requires_action', False)
        
        # Create user-friendly title and message
        title = self._create_error_title(severity, module_id)
        message = self._create_error_message(error_message, context)
        
        # Determine notification type and priority
        if severity == 'critical':
            notif_type = NotificationType.ERROR
            priority = NotificationPriority.CRITICAL
        elif severity == 'high':
            notif_type = NotificationType.ERROR
            priority = NotificationPriority.HIGH
        elif severity == 'medium':
            notif_type = NotificationType.WARNING
            priority = NotificationPriority.MEDIUM
        else:
            notif_type = NotificationType.INFO
            priority = NotificationPriority.LOW
        
        # Create action buttons
        actions = []
        
        if suggested_actions:
            for action in suggested_actions[:3]:  # Limit to 3 actions
                actions.append({
                    'text': action,
                    'callback': lambda x, action=action: self._execute_suggested_action(action)
                })
        
        # Add dismiss action
        actions.append({
            'text': 'Dismiss',
            'callback': lambda x: self._dismiss_current_notification()
        })
        
        # Create and show notification
        notification = Notification(
            title=title,
            message=message,
            notification_type=notif_type,
            priority=priority,
            actions=actions,
            auto_dismiss=not requires_action,
            dismiss_timeout=30 if requires_action else 10
        )
        
        self.show_notification(notification)
    
    def show_recovery_notification(self, module_id: str, action: str, success: bool) -> None:
        """Show notification about recovery attempt"""
        
        if success:
            title = "Recovery Successful"
            message = f"Successfully recovered {module_id} using {action}"
            notif_type = NotificationType.SUCCESS
            priority = NotificationPriority.LOW
        else:
            title = "Recovery Failed"
            message = f"Failed to recover {module_id} using {action}"
            notif_type = NotificationType.ERROR
            priority = NotificationPriority.MEDIUM
        
        notification = Notification(
            title=title,
            message=message,
            notification_type=notif_type,
            priority=priority,
            auto_dismiss=True,
            dismiss_timeout=8
        )
        
        self.show_notification(notification)
    
    def show_system_health_alert(self, health_info: Dict[str, Any]) -> None:
        """Show system health alert"""
        
        metric_name = health_info.get('metric', 'System')
        value = health_info.get('value', 'Unknown')
        threshold = health_info.get('threshold', 'Unknown')
        
        title = f"{metric_name} Alert"
        message = f"{metric_name} usage is {value}, exceeding threshold of {threshold}"
        
        actions = [
            {
                'text': 'View Details',
                'callback': lambda x: self._show_system_diagnostics()
            },
            {
                'text': 'Dismiss',
                'callback': lambda x: self._dismiss_current_notification()
            }
        ]
        
        notification = Notification(
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            priority=NotificationPriority.HIGH,
            actions=actions,
            auto_dismiss=False
        )
        
        self.show_notification(notification)
    
    def show_notification(self, notification: Notification) -> None:
        """Show a notification to the user"""
        
        # Check rate limiting
        if self._is_rate_limited(notification):
            return
        
        # Add to active notifications
        self.active_notifications.append(notification)
        
        # Sort by priority
        self.active_notifications.sort(key=lambda n: n.priority.value, reverse=True)
        
        # Show the highest priority notification
        self._display_notification(notification)
        
        # Schedule auto-dismiss if enabled
        if notification.auto_dismiss:
            Clock.schedule_once(
                lambda dt: self._auto_dismiss_notification(notification),
                notification.dismiss_timeout
            )
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss a specific notification"""
        for notification in self.active_notifications:
            if notification.id == notification_id:
                return self._dismiss_notification(notification)
        return False
    
    def dismiss_all_notifications(self) -> None:
        """Dismiss all active notifications"""
        for notification in self.active_notifications.copy():
            self._dismiss_notification(notification)
    
    def get_active_notifications(self) -> List[Notification]:
        """Get list of active notifications"""
        return self.active_notifications.copy()
    
    def get_notification_history(self, limit: int = 20) -> List[Notification]:
        """Get notification history"""
        return self.notification_history[-limit:] if self.notification_history else []
    
    def register_ui_callback(self, callback: Callable) -> None:
        """Register callback for UI updates"""
        self.ui_callbacks.append(callback)
    
    def unregister_ui_callback(self, callback: Callable) -> None:
        """Unregister UI callback"""
        if callback in self.ui_callbacks:
            self.ui_callbacks.remove(callback)
    
    def _create_error_title(self, severity: str, module_id: str) -> str:
        """Create user-friendly error title"""
        
        severity_map = {
            'critical': 'Critical Error',
            'high': 'Error',
            'medium': 'Warning',
            'low': 'Notice'
        }
        
        base_title = severity_map.get(severity, 'Notice')
        
        if module_id:
            module_names = {
                'task_manager': 'Task Manager',
                'calendar_module': 'Calendar',
                'smart_home': 'Smart Home',
                'spotify_controller': 'Spotify',
                'idea_board': 'Idea Board',
                'study_tracker': 'Study Tracker',
                'voice_assistant': 'Voice Assistant'
            }
            
            friendly_name = module_names.get(module_id, module_id.replace('_', ' ').title())
            return f"{base_title} - {friendly_name}"
        
        return base_title
    
    def _create_error_message(self, error_message: str, context: str) -> str:
        """Create user-friendly error message"""
        
        # Common error message translations
        message_map = {
            'Connection refused': 'Unable to connect to the service. Please check your internet connection.',
            'Permission denied': 'Access denied. Please check file permissions or run with appropriate privileges.',
            'No such file or directory': 'Required file not found. The application may need to be reinstalled.',
            'Timeout': 'The operation took too long to complete. Please try again.',
            'Network is unreachable': 'No internet connection available. Please check your network settings.',
            'Authentication failed': 'Login failed. Please check your credentials and try again.'
        }
        
        # Try to find a user-friendly translation
        for technical_msg, friendly_msg in message_map.items():
            if technical_msg.lower() in error_message.lower():
                return friendly_msg
        
        # If no translation found, clean up the technical message
        cleaned_message = error_message.replace('_', ' ').capitalize()
        
        if context:
            return f"{cleaned_message} (in {context})"
        
        return cleaned_message
    
    def _is_rate_limited(self, notification: Notification) -> bool:
        """Check if notification should be rate limited"""
        
        # Create a key based on title and type
        key = f"{notification.title}:{notification.type.value}"
        
        now = datetime.now()
        last_time = self.last_notification_times.get(key)
        
        if last_time and (now - last_time).total_seconds() < self.rate_limit_seconds:
            return True
        
        self.last_notification_times[key] = now
        return False
    
    def _display_notification(self, notification: Notification) -> None:
        """Display notification using Kivy popup"""
        
        try:
            # Create popup content
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            
            # Title
            title_label = StosOSLabel(
                text=notification.title,
                font_size='18sp',
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(title_label)
            
            # Message
            message_label = StosOSLabel(
                text=notification.message,
                text_size=(dp(400), None),
                halign='left',
                valign='top'
            )
            content.add_widget(message_label)
            
            # Action buttons
            if notification.actions:
                button_layout = BoxLayout(
                    orientation='horizontal',
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(50)
                )
                
                for action in notification.actions:
                    button = StosOSButton(
                        text=action['text'],
                        size_hint_x=1.0 / len(notification.actions)
                    )
                    button.bind(on_press=action['callback'])
                    button_layout.add_widget(button)
                
                content.add_widget(button_layout)
            
            # Create popup
            popup = Popup(
                title='',
                content=content,
                size_hint=(0.8, 0.6),
                auto_dismiss=notification.auto_dismiss
            )
            
            # Apply theme colors
            popup.background_color = StosOSTheme.get_color('surface')
            
            notification.popup_widget = popup
            popup.open()
            
            # Notify UI callbacks
            for callback in self.ui_callbacks:
                try:
                    callback('notification_shown', notification)
                except Exception as e:
                    self.logger.error(f"Error in UI callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to display notification: {e}")
    
    def _dismiss_notification(self, notification: Notification) -> bool:
        """Dismiss a specific notification"""
        try:
            if notification in self.active_notifications:
                self.active_notifications.remove(notification)
            
            if notification.popup_widget:
                notification.popup_widget.dismiss()
            
            notification.dismissed = True
            
            # Add to history
            self.notification_history.append(notification)
            
            # Limit history size
            if len(self.notification_history) > self.max_history:
                self.notification_history.pop(0)
            
            # Notify UI callbacks
            for callback in self.ui_callbacks:
                try:
                    callback('notification_dismissed', notification)
                except Exception as e:
                    self.logger.error(f"Error in UI callback: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to dismiss notification: {e}")
            return False
    
    def _auto_dismiss_notification(self, notification: Notification) -> None:
        """Auto-dismiss notification after timeout"""
        if notification in self.active_notifications and not notification.dismissed:
            self._dismiss_notification(notification)
    
    def _dismiss_current_notification(self) -> None:
        """Dismiss the currently displayed notification"""
        if self.active_notifications:
            self._dismiss_notification(self.active_notifications[0])
    
    def _execute_suggested_action(self, action: str) -> None:
        """Execute a suggested recovery action"""
        self.logger.info(f"User selected recovery action: {action}")
        
        # This would integrate with the actual system to execute actions
        # For now, just show a confirmation
        
        confirmation = Notification(
            title="Action Noted",
            message=f"Recovery action '{action}' has been noted. Please follow the suggested steps.",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.LOW,
            auto_dismiss=True,
            dismiss_timeout=5
        )
        
        self.show_notification(confirmation)
    
    def _show_system_diagnostics(self) -> None:
        """Show system diagnostics information"""
        from core.error_handler import diagnostic_tools
        
        try:
            diagnostics = diagnostic_tools.run_system_diagnostics()
            
            # Create diagnostic summary
            summary_parts = []
            for test_name, test_result in diagnostics['tests'].items():
                status = test_result.get('status', 'unknown')
                summary_parts.append(f"{test_name.title()}: {status.title()}")
            
            summary = "\n".join(summary_parts)
            
            diagnostic_notification = Notification(
                title="System Diagnostics",
                message=f"Diagnostic Results:\n\n{summary}",
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                auto_dismiss=True,
                dismiss_timeout=15
            )
            
            self.show_notification(diagnostic_notification)
            
        except Exception as e:
            self.logger.error(f"Failed to show diagnostics: {e}")


# Global notification manager instance
notification_manager = NotificationManager()