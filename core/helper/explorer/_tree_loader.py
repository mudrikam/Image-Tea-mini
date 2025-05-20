from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QColor, QBrush, QCursor
from PySide6.QtCore import Qt
from core.utils.logger import log, debug, warning, error, exception
import qtawesome as qta

class TreeLoader:
    """Helper class for loading and managing tree structure."""    
    def __init__(self, tree_widget):
        """Initialize the tree loader."""
        self.tree = tree_widget
        
        # Store references to hierarchical data
        self.years = {}      # Dictionary to store year nodes: {year_str: year_item}
        self.months = {}     # Nested dictionary: {year_str: {month_str: month_item}}
        self.days = {}       # Nested dict: {year_str: {month_str: {day_str: day_item}}}
        self.ids = {}        # For storing ID items: {year: {month: {day: {id: id_item}}}}
        
        # Setup hover cursor for tree items
        if self.tree:
            self.setup_item_hover_cursor()
        
        # Set up item hover cursor
        if self.tree:
            self.setup_item_hover_cursor()
        # Color palettes for individual items
        self.year_colors = {}    # {year_str: QColor}
        self.month_colors = {}   # {year_str: {month_str: QColor}}
        self.day_colors = {}     # {year_str: {month_str: {day_str: QColor}}
        
        # Track empty item for proper cleanup during refresh
        self.empty_item = None
    def clear_tree(self):
        """Clear the tree and internal tracking dictionaries."""
        if self.tree:
            self.tree.clear()
        
        # Clear internal data structures
        self.years = {}
        self.months = {}
        self.days = {}
        self.ids = {}
        self.year_colors = {}
        self.month_colors = {}
        self.day_colors = {}
        self.empty_item = None      
    def setup_item_hover_cursor(self):
        """Set up the tree widget to show pointing hand cursor when hovering over items."""
        if not self.tree:
            return
        
        # We'll set cursor for individual items in their creation methods instead
        # Enable hover tracking for the tree
        from PySide6.QtCore import Qt
        self.tree.setAttribute(Qt.WA_Hover, True)
        self.tree.setMouseTracking(True)
    def create_empty_tree(self, message="No data available"):
        """Create an empty tree with a message."""
        self.clear_tree()
        self.empty_item = QTreeWidgetItem(self.tree, [message])
        self.empty_item.setForeground(0, QBrush(QColor(150, 150, 150)))        # Set pointing hand cursor data
        self.empty_item.setData(0, Qt.UserRole, "pointing_hand_cursor")
        return self.empty_item
        
    def load_project_data(self, project_data, expanded_states=None):
        """
        Load project data into the explorer tree.
        
        Args:
            project_data: Dict containing project structure data
            expanded_states: Dict containing saved expanded states of tree items
            
        Returns:
            bool: Success status
        """
        # Clear existing tree first
        self.clear_tree()
        
        # Set up item hover cursor
        self.setup_item_hover_cursor()
        
        if not project_data:
            self.create_empty_tree()
            return False
        
        # Process each year from the data (data should already be sorted in descending order)
        for year_data in project_data.get('items', []):
            year_str = year_data.get('year')
            if not year_str:
                continue
                
            # Create year item with appropriate styling
            year_item = self._create_year_item(year_data)
            
            # Process each month in this year
            for month_data in year_data.get('months', []):
                month_name = month_data.get('name')
                if not month_name:
                    continue
                
                # Create month item with appropriate styling
                month_item = self._create_month_item(month_data, year_item, year_str)
                
                # Process each day in this month
                for day_data in month_data.get('days', []):
                    day_str = day_data.get('day')
                    if not day_str:
                        continue
                    
                    # Create day item with appropriate styling
                    day_item = self._create_day_item(day_data, month_item, year_str, month_name)
                    
                    # Process each item (ID) for this day
                    sorted_items = self._sort_day_items(day_data.get('items', []))
                    
                    for item_data in sorted_items:
                        # Create ID item with appropriate styling
                        self._create_id_item(item_data, day_item, year_str, month_name, day_str)
        
        # Restore expanded states if provided, otherwise expand years by default
        if expanded_states:
            self._restore_expanded_states(expanded_states)
        else:
            # Default behavior - expand all year items
            for year_item in self.years.values():
                self.tree.expandItem(year_item)
        
        return True
    def _create_year_item(self, year_data):
        """Create and style a year item in the tree."""
        year_str = year_data.get('year')
        
        # Create colors for the year
        year_color_rgb = year_data.get('color', [60, 120, 216])  # Default to blue if not specified
        year_color_bg = QColor(year_color_rgb[0], year_color_rgb[1], year_color_rgb[2], 20)
        year_color_fg = QColor(year_color_rgb[0], year_color_rgb[1], year_color_rgb[2])
        
        # Create year item
        year_item = QTreeWidgetItem(self.tree, [year_str])
        
        # Add calendar icon for year
        year_icon = qta.icon('fa6s.calendar-days', color=year_color_fg.name())
        year_item.setIcon(0, year_icon)
        
        # Set colors
        year_item.setBackground(0, QBrush(year_color_bg))
        year_item.setForeground(0, QBrush(year_color_fg))        # Set pointing hand cursor data
        year_item.setData(0, Qt.UserRole, "pointing_hand_cursor")
        
        # Store references
        self.years[year_str] = year_item
        self.year_colors[year_str] = year_color_bg
        self.months[year_str] = {}
        self.month_colors[year_str] = {}
        self.days[year_str] = {}
        self.day_colors[year_str] = {}
        self.ids[year_str] = {}
        
        return year_item
    def _create_month_item(self, month_data, year_item, year_str):
        """Create and style a month item in the tree."""
        month_name = month_data.get('name')
        
        # Create colors for the month
        month_color_rgb = month_data.get('color', [100, 100, 100])  # Default gray if not specified
        month_color_bg = QColor(month_color_rgb[0], month_color_rgb[1], month_color_rgb[2], 20)
        month_color_fg = QColor(month_color_rgb[0], month_color_rgb[1], month_color_rgb[2])
        
        # Create month item
        month_item = QTreeWidgetItem(year_item, [month_name])
        
        # Add month icon
        month_icon = qta.icon('fa6s.calendar-week', color=month_color_fg.name())
        month_item.setIcon(0, month_icon)
        
        # Set colors
        month_item.setBackground(0, QBrush(month_color_bg))
        month_item.setForeground(0, QBrush(month_color_fg))
        
        # Set pointing hand cursor data
        month_item.setData(0, Qt.UserRole, "pointing_hand_cursor")
        
        # Store references
        self.months[year_str][month_name] = month_item
        self.month_colors[year_str][month_name] = month_color_bg
        self.days[year_str][month_name] = {}
        self.day_colors[year_str][month_name] = {}
        self.ids[year_str][month_name] = {}
        
        return month_item
    def _create_day_item(self, day_data, month_item, year_str, month_name):
        """Create and style a day item in the tree."""
        day_str = day_data.get('day')
        
        # Create colors for the day
        day_color_rgb = day_data.get('color', [80, 80, 80])  # Default dark gray if not specified
        day_color_bg = QColor(day_color_rgb[0], day_color_rgb[1], day_color_rgb[2], 20)
        day_color_fg = QColor(day_color_rgb[0], day_color_rgb[1], day_color_rgb[2])
        
        # Create day item
        day_item = QTreeWidgetItem(month_item, [day_str])
        
        # Add day icon
        day_icon = qta.icon('fa6s.calendar-day', color=day_color_fg.name())
        day_item.setIcon(0, day_icon)
        
        # Set colors
        day_item.setBackground(0, QBrush(day_color_bg))
        day_item.setForeground(0, QBrush(day_color_fg))
        
        # Set pointing hand cursor data
        day_item.setData(0, Qt.UserRole, "pointing_hand_cursor")
        
        # Store references
        self.days[year_str][month_name][day_str] = day_item
        self.day_colors[year_str][month_name][day_str] = day_color_bg
        self.ids[year_str][month_name][day_str] = {}
        
        return day_item
    def _create_id_item(self, item_data, day_item, year_str, month_name, day_str):
        """Create and style an ID item in the tree."""
        id_value = item_data.get('item_id')
        status = item_data.get('status', 'unknown')
        
        # Get day's color for the ID item
        day_color_fg = day_item.foreground(0).color()
        
        # Format ID string: YYYY-MM-DD_ID_STATUS
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
        
        # Set pointing hand cursor data
        id_item.setData(0, Qt.UserRole, "pointing_hand_cursor")
        
        # Store reference
        self.ids[year_str][month_name][day_str][id_value] = id_item
        
        return id_item
    
    def _sort_day_items(self, items):
        """Sort items by database ID in descending order."""
        def get_db_id_for_sort(item):
            try:
                # Try to convert database ID to integer for numeric sorting
                return int(item.get('id', '0'))
            except (TypeError, ValueError):
                # If conversion fails, return 0 as fallback
                return 0
        
        # Sort using the database ID extraction function (descending order)
        return sorted(
            items,
            key=get_db_id_for_sort,
            reverse=True  # Descending order - newest items (with highest IDs) first
        )
    
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
    
    def save_expanded_states(self):
        """Save the expanded state of all tree items."""
        expanded_states = {}
        if self.tree and self.tree.topLevelItemCount() > 0:
            self._save_expanded_states(expanded_states)
        return expanded_states
    
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
    
    def expand_years(self):
        """Expand all year items."""
        for year_item in self.years.values():
            self.tree.expandItem(year_item)
    
    def expand_all(self):
        """Expand all items in the tree."""
        if self.tree:
            self.tree.expandAll()
    
    def collapse_all_except_years(self):
        """Collapse all items except year items."""
        if self.tree:
            # First collapse everything
            self.tree.collapseAll()
            # Then expand only year items
            for year_item in self.years.values():
                self.tree.expandItem(year_item)
