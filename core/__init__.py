"""
StosOS Core Framework
Provides base classes and utilities for the StosOS desktop environment
"""

from .base_module import BaseModule
from .config_manager import ConfigManager
from .screen_manager import StosOSScreenManager
from .error_handler import ErrorHandler, ErrorType, ErrorSeverity, error_handler
from .logger import StosOSLogger, stosos_logger
from .power_manager import PowerManager, PowerState, PowerConfig, power_manager

__all__ = [
    'BaseModule',
    'ConfigManager', 
    'StosOSScreenManager',
    'ErrorHandler',
    'ErrorType',
    'ErrorSeverity',
    'error_handler',
    'StosOSLogger',
    'stosos_logger',
    'PowerManager',
    'PowerState',
    'PowerConfig',
    'power_manager'
]