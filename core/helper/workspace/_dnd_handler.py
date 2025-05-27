# filepath: z:\Build\Image-Tea-mini\core\helper\workspace\_dnd_handler.py
import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.utils.logger import log, debug, warning, error, exception
from core.global_operations.file_operations import (
    get_new_operation_id,
    get_file_details,
    get_image_extensions,
    get_video_extensions
)
from database.db_workspace import WorkspaceDataModel

class DropAreaHandler(QtCore.QObject):
    """Handler for drag and drop operations in the workspace."""
    
    def __init__(self, workspace_controller):
        """Initialize the drop area handler."""
        super().__init__()
        self.controller = workspace_controller
        self.drop_area = None
        self.db_model = WorkspaceDataModel()
        
    def setup_drop_area(self, drop_area_widget):
        """Set up the drop area to handle drag and drop events."""
        self.drop_area = drop_area_widget
        
        if self.drop_area:
            # Enable dropping
            self.drop_area.setAcceptDrops(True)
            
            # Install event filter to handle drop events
            self.drop_area.installEventFilter(self)
        else:
            warning("Failed to set up drop area handler: widget not found")

    def eventFilter(self, obj, event):
        """Filter events to handle drag and drop."""
        if obj is self.drop_area:
            if event.type() == QtCore.QEvent.DragEnter:
                self._handle_drag_enter(event)
                return True
                
            elif event.type() == QtCore.QEvent.DragMove:
                event.acceptProposedAction()
                return True
                
            elif event.type() == QtCore.QEvent.Drop:
                self._handle_drop(event)
                return True
                
            elif event.type() == QtCore.QEvent.DragLeave:
                event.accept()
                return True
                
        # Let the parent class handle other events
        return super().eventFilter(obj, event)

    def _handle_drag_enter(self, event):
        """Handle drag enter event."""
        # Check if the dragged data has URLs (files/folders)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _handle_drop(self, event):
        """Handle drop event."""
        urls = event.mimeData().urls()
        
        if not urls:
            event.ignore()
            return
            
        event.acceptProposedAction()
        
        # Process the dropped files or directories
        self._process_dropped_urls(urls)

    def _process_dropped_urls(self, urls):
        """
        Process the dropped URLs (files and folders).
        
        Args:
            urls: List of QUrls representing the dropped files/folders
        """
        # Generate a single operation ID for all files in this drop
        operation_id = get_new_operation_id()
        
        # Sort URLs into files and folders
        file_paths = []
        folder_paths = []
        
        # Get supported extensions
        image_extensions = get_image_extensions()
        video_extensions = get_video_extensions()
        
        # Categorize the dropped items
        for url in urls:
            path = url.toLocalFile()
            
            if os.path.isfile(path):
                # Check if it's a supported file type
                _, ext = os.path.splitext(path)
                if ext.lower() in image_extensions or ext.lower() in video_extensions:
                    file_paths.append(path)
            elif os.path.isdir(path):
                folder_paths.append(path)
        
        # Process files first
        if file_paths:
            self._process_dropped_files(file_paths, operation_id)
            
        # Process folders next
        if folder_paths:
            self._process_dropped_folders(folder_paths)
          # If we added files, refresh the workspace to show the new files
        if file_paths or folder_paths:
            # Format the operation ID properly for the explorer (ID_XXXX format)
            formatted_item_id = f"ID_{operation_id}"
            # Switch to the workspace UI and refresh it with the new item ID
            self.controller.on_explorer_item_selected(formatted_item_id)

    def _process_dropped_files(self, file_paths, operation_id):
        """
        Process dropped files and add them to the database.
        
        Args:
            file_paths: List of file paths
            operation_id: Operation ID to use for all files
        """
        file_details_list = []
        
        for path in file_paths:
            details = get_file_details(path, operation_id)
            if details:
                file_details_list.append(details)
        
        if file_details_list:
            # Add all files to the database at once with the same item_id
            self.db_model.add_files_from_drop(file_details_list)
            
            log(f"Added {len(file_details_list)} files via drag and drop (Operation ID: {operation_id})")

    def _process_dropped_folders(self, folder_paths):
        """
        Process dropped folders and add them to the database.
        
        Args:
            folder_paths: List of folder paths
        """
        self.db_model.process_multiple_dropped_folders(folder_paths)
        log(f"Added {len(folder_paths)} folders via drag and drop")