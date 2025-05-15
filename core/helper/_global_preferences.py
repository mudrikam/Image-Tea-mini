"""
Helper module for managing global preferences dialog.

This module handles loading, displaying, and saving global application preferences.
"""

from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtGui import QIcon
import os
import logging

def show_global_preferences(parent, config, base_dir):
    """
    Load and display the global preferences dialog.
    
    Args:
        parent: The parent window
        config: Application configuration dictionary
        base_dir: Base directory path for the application
    """
    logging.debug("Opening global preferences dialog")  # Change to debug level
    
    # Load the UI file
    ui_path = os.path.join(base_dir, "gui", "dialogs", "global_preferences_window.ui")
    
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    
    # Create the dialog
    preferences_dialog = loader.load(ui_file, parent)
    ui_file.close()
    
    # Set dialog properties
    preferences_dialog.setWindowTitle("Global Preferences")
    
    # Set window icon from application config
    icon_path = os.path.join(base_dir, config.get("app_icon", "image_tea.ico"))
    if os.path.exists(icon_path):
        preferences_dialog.setWindowIcon(QIcon(icon_path))
    
    # Connect browse button for log location
    if hasattr(preferences_dialog, 'logBrowseButton'):
        preferences_dialog.logBrowseButton.clicked.connect(
            lambda: browse_log_path(preferences_dialog, base_dir)
        )
    
    # Load current log settings
    load_debug_log_settings(preferences_dialog, config, base_dir)
    
    # Configure buttons
    if hasattr(preferences_dialog, 'pushButton'):
        preferences_dialog.pushButton.setText("Reset Default")
        preferences_dialog.pushButton.clicked.connect(
            lambda: reset_to_defaults(preferences_dialog, base_dir)
        )
    
    if hasattr(preferences_dialog, 'pushButton_3'):
        preferences_dialog.pushButton_3.setText("Cancel")
        preferences_dialog.pushButton_3.clicked.connect(preferences_dialog.reject)
    
    if hasattr(preferences_dialog, 'pushButton_2'):
        preferences_dialog.pushButton_2.setText("Save")
        preferences_dialog.pushButton_2.clicked.connect(
            lambda: save_preferences(preferences_dialog, config, base_dir)
        )
    
    # Add enableLoggingCheckBox if it exists
    if hasattr(preferences_dialog, 'enableLoggingCheckBox'):
        enabled = config.get("logging", {}).get("enabled", True)
        preferences_dialog.enableLoggingCheckBox.setChecked(enabled)
    
    # Add log level combo box if it exists
    if hasattr(preferences_dialog, 'logLevelComboBox'):
        level = config.get("logging", {}).get("level", "INFO")
        index = preferences_dialog.logLevelComboBox.findText(level)
        if index >= 0:
            preferences_dialog.logLevelComboBox.setCurrentIndex(index)
    
    # Show the dialog as modal
    result = preferences_dialog.exec()
    
    # Handle dialog result if needed
    if result == QtWidgets.QDialog.DialogCode.Accepted:
        logging.debug("Preferences saved")  # Change to debug level
    else:
        logging.debug("Preferences canceled")  # Change to debug level

def browse_log_path(dialog, base_dir):
    """
    Open a file dialog to select log file location.
    
    Args:
        dialog: The preferences dialog
        base_dir: Base directory path for the application
    """
    if not hasattr(dialog, 'logLocationInput'):
        return
        
    # Get the current path or default to logs directory in base dir
    current_path = dialog.logLocationInput.text() or os.path.join(base_dir, "logs")
    
    # Make sure parent directory exists
    parent_dir = os.path.dirname(current_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    
    # Open file dialog to select a log file
    file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
        dialog,
        "Select Log File Location",
        current_path,
        "Log Files (*.log);;All Files (*.*)"
    )
    
    # If a file was selected, update the line edit with the path
    if file_path:
        dialog.logLocationInput.setText(file_path)
        logging.debug(f"Log file location set to: {file_path}")

def get_default_log_path(base_dir):
    """
    Get the default log file path based on the application base directory.
    
    Args:
        base_dir: Base directory path for the application
        
    Returns:
        Default log file path
    """
    # Create logs directory in the base directory
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Return default log file path
    return os.path.join(logs_dir, "image_tea_debug.log")

