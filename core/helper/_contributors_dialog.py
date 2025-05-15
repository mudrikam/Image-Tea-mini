"""
Helper module for the Contributors dialog.

This module contains functions to show the Contributors dialog with content from CONTRIBUTORS.txt.
"""

from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtGui import QIcon
import os

def show_contributors_dialog(parent, config, base_dir):
    """
    Show the Contributors dialog with content from CONTRIBUTORS.txt.
    
    Args:
        parent: The parent window
        config: The application configuration dictionary
        base_dir: Base directory path
    """
    # Load the Contributors window UI
    ui_path = os.path.join(base_dir, "gui", "dialogs", "contributors_window.ui")
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    contributors_dialog = loader.load(ui_file, parent)
    ui_file.close()
    
    # Set window icon
    icon_path = os.path.join(base_dir, config.get("app_icon", "image_tea.ico"))
    if os.path.exists(icon_path):
        contributors_dialog.setWindowIcon(QIcon(icon_path))
    
    # Set the window title
    app_name = config.get("app_name", "Application")
    contributors_dialog.setWindowTitle(f"{app_name} - Contributors")
    
    # Load contributors text from CONTRIBUTORS.txt
    contributors_path = os.path.join(base_dir, "CONTRIBUTORS.txt")
    contributors_text = "No contributors information available."
    
    try:
        if os.path.exists(contributors_path):
            with open(contributors_path, 'r') as contributors_file:
                contributors_text = contributors_file.read()
        else:
            contributors_text = f"Contributors file not found at: {contributors_path}"
    except Exception as e:
        contributors_text = f"Error reading contributors file: {str(e)}"
    
    # Display the contributors text
    contributors_dialog.textContributors.setPlainText(contributors_text)
    
    # Show the dialog as modal
    contributors_dialog.exec()
