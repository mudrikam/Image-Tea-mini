import sys
import os
import json
from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtGui import QIcon

# Import our helpers
from core.helper._main_menu_icons import apply_icons
from core.helper._about_dialog import show_about_dialog
from core.helper._license_dialog import show_license_dialog
from core.helper._contributors_dialog import show_contributors_dialog
from core.helper._updater_dialog import show_updater_dialog
from core.helper._url_handler import open_url
from core.helper._donation_dialog import populate_donation_dialog
from core.helper._status_bar_actions import setup_status_bar

class MainController:
    def __init__(self, base_dir=None):
        """Set up the main program controller."""
        # Create the Qt application instance - required before any UI elements
        # This is the core object that manages all Qt resources and event loop
        self.app = QApplication(sys.argv)
        self.window = None
        
        # Store the base directory path passed from main.py
        # If not provided, calculate it (for backward compatibility)
        self.BASE_DIR = base_dir
        if self.BASE_DIR is None:
            self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load our settings first so they're available throughout the app
        # This gives us flexibility to configure the app without recompiling
        self.config = self.load_config()
        
        # Add the program icon to the taskbar/dock
        self.set_application_icon()
    
    def load_config(self):
        """Get the program settings from config.json."""
        # Use the centralized BASE_DIR to find the config file
        config_path = os.path.join(self.BASE_DIR, "config.json")
        
        try:
            # Open and parse the JSON file in one go
            # This gives us all our settings in a Python dictionary
            with open(config_path, 'r') as config_file:
                return json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Be helpful when the config is missing or corrupted
            # This helps with debugging when something goes wrong
            print(f"Error loading config: {e}")
            # Return sensible defaults so the app doesn't crash
            # These values will be used if the config file is missing
            return {
                "app_name": "Image Tea Mini",
                "app_version": "1.0.0",
                "app_icon": "res/image_tea.ico"
            }
    
    def set_application_icon(self):
        """Add the program icon from settings."""
        # Skip if we couldn't load the config for some reason
        if not self.config:
            return
            
        # Use the centralized BASE_DIR to locate the icon
        icon_path = os.path.join(self.BASE_DIR, "res", self.config.get("app_icon", "image_tea.ico"))
        
        # Only set the icon if the file actually exists
        # This prevents crashes if the icon file is missing
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.app.setWindowIcon(app_icon)
    
    def load_ui(self):
        """Load the main window interface."""
        # Use the centralized BASE_DIR to get the UI file
        ui_path = os.path.join(self.BASE_DIR, "gui", "layout", "main_window.ui")
        
        # PySide6 needs to use a loader and file objects to read UI files
        # This loads the XML UI file created with Qt Designer
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()
        
        # Set window title from settings to show application name and version
        # This is nicer than hardcoding it in the UI file
        if self.config:
            app_name = self.config.get("app_name", "Image Tea Mini")
            app_version = self.config.get("app_version", "1.0.0")
            self.window.setWindowTitle(f"{app_name} {app_version}")
        
        # Add the program icon to the window itself
        # Use the centralized BASE_DIR
        icon_path = os.path.join(self.BASE_DIR, "res", self.config.get("app_icon", "image_tea.ico"))
        
        if os.path.exists(icon_path):
            window_icon = QIcon(icon_path)
            self.window.setWindowIcon(window_icon)
          # Apply QtAwesome icons to menu actions using our helper
        apply_icons(self.window)
        
        # Set up status bar with buttons and information
        setup_status_bar(self.window, self.config, self.BASE_DIR)
        
        # Connect menu actions to handlers
        self.connect_menu_actions()
            
        return self
    def connect_menu_actions(self):
        """Connect menu actions to their respective handlers."""
        # Connect the About action
        self.window.actionAbout_2.triggered.connect(self.show_about_dialog)
        
        # Connect the License action
        self.window.actionLicense.triggered.connect(self.show_license_dialog)
        
        # Connect the Contributors action
        self.window.actionContributors.triggered.connect(self.show_contributors_dialog)
        
        # Connect the WhatsApp Group action
        self.window.actionWhatsApp_Group.triggered.connect(self.open_whatsapp_group)
        
        # Connect the GitHub Repository action
        self.window.actionGithub_Repository.triggered.connect(self.open_github_repository)
        
        # Connect the Report Issue action
        self.window.actionReport_Issue.triggered.connect(self.open_report_issue)
        
        # Connect the Check for Updates action
        self.window.actionCheck_for_Updates.triggered.connect(self.show_updater_dialog)
        
        # Connect the Donate action
        self.window.actionDonate.triggered.connect(self.show_donation_dialog)
        
        # Connect the Preferences action
        self.window.actionPreferences.triggered.connect(self.show_global_preferences_dialog)
        
        # Connect the Quit action
        self.window.actionQuit.triggered.connect(self.app.quit)
    
    def show_about_dialog(self):
        """Show the About dialog with application information."""
        show_about_dialog(self.window, self.config, self.BASE_DIR)
    
    def show_license_dialog(self):
        """Show the License dialog with license text."""
        show_license_dialog(self.window, self.config, self.BASE_DIR)
    
    def show_contributors_dialog(self):
        """Show the Contributors dialog with contributors information."""
        show_contributors_dialog(self.window, self.config, self.BASE_DIR)
    
    def show_updater_dialog(self):
        """Show the updater dialog to check for updates."""
        show_updater_dialog(self.window, self.config, self.BASE_DIR)
    
    def open_whatsapp_group(self):
        """Open the WhatsApp group link in the default browser."""
        whatsapp_url = self.config.get("app_whatsapp", "")
        if whatsapp_url:
            open_url(whatsapp_url)
    
    def open_github_repository(self):
        """Open the GitHub repository in the default browser."""
        repo_url = self.config.get("app_repository", "")
        if repo_url:
            open_url(repo_url)
    
    def open_report_issue(self):
        """Open the issue reporting page in the default browser."""
        issue_url = self.config.get("app_report_issue", "")
        if issue_url:
            open_url(issue_url)
    
    def show_global_preferences_dialog(self):
        """Show the global preferences dialog."""
        # Import here to avoid circular imports
        from core.helper._global_preferences import show_global_preferences
        
        # Show the global preferences dialog
        show_global_preferences(self.window, self.config, self.BASE_DIR)
    
    def show_donation_dialog(self):
        """Show the donation dialog."""
        # Use the centralized BASE_DIR to get the UI file
        ui_path = os.path.join(self.BASE_DIR, "gui", "dialogs", "donation_window.ui")
        
        # Load the donation UI file
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        
        # Create the donation dialog
        donation_dialog = loader.load(ui_file, self.window)
        ui_file.close()
        
        # Populate the dialog with content from config
        populate_donation_dialog(donation_dialog, self.config, self.BASE_DIR)
        
        # Connect the Close button to close the dialog
        if hasattr(donation_dialog, 'closeButton'):
            donation_dialog.closeButton.clicked.connect(donation_dialog.close)
        
        # Show the dialog as modal
        donation_dialog.exec()
    
    def show_window(self):
        """Open the main window and start the program."""
        # Make sure we have a window before showing it
        # This lazy-loading approach means we only create the window when needed
        if self.window is None:
            self.load_ui()
        
        # Make the window visible to the user
        self.window.show()
        # Start the Qt event loop - this is where the app runs until closed
        # The event loop processes user interactions like clicks and key presses
        return self.app.exec()
        
    def initialize(self):
        """Prepare the program to run."""
        # Load the UI in advance so it's ready when we call show_window
        # This is called from main.py before running the app
        self.load_ui()
        return self
        
    def run(self):
        """Start the program."""
        # This is the main entry point from main.py
        # It shows the window and starts the event loop
        return self.show_window()
        
    def shutdown(self):
        """Clean up before closing."""
        # This is where we would save application state, close files, etc.
        # Currently it's empty but can be expanded as the app grows
        pass

def run_application():
    """Start the main program."""
    # Create the main controller that manages the application
    controller = MainController()
    # Set everything up
    controller.initialize()
    # Run the app and exit with its return code when done
    # This ensures proper exit codes for the operating system
    sys.exit(controller.run())

if __name__ == "__main__":
    # This lets the file be run directly or imported
    # If run directly, start the application
    run_application()
