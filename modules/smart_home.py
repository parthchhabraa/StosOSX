"""
Smart Home Integration Module for StosOS

Provides comprehensive smart home device control including:
- Google Assistant SDK integration for device discovery and control
- Alexa Voice Service API for device discovery and control
- Device control interface with appropriate controls for each device type
- Real-time device status updates and connectivity monitoring
- Scene management for predefined device configurations

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
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
from models.smart_device import SmartDevice, DeviceType, Platform
from services.google_assistant_service import GoogleAssistantService
from services.alexa_service import AlexaService
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class DeviceCard(StosOSCard):
    """Individual smart device card component"""
    
    def __init__(self, device: SmartDevice, on_control: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.device = device
        self.on_control = on_control
        
        self.size_hint_y = None
        self.height = dp(160)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the device card UI"""
        # Main content layout
        content_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Header with device name and status
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        # Device name and type
        name_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        name_label = StosOSLabel(
            text=self.device.name,
            label_type="subtitle",
            color=StosOSTheme.get_color('text_primary') if self.device.is_online 
                  else StosOSTheme.get_color('text_disabled')
        )
        name_layout.add_widget(name_label)
        
        type_label = StosOSLabel(
            text=f"{self._get_device_icon()} {self.device.device_type.value} • {self.device.room}",
            font_size=StosOSTheme.get_font_size('caption'),
            color=StosOSTheme.get_color('text_secondary')
        )
        name_layout.add_widget(type_label)
        
        header_layout.add_widget(name_layout)
        
        # Status indicator
        status_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
        
        platform_label = StosOSLabel(
            text=self.device.platform.value,
            font_size=StosOSTheme.get_font_size('caption'),
            color=StosOSTheme.get_color('accent_secondary'),
            halign='right'
        )
        platform_label.bind(size=platform_label.setter('text_size'))
        status_layout.add_widget(platform_label)
        
        online_status = "🟢 Online" if self.device.is_online else "🔴 Offline"
        status_label = StosOSLabel(
            text=online_status,
            font_size=StosOSTheme.get_font_size('caption'),
            color=StosOSTheme.get_color('success') if self.device.is_online 
                  else StosOSTheme.get_color('error'),
            halign='right'
        )
        status_label.bind(size=status_label.setter('text_size'))
        status_layout.add_widget(status_label)
        
        header_layout.add_widget(status_layout)
        content_layout.add_widget(header_layout)
        
        # Device controls based on type and capabilities
        controls_layout = self._build_device_controls()
        if controls_layout:
            content_layout.add_widget(controls_layout)
        
        self.add_widget(content_layout)
    
    def _get_device_icon(self) -> str:
        """Get icon for device type"""
        icons = {
            DeviceType.LIGHT: "💡",
            DeviceType.THERMOSTAT: "🌡️",
            DeviceType.SPEAKER: "🔊",
            DeviceType.SWITCH: "🔌",
            DeviceType.SENSOR: "📡",
            DeviceType.CAMERA: "📹",
            DeviceType.LOCK: "🔒",
            DeviceType.FAN: "🌀",
            DeviceType.OTHER: "📱"
        }
        return icons.get(self.device.device_type, "📱")
    
    def _build_device_controls(self) -> Optional[BoxLayout]:
        """Build device-specific controls"""
        if not self.device.is_online or not self.device.capabilities:
            return None
        
        controls_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'))
        
        # Power control (most common)
        if self.device.has_capability("power"):
            power_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            power_label = StosOSLabel(
                text="Power:",
                size_hint_x=0.3,
                font_size=StosOSTheme.get_font_size('body')
            )
            power_layout.add_widget(power_label)
            
            power_btn = StosOSToggleButton(
                text="ON" if self.device.get_status_value("power", False) else "OFF",
                size_hint_x=0.7,
                button_type="success" if self.device.get_status_value("power", False) else "secondary"
            )
            power_btn.is_toggled = self.device.get_status_value("power", False)
            power_btn.bind(on_press=lambda x: self._control_device("power_toggle"))
            power_layout.add_widget(power_btn)
            
            controls_layout.add_widget(power_layout)
        
        # Brightness control (lights)
        if self.device.has_capability("brightness"):
            brightness_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            brightness_label = StosOSLabel(
                text="Brightness:",
                size_hint_x=0.3,
                font_size=StosOSTheme.get_font_size('body')
            )
            brightness_layout.add_widget(brightness_label)
            
            brightness_slider = StosOSSlider(
                min=0, max=100,
                value=self.device.get_status_value("brightness", 50),
                size_hint_x=0.7
            )
            brightness_slider.bind(value=lambda x, v: self._control_device("set_brightness", {"brightness": int(v)}))
            brightness_layout.add_widget(brightness_slider)
            
            controls_layout.add_widget(brightness_layout)
        
        # Volume control (speakers)
        if self.device.has_capability("volume"):
            volume_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            volume_label = StosOSLabel(
                text="Volume:",
                size_hint_x=0.3,
                font_size=StosOSTheme.get_font_size('body')
            )
            volume_layout.add_widget(volume_label)
            
            volume_slider = StosOSSlider(
                min=0, max=100,
                value=self.device.get_status_value("volume", 50),
                size_hint_x=0.7
            )
            volume_slider.bind(value=lambda x, v: self._control_device("set_volume", {"volume": int(v)}))
            volume_layout.add_widget(volume_slider)
            
            controls_layout.add_widget(volume_layout)
        
        # Temperature control (thermostats)
        if self.device.has_capability("target_temperature"):
            temp_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            temp_label = StosOSLabel(
                text="Target:",
                size_hint_x=0.3,
                font_size=StosOSTheme.get_font_size('body')
            )
            temp_layout.add_widget(temp_label)
            
            current_temp = self.device.get_status_value("target_temperature", 70)
            temp_input = StosOSTextInput(
                text=str(current_temp),
                input_filter='int',
                size_hint_x=0.4,
                multiline=False
            )
            temp_input.bind(text=lambda x, t: self._control_device("set_temperature", {"temperature": int(t) if t.isdigit() else 70}))
            temp_layout.add_widget(temp_input)
            
            temp_unit_label = StosOSLabel(
                text="°F",
                size_hint_x=0.3,
                font_size=StosOSTheme.get_font_size('body')
            )
            temp_layout.add_widget(temp_unit_label)
            
            controls_layout.add_widget(temp_layout)
        
        # Media controls (speakers)
        if self.device.has_capability("play") or self.device.has_capability("pause"):
            media_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            if self.device.has_capability("play"):
                play_btn = StosOSIconButton(
                    icon="▶️",
                    size=(dp(30), dp(30)),
                    button_type="accent"
                )
                play_btn.bind(on_press=lambda x: self._control_device("play"))
                media_layout.add_widget(play_btn)
            
            if self.device.has_capability("pause"):
                pause_btn = StosOSIconButton(
                    icon="⏸️",
                    size=(dp(30), dp(30)),
                    button_type="secondary"
                )
                pause_btn.bind(on_press=lambda x: self._control_device("pause"))
                media_layout.add_widget(pause_btn)
            
            if self.device.has_capability("mute"):
                mute_btn = StosOSToggleButton(
                    text="🔇" if self.device.get_status_value("muted", False) else "🔊",
                    size=(dp(30), dp(30)),
                    button_type="warning" if self.device.get_status_value("muted", False) else "secondary"
                )
                mute_btn.is_toggled = self.device.get_status_value("muted", False)
                mute_btn.bind(on_press=lambda x: self._control_device("mute_toggle"))
                media_layout.add_widget(mute_btn)
            
            controls_layout.add_widget(media_layout)
        
        return controls_layout if controls_layout.children else None
    
    def _control_device(self, command: str, parameters: Dict[str, Any] = None):
        """Send control command to device"""
        if self.on_control:
            # Handle toggle commands
            if command == "power_toggle":
                current_power = self.device.get_status_value("power", False)
                command = "power_off" if current_power else "power_on"
            elif command == "mute_toggle":
                current_mute = self.device.get_status_value("muted", False)
                command = "unmute" if current_mute else "mute"
            
            self.on_control(self.device.id, command, parameters or {})
    
    def update_device(self, device: SmartDevice):
        """Update the card with new device data"""
        self.device = device
        # Rebuild UI to reflect changes
        self.clear_widgets()
        self._build_ui()


