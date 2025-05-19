from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSizePolicy, QPushButton, QHBoxLayout
from PySide6 import QtUiTools, QtCore
from PySide6.QtGui import QColor, QBrush, QFont
import qtawesome as qta  # Import qtawesome for icons
from database import db_explorer_widget
from core.utils.logger import log, debug, warning, error, exception
from core.utils.event_system import EventSystem
import time
import datetime

class ExplorerWidget:
    def __init__(self, base_dir=None):
        """Initialize the explorer widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.tree = None
        
        # Add cache for loaded data to speed up refreshes
        self._data_cache = None
        self._last_load_time = 0
        self._cache_valid = False
        
        # Store references to hierarchical data for future implementation
        self.years = {}      # Dictionary to store year nodes: {year_str: year_item}
        self.months = {}     # Nested dictionary: {year_str: {month_str: month_item}}
        self.days = {}       # Nested dict: {year_str: {month_str: {day_str: day_item}}}
        self.ids = {}        # For storing ID items: {year: {month: {day: {id: id_item}}}}
        
        # Color palettes for individual items - can be customized per item
        self.year_colors = {}    # {year_str: QColor}
        self.month_colors = {}   # {year_str: {month_str: QColor}}
        self.day_colors = {}     # {year_str: {month_str: {day_str: QColor}}
        
        # For debounced refresh handling
        self._debounced_refresh_timer = None
        
        # Subscribe to the project_data_changed event
        EventSystem.subscribe('project_data_changed', self.on_project_data_changed)
        
    def on_project_data_changed(self):
        """Called when project data changes in the database."""
        if self.tree:
            log("Project data changed. Scheduling explorer view refresh.")
            # Completely invalidate cache when data changes
            self._cache_valid = False
            self._data_cache = None
            # Use debounced refresh instead of immediate refresh
            self.debounced_refresh_data()

    def load_ui(self):
        """Load the dock widget from UI file."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/explorer/explorer_widget.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Access the dock widget content
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        
        # Create a vertical layout if not already present
        if content_widget.layout() is None:
            layout = QVBoxLayout(content_widget)
        else:
            layout = content_widget.layout()
            
        # Remove all margins to make the widget fill the entire dock
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Clear the layout (remove any existing widgets)
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Create the tree widget directly (no scroll area)
        self.tree = QTreeWidget(content_widget)
        self.tree.setHeaderHidden(True)  # Hide the header
        
        # Set size policy to allow the tree to expand
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Show branch lines
        self.tree.setRootIsDecorated(True)
        
        # Use standard scrollbar policies - built into QTreeWidget
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set modern scrollbar styling with more subtle appearance
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: transparent;
            }
            
            QTreeWidget::item {
                padding: 3px 0px;
            }
            
            /* Subtle scrollbar styling with lower opacity */
            QScrollBar:vertical {
                border: none;
                background-color: rgba(0, 0, 0, 5);  /* Very subtle background */
                width: 8px;  /* Slightly narrower */
                margin: 0px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(128, 128, 128, 60);  /* Lower opacity */
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: rgba(128, 128, 128, 120);  /* More visible on hover but still subtle */
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: rgba(0, 0, 0, 5);  /* Very subtle background */
                height: 8px;  /* Slightly narrower */
                margin: 0px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: rgba(128, 128, 128, 60);  /* Lower opacity */
                min-width: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(128, 128, 128, 120);  /* More visible on hover but still subtle */
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # Connect item click signal to handler
        try:
            # Check if our method is already connected
            if hasattr(self, '_old_connection') and self._old_connection:
                try:
                    self.tree.itemClicked.disconnect(self._old_connection)
                except TypeError:
                    pass
                    
            # Connect the signal and save the connection reference
            self.tree.itemClicked.connect(self.handle_item_clicked)
            self._old_connection = self.handle_item_clicked
            
        except Exception as e:
            error(f"Failed to connect click handler: {str(e)}")
        
        # Track empty item for proper cleanup during refresh
        self.empty_item = None
        
        # Load data from the database
        if not self.load_data_from_database():
            # Create an empty item that we can track and remove later
            self.empty_item = QTreeWidgetItem(self.tree, ["No data available"])
            self.empty_item.setForeground(0, QBrush(QColor(150, 150, 150)))
        
        # Expand the top levels by default
        for year_item in self.years.values():
            self.tree.expandItem(year_item)
        
        # Add tree directly to the layout
        layout.addWidget(self.tree)
        
        return self.widget

    def refresh_data(self):
        """Reload project data from the database and refresh the tree."""
        start_time = time.time()
        log("Refreshing explorer data...")
        
        # Force cache refresh if it's been more than 30 seconds since last load
        if time.time() - self._last_load_time > 30:
            self._cache_valid = False
            
        success = self.load_data_from_database()
        
        if success:
            # Track time for performance monitoring
            elapsed = time.time() - start_time
            log(f"Explorer data refreshed successfully in {elapsed:.3f} seconds.")
        else:
            warning("Failed to refresh explorer data.")
        
        # Force process events to update UI immediately
        from PySide6.QtWidgets import QApplication
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

    def load_data_from_database(self):
        """Load project data from the database using db_explorer_widget."""
        try:
            # Save expanded state of tree items before updating
            expanded_states = {}
            if self.tree and self.tree.topLevelItemCount() > 0:
                self._save_expanded_states(expanded_states)
            
            # Remove the empty item if it exists
            if hasattr(self, 'empty_item') and self.empty_item:
                index = self.tree.indexOfTopLevelItem(self.empty_item)
                if index >= 0:
                    self.tree.takeTopLevelItem(index)
                self.empty_item = None
            
            # Use cached data if valid and available
            if self._cache_valid and self._data_cache is not None:
                debug("Using cached project structure data")
                project_data = self._data_cache
            else:
                # Get project structure directly from the database module
                start_time = time.time()
                project_data = db_explorer_widget.get_project_structure(self.BASE_DIR)
                query_time = time.time() - start_time
                # debug(f"Database query completed in {query_time:.3f} seconds")
                
                # Cache the data for future use
                if project_data:
                    self._data_cache = project_data
                    self._last_load_time = time.time()
                    self._cache_valid = True
            
            if not project_data:
                return False
                
            # Load the data into the tree using the helper that processes the hierarchical structure
            start_time = time.time()
            success = self.load_project_data(project_data, expanded_states)
            ui_update_time = time.time() - start_time
            # debug(f"UI tree update completed in {ui_update_time:.3f} seconds")
            
            return success
                
        except Exception as e:
            exception(e, "Error loading data from database")
            return False

    def _save_expanded_states(self, expanded_states, parent_path="", item=None):
        """
        Recursively save the expanded state of all tree items.
        
        Args:
            expanded_states (dict): Dictionary to store the expanded states
            parent_path (str): Path of parent items
            item (QTreeWidgetItem): Current item being processed
        """
        if item is None:
            # Start with top level items
            for i in range(self.tree.topLevelItemCount()):
                top_item = self.tree.topLevelItem(i)
                self._save_expanded_states(expanded_states, top_item.text(0), top_item)
            return
            
        # Build the current path
        current_path = f"{parent_path}/{item.text(0)}" if parent_path else item.text(0)
        
        # Save the expanded state of this item
        expanded_states[current_path] = item.isExpanded()
        
        # Process children
        for i in range(item.childCount()):
            child_item = item.child(i)
            self._save_expanded_states(expanded_states, current_path, child_item)

    def _restore_expanded_states(self, expanded_states, parent_path="", item=None):
        """
        Recursively restore the expanded state of all tree items.
        
        Args:
            expanded_states (dict): Dictionary with stored expanded states
            parent_path (str): Path of parent items
            item (QTreeWidgetItem): Current item being processed
        """
        if item is None:
            # Start with top level items
            for i in range(self.tree.topLevelItemCount()):
                top_item = self.tree.topLevelItem(i)
                self._restore_expanded_states(expanded_states, top_item.text(0), top_item)
            return
            
        # Build the current path
        current_path = f"{parent_path}/{item.text(0)}" if parent_path else item.text(0)
        
        # Restore the expanded state if found in saved states
        if current_path in expanded_states:
            item.setExpanded(expanded_states[current_path])
        
        # Process children
        for i in range(item.childCount()):
            child_item = item.child(i)
            self._restore_expanded_states(expanded_states, current_path, child_item)

    def handle_item_clicked(self, item, column):
        """Handle click events on tree items."""
        from core.utils.logger import log, debug
        
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
                    
                    # Log the selection using the proper logger
                    log(f"Selected ID: {id_value} (Status: {status}) - Path: {path_str}")
                    
                    # Add extra debugging for event publishing
                    # debug(f">>> EXPLORER: Publishing explorer_item_selected event with item_id: {item_text}")
                    
                    # Notify the layout controller to update the workspace
                    from core.utils.event_system import EventSystem
                    EventSystem.publish('explorer_item_selected', item_text)
                    
                    # Add verification that event was published
                    # debug(f">>> EXPLORER: Event published for item_id: {item_text}")
                    
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

    def load_project_data(self, project_data=None, expanded_states=None):
        """
        Load actual project data into the explorer tree in descending order (newest first).
        
        Args:
            project_data: A dictionary containing the project structure data from the database.
                         If None, will try to load from database directly.
            expanded_states: Dictionary containing saved expanded states of tree items
        """
        # Clear existing tree first
        self.tree.clear()
        
        # Clear our internal data structures
        self.years = {}
        self.months = {}
        self.days = {}
        self.ids = {}
        self.year_colors = {}
        self.month_colors = {}
        self.day_colors = {}
        
        # Remove the bold font for years - no longer needed
        
        # If no data is provided, try to fetch it
        if project_data is None:
            # Try to get data from database
            project_data = db_explorer_widget.get_project_structure(self.BASE_DIR)
            if not project_data:
                warning("Failed to get project structure from database")
                return False
        
        # Process each year from the data (data should already be sorted in descending order)
        for year_data in project_data.get('items', []):
            year_str = year_data.get('year')
            if not year_str:
                continue
                
            # Create colors for the year
            year_color_rgb = year_data.get('color', [60, 120, 216])  # Default to blue if not specified
            
            # Create background color with alpha
            year_color_bg = QColor(year_color_rgb[0], year_color_rgb[1], year_color_rgb[2], 20)
            
            # Create text color without alpha
            year_color_fg = QColor(year_color_rgb[0], year_color_rgb[1], year_color_rgb[2])
            
            # Create year item - no longer setting bold font
            year_item = QTreeWidgetItem(self.tree, [year_str])
            
            # Add calendar icon for year
            year_icon = qta.icon('fa6s.calendar-days', color=year_color_fg.name())
            year_item.setIcon(0, year_icon)
            
            # Set colors
            year_item.setBackground(0, QBrush(year_color_bg))
            year_item.setForeground(0, QBrush(year_color_fg))
            
            # Store references
            self.years[year_str] = year_item
            self.year_colors[year_str] = year_color_bg
            self.months[year_str] = {}
            self.month_colors[year_str] = {}
            self.days[year_str] = {}
            self.day_colors[year_str] = {}
            self.ids[year_str] = {}
            
            # Process each month in this year (months should already be sorted in descending order)
            for month_data in year_data.get('months', []):
                month_name = month_data.get('name')
                if not month_name:
                    continue
                    
                # Create colors for the month
                month_color_rgb = month_data.get('color', [100, 100, 100])  # Default gray if not specified
                
                # Create background color with alpha
                month_color_bg = QColor(month_color_rgb[0], month_color_rgb[1], month_color_rgb[2], 20)
                
                # Create text color without alpha
                month_color_fg = QColor(month_color_rgb[0], month_color_rgb[1], month_color_rgb[2])
                
                # Create month item
                month_item = QTreeWidgetItem(year_item, [month_name])
                
                # Add month icon
                month_icon = qta.icon('fa6s.calendar-week', color=month_color_fg.name())
                month_item.setIcon(0, month_icon)
                
                # Set colors
                month_item.setBackground(0, QBrush(month_color_bg))
                month_item.setForeground(0, QBrush(month_color_fg))
                
                # Store references
                self.months[year_str][month_name] = month_item
                self.month_colors[year_str][month_name] = month_color_bg
                self.days[year_str][month_name] = {}
                self.day_colors[year_str][month_name] = {}
                self.ids[year_str][month_name] = {}
                
                # Process each day in this month (days should already be sorted in descending order)
                for day_data in month_data.get('days', []):
                    day_str = day_data.get('day')
                    if not day_str:
                        continue
                        
                    # Create colors for the day
                    day_color_rgb = day_data.get('color', [80, 80, 80])  # Default dark gray if not specified
                    
                    # Create background color with alpha
                    day_color_bg = QColor(day_color_rgb[0], day_color_rgb[1], day_color_rgb[2], 20)
                    
                    # Create text color without alpha
                    day_color_fg = QColor(day_color_rgb[0], day_color_rgb[1], day_color_rgb[2])
                    
                    # Create day item
                    day_item = QTreeWidgetItem(month_item, [day_str])
                    
                    # Add day icon
                    day_icon = qta.icon('fa6s.calendar-day', color=day_color_fg.name())
                    day_item.setIcon(0, day_icon)
                    
                    # Set colors
                    day_item.setBackground(0, QBrush(day_color_bg))
                    day_item.setForeground(0, QBrush(day_color_fg))
                    
                    # Store references
                    self.days[year_str][month_name][day_str] = day_item
                    self.day_colors[year_str][month_name][day_str] = day_color_bg
                    self.ids[year_str][month_name][day_str] = {}
                    
                    # Process each item (ID) for this day
                    item_list = day_data.get('items', [])
                    
                    # Sort items by database ID (primary key) in descending order
                    # Higher ID values were created more recently
                    def get_db_id_for_sort(item):
                        try:
                            # Try to convert database ID to integer for numeric sorting
                            return int(item.get('id', '0'))
                        except (TypeError, ValueError):
                            # If conversion fails, return 0 as fallback
                            return 0
                    
                    # Sort using the database ID extraction function (descending order)
                    sorted_items = sorted(
                        item_list,
                        key=get_db_id_for_sort,
                        reverse=True  # Descending order - newest items (with highest IDs) first
                    )
                    
                    for item_data in sorted_items:
                        id_value = item_data.get('item_id')  # Use item_id for display
                        status = item_data.get('status', 'unknown')
                        
                        # Create the formatted ID string: YYYY-MM-DD_ID_STATUS
                        # Pad month and day with leading zeros if needed
                        month_num = self._month_name_to_number(month_name)
                        day_num = day_str.zfill(2)  # Ensure day is two digits
                        formatted_id = f"{year_str}-{month_num}-{day_num}_{id_value}_{status}"
                        
                        # Create ID item
                        id_item = QTreeWidgetItem(day_item, [formatted_id])
                        
                        # Add table icon using parent day's color
                        table_icon = qta.icon('fa6s.table', color=day_color_fg.name())
                        id_item.setIcon(0, table_icon)
                        
                        # Set text color (inherit from parent day)
                        id_item.setForeground(0, QBrush(day_color_fg))
                        
                        # Store reference
                        self.ids[year_str][month_name][day_str][id_value] = id_item
        
        # Restore expanded states if provided, otherwise expand years by default
        if expanded_states:
            self._restore_expanded_states(expanded_states)
        else:
            # Default behavior - expand all year items
            for year_item in self.years.values():
                self.tree.expandItem(year_item)
            
        from core.utils.logger import log
        # log(f"Loaded project data: {len(self.years)} years, {sum(len(months) for months in self.months.values())} months, {sum(sum(len(days) for days in month.values()) for month in self.days.values())} days")
        
        return True
    
    def _month_name_to_number(self, month_name):
        """Convert month name to two-digit number string."""
        months = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }
        return months.get(month_name, '01')  # Default to '01' if not found

    def update_item_status(self, item_id, new_status):
        """Update an item's status in the database and refresh the UI."""
        if db_explorer_widget.update_item_status(item_id, new_status):
            # Refresh the tree to show updated data
            self.load_data_from_database()
            return True
        return False
        
    def add_new_item(self, year, month, day, item_id, status="draft"):
        """Add a new item to the database and refresh the UI."""
        if db_explorer_widget.add_project_item(year, month, day, item_id, status):
            # Refresh the tree to show the new item
            self.load_data_from_database()
            return True
        return False

    def __del__(self):
        """Clean up event subscriptions when the widget is destroyed."""
        try:
            EventSystem.unsubscribe('project_data_changed', self.on_project_data_changed)
        except:
            pass