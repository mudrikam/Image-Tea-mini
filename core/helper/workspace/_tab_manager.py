from PySide6 import QtWidgets, QtCore, QtGui
import os
import subprocess
import platform
from core.utils.logger import log, debug, warning, error, exception
from database.db_project_files import ProjectFilesModel

class CustomTabBar(QtWidgets.QTabBar):
    """Custom QTabBar that allows closing tabs with middle-click and right-click menu."""
    
    def __init__(self, tab_manager):
        super().__init__()
        self.tab_manager = tab_manager
        
    def mousePressEvent(self, event):
        """Handle mouse press events, close tab on middle-click or show context menu on right-click."""
        if event.button() == QtCore.Qt.MiddleButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                # Log the middle-click tab closure
                tab_text = self.tabText(index)
                
                # Call the tab manager's close_tab method
                self.tab_manager.close_tab(index)
                return  # Event has been handled
                
        # Pass other events to parent class
        super().mousePressEvent(event)
    def contextMenuEvent(self, event):
        """Show context menu on right-click on tab."""
        index = self.tabAt(event.pos())
        if index >= 0:
            menu = QtWidgets.QMenu()
            
            # Add actions
            close_action = menu.addAction("Close")
            close_others_action = menu.addAction("Close Others")
            close_all_action = menu.addAction("Close All")
            
            # Connect actions to functions
            close_action.triggered.connect(lambda: self.tab_manager.close_tab(index))
            close_others_action.triggered.connect(lambda: self.tab_manager.close_other_tabs(index))
            close_all_action.triggered.connect(self.tab_manager.close_all_tabs)
            
            # Show menu
            menu.exec_(event.globalPos())

