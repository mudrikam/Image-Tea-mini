# filepath: z:\Build\Image-Tea-mini\core\widgets\actions_widget.py
from PySide6 import QtWidgets, QtUiTools, QtCore
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

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

class ActionsWidget:
    def __init__(self, base_dir):
        """Initialize the Actions widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.config = {}  # Store config when it's passed to us
        self.main_window = None  # Store reference to main window
        
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
            generate_button = self.widget.findChild(QtWidgets.QPushButton, "generateButton")
            if generate_button:
                # Create a play icon from Font Awesome 6
                play_icon = qta.icon('fa5s.play', color='white')
                generate_button.setIcon(play_icon)
                generate_button.setText("Generate")  # Keep the "Generate" text
                generate_button.setToolTip("Run")  # Add tooltip
                
                # Optional: Style the button to look more like a play button
                generate_button.setStyleSheet("""
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
                """)
                
                # Make the icon bigger
                generate_button.setIconSize(QtCore.QSize(16, 16))
            
            # Configure the stop button
            stop_button = self.widget.findChild(QtWidgets.QPushButton, "stopButton")
            if stop_button:
                # Create a stop icon from Font Awesome
                stop_icon = qta.icon('fa5s.stop', color="#ff4460")
                stop_button.setIcon(stop_icon)
                stop_button.setText("")  # Remove text
                stop_button.setToolTip("Stop")  # Add tooltip
                
                # Style the stop button using the requested red color
                stop_button.setStyleSheet("""
                    QPushButton {
                        background-color: #993244;
                        border-radius: 12px;
                        padding: 5px;
                        color: #eb314d;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #8a2d3d;
                    }
                    QPushButton:pressed {
                        background-color: #7a2836;
                    }
                    QPushButton:disabled {
                        background-color: rgba(115, 119, 123, 0.18);
                        color: rgba(115, 119, 123, 0.48);
                    }
                """)
                
                # Make the icon bigger and consistent with generate button
                stop_button.setIconSize(QtCore.QSize(16, 16))
                
                # Initially disable the stop button
                stop_button.setEnabled(False)
                
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
                        font-weight: bold;
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
                        font-weight: bold;
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
    
    # Remove the _on_donate_button_clicked method since it's no longer used
    # We're using _show_donation_dialog directly like status_bar_actions.py does
