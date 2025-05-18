"""
Logger utility for Image Tea Mini.

This module provides simple logging functions that can be imported and used 
from anywhere in the application to log messages to the Output Logs widget.
"""

from datetime import datetime
import sys
import traceback

# Reference to the output logs widget instance
_global_output_logs = None

def set_output_logs(output_logs_instance):
    """Set the global output logs instance for logging."""
    global _global_output_logs
    _global_output_logs = output_logs_instance

def log(message):
    """Log an INFO message."""
    # Print to console for fallback
    print(message)
    
    # Send to output logs widget if available
    if _global_output_logs:
        _global_output_logs.append_log("Info", message, "INFO")

def debug(message):
    """Log a DEBUG message."""
    # Print to console for fallback
    print(f"[DEBUG] {message}")
    
    # Send to output logs widget if available
    if _global_output_logs:
        _global_output_logs.append_log("Debug", message, "DEBUG")

def warning(message):
    """Log a WARNING message."""
    # Print to console for fallback
    print(f"[WARNING] {message}")
    
    # Send to output logs widget if available
    if _global_output_logs:
        _global_output_logs.append_log("Warning", message, "WARNING")

def error(message):
    """Log an ERROR message."""
    # Print to console for fallback
    print(f"[ERROR] {message}")
    
    # Send to output logs widget if available
    if _global_output_logs:
        _global_output_logs.append_log("Error", message, "ERROR")

def exception(e, message="An exception occurred"):
    """Log an exception with traceback."""
    # Get the exception traceback
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    # Print to console for fallback
    print(f"[EXCEPTION] {message}: {str(e)}")
    print(tb_str)
    
    # Send to output logs widget if available
    if _global_output_logs:
        _global_output_logs.append_log("Exception", f"{message}: {str(e)}", "ERROR")
        _global_output_logs.append_log("Exception", f"Traceback: {tb_str}", "ERROR")
