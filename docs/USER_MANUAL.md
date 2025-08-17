# StosOS User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Main Dashboard](#main-dashboard)
4. [Calendar Module](#calendar-module)
5. [Task Manager](#task-manager)
6. [Idea Board](#idea-board)
7. [Study Tracker](#study-tracker)
8. [Smart Home Control](#smart-home-control)
9. [Spotify Controller](#spotify-controller)
10. [Voice Assistant](#voice-assistant)
11. [System Settings](#system-settings)
12. [Power Management](#power-management)
13. [Keyboard Shortcuts](#keyboard-shortcuts)
14. [Tips and Best Practices](#tips-and-best-practices)

## Introduction

Welcome to StosOS, your personalized desktop environment designed for productivity, learning, and smart home control. StosOS combines a sleek, minimalist interface with powerful features to help you manage your studies, tasks, ideas, and connected devices.

### Key Features

- **Unified Dashboard**: Central hub for all your productivity tools
- **Calendar Integration**: Sync with Google Calendar for seamless scheduling
- **Task Management**: Organize and track your to-do items with priorities
- **Idea Capture**: Quick note-taking and idea organization system
- **Study Tracker**: Pomodoro timer and study session analytics
- **Smart Home Control**: Manage Google/Alexa connected devices
- **Music Control**: Spotify integration with voice commands
- **AI Voice Assistant**: Natural language control of all features
- **Touch Optimized**: Designed for 7-inch touchscreen interfaces

## Getting Started

### First Launch

When StosOS starts for the first time, you'll see:

1. **Animated Branding Screen**: "StosOS X" logo with smooth transitions
2. **Initial Setup Wizard**: Configure basic settings and preferences
3. **API Authentication**: Connect to Google, Spotify, and other services
4. **Main Dashboard**: Your central control hub

### Navigation Basics

- **Touch**: Tap buttons and interface elements
- **Swipe**: Navigate between screens and modules
- **Voice**: Say "Stos" followed by commands
- **Long Press**: Access context menus and additional options

### Interface Elements

- **Module Tiles**: Large buttons for each major feature
- **Status Bar**: Shows time, connectivity, and system status
- **Navigation Bar**: Quick access to home and settings
- **Notification Area**: Alerts and system messages

## Main Dashboard

The dashboard is your central hub, providing quick access to all StosOS modules and system information.

### Dashboard Layout

```
┌─────────────────────────────────────────┐
│  StosOS Dashboard    [Time] [Status]    │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │Calendar │  │  Tasks  │  │  Ideas  │  │
│  │   📅    │  │   ✓     │  │   💡    │  │
│  └─────────┘  └─────────┘  └─────────┘  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ Study   │  │Smart    │  │ Spotify │  │
│  │Tracker  │  │Home     │  │   🎵    │  │
│  └─────────┘  └─────────┘  └─────────┘  │
├─────────────────────────────────────────┤
│  Quick Actions: [Voice] [Settings]      │
└─────────────────────────────────────────┘
```

### Dashboard Features

1. **Module Status Indicators**
   - Green: Module active and connected
   - Yellow: Module active but with warnings
   - Red: Module offline or error state
   - Gray: Module disabled

2. **Quick Information**
   - Next calendar event
   - Pending task count
   - Current study session status
   - Smart home device summary

3. **System Status**
   - Network connectivity
   - API service status
   - System performance indicators
   - Battery/power status

### Customizing the Dashboard

1. **Rearrange Modules**
   - Long press on module tile
   - Drag to new position
   - Release to place

2. **Module Settings**
   - Tap gear icon on module tile
   - Configure module-specific options
   - Enable/disable modules

3. **Dashboard Themes**
   - Access through Settings > Appearance
   - Choose from dark, light, or custom themes
   - Adjust colors and fonts

## Calendar Module

The Calendar module provides comprehensive schedule management with Google Calendar integration.

### Calendar Views

1. **Day View**
   - Hourly timeline for current day
   - Event details and duration
   - Quick event creation

2. **Week View**
   - 7-day overview with events
   - Drag and drop event scheduling
   - Multi-day event support

3. **Month View**
   - Full month calendar grid
   - Event indicators and counts
   - Quick navigation between months

4. **Agenda View**
   - List of upcoming events
   - Detailed event information
   - Search and filter options

### Creating Events

1. **Quick Add**
   - Tap "+" button or empty time slot
   - Enter event title and basic details
   - Save with default settings

2. **Detailed Event Creation**
   - Use "New Event" button
   - Set title, description, location
   - Configure date, time, and duration
   - Add attendees and reminders
   - Set recurrence patterns

3. **Voice Event Creation**
   - Say "Stos, add event"
   - Speak event details naturally
   - Confirm details before saving

### Event Management

1. **Editing Events**
   - Tap event to view details
   - Use "Edit" button to modify
   - Change any event properties
   - Save changes to sync with Google Calendar

2. **Deleting Events**
   - Open event details
   - Tap "Delete" button
   - Confirm deletion

3. **Event Reminders**
   - Set multiple reminders per event
   - Choose notification timing
   - Configure reminder methods

### Calendar Settings

```json
{
  "calendar": {
    "default_view": "week",
    "sync_interval": 15,
    "show_weekends": true,
    "start_week_on": "monday",
    "default_event_duration": 60,
    "reminder_defaults": [15, 60]
  }
}
```

## Task Manager

The Task Manager helps you organize, prioritize, and track your to-do items with advanced filtering and categorization.

### Task Organization

1. **Categories**
   - Academic: Physics, Chemistry, Mathematics, Biology
   - Personal: Health, Finance, Hobbies
   - Work: Projects, Meetings, Deadlines
   - Custom: Create your own categories

2. **Priority Levels**
   - **HIGH**: Urgent and important tasks
   - **MEDIUM**: Important but not urgent
   - **LOW**: Nice to have, low priority

3. **Task Status**
   - **Pending**: Not started
   - **In Progress**: Currently working on
   - **Completed**: Finished tasks
   - **Cancelled**: No longer needed

### Creating Tasks

1. **Quick Task Creation**
   ```
   Tap "+" button → Enter title → Set priority → Save
   ```

2. **Detailed Task Creation**
   - Title and description
   - Due date and time
   - Priority level
   - Category assignment
   - Estimated duration
   - Subtasks and dependencies

3. **Voice Task Creation**
   ```
   "Stos, add task: Study physics chapter 5 for tomorrow"
   "Stos, create high priority task: Submit assignment by Friday"
   ```

### Task Views and Filters

1. **List View**
   - All tasks in chronological order
   - Filter by category, priority, status
   - Sort by due date, priority, or creation date

2. **Kanban Board**
   - Visual task organization
   - Drag tasks between status columns
   - Quick status updates

3. **Calendar Integration**
   - View tasks alongside calendar events
   - Schedule task work sessions
   - Deadline visualization

4. **Today View**
   - Tasks due today
   - Overdue tasks
   - Scheduled work sessions

### Task Analytics

1. **Completion Statistics**
   - Daily/weekly completion rates
   - Category-wise performance
   - Priority distribution analysis

2. **Time Tracking**
   - Estimated vs. actual time spent
   - Productivity patterns
   - Efficiency metrics

3. **Progress Visualization**
   - Charts and graphs
   - Trend analysis
   - Goal achievement tracking

## Idea Board

The Idea Board provides a fast, distraction-free way to capture and organize your thoughts and inspirations.

### Capturing Ideas

1. **Quick Capture**
   - Tap "New Idea" button
   - Type or speak your idea
   - Auto-save with timestamp

2. **Voice Capture**
   ```
   "Stos, note: Interesting concept about renewable energy storage"
   "Stos, idea: Mobile app for study group coordination"
   ```

3. **Rich Text Ideas**
   - Add formatting (bold, italic, lists)
   - Insert links and references
   - Attach images or files

### Organizing Ideas

1. **Tagging System**
   - Add multiple tags per idea
   - Create custom tag categories
   - Color-coded tag visualization

2. **Categories**
   - Academic research
   - Project ideas
   - Personal thoughts
   - Business concepts
   - Creative inspiration

3. **Search and Filter**
   - Full-text search across all ideas
   - Filter by tags, date, category
   - Advanced search with operators

### Idea Development

1. **Expanding Ideas**
   - Add detailed descriptions
   - Create action items
   - Link related ideas
   - Add research notes

2. **Collaboration**
   - Share ideas via export
   - Create presentation formats
   - Generate reports

3. **Implementation Tracking**
   - Convert ideas to tasks
   - Track development progress
   - Mark ideas as implemented

### Export Options

1. **Markdown Export**
   - Clean, readable format
   - Preserve formatting and links
   - Compatible with other tools

2. **PDF Generation**
   - Professional presentation format
   - Include images and formatting
   - Print-ready output

3. **Text Export**
   - Simple text format
   - Easy copy/paste
   - Universal compatibility

## Study Tracker

The Study Tracker helps you monitor your learning progress with time tracking, analytics, and motivation features.

### Study Sessions

1. **Starting a Session**
   - Select subject/topic
   - Choose session type (focused study, review, practice)
   - Set target duration
   - Start timer

2. **Pomodoro Timer**
   - 25-minute focused work sessions
   - 5-minute short breaks
   - 15-30 minute long breaks
   - Customizable intervals

3. **Session Management**
   - Pause/resume sessions
   - Add notes during breaks
   - Track completed tasks
   - Rate session effectiveness

### Study Analytics

1. **Time Tracking**
   - Daily study hours
   - Subject-wise time distribution
   - Weekly/monthly trends
   - Goal vs. actual comparison

2. **Performance Metrics**
   - Study streak counters
   - Consistency ratings
   - Productivity scores
   - Improvement trends

3. **Subject Analysis**
   - Time spent per subject
   - Difficulty ratings
   - Progress indicators
   - Weak area identification

### Goal Setting

1. **Daily Goals**
   - Target study hours
   - Subject-specific goals
   - Task completion targets
   - Break adherence goals

2. **Weekly/Monthly Goals**
   - Long-term study targets
   - Skill development goals
   - Exam preparation milestones
   - Habit formation objectives

3. **Progress Tracking**
   - Visual progress bars
   - Achievement badges
   - Milestone celebrations
   - Streak maintenance

### Motivation Features

1. **Achievement System**
   - Study streak badges
   - Time milestone rewards
   - Consistency achievements
   - Subject mastery levels

2. **Progress Visualization**
   - Charts and graphs
   - Calendar heat maps
   - Trend analysis
   - Comparative statistics

3. **Motivational Content**
   - Inspirational quotes
   - Success stories
   - Progress celebrations
   - Encouragement messages

## Smart Home Control

The Smart Home module provides unified control of your Google Assistant and Alexa-connected devices.

### Device Discovery

1. **Automatic Discovery**
   - Scans for connected devices on startup
   - Detects Google and Alexa devices
   - Updates device list periodically

2. **Manual Device Addition**
   - Add devices by IP address
   - Configure device types and capabilities
   - Set custom device names

3. **Device Categories**
   - Lights and switches
   - Thermostats and climate control
   - Entertainment devices
   - Security systems
   - Custom device types

### Device Control

1. **Light Control**
   - On/off switches
   - Brightness adjustment
   - Color temperature control
   - RGB color selection (if supported)

2. **Climate Control**
   - Temperature adjustment
   - Mode selection (heat/cool/auto)
   - Fan speed control
   - Schedule programming

3. **Entertainment Control**
   - Volume adjustment
   - Playback control
   - Source selection
   - Multi-room audio

### Scene Management

1. **Predefined Scenes**
   - Study Mode: Optimal lighting and temperature
   - Sleep Mode: Dim lights, comfortable temperature
   - Party Mode: Bright lights, music on
   - Away Mode: Security settings, energy saving

2. **Custom Scenes**
   - Create personalized device configurations
   - Set multiple device states simultaneously
   - Schedule scene activation
   - Voice-activated scenes

3. **Scene Automation**
   - Time-based activation
   - Sensor-triggered scenes
   - Conditional logic
   - Integration with other modules

### Voice Control

```
"Stos, turn on the lights"
"Stos, set temperature to 22 degrees"
"Stos, activate study mode"
"Stos, play music in the living room"
"Stos, turn off all devices"
```

## Spotify Controller

The Spotify Controller provides comprehensive music control with voice commands and device selection.

### Music Playback

1. **Basic Controls**
   - Play/pause current track
   - Skip to next/previous track
   - Adjust volume
   - Shuffle and repeat modes

2. **Track Information**
   - Current song details
   - Album artwork display
   - Artist and album information
   - Track progress and duration

3. **Queue Management**
   - View upcoming tracks
   - Add songs to queue
   - Reorder queue items
   - Clear queue

### Music Library

1. **Playlists**
   - Browse personal playlists
   - Access liked songs
   - Discover weekly playlists
   - Create new playlists

2. **Recently Played**
   - View listening history
   - Quickly restart recent tracks
   - Discover patterns in listening habits

3. **Search and Discovery**
   - Search for songs, artists, albums
   - Browse by genre or mood
   - Explore new releases
   - Get personalized recommendations

### Device Selection

1. **Available Devices**
   - Spotify Connect devices
   - Alexa-connected speakers
   - Computer speakers
   - Mobile devices

2. **Multi-Room Audio**
   - Play on multiple devices
   - Synchronize playback
   - Control volume per device
   - Create speaker groups

### Voice Music Control

```
"Stos, play some jazz music"
"Stos, skip this song"
"Stos, play my study playlist"
"Stos, turn up the volume"
"Stos, play music on the kitchen speaker"
"Stos, what song is this?"
```

## Voice Assistant

The AI-powered voice assistant provides natural language control of all StosOS features.

### Activation

1. **Wake Words**
   - "Stos" (primary)
   - "Hey Stos" (alternative)
   - "Computer" (fallback)

2. **Visual Indicators**
   - Microphone icon activation
   - Listening animation
   - Processing indicator
   - Response confirmation

### Command Categories

1. **System Navigation**
   ```
   "Stos, open calendar"
   "Stos, show my tasks"
   "Stos, go to dashboard"
   "Stos, open settings"
   ```

2. **Task Management**
   ```
   "Stos, add task: Review chemistry notes"
   "Stos, what are my tasks for today?"
   "Stos, mark task as complete"
   "Stos, show high priority tasks"
   ```

3. **Calendar Control**
   ```
   "Stos, what's my next meeting?"
   "Stos, add event: Math exam tomorrow at 10 AM"
   "Stos, show today's schedule"
   "Stos, when is my physics class?"
   ```

4. **Study Assistance**
   ```
   "Stos, start a study session"
   "Stos, set a 25-minute timer"
   "Stos, how long have I studied today?"
   "Stos, what's the formula for kinetic energy?"
   ```

5. **Smart Home Control**
   ```
   "Stos, turn on the lights"
   "Stos, set temperature to 22 degrees"
   "Stos, activate study mode"
   "Stos, what devices are online?"
   ```

### Conversation Features

1. **Context Awareness**
   - Remembers previous commands
   - Understands follow-up questions
   - Maintains conversation context
   - Provides relevant suggestions

2. **Natural Language Processing**
   - Understands casual speech
   - Handles variations in phrasing
   - Processes complex requests
   - Provides clarifying questions

3. **Personalization**
   - Learns your preferences
   - Adapts to your speech patterns
   - Provides personalized responses
   - Remembers important information

## System Settings

Access system settings through the dashboard settings button or voice command "Stos, open settings".

### General Settings

1. **Display**
   - Brightness levels
   - Screen timeout settings
   - Orientation lock
   - Theme selection

2. **Audio**
   - Input/output device selection
   - Volume levels
   - Voice feedback settings
   - Audio quality preferences

3. **Network**
   - WiFi configuration
   - Proxy settings
   - API connection status
   - Sync preferences

### Module Settings

1. **Calendar**
   - Sync frequency
   - Default view
   - Notification settings
   - Time zone configuration

2. **Tasks**
   - Default priority
   - Auto-save settings
   - Reminder preferences
   - Category management

3. **Voice Assistant**
   - Wake word sensitivity
   - Response voice selection
   - Language preferences
   - Privacy settings

### Privacy and Security

1. **Data Management**
   - Local data storage
   - Cloud sync settings
   - Data export options
   - Privacy controls

2. **API Security**
   - Token management
   - Permission settings
   - Connection encryption
   - Access logging

## Power Management

StosOS includes intelligent power management to extend display life and optimize energy usage.

### Power States

1. **Active Mode** (100% brightness)
   - User interaction detected
   - Full functionality available
   - All modules active

2. **Dimmed Mode** (20% brightness)
   - 30 seconds of inactivity
   - Touch sensitivity maintained
   - Background processes continue

3. **Sleep Mode** (Display off)
   - 60 seconds of inactivity
   - Touch wake enabled
   - Voice wake available
   - Background sync continues

### Wake Methods

1. **Touch Wake**
   - Tap anywhere on screen
   - Immediate response
   - Returns to previous state

2. **Voice Wake**
   - Say wake word
   - Voice command processing
   - Hands-free operation

3. **Scheduled Wake**
   - Calendar event reminders
   - Task notifications
   - Study session alerts

### Power Settings

```json
{
  "power_management": {
    "dim_timeout_seconds": 30,
    "sleep_timeout_seconds": 60,
    "brightness_levels": [20, 50, 100],
    "wake_on_touch": true,
    "wake_on_voice": true,
    "scheduled_wake": true
  }
}
```

## Keyboard Shortcuts

For users with connected keyboards, StosOS supports various keyboard shortcuts.

### Global Shortcuts

- `Ctrl + H`: Go to dashboard
- `Ctrl + 1-6`: Switch to module (1=Calendar, 2=Tasks, etc.)
- `Ctrl + S`: Open settings
- `Ctrl + Q`: Quit StosOS
- `F11`: Toggle fullscreen
- `Ctrl + R`: Refresh current module

### Module-Specific Shortcuts

#### Calendar
- `N`: New event
- `T`: Go to today
- `←/→`: Navigate dates
- `1/2/3/4`: Switch views (Day/Week/Month/Agenda)

#### Tasks
- `N`: New task
- `Space`: Mark task complete
- `Del`: Delete selected task
- `F`: Filter tasks
- `S`: Search tasks

#### Voice Assistant
- `Ctrl + Space`: Activate voice assistant
- `Esc`: Cancel voice input
- `Ctrl + M`: Mute microphone

## Tips and Best Practices

### Productivity Tips

1. **Daily Routine**
   - Start with dashboard overview
   - Check calendar for the day
   - Review high-priority tasks
   - Set study session goals

2. **Voice Commands**
   - Use natural language
   - Be specific with requests
   - Confirm important actions
   - Practice common commands

3. **Organization**
   - Use consistent naming conventions
   - Regularly review and clean up data
   - Set up automated routines
   - Backup important information

### Performance Optimization

1. **System Maintenance**
   - Restart StosOS weekly
   - Clear cache regularly
   - Monitor system resources
   - Keep software updated

2. **Module Management**
   - Disable unused modules
   - Adjust sync frequencies
   - Optimize notification settings
   - Use offline modes when possible

### Troubleshooting

1. **Common Issues**
   - Check network connectivity
   - Verify API credentials
   - Review system logs
   - Restart problematic modules

2. **Getting Help**
   - Use built-in diagnostics
   - Check documentation
   - Report issues with logs
   - Join community discussions

---

**Congratulations!** You're now ready to make the most of your StosOS desktop environment. Explore the features, customize settings to your preferences, and enjoy a more productive and organized digital workspace.