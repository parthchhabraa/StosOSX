"""
Google Calendar API Service for StosOS

Handles OAuth authentication and Google Calendar API operations.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.calendar_event import CalendarEvent


class GoogleCalendarService:
    """
    Google Calendar API service for StosOS
    
    Handles OAuth authentication, calendar operations, and event synchronization.
    """
    
    # OAuth 2.0 scopes for Google Calendar
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, credentials_file: str = "config/google_credentials.json", 
                 token_file: str = "config/google_token.json"):
        """
        Initialize Google Calendar service
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON file
            token_file: Path to store OAuth token
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.logger = logging.getLogger(__name__)
        
        self.credentials = None
        self.service = None
        self._authenticated = False
        
        # Ensure config directory exists
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Load existing token if available
            if self.token_file.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), self.SCOPES
                )
            
            # If there are no valid credentials, request authorization
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # Refresh expired credentials
                    self.credentials.refresh(Request())
                    self.logger.info("Refreshed Google Calendar credentials")
                else:
                    # Request new authorization
                    if not self.credentials_file.exists():
                        self.logger.error(f"Google credentials file not found: {self.credentials_file}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                    self.logger.info("Obtained new Google Calendar credentials")
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            self._authenticated = True
            
            self.logger.info("Google Calendar service authenticated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Google Calendar: {e}")
            self._authenticated = False
            return False
    
    def is_authenticated(self) -> bool:
        """Check if service is authenticated"""
        return self._authenticated and self.service is not None
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get list of user's calendars
        
        Returns:
            List of calendar dictionaries
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return []
        
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            self.logger.debug(f"Retrieved {len(calendars)} calendars")
            return calendars
            
        except HttpError as e:
            self.logger.error(f"Failed to get calendars: {e}")
            return []
    
    def get_events(self, calendar_id: str = 'primary', time_min: datetime = None, 
                   time_max: datetime = None, max_results: int = 250) -> List[CalendarEvent]:
        """
        Get events from a specific calendar
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Minimum time for events (default: now)
            time_max: Maximum time for events (default: 1 month from now)
            max_results: Maximum number of events to retrieve
            
        Returns:
            List of CalendarEvent objects
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return []
        
        try:
            # Set default time range if not provided
            if time_min is None:
                time_min = datetime.now()
            if time_max is None:
                time_max = datetime.now() + timedelta(days=30)
            
            # Convert to RFC3339 format
            time_min_rfc = time_min.isoformat() + 'Z'
            time_max_rfc = time_max.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min_rfc,
                timeMax=time_max_rfc,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            google_events = events_result.get('items', [])
            
            # Convert to CalendarEvent objects
            calendar_events = []
            for google_event in google_events:
                try:
                    event = CalendarEvent.from_google_event(google_event, calendar_id)
                    calendar_events.append(event)
                except Exception as e:
                    self.logger.warning(f"Failed to parse Google event {google_event.get('id', 'unknown')}: {e}")
            
            self.logger.debug(f"Retrieved {len(calendar_events)} events from calendar {calendar_id}")
            return calendar_events
            
        except HttpError as e:
            self.logger.error(f"Failed to get events from calendar {calendar_id}: {e}")
            return []
    
    def create_event(self, event: CalendarEvent, calendar_id: str = 'primary') -> Optional[str]:
        """
        Create a new event in Google Calendar
        
        Args:
            event: CalendarEvent to create
            calendar_id: Calendar ID to create event in
            
        Returns:
            Google event ID if successful, None otherwise
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return None
        
        try:
            google_event = event.to_google_event()
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=google_event
            ).execute()
            
            google_event_id = created_event.get('id')
            self.logger.info(f"Created Google Calendar event: {google_event_id}")
            return google_event_id
            
        except HttpError as e:
            self.logger.error(f"Failed to create Google Calendar event: {e}")
            return None
    
    def update_event(self, event: CalendarEvent, calendar_id: str = 'primary') -> bool:
        """
        Update an existing event in Google Calendar
        
        Args:
            event: CalendarEvent to update (must have google_event_id)
            calendar_id: Calendar ID containing the event
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return False
        
        if not event.google_event_id:
            self.logger.error("Cannot update event without Google event ID")
            return False
        
        try:
            google_event = event.to_google_event()
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event.google_event_id,
                body=google_event
            ).execute()
            
            self.logger.info(f"Updated Google Calendar event: {event.google_event_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Failed to update Google Calendar event {event.google_event_id}: {e}")
            return False
    
    def delete_event(self, google_event_id: str, calendar_id: str = 'primary') -> bool:
        """
        Delete an event from Google Calendar
        
        Args:
            google_event_id: Google event ID to delete
            calendar_id: Calendar ID containing the event
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return False
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=google_event_id
            ).execute()
            
            self.logger.info(f"Deleted Google Calendar event: {google_event_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Failed to delete Google Calendar event {google_event_id}: {e}")
            return False
    
    def sync_events(self, local_events: List[CalendarEvent], 
                   calendar_id: str = 'primary') -> Tuple[List[CalendarEvent], List[str]]:
        """
        Synchronize local events with Google Calendar
        
        Args:
            local_events: List of local CalendarEvent objects
            calendar_id: Calendar ID to sync with
            
        Returns:
            Tuple of (updated_events, error_messages)
        """
        if not self.is_authenticated():
            return [], ["Not authenticated with Google Calendar"]
        
        updated_events = []
        errors = []
        
        for event in local_events:
            try:
                if event.needs_sync:
                    if event.google_event_id:
                        # Update existing event
                        if self.update_event(event, calendar_id):
                            event.needs_sync = False
                            event.last_synced = datetime.now()
                            updated_events.append(event)
                        else:
                            errors.append(f"Failed to update event: {event.title}")
                    else:
                        # Create new event
                        google_event_id = self.create_event(event, calendar_id)
                        if google_event_id:
                            event.google_event_id = google_event_id
                            event.needs_sync = False
                            event.last_synced = datetime.now()
                            event.is_local_only = False
                            updated_events.append(event)
                        else:
                            errors.append(f"Failed to create event: {event.title}")
                            
            except Exception as e:
                errors.append(f"Error syncing event {event.title}: {str(e)}")
        
        self.logger.info(f"Synced {len(updated_events)} events, {len(errors)} errors")
        return updated_events, errors
    
    def get_free_busy(self, calendar_id: str = 'primary', 
                     time_min: datetime = None, time_max: datetime = None) -> List[Dict[str, str]]:
        """
        Get free/busy information for a calendar
        
        Args:
            calendar_id: Calendar ID to check
            time_min: Start time for free/busy query
            time_max: End time for free/busy query
            
        Returns:
            List of busy time periods
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return []
        
        try:
            if time_min is None:
                time_min = datetime.now()
            if time_max is None:
                time_max = datetime.now() + timedelta(days=7)
            
            body = {
                "timeMin": time_min.isoformat() + 'Z',
                "timeMax": time_max.isoformat() + 'Z',
                "items": [{"id": calendar_id}]
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            
            busy_times = []
            calendars = freebusy_result.get('calendars', {})
            if calendar_id in calendars:
                busy_periods = calendars[calendar_id].get('busy', [])
                for period in busy_periods:
                    busy_times.append({
                        'start': period['start'],
                        'end': period['end']
                    })
            
            return busy_times
            
        except HttpError as e:
            self.logger.error(f"Failed to get free/busy information: {e}")
            return []
    
    def quick_add_event(self, text: str, calendar_id: str = 'primary') -> Optional[CalendarEvent]:
        """
        Create an event using Google's Quick Add feature
        
        Args:
            text: Natural language event description (e.g., "Lunch with John tomorrow at 12pm")
            calendar_id: Calendar ID to create event in
            
        Returns:
            CalendarEvent if successful, None otherwise
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Google Calendar")
            return None
        
        try:
            created_event = self.service.events().quickAdd(
                calendarId=calendar_id,
                text=text
            ).execute()
            
            # Convert the created Google event to CalendarEvent
            event = CalendarEvent.from_google_event(created_event, calendar_id)
            
            self.logger.info(f"Quick added event: {event.title}")
            return event
            
        except HttpError as e:
            self.logger.error(f"Failed to quick add event '{text}': {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test the connection to Google Calendar API
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            if not self.is_authenticated():
                return False
            
            # Try to get calendar list as a simple test
            calendars = self.get_calendars()
            return len(calendars) >= 0  # Even 0 calendars is a valid response
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False