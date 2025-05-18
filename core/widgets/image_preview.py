from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6 import QtUiTools, QtCore

class ImagePreviewWidget:
    def __init__(self, base_dir=None):
        """Initialize the image preview widget.
        
        Args:
            base_dir: The base directory of the application
        """
        self.BASE_DIR = base_dir
        self.widget = None
        self.preview_label = None
        
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
        
        # Find the preview label
        self.preview_label = content_widget.findChild(QLabel, "previewLabel")
        
        # Set some styling for the preview label
        self.preview_label.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                font-size: 14pt;
            }
        """)
        
        return self.widget
    
    def set_image(self, image_path):
        """Set an image to be displayed in the preview.
        
        Args:
            image_path: Path to the image file to display
        """
        if not self.preview_label:
            return False
            
        try:
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
            return True
        except Exception as e:
            self.preview_label.setText(f"Error: {str(e)}")
            return False
    
    def clear_preview(self):
        """Clear the current preview image and display the default message."""
        if self.preview_label:
            self.preview_label.clear()
            self.preview_label.setText("Preview Image")
            self.preview_label.setAlignment(Qt.AlignCenter)
