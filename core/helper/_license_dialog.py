"""
Helper module for the License dialog.

This module contains functions to show the License dialog with content from LICENSE.txt.
"""

from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtGui import QIcon
import os

def show_license_dialog(parent, config, base_dir):
    """
    Show the License dialog with content from LICENSE.txt.
    
    Args:
        parent: The parent window
        config: The application configuration dictionary
        base_dir: Base directory path
    """
    # Load the License window UI
    ui_path = os.path.join(base_dir, "gui", "dialogs", "license_window.ui")
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    license_dialog = loader.load(ui_file, parent)
    ui_file.close()
    
    # Set window icon
    icon_path = os.path.join(base_dir, "res", config.get("app_icon", "image_tea.ico"))
    if os.path.exists(icon_path):
        license_dialog.setWindowIcon(QIcon(icon_path))
    
    # Set the window title
    app_name = config.get("app_name", "Application")
    license_type = config.get("app_license", "License")
    license_dialog.setWindowTitle(f"{app_name} - {license_type} License")
    
    # Set title label
    license_dialog.lblTitle.setText(f"{license_type} License")
    
    # Load license text from LICENSE.txt
    license_path = os.path.join(base_dir, "LICENSE.txt")
    license_text = "License file not found."
    
    try:
        if os.path.exists(license_path):
            with open(license_path, 'r') as license_file:
                license_text = license_file.read()
        else:
            license_text = f"License file not found at: {license_path}"
    except Exception as e:
        license_text = f"Error reading license file: {str(e)}"
    
    # Display the license text
    license_dialog.textLicense.setPlainText(license_text)
    
    # Show the dialog as modal
    license_dialog.exec()
