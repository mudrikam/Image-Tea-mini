"""
Helper module for resetting widgets to their default layout as defined in UI files.

This module provides a simple reset function that applies original dimensions from UI files
without any hardcoding or searching logic.
"""

from PySide6 import QtWidgets, QtUiTools, QtCore
from core.utils.logger import log, debug, warning, error, exception

def reset_widget_to_default(widget, ui_path):
    """
    Reset a widget to its default size as defined in the UI file.
    
    Args:
        widget: The widget to reset
        ui_path: Full path to the UI file defining the widget's original dimensions
    
    Returns:
        bool: True if reset was successful, False otherwise
    """
    # Load the UI file to get original dimensions
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_path)
    if ui_file.open(QtCore.QFile.ReadOnly):
        try:
            # Load the widget from the UI file
            original_widget = loader.load(ui_file)
            ui_file.close()
            
            # Get the original size
            original_width = original_widget.width()
            original_height = original_widget.height()
            
            # Fix: Set both minimum and maximum sizes to enforce dimensions
            widget.setMinimumSize(original_width, original_height)
            widget.setMaximumSize(original_width, original_height)
            
            # Force resize 
            widget.resize(original_width, original_height)
            
            # Allow it to be resizable again after a brief delay
            QtCore.QTimer.singleShot(100, lambda: reset_size_constraints(widget))
            
            widget_name = widget.windowTitle() or "Unknown widget"
            # log(f"Reset {widget_name} to default size.")
            return True
        except Exception as e:
            error(f"Error resetting widget size: {e}")
    else:
        error(f"Could not open UI file: {ui_path}")
    
    return False

def reset_size_constraints(widget):
    """Remove size constraints after reset to allow user resizing."""
    widget.setMinimumSize(10, 10)  # Set reasonable minimum
    widget.setMaximumSize(16777215, 16777215)  # Qt's QWIDGETSIZE_MAX