class TabManager:
    """Helper class for managing tabs in the workspace."""
    def __init__(self, parent_controller):
        """Initialize the tab manager."""
        self.controller = parent_controller
        self.tab_widget = None
        self.table_widgets = {}  # Dictionary to store table widgets for each tab: {item_id: table_widget}
        self.grid_widgets = {}   # Dictionary to store grid widgets for each tab: {item_id: grid_widget}
        self.tab_ids = {}  # Dictionary to map tab indices to item IDs: {tab_index: item_id}
        self._qt_objects = []  # Track Qt objects that need explicit deletion
    def initialize_tabs(self, tab_widget):
        """Initialize with the tab widget from the UI."""
        self.tab_widget = tab_widget
        
        if self.tab_widget:
            # Enable close buttons on tabs
            self.tab_widget.setTabsClosable(True)
            
            # Store the first tab as a template if available
            if self.tab_widget.count() > 0:
                self.template_tab = self.tab_widget.widget(0)
                
            # Clear any existing tabs
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
              # Reset tracking dictionaries
            self.table_widgets = {}
            self.tab_ids = {}
            
            # Set custom tab bar to support middle-click closing and context menu
            custom_tab_bar = CustomTabBar(self)
            self.tab_widget.setTabBar(custom_tab_bar)
            
            # Connect tab close signal
            self.tab_widget.tabCloseRequested.connect(self.close_tab)
    def add_or_select_tab(self, item_id):
        """Add a new tab for the item if it doesn't exist, or select it if it does."""
        debug(f"Tab manager add_or_select_tab called with item_id: {item_id}")
        
        if not self.tab_widget:
            warning("Tab widget not found, can't add tab")
            return None
        
        # Check if a tab already exists for this item
        debug(f"Current tab_ids: {self.tab_ids}")
        for idx, tab_item_id in self.tab_ids.items():
            if tab_item_id == item_id:
                debug(f"Found existing tab for {item_id} at index {idx}")
                # Select the existing tab
                self.tab_widget.setCurrentIndex(idx)
                return self.table_widgets.get(item_id)
        
        # We'll use the UI template to create new tabs instead of building them from scratch
        if hasattr(self, 'template_tab') and self.template_tab:
            # Clone the template tab structure
            tab_content = self._clone_template_tab()
        else:
            # Fallback if no template is available
            tab_content = self._create_default_tab_content()
        
        # Find the table widget in the new tab content
        inner_tab_widget = tab_content.findChild(QtWidgets.QTabWidget)
        table_tab = inner_tab_widget.widget(0) if inner_tab_widget else None
        table_widget = table_tab.findChild(QtWidgets.QTableWidget) if table_tab else None
        if not table_widget:
            # Fallback if we couldn't find the table widget in the cloned template
            table_widget = QtWidgets.QTableWidget()
            table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table_widget.setColumnCount(5)
            table_widget.setHorizontalHeaderLabels(["Filename", "Extension", "ID", "Status", "Filepath"])
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
        
        # Set up the grid view if available
        if inner_tab_widget and inner_tab_widget.count() > 1:
            grid_tab = inner_tab_widget.widget(1)  # Grid view is the second tab (index 1)
            
            # Check if this is a valid grid tab
            if grid_tab:
                # Load the main_workspace_grid.ui file into the grid tab
                from core.helper.workspace._ui_loader import UILoader
                ui_loader = UILoader(self.controller.BASE_DIR)
                
                # Load the grid UI file to the grid tab
                ui_loader.load_ui_to_widget("main_workspace_grid.ui", grid_tab)
                
                # Store the grid widget reference
                self.grid_widgets[item_id] = grid_tab
                
                # Set up grid click handler if controller has image preview
                if hasattr(self.controller, 'on_table_item_clicked'):
                    from core.helper.workspace._grid_manager import GridManager
                    grid_manager = GridManager()
                    # Setup is done in the update_grid_data method
                else:
                    warning(f"Could not find verticalLayoutGrid in grid_tab")
        
        # Set up table click handler if controller has image preview
        if hasattr(self.controller, 'on_table_item_clicked'):
            # Connect the click handler using TableManager
            from core.helper.workspace._table_manager import TableManager
            table_manager = TableManager()
            table_manager.setup_table_click_handler(
                table_widget, 
                self.controller.on_table_item_clicked
            )
        
        return table_widget
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
        
        # Get the new current item ID
        current_idx = self.tab_widget.currentIndex()
        current_item_id = self.tab_ids.get(current_idx)
        
        # Check if there are no tabs left and update controller
        if self.tab_widget.count() == 0:
            # If last tab was closed, notify controller to show dnd UI
            if hasattr(self.controller, 'on_last_tab_closed') and callable(self.controller.on_last_tab_closed):
                self.controller.on_last_tab_closed()
            elif hasattr(self.controller, 'layout') and hasattr(self.controller, 'dnd_widget'):
                # Direct access as fallback
                self.controller.layout.setCurrentWidget(self.controller.dnd_widget)
                
                # Clear image preview when all tabs are closed (fallback method)
                if hasattr(self.controller, 'image_preview') and self.controller.image_preview:
                    debug("Clearing image preview - all tabs closed (fallback)")
                    self.controller.image_preview.clear_preview()
        
        # Return whether tabs remain and the current item ID
        return self.tab_widget.count() > 0, current_item_id
    
    def update_tab_title(self, item_id, file_count):
        """Update the tab title with the file count."""
        for idx, tab_item_id in self.tab_ids.items():
            if tab_item_id == item_id:
                # Get the actual ID part from the item_id
                parts = item_id.split('_')
                actual_id = parts[1] if len(parts) >= 2 else item_id
                
                tab_text = f"{actual_id} ({file_count})"
                self.tab_widget.setTabText(idx, tab_text)
                break
    def _get_tab_name_from_item_id(self, item_id):
        """Extract a shorter name for the tab from the item_id."""
        debug(f"Getting tab name from item_id: {item_id}")
        
        # Handle both potential formats:
        # Format 1: YYYY-MM-DD_ID_STATUS
        # Format 2: ID_XXXX
        parts = item_id.split('_')
        
        if item_id.startswith('ID_') and len(parts) == 2:
            # Format: ID_XXXX
            id_part = parts[1]
            debug(f"Extracted ID part from ID_XXXX format: {id_part}")
        elif len(parts) >= 2:
            # Format: YYYY-MM-DD_ID_STATUS
            id_part = parts[1]
            debug(f"Extracted ID part from YYYY-MM-DD_ID_STATUS format: {id_part}")
        else:
            # Return the full ID if we can't parse it
            id_part = item_id
            debug(f"Could not parse item_id, using as is: {item_id}")
            
        # We'll add the file count later when data is loaded
        return f"{id_part} (0)"  # Default to 0 files initially
    
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
    
    def _create_default_tab_content(self):
        """Create a default tab content structure when no template is available."""
        # Create main tab content widget
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
        table_widget.setColumnCount(5)
        table_widget.setHorizontalHeaderLabels(["Filename", "Extension", "ID", "Status", "Filepath"])
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.verticalHeader().setVisible(True)
        
        # Add table to layout
        table_layout.addWidget(table_widget)
        
        # Add inner tabs
        inner_tab_widget.addTab(table_tab, "Table")
        inner_tab_widget.addTab(QtWidgets.QWidget(), "Grid")
        inner_tab_widget.addTab(QtWidgets.QWidget(), "Details")
        
        return tab_content
    
    def _create_tab_close_button(self, icon):
        """Create a custom close button for tabs with QtAwesome icon."""
        button = QtWidgets.QToolButton()
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(12, 12))  # Small icon size
        button.setCursor(QtCore.Qt.ArrowCursor)
        button.setStyleSheet("QToolButton { border: none; padding: 0px; background: transparent; }")
        
        # Store the button in our tracked objects list
        self._qt_objects.append(button)
        
        # Connect button click to tab close handler
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
            warning(f"Error closing tab: {e}")
    def get_current_item_id(self):
        """Get the current selected item ID."""
        if not self.tab_widget:
            return None
        
        current_index = self.tab_widget.currentIndex()
        return self.tab_ids.get(current_index)
    
    def close_other_tabs(self, keep_index):
        """Close all tabs except the one at keep_index."""
        if not self.tab_widget or keep_index < 0 or keep_index >= self.tab_widget.count():
            return
            
        # Get the tab we want to keep
        keep_widget = self.tab_widget.widget(keep_index)
        keep_id = self.tab_ids.get(keep_index)
        
        # Remove all other tabs in reverse order to avoid index issues
        for i in range(self.tab_widget.count() - 1, -1, -1):
            if i != keep_index:
                # Close the tab
                self.close_tab(i)
                
        # Make sure our indices are correct after closing tabs
        self.tab_ids = {0: keep_id}
          # Select the remaining tab
        self.tab_widget.setCurrentIndex(0)
        
    def close_all_tabs(self):
        """Close all tabs."""
        # Remove all tabs in reverse order to avoid index issues
        for i in range(self.tab_widget.count() - 1, -1, -1):
            self.close_tab(i)    # Reveal in Explorer functionality has been removed
    def cleanup(self):
        """Clean up resources when the manager is no longer needed."""
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
          # Clean up table widgets
        for item_id in list(self.table_widgets.keys()):
            try:
                table = self.table_widgets[item_id]
                if table:
                    table.setModel(None)
                    table.deleteLater()
            except:
                pass
                
        # Clean up grid widgets
        for item_id in list(self.grid_widgets.keys()):
            try:
                grid = self.grid_widgets[item_id]
                if grid:
                    grid.deleteLater()
            except:
                pass
        
        # Clear dictionaries
        self.table_widgets.clear()
        self.grid_widgets.clear()
        self.tab_ids.clear()
