from PySide6 import QtCore, QtUiTools
from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidget, QLineEdit, QLabel, QPushButton
from PySide6.QtGui import QAction  # Fixed import - QAction is in QtGui, not QtWidgets
import qtawesome as qta
from core.utils.logger import log, debug, warning, error, exception
from core.utils.event_system import EventSystem

class UIHelper:
    """Helper class for managing UI components and events for explorer widget."""
    
    def __init__(self, base_dir=None):
        """Initialize the UI helper."""
        self.BASE_DIR = base_dir
    
    def load_ui(self):
        """Load the explorer widget from UI file."""
        try:
            # Load UI file
            ui_path = f"{self.BASE_DIR}/gui/widgets/explorer/explorer_widget.ui"
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(ui_path)
            
            if not ui_file.exists():
                error(f"UI file not found: {ui_path}")
                return None, {}
                
            ui_file.open(QtCore.QFile.ReadOnly)
            widget = loader.load(ui_file)
            ui_file.close()
            
            # Find UI components
            components = {
                'tree': widget.findChild(QTreeWidget, "treeWidget"),
                'search_field': widget.findChild(QLineEdit, "searchField"),
                'search_icon': widget.findChild(QLabel, "searchIcon"),
                'expand_all_btn': widget.findChild(QPushButton, "expandAllButton"),
                'collapse_all_btn': widget.findChild(QPushButton, "collapseAllButton"),
                'clear_search_btn': widget.findChild(QPushButton, "clearSearchButton")
            }
            
            # Set icons for UI components
            self.set_icons(components)
            
            return widget, components
            
        except Exception as e:
            exception(e, "Error loading explorer UI")
            return None, {}
    
    def set_icons(self, components):
        """Set icons for UI components."""
        try:
            # Set search icon
            search_icon = components.get('search_icon')
            if search_icon:
                search_icon.setPixmap(qta.icon('fa5s.search').pixmap(16, 16))
            
            # Set expand all button icon
            expand_all_btn = components.get('expand_all_btn')
            if expand_all_btn:
                expand_all_btn.setIcon(qta.icon('fa5s.expand-arrows-alt'))
            
            # Set collapse all button icon
            collapse_all_btn = components.get('collapse_all_btn')
            if collapse_all_btn:
                collapse_all_btn.setIcon(qta.icon('fa5s.compress-arrows-alt'))
            
            # Set clear search button icon
            clear_search_btn = components.get('clear_search_btn')
            if clear_search_btn:
                clear_search_btn.setIcon(qta.icon('fa5s.times-circle'))
                
        except Exception as e:
            warning(f"Could not set icons for explorer: {e}")
    
    def connect_tree_signals(self, tree_widget, item_click_handler):
        """Connect tree widget signals to handlers."""
        if not tree_widget:
            warning("Cannot connect signals - tree widget is None")
            return False
            
        try:
            # Connect item click signal to handler
            tree_widget.itemClicked.connect(item_click_handler)
            return True
        except Exception as e:
            error(f"Failed to connect tree click handler: {str(e)}")
            return False
    
    def handle_item_clicked(self, item, column, tree_widget):
        """Handle click events on tree items."""
        # Get the full path of the clicked item (text of all parent items)
        path = []
        temp_item = item
        while temp_item is not None:
            path.insert(0, temp_item.text(0))
            temp_item = temp_item.parent()
        
        path_str = " > ".join(path)
        
        # Check if the clicked item is an ID item (level 4 - has 3 parent levels)
        parents = 0
        temp_item = item.parent()
        while temp_item is not None:
            parents += 1
            temp_item = temp_item.parent()
        
        if parents == 3:  # It's an ID item (year > month > day > ID)
            # Parse the ID from the text (format: YYYY-MM-DD_ID_STATUS)
            item_text = item.text(0)
            try:
                parts = item_text.split('_')
                if len(parts) >= 2:
                    id_value = parts[1]
                    status = parts[2] if len(parts) > 2 else "unknown"
                    
                    # Log the selection
                    log(f"Selected ID: {id_value} (Status: {status}) - Path: {path_str}")
                    
                    # Notify the layout controller to update the workspace
                    EventSystem.publish('explorer_item_selected', item_text)
                    
            except Exception as e:
                debug(f"Error parsing ID item: {e}")
        else:
            # It's not an ID item, log with level name
            level_name = "Year" if parents == 0 else "Month" if parents == 1 else "Day" if parents == 2 else "Unknown"
            
            # Log with the proper logger
            log(f"Selected {level_name}: {item.text(0)} - Path: {path_str}")
            
            # Publish deselection event
            EventSystem.publish('explorer_item_deselected')
        
        # Force process events to update UI immediately
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
