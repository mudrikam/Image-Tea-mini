from PySide6 import QtWidgets, QtCore, QtGui
from core.utils.logger import log, debug, warning, error, exception

# Define a FlowLayout class for dynamic grid layouts - inspired by the example
class FlowLayout(QtWidgets.QLayout):
    """A flow layout that arranges items horizontally and wraps to the next line when needed."""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing)
        self.itemList = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.itemList.append(item)
    
    def count(self):
        return len(self.itemList)
    
    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None
    
    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None
    
    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QtCore.QSize()
        
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
            
        margin = self.contentsMargins()
        size += QtCore.QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
    
    def doLayout(self, rect, testOnly):
        """Arrange items in a horizontal flow that wraps to next line when full."""
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        
        for item in self.itemList:
            spaceX = self.spacing()
            spaceY = self.spacing()
            
            nextX = x + item.sizeHint().width() + spaceX
            
            # If this item would extend beyond the right edge and we're not on the first item of a line,
            # move to the next row
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
                
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
                
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
            
        return y + lineHeight - rect.y()


class GridManager:
    """Helper class for managing grid view display of images with names."""
    def __init__(self):
        """Initialize the grid manager."""
        self.image_items = []  # Keep track of created items to manage memory
        self.image_size = 150  # Default image size in the grid
        self.grid_spacing = 10  # Default spacing between grid items
        self.active_image = None  # Track the currently active image widget
        
    def update_grid_data(self, grid_widget, item_id):
        """
        Update the grid data for a specific item tab.
        
        Args:
            grid_widget: The grid container widget
            item_id: The item ID to load data for
            
        Returns:
            int: Number of images loaded
        """
        debug(f"GridManager update_grid_data called for item_id: {item_id}")
        
        if not grid_widget:
            warning(f"Grid widget not provided for item {item_id}")
            return 0
        
        try:
            # Get the actual ID part from the item_id
            parts = item_id.split('_')
            debug(f"Item ID parts: {parts}")
            
            if len(parts) < 2:
                warning(f"Invalid item ID format: {item_id}")
                return 0
                
            actual_id = parts[1]
            debug(f"Using actual_id: {actual_id} for database lookup")
            
            # Get data from the database
            try:
                from database.db_project_files import ProjectFilesModel
                debug(f"Fetching files from database for item_id: {actual_id}")
                files_data = ProjectFilesModel().get_files_by_item_id(actual_id)
                debug(f"Found {len(files_data) if files_data else 0} files from database")
            except Exception as e:
                exception(e, "Error getting data from database")
                files_data = []
            
            # Clear existing items
            self._clear_grid(grid_widget)
            
            # Get the number of files
            file_count = len(files_data) if files_data else 0
            
            # Create a new scroll area and flow layout from scratch
            # This ensures we have a clean implementation like the example
            
            # First, clear any existing layouts
            old_layout = grid_widget.layout()
            if old_layout:
                # Clear items from old layout
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Need to use this approach to fully remove old layout
                QtWidgets.QWidget().setLayout(old_layout)
            
            # Create new vertical layout for the grid widget
            main_layout = QtWidgets.QVBoxLayout(grid_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create scroll area
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setObjectName("gridScrollArea") 
            scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)  # Hide the frame
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            
            # Style scrollbars - consistent with output logs
            scroll_area.setStyleSheet("""
                QScrollBar:vertical {
                    border: none;
                    background-color: rgba(0, 0, 0, 5);
                    width: 8px;
                    margin: 0px;
                    border-radius: 4px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: rgba(128, 128, 128, 60);
                    min-height: 20px;
                    border-radius: 4px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: rgba(128, 128, 128, 120);
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                QScrollBar:horizontal {
                    border: none;
                    background-color: rgba(0, 0, 0, 5);
                    height: 8px;
                    margin: 0px;
                    border-radius: 4px;
                }
                
                QScrollBar::handle:horizontal {
                    background-color: rgba(128, 128, 128, 60);
                    min-width: 20px;
                    border-radius: 4px;
                }
                
                QScrollBar::handle:horizontal:hover {
                    background-color: rgba(128, 128, 128, 120);
                }
                
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)
            
            # Add scroll area to main layout
            main_layout.addWidget(scroll_area)
            
            # Create content widget for scroll area
            scroll_content = QtWidgets.QWidget()
            scroll_area.setWidget(scroll_content)
            
            # Create the flow layout for the image grid
            flow_layout = FlowLayout(margin=10, spacing=self.grid_spacing)
            scroll_content.setLayout(flow_layout)
            
            # Add data to the grid using the flow layout
            if files_data and len(files_data) > 0:
                # Add each file to the flow grid
                for idx, file_info in enumerate(files_data):
                    try:
                        # Create image widget and add to flow layout
                        image_widget = self._create_image_widget(file_info)
                        flow_layout.addWidget(image_widget)
                        
                        # Store for memory management
                        self.image_items.append(image_widget)
                    except Exception as e:
                        exception(e, f"Error adding image {idx} to grid")
            else:
                # No images found
                no_data_label = QtWidgets.QLabel("No images found")
                no_data_label.setAlignment(QtCore.Qt.AlignCenter)
                flow_layout.addWidget(no_data_label)
                self.image_items.append(no_data_label)
            
            return file_count
                
        except Exception as e:
            exception(e, f"Error updating grid data for item {item_id}")
            return 0
    
    def _clear_grid(self, grid_widget):
        """Clear all items from the grid and release memory."""
        # Clear our tracked items first to help garbage collection
        for item in self.image_items:
            if item:
                try:
                    item.deleteLater()
                except:
                    pass
        
        self.image_items.clear()
        
        # We'll recreate the layout from scratch, so we don't need complex clearing here
    
    def _create_image_widget(self, file_info):
        """
        Create a widget containing an image and its name like in the example image_grid.py.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            QWidget: Widget containing the image and name
        """
        filepath = file_info.get('filepath', '')
        filename = file_info.get('filename', '')
        extension = file_info.get('extension', '')
        
        # Create a container widget
        container = QtWidgets.QWidget()
        
        # Set fixed width but flexible height
        item_width = self.image_size + 10
        container.setFixedWidth(item_width)
        
        # Use vertical layout like in the example
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Create image label with hover effects (like in the example)
        image_label = QtWidgets.QLabel()
        image_label.setAlignment(QtCore.Qt.AlignCenter)
        image_label.setFixedSize(self.image_size, self.image_size)
          # Add hover effects similar to the example
        image_label.setStyleSheet("""
            QLabel {
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                padding: 2px;
            }
            QLabel:hover {
                border: 2px solid rgba(88, 165, 0, 0.3);
                background-color: rgba(88, 165, 0, 0.05);
            }
        """)
        
        # Enable hover events and pointer cursor
        image_label.setAttribute(QtCore.Qt.WA_Hover, True)
        image_label.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Load the image
        self._load_image(image_label, filepath)
        
        # Create text label for filename
        MAX_NAME_LENGTH = 18
        if len(filename) > MAX_NAME_LENGTH:
            display_name = f"{filename[:MAX_NAME_LENGTH-3]}...{extension}"
        else:
            display_name = f"{filename}{extension}"
            
        text_label = QtWidgets.QLabel(display_name)
        text_label.setAlignment(QtCore.Qt.AlignCenter)
        text_label.setWordWrap(False)
        text_label.setFixedWidth(self.image_size)
        text_label.setStyleSheet("font-size: 9pt;")
        text_label.setToolTip(f"{filename}{extension}")
        
        # Add widgets to layout
        layout.addWidget(image_label)
        layout.addWidget(text_label)
        
        # Store file info in widget
        container.setProperty("file_info", file_info)
        
        # Add click handler - both container and image can be clicked
        container.mousePressEvent = lambda event: self._handle_image_click(container, event)
        image_label.mousePressEvent = lambda event: self._handle_image_click(container, event)
        
        return container
    
    def _load_image(self, label, image_path):
        """Load an image from a path and display it in a label."""
        try:
            pixmap = QtGui.QPixmap(image_path)
            
            # If the image loaded successfully
            if not pixmap.isNull():
                # Scale to fit while keeping aspect ratio
                pixmap = pixmap.scaled(
                    self.image_size, self.image_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                label.setPixmap(pixmap)
            else:                # Use a placeholder for failed loads
                label.setText("Cannot load\nimage")
                warning(f"Failed to load image: {image_path}")
                
        except Exception as e:
            label.setText("Error")
            exception(e, f"Error loading image: {image_path}")
            
    def _update_active_image(self, new_active_widget):
        """
        Update the styling to highlight the active image and reset previous selection.
        
        Args:
            new_active_widget: The widget to set as active
        """
        try:
            # Reset the previous active image if exists
            if self.active_image:
                # Find the image label in the container
                for child in self.active_image.children():
                    if isinstance(child, QtWidgets.QLabel) and child.objectName() != "filename_label":
                        # Reset to normal style
                        child.setStyleSheet("""
                            QLabel {
                                border: 2px solid rgba(0, 0, 0, 0.1);
                                border-radius: 4px;
                                padding: 2px;
                            }
                            QLabel:hover {
                                border: 2px solid rgba(88, 165, 0, 0.3);
                                background-color: rgba(88, 165, 0, 0.05);
                            }
                        """)
                        break
            
            # Update the active image
            self.active_image = new_active_widget
            
            # Apply active style to the new active image
            if self.active_image:
                for child in self.active_image.children():
                    if isinstance(child, QtWidgets.QLabel) and child.objectName() != "filename_label":
                        # Set active style with green border at 20% opacity
                        child.setStyleSheet("""
                            QLabel {
                                border: 2px solid rgba(88, 165, 0, 0.3);
                                border-radius: 4px;
                                padding: 2px;
                                background-color: rgba(88, 165, 0, 0.20);
                            }
                            QLabel:hover {
                                border: 2px solid rgba(88, 165, 0, 0.5);
                                background-color: rgba(88, 165, 0, 0.25);
                            }
                        """)
                        break
        except Exception as e:
            exception(e, "Error updating active image styling")
    def _handle_image_click(self, widget, event):
        """
        Handle click events on grid images to update both image preview and file properties.
        """
        try:
            # Get file info from the widget
            file_info = widget.property("file_info")
            
            if not file_info:
                return
                
            debug(f"Grid image clicked: {file_info.get('filename')} ({file_info.get('filepath')})")
            
            # Update active image border styling
            self._update_active_image(widget)
            
            # Get the parent grid widget to access the callback function
            parent_widget = widget.parent()
            while parent_widget and not hasattr(parent_widget, '_callback_function'):
                parent_widget = parent_widget.parent()
            
            # Call the same callback function that the table uses
            if parent_widget and hasattr(parent_widget, '_callback_function'):
                callback_function = parent_widget._callback_function
                if callback_function:
                    # Call with same parameters as table click handler
                    callback_function(0, 0, file_info)
                else:
                    debug("No callback function found in grid widget")
            else:
                debug("No callback function available for grid click")
                        
        except Exception as e:
            exception(e, "Error handling grid image click")
    
    def setup_grid_click_handler(self, grid_widget, callback_function):
        """
        Set up a click handler for the grid widget items.
        This stores the callback function for use by the grid items.
        
        Args:
            grid_widget: The grid widget to set up the click handler for
            callback_function: The function to call when an item is clicked
        """
        if not grid_widget:
            warning("Grid widget not provided, can't set up click handler")
            return
        
        # Store callback reference for use by items
        grid_widget._callback_function = callback_function
        debug(f"Set up grid click handler with callback: {callback_function.__name__}")
