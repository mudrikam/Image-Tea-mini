from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QTreeWidget
from PySide6 import QtUiTools, QtCore
from PySide6.QtGui import QBrush, QColor
import os
from core.utils.logger import log, debug, warning, error, exception

class FilePropertiesWidget:
    def __init__(self, base_dir=None):
        """Initialize the file properties widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        # Tree widget for properties
        self.properties_tree = None
        
        self.current_item_id = None
        self.current_file_id = None
        
    def load_ui(self):
        """Load the dock widget from UI file and set up the properties panel."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/properties/file_properties.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Access the tree widget
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        self.properties_tree = content_widget.findChild(QTreeWidget, "propertiesTreeWidget")
        
        # Set up tree widget columns
        if self.properties_tree:
            self.properties_tree.setColumnCount(2)
            self.properties_tree.setHeaderLabels(["Property", "Value"])
            # Set column widths
            self.properties_tree.setColumnWidth(0, 100)
            self.properties_tree.setColumnWidth(1, 180)
        
        return self.widget
    def format_file_size(self, size_bytes):
        """Format file size in bytes to human-readable format."""
        if not size_bytes or size_bytes == 0:
            return "0 B"
        
        try:
            size_bytes = int(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} PB"
        except (ValueError, TypeError):
            return "Unknown"
    
    def update_properties_from_database(self, item_id=None, id=None):
        """Update the properties based on database information.
        
        Args:
            item_id: The item_id to search for in the database
            id: The primary key id to search for in the database
            
        Returns:
            bool: True if properties were updated successfully, False otherwise
        """
        try:
            from database.db_project_files import ProjectFilesModel
            db = ProjectFilesModel()
            
            # Get the file information based on provided parameters
            file_info = None
            if id is not None:
                # Get specific file by ID
                files = db.get_files_by_id(id)
                if files and len(files) > 0:
                    file_info = files[0]
                    self.current_file_id = id
            elif item_id is not None:
                # Get files for the item_id - use the first file
                files = db.get_files_by_item_id(item_id)
                if files and len(files) > 0:
                    file_info = files[0]
                    self.current_item_id = item_id
                    self.current_file_id = file_info.get('id')
            
            if file_info:
                self.update_property_values(file_info)
                return True
            else:
                # No file found, clear properties
                self.clear_properties()
                return False
                
        except Exception as e:
            error(f"Error updating properties from database: {str(e)}")
            self.clear_properties()
            return False
    def update_property_values(self, file_info):
        """Update all property values in the tree widget with data from file_info."""
        try:
            if not self.properties_tree:
                return
                
            # Clear existing items
            self.properties_tree.clear()
            
            # Basic file properties
            filename = file_info.get('filename', '-')
            if file_info.get('extension'):
                filename = f"{filename}.{file_info.get('extension')}"
            
            # Add items to tree
            self.add_tree_item("Filename", filename)
            self.add_tree_item("Title", file_info.get('title', '-'))
            self.add_tree_item("Tags", file_info.get('tags', '-'))
            self.add_tree_item("Description", file_info.get('description', '-'))
            self.add_tree_item("Filepath", file_info.get('filepath', '-'))
            self.add_tree_item("Category", file_info.get('category', '-'))
            self.add_tree_item("Sub Category", file_info.get('sub_category', '-'))
            
            # Metadata
            self.add_tree_item("Title Length", str(file_info.get('title_length', 0)))
            self.add_tree_item("Tags Count", str(file_info.get('tags_count', 0)))
            self.add_tree_item("Status", file_info.get('status', '-'))
            self.add_tree_item("ID", str(file_info.get('id', '-')))
            
            # File system properties
            self.add_tree_item("Type", file_info.get('file_type', file_info.get('extension', 'Unknown').upper()))
            
            # File size
            file_size = file_info.get('filesize')
            if file_size:
                formatted_size = self.format_file_size(file_size)
            else:
                formatted_size = "Unknown"
            self.add_tree_item("Size", formatted_size)
            
            # Image dimensions
            dimensions = file_info.get('dimensions')
            if dimensions:
                self.add_tree_item("Dimensions", dimensions)
            else:
                # Fallback: try to construct from width/height if available
                width = file_info.get('image_width')
                height = file_info.get('image_height')
                if width and height:
                    self.add_tree_item("Dimensions", f"{width} x {height}")
                else:
                    self.add_tree_item("Dimensions", '-')
                
        except Exception as e:
            error(f"Error updating property values: {str(e)}")
    
    def add_tree_item(self, property_name, value):
        """Add a property item to the tree widget."""
        if self.properties_tree:
            item = QTreeWidgetItem([property_name, str(value) if value is not None else '-'])
            self.properties_tree.addTopLevelItem(item)
    
    def clear_properties(self):
        """Clear all property values and display default message."""
        try:            
            if self.properties_tree:
                self.properties_tree.clear()
                
            self.current_item_id = None
            self.current_file_id = None
            
        except Exception as e:
            error(f"Error clearing properties: {str(e)}")
    
    def get_current_item_id(self):
        """Get the item_id of the currently displayed properties."""
        return self.current_item_id
    
    def get_current_file_id(self):
        """Get the file id of the currently displayed properties."""
        return self.current_file_id
