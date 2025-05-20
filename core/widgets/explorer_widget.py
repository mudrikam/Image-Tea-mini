from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLineEdit
from core.utils.logger import log, debug, warning, error, exception
from core.utils.event_system import EventSystem
import time

# Import helper modules
from core.helper.explorer._data_manager import DataManager
from core.helper.explorer._tree_loader import TreeLoader
from core.helper.explorer._search_handler import SearchHandler
from core.helper.explorer._ui_helper import UIHelper

class ExplorerWidget:
    def __init__(self, base_dir=None):
        """Initialize the explorer widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.tree = None
        
        # Initialize helper modules
        self.data_manager = DataManager(base_dir)
        self.ui_helper = UIHelper(base_dir)
        
        # These will be initialized after loading UI
        self.tree_loader = None
        self.search_handler = None
        
        # For debounced refresh handling
        self._debounced_refresh_timer = None
        
        # Subscribe to the project_data_changed event
        EventSystem.subscribe('project_data_changed', self.on_project_data_changed)
        
    def on_project_data_changed(self):
        """Called when project data changes in the database."""
        if self.tree:
            log("Project data changed. Scheduling explorer view refresh.")
            # Invalidate cache when data changes
            self.data_manager.invalidate_cache()
            # Use debounced refresh instead of immediate refresh
            self.debounced_refresh_data()

    def load_ui(self):
        """Load the explorer widget from UI file."""
        # Load UI using the UI helper
        self.widget, components = self.ui_helper.load_ui()
        
        if not self.widget:
            error("Failed to load explorer UI")
            return None
        
        # Get tree widget
        self.tree = components.get('tree')
        if not self.tree:
            error("Tree widget not found in explorer UI")
            return self.widget
        
        # Initialize tree loader with the tree widget
        self.tree_loader = TreeLoader(self.tree)
        
        # Initialize search handler with the tree widget
        self.search_handler = SearchHandler(self.tree)
        search_field = components.get('search_field')
        if search_field:
            self.search_handler.set_search_field(search_field)
        
        # Connect expand/collapse buttons
        expand_all_btn = components.get('expand_all_btn')
        if expand_all_btn:
            expand_all_btn.clicked.connect(self.tree_loader.expand_all)
        
        collapse_all_btn = components.get('collapse_all_btn')
        if collapse_all_btn:
            collapse_all_btn.clicked.connect(self.tree_loader.collapse_all_except_years)
        # Connect clear search button
        clear_search_btn = components.get('clear_search_btn')
        if clear_search_btn:
            clear_search_btn.clicked.connect(self.clear_search)
        
        # Connect refresh button
        refresh_btn = components.get('refresh_btn')
        if refresh_btn:
            refresh_btn.clicked.connect(self.refresh_data)
        
        # Connect item click handler
        self.ui_helper.connect_tree_signals(
            self.tree,
            lambda item, col: self.ui_helper.handle_item_clicked(item, col, self.tree)
        )
        
        # Load data from the database
        if not self.load_data_from_database():
            # Create an empty item if no data found
            self.tree_loader.create_empty_tree("No data available")
        
        return self.widget
    
    def clear_search(self):
        """Clear the search field and reset the tree view."""
        if self.search_handler:
            self.search_handler.clear_search()

    def refresh_data(self):
        """Reload project data from the database and refresh the tree."""
        start_time = time.time()
        log("Refreshing explorer data...")
        
        # Clear any active search
        if self.search_handler:
            self.search_handler.clear_search()
        
        # Refresh data
        success = self.load_data_from_database(force_refresh=True)
        
        if success:
            # Track time for performance monitoring
            elapsed = time.time() - start_time
            log(f"Explorer data refreshed successfully in {elapsed:.3f} seconds.")
        else:
            warning("Failed to refresh explorer data.")
        
        # Process events to update UI immediately
        QApplication.processEvents()

    def debounced_refresh_data(self, delay=500):
        """
        Debounce refresh calls to prevent multiple rapid refreshes.
        
        Args:
            delay (int): Delay in milliseconds before refresh happens
        """
        # Cancel any existing timer
        if self._debounced_refresh_timer is not None:
            self._debounced_refresh_timer.stop()
            
        # Create a new timer
        self._debounced_refresh_timer = QTimer()
        self._debounced_refresh_timer.setSingleShot(True)
        self._debounced_refresh_timer.timeout.connect(self.refresh_data)
        self._debounced_refresh_timer.start(delay)  # milliseconds

    def load_data_from_database(self, force_refresh=False):
        """Load project data from the database and update the tree."""
        try:
            # Save expanded state if tree already has data
            expanded_states = {}
            if self.tree_loader and self.tree.topLevelItemCount() > 0:
                expanded_states = self.tree_loader.save_expanded_states()
            
            # Load data from database using data manager
            project_data, success = self.data_manager.load_data_from_database(force_refresh)
            
            if not success:
                return False
            
            # Load the data into the tree using the tree loader
            return self.tree_loader.load_project_data(project_data, expanded_states)
                
        except Exception as e:
            exception(e, "Error loading data from database")
            return False

    def update_item_status(self, item_id, new_status):
        """Update an item's status in the database and refresh the UI."""
        if self.data_manager.update_item_status(item_id, new_status):
            # Refresh the tree to show updated data
            self.load_data_from_database(force_refresh=True)
            return True
        return False
        
    def add_new_item(self, year, month, day, item_id, status="draft"):
        """Add a new item to the database and refresh the UI."""
        if self.data_manager.add_new_item(year, month, day, item_id, status):
            # Refresh the tree to show the new item
            self.load_data_from_database(force_refresh=True)
            return True
        return False

    def __del__(self):
        """Clean up event subscriptions when the widget is destroyed."""
        try:
            EventSystem.unsubscribe('project_data_changed', self.on_project_data_changed)
        except:
            pass