"""
Spotify Controller Module for StosOS

Provides comprehensive Spotify integration including:
- Spotify Web API integration using Spotipy library
- Playback control interface (play, pause, skip, volume)
- Music library browser for playlists and recently played
- Device selection functionality for Alexa-connected speakers
- Now playing display with album art and track information

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
"""

import logging
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from core.base_module import BaseModule
from core.config_manager import ConfigManager
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class TrackCard(StosOSCard):
    """Individual track card component"""
    
    def __init__(self, track_info: Dict[str, Any], on_play: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.track_info = track_info
        self.on_play = on_play
        
        self.size_hint_y = None
        self.height = dp(80)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the track card UI"""
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Track info
        info_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'))
        
        # Track name
        track_name = self.track_info.get('name', 'Unknown Track')
        name_label = StosOSLabel(
            text=track_name,
            label_type="title",
            color=StosOSTheme.get_color('text_primary'),
            size_hint_y=None,
            height=dp(25)
        )
        name_label.bind(size=name_label.setter('text_size'))
        info_layout.add_widget(name_label)
        
        # Artist name
        artists = self.track_info.get('artists', [])
        artist_names = ', '.join([artist.get('name', '') for artist in artists])
        artist_label = StosOSLabel(
            text=artist_names,
            color=StosOSTheme.get_color('text_secondary'),
            font_size=StosOSTheme.get_font_size('caption'),
            size_hint_y=None,
            height=dp(20)
        )
        artist_label.bind(size=artist_label.setter('text_size'))
        info_layout.add_widget(artist_label)
        
        # Album name
        album_name = self.track_info.get('album', {}).get('name', '')
        if album_name:
            album_label = StosOSLabel(
                text=f"Album: {album_name}",
                color=StosOSTheme.get_color('text_tertiary'),
                font_size=StosOSTheme.get_font_size('small'),
                size_hint_y=None,
                height=dp(18)
            )
            album_label.bind(size=album_label.setter('text_size'))
            info_layout.add_widget(album_label)
        
        content_layout.add_widget(info_layout)
        
        # Play button
        play_btn = StosOSIconButton(
            icon="play",
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            on_press_callback=lambda: self.on_play(self.track_info) if self.on_play else None
        )
        content_layout.add_widget(play_btn)
        
        self.add_widget(content_layout)


class DeviceCard(StosOSCard):
    """Individual device card component"""
    
    def __init__(self, device_info: Dict[str, Any], on_select: Callable = None, 
                 is_active: bool = False, **kwargs):
        super().__init__(**kwargs)
        
        self.device_info = device_info
        self.on_select = on_select
        self.is_active = is_active
        
        self.size_hint_y = None
        self.height = dp(60)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the device card UI"""
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Device info
        info_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'))
        
        # Device name
        device_name = self.device_info.get('name', 'Unknown Device')
        name_label = StosOSLabel(
            text=device_name,
            label_type="title" if self.is_active else "body",
            color=StosOSTheme.get_color('accent_primary') if self.is_active 
                  else StosOSTheme.get_color('text_primary'),
            size_hint_y=None,
            height=dp(25)
        )
        name_label.bind(size=name_label.setter('text_size'))
        info_layout.add_widget(name_label)
        
        # Device type and status
        device_type = self.device_info.get('type', 'Unknown')
        is_active_text = " (Active)" if self.is_active else ""
        status_label = StosOSLabel(
            text=f"{device_type}{is_active_text}",
            color=StosOSTheme.get_color('text_secondary'),
            font_size=StosOSTheme.get_font_size('caption'),
            size_hint_y=None,
            height=dp(20)
        )
        status_label.bind(size=status_label.setter('text_size'))
        info_layout.add_widget(status_label)
        
        content_layout.add_widget(info_layout)
        
        # Select button
        select_btn = StosOSButton(
            text="Select" if not self.is_active else "Active",
            button_type="accent" if not self.is_active else "secondary",
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            on_press_callback=lambda: self.on_select(self.device_info) if self.on_select and not self.is_active else None
        )
        content_layout.add_widget(select_btn)
        
        self.add_widget(content_layout)


class SpotifyController(BaseModule):
    """Spotify Controller Module"""
    
    def __init__(self):
        super().__init__(
            module_id="spotify_controller",
            display_name="Spotify Controller",
            icon="music"
        )
        
        self.config_manager = ConfigManager()
        self.spotify_client = None
        self.current_playback = None
        self.devices = []
        self.playlists = []
        self.recently_played = []
        self.current_track = None
        
        # UI components
        self.main_screen = None
        self.loading_overlay = None
        self.now_playing_panel = None
        self.control_panel = None
        self.library_panel = None
        self.device_panel = None
        
        # Update timer
        self.update_timer = None
    
    def initialize(self) -> bool:
        """Initialize the Spotify controller module"""
        try:
            self.logger.info("Initializing Spotify Controller module")
            
            # Initialize Spotify client
            if not self._initialize_spotify_client():
                self.logger.error("Failed to initialize Spotify client")
                return False
            
            # Create UI
            self._create_ui()
            
            # Start periodic updates
            self._start_updates()
            
            self._initialized = True
            self.logger.info("Spotify Controller module initialized successfully")
            return True
            
        except Exception as e:
            self.handle_error(e, "initialize")
            return False
    
    def _initialize_spotify_client(self) -> bool:
        """Initialize Spotify API client"""
        try:
            # Get Spotify credentials from config
            spotify_config = self.config_manager.get_config().get('spotify', {})
            
            client_id = spotify_config.get('client_id')
            client_secret = spotify_config.get('client_secret')
            redirect_uri = spotify_config.get('redirect_uri', 'http://localhost:8080/callback')
            
            if not client_id or not client_secret:
                self.logger.error("Spotify credentials not configured")
                return False
            
            # Set up OAuth
            scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private user-read-recently-played"
            
            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                cache_path=".spotify_cache"
            )
            
            self.spotify_client = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test connection
            user_info = self.spotify_client.current_user()
            self.logger.info(f"Connected to Spotify as {user_info.get('display_name', 'Unknown')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify client: {e}")
            return False  
  
    def _create_ui(self):
        """Create the main UI for Spotify controller"""
        self.main_screen = Screen(name='spotify_controller')
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('lg'))
        
        # Header
        header = self._create_header()
        main_layout.add_widget(header)
        
        # Content area with tabs
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Left panel - Now Playing and Controls
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=StosOSTheme.get_spacing('md'))
        
        # Now Playing panel
        self.now_playing_panel = self._create_now_playing_panel()
        left_panel.add_widget(self.now_playing_panel)
        
        # Control panel
        self.control_panel = self._create_control_panel()
        left_panel.add_widget(self.control_panel)
        
        # Device selection panel
        self.device_panel = self._create_device_panel()
        left_panel.add_widget(self.device_panel)
        
        content_layout.add_widget(left_panel)
        
        # Right panel - Library Browser
        self.library_panel = self._create_library_panel()
        content_layout.add_widget(self.library_panel)
        
        main_layout.add_widget(content_layout)
        
        # Loading overlay
        self.loading_overlay = StosOSLoadingOverlay()
        
        # Add to screen
        root_layout = FloatLayout()
        root_layout.add_widget(main_layout)
        root_layout.add_widget(self.loading_overlay)
        
        self.main_screen.add_widget(root_layout)
    
    def _create_header(self) -> BoxLayout:
        """Create header with title and refresh button"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Title
        title_label = StosOSLabel(
            text="Spotify Controller",
            label_type="title",
            color=StosOSTheme.get_color('text_primary')
        )
        header.add_widget(title_label)
        
        # Refresh button
        refresh_btn = StosOSButton(
            text="Refresh",
            button_type="secondary",
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            on_press_callback=self._refresh_data
        )
        header.add_widget(refresh_btn)
        
        return header
    
    def _create_now_playing_panel(self) -> StosOSPanel:
        """Create now playing display panel"""
        panel = StosOSPanel(
            title="Now Playing",
            size_hint_y=None,
            height=dp(200)
        )
        
        content_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Track info layout
        self.track_info_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Track name
        self.track_name_label = StosOSLabel(
            text="No track playing",
            label_type="title",
            color=StosOSTheme.get_color('text_primary')
        )
        self.track_info_layout.add_widget(self.track_name_label)
        
        # Artist name
        self.artist_name_label = StosOSLabel(
            text="",
            color=StosOSTheme.get_color('text_secondary'),
            font_size=StosOSTheme.get_font_size('body')
        )
        self.track_info_layout.add_widget(self.artist_name_label)
        
        # Album name
        self.album_name_label = StosOSLabel(
            text="",
            color=StosOSTheme.get_color('text_tertiary'),
            font_size=StosOSTheme.get_font_size('caption')
        )
        self.track_info_layout.add_widget(self.album_name_label)
        
        # Progress bar (placeholder)
        self.progress_label = StosOSLabel(
            text="--:-- / --:--",
            color=StosOSTheme.get_color('text_secondary'),
            font_size=StosOSTheme.get_font_size('caption')
        )
        self.track_info_layout.add_widget(self.progress_label)
        
        content_layout.add_widget(self.track_info_layout)
        
        panel.add_widget(content_layout)
        return panel
    
    def _create_control_panel(self) -> StosOSPanel:
        """Create playback control panel"""
        panel = StosOSPanel(
            title="Playback Controls",
            size_hint_y=None,
            height=dp(150)
        )
        
        content_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Main controls
        controls_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Previous button
        prev_btn = StosOSButton(
            text="⏮",
            button_type="secondary",
            size_hint=(None, None),
            size=(dp(60), dp(50)),
            on_press_callback=self._previous_track
        )
        controls_layout.add_widget(prev_btn)
        
        # Play/Pause button
        self.play_pause_btn = StosOSButton(
            text="▶",
            button_type="accent",
            size_hint=(None, None),
            size=(dp(80), dp(50)),
            on_press_callback=self._toggle_playback
        )
        controls_layout.add_widget(self.play_pause_btn)
        
        # Next button
        next_btn = StosOSButton(
            text="⏭",
            button_type="secondary",
            size_hint=(None, None),
            size=(dp(60), dp(50)),
            on_press_callback=self._next_track
        )
        controls_layout.add_widget(next_btn)
        
        content_layout.add_widget(controls_layout)
        
        # Volume control
        volume_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('sm'))
        
        volume_label = StosOSLabel(
            text="Volume:",
            size_hint_x=None,
            width=dp(60)
        )
        volume_layout.add_widget(volume_label)
        
        # Volume buttons
        vol_down_btn = StosOSButton(
            text="🔉",
            button_type="secondary",
            size_hint=(None, None),
            size=(dp(40), dp(30)),
            on_press_callback=lambda: self._adjust_volume(-10)
        )
        volume_layout.add_widget(vol_down_btn)
        
        self.volume_label = StosOSLabel(
            text="50%",
            size_hint_x=None,
            width=dp(50)
        )
        volume_layout.add_widget(self.volume_label)
        
        vol_up_btn = StosOSButton(
            text="🔊",
            button_type="secondary",
            size_hint=(None, None),
            size=(dp(40), dp(30)),
            on_press_callback=lambda: self._adjust_volume(10)
        )
        volume_layout.add_widget(vol_up_btn)
        
        content_layout.add_widget(volume_layout)
        
        panel.add_widget(content_layout)
        return panel
    
    def _create_device_panel(self) -> StosOSPanel:
        """Create device selection panel"""
        panel = StosOSPanel(
            title="Playback Devices",
            size_hint_y=None,
            height=dp(200)
        )
        
        # Device list
        self.device_scroll = StosOSScrollView()
        self.device_list_layout = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None
        )
        self.device_list_layout.bind(minimum_height=self.device_list_layout.setter('height'))
        
        self.device_scroll.add_widget(self.device_list_layout)
        panel.add_widget(self.device_scroll)
        
        return panel
    
    def _create_library_panel(self) -> StosOSPanel:
        """Create library browser panel"""
        panel = StosOSPanel(
            title="Music Library",
            size_hint_x=0.6
        )
        
        content_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Tab buttons
        tab_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        self.playlists_btn = StosOSToggleButton(
            text="Playlists",
            on_press_callback=lambda: self._show_library_tab("playlists")
        )
        self.playlists_btn.set_state(True)  # Default selected
        tab_layout.add_widget(self.playlists_btn)
        
        self.recent_btn = StosOSToggleButton(
            text="Recently Played",
            on_press_callback=lambda: self._show_library_tab("recent")
        )
        tab_layout.add_widget(self.recent_btn)
        
        content_layout.add_widget(tab_layout)
        
        # Content area
        self.library_scroll = StosOSScrollView()
        self.library_content_layout = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None
        )
        self.library_content_layout.bind(minimum_height=self.library_content_layout.setter('height'))
        
        self.library_scroll.add_widget(self.library_content_layout)
        content_layout.add_widget(self.library_scroll)
        
        panel.add_widget(content_layout)
        return panel    
 
   def get_screen(self) -> Screen:
        """Get the main screen for this module"""
        return self.main_screen
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        self._refresh_data()
    
    def on_deactivate(self):
        """Called when module becomes inactive"""
        super().on_deactivate()
        if self.update_timer:
            self.update_timer.cancel()
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands for Spotify control"""
        command_lower = command.lower()
        
        try:
            if "play" in command_lower and "pause" not in command_lower:
                if "spotify" in command_lower or "music" in command_lower:
                    self._play_music()
                    return True
            elif "pause" in command_lower or "stop" in command_lower:
                self._pause_music()
                return True
            elif "next" in command_lower or "skip" in command_lower:
                self._next_track()
                return True
            elif "previous" in command_lower or "back" in command_lower:
                self._previous_track()
                return True
            elif "volume up" in command_lower:
                self._adjust_volume(20)
                return True
            elif "volume down" in command_lower:
                self._adjust_volume(-20)
                return True
            
        except Exception as e:
            self.handle_error(e, "voice_command")
        
        return False
    
    def _start_updates(self):
        """Start periodic updates of playback status"""
        def update_status():
            if self._active and self.spotify_client:
                self._update_current_playback()
                # Schedule next update
                self.update_timer = Clock.schedule_once(lambda dt: update_status(), 5.0)
        
        # Initial update
        Clock.schedule_once(lambda dt: update_status(), 1.0)
    
    def _refresh_data(self):
        """Refresh all Spotify data"""
        if not self.spotify_client:
            return
        
        self.loading_overlay.show(self.main_screen)
        
        def refresh_thread():
            try:
                # Update current playback
                self._update_current_playback()
                
                # Update devices
                self._update_devices()
                
                # Update playlists
                self._update_playlists()
                
                # Update recently played
                self._update_recently_played()
                
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._update_ui(), 0)
                
            except Exception as e:
                self.handle_error(e, "refresh_data")
            finally:
                Clock.schedule_once(lambda dt: self.loading_overlay.hide(), 0)
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def _update_current_playback(self):
        """Update current playback information"""
        try:
            self.current_playback = self.spotify_client.current_playback()
            if self.current_playback and self.current_playback.get('item'):
                self.current_track = self.current_playback['item']
            else:
                self.current_track = None
                
        except Exception as e:
            self.logger.error(f"Failed to update current playback: {e}")
    
    def _update_devices(self):
        """Update available devices"""
        try:
            devices_response = self.spotify_client.devices()
            self.devices = devices_response.get('devices', [])
            
        except Exception as e:
            self.logger.error(f"Failed to update devices: {e}")
    
    def _update_playlists(self):
        """Update user playlists"""
        try:
            playlists_response = self.spotify_client.current_user_playlists(limit=20)
            self.playlists = playlists_response.get('items', [])
            
        except Exception as e:
            self.logger.error(f"Failed to update playlists: {e}")
    
    def _update_recently_played(self):
        """Update recently played tracks"""
        try:
            recent_response = self.spotify_client.current_user_recently_played(limit=20)
            self.recently_played = recent_response.get('items', [])
            
        except Exception as e:
            self.logger.error(f"Failed to update recently played: {e}")
    
    def _update_ui(self):
        """Update UI with current data"""
        # Update now playing
        self._update_now_playing_ui()
        
        # Update control buttons
        self._update_control_ui()
        
        # Update devices
        self._update_device_ui()
        
        # Update library based on current tab
        if hasattr(self, 'playlists_btn') and self.playlists_btn.is_toggled:
            self._show_library_tab("playlists")
        else:
            self._show_library_tab("recent")
    
    def _update_now_playing_ui(self):
        """Update now playing display"""
        if self.current_track:
            # Track name
            track_name = self.current_track.get('name', 'Unknown Track')
            self.track_name_label.text = track_name
            
            # Artist names
            artists = self.current_track.get('artists', [])
            artist_names = ', '.join([artist.get('name', '') for artist in artists])
            self.artist_name_label.text = artist_names
            
            # Album name
            album_name = self.current_track.get('album', {}).get('name', '')
            self.album_name_label.text = f"Album: {album_name}"
            
            # Progress
            if self.current_playback:
                progress_ms = self.current_playback.get('progress_ms', 0)
                duration_ms = self.current_track.get('duration_ms', 0)
                
                progress_min = progress_ms // 60000
                progress_sec = (progress_ms % 60000) // 1000
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000
                
                self.progress_label.text = f"{progress_min:02d}:{progress_sec:02d} / {duration_min:02d}:{duration_sec:02d}"
        else:
            self.track_name_label.text = "No track playing"
            self.artist_name_label.text = ""
            self.album_name_label.text = ""
            self.progress_label.text = "--:-- / --:--"
    
    def _update_control_ui(self):
        """Update control button states"""
        if self.current_playback:
            is_playing = self.current_playback.get('is_playing', False)
            self.play_pause_btn.text = "⏸" if is_playing else "▶"
            
            # Update volume
            device = self.current_playback.get('device', {})
            volume = device.get('volume_percent', 50)
            self.volume_label.text = f"{volume}%"
        else:
            self.play_pause_btn.text = "▶"
            self.volume_label.text = "50%"
    
    def _update_device_ui(self):
        """Update device list"""
        self.device_list_layout.clear_widgets()
        
        active_device_id = None
        if self.current_playback:
            active_device_id = self.current_playback.get('device', {}).get('id')
        
        for device in self.devices:
            is_active = device.get('id') == active_device_id
            device_card = DeviceCard(
                device_info=device,
                on_select=self._select_device,
                is_active=is_active
            )
            self.device_list_layout.add_widget(device_card)
    
    def _show_library_tab(self, tab_name: str):
        """Show specific library tab content"""
        self.library_content_layout.clear_widgets()
        
        if tab_name == "playlists":
            for playlist in self.playlists:
                playlist_card = TrackCard(
                    track_info={
                        'name': playlist.get('name', 'Unknown Playlist'),
                        'artists': [{'name': f"{playlist.get('tracks', {}).get('total', 0)} tracks"}],
                        'album': {'name': f"by {playlist.get('owner', {}).get('display_name', 'Unknown')}"},
                        'uri': playlist.get('uri')
                    },
                    on_play=self._play_playlist
                )
                self.library_content_layout.add_widget(playlist_card)
        
        elif tab_name == "recent":
            for item in self.recently_played:
                track = item.get('track', {})
                track_card = TrackCard(
                    track_info=track,
                    on_play=self._play_track
                )
                self.library_content_layout.add_widget(track_card)
    
    # Playback control methods
    def _toggle_playback(self):
        """Toggle play/pause"""
        try:
            if self.current_playback and self.current_playback.get('is_playing'):
                self.spotify_client.pause_playback()
            else:
                self.spotify_client.start_playback()
            
            # Update UI after short delay
            Clock.schedule_once(lambda dt: self._update_current_playback(), 0.5)
            
        except Exception as e:
            self.handle_error(e, "toggle_playback")
    
    def _play_music(self):
        """Start playback"""
        try:
            self.spotify_client.start_playback()
            Clock.schedule_once(lambda dt: self._update_current_playback(), 0.5)
            
        except Exception as e:
            self.handle_error(e, "play_music")
    
    def _pause_music(self):
        """Pause playback"""
        try:
            self.spotify_client.pause_playback()
            Clock.schedule_once(lambda dt: self._update_current_playback(), 0.5)
            
        except Exception as e:
            self.handle_error(e, "pause_music")
    
    def _next_track(self):
        """Skip to next track"""
        try:
            self.spotify_client.next_track()
            Clock.schedule_once(lambda dt: self._update_current_playback(), 1.0)
            
        except Exception as e:
            self.handle_error(e, "next_track")
    
    def _previous_track(self):
        """Skip to previous track"""
        try:
            self.spotify_client.previous_track()
            Clock.schedule_once(lambda dt: self._update_current_playback(), 1.0)
            
        except Exception as e:
            self.handle_error(e, "previous_track")
    
    def _adjust_volume(self, change: int):
        """Adjust volume by specified amount"""
        try:
            if self.current_playback:
                current_volume = self.current_playback.get('device', {}).get('volume_percent', 50)
                new_volume = max(0, min(100, current_volume + change))
                self.spotify_client.volume(new_volume)
                
                # Update UI
                self.volume_label.text = f"{new_volume}%"
            
        except Exception as e:
            self.handle_error(e, "adjust_volume")
    
    def _select_device(self, device_info: Dict[str, Any]):
        """Select playback device"""
        try:
            device_id = device_info.get('id')
            if device_id:
                self.spotify_client.transfer_playback(device_id, force_play=False)
                Clock.schedule_once(lambda dt: self._refresh_data(), 1.0)
            
        except Exception as e:
            self.handle_error(e, "select_device")
    
    def _play_track(self, track_info: Dict[str, Any]):
        """Play specific track"""
        try:
            track_uri = track_info.get('uri')
            if track_uri:
                self.spotify_client.start_playback(uris=[track_uri])
                Clock.schedule_once(lambda dt: self._update_current_playback(), 1.0)
            
        except Exception as e:
            self.handle_error(e, "play_track")
    
    def _play_playlist(self, playlist_info: Dict[str, Any]):
        """Play specific playlist"""
        try:
            playlist_uri = playlist_info.get('uri')
            if playlist_uri:
                self.spotify_client.start_playback(context_uri=playlist_uri)
                Clock.schedule_once(lambda dt: self._update_current_playback(), 1.0)
            
        except Exception as e:
            self.handle_error(e, "play_playlist")
    
    def cleanup(self):
        """Cleanup module resources"""
        super().cleanup()
        if self.update_timer:
            self.update_timer.cancel()
        self.spotify_client = None