from PySide6 import QtCore, QtUiTools
from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidget, QLineEdit, QLabel, QPushButton
from PySide6.QtGui import QAction, QCursor  # Added QCursor import
from PySide6.QtCore import Qt, QObject, QEvent
import qtawesome as qta
from core.utils.logger import log, debug, warning, error, exception
from core.utils.event_system import EventSystem

class TreeItemHoverFilter(QObject):
    """Event filter for handling hover events over tree items."""
    
    def __init__(self, tree_widget):
        super().__init__(tree_widget)
        self.tree = tree_widget
        self.last_item = None    
    def eventFilter(self, obj, event):
        """Filter events to handle mouse hover."""
        if obj == self.tree:
            if event.type() == QEvent.HoverMove:
                # Get item at current position
                pos = event.pos()
                item = self.tree.itemAt(pos)
                
                if item:
                    # Check item data
                    cursor_data = item.data(0, Qt.UserRole)
                    
                    if item and item != self.last_item:
                        # Check if item has pointing cursor data
                        if cursor_data == "pointing_hand_cursor":
                            self.tree.setCursor(QCursor(Qt.PointingHandCursor))
                        else:
                            self.tree.setCursor(QCursor(Qt.ArrowCursor))
                        self.last_item = item
                elif not item and self.last_item:
                    self.tree.setCursor(QCursor(Qt.ArrowCursor))
                    self.last_item = None
            
            elif event.type() == QEvent.Leave:
                # Reset cursor when mouse leaves the widget
                self.tree.setCursor(QCursor(Qt.ArrowCursor))
                self.last_item = None
        
        # Always allow event to be processed
        return False

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
                'refresh_btn': widget.findChild(QPushButton, "refreshButton"),
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
            # Import QCursor and Qt here to prevent circular imports
            from PySide6.QtGui import QCursor
            from PySide6.QtCore import Qt
            
            # Set search icon
            search_icon = components.get('search_icon')
            if search_icon:
                search_icon.setPixmap(qta.icon('fa5s.search').pixmap(16, 16))
            
            # Set expand all button icon and cursor
            expand_all_btn = components.get('expand_all_btn')
            if expand_all_btn:
                expand_all_btn.setIcon(qta.icon('fa5s.expand-arrows-alt'))
                expand_all_btn.setCursor(QCursor(Qt.PointingHandCursor))
                
            # Set collapse all button icon and cursor
            collapse_all_btn = components.get('collapse_all_btn')
            if collapse_all_btn:
                collapse_all_btn.setIcon(qta.icon('fa5s.compress-arrows-alt'))
                collapse_all_btn.setCursor(QCursor(Qt.PointingHandCursor))
            
            # Set refresh button icon and cursor
            refresh_btn = components.get('refresh_btn')
            if refresh_btn:
                refresh_btn.setIcon(qta.icon('fa5s.sync-alt'))
                refresh_btn.setCursor(QCursor(Qt.PointingHandCursor))
            
            # Set clear search button icon and cursor
            clear_search_btn = components.get('clear_search_btn')
            if clear_search_btn:
                clear_search_btn.setIcon(qta.icon('fa5s.times-circle'))
                clear_search_btn.setCursor(QCursor(Qt.PointingHandCursor))
                
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
            
            # Install hover event filter for cursor changing
            tree_widget.setMouseTracking(True)
            
            # Create and install the hover event filter
            hover_filter = TreeItemHoverFilter(tree_widget)
            tree_widget.installEventFilter(hover_filter)
            
            # Enable hover events explicitly
            tree_widget.setAttribute(Qt.WA_Hover, True)
            
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
