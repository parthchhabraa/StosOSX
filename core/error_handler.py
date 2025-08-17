"""
Error Handling System for StosOS
Provides centralized error handling, recovery, and user notification
"""

import logging
import traceback
from enum import Enum
from typing import Dict, Callable, Any, Optional
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Types of errors that can occur"""
    NETWORK = "network"
    HARDWARE = "hardware"
    MODULE = "module"
    SYSTEM = "system"
    API = "api"
    CONFIG = "config"
    USER_INPUT = "user_input"


class ErrorHandler:
    """Centralized error handling and recovery system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_strategies: Dict[ErrorType, Callable] = {}
        self.error_history = []
        self.max_history = 100
        
        # Error counters for tracking patterns
        self.error_counts: Dict[str, int] = {}
        
        # Setup default recovery strategies
        self._setup_default_strategies()
    
    def register_recovery_strategy(self, error_type: ErrorType, strategy: Callable) -> None:
        """
        Register a recovery strategy for a specific error type
        
        Args:
            error_type: Type of error this strategy handles
            strategy: Callable that attempts to recover from the error
        """
        self.recovery_strategies[error_type] = strategy
        self.logger.debug(f"Recovery strategy registered for {error_type.value}")
    
    def handle_error(self, error: Exception, context: str = "", 
                    error_type: ErrorType = ErrorType.SYSTEM,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    module_id: str = "") -> bool:
        """
        Handle an error with appropriate logging, recovery, and notification
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            error_type: Type of error for recovery strategy selection
            severity: Severity level of the error
            module_id: ID of the module where error occurred
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        try:
            # Create error record
            error_record = {
                'timestamp': datetime.now(),
                'error_type': error_type.value,
                'severity': severity.value,
                'module_id': module_id,
                'context': context,
                'error_message': str(error),
                'error_class': type(error).__name__,
                'traceback': traceback.format_exc()
            }
            
            # Add to history
            self._add_to_history(error_record)
            
            # Update error counts
            error_key = f"{error_type.value}:{type(error).__name__}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            # Log the error
            self._log_error(error_record)
            
            # Attempt recovery
            recovery_success = self._attempt_recovery(error_type, error, context)
            
            # Check for error patterns
            self._check_error_patterns(error_key)
            
            return recovery_success
            
        except Exception as handler_error:
            # Error in error handler - log and continue
            self.logger.critical(f"Error in error handler: {handler_error}")
            return False
    
    def get_error_history(self, limit: int = 10) -> list:
        """
        Get recent error history
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error records
        """
        return self.error_history[-limit:] if self.error_history else []
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics and patterns
        
        Returns:
            Dictionary with error statistics
        """
        total_errors = len(self.error_history)
        
        # Count by type
        type_counts = {}
        severity_counts = {}
        module_counts = {}
        
        for error in self.error_history:
            error_type = error['error_type']
            severity = error['severity']
            module_id = error['module_id']
            
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if module_id:
                module_counts[module_id] = module_counts.get(module_id, 0) + 1
        
        return {
            'total_errors': total_errors,
            'error_counts': self.error_counts.copy(),
            'type_distribution': type_counts,
            'severity_distribution': severity_counts,
            'module_distribution': module_counts
        }
    
    def clear_error_history(self) -> None:
        """Clear error history and reset counters"""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info("Error history cleared")
    
    def _setup_default_strategies(self) -> None:
        """Setup default recovery strategies for common error types"""
        
        def network_recovery(error: Exception, context: str) -> bool:
            """Default network error recovery"""
            self.logger.info("Attempting network error recovery")
            # Could implement network reconnection logic here
            return False
        
        def module_recovery(error: Exception, context: str) -> bool:
            """Default module error recovery"""
            self.logger.info(f"Attempting module error recovery for context: {context}")
            # Could implement module restart logic here
            return False
        
        def hardware_recovery(error: Exception, context: str) -> bool:
            """Default hardware error recovery"""
            self.logger.info("Attempting hardware error recovery")
            # Could implement hardware reinitialization here
            return False
        
        # Register default strategies
        self.recovery_strategies[ErrorType.NETWORK] = network_recovery
        self.recovery_strategies[ErrorType.MODULE] = module_recovery
        self.recovery_strategies[ErrorType.HARDWARE] = hardware_recovery
    
    def _add_to_history(self, error_record: Dict) -> None:
        """Add error record to history"""
        self.error_history.append(error_record)
        
        # Limit history size
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
    
    def _log_error(self, error_record: Dict) -> None:
        """Log error with appropriate level based on severity"""
        severity = error_record['severity']
        message = (f"Error in {error_record['context']}: "
                  f"{error_record['error_message']} "
                  f"(Type: {error_record['error_type']}, "
                  f"Module: {error_record['module_id']})")
        
        if severity == ErrorSeverity.CRITICAL.value:
            self.logger.critical(message)
        elif severity == ErrorSeverity.HIGH.value:
            self.logger.error(message)
        elif severity == ErrorSeverity.MEDIUM.value:
            self.logger.warning(message)
        else:  # LOW
            self.logger.info(message)
        
        # Log full traceback for debugging
        if error_record['traceback']:
            self.logger.debug(f"Full traceback: {error_record['traceback']}")
    
    def _attempt_recovery(self, error_type: ErrorType, error: Exception, context: str) -> bool:
        """Attempt to recover from error using registered strategy"""
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            try:
                self.logger.info(f"Attempting recovery for {error_type.value} error")
                return strategy(error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
                return False
        else:
            self.logger.debug(f"No recovery strategy available for {error_type.value}")
            return False
    
    def _check_error_patterns(self, error_key: str) -> None:
        """Check for error patterns that might indicate systemic issues"""
        count = self.error_counts[error_key]
        
        # Alert on repeated errors
        if count == 5:
            self.logger.warning(f"Error pattern detected: {error_key} occurred {count} times")
        elif count == 10:
            self.logger.error(f"Frequent error pattern: {error_key} occurred {count} times")
        elif count >= 20:
            self.logger.critical(f"Critical error pattern: {error_key} occurred {count} times")


# Global error handler instance
error_handler = ErrorHandler()