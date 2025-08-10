import os
from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from core.utils.logger import log, debug, warning, error, exception

# Import QtAwesome for icons
try:
    import qtawesome as qta
except ImportError:
    print("QtAwesome not found. Please install it with 'pip install qtawesome'")
    qta = None

# Import the donation dialog function and URL handler from the same places used in status_bar_actions.py
try:
    from core.helper.dialogs._donation_dialog import show_donation_dialog
    from core.helper._url_handler import open_url
except ImportError:
    print("Donation dialog module or URL handler not found")
    show_donation_dialog = None
    open_url = None

# Import Gemini AI System
try:
    from core.utils.gemini_ai_system import GeminiAISystem
except ImportError:
    print("Gemini AI System not found")
    GeminiAISystem = None
try:
    from core.helper.dialogs._donation_dialog import show_donation_dialog
    from core.helper._url_handler import open_url
except ImportError:
    print("Donation dialog module or URL handler not found")
    show_donation_dialog = None
    open_url = None

class ActionsWidget:
    def __init__(self, base_dir):
        """Initialize the Actions widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.config = {}  # Store config when it's passed to us
        self.main_window = None  # Store reference to main window
        
        # Initialize Gemini AI System
        self.gemini_ai_system = None
        
        # UI References
        self.generate_button = None
        self.stop_button = None
        
        # Workspace controller reference (will be set by controller)
        self.workspace_controller = None
        
    def load_ui(self):
        """Load the UI from the .ui file and return the dock widget."""
        try:
            # Load the UI file
            ui_file = os.path.join(self.BASE_DIR, "gui", "widgets", "actions", "actions_widget.ui")
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(ui_file)
            ui_file.open(QtCore.QFile.ReadOnly)
            
            # Create the dock widget from the UI file
            dock_widget = loader.load(ui_file)
            ui_file.close()
            
            self.widget = dock_widget
            
            # Initialize any additional components or connections here
            self._setup_components()
            
            return dock_widget
        except Exception as e:
            print(f"Error loading Actions widget UI: {str(e)}")
            return None
    
    def _setup_components(self):
        """Set up components and connections for the Actions widget."""
        # Apply Font Awesome play icon to the generate button
        if self.widget and qta:
            # Debug information to check which buttons are available in the UI
            all_buttons = self.widget.findChildren(QtWidgets.QPushButton)
            button_names = [btn.objectName() for btn in all_buttons]
            # print(f"Available buttons: {button_names}")
            
            # Set pointing hand cursor for all buttons
            for button in all_buttons:
                button.setCursor(QCursor(Qt.PointingHandCursor))
            
            # Apply Font Awesome play icon to the generate button
            self.generate_button = self.widget.findChild(QtWidgets.QPushButton, "generateButton")
            if self.generate_button:
                # Create a play icon from Font Awesome 6
                play_icon = qta.icon('fa5s.play', color='white')
                self.generate_button.setIcon(play_icon)
                self.generate_button.setText("Generate")  # Keep the "Generate" text
                self.generate_button.setToolTip("Run")  # Add tooltip
                
                # Optional: Style the button to look more like a play button
                self.generate_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        border-radius: 12px;
                        padding: 5px;
                        padding-left: 8px;
                        padding-right: 10px;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                    }
                    QPushButton:disabled {
                        background-color: rgba(115, 119, 123, 0.18);
                        color: rgba(115, 119, 123, 0.48);
                    }
                """)
                
                # Make the icon bigger
                self.generate_button.setIconSize(QtCore.QSize(16, 16))
                
                # Connect to processing function
                self.generate_button.clicked.connect(self._on_generate_clicked)
            
            # Configure the stop button
            self.stop_button = self.widget.findChild(QtWidgets.QPushButton, "stopButton")
            if self.stop_button:
                # Create a stop icon from Font Awesome
                stop_icon = qta.icon('fa5s.stop', color="#ff4460")
                self.stop_button.setIcon(stop_icon)
                self.stop_button.setText("")  # Remove text
                self.stop_button.setToolTip("Stop")  # Add tooltip
                
                # Style the stop button using the requested red color
                self.stop_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(233, 29, 73, 0.32);
                        border-radius: 12px;
                        padding: 5px;
                        color: #eb314d;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(233, 29, 73, 0.65);
                    }
                    QPushButton:pressed {
                        background-color: rgba(233, 29, 73, 0.8);
                    }
                    QPushButton:disabled {
                        background-color: rgba(115, 119, 123, 0.18);
                        color: rgba(115, 119, 123, 0.48);
                    }
                """)
                
                # Make the icon bigger and consistent with generate button
                self.stop_button.setIconSize(QtCore.QSize(16, 16))
                
                # Initially disable the stop button
                self.stop_button.setEnabled(False)
                
                # Connect to stop function
                self.stop_button.clicked.connect(self._on_stop_clicked)
                
            # Check if donate button exists in UI
            donate_button = self.widget.findChild(QtWidgets.QPushButton, "donateButton")
            if donate_button:
                # Create a donate/heart icon from Font Awesome
                donate_icon = qta.icon('fa5s.heart', color='#ff1764')
                donate_button.setIcon(donate_icon)
                donate_button.setToolTip("Support this project")
                
                # Style the donate button with the specified pink color
                donate_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(115, 119, 123, 0.18);
                        border-radius: 12px;
                        padding: 5px;
                        padding-left: 8px;
                        padding-right: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgba(115, 119, 123, 0.1);
                    }
                    QPushButton:pressed {
                        background-color: #c0124c;
                    }
                """)
                
                # Make the icon size consistent with other buttons
                donate_button.setIconSize(QtCore.QSize(16, 16))
                
                # Connect click event to show donation dialog using the same approach as status_bar_actions.py
                if show_donation_dialog is not None:
                    # Use the simplified donation dialog call like status_bar_actions.py
                    donate_button.clicked.connect(self._show_donation_dialog)
                else:
                    print("Warning: Donation dialog function not available")
            else:
                print("Warning: donateButton not found in UI")
                
            # Check if WhatsApp button exists in UI
            whatsapp_button = self.widget.findChild(QtWidgets.QPushButton, "whatsappButton")
            if whatsapp_button:
                # Create a WhatsApp icon from Font Awesome
                whatsapp_icon = qta.icon('fa5b.whatsapp', color='#25D366')
                whatsapp_button.setIcon(whatsapp_icon)
                whatsapp_button.setToolTip("Join WhatsApp Group")
                
                # Style the WhatsApp button with WhatsApp green color
                whatsapp_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(115, 119, 123, 0.18);
                        border-radius: 12px;
                        padding: 5px;
                        padding-left: 8px;
                        padding-right: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgba(115, 119, 123, 0.1);
                    }
                    QPushButton:pressed {
                        background-color: #1eb455;
                    }
                """)
                
                # Make the icon size consistent with other buttons
                whatsapp_button.setIconSize(QtCore.QSize(16, 16))
                
                # Connect click event to open WhatsApp group link
                whatsapp_button.clicked.connect(self._open_whatsapp_group)
            else:
                print("Warning: whatsappButton not found in UI")
    
    def _open_whatsapp_group(self):
        """Open WhatsApp group invite link in default browser."""
        if not self.config:
            print("Warning: Config not available, cannot get WhatsApp URL")
            return
        
        # Get WhatsApp URL from config if available (same field name as in status_bar_actions.py)
        whatsapp_url = self.config.get("app_whatsapp", "")
        
        # If no URL in config, use a default URL
        if not whatsapp_url:
            whatsapp_url = "https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3"
            print("Warning: Using default WhatsApp URL since no URL found in config")
        
        # Use the open_url function from _url_handler.py, like status_bar_actions.py does
        if open_url:
            open_url(whatsapp_url)
        else:
            print("Warning: open_url function not available")
    
    def _show_donation_dialog(self):
        """Show the donation dialog directly, matching the status bar implementation."""
        if show_donation_dialog is None:
            print("Warning: Donation dialog function not available")
            return
            
        if self.main_window is None:
            print("Warning: Main window reference not available")
            return
            
        if not self.config:
            print("Warning: Config not available")
            return
            
        # Directly call the show_donation_dialog function with the same parameters used in status_bar_actions.py
        show_donation_dialog(self.main_window, self.config, self.BASE_DIR)
    
    def set_main_window_and_config(self, main_window, config):
        """Set both the main window and configuration for use in dialogs."""
        self.main_window = main_window
        self.config = config
        
        # Initialize Gemini AI System with config
        if GeminiAISystem and config:
            self.gemini_ai_system = GeminiAISystem(config)
            debug("Gemini AI System initialized")
    
    def set_workspace_controller(self, workspace_controller):
        """Set the workspace controller reference."""
        self.workspace_controller = workspace_controller
        debug("Workspace controller reference set")
        
        # Subscribe to database change events for table refresh
        try:
            from core.utils.event_system import EventSystem
            EventSystem.subscribe('project_data_changed', self._on_database_changed, weak=True)
            debug("Subscribed to project_data_changed events")
        except Exception as e:
            warning(f"Failed to subscribe to database events: {e}")
    
    def _on_database_changed(self):
        """Handle database change events to refresh table colors."""
        try:
            if self.gemini_ai_system and hasattr(self.gemini_ai_system, 'refresh_table_colors'):
                self.gemini_ai_system.refresh_table_colors()
                debug("Refreshed table colors due to database change")
        except Exception as e:
            warning(f"Error handling database change event: {e}")
    
    def _on_generate_clicked(self):
        """Handle generate button click."""
        debug("Generate button clicked")
        
        if not self.gemini_ai_system:
            warning("Gemini AI System not initialized")
            return
        
        if not self.workspace_controller:
            warning("Workspace controller not available")
            return
        
        # Get current tab data from workspace controller
        current_item_id = self._get_current_tab_item_id()
        debug(f"Current item_id from tab manager: {current_item_id}")
        
        if not current_item_id:
            warning("No active tab with data to process")
            return
        
        # Get files data for current tab
        files_data = self._get_current_tab_files_data(current_item_id)
        debug(f"Files data result: {len(files_data) if files_data else 'None'}")
        
        if not files_data:
            warning("No files data found for current tab")
            return
        
        # Get current table widget for highlighting
        current_table_widget = self._get_current_table_widget()
        debug(f"Current table widget: {current_table_widget}")
        
        # Setup AI system with UI components
        self.gemini_ai_system.set_ui_components(
            self.generate_button,
            self.stop_button, 
            current_table_widget
        )
        
        # Start processing
        self.gemini_ai_system.start_processing(current_item_id, files_data)
        log(f"Started Gemini AI processing for item_id: {current_item_id}")
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        debug("Stop button clicked")
        
        if self.gemini_ai_system:
            self.gemini_ai_system.stop_processing()
            log("Stopped Gemini AI processing")
    
    def _get_current_tab_item_id(self):
        """Get the item ID of the currently active tab."""
        try:
            if hasattr(self.workspace_controller, 'tab_manager'):
                return self.workspace_controller.tab_manager.get_current_item_id()
        except Exception as e:
            exception(e, "Error getting current tab item ID")
        return None
    
    def _get_current_tab_files_data(self, item_id):
        """Get files data for the current tab."""
        try:
            # Extract actual ID from item_id 
            # Format is: YYYY-MM-DD_ID_STATUS (like 2025-08-02_0007_draft)
            parts = item_id.split('_')
            debug(f"Item ID parts for files data: {parts}")
            
            if len(parts) >= 2:
                # For format YYYY-MM-DD_ID_STATUS, the actual ID is parts[1]
                actual_id = parts[1]
                debug(f"Using actual_id: {actual_id} for database lookup")
                
                # Use ProjectFilesModel directly like in table_manager and grid_manager
                from database.db_project_files import ProjectFilesModel
                files_data = ProjectFilesModel().get_files_by_item_id(actual_id)
                debug(f"Found {len(files_data) if files_data else 0} files for actual_id: {actual_id}")
                
                return files_data
            else:
                warning(f"Invalid item_id format: {item_id}")
        except Exception as e:
            exception(e, "Error getting files data for current tab")
        return None
    
    def _get_current_table_widget(self):
        """Get the table widget of the currently active tab."""
        try:
            if hasattr(self.workspace_controller, 'tab_manager'):
                current_item_id = self.workspace_controller.tab_manager.get_current_item_id()
                if current_item_id and current_item_id in self.workspace_controller.tab_manager.table_widgets:
                    return self.workspace_controller.tab_manager.table_widgets[current_item_id]
        except Exception as e:
            exception(e, "Error getting current table widget")
        return None
    
    # Remove the _on_donate_button_clicked method since it's no longer used
    # We're using _show_donation_dialog directly like status_bar_actions.py does
