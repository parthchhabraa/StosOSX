"""
Idea Board Module for StosOS

Provides comprehensive idea management functionality including:
- Quick capture interface for fast idea input
- Tag system for categorizing and organizing ideas
- Search and filtering functionality for idea retrieval
- Idea editing capabilities with rich text support
- Export functionality for ideas (markdown, PDF formats)

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import logging
import os
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
from models.idea import Idea
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class IdeaCard(StosOSCard):
    """Individual idea card component"""
    
    def __init__(self, idea: Idea, on_edit: Callable = None, on_delete: Callable = None, 
                 on_export: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.idea = idea
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_export = on_export
        
        self.size_hint_y = None
        self.height = dp(150)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the idea card UI"""
        # Main content layout
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Left side - idea info
        info_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'))
        
        # Content preview
        content_preview = self._get_content_preview()
        content_label = StosOSLabel(
            text=content_preview,
            color=StosOSTheme.get_color('text_primary'),
            font_size=StosOSTheme.get_font_size('body'),
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content_label.bind(size=content_label.setter('text_size'))
        info_layout.add_widget(content_label)
        
        # Tags
        if self.idea.tags:
            tags_layout = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height=dp(30),
                spacing=StosOSTheme.get_spacing('xs')
            )
            
            # Show first few tags
            displayed_tags = self.idea.tags[:3]
            for tag in displayed_tags:
                tag_label = StosOSLabel(
                    text=f"#{tag}",
                    color=StosOSTheme.get_color('accent_tertiary'),
                    font_size=StosOSTheme.get_font_size('caption'),
                    size_hint_x=None,
                    width=dp(80)
                )
                tags_layout.add_widget(tag_label)
            
            # Show count if more tags exist
            if len(self.idea.tags) > 3:
                more_label = StosOSLabel(
                    text=f"+{len(self.idea.tags) - 3}",
                    color=StosOSTheme.get_color('text_disabled'),
                    font_size=StosOSTheme.get_font_size('caption'),
                    size_hint_x=None,
                    width=dp(30)
                )
                tags_layout.add_widget(more_label)
            
            info_layout.add_widget(tags_layout)
        
        # Timestamps
        timestamp_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
        
        # Created date
        created_text = f"Created: {self.idea.created_at.strftime('%m/%d %H:%M')}"
        created_label = StosOSLabel(
            text=created_text,
            color=StosOSTheme.get_color('text_disabled'),
            font_size=StosOSTheme.get_font_size('caption'),
            size_hint_x=0.5
        )
        timestamp_layout.add_widget(created_label)
        
        # Updated date (if different from created)
        if self.idea.updated_at != self.idea.created_at:
            updated_text = f"Updated: {self.idea.updated_at.strftime('%m/%d %H:%M')}"
            updated_label = StosOSLabel(
                text=updated_text,
                color=StosOSTheme.get_color('text_disabled'),
                font_size=StosOSTheme.get_font_size('caption'),
                size_hint_x=0.5,
                halign='right'
            )
            updated_label.bind(size=updated_label.setter('text_size'))
            timestamp_layout.add_widget(updated_label)
        
        info_layout.add_widget(timestamp_layout)
        
        # Attachments indicator
        if self.idea.attachments:
            attachment_label = StosOSLabel(
                text=f"📎 {len(self.idea.attachments)} attachment(s)",
                color=StosOSTheme.get_color('accent_secondary'),
                font_size=StosOSTheme.get_font_size('caption'),
                size_hint_y=None,
                height=dp(20)
            )
            info_layout.add_widget(attachment_label)
        
        content_layout.add_widget(info_layout)
        
        # Right side - action buttons
        actions_layout = BoxLayout(
            orientation='vertical', 
            size_hint_x=None, 
            width=dp(80),
            spacing=StosOSTheme.get_spacing('xs')
        )
        
        # Edit button
        edit_btn = StosOSIconButton(
            icon="✏",
            size=(dp(35), dp(35)),
            button_type="secondary"
        )
        edit_btn.bind(on_press=self._on_edit)
        actions_layout.add_widget(edit_btn)
        
        # Export button
        export_btn = StosOSIconButton(
            icon="📤",
            size=(dp(35), dp(35)),
            button_type="accent"
        )
        export_btn.bind(on_press=self._on_export)
        actions_layout.add_widget(export_btn)
        
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
    
    def _get_content_preview(self) -> str:
        """Get truncated content preview"""
        content = self.idea.content.strip()
        if len(content) > 120:
            return content[:120] + "..."
        return content
    
    def _on_edit(self, *args):
        """Handle edit button press"""
        if self.on_edit:
            self.on_edit(self.idea)
    
    def _on_export(self, *args):
        """Handle export button press"""
        if self.on_export:
            self.on_export(self.idea)
    
    def _on_delete(self, *args):
        """Handle delete button press"""
        if self.on_delete:
            self.on_delete(self.idea)


