import sys
import os
import json
from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtGui import QIcon

# Import our helpers
from core.helper._main_menu_icons import apply_icons
from core.helper._main_menu_actions import MenuActionHandler
from core.helper._status_bar_actions import setup_status_bar
from core.helper._window_utils import center_window
from core.layout_controller import LayoutController
from core.utils.logger import log, debug, warning, error, exception
from database import db_config  # Import the database module

class MainController:
    """
    Main controller class for the application.
    
    This class:
    1. Manages the main window and UI components
    2. Handles application lifecycle (init, run, shutdown)
    3. Coordinates between different parts of the application
    """
    
    def __init__(self, base_dir=None):
        """
        Initialize the main controller.
        
        Args:
            base_dir (str): Base directory of the application
        """
        # Store the base directory
        self.base_dir = base_dir
        
        # Get existing QApplication instance instead of creating a new one
        self.app = QApplication.instance()
        
        # Force the menu to stay with the window on macOS
        if sys.platform == 'darwin' and self.app:
            self.app.setAttribute(QtCore.Qt.AA_DontUseNativeMenuBar, True)
            
        self.window = None
        self.layout_controller = None
        self.menu_handler = None
        
        # Store the base directory path
        self.BASE_DIR = base_dir
        if self.BASE_DIR is None:
            self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize database
        self.init_database()
        
        # Load program settings
        self.config = self.load_config()
        
        # Configure the app icon
        self.set_application_icon()
    
    def init_database(self):
        """Initialize the database connection and create necessary tables."""
        try:
            # Initialize database with BASE_DIR
            db_path = db_config.initialize(self.BASE_DIR)
            
            # Create database if needed and set up tables
            db_config.main(self.BASE_DIR)
            
            log(f"Database initialized at {db_path}")
        except Exception as e:
            exception(e, "Failed to initialize database")
    
    def load_config(self):
        """Get the program settings from config.json."""
        config_path = os.path.join(self.BASE_DIR, "config.json")
        
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                debug(f"{config.get('app_name')} {config.get('app_version')}")
                return config
        except FileNotFoundError:
            error(f"Configuration file missing: {config_path}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            error(f"Invalid configuration file: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Provide default configuration values if config file is missing."""
        warning("Using default configuration settings")
        return {
            "app_name": "Image Tea Mini",
            "app_version": "1.0.0",
            "app_icon": "res/image_tea.ico"
        }
    
    def set_application_icon(self):
        """Add the program icon from settings."""
        if not self.config:
            return
            
        icon_path = os.path.join(self.BASE_DIR, "res", self.config.get("app_icon", "image_tea.ico"))
        
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.app.setWindowIcon(app_icon)
        else:
            warning(f"Application icon not found at {icon_path}")
    
    def load_ui(self):
        """Load the main window interface."""
        ui_path = os.path.join(self.BASE_DIR, "gui", "layout", "main_window.ui")
        
        try:
            # Load the UI file
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(ui_path)
            
            if not ui_file.exists():
                error(f"UI file not found: {ui_path}")
                return self
                
            ui_file.open(QtCore.QFile.ReadOnly)
            self.window = loader.load(ui_file)
            ui_file.close()
            
            # Set window title from settings
            if self.config:
                app_name = self.config.get("app_name", "Image Tea Mini")
                app_version = self.config.get("app_version", "1.0.0")
                self.window.setWindowTitle(f"{app_name} {app_version}")
            
            # Add the program icon
            icon_path = os.path.join(self.BASE_DIR, "res", self.config.get("app_icon", "image_tea.ico"))
            if os.path.exists(icon_path):
                window_icon = QIcon(icon_path)
                self.window.setWindowIcon(window_icon)
            
            # Apply icons to menus
            apply_icons(self.window)
            
            # Set up status bar with buttons and information
            setup_status_bar(self.window, self.config, self.BASE_DIR)
            
            # Initialize the layout controller
            self.layout_controller = LayoutController(self.window, self.BASE_DIR)
            self.layout_controller.setup_ui()
            
            # Initialize and connect menu actions
            self.menu_handler = MenuActionHandler(
                self.window, 
                self.config, 
                self.BASE_DIR,
                self.layout_controller
            )
            self.menu_handler.connect_all_actions()
            
            # Connect signals to save layout when dock widgets are moved/resized
            self.setup_layout_save_signals()
            
        except Exception as e:
            exception(e, "Failed to start application")
            
        return self
    
    def setup_layout_save_signals(self):
        """Connect signals to save layout when it changes."""
        # Connect dock widget signals
        for dock_widget in self.window.findChildren(QtWidgets.QDockWidget):
            dock_widget.dockLocationChanged.connect(self.save_layout_delayed)
            dock_widget.visibilityChanged.connect(self.save_layout_delayed)
        
        # Save layout when the window is resized or moved
        self.window.resizeEvent = self.wrap_event(self.window.resizeEvent, self.save_layout_delayed)
        self.window.moveEvent = self.wrap_event(self.window.moveEvent, self.save_layout_delayed)
    
    def wrap_event(self, original_event, additional_handler):
        """Wrap an existing event handler to add functionality."""
        def wrapped_event(event):
            if original_event:
                original_event(event)
            additional_handler()
        return wrapped_event
    
    def save_layout_delayed(self):
        """Save layout after a short delay to avoid excessive writes."""
        if hasattr(self, '_layout_save_timer'):
            self._layout_save_timer.stop()
        else:
            self._layout_save_timer = QtCore.QTimer()
            self._layout_save_timer.setSingleShot(True)
            self._layout_save_timer.timeout.connect(self.save_current_layout)
        
        self._layout_save_timer.start(1000)
    
    def save_current_layout(self):
        """Save the current layout immediately."""
        if self.layout_controller:
            self.layout_controller.save_layout()
            
    def show_window(self):
        """Open the main window and start the program."""
        try:
            if self.window is None:
                self.load_ui()
                
            if self.window is None:
                error("Failed to create application window")
                return 1
            
            # Center the window on the screen before showing
            center_window(self.window)
            
            # Show the window
            self.window.show()
            
            # Start the Qt event loop
            return self.app.exec()
            
        except Exception as e:
            exception(e, "Fatal application error")
            return 1
        
    def initialize(self):
        """Prepare the program to run."""
        log(f"Starting {self.config.get('app_name', 'Image Tea Mini')}...")
        self.load_ui()
        return self
        
    def run(self):
        """Start the program."""
        return self.show_window()
    
    def shutdown(self):
        """Clean up before closing."""
        if self.layout_controller:
            self.layout_controller.save_layout()

def run_application():
    """Start the main program."""
    try:
        # Create the main controller
        controller = MainController()
        
        # Set everything up
        controller.initialize()
        
        # Run the app and exit with its return code
        exit_code = controller.run()
        sys.exit(exit_code)
        
    except Exception as e:
        error(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_application()
