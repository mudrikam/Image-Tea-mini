from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6 import QtUiTools, QtCore

class OutputLogsWidget:
    def __init__(self, base_dir=None):
        """Initialize the output logs widget.
        
        Args:
            base_dir: The base directory of the application
        """
        self.BASE_DIR = base_dir
        self.widget = None
        self.log_text = None
    
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
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        
        # Set monospace font and dark theme style
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: none;
            }
        """)
        
        # Add some initial welcome content
        self.log_text.append("=== Image Tea Mini - Output Logs ===")
        self.log_text.append("Application started successfully.")
        self.log_text.append("Ready for commands...")
        
        # Add the text edit to the layout
        layout.addWidget(self.log_text)
        
        return self.widget
    
    def append_log(self, message):
        """Add a new log message to the output.
        
        Args:
            message: The message text to append to the logs
        """
        if self.log_text:
            self.log_text.append(message)
            
            # Auto-scroll to the bottom
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.End)
            self.log_text.setTextCursor(cursor)
