import sys  # Import sys to fix the NameError
from datetime import datetime
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication, QMenu, QFileDialog
from PySide6.QtGui import QTextCursor, QKeySequence, QShortcut  # Corrected: QShortcut is in QtGui, not QtWidgets
from PySide6 import QtUiTools, QtCore
import qtawesome as qta  # Import qtawesome for icons
from threading import Lock
import os
import platform  # Import platform to get the operating system

# Global output logs instance that can be accessed from anywhere
_global_output_logs = None

class OutputLogsWidget:
    def __init__(self, base_dir=None):
        """Initialize the output logs widget.
        
        Args:
            base_dir: The base directory of the application
        """
        self.BASE_DIR = base_dir
        self.widget = None
        self.log_text = None
        
        # Set this instance as the global one for easy access
        global _global_output_logs
        _global_output_logs = self

    def _load_app_details(self):
        """Load application details from config.json."""
        import json
        config_path = f"{self.BASE_DIR}/config.json"
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            app_name = config.get('app_name', 'Image Tea Mini')
            app_version = config.get('app_version', '1.0.0')
            app_copyright = config.get('app_copyright', '2025 Desainia Stduio')
            app_commit_hash = config.get('app_commit_hash', '')
            short_hash = app_commit_hash[:7] if app_commit_hash else ''
        except Exception as e:
            app_name = "Image Tea Mini"
            app_version = "1.0.0"
            app_copyright = "2025 Desainia Stduio"  # Fixed: changed variable name to app_copyright
            short_hash = ""
            
        return app_name, app_version, app_copyright, short_hash  # Fixed: return app_copyright instead of copyright
        
    def _add_welcome_header(self):
        """Add the welcome header to the log text."""
        # Get application details
        app_name, app_version, app_copyright, short_hash = self._load_app_details()  # Fixed: variable name to app_copyright
        
        # Create welcome messages with consistent formatting
        header_line = "=" * 70
        welcome_msg1 = f"{header_line}"
        welcome_msg2 = f"{app_name} v{app_version} - {short_hash} - © {app_copyright}"  # Fixed: use app_copyright
        welcome_msg3 = f"{header_line}"
        welcome_msg4 = f"MIT License - Do whatever you want. Zero liability."
        welcome_msg5 = f"Copy, modify, sell it - I don't care. Just keep the license."
        welcome_msg6 = f"Use entirely at your own risk."
        welcome_msg7 = f"{header_line}"
        
        # Apply consistent formatting with HTML color - header in green
        self.log_text.append(f"<span style='color:#88cc88;'>{welcome_msg1}</span>")
        self.log_text.append(f"<span style='color:#88cc88; font-size:14px'>{welcome_msg2}</span>")
        self.log_text.append(f"<span style='color:#88cc88;'>{welcome_msg3}</span>")
        
        # License info in blue, with each line separate for cleaner appearance
        self.log_text.append(f"<span style='color:#036ffc;'>{welcome_msg4}</span>")
        self.log_text.append(f"<span style='color:#036ffc;'>{welcome_msg5}</span>")
        self.log_text.append(f"<span style='color:#036ffc;'>{welcome_msg6}</span>")
        self.log_text.append(f"<span style='color:#036ffc;'>{welcome_msg7}</span>")

    def load_ui(self):
        """Load the dock widget from UI file and set up the text area."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/logs/output_logs.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Access the dock widget content
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        
        # Create a vertical layout if not already present
        if content_widget.layout() is None:
            layout = QVBoxLayout(content_widget)
        else:
            layout = content_widget.layout()
            
        # Remove all margins to make the text area fill the entire dock
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Clear the layout (remove any existing widgets)
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create the text edit for logs
        self.log_text = QTextEdit(content_widget)
        self.log_text.setReadOnly(True)
        # Change from NoWrap to WidgetWidth to enable word wrapping
        self.log_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Use native scrollbar when needed
        
        # Set monospace font and dark theme style with modern scrollbars
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(129, 154, 165, 0.06);
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: none;
            }
            
            /* Subtle scrollbar styling with lower opacity */
            QScrollBar:vertical {
                border: none;
                background-color: rgba(0, 0, 0, 5);  /* Very subtle background */
                width: 8px;  /* Slightly narrower */
                margin: 0px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(128, 128, 128, 60);  /* Lower opacity */
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: rgba(128, 128, 128, 120);  /* More visible on hover but still subtle */
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: rgba(0, 0, 0, 5);  /* Very subtle background */
                height: 8px;  /* Slightly narrower */
                margin: 0px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: rgba(128, 128, 128, 60);  /* Lower opacity */
                min-width: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(128, 128, 128, 120);  /* More visible on hover but still subtle */
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # Add initial welcome content using the same format as append_log
        os_name = platform.system()[:3]  # Shorten OS name (e.g., "Win", "Mac", "Lin")
        date = datetime.now().strftime("%b/%d/%Y")  # Format: "May/18/2025"
        time = datetime.now().strftime("%H:%M:%S")  # Format: "10:55:20"
        
        # Add welcome header
        self._add_welcome_header()
        
        # Add the text edit to the layout
        layout.addWidget(self.log_text)
        
        # Add context menu for the log text area
        self.log_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log_text.customContextMenuRequested.connect(self.show_context_menu)
        
        return self.widget
    
    def connect_to_main_menu(self, main_window):
        """Connect log text operations to main window edit menu.
        
        Args:
            main_window: The main application window with menu bar
        """
        try:
            # Connect copy action from main menu
            if hasattr(main_window, 'actionCopy'):
                main_window.actionCopy.triggered.connect(self.handle_copy_action)
                
            # Connect select all action from main menu
            if hasattr(main_window, 'actionSelect_All'):
                main_window.actionSelect_All.triggered.connect(self.handle_select_all_action)
                
            # Connect clear action from main menu
            if hasattr(main_window, 'actionClear'):
                main_window.actionClear.triggered.connect(self.handle_clear_action)
                
            # Connect save logs action from main menu
            if hasattr(main_window, 'actionSave_Logs'):
                main_window.actionSave_Logs.triggered.connect(self.handle_save_logs_action)
        except Exception as e:
            print(f"Error connecting log widget to main menu: {e}")
    
    def handle_copy_action(self):
        """Handle copy action from main menu."""
        # Only process if log text has focus
        if self.log_text and self.log_text.hasFocus():
            try:
                # Instead of using copy() directly, get selected text and use the clipboard
                selected_text = self.log_text.textCursor().selectedText()
                if selected_text:
                    clipboard = QApplication.clipboard()
                    # Set plain text to clipboard to avoid HTML formatting issues
                    clipboard.setText(selected_text)
                    
                    # Create a more informative log message with a preview of the copied text
                    preview = selected_text[:30] + "..." if len(selected_text) > 30 else selected_text
                    self.append_log("Clipboard", f"Copied text: \"{preview}\"", "DEBUG")
            except Exception as e:
                # Log the clipboard error but don't show it to users
                print(f"Clipboard error: {e}")
    
    def handle_select_all_action(self):
        """Handle select all action from main menu."""
        # Only process if log text has focus
        if self.log_text and self.log_text.hasFocus():
            self.log_text.selectAll()
    
    def handle_clear_action(self):
        """Handle clear action from main menu."""
        # Only process if log text has focus
        if self.log_text and self.log_text.hasFocus():
            self.clear_logs()
    
    def handle_save_logs_action(self):
        """Handle save logs action from main menu."""
        # Only process if log text has focus or explicitly called
        if self.log_text and (self.log_text.hasFocus() or not QApplication.focusWidget()):
            self.save_logs()
    
    def append_log(self, operation, details, level="INFO"):
        """Add a new log message to the output with the specified concise format.
        
        Args:
            operation: The operation being logged (e.g., "Load", "Save", "Error").
            details: Additional details about the operation.
            level: Log level (INFO, WARNING, ERROR, DEBUG).
        """
        if self.log_text:
            # Get the current date, time, and operating system
            os_name = platform.system()[:3]  # Shorten OS name (e.g., "Win", "Mac", "Lin")
            date = datetime.now().strftime("%b/%d/%Y")  # Format: "May/18/2025"
            time = datetime.now().strftime("%H:%M:%S")  # Format: "10:55:20"
            
            # Format the log message - Make sure level is consistent
            log_message = f"[{os_name}] [{level}] {date} {time} - {operation} - {details}"
            
            # Apply color formatting based on log level
            if level == "ERROR":
                formatted = f"<span style='color:#ff5050;'>{log_message}</span>"
            elif level == "WARNING":
                formatted = f"<span style='color:#ffcc00;'>{log_message}</span>"
            elif level == "DEBUG":
                formatted = f"<span style='color:#88cc88;'>{log_message}</span>"
            else:  # INFO
                formatted = f"<span style='color:#919191;'>{log_message}</span>"  # Default color for INFO
            
            # Append the formatted log message
            self.log_text.append(formatted)
            
            # Auto-scroll to the bottom
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_text.setTextCursor(cursor)
            
            # Process events to ensure UI updates
            QApplication.processEvents()
    
    def clear_logs(self):
        """Clear all log content."""
        if self.log_text:
            self.log_text.clear()
            
            # Add welcome header
            self._add_welcome_header()
            
            # Add a log cleared message
            os_name = platform.system()[:3]
            date = datetime.now().strftime("%b/%d/%Y")
            time = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"<span style='color:#f0f0f0;'>[{os_name}] [INFO] {date} {time} - System - Logs cleared</span>")
    
    def save_logs(self):
        """Save the logs to a file."""
        if self.log_text:
            # Get the current logs
            logs = self.log_text.toPlainText()
            
            # Generate a default filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"Image_Tea_Mini_Logs_{timestamp}.log"
            
            # Open a file dialog to save the file
            options = QFileDialog.Options()
            if sys.platform == "darwin":  # macOS
                options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save Logs",
                default_filename,
                "Log Files (*.log);;All Files (*)",
                options=options
            )
            
            # Save the file if a path was selected
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(logs)
                    self.append_log("Save", f"Logs saved to {file_path}", "INFO")
                except Exception as e:
                    self.append_log("Save", f"Failed to save logs: {e}", "ERROR")
    
    def show_context_menu(self, position):
        """Show a custom context menu for the log text area."""
        menu = QMenu()
        
        # Add "Copy" action with icon 
        copy_action = menu.addAction(qta.icon('fa6s.copy'), "Copy")
        # Connect to our custom copy handler that uses plain text
        copy_action.triggered.connect(lambda: self.handle_plain_text_copy())
        
        # Add "Select All" action with icon and shortcut hint - use the same handler as the main menu
        select_all_action = menu.addAction(qta.icon('fa6s.check-double'), "Select All")
        select_all_action.triggered.connect(self.handle_select_all_action)
        
        # Add "Clear" action with icon and shortcut hint but WITHOUT setting the shortcut to avoid conflict
        clear_action = menu.addAction(qta.icon('fa6s.broom'), "Clear Logs")
        clear_action.triggered.connect(self.handle_clear_action)
        
        # Add "Save" action with icon and shortcut hint but WITHOUT setting the shortcut to avoid conflict
        save_action = menu.addAction(qta.icon('fa6s.floppy-disk'), "Save Logs")
        save_action.triggered.connect(self.handle_save_logs_action)
        
        # Show the menu at the requested position
        menu.exec(self.log_text.mapToGlobal(position))
    
    def handle_plain_text_copy(self):
        """Handle copy action ensuring plain text is used."""
        if self.log_text:
            # Get the cursor and selected text
            cursor = self.log_text.textCursor()
            text = cursor.selectedText()
            
            # Only proceed if text is selected
            if text:
                # Use the clipboard directly with plain text
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                
                # Create a more informative log message with a preview of the copied text
                preview = text[:30] + "..." if len(text) > 30 else text
                self.append_log("Clipboard", f"Copied text: \"{preview}\"", "DEBUG")
