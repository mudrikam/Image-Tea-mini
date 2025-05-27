from PySide6 import QtWidgets, QtCore, QtGui
from core.utils.logger import log, debug, warning, error, exception

# Define a FlowLayout class for dynamic grid layouts
class FlowLayout(QtWidgets.QLayout):
    """A flow layout that arranges items dynamically based on available space."""
    
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
        """
        Layout all items in a flow layout (left-to-right, top-to-bottom)
        
        Args:
            rect (QRect): Rectangle to lay out items in
            testOnly (bool): If True, just calculate height, don't move widgets
            
        Returns:
            int: Required height for layout
        """
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        
        for item in self.itemList:
            spaceX = self.spacing()
            spaceY = self.spacing()
            
            nextX = x + item.sizeHint().width() + spaceX
            
            # If item would extend beyond right edge, move to next row
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            
            # Only set the actual geometry when not just testing
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            
            # Move x position to next item
            x = nextX
            # Update line height to tallest item in this row
            lineHeight = max(lineHeight, item.sizeHint().height())
        
        # Return total height needed
        return y + lineHeight - rect.y()

class GridManager:
    """Helper class for managing grid view display of images with names."""
    
    def __init__(self):
        """Initialize the grid manager."""
        self.image_items = []  # Keep track of created items to manage memory
        self.image_size = 150  # Default image size in the grid
        self.grid_spacing = 10  # Default spacing between grid items
        
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
            
            # Find the grid layout in our UI structure
            grid_layout = None
            
            # Find standard components from our main_workspace_grid.ui
            # First check for the scroll area in verticalLayoutGrid
            vertical_layout = grid_widget.findChild(QtWidgets.QVBoxLayout, "verticalLayoutGrid")
            if vertical_layout:
                debug("Found verticalLayoutGrid")
                
                # Look for scroll area in this layout or directly in the widget
                scroll_area = grid_widget.findChild(QtWidgets.QScrollArea, "scrollArea")
                if not scroll_area:
                    # Try looking in verticalLayoutGrid
                    for i in range(vertical_layout.count()):
                        item = vertical_layout.itemAt(i)
                        if item and item.widget() and isinstance(item.widget(), QtWidgets.QScrollArea):
                            scroll_area = item.widget()
                            break
                
                if scroll_area:
                    debug("Found scrollArea")
                    # Get the scroll area content widget
                    scroll_content = scroll_area.widget()
                    if scroll_content:
                        # Find the grid container in the scroll content
                        grid_container = scroll_content.findChild(QtWidgets.QWidget, "gridContainer")
                        if grid_container and hasattr(grid_container, 'layout'):
                            grid_layout = grid_container.layout()
                            debug("Found grid layout in grid container")
            
            # If still not found, look for any gridContainer in the widget hierarchy
            if not grid_layout:
                grid_container = grid_widget.findChild(QtWidgets.QWidget, "gridContainer") 
                if grid_container and hasattr(grid_container, 'layout'):
                    grid_layout = grid_container.layout()
                    debug("Found grid layout through direct gridContainer search")
                                    
            # If we still don't have a grid layout, create one in a scroll area
            if not grid_layout:
                debug("Creating new grid layout as fallback")
                # Find or create scroll area
                scroll_area = grid_widget.findChild(QtWidgets.QScrollArea)
                if not scroll_area:
                    # Try to find the verticalLayoutGrid to place our scroll area
                    vertical_layout = grid_widget.findChild(QtWidgets.QVBoxLayout, "verticalLayoutGrid")
                      # Create scrollarea with proper styling for seamless integration
                    scroll_area = QtWidgets.QScrollArea()
                    scroll_area.setWidgetResizable(True)
                    scroll_area.setObjectName("gridScrollArea")
                    scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)  # Hide the frame
                    scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
                    scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
                    
                    # Style the scrollbars to match the application style
                    scroll_area.setStyleSheet("""
                        QScrollBar:vertical {
                            background: #f0f0f0;
                            width: 10px;
                            margin: 0px;
                        }
                        QScrollBar::handle:vertical {
                            background: #c0c0c0;
                            border-radius: 4px;
                            min-height: 20px;
                        }
                        QScrollBar::handle:vertical:hover {
                            background: #a0a0a0;
                        }
                        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                            height: 0px;
                        }
                        QScrollBar:horizontal {
                            background: #f0f0f0;
                            height: 10px;
                            margin: 0px;
                        }
                        QScrollBar::handle:horizontal {
                            background: #c0c0c0;
                            border-radius: 4px;
                            min-width: 20px;
                        }
                        QScrollBar::handle:horizontal:hover {
                            background: #a0a0a0;
                        }
                        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                            width: 0px;
                        }
                    """)
                    
                    # Add to layout if found
                    if vertical_layout:
                        vertical_layout.addWidget(scroll_area)
                    else:
                        # Create a layout for grid_widget if needed
                        if not grid_widget.layout():
                            layout = QtWidgets.QVBoxLayout(grid_widget)
                        else:
                            layout = grid_widget.layout()
                        layout.addWidget(scroll_area)                
                        # Create or get scroll content
                scroll_content = scroll_area.widget()
                if not scroll_content:
                    scroll_content = QtWidgets.QWidget()
                    scroll_area.setWidget(scroll_content)
                
                # Create content layout if needed
                if not scroll_content.layout():
                    scroll_content_layout = QtWidgets.QVBoxLayout(scroll_content)
                    scroll_content_layout.setContentsMargins(10, 10, 10, 10)
                else:
                    scroll_content_layout = scroll_content.layout()
                
                # Create grid container
                grid_container = QtWidgets.QWidget()
                grid_container.setObjectName("gridContainer")
                  # Add to layout
                scroll_content_layout.addWidget(grid_container)
                
                # Create a flow layout instead of grid layout for better dynamic layout
                # Use spacing for nicer look and margin to better utilize container space
                flow_layout = FlowLayout(parent=grid_container, spacing=self.grid_spacing, margin=5)
                grid_container.setLayout(flow_layout)
                grid_layout = flow_layout
            
            # Add data to the grid
            if files_data and len(files_data) > 0:                
                # Add each file to the grid
                for idx, file_info in enumerate(files_data):
                    try:
                        # Get data from file info
                        filename = str(file_info.get('filename', ''))
                        extension = str(file_info.get('extension', ''))
                        filepath = str(file_info.get('filepath', ''))
                        
                        # Create a truncated name for display
                        MAX_NAME_LENGTH = 20
                        if len(filename) > MAX_NAME_LENGTH:
                            display_name = f"{filename[:MAX_NAME_LENGTH-3]}...{extension}"
                        else:
                            display_name = f"{filename}{extension}"
                        
                        # Create the image item widget
                        item_widget = self._create_image_widget(file_info)
                        
                        # Add the widget to the flow layout
                        grid_layout.addWidget(item_widget)
                        
                        # Store the widget reference
                        self.image_items.append(item_widget)
                    
                    except Exception as e:
                        exception(e, f"Error adding image {idx} to grid")
                
            else:
                # No data found - add a message
                no_data_label = QtWidgets.QLabel("No images found")
                no_data_label.setAlignment(QtCore.Qt.AlignCenter)
                grid_layout.addWidget(no_data_label)
                self.image_items.append(no_data_label)
            
            return file_count
            
        except Exception as e:
            exception(e, f"Error updating grid data for item {item_id}")
            return 0
    
    def _clear_grid(self, container):
        """
        Clear all items from the grid layout.
        
        Args:
            container: The container widget holding the grid
        """        # Find the grid layout
        grid_layout = None
        for child in container.children():
            if isinstance(child, QtWidgets.QWidget) and hasattr(child, 'layout'):
                grid_container = child
                layout_obj = grid_container.layout()
                if hasattr(grid_container, 'layout') and layout_obj is not None and (
                    isinstance(layout_obj, QtWidgets.QGridLayout) or 
                    isinstance(layout_obj, FlowLayout)
                ):
                    grid_layout = layout_obj
                    break
        
        # If we couldn't find the grid layout, try to find a container named gridContainer
        if not grid_layout:
            grid_container = container.findChild(QtWidgets.QWidget, "gridContainer")
            if grid_container and hasattr(grid_container, 'layout'):
                grid_layout = grid_container.layout()
        
        # Clear the layout if found
        if grid_layout:
            while grid_layout.count():
                item = grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()        # Clear our list of items        self.image_items.clear()
        
    def _create_image_widget(self, file_info):
        """
        Create a widget containing an image and its name.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            QWidget: Widget containing the image and name
        """
        filepath = file_info.get('filepath', '')
        filename = file_info.get('filename', '')
        extension = file_info.get('extension', '')
        
        # Create a container widget for image and filename
        container = QtWidgets.QWidget()
        
        # Set appropriate size for proper horizontal flow layout
        # Use fixed width but flexible height to allow flow layout to work
        item_width = self.image_size + 20
        item_height = self.image_size + 40  # Image height + space for text + margins
        container.setMinimumSize(item_width, item_height)
        container.setFixedWidth(item_width)  # Fixed width ensures proper horizontal flow
        
        # Use a QVBoxLayout with center alignment to ensure the label is right below the image
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        
        # Create the image label with hover effects
        image_label = QtWidgets.QLabel()
        image_label.setAlignment(QtCore.Qt.AlignCenter)
        image_label.setFixedSize(self.image_size, self.image_size)
        
        # Add hover effects with CSS styling
        image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid rgba(0, 0, 0, 0);
                border-radius: 4px;
                padding: 2px;
            }
            QLabel:hover {
                border: 2px solid rgba(88, 165, 0, 0.3);
                background-color: rgba(88, 165, 0, 0.05);
            }
        """)
        
        # Make sure the label can use hover effects
        image_label.setAttribute(QtCore.Qt.WA_Hover, True)
        
        # Change cursor to pointing hand when hovering over image
        image_label.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Load the image
        self._load_image(image_label, filepath)
        
        # Create the text label for the filename - centered below the image
        MAX_NAME_LENGTH = 20
        if len(filename) > MAX_NAME_LENGTH:
            display_name = f"{filename[:MAX_NAME_LENGTH-3]}...{extension}"
        else:
            display_name = f"{filename}{extension}"
            
        text_label = QtWidgets.QLabel(display_name)
        text_label.setAlignment(QtCore.Qt.AlignCenter)
        text_label.setWordWrap(False)  # No word wrap for image name
        text_label.setFixedWidth(self.image_size)  # Match the image width
        text_label.setStyleSheet("font-size: 9pt;")
        text_label.setToolTip(f"{filename}{extension}")
        
        # Add the widgets to the layout
        layout.addWidget(image_label)
        layout.addWidget(text_label)
        
        # Store the file info in the container's user data
        container.setProperty("file_info", file_info)
        
        # Add mouse event handling
        container.mousePressEvent = lambda event: self._handle_image_click(container, event)
        
        return container
    
    def _load_image(self, label, image_path):
        """
        Load an image from a path and display it in a label.
        
        Args:
            label (QLabel): The label to set the image on
            image_path (str): Path to the image file
        """
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
            else:
                # Use a placeholder for failed loads
                label.setText(f"Cannot load image")
                warning(f"Failed to load image: {image_path}")
                
        except Exception as e:
            label.setText("Error")
            exception(e, f"Error loading image: {image_path}")
    def _handle_image_click(self, widget, event):
        """
        Handle click events on image items.
        
        Args:
            widget (QWidget): The widget that was clicked
            event (QMouseEvent): The mouse event
        """
        try:
            # Get the file info from the widget's properties
            file_info = widget.property("file_info")
            
            if file_info:
                debug(f"Image clicked: {file_info.get('filename')} with path: {file_info.get('filepath')}")
                
                # Direct way to access the main controller
                from core.workspace_controller import WorkspaceController
                
                # Find the main window
                main_window = QtWidgets.QApplication.activeWindow()
                
                # First try: Look for WorkspaceController in the parent hierarchy
                parent = widget
                workspace_controller = None
                
                # Navigate up the widget hierarchy looking for workspace controller
                while parent:
                    if hasattr(parent, 'controller') and isinstance(parent.controller, WorkspaceController):
                        workspace_controller = parent.controller
                        debug("Found workspace controller in parent hierarchy")
                        break
                    parent = parent.parent()
                
                if workspace_controller and hasattr(workspace_controller, 'on_table_item_clicked'):
                    # Pass the file info to the workspace controller's click handler
                    debug(f"Calling on_table_item_clicked via found controller")
                    workspace_controller.on_table_item_clicked(0, 0, file_info)
                    return
                
                # Second try: Find any widget with on_table_item_clicked method
                if main_window:
                    for child in main_window.findChildren(QtWidgets.QWidget):
                        if hasattr(child, 'on_table_item_clicked'):
                            debug(f"Found widget with on_table_item_clicked method")
                            child.on_table_item_clicked(0, 0, file_info)
                            return
                    
                # Third try: Look directly for image preview widget
                image_preview = main_window.findChild(QtWidgets.QWidget, "dockWidgetContents")
                if image_preview:
                    # Look for set_image method on children
                    for child in image_preview.findChildren(QtWidgets.QWidget):
                        if hasattr(child, 'set_image'):
                            image_path = file_info.get('filepath')
                            if image_path:
                                debug(f"Setting image directly: {image_path}")
                                child.set_image(image_path)
                                return
                
                # Fourth try: Look for image preview directly
                for dock in main_window.findChildren(QtWidgets.QDockWidget):
                    if hasattr(dock, 'set_image'):
                        image_path = file_info.get('filepath')
                        if image_path:
                            debug(f"Setting image via dock widget: {image_path}")
                            dock.set_image(image_path)
                            return
                
        except Exception as e:
            exception(e, "Error handling image click")
    
    def setup_grid_click_handler(self, grid_widget, callback_function):
        """
        Set up a click handler for the grid widget items.
        
        Args:
            grid_widget: The grid widget to set up the click handler for
            callback_function: The function to call when an item is clicked
                               Should accept parameters: row, column, data_dict
        """
        if not grid_widget:
            warning("Grid widget not provided, can't set up click handler")
            return
        
        # Store the callback function to be used by _handle_image_click
        grid_widget._callback_function = callback_function