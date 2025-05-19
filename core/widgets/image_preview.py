from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6 import QtUiTools, QtCore
from core.utils.logger import log, debug, warning, error, exception

class ScalableImageLabel(QLabel):
    """A label that automatically scales its image to fit the available space."""
    
    def __init__(self, parent=None):
        """Initialize the scalable image label."""
        super().__init__(parent)
        self.original_pixmap = None
        self.image_path = None
        # Set size policy to allow the widget to shrink and expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def setImagePath(self, path):
        """Set an image path and load the original pixmap.
        
        Args:
            path: Path to the image file
        """
        self.image_path = path
        self.original_pixmap = QPixmap(path)
        self.updatePixmap()
        
    def updatePixmap(self):
        """Adjust the pixmap size to fit the label dimensions while maintaining aspect ratio."""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # Scale the pixmap to fit the label while preserving aspect ratio
            scaled_pixmap = self.original_pixmap.scaled(
                self.width(), 
                self.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            self.setAlignment(Qt.AlignCenter)
    
    def resizeEvent(self, event):
        """Handle resize events to update the pixmap size."""
        super().resizeEvent(event)
        self.updatePixmap()
        
    # Override size hint methods to allow widget to shrink
    def sizeHint(self):
        return QtCore.QSize(200, 200)
        
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

class ImagePreviewWidget:
    """Widget to preview images with automatic scaling."""
    
    def __init__(self, base_dir=None):
        """Initialize the image preview widget.
        
        Args:
            base_dir: The base directory of the application
        """
        self.BASE_DIR = base_dir
        self.widget = None
        self.preview_label = None
        self.current_item_id = None
        self.current_filepath = None
        
    def load_ui(self):
        """Load the dock widget from UI file and set up the preview area."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/preview/image_preview.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Access the dock widget content
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        
        # Remove existing preview label if it exists
        old_label = content_widget.findChild(QLabel, "previewLabel")
        if old_label:
            layout = content_widget.layout()
            layout.removeWidget(old_label)
            old_label.deleteLater()
        
        # Create a new ScalableImageLabel
        self.preview_label = ScalableImageLabel(content_widget)
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setText("Preview Image")
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        # Set some styling for the preview label
        self.preview_label.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                font-size: 14pt;
                background-color: rgba(40, 40, 40, 0.5);
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Add the new label to the layout
        content_widget.layout().addWidget(self.preview_label)
        
        return self.widget
    
    def set_image(self, image_path):
        """Set an image to be displayed in the preview.
        
        Args:
            image_path: Path to the image file to display
        """
        if not self.preview_label:
            return False
            
        try:
            if not isinstance(self.preview_label, ScalableImageLabel):
                debug("Preview label is not a ScalableImageLabel, using standard QLabel method")
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    self.preview_label.setText("Could not load image")
                    return False
                    
                # Scale the pixmap to fit in the preview label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                # Set the pixmap to the preview label
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setAlignment(Qt.AlignCenter)
            else:
                debug(f"Using ScalableImageLabel for image: {image_path}")
                self.preview_label.setImagePath(image_path)
                self.current_filepath = image_path
            
            return True
        except Exception as e:
            error(f"Error setting image: {str(e)}")
            self.preview_label.setText(f"Error: {str(e)}")
            return False
    
    def update_preview_from_database(self, item_id=None, id=None):
        """Update the preview based on database information.
        
        Args:
            item_id: The item_id to search for in the database
            id: The primary key id to search for in the database
            
        Returns:
            bool: True if preview was updated successfully, False otherwise
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
            elif item_id is not None:
                # Get files for the item_id - use the first file
                files = db.get_files_by_item_id(item_id)
                if files and len(files) > 0:
                    file_info = files[0]
                    self.current_item_id = item_id
            
            if file_info and 'filepath' in file_info:
                filepath = file_info.get('filepath')
                if filepath:
                    debug(f"Setting image preview from database: {filepath}")
                    return self.set_image(filepath)
            
            # If we got here, we couldn't find a valid image
            self.clear_preview()
            self.preview_label.setText("No image found")
            return False
            
        except Exception as e:
            error(f"Error updating preview from database: {str(e)}")
            self.clear_preview()
            self.preview_label.setText(f"Error: {str(e)}")
            return False
    
    def clear_preview(self):
        """Clear the current preview image and display the default message."""
        if self.preview_label:
            if isinstance(self.preview_label, ScalableImageLabel):
                self.preview_label.setPixmap(QPixmap())  # Clear the pixmap
                self.preview_label.original_pixmap = None
                self.preview_label.image_path = None
            
            self.preview_label.clear()
            self.preview_label.setText("Preview Image")
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.current_filepath = None
            
    def get_current_filepath(self):
        """Get the filepath of the currently displayed image."""
        return self.current_filepath
