"""
Helper module for managing status bar actions.

This module adds buttons to the status bar for quick access to
important features and information, like donate, WhatsApp, about,
license, current version, commit hash, and GitHub repository link.
"""

from PySide6.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
import qtawesome as qta
from core.helper._url_handler import open_url
from core.helper._about_dialog import show_about_dialog
from core.helper._license_dialog import show_license_dialog
from core.helper._donation_dialog import populate_donation_dialog
from PySide6 import QtUiTools, QtCore

def setup_status_bar(window, config, base_dir):
    """
    Set up status bar with buttons and information.
    
    Args:
        window: The main window object
        config: The application configuration
        base_dir: The base directory path
    """
    # Create a widget to hold all status bar items
    status_widget = QWidget()
    layout = QHBoxLayout(status_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)  # Space between items
    
    # Add version info label
    app_version = config.get("app_version", "1.0.0")
    version_label = QLabel(f"v{app_version}")
    version_label.setToolTip("Current version")
    layout.addWidget(version_label)
    
    # Add commit hash label if available
    commit_hash = config.get("app_commit_hash", "")
    repo_url = config.get("app_repository", "")
    if commit_hash and repo_url:
        # Display only first 7 characters of the hash
        short_hash = commit_hash[:7] if len(commit_hash) > 7 else commit_hash
        commit_icon = qta.icon('fa6s.code-commit')
        commit_btn = QPushButton(commit_icon, f" {short_hash}")
        commit_btn.setFlat(True)
        commit_btn.setToolTip(f"View commit: {commit_hash}")
        commit_btn.setCursor(Qt.PointingHandCursor)
        # Create a URL to the specific commit by appending /commit/{hash} to the repo URL
        commit_url = f"{repo_url}/commit/{commit_hash}"
        commit_btn.clicked.connect(lambda: open_url(commit_url))
        layout.addWidget(commit_btn)
    
    # Add GitHub repository button
    if repo_url:
        github_btn = create_button(qta.icon('fa6b.github'), "GitHub Repository")
        github_btn.clicked.connect(lambda: open_url(repo_url))
        layout.addWidget(github_btn)
    
    # Add WhatsApp button
    whatsapp_url = config.get("app_whatsapp", "")
    if whatsapp_url:
        whatsapp_btn = create_button(qta.icon('fa6b.whatsapp', color='green'), "WhatsApp Group")
        whatsapp_btn.clicked.connect(lambda: open_url(whatsapp_url))
        layout.addWidget(whatsapp_btn)
    
    # Add About button
    about_btn = create_button(qta.icon('fa6s.circle-info'), "About")
    about_btn.clicked.connect(lambda: show_about_dialog(window, config, base_dir))
    layout.addWidget(about_btn)
    
    # Add License button
    license_btn = create_button(qta.icon('fa6s.scale-balanced'), "License")
    license_btn.clicked.connect(lambda: show_license_dialog(window, config, base_dir))
    layout.addWidget(license_btn)
    
    # Add Donate button
    donate_btn = create_button(qta.icon('fa6s.heart', color='#ff1764'), "Donate")
    donate_btn.clicked.connect(lambda: show_donation_dialog_wrapper(window, config, base_dir))
    layout.addWidget(donate_btn)
    
    # Add the widget to the status bar
    window.statusbar.setSizeGripEnabled(False)  # Disable the size grip if present
    # Don't modify the existing stylesheet - just add the permanent widget
    window.statusbar.addPermanentWidget(status_widget)  # Use addPermanentWidget for right alignment

def create_button(icon, tooltip):
    """
    Create a flat button for the status bar with an icon.
    
    Args:
        icon: The QtAwesome icon to use
        tooltip: The tooltip text for the button
        
    Returns:
        QPushButton: The created button
    """
    button = QPushButton(icon, "")
    button.setFlat(True)  # Make it look like just an icon
    button.setToolTip(tooltip)
    button.setCursor(Qt.PointingHandCursor)  # Change cursor on hover
    button.setMaximumSize(24, 24)  # Keep buttons a consistent size
    return button

def show_donation_dialog_wrapper(window, config, base_dir):
    """
    Show the donation dialog.
    
    This is a wrapper around the donation dialog to handle the UI loading.
    
    Args:
        window: The main window object
        config: The application configuration
        base_dir: The base directory path
    """
    # Load the donation UI file
    ui_path = QtCore.QFile(f"{base_dir}/gui/dialogs/donation_window.ui")
    ui_path.open(QtCore.QFile.ReadOnly)
    
    loader = QtUiTools.QUiLoader()
    donation_dialog = loader.load(ui_path, window)
    ui_path.close()
    
    # Populate the dialog with content
    populate_donation_dialog(donation_dialog, config, base_dir)
    
    # Connect the Close button
    if hasattr(donation_dialog, 'closeButton'):
        donation_dialog.closeButton.clicked.connect(donation_dialog.close)
    
    # Show the dialog
    donation_dialog.exec()