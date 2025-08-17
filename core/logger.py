"""
Logging configuration for StosOS
Provides centralized logging setup and utilities
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class StosOSLogger:
    """Centralized logging configuration for StosOS"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging with file and console handlers"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler for detailed logs
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "stosos.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Configure Kivy logger to use our setup
        kivy_logger = logging.getLogger('kivy')
        kivy_logger.setLevel(logging.WARNING)  # Reduce Kivy verbosity
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for a specific module"""
        return logging.getLogger(name)
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug logging"""
        level = logging.DEBUG if enabled else logging.INFO
        logging.getLogger().setLevel(level)
        
        # Update console handler level
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)


# Global logger instance
stosos_logger = StosOSLogger()