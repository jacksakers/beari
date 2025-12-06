"""
Debug Logger for Beari2.
Provides detailed logging of parsing and learning steps.
"""

from typing import Any, Optional
from datetime import datetime


class DebugLogger:
    """
    Logs detailed analysis steps for debugging Beari's learning process.
    
    Can be enabled/disabled globally to show/hide debug output.
    """
    
    def __init__(self, enabled: bool = False):
        """
        Initialize the debug logger.
        
        Args:
            enabled: Whether debug logging is enabled
        """
        self.enabled = enabled
        self.indent_level = 0
    
    def enable(self):
        """Enable debug logging."""
        self.enabled = True
    
    def disable(self):
        """Disable debug logging."""
        self.enabled = False
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message if debug mode is enabled.
        
        Args:
            message: Message to log
            level: Log level (INFO, PARSE, LEARN, RESPONSE, etc.)
        """
        if self.enabled:
            indent = "  " * self.indent_level
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [{level}] {indent}{message}")
    
    def log_step(self, step_number: int, description: str):
        """Log a numbered analysis step."""
        self.log(f"Step {step_number}: {description}", "STEP")
    
    def log_parse(self, message: str):
        """Log parsing activity."""
        self.log(message, "PARSE")
    
    def log_learn(self, message: str):
        """Log learning activity."""
        self.log(message, "LEARN")
    
    def log_response(self, message: str):
        """Log response generation activity."""
        self.log(message, "RESPONSE")
    
    def log_db(self, message: str):
        """Log database operations."""
        self.log(message, "DB")
    
    def log_object(self, obj_name: str, obj_data: dict):
        """Log object state."""
        if self.enabled:
            self.log(f"Object '{obj_name}':", "OBJECT")
            self.indent_level += 1
            for key, value in obj_data.items():
                self.log(f"{key}: {value}", "OBJECT")
            self.indent_level -= 1
    
    def indent(self):
        """Increase indentation level."""
        self.indent_level += 1
    
    def dedent(self):
        """Decrease indentation level."""
        self.indent_level = max(0, self.indent_level - 1)
    
    def section(self, title: str):
        """Log a section header."""
        if self.enabled:
            print(f"\n{'='*60}")
            print(f"  {title}")
            print(f"{'='*60}")


# Global debug logger instance
_debug_logger = DebugLogger(enabled=False)


def get_debug_logger() -> DebugLogger:
    """Get the global debug logger instance."""
    return _debug_logger


def set_debug_mode(enabled: bool):
    """Enable or disable debug mode globally."""
    _debug_logger.enabled = enabled
