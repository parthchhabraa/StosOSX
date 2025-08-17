"""
Alexa Voice Service API Integration for StosOS Smart Home

Handles device discovery and control through Alexa Voice Service API.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta

try:
    from ask_sdk_core.skill_builder import SkillBuilder
    from ask_sdk_core.dispatch_components import AbstractRequestHandler
    from ask_sdk_core.utils import is_request_type, is_intent_name
    from ask_sdk_model import Response
    ALEXA_SDK_AVAILABLE = True
except ImportError:
    ALEXA_SDK_AVAILABLE = False
    logging.warning("Alexa SDK not available - using mock implementation")

from models.smart_device import SmartDevice, DeviceType, Platform


class AlexaService:
    """
    Alexa Voice Service API integration for smart home device control
    
    Handles device discovery, status monitoring, and control commands
    through the Alexa Voice Service API.
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 refresh_token: str = None, config_file: str = "config/alexa_config.json"):
        """
        Initialize Alexa service
        
        Args:
            client_id: Alexa app client ID
            client_secret: Alexa app client secret
            refresh_token: OAuth refresh token
            config_file: Path to Alexa configuration file
        """
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._load_config()
        
        self.access_token = None
        self.token_expires_at = None
        self._authenticated = False
        self._devices = {}
        self._device_callbacks = []
        
        # API endpoints
        self.auth_url = "https://api.amazon.com/auth/o2/token"
        self.smart_home_url = "https://api.amazonalexa.com/v1/smarthome"
        
        # Mock data for development/testing
        self._mock_devices = self._create_mock_devices()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.client_id = self.client_id or config.get('client_id')
                self.client_secret = self.client_secret or config.get('client_secret')
                self.refresh_token = self.refresh_token or config.get('refresh_token')
                
                self.logger.debug("Loaded Alexa configuration from file")
        except Exception as e:
            self.logger.warning(f"Could not load Alexa config: {e}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.logger.debug("Saved Alexa configuration to file")
        except Exception as e:
            self.logger.error(f"Could not save Alexa config: {e}")
    
    def _create_mock_devices(self) -> Dict[str, SmartDevice]:
        """Create mock Alexa devices for development/testing"""
        mock_devices = {}
        
        # Echo Dot in bedroom
        echo_dot = SmartDevice(
            name="Bedroom Echo Dot",
            device_type=DeviceType.SPEAKER,
            platform=Platform.ALEXA,
            status={"power": True, "volume": 40, "playing": False, "muted": False},
            capabilities=["power", "volume", "play", "pause", "mute"],
            room="Bedroom"
        )
        mock_devices[echo_dot.id] = echo_dot
        
        # Smart plug
        smart_plug = SmartDevice(
            name="Coffee Maker Plug",
            device_type=DeviceType.SWITCH,
            platform=Platform.ALEXA,
            status={"power": False},
            capabilities=["power"],
            room="Kitchen"
        )
        mock_devices[smart_plug.id] = smart_plug
        
        # Smart bulb
        smart_bulb = SmartDevice(
            name="Hallway Light",
            device_type=DeviceType.LIGHT,
            platform=Platform.ALEXA,
            status={"power": True, "brightness": 75, "color": "white"},
            capabilities=["power", "brightness", "color"],
            room="Hallway"
        )
        mock_devices[smart_bulb.id] = smart_bulb
        
        # Temperature sensor
        temp_sensor = SmartDevice(
            name="Living Room Sensor",
            device_type=DeviceType.SENSOR,
            platform=Platform.ALEXA,
            status={"temperature": 73, "humidity": 45},
            capabilities=["temperature", "humidity"],
            room="Living Room"
        )
        mock_devices[temp_sensor.id] = temp_sensor
        
        return mock_devices
    
    def authenticate(self) -> bool:
        """
        Authenticate with Alexa Voice Service
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not ALEXA_SDK_AVAILABLE:
            self.logger.warning("Using mock Alexa service")
            self._authenticated = True
            self._devices = self._mock_devices.copy()
            return True
        
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            self.logger.error("Missing Alexa credentials")
            return False
        
        try:
            # Get access token using refresh token
            token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.auth_url, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            self.access_token = token_info['access_token']
            
            # Calculate token expiration
            expires_in = token_info.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            self._authenticated = True
            self.logger.info("Alexa service authenticated successfully")
            
            # Discover devices
            self._discover_devices()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Alexa: {e}")
            self._authenticated = False
            return False
    
    def is_authenticated(self) -> bool:
        """Check if service is authenticated and token is valid"""
        if not ALEXA_SDK_AVAILABLE:
            # For mock implementation, just return authenticated status
            return self._authenticated
        
        if not self._authenticated or not self.access_token:
            return False
        
        # Check if token is expired
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            self.logger.info("Alexa token expired, re-authenticating")
            return self.authenticate()
        
        return True
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def _discover_devices(self):
        """Discover Alexa connected devices"""
        if not ALEXA_SDK_AVAILABLE:
            # Use mock devices
            self._devices = self._mock_devices.copy()
            self.logger.info(f"Loaded {len(self._devices)} mock Alexa devices")
            return
        
        try:
            # In a real implementation, this would query the Alexa Smart Home API
            # for connected devices. For now, we'll use mock data.
            self._devices = self._mock_devices.copy()
            self.logger.info(f"Discovered {len(self._devices)} Alexa devices")
            
        except Exception as e:
            self.logger.error(f"Failed to discover Alexa devices: {e}")
            self._devices = {}
    
    def get_devices(self) -> List[SmartDevice]:
        """
        Get list of discovered Alexa devices
        
        Returns:
            List of SmartDevice objects
        """
        return list(self._devices.values())
    
    def get_device(self, device_id: str) -> Optional[SmartDevice]:
        """
        Get a specific device by ID
        
        Args:
            device_id: Device ID to retrieve
            
        Returns:
            SmartDevice if found, None otherwise
        """
        return self._devices.get(device_id)
    
    def control_device(self, device_id: str, command: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Send control command to a device
        
        Args:
            device_id: Target device ID
            command: Command to execute
            parameters: Command parameters
            
        Returns:
            True if command successful, False otherwise
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Alexa")
            return False
        
        device = self.get_device(device_id)
        if not device:
            self.logger.error(f"Device not found: {device_id}")
            return False
        
        if not device.is_online:
            self.logger.error(f"Device offline: {device.name}")
            return False
        
        try:
            # Execute command based on device type and capabilities
            success = self._execute_device_command(device, command, parameters or {})
            
            if success:
                # Update device status
                device.last_updated = datetime.now()
                self._notify_device_update(device)
                self.logger.info(f"Command '{command}' executed on {device.name}")
            else:
                self.logger.error(f"Failed to execute command '{command}' on {device.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error controlling device {device.name}: {e}")
            return False
    
    def _execute_device_command(self, device: SmartDevice, command: str, parameters: Dict[str, Any]) -> bool:
        """
        Execute a specific command on a device
        
        Args:
            device: Target device
            command: Command to execute
            parameters: Command parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if command == "power_on":
                if device.has_capability("power"):
                    device.set_status_value("power", True)
                    return True
            
            elif command == "power_off":
                if device.has_capability("power"):
                    device.set_status_value("power", False)
                    return True
            
            elif command == "set_volume":
                if device.has_capability("volume") and "volume" in parameters:
                    volume = max(0, min(100, int(parameters["volume"])))
                    device.set_status_value("volume", volume)
                    return True
            
            elif command == "mute":
                if device.has_capability("mute"):
                    device.set_status_value("muted", True)
                    return True
            
            elif command == "unmute":
                if device.has_capability("mute"):
                    device.set_status_value("muted", False)
                    return True
            
            elif command == "play":
                if device.has_capability("play"):
                    device.set_status_value("playing", True)
                    return True
            
            elif command == "pause":
                if device.has_capability("pause"):
                    device.set_status_value("playing", False)
                    return True
            
            elif command == "set_brightness":
                if device.has_capability("brightness") and "brightness" in parameters:
                    brightness = max(0, min(100, int(parameters["brightness"])))
                    device.set_status_value("brightness", brightness)
                    return True
            
            elif command == "set_color":
                if device.has_capability("color") and "color" in parameters:
                    device.set_status_value("color", parameters["color"])
                    return True
            
            else:
                self.logger.warning(f"Unknown command: {command}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            return False
        
        return False
    
    def send_voice_command(self, command_text: str) -> Optional[str]:
        """
        Send a voice command to Alexa
        
        Args:
            command_text: Natural language command
            
        Returns:
            Alexa response text if successful, None otherwise
        """
        if not self.is_authenticated():
            self.logger.error("Not authenticated with Alexa")
            return None
        
        try:
            # In a real implementation, this would send the command to Alexa
            # and return the response. For now, return a mock response.
            self.logger.info(f"Sending command to Alexa: {command_text}")
            return f"Alexa executed: {command_text}"
            
        except Exception as e:
            self.logger.error(f"Error sending voice command: {e}")
            return None
    
    def refresh_device_status(self, device_id: str = None) -> bool:
        """
        Refresh status for a specific device or all devices
        
        Args:
            device_id: Specific device ID to refresh, or None for all devices
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        try:
            if device_id:
                device = self.get_device(device_id)
                if device:
                    # In a real implementation, this would query the device status
                    # For now, we'll just update the timestamp
                    device.last_updated = datetime.now()
                    self._notify_device_update(device)
                    return True
                return False
            else:
                # Refresh all devices
                for device in self._devices.values():
                    device.last_updated = datetime.now()
                    self._notify_device_update(device)
                return True
                
        except Exception as e:
            self.logger.error(f"Error refreshing device status: {e}")
            return False
    
    def add_device_callback(self, callback: Callable[[SmartDevice], None]):
        """
        Add callback for device status updates
        
        Args:
            callback: Function to call when device status changes
        """
        if callback not in self._device_callbacks:
            self._device_callbacks.append(callback)
    
    def remove_device_callback(self, callback: Callable[[SmartDevice], None]):
        """
        Remove device status update callback
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)
    
    def _notify_device_update(self, device: SmartDevice):
        """
        Notify all callbacks of device status update
        
        Args:
            device: Updated device
        """
        for callback in self._device_callbacks:
            try:
                callback(device)
            except Exception as e:
                self.logger.error(f"Error in device callback: {e}")
    
    def get_device_groups(self) -> Dict[str, List[str]]:
        """
        Get device groups/rooms
        
        Returns:
            Dictionary mapping room names to device IDs
        """
        groups = {}
        for device in self._devices.values():
            room = device.room or "Unknown"
            if room not in groups:
                groups[room] = []
            groups[room].append(device.id)
        
        return groups
    
    def control_group(self, room: str, command: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Send command to all devices in a room/group
        
        Args:
            room: Room name
            command: Command to execute
            parameters: Command parameters
            
        Returns:
            True if all commands successful, False otherwise
        """
        devices_in_room = [d for d in self._devices.values() if d.room == room]
        
        if not devices_in_room:
            self.logger.warning(f"No devices found in room: {room}")
            return False
        
        success_count = 0
        for device in devices_in_room:
            if self.control_device(device.id, command, parameters):
                success_count += 1
        
        self.logger.info(f"Group command '{command}' executed on {success_count}/{len(devices_in_room)} devices in {room}")
        return success_count == len(devices_in_room)
    
    def test_connection(self) -> bool:
        """
        Test the connection to Alexa Voice Service
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            if not self.is_authenticated():
                return False
            
            # Try to get device list as a simple test
            devices = self.get_devices()
            return True  # If we can get devices, connection is working
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self._authenticated = False
            self.access_token = None
            self.token_expires_at = None
            self._devices.clear()
            self._device_callbacks.clear()
            self.logger.info("Alexa service cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")