from PySide6 import QtWidgets, QtCore
from core.utils.logger import log, debug, warning, error, exception

# Import helper modules
from core.helper.workspace._ui_loader import UILoader
from core.helper.workspace._tab_manager import TabManager
from core.helper.workspace._table_manager import TableManager
from core.helper.workspace._dnd_handler import DropAreaHandler

class WorkspaceController:
    """Controller for managing the main workspace area of the application."""
    def __init__(self, parent_window, base_dir):
        """Initialize the workspace controller."""
        self.parent = parent_window
        self.BASE_DIR = base_dir
        self.current_item_id = None
        self.workspace_widget = None
        self.dnd_widget = None
        self.layout = None
        self.container = None
        
        # Initialize helper modules
        self.ui_loader = UILoader(base_dir)
        self.tab_manager = TabManager(self)
        self.table_manager = TableManager()
        self.dnd_handler = DropAreaHandler(self)
        
        # References to UI elements
        self.tab_widget = None
        self.inner_tab_widget = None
        self.inner_table_widget = None
        
        # Subscribe to the explorer selection events using weak references
        from core.utils.event_system import EventSystem
        EventSystem.subscribe('explorer_item_selected', self.on_explorer_item_selected, weak=True)
        EventSystem.subscribe('explorer_item_deselected', self.on_explorer_item_deselected, weak=True)
        
        # Set thread timeout to minimize thread issues
        QtCore.QThreadPool.globalInstance().setExpiryTimeout(1000)  # 1 second thread expiry
    
    def load_workspace(self, item_id=None):
        """
        Load both workspace UIs (tabbed and drag-and-drop) and switch between them as needed.
        """
        try:
            # Create a container widget and QStackedLayout if not already done
            if self.container is None:
                self.container = QtWidgets.QWidget()
                self.layout = QtWidgets.QStackedLayout(self.container)
                self.parent.setCentralWidget(self.container)
            
            # Initialize the workspace UI if not already done
            if self.workspace_widget is None:
                workspace_widget, error_msg = self.ui_loader.load_workspace_ui("main_workspace.ui")
                if not workspace_widget:
                    workspace_widget = self.ui_loader.create_fallback_widget(error_msg)
                
                self.workspace_widget = workspace_widget
                
                # Find UI components
                components = self.ui_loader.find_ui_components(workspace_widget)
                self.tab_widget = components.get('tab_widget')
                self.inner_tab_widget = components.get('inner_tab_widget')
                self.inner_table_widget = components.get('inner_table_widget')
                
                # Initialize the tab manager with the tab widget
                if self.tab_widget:
                    self.tab_manager.initialize_tabs(self.tab_widget)
                else:
                    warning("Could not find tabWidget in main_workspace.ui")
                
                # Add to QStackedLayout
                self.layout.addWidget(self.workspace_widget)
            
            # Initialize the drag-and-drop UI if not already done            if self.dnd_widget is None:
                dnd_widget, error_msg = self.ui_loader.load_workspace_ui("main_workspace_dnd.ui")
                if not dnd_widget:
                    dnd_widget = self.ui_loader.create_fallback_widget(error_msg)
                
                self.dnd_widget = dnd_widget
                
                # Set up the drag and drop handler for the drop area
                drop_area = self.dnd_widget.findChild(QtWidgets.QFrame, "dropArea")
                if drop_area:
                    self.dnd_handler.setup_drop_area(drop_area)
                else:
                    warning("Could not find dropArea in main_workspace_dnd.ui")
                
                # Add to QStackedLayout
                self.layout.addWidget(self.dnd_widget)
            
            # If an item is specified, add or select a tab for it
            if item_id:
                debug(f"Adding or selecting tab for item: {item_id}")
                table_widget = self.tab_manager.add_or_select_tab(item_id)
                if table_widget:
                    # Update the table data
                    file_count = self.table_manager.update_table_data(table_widget, item_id)
                    self.tab_manager.update_tab_title(item_id, file_count)
                    self.current_item_id = item_id
            
            # Show the appropriate UI based on whether there are tabs
            if self.tab_widget and self.tab_widget.count() > 0:
                debug(f"Showing workspace UI with {self.tab_widget.count()} tabs")
                self.layout.setCurrentWidget(self.workspace_widget)
            else:
                self.layout.setCurrentWidget(self.dnd_widget)
            
            return self.workspace_widget
            
        except Exception as e:
            exception(e, "Error loading workspace")
            fallback_widget = self.ui_loader.create_fallback_widget(f"Error: {str(e)}")
            if self.layout:
                self.layout.addWidget(fallback_widget)
                self.layout.setCurrentWidget(fallback_widget)
            else:
                self.parent.setCentralWidget(fallback_widget)
            return fallback_widget
    def on_explorer_item_selected(self, item_id):
        """
        Handle explorer item selection event.
        Add a new tab or switch to existing tab for the selected item.
        """
        debug(f"WorkspaceController on_explorer_item_selected called with item_id: {item_id}")
        
        # Ensure both workspace UIs are loaded
        if self.workspace_widget is None or self.dnd_widget is None:
            debug("Loading workspace UIs on first item selection")
            self.load_workspace(item_id)
        else:
            # Add or select tab for this item
            debug(f"Calling tab_manager.add_or_select_tab with item_id: {item_id}")
            table_widget = self.tab_manager.add_or_select_tab(item_id)
            
            if table_widget:
                debug(f"Got table_widget, updating data for item_id: {item_id}")
                # Update the table data
                file_count = self.table_manager.update_table_data(table_widget, item_id)
                self.tab_manager.update_tab_title(item_id, file_count)
                self.current_item_id = item_id
                debug(f"Updated tab title with file count: {file_count}")
            else:
                warning(f"Failed to get table_widget for item_id: {item_id}")
            
            # Show the workspace UI with tabs
            if self.layout:
                debug("Setting workspace widget as current in layout")
                self.layout.setCurrentWidget(self.workspace_widget)
            else:
                warning("Layout is not available to set workspace widget as current")
        
        return self.workspace_widget
    def on_explorer_item_deselected(self):
        """
        Handle explorer item deselection event.
        This no longer switches to the drag-drop UI immediately since we have tabs.
        """
        
        # If there are no tabs open, make sure to clear the image preview
        if self.tab_widget and self.tab_widget.count() == 0:
            if hasattr(self, 'image_preview') and self.image_preview:
                self.image_preview.clear_preview()
        
        # No longer switching to drag-drop UI on deselection
        # We only switch when all tabs are closed
        return self.workspace_widget
    
    def refresh_current_workspace(self):
        """Refresh the data in the current tab."""
        if self.current_item_id:
            table_widget = self.tab_manager.table_widgets.get(self.current_item_id)
            if table_widget:
                file_count = self.table_manager.update_table_data(table_widget, self.current_item_id)
                self.tab_manager.update_tab_title(self.current_item_id, file_count)
        return self.workspace_widget
    def on_last_tab_closed(self):
        """
        Handle the event when last tab is closed.
        Show the drag-and-drop UI and clear image preview.
        """
        
        # Make sure both UIs are loaded
        if self.dnd_widget is None:
            debug("Loading workspace UIs because DnD widget is not initialized")
            self.load_workspace()
            return self.workspace_widget
        
        # Show the drag-and-drop UI
        if self.layout:
            self.layout.setCurrentWidget(self.dnd_widget)
              # Reset image preview when closing all tabs
            if hasattr(self, 'image_preview') and self.image_preview:
                self.image_preview.clear_preview()
                
                # Ensure the preview is truly reset by forcing a UI update
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()
        else:
            warning("QStackedLayout is not initialized when trying to show DnD UI")
            
        return self.dnd_widget
    def _switch_to_dnd_ui(self):
        """Show the drag-and-drop UI by using QStackedLayout."""
        try:
            debug("Switching to drag-and-drop UI")
            # Just change the current widget in the stacked layout
            if self.layout and self.dnd_widget:
                self.layout.setCurrentWidget(self.dnd_widget)
                self.current_item_id = None
                  # Reset image preview when switching to drag-and-drop UI
                if hasattr(self, 'image_preview') and self.image_preview:
                    self.image_preview.clear_preview()
                    
                    # Ensure the preview is truly reset by forcing a UI update
                    from PySide6.QtWidgets import QApplication
                    QApplication.processEvents()
                
                return self.dnd_widget
            else:
                # If for some reason we don't have the layout or dnd_widget yet, load it
                debug("DnD UI not initialized yet, loading it")
                self.load_workspace()
                if self.layout and self.dnd_widget:
                    self.layout.setCurrentWidget(self.dnd_widget)
                    
                    # Reset image preview here too
                    if hasattr(self, 'image_preview') and self.image_preview:
                        self.image_preview.clear_preview()
                    
                    return self.dnd_widget
                else:
                    error("Failed to initialize drag-and-drop UI")
                    return None
                
        except Exception as e:
            exception(e, "Error switching to drag-and-drop UI")
            return None
    
    def connect_to_image_preview(self, image_preview):
        """
        Connect the workspace to the image preview widget so selected items can be previewed.
        
        Args:
            image_preview: An instance of ImagePreviewWidget
        """
        self.image_preview = image_preview
        
    def on_table_item_clicked(self, row, column, data):
        """
        Handle when an item in a table is clicked.
        Update the image preview if available.
        
        Args:
            row: The row index
            column: The column index
            data: The data associated with the item (dict from table data)
        """
        if not hasattr(self, 'image_preview') or not self.image_preview:
            debug("No image preview widget available")
            return
            
        
        try:
            if isinstance(data, dict):
                # Try to get the file ID from the data
                file_id = data.get('id')
                
                if file_id:
                    self.image_preview.update_preview_from_database(id=file_id)
                else:
                    debug("No file ID found in table item data")
        except Exception as e:
            exception(e, "Error updating image preview from table selection")
    
    def __del__(self):
        """Clean up resources when the controller is deleted."""
        try:
            # Unsubscribe from events
            from core.utils.event_system import EventSystem
            EventSystem.unsubscribe('explorer_item_selected', self.on_explorer_item_selected)
            EventSystem.unsubscribe('explorer_item_deselected', self.on_explorer_item_deselected)
            
            # Clean up the tab manager
            if hasattr(self, 'tab_manager'):
                self.tab_manager.cleanup()
            
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