from PySide6 import QtWidgets, QtCore, QtUiTools
from core.utils.logger import log, debug, warning, error, exception

class UILoader:
    """Helper class for loading and managing UI components."""
    
    def __init__(self, base_dir):
        """Initialize the UI loader."""
        self.BASE_DIR = base_dir
    
    def load_workspace_ui(self, ui_filename="main_workspace.ui"):
        """Load a workspace UI file."""
        try:
            ui_path = f"{self.BASE_DIR}/gui/layout/{ui_filename}"
            
            # debug(f"Loading workspace UI: {ui_path}")
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(ui_path)
            
            if not ui_file.exists():
                error(f"UI file not found: {ui_path}")
                return None, f"No workspace template found ({ui_filename})"
            
            ui_file.open(QtCore.QFile.ReadOnly)
            workspace_widget = loader.load(ui_file)
            ui_file.close()
            
            return workspace_widget, None
        except Exception as e:
            exception(e, f"Error loading UI file {ui_filename}")
            return None, f"Error: {str(e)}"
    
    def create_fallback_widget(self, message):
        """Create a fallback widget with an error message."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel(message)
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        return widget
    
    def find_ui_components(self, workspace_widget):
        """Find important UI components in the loaded workspace widget."""
        components = {}
        
        # Find the main tab widget
        tab_widget = workspace_widget.findChild(QtWidgets.QTabWidget, "tabWidget")
        components['tab_widget'] = tab_widget
        
        if tab_widget:
            # Find the nested tab widget
            inner_tab_widget = tab_widget.findChild(QtWidgets.QTabWidget, "tabWidget_2")
            components['inner_tab_widget'] = inner_tab_widget
            
            if inner_tab_widget:
                # Find the table widget inside the inner tab
                inner_table_widget = inner_tab_widget.findChild(QtWidgets.QTableWidget, "tableWidget")
                components['inner_table_widget'] = inner_table_widget
        
        return components
