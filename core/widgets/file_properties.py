from PySide6.QtWidgets import QWidget, QLabel
from PySide6 import QtUiTools, QtCore

class FilePropertiesWidget:
    def __init__(self, base_dir=None):
        """Initialize the file properties widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.properties_label = None
        
    def load_ui(self):
        """Load the dock widget from UI file and set up the properties panel."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/properties/file_properties.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Access the dock widget content
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        
        # Find the properties label widget
        self.properties_label = content_widget.findChild(QLabel, "propertiesLabel")
        
        return self.widget
