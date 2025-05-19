from PySide6 import QtWidgets, QtCore
from core.utils.logger import log, debug, warning, error, exception

# Import helper modules
from core.helper.workspace._ui_loader import UILoader
from core.helper.workspace._tab_manager import TabManager
from core.helper.workspace._table_manager import TableManager

class WorkspaceController:
    """Controller for managing the main workspace area of the application."""
    
    def __init__(self, parent_window, base_dir):
        """Initialize the workspace controller."""
        self.parent = parent_window
        self.BASE_DIR = base_dir
        self.current_item_id = None
        self.workspace_widget = None
        
        # Initialize helper modules
        self.ui_loader = UILoader(base_dir)
        self.tab_manager = TabManager(self)
        self.table_manager = TableManager()
        
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
        Load the workspace using the main_workspace.ui file with tabs.
        If no tabs are open or item_id is None, load the drag-and-drop UI.
        """
        try:
            # If we're loading the main workspace UI for the first time or switching from DnD to tabbed
            if self.workspace_widget is None or self.tab_widget is None:
                # Load the appropriate UI file
                workspace_widget, error_msg = self.ui_loader.load_workspace_ui("main_workspace.ui")
                
                if not workspace_widget:
                    # Use fallback widget if UI loading failed
                    workspace_widget = self.ui_loader.create_fallback_widget(error_msg)
                    self.parent.setCentralWidget(workspace_widget)
                    self.workspace_widget = workspace_widget
                    return workspace_widget
                
                # Store reference to the workspace widget
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
            
            # If an item is specified, add or select a tab for it
            if item_id:
                table_widget = self.tab_manager.add_or_select_tab(item_id)
                if table_widget:
                    # Update the table data
                    file_count = self.table_manager.update_table_data(table_widget, item_id)
                    self.tab_manager.update_tab_title(item_id, file_count)
                    self.current_item_id = item_id
            
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
            workspace_widget = self.ui_loader.create_fallback_widget(f"Error: {str(e)}")
            self.parent.setCentralWidget(workspace_widget)
            self.workspace_widget = workspace_widget
            return workspace_widget
    
    def _switch_to_dnd_ui(self):
        """Switch to the drag-and-drop UI when no tabs are open."""
        try:
            # Load the drag-and-drop UI file
            workspace_widget, error_msg = self.ui_loader.load_workspace_ui("main_workspace_dnd.ui")
            
            if not workspace_widget:
                # Use fallback widget if UI loading failed
                workspace_widget = self.ui_loader.create_fallback_widget(error_msg)
                self.parent.setCentralWidget(workspace_widget)
                self.workspace_widget = workspace_widget
                return workspace_widget
            
            # Clear tab references since we're switching to DnD view
            self.tab_widget = None
            
            # Set the DnD widget as the central widget
            self.parent.setCentralWidget(workspace_widget)
            self.workspace_widget = workspace_widget
            self.current_item_id = None
            
            return workspace_widget
            
        except Exception as e:
            exception(e, "Error switching to drag-and-drop UI")
            workspace_widget = self.ui_loader.create_fallback_widget(f"Error: {str(e)}")
            self.parent.setCentralWidget(workspace_widget)
            self.workspace_widget = workspace_widget
            return workspace_widget
    
    def on_explorer_item_selected(self, item_id):
        """
        Handle explorer item selection event.
        Add a new tab or switch to existing tab for the selected item.
        """
        # Ensure main workspace UI is loaded
        if self.workspace_widget is None or self.tab_widget is None:
            self.load_workspace(item_id)
        else:
            # Add or select tab for this item
            table_widget = self.tab_manager.add_or_select_tab(item_id)
            if table_widget:
                # Update the table data
                file_count = self.table_manager.update_table_data(table_widget, item_id)
                self.tab_manager.update_tab_title(item_id, file_count)
                self.current_item_id = item_id
        
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
            table_widget = self.tab_manager.table_widgets.get(self.current_item_id)
            if table_widget:
                file_count = self.table_manager.update_table_data(table_widget, self.current_item_id)
                self.tab_manager.update_tab_title(self.current_item_id, file_count)
        return self.workspace_widget
    
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