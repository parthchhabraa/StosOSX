"""
Smart device data model for StosOS smart home integration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
import uuid


class DeviceType(Enum):
    """Smart device types."""
    LIGHT = "LIGHT"
    THERMOSTAT = "THERMOSTAT"
    SPEAKER = "SPEAKER"
    SWITCH = "SWITCH"
    SENSOR = "SENSOR"
    CAMERA = "CAMERA"
    LOCK = "LOCK"
    FAN = "FAN"
    OTHER = "OTHER"


class Platform(Enum):
    """Smart home platforms."""
    GOOGLE = "GOOGLE"
    ALEXA = "ALEXA"
    OTHER = "OTHER"


@dataclass
class SmartDevice:
    """
    Smart device model for home automation control.
    
    Attributes:
        id: Unique identifier for the device
        name: Human-readable device name
        device_type: Type of device (light, thermostat, etc.)
        platform: Platform the device is connected to (Google, Alexa)
        status: Current device status and properties
        capabilities: List of supported capabilities/actions
        room: Room where the device is located
        last_updated: When the device status was last updated
        is_online: Whether the device is currently reachable
    """
    name: str
    device_type: DeviceType
    platform: Platform
    status: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    room: str = "Unknown"
    is_online: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate smart device data after initialization."""
        if not self.name.strip():
            raise ValueError("Device name cannot be empty")
        
        if isinstance(self.device_type, str):
            self.device_type = DeviceType(self.device_type)
        
        if isinstance(self.platform, str):
            self.platform = Platform(self.platform)
        
        # Ensure capabilities are unique
        self.capabilities = list(set(self.capabilities))
    
    def to_dict(self) -> dict:
        """Convert smart device to dictionary for database storage."""
        return {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type.value,
            'platform': self.platform.value,
            'status': str(self.status),  # Store as string representation
            'capabilities': ','.join(self.capabilities),  # Store as comma-separated string
            'room': self.room,
            'is_online': self.is_online,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SmartDevice':
        """Create smart device from dictionary data."""
        # Handle datetime fields
        if data.get('last_updated'):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        # Handle enum fields
        if data.get('device_type'):
            data['device_type'] = DeviceType(data['device_type'])
        if data.get('platform'):
            data['platform'] = Platform(data['platform'])
        
        # Handle capabilities list
        if data.get('capabilities'):
            data['capabilities'] = [cap.strip() for cap in data['capabilities'].split(',') if cap.strip()]
        else:
            data['capabilities'] = []
        
        # Handle status dict (stored as string)
        if data.get('status'):
            try:
                # Simple parsing - in production, use json.loads
                data['status'] = eval(data['status']) if data['status'] != '{}' else {}
            except:
                data['status'] = {}
        else:
            data['status'] = {}
        
        return cls(**data)
    
    def update_status(self, new_status: Dict[str, Any]):
        """Update device status."""
        self.status.update(new_status)
        self.last_updated = datetime.now()
    
    def set_online_status(self, is_online: bool):
        """Update device online status."""
        self.is_online = is_online
        self.last_updated = datetime.now()
    
    def add_capability(self, capability: str):
        """Add a capability to the device."""
        if capability and capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def remove_capability(self, capability: str):
        """Remove a capability from the device."""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
    
    def has_capability(self, capability: str) -> bool:
        """Check if device has a specific capability."""
        return capability in self.capabilities
    
    def get_status_value(self, key: str, default=None):
        """Get a specific status value."""
        return self.status.get(key, default)
    
    def set_status_value(self, key: str, value: Any):
        """Set a specific status value."""
        self.status[key] = value
        self.last_updated = datetime.now()
    
    def is_controllable(self) -> bool:
        """Check if device can be controlled (has capabilities and is online)."""
        return self.is_online and len(self.capabilities) > 0