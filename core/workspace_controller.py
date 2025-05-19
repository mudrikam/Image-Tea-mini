from PySide6 import QtWidgets, QtCore, QtUiTools
from core.utils.logger import log, debug, warning, error, exception

class WorkspaceController:
    """Controller for managing the main workspace area of the application."""
    
    def __init__(self, parent_window, base_dir):
        """Initialize the workspace controller."""
        self.parent = parent_window
        self.BASE_DIR = base_dir
        self.current_item_id = None
        self.workspace_widget = None
        
        # References to UI elements
        self.tab_widget = None
        self.table_widgets = {}  # Dictionary to store table widgets for each tab: {item_id: table_widget}
        self.tab_ids = {}  # Dictionary to map tab indices to item IDs: {tab_index: item_id}
        
        # Subscribe to the explorer selection events
        from core.utils.event_system import EventSystem
        EventSystem.subscribe('explorer_item_selected', self.on_explorer_item_selected)
        EventSystem.subscribe('explorer_item_deselected', self.on_explorer_item_deselected)
        
        debug("WorkspaceController initialized and subscribed to events")
    
    def load_workspace(self, item_id=None):
        """
        Load the workspace using the main_workspace.ui file with tabs.
        If no tabs are open or item_id is None, load the drag-and-drop UI.
        """
        try:
            # If we're loading the main workspace UI for the first time or switching from DnD to tabbed
            if self.workspace_widget is None or self.tab_widget is None:
                # Load the appropriate UI file
                ui_filename = "main_workspace.ui"
                ui_path = f"{self.BASE_DIR}/gui/layout/{ui_filename}"
                
                debug(f"Loading main workspace UI: {ui_path}")
                loader = QtUiTools.QUiLoader()
                ui_file = QtCore.QFile(ui_path)
                
                if not ui_file.exists():
                    error(f"UI file not found: {ui_path}")
                    workspace_widget = self._create_fallback_widget(f"No workspace template found ({ui_filename})")
                    self.parent.setCentralWidget(workspace_widget)
                    self.workspace_widget = workspace_widget
                    return workspace_widget
                    
                ui_file.open(QtCore.QFile.ReadOnly)
                workspace_widget = loader.load(ui_file)
                ui_file.close()
                
                # Store reference to the workspace widget
                self.workspace_widget = workspace_widget
                
                # Find the tab widget
                self.tab_widget = workspace_widget.findChild(QtWidgets.QTabWidget, "tabWidget")
                
                if self.tab_widget:
                    # Enable close buttons on tabs
                    self.tab_widget.setTabsClosable(True)
                    
                    # Clear any existing tabs
                    while self.tab_widget.count() > 0:
                        self.tab_widget.removeTab(0)
                    
                    # Reset our tracking dictionaries
                    self.table_widgets = {}
                    self.tab_ids = {}
                else:
                    warning("Could not find tabWidget in main_workspace.ui")
            
            # If an item is specified, add or select a tab for it
            if item_id:
                self._add_or_select_tab_for_item(item_id)
            
            # If there are no tabs and no item_id, show the drag-and-drop UI
            if self.tab_widget and self.tab_widget.count() == 0:
                # Close the current workspace and switch to DnD UI
                return self._switch_to_dnd_ui()
            
            # Set as central widget if not already
            if self.parent.centralWidget() != self.workspace_widget:
                self.parent.setCentralWidget(self.workspace_widget)
            
            return self.workspace_widget
            
        except Exception as e:
            exception(e, "Error loading workspace")
            workspace_widget = self._create_fallback_widget(f"Error: {str(e)}")
            self.parent.setCentralWidget(workspace_widget)
            self.workspace_widget = workspace_widget
            return workspace_widget
    
    def _switch_to_dnd_ui(self):
        """Switch to the drag-and-drop UI when no tabs are open."""
        try:
            # Load the drag-and-drop UI file
            ui_path = f"{self.BASE_DIR}/gui/layout/main_workspace_dnd.ui"
            
            debug(f"Loading drag-and-drop UI: {ui_path}")
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(ui_path)
            
            if not ui_file.exists():
                error(f"UI file not found: {ui_path}")
                workspace_widget = self._create_fallback_widget("No drag-and-drop template found")
                self.parent.setCentralWidget(workspace_widget)
                self.workspace_widget = workspace_widget
                return workspace_widget
                
            ui_file.open(QtCore.QFile.ReadOnly)
            dnd_widget = loader.load(ui_file)
            ui_file.close()
            
            # Clear tab references since we're switching to DnD view
            self.tab_widget = None
            self.table_widgets = {}
            self.tab_ids = {}
            
            # Set the DnD widget as the central widget
            self.parent.setCentralWidget(dnd_widget)
            self.workspace_widget = dnd_widget
            self.current_item_id = None
            
            return dnd_widget
            
        except Exception as e:
            exception(e, "Error switching to drag-and-drop UI")
            workspace_widget = self._create_fallback_widget(f"Error: {str(e)}")
            self.parent.setCentralWidget(workspace_widget)
            self.workspace_widget = workspace_widget
            return workspace_widget
    
    def _add_or_select_tab_for_item(self, item_id):
        """Add a new tab for the item if it doesn't exist, or select it if it does."""
        if not self.tab_widget:
            warning("Tab widget not found, can't add tab")
            return
        
        # Check if a tab already exists for this item
        for idx, tab_item_id in self.tab_ids.items():
            if tab_item_id == item_id:
                # Select the existing tab
                self.tab_widget.setCurrentIndex(idx)
                self.current_item_id = item_id
                return
        
        # Create a new tab for this item
        tab_content = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(tab_content)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a table widget for this tab
        table_widget = QtWidgets.QTableWidget()
        table_widget.setAlternatingRowColors(True)
        table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        # Set up columns
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["Filename", "Extension"])
        table_widget.horizontalHeader().setStretchLastSection(True)
        
        # Add table to layout
        tab_layout.addWidget(table_widget)
        
        # Extract a shorter name for the tab
        tab_name = self._get_tab_name_from_item_id(item_id)
        
        # Add the tab
        new_tab_idx = self.tab_widget.addTab(tab_content, tab_name)
        
        # Set custom close button icon using QtAwesome
        try:
            import qtawesome as qta
            close_icon = qta.icon('fa5s.times', color='grey')  # Simple grey X icon
            
            # Create a custom close button with proper click handling
            close_button = self._create_tab_close_button(close_icon)
            
            # Add it to the tab
            tab_bar = self.tab_widget.tabBar()
            tab_bar.setTabButton(new_tab_idx, QtWidgets.QTabBar.RightSide, close_button)
        except ImportError:
            warning("QtAwesome not installed, using default close button")
        
        # Store references
        self.table_widgets[item_id] = table_widget
        self.tab_ids[new_tab_idx] = item_id
        
        # Select the new tab
        self.tab_widget.setCurrentIndex(new_tab_idx)
        self.current_item_id = item_id
        
        # Populate the tab with data
        self._update_table_data(item_id)
    
    def _get_tab_name_from_item_id(self, item_id):
        """Extract a shorter name for the tab from the item_id."""
        # Format: YYYY-MM-DD_ID_STATUS
        parts = item_id.split('_')
        if len(parts) >= 3:
            # Return "ID - STATUS"
            return f"{parts[1]} - {parts[2]}"
        elif len(parts) >= 2:
            # Return just the ID
            return parts[1]
        else:
            # Return the full ID if we can't parse it
            return item_id
    
    def close_tab(self, tab_index):
        """Close the tab at the specified index."""
        if not self.tab_widget or tab_index < 0 or tab_index >= self.tab_widget.count():
            return
        
        # Get the item ID for this tab
        item_id = self.tab_ids.get(tab_index)
        
        # Remove tab
        self.tab_widget.removeTab(tab_index)
        
        # Update our tracking dictionaries
        if item_id:
            self.table_widgets.pop(item_id, None)
        
        # Rebuild tab_ids mapping as indices have changed
        new_tab_ids = {}
        for i in range(self.tab_widget.count()):
            old_idx = next((idx for idx, tab_id in self.tab_ids.items() 
                          if self.tab_widget.widget(i) == self.tab_widget.widget(idx)), None)
            if old_idx is not None and old_idx in self.tab_ids:
                new_tab_ids[i] = self.tab_ids[old_idx]
        self.tab_ids = new_tab_ids
        
        # Update current item ID to the selected tab
        current_idx = self.tab_widget.currentIndex()
        self.current_item_id = self.tab_ids.get(current_idx)
        
        # If no tabs left, show drag-and-drop UI
        if self.tab_widget.count() == 0:
            self._switch_to_dnd_ui()
    
    def _update_table_data(self, item_id):
        """Update the table data for a specific item tab."""
        # Get the table widget for this item
        table_widget = self.table_widgets.get(item_id)
        if not table_widget:
            warning(f"Table widget not found for item {item_id}")
            return
        
        try:
            # Get the actual ID part from the item_id
            parts = item_id.split('_')
            if len(parts) < 2:
                warning(f"Invalid item ID format: {item_id}")
                return
                
            actual_id = parts[1]
            
            # Get data from the database
            try:
                from database.db_project_files import ProjectFilesModel
                files_data = ProjectFilesModel().get_files_by_item_id(actual_id)
            except Exception as e:
                exception(e, "Error getting data from database")
                files_data = []
            
            # Clear existing table data
            table_widget.setRowCount(0)
            
            # Add data to the table
            if files_data and len(files_data) > 0:
                # Set row count for the data we have
                table_widget.setRowCount(len(files_data))
                
                # Add each row of data
                for row_idx, file_info in enumerate(files_data):
                    # Get data from file info
                    filename = str(file_info.get('filename', ''))
                    extension = str(file_info.get('extension', ''))
                    
                    # Truncate long filenames for display
                    MAX_FILENAME_LENGTH = 25
                    if len(filename) > MAX_FILENAME_LENGTH:
                        # Truncate and add ellipsis
                        truncated_filename = f"{filename[:MAX_FILENAME_LENGTH-3]}..."
                    else:
                        truncated_filename = filename
                    
                    # Create table items
                    filename_item = QtWidgets.QTableWidgetItem(truncated_filename)
                    extension_item = QtWidgets.QTableWidgetItem(extension)
                    
                    # Set tooltip to show full filename when hovering
                    filename_item.setToolTip(filename + extension)
                    
                    # Set items in the table
                    table_widget.setItem(row_idx, 0, filename_item)
                    table_widget.setItem(row_idx, 1, extension_item)
                
            else:
                # No data found - add a single row with a message
                table_widget.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No files found")
                table_widget.setItem(0, 0, no_data_item)
                table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
            
            # Resize columns to content
            table_widget.resizeColumnsToContents()
            
        except Exception as e:
            exception(e, f"Error updating table data for item {item_id}")
    
    def _create_fallback_widget(self, message):
        """Create a fallback widget with an error message."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel(message)
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        return widget
    
    def _create_tab_close_button(self, icon):
        """Create a custom close button for tabs with QtAwesome icon."""
        button = QtWidgets.QToolButton()
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(12, 12))  # Small icon size
        button.setCursor(QtCore.Qt.ArrowCursor)
        button.setStyleSheet("QToolButton { border: none; padding: 0px; background: transparent; }")
        
        # Connect button click to close tab, but use a lambda to capture the button
        button.clicked.connect(lambda: self._handle_tab_close_button_clicked(button))
        return button

    def _handle_tab_close_button_clicked(self, button):
        """Handle clicks on the custom tab close button."""
        # Find which tab this button belongs to
        tab_bar = self.tab_widget.tabBar()
        for i in range(tab_bar.count()):
            if tab_bar.tabButton(i, QtWidgets.QTabBar.RightSide) == button:
                # Close this tab
                self.close_tab(i)
                break
    
    def _format_size(self, size):
        """Format file size to human readable format."""
        if not size:
            return ""
            
        if size > 1024*1024:
            return f"{size/(1024*1024):.2f} MB"
        elif size > 1024:
            return f"{size/1024:.2f} KB"
        else:
            return f"{size} bytes"
    
    def on_explorer_item_selected(self, item_id):
        """
        Handle explorer item selection event.
        Add a new tab or switch to existing tab for the selected item.
        """
        debug(f"Explorer item selected: {item_id}")
        
        # Ensure main workspace UI is loaded
        if self.workspace_widget is None or self.tab_widget is None:
            self.load_workspace(item_id)
        else:
            # Add or select tab for this item
            self._add_or_select_tab_for_item(item_id)
        
        return self.workspace_widget
    
    def on_explorer_item_deselected(self):
        """
        Handle explorer item deselection event.
        This no longer switches to the drag-drop UI immediately since we have tabs.
        """
        debug("Explorer item deselected")
        # No longer switching to drag-drop UI on deselection
        # We only switch when all tabs are closed
        return self.workspace_widget
    
    def refresh_current_workspace(self):
        """Refresh the data in the current tab."""
        if self.current_item_id:
            self._update_table_data(self.current_item_id)
        return self.workspace_widget