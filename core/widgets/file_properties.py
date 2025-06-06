from PySide6.QtWidgets import QWidget, QLabel
from PySide6 import QtUiTools, QtCore
import os
from core.utils.logger import log, debug, warning, error, exception

class FilePropertiesWidget:
    def __init__(self, base_dir=None):
        """Initialize the file properties widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        
        # Property value labels
        self.filename_value = None
        self.title_value = None
        self.tags_value = None
        self.filepath_value = None
        self.category_value = None
        self.sub_category_value = None
        self.title_length_value = None
        self.tags_count_value = None
        self.status_value = None
        self.id_value = None
        self.type_value = None
        self.size_value = None
        self.dimensions_value = None
        
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
        
        # Access the dock widget content
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        
        # Find all property value labels
        self.filename_value = content_widget.findChild(QLabel, "filenameValue")
        self.title_value = content_widget.findChild(QLabel, "titleValue")
        self.tags_value = content_widget.findChild(QLabel, "tagsValue")
        self.filepath_value = content_widget.findChild(QLabel, "filepathValue")
        self.category_value = content_widget.findChild(QLabel, "categoryValue")
        self.sub_category_value = content_widget.findChild(QLabel, "subCategoryValue")
        self.title_length_value = content_widget.findChild(QLabel, "titleLengthValue")
        self.tags_count_value = content_widget.findChild(QLabel, "tagsCountValue")
        self.status_value = content_widget.findChild(QLabel, "statusValue")
        self.id_value = content_widget.findChild(QLabel, "idValue")
        self.type_value = content_widget.findChild(QLabel, "typeValue")
        self.size_value = content_widget.findChild(QLabel, "sizeValue")
        self.dimensions_value = content_widget.findChild(QLabel, "dimensionsValue")
        
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
    
    def get_image_dimensions(self, filepath):
        """Get image dimensions from file."""
        try:
            from PIL import Image
            if filepath and os.path.exists(filepath):
                with Image.open(filepath) as img:
                    return f"{img.width} x {img.height}"
        except Exception as e:
            debug(f"Could not get image dimensions: {str(e)}")
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
        """Update all property value labels with data from file_info."""
        try:
            # Basic file properties
            filename = file_info.get('filename', '-')
            if file_info.get('extension'):
                filename = f"{filename}.{file_info.get('extension')}"
            self.set_label_text(self.filename_value, filename)
            
            self.set_label_text(self.title_value, file_info.get('title', '-'))
            self.set_label_text(self.tags_value, file_info.get('tags', '-'))
            self.set_label_text(self.filepath_value, file_info.get('filepath', '-'))
            
            # Category and sub-category (not in current database schema, set as placeholder)
            self.set_label_text(self.category_value, '-')
            self.set_label_text(self.sub_category_value, '-')
            
            # Calculated properties
            title = file_info.get('title', '')
            title_length = len(title) if title and title != '-' else 0
            self.set_label_text(self.title_length_value, str(title_length))
            
            tags = file_info.get('tags', '')
            if tags and tags != '-':
                # Count tags by splitting on common separators
                tags_list = [tag.strip() for tag in tags.replace(',', ' ').split() if tag.strip()]
                tags_count = len(tags_list)
            else:
                tags_count = 0
            self.set_label_text(self.tags_count_value, str(tags_count))
            
            self.set_label_text(self.status_value, file_info.get('status', '-'))
            self.set_label_text(self.id_value, str(file_info.get('id', '-')))
            
            # File system properties
            filepath = file_info.get('filepath')
            if filepath and os.path.exists(filepath):
                # File type from extension
                file_extension = file_info.get('extension', '').upper()
                self.set_label_text(self.type_value, file_extension if file_extension else 'Unknown')
                
                # File size
                file_size = file_info.get('filesize')
                if file_size:
                    formatted_size = self.format_file_size(file_size)
                else:
                    # Get size from file system if not in database
                    try:
                        file_size = os.path.getsize(filepath)
                        formatted_size = self.format_file_size(file_size)
                    except:
                        formatted_size = "Unknown"
                self.set_label_text(self.size_value, formatted_size)
                
                # Image dimensions (for image files)
                if file_extension.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp']:
                    dimensions = self.get_image_dimensions(filepath)
                    self.set_label_text(self.dimensions_value, dimensions)
                else:
                    self.set_label_text(self.dimensions_value, '-')
            else:
                self.set_label_text(self.type_value, file_info.get('extension', 'Unknown').upper())
                self.set_label_text(self.size_value, self.format_file_size(file_info.get('filesize', 0)))
                self.set_label_text(self.dimensions_value, '-')
                
        except Exception as e:
            error(f"Error updating property values: {str(e)}")
    
    def set_label_text(self, label, text):
        """Safely set text to a label widget."""
        if label:
            label.setText(str(text) if text is not None else '-')
    
    def clear_properties(self):
        """Clear all property values and display default message."""
        try:
            labels = [
                self.filename_value, self.title_value, self.tags_value,
                self.filepath_value, self.category_value, self.sub_category_value,
                self.title_length_value, self.tags_count_value, self.status_value,
                self.id_value, self.type_value, self.size_value, self.dimensions_value
            ]
            
            for label in labels:
                self.set_label_text(label, '-')
                
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
