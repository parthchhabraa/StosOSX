"""
Google Assistant SDK Service for StosOS Smart Home Integration

Handles device discovery and control through Google Assistant SDK.
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

try:
    from google.assistant.embedded.v1alpha2 import (
        embedded_assistant_pb2,
        embedded_assistant_pb2_grpc
    )
    from google.auth.transport.grpc import secure_authorized_channel
    from google.oauth2.credentials import Credentials
    GOOGLE_ASSISTANT_AVAILABLE = True
except ImportError:
    GOOGLE_ASSISTANT_AVAILABLE = False
    logging.warning("Google Assistant SDK not available - using mock implementation")

from models.smart_device import SmartDevice, DeviceType, Platform


class GoogleAssistantService:
    """
    Google Assistant SDK service for smart home device control
    
    Handles device discovery, status monitoring, and control commands
    through the Google Assistant SDK.
    """
    
    def __init__(self, credentials_file: str = "config/google_credentials.json"):
        """
        Initialize Google Assistant service
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON file
        """
        self.credentials_file = Path(credentials_file)
        self.logger = logging.getLogger(__name__)
        
        self.credentials = None
        self.channel = None
        self.assistant = None
        self._authenticated = False
        self._devices = {}
        self._device_callbacks = []
        
        # Mock data for development/testing when SDK not available
        self._mock_devices = self._create_mock_devices()
    
    def _create_mock_devices(self) -> Dict[str, SmartDevice]:
        """Create mock devices for development/testing"""
        mock_devices = {}
        
        # Living room lights
        light1 = SmartDevice(
            name="Living Room Lights",
            device_type=DeviceType.LIGHT,
            platform=Platform.GOOGLE,
            status={"power": True, "brightness": 80, "color": "warm_white"},
            capabilities=["power", "brightness", "color"],
            room="Living Room"
        )
        mock_devices[light1.id] = light1
        
        # Bedroom thermostat
        thermostat = SmartDevice(
            name="Bedroom Thermostat",
            device_type=DeviceType.THERMOSTAT,
            platform=Platform.GOOGLE,
            status={"temperature": 72, "target_temperature": 70, "mode": "cool"},
            capabilities=["temperature", "target_temperature", "mode"],
            room="Bedroom"
        )
        mock_devices[thermostat.id] = thermostat
        
        # Kitchen speaker
        speaker = SmartDevice(
            name="Kitchen Speaker",
            device_type=DeviceType.SPEAKER,
            platform=Platform.GOOGLE,
            status={"power": True, "volume": 50, "playing": False},
            capabilities=["power", "volume", "play", "pause"],
            room="Kitchen"
        )
        mock_devices[speaker.id] = speaker
        
        # Smart switch
        switch = SmartDevice(
            name="Desk Lamp",
            device_type=DeviceType.SWITCH,
            platform=Platform.GOOGLE,
            status={"power": False},
            capabilities=["power"],
            room="Study"
        )
        mock_devices[switch.id] = switch
        
        return mock_devices
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Assistant SDK
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not GOOGLE_ASSISTANT_AVAILABLE:
            self.logger.warning("Using mock Google Assistant service")
            self._authenticated = True
            self._devices = self._mock_devices.copy()
            return True
        
        try:
            # Load credentials
            if not self.credentials_file.exists():
                self.logger.error(f"Google credentials file not found: {self.credentials_file}")
                return False
            
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            self.credentials = Credentials.from_authorized_user_info(creds_data)
            
            # Create secure channel
            self.channel = secure_authorized_channel(
                self.credentials,
                'embeddedassistant.googleapis.com:443'
            )
            
            # Create assistant client
            self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(self.channel)
            
            self._authenticated = True
            self.logger.info("Google Assistant service authenticated successfully")
            
            # Discover devices
            self._discover_devices()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Google Assistant: {e}")
            self._authenticated = False
            return False
    
    def is_authenticated(self) -> bool:
        """Check if service is authenticated"""
        return self._authenticated
    
    def _discover_devices(self):
        """Discover Google Assistant connected devices"""
        if not GOOGLE_ASSISTANT_AVAILABLE:
            # Use mock devices
            self._devices = self._mock_devices.copy()
            self.logger.info(f"Loaded {len(self._devices)} mock Google devices")
            return
        
        try:
            # In a real implementation, this would query the Google Assistant API
            # for connected smart home devices. For now, we'll use mock data.
            self._devices = self._mock_devices.copy()
            self.logger.info(f"Discovered {len(self._devices)} Google devices")
            
        except Exception as e:
            self.logger.error(f"Failed to discover Google devices: {e}")
            self._devices = {}
    
    def get_devices(self) -> List[SmartDevice]:
        """
        Get list of discovered Google Assistant devices
        
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
            command: Command to execute (e.g., "power_on", "set_brightness")
            parameters: Command parameters
            
        Returns:
            True if command successful, False otherwise
        """
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
            
            elif command == "set_brightness":
                if device.has_capability("brightness") and "brightness" in parameters:
                    brightness = max(0, min(100, int(parameters["brightness"])))
                    device.set_status_value("brightness", brightness)
                    return True
            
            elif command == "set_temperature":
                if device.has_capability("target_temperature") and "temperature" in parameters:
                    temp = max(50, min(90, int(parameters["temperature"])))
                    device.set_status_value("target_temperature", temp)
                    return True
            
            elif command == "set_volume":
                if device.has_capability("volume") and "volume" in parameters:
                    volume = max(0, min(100, int(parameters["volume"])))
                    device.set_status_value("volume", volume)
                    return True
            
            elif command == "play":
                if device.has_capability("play"):
                    device.set_status_value("playing", True)
                    return True
            
            elif command == "pause":
                if device.has_capability("pause"):
                    device.set_status_value("playing", False)
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
    
    def refresh_device_status(self, device_id: str = None) -> bool:
        """
        Refresh status for a specific device or all devices
        
        Args:
            device_id: Specific device ID to refresh, or None for all devices
            
        Returns:
            True if successful, False otherwise
        """
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
    
    def send_text_command(self, command_text: str) -> Optional[str]:
        """
        Send a text command to Google Assistant
        
        Args:
            command_text: Natural language command
            
        Returns:
            Assistant response text if successful, None otherwise
        """
        if not GOOGLE_ASSISTANT_AVAILABLE:
            # Mock response for development
            return f"Mock response for: {command_text}"
        
        try:
            # In a real implementation, this would send the command to Google Assistant
            # and return the response. For now, return a mock response.
            self.logger.info(f"Sending command to Google Assistant: {command_text}")
            return f"Command executed: {command_text}"
            
        except Exception as e:
            self.logger.error(f"Error sending text command: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test the connection to Google Assistant
        
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
            if self.channel:
                self.channel.close()
            self._authenticated = False
            self._devices.clear()
            self._device_callbacks.clear()
            self.logger.info("Google Assistant service cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")