class QuickCaptureWidget(StosOSPanel):
    """Quick idea capture widget for fast input"""
    
    def __init__(self, on_save: Callable = None, **kwargs):
        super().__init__(title="💡 Quick Capture", **kwargs)
        
        self.on_save = on_save
        self.size_hint_y = None
        self.height = dp(180)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the quick capture UI"""
        capture_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Idea input
        self.idea_input = StosOSTextInput(
            placeholder="What's your idea? Type here for quick capture...",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        capture_layout.add_widget(self.idea_input)
        
        # Tags input
        self.tags_input = StosOSTextInput(
            placeholder="Tags (comma-separated, e.g., physics, experiment, research)",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        capture_layout.add_widget(self.tags_input)
        
        # Action buttons
        button_layout = BoxLayout(
            orientation='horizontal', 
            spacing=StosOSTheme.get_spacing('md'),
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height')
        )
        
        clear_btn = StosOSButton(
            text="Clear",
            button_type="secondary",
            size_hint_x=0.3
        )
        clear_btn.bind(on_press=self._clear_inputs)
        button_layout.add_widget(clear_btn)
        
        save_btn = StosOSButton(
            text="💾 Save Idea",
            button_type="accent",
            size_hint_x=0.7
        )
        save_btn.bind(on_press=self._save_idea)
        button_layout.add_widget(save_btn)
        
        capture_layout.add_widget(button_layout)
        
        self.add_widget(capture_layout)
    
    def _clear_inputs(self, *args):
        """Clear all input fields"""
        self.idea_input.text = ""
        self.tags_input.text = ""
        self.idea_input.focus = True
    
    def _save_idea(self, *args):
        """Save the captured idea"""
        content = self.idea_input.text.strip()
        if not content:
            return
        
        # Parse tags
        tags = []
        if self.tags_input.text.strip():
            tags = [tag.strip().lower() for tag in self.tags_input.text.split(',') if tag.strip()]
        
        # Create idea
        idea = Idea(content=content, tags=tags)
        
        # Call save callback
        if self.on_save:
            self.on_save(idea)
        
        # Clear inputs after save
        self._clear_inputs()


class IdeaFormPopup(StosOSPopup):
    """Popup for creating/editing ideas with rich text support"""
    
    def __init__(self, idea: Idea = None, on_save: Callable = None, **kwargs):
        self.idea = idea
        self.on_save = on_save
        self.is_editing = idea is not None
        
        title = "Edit Idea" if self.is_editing else "New Idea"
        super().__init__(
            title=title,
            size_hint=(0.9, 0.8),
            auto_dismiss=False,
            **kwargs
        )
        
        self._build_form()
    
    def _build_form(self):
        """Build the idea form with rich text support"""
        form_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Content input (multiline for rich text)
        content_label = StosOSLabel(text="Idea Content:", size_hint_y=None, height=dp(25))
        form_layout.add_widget(content_label)
        
        self.content_input = StosOSTextInput(
            placeholder="Describe your idea in detail...",
            text=self.idea.content if self.is_editing else "",
            multiline=True,
            size_hint_y=None,
            height=dp(200)
        )
        form_layout.add_widget(self.content_input)
        
        # Tags input with suggestions
        tags_label = StosOSLabel(text="Tags (comma-separated):", size_hint_y=None, height=dp(25))
        form_layout.add_widget(tags_label)
        
        self.tags_input = StosOSTextInput(
            placeholder="e.g., physics, experiment, research, breakthrough",
            text=', '.join(self.idea.tags) if self.is_editing else "",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        form_layout.add_widget(self.tags_input)
        
        # Common tag suggestions
        suggestions_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=StosOSTheme.get_spacing('xs')
        )
        
        common_tags = ["physics", "math", "chemistry", "research", "experiment", "theory", "project"]
        for tag in common_tags:
            tag_btn = StosOSButton(
                text=f"#{tag}",
                button_type="secondary",
                size_hint_x=None,
                width=dp(80),
                font_size=StosOSTheme.get_font_size('caption')
            )
            tag_btn.bind(on_press=lambda x, t=tag: self._add_tag_suggestion(t))
            suggestions_layout.add_widget(tag_btn)
        
        form_layout.add_widget(suggestions_layout)
        
        # Attachments section (placeholder for future file attachment support)
        if self.is_editing and self.idea.attachments:
            attachments_label = StosOSLabel(
                text=f"Attachments: {len(self.idea.attachments)} file(s)",
                size_hint_y=None,
                height=dp(25)
            )
            form_layout.add_widget(attachments_label)
        
        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal', 
            spacing=StosOSTheme.get_spacing('md'),
            size_hint_y=None, 
            height=StosOSTheme.get_dimension('button_height')
        )
        
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
        save_btn.bind(on_press=self._save_idea)
        button_layout.add_widget(save_btn)
        
        form_layout.add_widget(button_layout)
        
        self.content = form_layout
    
    def _add_tag_suggestion(self, tag: str):
        """Add suggested tag to tags input"""
        current_tags = self.tags_input.text.strip()
        if current_tags:
            if tag not in current_tags.lower():
                self.tags_input.text = f"{current_tags}, {tag}"
        else:
            self.tags_input.text = tag
    
    def _save_idea(self, *args):
        """Save the idea"""
        try:
            # Validate content
            content = self.content_input.text.strip()
            if not content:
                # Show error - content required
                return
            
            # Parse tags
            tags = []
            if self.tags_input.text.strip():
                tags = [tag.strip().lower() for tag in self.tags_input.text.split(',') if tag.strip()]
            
            # Create or update idea
            if self.is_editing:
                self.idea.update_content(content)
                self.idea.tags = tags
            else:
                self.idea = Idea(content=content, tags=tags)
            
            # Call save callback
            if self.on_save:
                self.on_save(self.idea)
            
            self.dismiss()
            
        except Exception as e:
            logging.error(f"Error saving idea: {e}")


class ExportOptionsPopup(StosOSPopup):
    """Popup for selecting export options"""
    
    def __init__(self, idea: Idea, on_export: Callable = None, **kwargs):
        self.idea = idea
        self.on_export = on_export
        
        super().__init__(
            title="Export Idea",
            size_hint=(0.6, 0.5),
            auto_dismiss=False,
            **kwargs
        )
        
        self._build_ui()
    
    def _build_ui(self):
        """Build export options UI"""
        export_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Export format selection
        format_label = StosOSLabel(
            text="Select export format:",
            size_hint_y=None,
            height=dp(30)
        )
        export_layout.add_widget(format_label)
        
        # Format buttons
        format_buttons_layout = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        # Markdown export
        markdown_btn = StosOSButton(
            text="📝 Export as Markdown (.md)",
            button_type="accent"
        )
        markdown_btn.bind(on_press=lambda x: self._export_format('markdown'))
        format_buttons_layout.add_widget(markdown_btn)
        
        # Text export
        text_btn = StosOSButton(
            text="📄 Export as Text (.txt)",
            button_type="secondary"
        )
        text_btn.bind(on_press=lambda x: self._export_format('text'))
        format_buttons_layout.add_widget(text_btn)
        
        # JSON export (for backup/import)
        json_btn = StosOSButton(
            text="🔧 Export as JSON (.json)",
            button_type="secondary"
        )
        json_btn.bind(on_press=lambda x: self._export_format('json'))
        format_buttons_layout.add_widget(json_btn)
        
        export_layout.add_widget(format_buttons_layout)
        
        # Cancel button
        cancel_btn = StosOSButton(
            text="Cancel",
            button_type="secondary"
        )
        cancel_btn.bind(on_press=self.dismiss)
        export_layout.add_widget(cancel_btn)
        
        self.content = export_layout
    
    def _export_format(self, format_type: str):
        """Handle export format selection"""
        if self.on_export:
            self.on_export(self.idea, format_type)
        self.dismiss()


class IdeaBoard(BaseModule):
    """
    Idea Board Module
    
    Provides comprehensive idea management functionality including quick capture,
    tag system, search/filtering, rich text editing, and export capabilities.
    """
    
    def __init__(self):
        super().__init__(
            module_id="idea_board",
            display_name="Idea Board",
            icon="💡"
        )
        
        self.db_manager = None
        self.ideas = []
        self.filtered_ideas = []
        self.current_filter = {"tag": None}
        self.current_sort = "updated_at"
        self.search_term = ""
        
        # UI components
        self.quick_capture = None
        self.idea_list_layout = None
        self.stats_panel = None
        self.filter_panel = None
        self.search_input = None
    
    def initialize(self) -> bool:
        """Initialize the idea board module"""
        try:
            self.db_manager = DatabaseManager()
            self._load_ideas()
            self._initialized = True
            self.logger.info("Idea Board module initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Idea Board: {e}")
            self.handle_error(e, "initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Get the idea board screen"""
        if self.screen_widget is None:
            self.screen_widget = Screen(name=self.module_id)
            self._build_ui()
        return self.screen_widget
    
    def _build_ui(self):
        """Build the idea board UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Header with title and new idea button
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        title_label = StosOSLabel(
            text="💡 Idea Board",
            label_type="title",
            size_hint_x=0.7
        )
        header_layout.add_widget(title_label)
        
        new_idea_btn = StosOSButton(
            text="+ New Idea",
            button_type="accent",
            size_hint_x=0.3
        )
        new_idea_btn.bind(on_press=self._show_new_idea_form)
        header_layout.add_widget(new_idea_btn)
        
        main_layout.add_widget(header_layout)
        
        # Quick capture widget
        self.quick_capture = QuickCaptureWidget(on_save=self._save_quick_idea)
        main_layout.add_widget(self.quick_capture)
        
        # Statistics panel
        self._build_stats_panel()
        main_layout.add_widget(self.stats_panel)
        
        # Search and filter panel
        self._build_filter_panel()
        main_layout.add_widget(self.filter_panel)
        
        # Idea list
        self._build_idea_list()
        main_layout.add_widget(self.idea_list_layout)
        
        self.screen_widget.add_widget(main_layout)
    
    def _build_stats_panel(self):
        """Build the statistics panel"""
        self.stats_panel = StosOSPanel(
            title="Statistics",
            size_hint_y=None,
            height=dp(100)
        )
        
        stats_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Total ideas
        total_label = StosOSLabel(
            text="Total: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(total_label)
        
        # Ideas this week
        week_label = StosOSLabel(
            text="This Week: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(week_label)
        
        # Total tags
        tags_label = StosOSLabel(
            text="Tags: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(tags_label)
        
        # Recent activity
        recent_label = StosOSLabel(
            text="Recent: 0",
            halign='center',
            size_hint_x=0.25
        )
        stats_layout.add_widget(recent_label)
        
        self.stats_panel.add_widget(stats_layout)
        
        # Store references for updates
        self.stats_labels = {
            'total': total_label,
            'week': week_label,
            'tags': tags_label,
            'recent': recent_label
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
            placeholder="Search ideas by content or tags...",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        self.search_input.bind(text=self._on_search_text_change)
        filter_layout.add_widget(self.search_input)
        
        # Filter buttons row
        filter_buttons_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('xs'))
        
        # Tag filter
        self.tag_filter_btn = StosOSToggleButton(text="All Tags")
        self.tag_filter_btn.bind(on_press=self._show_tag_filter)
        filter_buttons_layout.add_widget(self.tag_filter_btn)
        
        # Sort button
        self.sort_btn = StosOSButton(text="Sort: Recent", button_type="secondary")
        self.sort_btn.bind(on_press=self._show_sort_options)
        filter_buttons_layout.add_widget(self.sort_btn)
        
        # Export all button
        export_all_btn = StosOSButton(text="📤 Export All", button_type="secondary")
        export_all_btn.bind(on_press=self._export_all_ideas)
        filter_buttons_layout.add_widget(export_all_btn)
        
        filter_layout.add_widget(filter_buttons_layout)
        
        self.filter_panel.add_widget(filter_layout)
    
    def _build_idea_list(self):
        """Build the scrollable idea list"""
        self.idea_list_layout = StosOSScrollView()
        
        self.idea_container = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None
        )
        self.idea_container.bind(minimum_height=self.idea_container.setter('height'))
        
        self.idea_list_layout.add_widget(self.idea_container)
        
        # Initial idea list population
        self._refresh_idea_list()    def 
_load_ideas(self):
        """Load ideas from database"""
        try:
            self.ideas = self.db_manager.get_ideas()
            self._apply_filters_and_sort()
            self.logger.debug(f"Loaded {len(self.ideas)} ideas")
        except Exception as e:
            self.logger.error(f"Failed to load ideas: {e}")
            self.ideas = []
            self.filtered_ideas = []
    
    def _apply_filters_and_sort(self):
        """Apply current filters and sorting to idea list"""
        # Start with all ideas
        filtered = self.ideas[:]
        
        # Apply search filter
        if self.search_term:
            filtered = [
                idea for idea in filtered
                if self.search_term.lower() in idea.content.lower() or
                   any(self.search_term.lower() in tag for tag in idea.tags)
            ]
        
        # Apply tag filter
        if self.current_filter["tag"]:
            filtered = [idea for idea in filtered if self.current_filter["tag"] in idea.tags]
        
        # Apply sorting
        if self.current_sort == "updated_at":
            filtered.sort(key=lambda i: i.updated_at, reverse=True)
        elif self.current_sort == "created_at":
            filtered.sort(key=lambda i: i.created_at, reverse=True)
        elif self.current_sort == "content":
            filtered.sort(key=lambda i: i.content.lower())
        elif self.current_sort == "tags":
            filtered.sort(key=lambda i: len(i.tags), reverse=True)
        
        self.filtered_ideas = filtered
    
    def _refresh_idea_list(self):
        """Refresh the idea list UI"""
        # Clear existing idea cards
        self.idea_container.clear_widgets()
        
        # Add idea cards
        for idea in self.filtered_ideas:
            idea_card = IdeaCard(
                idea=idea,
                on_edit=self._edit_idea,
                on_delete=self._delete_idea,
                on_export=self._export_single_idea
            )
            self.idea_container.add_widget(idea_card)
        
        # Show empty state if no ideas
        if not self.filtered_ideas:
            empty_label = StosOSLabel(
                text="No ideas found" if self.search_term or self.current_filter["tag"] 
                      else "No ideas yet. Capture your first brilliant thought!",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.idea_container.add_widget(empty_label)
        
        # Update statistics
        self._update_statistics()
    
    def _update_statistics(self):
        """Update the statistics panel"""
        if not hasattr(self, 'stats_labels'):
            return
        
        total_ideas = len(self.ideas)
        
        # Ideas this week
        week_ago = datetime.now() - timedelta(days=7)
        week_ideas = len([i for i in self.ideas if i.created_at >= week_ago])
        
        # Unique tags
        all_tags = set()
        for idea in self.ideas:
            all_tags.update(idea.tags)
        unique_tags = len(all_tags)
        
        # Recent activity (last 24 hours)
        day_ago = datetime.now() - timedelta(days=1)
        recent_ideas = len([i for i in self.ideas if i.updated_at >= day_ago])
        
        self.stats_labels['total'].text = f"Total: {total_ideas}"
        self.stats_labels['week'].text = f"This Week: {week_ideas}"
        self.stats_labels['tags'].text = f"Tags: {unique_tags}"
        self.stats_labels['recent'].text = f"Recent: {recent_ideas}"
    
    def _on_search_text_change(self, instance, text):
        """Handle search text change"""
        self.search_term = text.strip()
        self._apply_filters_and_sort()
        self._refresh_idea_list()
    
    def _show_new_idea_form(self, *args):
        """Show form for creating new idea"""
        popup = IdeaFormPopup(on_save=self._save_new_idea)
        popup.open_with_animation()
    
    def _save_quick_idea(self, idea: Idea):
        """Save quick captured idea to database"""
        try:
            if self.db_manager.create_idea(idea):
                self.ideas.append(idea)
                self._apply_filters_and_sort()
                self._refresh_idea_list()
                self.logger.info(f"Quick captured idea: {idea.content[:50]}...")
                
                # Show success feedback
                StosOSAnimations.pulse(self.quick_capture, scale=1.02, duration=0.3)
            else:
                self.logger.error("Failed to save quick idea to database")
        except Exception as e:
            self.logger.error(f"Error saving quick idea: {e}")
            self.handle_error(e, "save_quick_idea")
    
    def _save_new_idea(self, idea: Idea):
        """Save new idea to database"""
        try:
            if self.db_manager.create_idea(idea):
                self.ideas.append(idea)
                self._apply_filters_and_sort()
                self._refresh_idea_list()
                self.logger.info(f"Created new idea: {idea.content[:50]}...")
            else:
                self.logger.error("Failed to save new idea to database")
        except Exception as e:
            self.logger.error(f"Error saving new idea: {e}")
            self.handle_error(e, "save_new_idea")
    
    def _edit_idea(self, idea: Idea):
        """Show form for editing existing idea"""
        popup = IdeaFormPopup(idea=idea, on_save=self._save_edited_idea)
        popup.open_with_animation()
    
    def _save_edited_idea(self, idea: Idea):
        """Save edited idea to database"""
        try:
            if self.db_manager.update_idea(idea):
                self._apply_filters_and_sort()
                self._refresh_idea_list()
                self.logger.info(f"Updated idea: {idea.content[:50]}...")
            else:
                self.logger.error("Failed to update idea in database")
        except Exception as e:
            self.logger.error(f"Error updating idea: {e}")
            self.handle_error(e, "save_edited_idea")
    
    def _delete_idea(self, idea: Idea):
        """Delete idea with confirmation"""
        def confirm_delete():
            try:
                if self.db_manager.delete_idea(idea.id):
                    self.ideas = [i for i in self.ideas if i.id != idea.id]
                    self._apply_filters_and_sort()
                    self._refresh_idea_list()
                    self.logger.info(f"Deleted idea: {idea.content[:50]}...")
                else:
                    self.logger.error("Failed to delete idea from database")
            except Exception as e:
                self.logger.error(f"Error deleting idea: {e}")
                self.handle_error(e, "delete_idea")
        
        # Show confirmation popup
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        preview = idea.content[:100] + "..." if len(idea.content) > 100 else idea.content
        message = StosOSLabel(
            text=f"Are you sure you want to delete this idea?\n\n'{preview}'",
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
            size_hint=(0.7, 0.5)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        delete_btn.bind(on_press=lambda x: (confirm_delete(), popup.dismiss()))
        
        popup.open_with_animation()
    
    def _export_single_idea(self, idea: Idea):
        """Show export options for single idea"""
        popup = ExportOptionsPopup(idea=idea, on_export=self._perform_export)
        popup.open_with_animation()
    
    def _export_all_ideas(self, *args):
        """Export all ideas"""
        if not self.ideas:
            # Show message - no ideas to export
            return
        
        # Show format selection for all ideas
        def export_all_format(format_type):
            self._perform_bulk_export(self.ideas, format_type)
        
        # Create simple format selection popup
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        content.add_widget(StosOSLabel(
            text=f"Export all {len(self.ideas)} ideas:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        markdown_btn = StosOSButton(text="📝 Markdown Collection", button_type="accent")
        markdown_btn.bind(on_press=lambda x: (export_all_format('markdown_collection'), popup.dismiss()))
        content.add_widget(markdown_btn)
        
        json_btn = StosOSButton(text="🔧 JSON Backup", button_type="secondary")
        json_btn.bind(on_press=lambda x: (export_all_format('json_backup'), popup.dismiss()))
        content.add_widget(json_btn)
        
        cancel_btn = StosOSButton(text="Cancel", button_type="secondary")
        content.add_widget(cancel_btn)
        
        popup = StosOSPopup(
            title="Export All Ideas",
            content=content,
            size_hint=(0.6, 0.5)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open_with_animation()
    
    def _perform_export(self, idea: Idea, format_type: str):
        """Perform the actual export of a single idea"""
        try:
            # Create exports directory if it doesn't exist
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            safe_title = "".join(c for c in idea.content[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format_type == 'markdown':
                filename = f"{export_dir}/idea_{safe_title}_{timestamp}.md"
                content = self._generate_markdown_content(idea)
            elif format_type == 'text':
                filename = f"{export_dir}/idea_{safe_title}_{timestamp}.txt"
                content = self._generate_text_content(idea)
            elif format_type == 'json':
                filename = f"{export_dir}/idea_{safe_title}_{timestamp}.json"
                content = self._generate_json_content(idea)
            else:
                return
            
            # Write file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Exported idea to {filename}")
            
            # Show success message
            self._show_export_success(filename)
            
        except Exception as e:
            self.logger.error(f"Error exporting idea: {e}")
            self.handle_error(e, "export_idea")
    
    def _perform_bulk_export(self, ideas: List[Idea], format_type: str):
        """Perform bulk export of multiple ideas"""
        try:
            # Create exports directory if it doesn't exist
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format_type == 'markdown_collection':
                filename = f"{export_dir}/ideas_collection_{timestamp}.md"
                content = self._generate_markdown_collection(ideas)
            elif format_type == 'json_backup':
                filename = f"{export_dir}/ideas_backup_{timestamp}.json"
                content = self._generate_json_backup(ideas)
            else:
                return
            
            # Write file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Exported {len(ideas)} ideas to {filename}")
            
            # Show success message
            self._show_export_success(filename)
            
        except Exception as e:
            self.logger.error(f"Error exporting ideas: {e}")
            self.handle_error(e, "bulk_export_ideas")
    
    def _generate_markdown_content(self, idea: Idea) -> str:
        """Generate markdown content for a single idea"""
        content = f"# Idea: {idea.content[:50]}{'...' if len(idea.content) > 50 else ''}\n\n"
        content += f"**Created:** {idea.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Updated:** {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if idea.tags:
            content += f"**Tags:** {', '.join(f'#{tag}' for tag in idea.tags)}\n\n"
        
        content += "## Content\n\n"
        content += idea.content + "\n\n"
        
        if idea.attachments:
            content += "## Attachments\n\n"
            for attachment in idea.attachments:
                content += f"- {attachment}\n"
            content += "\n"
        
        content += "---\n"
        content += f"*Exported from StosOS Idea Board on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return content
    
    def _generate_text_content(self, idea: Idea) -> str:
        """Generate plain text content for a single idea"""
        content = f"IDEA: {idea.content[:50]}{'...' if len(idea.content) > 50 else ''}\n"
        content += "=" * 60 + "\n\n"
        content += f"Created: {idea.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"Updated: {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if idea.tags:
            content += f"Tags: {', '.join(idea.tags)}\n"
        
        content += "\nCONTENT:\n"
        content += "-" * 20 + "\n"
        content += idea.content + "\n\n"
        
        if idea.attachments:
            content += "ATTACHMENTS:\n"
            content += "-" * 20 + "\n"
            for attachment in idea.attachments:
                content += f"- {attachment}\n"
            content += "\n"
        
        content += f"Exported from StosOS Idea Board on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return content
    
    def _generate_json_content(self, idea: Idea) -> str:
        """Generate JSON content for a single idea"""
        import json
        
        data = {
            "idea": idea.to_dict(),
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "exported_by": "StosOS Idea Board",
                "format_version": "1.0"
            }
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _generate_markdown_collection(self, ideas: List[Idea]) -> str:
        """Generate markdown collection of multiple ideas"""
        content = f"# StosOS Ideas Collection\n\n"
        content += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Total Ideas:** {len(ideas)}\n\n"
        
        # Table of contents
        content += "## Table of Contents\n\n"
        for i, idea in enumerate(ideas, 1):
            title = idea.content[:50] + "..." if len(idea.content) > 50 else idea.content
            title = title.replace('\n', ' ').strip()
            content += f"{i}. [{title}](#idea-{i})\n"
        content += "\n---\n\n"
        
        # Individual ideas
        for i, idea in enumerate(ideas, 1):
            content += f"## Idea {i}\n\n"
            content += f"**Created:** {idea.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**Updated:** {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if idea.tags:
                content += f"**Tags:** {', '.join(f'#{tag}' for tag in idea.tags)}\n"
            
            content += "\n### Content\n\n"
            content += idea.content + "\n\n"
            
            if idea.attachments:
                content += "### Attachments\n\n"
                for attachment in idea.attachments:
                    content += f"- {attachment}\n"
                content += "\n"
            
            content += "---\n\n"
        
        content += f"*Collection exported from StosOS Idea Board*\n"
        
        return content
    
    def _generate_json_backup(self, ideas: List[Idea]) -> str:
        """Generate JSON backup of multiple ideas"""
        import json
        
        data = {
            "ideas": [idea.to_dict() for idea in ideas],
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "exported_by": "StosOS Idea Board",
                "format_version": "1.0",
                "total_ideas": len(ideas)
            }
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _show_export_success(self, filename: str):
        """Show export success message"""
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        message = StosOSLabel(
            text=f"Successfully exported to:\n{filename}",
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        content.add_widget(message)
        
        ok_btn = StosOSButton(text="OK", button_type="accent")
        content.add_widget(ok_btn)
        
        popup = StosOSPopup(
            title="Export Complete",
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open_with_animation()
    
    def _show_tag_filter(self, *args):
        """Show tag filter options"""
        # Get all unique tags
        all_tags = set()
        for idea in self.ideas:
            all_tags.update(idea.tags)
        
        if not all_tags:
            return
        
        # Create tag selection popup
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # All tags option
        all_btn = StosOSButton(
            text="All Tags",
            button_type="accent" if not self.current_filter["tag"] else "secondary"
        )
        all_btn.bind(on_press=lambda x: self._apply_tag_filter(None))
        content.add_widget(all_btn)
        
        # Individual tags
        scroll_view = StosOSScrollView(size_hint_y=0.7)
        tag_container = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'), size_hint_y=None)
        tag_container.bind(minimum_height=tag_container.setter('height'))
        
        for tag in sorted(all_tags):
            tag_count = sum(1 for idea in self.ideas if tag in idea.tags)
            tag_btn = StosOSButton(
                text=f"#{tag} ({tag_count})",
                button_type="accent" if self.current_filter["tag"] == tag else "secondary",
                size_hint_y=None,
                height=dp(40)
            )
            tag_btn.bind(on_press=lambda x, t=tag: self._apply_tag_filter(t))
            tag_container.add_widget(tag_btn)
        
        scroll_view.add_widget(tag_container)
        content.add_widget(scroll_view)
        
        popup = StosOSPopup(
            title="Filter by Tag",
            content=content,
            size_hint=(0.6, 0.7)
        )
        
        # Update filter button text when selection changes
        def update_and_close(tag):
            self._apply_tag_filter(tag)
            popup.dismiss()
        
        all_btn.bind(on_press=lambda x: update_and_close(None))
        for child in tag_container.children:
            if hasattr(child, 'tag'):
                child.bind(on_press=lambda x, t=child.tag: update_and_close(t))
        
        popup.open_with_animation()
    
    def _apply_tag_filter(self, tag: Optional[str]):
        """Apply tag filter"""
        self.current_filter["tag"] = tag
        
        # Update filter button text
        if tag:
            self.tag_filter_btn.text = f"#{tag}"
        else:
            self.tag_filter_btn.text = "All Tags"
        
        self._apply_filters_and_sort()
        self._refresh_idea_list()
    
    def _show_sort_options(self, *args):
        """Show sort options"""
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        sort_options = [
            ("updated_at", "Most Recent"),
            ("created_at", "Newest First"),
            ("content", "Alphabetical"),
            ("tags", "Most Tags")
        ]
        
        for sort_key, sort_label in sort_options:
            btn = StosOSButton(
                text=sort_label,
                button_type="accent" if self.current_sort == sort_key else "secondary"
            )
            btn.bind(on_press=lambda x, key=sort_key, label=sort_label: self._apply_sort(key, label))
            content.add_widget(btn)
        
        popup = StosOSPopup(
            title="Sort Ideas",
            content=content,
            size_hint=(0.5, 0.6)
        )
        
        def update_and_close(key, label):
            self._apply_sort(key, label)
            popup.dismiss()
        
        for child in content.children:
            if hasattr(child, 'sort_key'):
                child.bind(on_press=lambda x, k=child.sort_key, l=child.sort_label: update_and_close(k, l))
        
        popup.open_with_animation()
    
    def _apply_sort(self, sort_key: str, sort_label: str):
        """Apply sort option"""
        self.current_sort = sort_key
        self.sort_btn.text = f"Sort: {sort_label}"
        
        self._apply_filters_and_sort()
        self._refresh_idea_list()
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands for idea board"""
        command_lower = command.lower()
        
        if "new idea" in command_lower or "capture idea" in command_lower:
            self._show_new_idea_form()
            return True
        elif "search" in command_lower:
            # Extract search term and apply it
            search_term = command_lower.replace("search", "").strip()
            if search_term:
                self.search_input.text = search_term
            return True
        elif "export" in command_lower:
            if "all" in command_lower:
                self._export_all_ideas()
            return True
        
        return False
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        # Refresh data when activated
        self._load_ideas()
        self._refresh_idea_list()
    
    def cleanup(self):
        """Cleanup module resources"""
        super().cleanup()
        # Clear any timers or resources if needed