from PySide6.QtCore import QTimer
from core.utils.logger import log, debug, warning, error, exception

class SearchHandler:
    """Helper class for handling tree search functionality."""
    
    def __init__(self, tree_widget):
        """Initialize the search handler."""
        self.tree = tree_widget
        self._search_field = None
        self._search_timer = None
        self._original_items_visibility = {}
        self._current_search_text = ""
    
    def set_search_field(self, search_field):
        """Set the search field and connect signals."""
        self._search_field = search_field
        if self._search_field:
            try:
                # Disconnect previous connections if any
                try:
                    self._search_field.textChanged.disconnect()
                except:
                    pass
                # Connect to our debounced search handler
                self._search_field.textChanged.connect(self._debounced_search)
            except Exception as e:
                error(f"Error connecting search field: {e}")
    
    def _debounced_search(self):
        """Debounce search calls to prevent multiple rapid searches during typing."""
        # Cancel any existing timer
        if self._search_timer is not None:
            self._search_timer.stop()
            
        # Create a new timer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._search_timer.start(300)  # 300ms delay
    
    def clear_search(self):
        """Clear the search field and restore tree visibility."""
        if not self._search_field:
            return
            
        # Save current expanded states before clearing search
        expanded_states = {}
        self._save_expanded_states(expanded_states)
        
        # Clear the search field (this will trigger textChanged)
        # To prevent double processing, disconnect signal temporarily
        try:
            self._search_field.textChanged.disconnect(self._debounced_search)
            self._search_field.clear()
            self._search_field.textChanged.connect(self._debounced_search)
        except Exception:
            # In case of connection error, just clear
            self._search_field.clear()
        
        # Reset current search text
        self._current_search_text = ""
        
        # Restore tree visibility
        self._restore_tree_visibility()
        
        # Restore expanded states (don't expand everything)
        self._restore_expanded_states(expanded_states)
    
    def _perform_search(self):
        """Filter tree items based on search text."""
        if not self.tree or not self._search_field:
            return
            
        search_text = self._search_field.text().lower().strip()
        
        # Skip if search text hasn't changed
        if search_text == self._current_search_text:
            return
            
        self._current_search_text = search_text
            
        # If search is empty, restore all items visibility
        if not search_text:
            self._restore_tree_visibility()
            return
        
        # Save original visibility before filtering if not already saved
        if not self._original_items_visibility:
            self._save_items_visibility()
        
        # First hide all items
        self._hide_all_items()
        
        # Find matching items
        matching_items = []
        self._find_matching_items(search_text, matching_items)
        
        # Show matching items and their parents
        for item in matching_items:
            self._show_item_and_parents(item)
        
        # Expand items to show matches
        self._expand_visible_items()
    
    def _save_items_visibility(self):
        """Save the visibility state of all tree items."""
        self._original_items_visibility = {}
        
        # Save top level items
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self._save_item_visibility_recursive(item)
            
    def _save_item_visibility_recursive(self, item):
        """Recursively save visibility of an item and its children."""
        # Store item by its memory address as a unique identifier
        self._original_items_visibility[id(item)] = item.isHidden()
        
        # Process children
        for i in range(item.childCount()):
            child = item.child(i)
            self._save_item_visibility_recursive(child)
    
    def _restore_tree_visibility(self):
        """Restore original visibility of all tree items."""
        if not self._original_items_visibility:
            # If no saved state, show all items but keep expansion state
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                self._show_item_recursive(item)
            return
            
        # Restore top level items
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self._restore_item_visibility_recursive(item)
        
        # Clear saved visibility data
        self._original_items_visibility = {}
            
    def _restore_item_visibility_recursive(self, item):
        """Recursively restore visibility of an item and its children."""
        # Get the original visibility state
        item_id = id(item)
        if item_id in self._original_items_visibility:
            item.setHidden(self._original_items_visibility[item_id])
        else:
            item.setHidden(False)  # Default visible
            
        # Process children
        for i in range(item.childCount()):
            child = item.child(i)
            self._restore_item_visibility_recursive(child)
            
    def _hide_all_items(self):
        """Hide all items in the tree."""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self._hide_item_recursive(item)
            
    def _hide_item_recursive(self, item):
        """Recursively hide an item and its children."""
        item.setHidden(True)
        for i in range(item.childCount()):
            child = item.child(i)
            self._hide_item_recursive(child)
            
    def _show_item_recursive(self, item):
        """Recursively show an item and its children."""
        item.setHidden(False)
        for i in range(item.childCount()):
            child = item.child(i)
            self._show_item_recursive(child)
    
    def _find_matching_items(self, search_text, matching_items):
        """Find all items that match the search text."""
        # Check top level items
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self._find_matching_items_recursive(item, search_text, matching_items)
    
    def _find_matching_items_recursive(self, item, search_text, matching_items):
        """Recursively search for items matching the search text."""
        # Check if this item matches
        if search_text in item.text(0).lower():
            matching_items.append(item)
            
        # Check children
        for i in range(item.childCount()):
            child = item.child(i)
            self._find_matching_items_recursive(child, search_text, matching_items)
    
    def _show_item_and_parents(self, item):
        """Show an item and all its parent items."""
        # Show this item
        item.setHidden(False)
        
        # Show all parent items
        parent = item.parent()
        while parent:
            parent.setHidden(False)
            parent = parent.parent()
    
    def _expand_visible_items(self):
        """Expand all visible items to show search results."""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if not item.isHidden():
                self._expand_item_recursive(item)
                
    def _expand_item_recursive(self, item):
        """Recursively expand visible items."""
        # Only expand items that aren't hidden
        if not item.isHidden():
            self.tree.expandItem(item)
            
            # Process children only if parent is visible
            for i in range(item.childCount()):
                child = item.child(i)
                self._expand_item_recursive(child)
    
    def _save_expanded_states(self, expanded_states, parent_path="", item=None):
        """Save the expanded state of all tree items."""
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
        """Restore the expanded state of all tree items."""
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
