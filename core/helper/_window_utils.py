"""
Helper module for window-related utilities.

This module provides functions for window positioning and other window-related operations.
"""

from PySide6 import QtWidgets, QtCore

def center_window(window):
    """
    Center a window on the screen.
    
    Args:
        window: The window to center
    """
    # Process any pending events to ensure window geometry is updated
    QtWidgets.QApplication.processEvents()
    
    # Get the available screen geometry
    screen = QtWidgets.QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    
    # Ensure window has valid size information before centering
    window_size = window.size()
    if window_size.width() <= 0 or window_size.height() <= 0:
        # If the window size isn't valid yet, adjust it
        window.adjustSize()
    
    # Calculate the center position
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    
    # Move the window's center point to the screen's center point
    window_geometry.moveCenter(center_point)
    
    # Move the window to the center position
    window.move(window_geometry.topLeft())
