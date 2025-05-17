"""
Helper module for the About dialog.

This module contains functions to show the About dialog with information from config.json.
"""

from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtGui import QIcon
import os

# Import the license dialog helper and URL opener
from core.helper._license_dialog import show_license_dialog
from core.helper._url_handler import open_url
from core.helper._window_utils import center_window

def show_about_dialog(parent, config, base_dir):
    """
    Show the About dialog with application information.
    
    Args:
        parent: The parent window
        config: The application configuration dictionary
        base_dir: Base directory path
    """
    # Load the About window UI
    ui_path = os.path.join(base_dir, "gui", "dialogs", "about_window.ui")
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    about_dialog = loader.load(ui_file, parent)
    ui_file.close()
    
    # Set window icon
    icon_path = os.path.join(base_dir, "res", config.get("app_icon", "image_tea.ico"))
    if os.path.exists(icon_path):
        about_dialog.setWindowIcon(QIcon(icon_path))
    
    # Set values from config
    about_dialog.lblAppName.setText(config.get("app_name", "Application Name"))
    about_dialog.lblVersion.setText(f"Version {config.get('app_version', '1.0.0')}")
    about_dialog.lblDescription.setText(config.get("app_description", "Description not available"))
    about_dialog.lblAuthor.setText(f"Developed by {config.get('app_author', 'Unknown')}")
    about_dialog.lblEmail.setText(config.get("app_author_email", ""))
    about_dialog.lblCopyright.setText(config.get("app_copyright", ""))
    about_dialog.lblLicense.setText(f"Licensed under {config.get('app_license', 'Unknown')}")
    
    # Set commit info if available
    commit_hash = config.get("app_commit_hash", "")
    commit_date = config.get("app_commit_date", "")
    if commit_hash and commit_date:
        about_dialog.lblCommitInfo.setText(f"Build: {commit_hash[:7]} ({commit_date})")
    else:
        about_dialog.lblCommitInfo.setVisible(False)
    
    # Center the See License button
    about_dialog.verticalLayout.setAlignment(about_dialog.btnSeeLicense, QtCore.Qt.AlignHCenter)
    
    # Connect the See License button to show the license dialog
    about_dialog.btnSeeLicense.clicked.connect(lambda: show_license_dialog(parent, config, base_dir))
    
    # If we have email info, make it clickable
    email = config.get("app_author_email", "")
    if email:
        about_dialog.lblEmail.setText(f'<a href="mailto:{email}">{email}</a>')
        about_dialog.lblEmail.setOpenExternalLinks(True)
    
    # Center the dialog on the screen using the helper function
    center_window(about_dialog)
    
    # Show the dialog as modal
    about_dialog.exec()