def load_debug_log_settings(dialog, config, base_dir):
    """
    Load debug log settings from config into the dialog.
    
    Args:
        dialog: The preferences dialog
        config: Application configuration dictionary
        base_dir: Base directory path for the application
    """
    # Get log settings from config or use defaults
    log_config = config.get("logging", {})
    
    # Set log location
    if hasattr(dialog, 'logLocationInput'):
        default_log_path = get_default_log_path(base_dir)
        log_path = log_config.get("path", default_log_path)
        # Make path absolute if it's relative
        if not os.path.isabs(log_path):
            log_path = os.path.join(base_dir, log_path)
        dialog.logLocationInput.setText(log_path)
    
    # Set max log size
    if hasattr(dialog, 'maxLogSizeSpinBox'):
        max_size = log_config.get("max_size_mb", 10)
        dialog.maxLogSizeSpinBox.setValue(max_size)
    
    # Set max log count
    if hasattr(dialog, 'maxLogCountSpinBox'):
        max_count = log_config.get("max_count", 5)
        dialog.maxLogCountSpinBox.setValue(max_count)
    
    # Set logging enabled
    if hasattr(dialog, 'enableLoggingCheckBox'):
        enabled = log_config.get("enabled", True)
        dialog.enableLoggingCheckBox.setChecked(enabled)
    
    # Set log level
    if hasattr(dialog, 'logLevelComboBox'):
        level = log_config.get("level", "INFO")
        index = dialog.logLevelComboBox.findText(level)
        if index >= 0:
            dialog.logLevelComboBox.setCurrentIndex(index)

def reset_to_defaults(dialog, base_dir):
    """
    Reset the dialog settings to default values.
    
    Args:
        dialog: The preferences dialog
        base_dir: Base directory path for the application
    """
    logging.debug("Resetting preferences to defaults")
    
    # Reset log location
    if hasattr(dialog, 'logLocationInput'):
        default_log_path = get_default_log_path(base_dir)
        dialog.logLocationInput.setText(default_log_path)
    
    # Reset max log size
    if hasattr(dialog, 'maxLogSizeSpinBox'):
        dialog.maxLogSizeSpinBox.setValue(10)
    
    # Reset max log count
    if hasattr(dialog, 'maxLogCountSpinBox'):
        dialog.maxLogCountSpinBox.setValue(5)
    
    # Reset logging enabled
    if hasattr(dialog, 'enableLoggingCheckBox'):
        dialog.enableLoggingCheckBox.setChecked(True)
    
    # Reset log level
    if hasattr(dialog, 'logLevelComboBox'):
        index = dialog.logLevelComboBox.findText("INFO")
        if index >= 0:
            dialog.logLevelComboBox.setCurrentIndex(index)

def save_preferences(dialog, config, base_dir):
    """
    Save preferences from the dialog to config.
    
    Args:
        dialog: The preferences dialog
        config: Application configuration dictionary
        base_dir: Base directory path for the application
    """
    logging.debug("Saving preferences")
    
    # Ensure logging section exists in config
    if "logging" not in config:
        config["logging"] = {}
    
    # Save log settings
    if hasattr(dialog, 'logLocationInput'):
        log_path = dialog.logLocationInput.text()
        # Convert to relative path if it's inside the base directory
        if log_path.startswith(base_dir):
            rel_path = os.path.relpath(log_path, base_dir)
            # Use forward slashes for cross-platform compatibility in JSON
            rel_path = rel_path.replace("\\", "/")
            config["logging"]["path"] = rel_path
        else:
            config["logging"]["path"] = log_path
    
    # Save max log size
    if hasattr(dialog, 'maxLogSizeSpinBox'):
        config["logging"]["max_size_mb"] = dialog.maxLogSizeSpinBox.value()
    
    # Save max log count
    if hasattr(dialog, 'maxLogCountSpinBox'):
        config["logging"]["max_count"] = dialog.maxLogCountSpinBox.value()
    
    # Save logging enabled
    if hasattr(dialog, 'enableLoggingCheckBox'):
        config["logging"]["enabled"] = dialog.enableLoggingCheckBox.isChecked()
    
    # Save log level
    if hasattr(dialog, 'logLevelComboBox'):
        config["logging"]["level"] = dialog.logLevelComboBox.currentText()
    
    # Save config to file
    try:
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, 'w') as config_file:
            import json
            json.dump(config, config_file, indent=4)
        logging.debug("Config saved successfully")  # Change to debug level
    except Exception as e:
        error_msg = f"Error saving config: {e}"
        logging.error(error_msg)  # Keep errors at error level
        QtWidgets.QMessageBox.critical(dialog, "Error", error_msg)
    
    # Close the dialog
    dialog.accept()