class SceneCard(StosOSCard):
    """Scene management card component"""
    
    def __init__(self, scene_name: str, scene_data: Dict[str, Any], 
                 on_activate: Callable = None, on_edit: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.scene_name = scene_name
        self.scene_data = scene_data
        self.on_activate = on_activate
        self.on_edit = on_edit
        
        self.size_hint_y = None
        self.height = dp(100)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the scene card UI"""
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Scene info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        name_label = StosOSLabel(
            text=self.scene_name,
            label_type="subtitle",
            color=StosOSTheme.get_color('text_primary')
        )
        info_layout.add_widget(name_label)
        
        device_count = len(self.scene_data.get('devices', {}))
        desc_label = StosOSLabel(
            text=f"{device_count} devices • {self.scene_data.get('description', 'No description')}",
            font_size=StosOSTheme.get_font_size('caption'),
            color=StosOSTheme.get_color('text_secondary')
        )
        info_layout.add_widget(desc_label)
        
        content_layout.add_widget(info_layout)
        
        # Action buttons
        actions_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3, spacing=StosOSTheme.get_spacing('xs'))
        
        activate_btn = StosOSButton(
            text="Activate",
            button_type="accent",
            size_hint_x=0.7
        )
        activate_btn.bind(on_press=self._activate_scene)
        actions_layout.add_widget(activate_btn)
        
        edit_btn = StosOSIconButton(
            icon="✏",
            size=(dp(35), dp(35)),
            button_type="secondary"
        )
        edit_btn.bind(on_press=self._edit_scene)
        actions_layout.add_widget(edit_btn)
        
        content_layout.add_widget(actions_layout)
        
        self.add_widget(content_layout)
    
    def _activate_scene(self, *args):
        """Activate the scene"""
        if self.on_activate:
            self.on_activate(self.scene_name, self.scene_data)
    
    def _edit_scene(self, *args):
        """Edit the scene"""
        if self.on_edit:
            self.on_edit(self.scene_name, self.scene_data)


class SmartHomeModule(BaseModule):
    """
    Smart Home Integration Module
    
    Provides comprehensive smart home device control including Google Assistant
    and Alexa integration, device control interfaces, real-time status updates,
    and scene management.
    """
    
    def __init__(self):
        super().__init__(
            module_id="smart_home",
            display_name="Smart Home",
            icon="🏠"
        )
        
        self.db_manager = None
        self.google_service = None
        self.alexa_service = None
        
        self.devices = {}  # Combined devices from both services
        self.scenes = {}   # Predefined device configurations
        self.rooms = {}    # Devices grouped by room
        
        # UI components
        self.device_container = None
        self.scene_container = None
        self.status_panel = None
        self.current_view = "devices"  # "devices", "scenes", "rooms"
        
        # Status monitoring
        self.status_timer = None
        self.last_refresh = None
    
    def initialize(self) -> bool:
        """Initialize the smart home module"""
        try:
            self.db_manager = DatabaseManager()
            
            # Initialize services
            self.google_service = GoogleAssistantService()
            self.alexa_service = AlexaService()
            
            # Load scenes from database/config
            self._load_scenes()
            
            # Start services
            self._start_services()
            
            # Start status monitoring
            self._start_status_monitoring()
            
            self._initialized = True
            self.logger.info("Smart Home module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Smart Home module: {e}")
            self.handle_error(e, "initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Get the smart home screen"""
        if self.screen_widget is None:
            self.screen_widget = Screen(name=self.module_id)
            self._build_ui()
        return self.screen_widget
    
    def _build_ui(self):
        """Build the smart home UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Header with title and view controls
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        title_label = StosOSLabel(
            text="🏠 Smart Home",
            label_type="title",
            size_hint_x=0.4
        )
        header_layout.add_widget(title_label)
        
        # View toggle buttons
        view_layout = BoxLayout(orientation='horizontal', size_hint_x=0.6, spacing=StosOSTheme.get_spacing('xs'))
        
        devices_btn = StosOSToggleButton(
            text="Devices",
            button_type="accent" if self.current_view == "devices" else "secondary"
        )
        devices_btn.bind(on_press=lambda x: self._switch_view("devices"))
        view_layout.add_widget(devices_btn)
        
        rooms_btn = StosOSToggleButton(
            text="Rooms",
            button_type="accent" if self.current_view == "rooms" else "secondary"
        )
        rooms_btn.bind(on_press=lambda x: self._switch_view("rooms"))
        view_layout.add_widget(rooms_btn)
        
        scenes_btn = StosOSToggleButton(
            text="Scenes",
            button_type="accent" if self.current_view == "scenes" else "secondary"
        )
        scenes_btn.bind(on_press=lambda x: self._switch_view("scenes"))
        view_layout.add_widget(scenes_btn)
        
        header_layout.add_widget(view_layout)
        
        main_layout.add_widget(header_layout)
        
        # Status panel
        self._build_status_panel()
        main_layout.add_widget(self.status_panel)
        
        # Content area (will be populated based on current view)
        self.content_scroll = StosOSScrollView()
        self.content_container = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None
        )
        self.content_container.bind(minimum_height=self.content_container.setter('height'))
        
        self.content_scroll.add_widget(self.content_container)
        main_layout.add_widget(self.content_scroll)
        
        # Action buttons
        action_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        refresh_btn = StosOSButton(
            text="🔄 Refresh",
            button_type="secondary",
            size_hint_x=0.33
        )
        refresh_btn.bind(on_press=self._refresh_devices)
        action_layout.add_widget(refresh_btn)
        
        add_scene_btn = StosOSButton(
            text="+ Scene",
            button_type="accent",
            size_hint_x=0.33
        )
        add_scene_btn.bind(on_press=self._show_add_scene_dialog)
        action_layout.add_widget(add_scene_btn)
        
        settings_btn = StosOSButton(
            text="⚙️ Settings",
            button_type="secondary",
            size_hint_x=0.34
        )
        settings_btn.bind(on_press=self._show_settings)
        action_layout.add_widget(settings_btn)
        
        main_layout.add_widget(action_layout)
        
        self.screen_widget.add_widget(main_layout)
        
        # Initial content load
        self._refresh_content()
    
    def _build_status_panel(self):
        """Build the status panel"""
        self.status_panel = StosOSPanel(
            title="System Status",
            size_hint_y=None,
            height=dp(80)
        )
        
        status_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Google Assistant status
        self.google_status_label = StosOSLabel(
            text="Google: Connecting...",
            halign='center',
            size_hint_x=0.33
        )
        status_layout.add_widget(self.google_status_label)
        
        # Alexa status
        self.alexa_status_label = StosOSLabel(
            text="Alexa: Connecting...",
            halign='center',
            size_hint_x=0.33
        )
        status_layout.add_widget(self.alexa_status_label)
        
        # Device count
        self.device_count_label = StosOSLabel(
            text="Devices: 0",
            halign='center',
            size_hint_x=0.34
        )
        status_layout.add_widget(self.device_count_label)
        
        self.status_panel.add_widget(status_layout)
    
    def _start_services(self):
        """Start Google Assistant and Alexa services"""
        # Start Google Assistant service
        Clock.schedule_once(lambda dt: self._authenticate_google(), 0.1)
        
        # Start Alexa service
        Clock.schedule_once(lambda dt: self._authenticate_alexa(), 0.2)
    
    def _authenticate_google(self):
        """Authenticate Google Assistant service"""
        try:
            if self.google_service.authenticate():
                self.google_status_label.text = "Google: ✅ Connected"
                self.google_status_label.color = StosOSTheme.get_color('success')
                
                # Add device update callback
                self.google_service.add_device_callback(self._on_device_update)
                
                # Merge Google devices
                self._merge_devices()
            else:
                self.google_status_label.text = "Google: ❌ Failed"
                self.google_status_label.color = StosOSTheme.get_color('error')
        except Exception as e:
            self.logger.error(f"Google authentication error: {e}")
            self.google_status_label.text = "Google: ❌ Error"
            self.google_status_label.color = StosOSTheme.get_color('error')
    
    def _authenticate_alexa(self):
        """Authenticate Alexa service"""
        try:
            if self.alexa_service.authenticate():
                self.alexa_status_label.text = "Alexa: ✅ Connected"
                self.alexa_status_label.color = StosOSTheme.get_color('success')
                
                # Add device update callback
                self.alexa_service.add_device_callback(self._on_device_update)
                
                # Merge Alexa devices
                self._merge_devices()
            else:
                self.alexa_status_label.text = "Alexa: ❌ Failed"
                self.alexa_status_label.color = StosOSTheme.get_color('error')
        except Exception as e:
            self.logger.error(f"Alexa authentication error: {e}")
            self.alexa_status_label.text = "Alexa: ❌ Error"
            self.alexa_status_label.color = StosOSTheme.get_color('error')
    
    def _merge_devices(self):
        """Merge devices from both services"""
        self.devices.clear()
        
        # Add Google devices
        if self.google_service and self.google_service.is_authenticated():
            for device in self.google_service.get_devices():
                self.devices[device.id] = device
        
        # Add Alexa devices
        if self.alexa_service and self.alexa_service.is_authenticated():
            for device in self.alexa_service.get_devices():
                self.devices[device.id] = device
        
        # Group devices by room
        self._group_devices_by_room()
        
        # Update UI
        self._update_device_count()
        self._refresh_content()
        
        self.logger.info(f"Merged {len(self.devices)} devices from smart home services")
    
    def _group_devices_by_room(self):
        """Group devices by room"""
        self.rooms.clear()
        
        for device in self.devices.values():
            room = device.room or "Unknown"
            if room not in self.rooms:
                self.rooms[room] = []
            self.rooms[room].append(device)
    
    def _update_device_count(self):
        """Update device count in status panel"""
        online_count = len([d for d in self.devices.values() if d.is_online])
        total_count = len(self.devices)
        
        self.device_count_label.text = f"Devices: {online_count}/{total_count}"
        
        if online_count == total_count and total_count > 0:
            self.device_count_label.color = StosOSTheme.get_color('success')
        elif online_count > 0:
            self.device_count_label.color = StosOSTheme.get_color('warning')
        else:
            self.device_count_label.color = StosOSTheme.get_color('error')
    
    def _switch_view(self, view: str):
        """Switch between different views"""
        self.current_view = view
        self._refresh_content()
    
    def _refresh_content(self):
        """Refresh content based on current view"""
        self.content_container.clear_widgets()
        
        if self.current_view == "devices":
            self._build_devices_view()
        elif self.current_view == "rooms":
            self._build_rooms_view()
        elif self.current_view == "scenes":
            self._build_scenes_view()
    
    def _build_devices_view(self):
        """Build the devices list view"""
        if not self.devices:
            empty_label = StosOSLabel(
                text="No smart home devices found.\nMake sure your Google Assistant and Alexa devices are set up.",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.content_container.add_widget(empty_label)
            return
        
        # Sort devices by room, then by name
        sorted_devices = sorted(self.devices.values(), key=lambda d: (d.room or "ZZZ", d.name))
        
        for device in sorted_devices:
            device_card = DeviceCard(
                device=device,
                on_control=self._control_device
            )
            self.content_container.add_widget(device_card)
    
    def _build_rooms_view(self):
        """Build the rooms view"""
        if not self.rooms:
            empty_label = StosOSLabel(
                text="No rooms found.",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.content_container.add_widget(empty_label)
            return
        
        for room_name, room_devices in self.rooms.items():
            # Room header
            room_panel = StosOSPanel(
                title=f"{room_name} ({len(room_devices)} devices)",
                size_hint_y=None,
                height=dp(60) + len(room_devices) * dp(170)
            )
            
            room_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
            
            # Room controls
            room_controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            
            all_on_btn = StosOSButton(
                text="All On",
                button_type="success",
                size_hint_x=0.33
            )
            all_on_btn.bind(on_press=lambda x, r=room_name: self._control_room(r, "power_on"))
            room_controls.add_widget(all_on_btn)
            
            all_off_btn = StosOSButton(
                text="All Off",
                button_type="secondary",
                size_hint_x=0.33
            )
            all_off_btn.bind(on_press=lambda x, r=room_name: self._control_room(r, "power_off"))
            room_controls.add_widget(all_off_btn)
            
            room_settings_btn = StosOSIconButton(
                icon="⚙️",
                size=(dp(35), dp(35)),
                button_type="secondary"
            )
            room_controls.add_widget(room_settings_btn)
            
            room_layout.add_widget(room_controls)
            
            # Room devices
            for device in room_devices:
                device_card = DeviceCard(
                    device=device,
                    on_control=self._control_device
                )
                room_layout.add_widget(device_card)
            
            room_panel.add_widget(room_layout)
            self.content_container.add_widget(room_panel)
    
    def _build_scenes_view(self):
        """Build the scenes view"""
        if not self.scenes:
            empty_label = StosOSLabel(
                text="No scenes configured.\nCreate scenes to control multiple devices at once.",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.content_container.add_widget(empty_label)
            return
        
        for scene_name, scene_data in self.scenes.items():
            scene_card = SceneCard(
                scene_name=scene_name,
                scene_data=scene_data,
                on_activate=self._activate_scene,
                on_edit=self._edit_scene
            )
            self.content_container.add_widget(scene_card)
    
    def _control_device(self, device_id: str, command: str, parameters: Dict[str, Any] = None):
        """Control a specific device"""
        device = self.devices.get(device_id)
        if not device:
            self.logger.error(f"Device not found: {device_id}")
            return
        
        try:
            success = False
            
            # Route command to appropriate service
            if device.platform == Platform.GOOGLE and self.google_service:
                success = self.google_service.control_device(device_id, command, parameters)
            elif device.platform == Platform.ALEXA and self.alexa_service:
                success = self.alexa_service.control_device(device_id, command, parameters)
            
            if success:
                self.logger.info(f"Device control successful: {device.name} - {command}")
                # Refresh device status
                Clock.schedule_once(lambda dt: self._refresh_device_status(device_id), 1.0)
            else:
                self.logger.error(f"Device control failed: {device.name} - {command}")
                
        except Exception as e:
            self.logger.error(f"Error controlling device {device.name}: {e}")
            self.handle_error(e, f"control_device_{device_id}")
    
    def _control_room(self, room_name: str, command: str, parameters: Dict[str, Any] = None):
        """Control all devices in a room"""
        room_devices = self.rooms.get(room_name, [])
        
        if not room_devices:
            self.logger.warning(f"No devices found in room: {room_name}")
            return
        
        success_count = 0
        for device in room_devices:
            try:
                if device.platform == Platform.GOOGLE and self.google_service:
                    if self.google_service.control_device(device.id, command, parameters):
                        success_count += 1
                elif device.platform == Platform.ALEXA and self.alexa_service:
                    if self.alexa_service.control_device(device.id, command, parameters):
                        success_count += 1
            except Exception as e:
                self.logger.error(f"Error controlling device {device.name}: {e}")
        
        self.logger.info(f"Room control '{command}' executed on {success_count}/{len(room_devices)} devices in {room_name}")
        
        # Refresh room device status
        Clock.schedule_once(lambda dt: self._refresh_room_status(room_name), 1.0)
    
    def _activate_scene(self, scene_name: str, scene_data: Dict[str, Any]):
        """Activate a scene"""
        devices_config = scene_data.get('devices', {})
        
        if not devices_config:
            self.logger.warning(f"No devices configured in scene: {scene_name}")
            return
        
        success_count = 0
        total_count = len(devices_config)
        
        for device_id, device_config in devices_config.items():
            device = self.devices.get(device_id)
            if not device:
                self.logger.warning(f"Device not found for scene: {device_id}")
                continue
            
            try:
                # Apply each setting in the device config
                for setting, value in device_config.items():
                    command = self._setting_to_command(setting, value)
                    if command:
                        cmd, params = command
                        if device.platform == Platform.GOOGLE and self.google_service:
                            if self.google_service.control_device(device_id, cmd, params):
                                success_count += 1
                        elif device.platform == Platform.ALEXA and self.alexa_service:
                            if self.alexa_service.control_device(device_id, cmd, params):
                                success_count += 1
                        
            except Exception as e:
                self.logger.error(f"Error applying scene to device {device.name}: {e}")
        
        self.logger.info(f"Scene '{scene_name}' activated on {success_count} device settings")
        
        # Refresh all device status
        Clock.schedule_once(lambda dt: self._refresh_devices(), 2.0)
    
    def _setting_to_command(self, setting: str, value: Any) -> Optional[tuple]:
        """Convert scene setting to device command"""
        if setting == "power":
            return ("power_on" if value else "power_off", {})
        elif setting == "brightness":
            return ("set_brightness", {"brightness": value})
        elif setting == "volume":
            return ("set_volume", {"volume": value})
        elif setting == "temperature":
            return ("set_temperature", {"temperature": value})
        elif setting == "color":
            return ("set_color", {"color": value})
        else:
            return None
    
    def _refresh_devices(self, *args):
        """Refresh all device status"""
        try:
            if self.google_service and self.google_service.is_authenticated():
                self.google_service.refresh_device_status()
            
            if self.alexa_service and self.alexa_service.is_authenticated():
                self.alexa_service.refresh_device_status()
            
            self.last_refresh = datetime.now()
            self.logger.info("Device status refresh completed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing devices: {e}")
            self.handle_error(e, "refresh_devices")
    
    def _refresh_device_status(self, device_id: str):
        """Refresh status for a specific device"""
        device = self.devices.get(device_id)
        if not device:
            return
        
        try:
            if device.platform == Platform.GOOGLE and self.google_service:
                self.google_service.refresh_device_status(device_id)
            elif device.platform == Platform.ALEXA and self.alexa_service:
                self.alexa_service.refresh_device_status(device_id)
                
        except Exception as e:
            self.logger.error(f"Error refreshing device {device.name}: {e}")
    
    def _refresh_room_status(self, room_name: str):
        """Refresh status for all devices in a room"""
        room_devices = self.rooms.get(room_name, [])
        
        for device in room_devices:
            self._refresh_device_status(device.id)
    
    def _on_device_update(self, device: SmartDevice):
        """Handle device status update callback"""
        # Update local device cache
        self.devices[device.id] = device
        
        # Update UI if currently viewing devices
        if self.current_view in ["devices", "rooms"]:
            Clock.schedule_once(lambda dt: self._refresh_content(), 0.1)
    
    def _start_status_monitoring(self):
        """Start periodic status monitoring"""
        # Refresh device status every 30 seconds
        self.status_timer = Clock.schedule_interval(self._refresh_devices, 30.0)
    
    def _load_scenes(self):
        """Load scenes from configuration"""
        # Default scenes
        self.scenes = {
            "Study Mode": {
                "description": "Optimal lighting and temperature for studying",
                "devices": {
                    # Will be populated with actual device IDs when devices are discovered
                }
            },
            "Sleep Mode": {
                "description": "Turn off lights and lower temperature",
                "devices": {}
            },
            "Movie Mode": {
                "description": "Dim lights and adjust audio",
                "devices": {}
            }
        }
    
    def _show_add_scene_dialog(self, *args):
        """Show dialog to create new scene"""
        # TODO: Implement scene creation dialog
        self.logger.info("Scene creation dialog not yet implemented")
    
    def _edit_scene(self, scene_name: str, scene_data: Dict[str, Any]):
        """Edit an existing scene"""
        # TODO: Implement scene editing dialog
        self.logger.info(f"Scene editing not yet implemented: {scene_name}")
    
    def _show_settings(self, *args):
        """Show smart home settings"""
        # TODO: Implement settings dialog
        self.logger.info("Smart home settings not yet implemented")
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice command directed to smart home"""
        command_lower = command.lower()
        
        try:
            # Simple command parsing
            if "turn on" in command_lower or "turn off" in command_lower:
                action = "power_on" if "turn on" in command_lower else "power_off"
                
                # Extract device/room name
                words = command_lower.split()
                if "lights" in command_lower:
                    # Control all lights
                    light_devices = [d for d in self.devices.values() if d.device_type == DeviceType.LIGHT]
                    for device in light_devices:
                        self._control_device(device.id, action)
                    return True
                
                # Look for specific device names
                for device in self.devices.values():
                    if device.name.lower() in command_lower:
                        self._control_device(device.id, action)
                        return True
            
            elif "activate" in command_lower or "scene" in command_lower:
                # Scene activation
                for scene_name in self.scenes.keys():
                    if scene_name.lower() in command_lower:
                        self._activate_scene(scene_name, self.scenes[scene_name])
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
            return False
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        
        # Refresh devices when module is activated
        Clock.schedule_once(lambda dt: self._refresh_devices(), 0.5)
    
    def cleanup(self):
        """Clean up module resources"""
        try:
            # Stop status monitoring
            if self.status_timer:
                self.status_timer.cancel()
            
            # Clean up services
            if self.google_service:
                self.google_service.cleanup()
            
            if self.alexa_service:
                self.alexa_service.cleanup()
            
            super().cleanup()
            self.logger.info("Smart Home module cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")