import time
from core.utils.logger import log, debug, warning, error, exception
from database import db_explorer_widget

class DataManager:
    """Helper class for managing explorer data loading and caching."""
    
    def __init__(self, base_dir=None):
        """Initialize the data manager."""
        self.BASE_DIR = base_dir
        self._data_cache = None
        self._last_load_time = 0
        self._cache_valid = False
    
    def load_data_from_database(self, force_refresh=False):
        """
        Load project data from the database with caching.
        
        Args:
            force_refresh (bool): If True, ignores cache and forces a database reload
            
        Returns:
            tuple: (project_data, success)
        """
        try:
            # Force cache refresh if requested or if it's been more than 30 seconds
            if force_refresh or not self._cache_valid or (time.time() - self._last_load_time > 30):
                self._cache_valid = False
                
                # Get project structure from the database
                start_time = time.time()
                project_data = db_explorer_widget.get_project_structure(self.BASE_DIR)
                query_time = time.time() - start_time
                # debug(f"Database query completed in {query_time:.3f} seconds")
                
                # Cache the data for future use if available
                if project_data:
                    self._data_cache = project_data
                    self._last_load_time = time.time()
                    self._cache_valid = True
                    return project_data, True
                else:
                    return None, False
            else:
                # Use cached data if valid and available
                debug("Using cached project structure data")
                return self._data_cache, True
                
        except Exception as e:
            exception(e, "Error loading data from database")
            return None, False
    
    def invalidate_cache(self):
        """Invalidate the cache to force reload on next request."""
        self._cache_valid = False
        self._data_cache = None
    
    def update_item_status(self, item_id, new_status):
        """Update an item's status in the database."""
        result = db_explorer_widget.update_item_status(item_id, new_status)
        if result:
            # Invalidate cache since data has changed
            self.invalidate_cache()
        return result
    
    def add_new_item(self, year, month, day, item_id, status="draft"):
        """Add a new item to the database."""
        result = db_explorer_widget.add_project_item(year, month, day, item_id, status)
        if result:
            # Invalidate cache since data has changed
            self.invalidate_cache()
        return result
    
    def get_cached_data(self):
        """Get the current cached data if available."""
        if self._cache_valid and self._data_cache is not None:
            return self._data_cache
        return None
    
    def is_cache_valid(self):
        """Check if cache is currently valid."""
        return self._cache_valid
    
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
