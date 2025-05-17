from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PySide6 import QtUiTools, QtCore

class ExplorerWidget:
    def __init__(self, base_dir=None):
        """Initialize the explorer widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.tree_widget = None

    def load_ui(self):
        """Load the dock widget from UI file and set up the tree widget."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/explorer/explorer_widget.ui"
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
            
        # Remove all margins to make the tree fill the entire dock
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Clear the layout (remove any existing widgets)
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create the tree widget
        self.tree_widget = QTreeWidget(content_widget)
        
        # Hide the header to remove the title
        self.tree_widget.setHeaderHidden(True)
        
        # Set up the tree structure
        self.populate_tree()
        
        # Add the tree widget to the layout
        layout.addWidget(self.tree_widget)
        
        return self.widget

    def populate_tree(self):
        """Add items to the tree widget."""
        # Add items to the tree - Batch sessions by date
        root1 = QTreeWidgetItem(self.tree_widget, ["2023-09-15"])
        QTreeWidgetItem(root1, ["batch_001_active"])
        QTreeWidgetItem(root1, ["batch_002_finished"])
        QTreeWidgetItem(root1, ["batch_003_draft"])
        
        root2 = QTreeWidgetItem(self.tree_widget, ["2023-10-20"])
        QTreeWidgetItem(root2, ["batch_004_active"])
        QTreeWidgetItem(root2, ["batch_005_active"])
        QTreeWidgetItem(root2, ["batch_006_draft"])
        
        root3 = QTreeWidgetItem(self.tree_widget, ["2023-11-05"])
        QTreeWidgetItem(root3, ["batch_007_finished"])
        QTreeWidgetItem(root3, ["batch_008_draft"])
        
        root4 = QTreeWidgetItem(self.tree_widget, ["2023-12-01"])
        QTreeWidgetItem(root4, ["batch_009_active"])
        QTreeWidgetItem(root4, ["batch_010_draft"])
        
        # Expand all items by default
        self.tree_widget.expandAll()
