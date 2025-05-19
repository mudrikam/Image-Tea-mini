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
        self.inner_tab_widget = None  # Add reference to the nested tab widget
        self.inner_table_widget = None  # Add reference to the table inside nested tabs
        self.table_widgets = {}  # Dictionary to store table widgets for each tab: {item_id: table_widget}
        self.tab_ids = {}  # Dictionary to map tab indices to item IDs: {tab_index: item_id}
        
        # Keep track of QtCore.QObject objects that need to be explicitly deleted
        self._qt_objects = []
        
        # Subscribe to the explorer selection events using weak references
        from core.utils.event_system import EventSystem
        EventSystem.subscribe('explorer_item_selected', self.on_explorer_item_selected, weak=True)
        EventSystem.subscribe('explorer_item_deselected', self.on_explorer_item_deselected, weak=True)
        
        # Set thread timeout to minimize thread issues
        QtCore.QThreadPool.globalInstance().setExpiryTimeout(1000)  # 1 second thread expiry
        
        # debug("WorkspaceController initialized and subscribed to events")
    
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
                
                # debug(f"Loading main workspace UI: {ui_path}")
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
                    # Find the nested tab widget and table
                    self.inner_tab_widget = self.tab_widget.findChild(QtWidgets.QTabWidget, "tabWidget_2")
                    
                    if self.inner_tab_widget:
                        # Find the table widget inside the inner tab
                        self.inner_table_widget = self.inner_tab_widget.findChild(QtWidgets.QTableWidget, "tableWidget")
                    
                    # Enable close buttons on tabs
                    self.tab_widget.setTabsClosable(True)
                    
                    # Store the first tab as a template
                    if self.tab_widget.count() > 0:
                        self.template_tab = self.tab_widget.widget(0)
                        
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
            
            # debug(f"Loading drag-and-drop UI: {ui_path}")
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
        
        # We'll use the UI template to create new tabs instead of building them from scratch
        if hasattr(self, 'template_tab') and self.template_tab:
            # Clone the template tab structure
            tab_content = self._clone_template_tab()
        else:
            # Fallback if no template is available
            tab_content = QtWidgets.QWidget()
            tab_layout = QtWidgets.QVBoxLayout(tab_content)
            tab_layout.setContentsMargins(0, 5, 0, 0)
            
            # Create nested tab widget
            inner_tab_widget = QtWidgets.QTabWidget()
            tab_layout.addWidget(inner_tab_widget)
            
            # Create table view tab
            table_tab = QtWidgets.QWidget()
            table_layout = QtWidgets.QVBoxLayout(table_tab)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create table
            table_widget = QtWidgets.QTableWidget()
            table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table_widget.setColumnCount(2)
            table_widget.setHorizontalHeaderLabels(["Filename", "Extension"])
            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.verticalHeader().setVisible(True)
            
            # Add table to layout
            table_layout.addWidget(table_widget)
            
            # Add inner tabs
            inner_tab_widget.addTab(table_tab, "Table")
            inner_tab_widget.addTab(QtWidgets.QWidget(), "Grid")
            inner_tab_widget.addTab(QtWidgets.QWidget(), "Details")
        
        # Find the table widget in the new tab content
        inner_tab_widget = tab_content.findChild(QtWidgets.QTabWidget)
        table_tab = inner_tab_widget.widget(0) if inner_tab_widget else None
        table_widget = table_tab.findChild(QtWidgets.QTableWidget) if table_tab else None
        
        if not table_widget:
            # Fallback if we couldn't find the table widget in the cloned template
            table_widget = QtWidgets.QTableWidget()
            table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table_widget.setColumnCount(2)
            table_widget.setHorizontalHeaderLabels(["Filename", "Extension"])
            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.verticalHeader().setVisible(True)
            
        # Extract a shorter name for the tab
        tab_name = self._get_tab_name_from_item_id(item_id)
        
        # Add the main tab
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
    
    def _clone_template_tab(self):
        """Clone the template tab structure to create a new tab with the same layout."""
        # Create a new widget as the base for our cloned tab
        cloned_widget = QtWidgets.QWidget()
        cloned_layout = QtWidgets.QVBoxLayout(cloned_widget)
        cloned_layout.setContentsMargins(0, 5, 0, 0)
        
        # Find the inner tab widget in the template
        template_inner_tab = self.template_tab.findChild(QtWidgets.QTabWidget)
        
        if template_inner_tab:
            # Create a new tab widget for our clone
            new_inner_tab = QtWidgets.QTabWidget()
            cloned_layout.addWidget(new_inner_tab)
            
            # Clone each tab from the template
            for i in range(template_inner_tab.count()):
                tab_name = template_inner_tab.tabText(i)
                template_tab_page = template_inner_tab.widget(i)
                
                # Create a new widget for this inner tab
                new_tab_page = QtWidgets.QWidget()
                new_tab_layout = QtWidgets.QVBoxLayout(new_tab_page)
                new_tab_layout.setContentsMargins(0, 0, 0, 0)
                
                # If this is the table tab, create a table widget
                if i == 0:  # Assuming first tab is always the table tab
                    template_table = template_tab_page.findChild(QtWidgets.QTableWidget)
                    if template_table:
                        new_table = QtWidgets.QTableWidget()
                        
                        # Copy properties from the template table
                        new_table.setSelectionBehavior(template_table.selectionBehavior())
                        new_table.setColumnCount(template_table.columnCount())
                        
                        # Set header labels
                        headers = []
                        for col in range(template_table.columnCount()):
                            headers.append(template_table.horizontalHeaderItem(col).text())
                        new_table.setHorizontalHeaderLabels(headers)
                        
                        # Copy more properties
                        new_table.horizontalHeader().setStretchLastSection(
                            template_table.horizontalHeader().stretchLastSection())
                        new_table.verticalHeader().setVisible(
                            template_table.verticalHeader().isVisible())
                        
                        # Add the table to the tab layout
                        new_tab_layout.addWidget(new_table)
                
                # Add the new tab page to the inner tab widget
                new_inner_tab.addTab(new_tab_page, tab_name)
        
        return cloned_widget

    def _get_tab_name_from_item_id(self, item_id):
        """Extract a shorter name for the tab from the item_id."""
        # Format: YYYY-MM-DD_ID_STATUS
        parts = item_id.split('_')
        if len(parts) >= 2:
            # Get the ID part
            id_part = parts[1]
            # We'll add the file count later when data is loaded
            return f"{id_part} (0)"  # Default to 0 files initially
        else:
            # Return the full ID if we can't parse it
            return f"{item_id} (0)"
    
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
            
            # Make sure vertical header (row numbers) is visible
            table_widget.verticalHeader().setVisible(True)
            
            # Clear existing table data
            table_widget.setRowCount(0)
            
            # Get the number of files
            file_count = len(files_data) if files_data else 0
            
            # Update the tab text with file count
            for idx, tab_item_id in self.tab_ids.items():
                if tab_item_id == item_id:
                    tab_text = f"{actual_id} ({file_count})"
                    self.tab_widget.setTabText(idx, tab_text)
                    break
            
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
                    filename_item.setToolTip(filename)
                    
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
        
        # Store the button in our tracked objects list
        self._qt_objects.append(button)
        
        # Use a direct connection approach with a simple lambda that captures the button
        # This avoids the QMetaObject.invokeMethod complexity that's causing issues
        button.clicked.connect(lambda: self._close_tab_for_button(button))
        return button

    def _close_tab_for_button(self, button):
        """Find and close the tab associated with this button."""
        try:
            if self.tab_widget:
                tab_bar = self.tab_widget.tabBar()
                for i in range(tab_bar.count()):
                    if tab_bar.tabButton(i, QtWidgets.QTabBar.RightSide) == button:
                        # Close this tab
                        self.close_tab(i)
                        break
        except Exception as e:
            warning(f"Error closing tab: {e}")  # Use warning instead of print
    
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
        # debug(f"Explorer item selected: {item_id}")
        
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
    
    def __del__(self):
        """Clean up resources when the controller is deleted."""
        try:
            # Unsubscribe from events
            from core.utils.event_system import EventSystem
            EventSystem.unsubscribe('explorer_item_selected', self.on_explorer_item_selected)
            EventSystem.unsubscribe('explorer_item_deselected', self.on_explorer_item_deselected)
            
            # Explicitly clean up Qt objects to avoid thread storage issues
            for obj in self._qt_objects:
                try:
                    # Disconnect all signals from this object
                    if hasattr(obj, 'disconnect'):
                        obj.disconnect()
                    
                    # Delete the object
                    obj.deleteLater()
                except:
                    pass
            
            # Clear references
            self._qt_objects.clear()
            
            # Clear table widgets
            for item_id in list(self.table_widgets.keys()):
                try:
                    table = self.table_widgets[item_id]
                    if table:
                        table.setModel(None)
                        table.deleteLater()
                except:
                    pass
            
            # Clear dictionaries
            self.table_widgets.clear()
            self.tab_ids.clear()
            
            # Clear other references
            self.tab_widget = None
            self.workspace_widget = None
            self.current_item_id = None
            
            # Force garbage collection
            import gc
            gc.collect()
        
        except Exception as e:
            # Use logger instead of print
            log(f"Error during WorkspaceController cleanup: {e}")