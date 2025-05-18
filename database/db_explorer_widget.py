import sqlite3
import os
import datetime
from core.utils.logger import log, debug, warning, error, exception
from database import db_config

def get_project_structure(base_dir=None, refresh=False):
    """
    Get the project structure data from the database and transform it into the hierarchical format
    required by the explorer widget, sorted in descending order (newest first).
    
    Args:
        base_dir (str): Optional base directory path
        refresh (bool): Whether this is a refresh call
    
    Returns:
        dict: A hierarchical structure containing years, months, days, and items
        or None if there was an error
    """
    # Check and update colors for previous years on startup
    if not refresh:
        check_and_update_year_colors()
    
    conn = None
    try:
        # Get a database connection
        conn = db_config.connect_to_database()
        if not conn:
            warning("Could not connect to database")
            return None
            
        # Create cursor and execute query
        cursor = conn.cursor()
        
        # Check if the project_data table exists and has rows
        cursor.execute("SELECT COUNT(*) FROM project_data")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # warning("No project data found in database")
            return None
            
        # Query all project data rows with DISTINCT item_id to avoid duplicates
        # Include id (primary key), created_at and updated_at fields for proper sorting
        cursor.execute("""
            SELECT DISTINCT id, year, month, day, item_id, status, year_color, 
                    month_color, day_color, created_at, updated_at
            FROM project_data
            WHERE deleted_at IS NULL
        """)
        rows = cursor.fetchall()
        
        if not rows:
            warning("No project data records found")
            return None
        
        # Transform the flat data into the hierarchical structure needed for the explorer widget
        project_structure = {
            'project_id': 'tea_mini_project',
            'items': []  # Will contain year objects
        }
        
        # Process rows and build the hierarchical structure
        years_dict = {}  # Hold year data temporarily for processing
        item_ids_added = set()  # Track which item_ids have been added
        
        for row in rows:
            id_, year, month, day, item_id, status, year_color_str, month_color_str, day_color_str, created_at, updated_at = row
            
            # Skip if this item_id has already been added
            if item_id in item_ids_added:
                continue
                
            item_ids_added.add(item_id)
            
            # Parse color strings to arrays
            try:
                year_color = eval(year_color_str)  # Convert "[60,120,216]" to [60,120,216]
                month_color = eval(month_color_str)
                day_color = eval(day_color_str)
            except:
                # Default colors if parsing fails
                year_color = [60, 120, 216]  # Blue
                month_color = [100, 100, 100]  # Gray
                day_color = [80, 80, 80]  # Dark Gray
                warning(f"Failed to parse color data for item {item_id}, using defaults")
            
            # Create or get year
            if year not in years_dict:
                years_dict[year] = {
                    'year': year,
                    'color': year_color,
                    'months': {}  # Temporarily use a dict for easy lookup
                }
            
            year_obj = years_dict[year]
            
            # Create or get month
            if month not in year_obj['months']:
                year_obj['months'][month] = {
                    'name': month,
                    'color': month_color,
                    'days': {}  # Temporarily use a dict for easy lookup
                }
            
            month_obj = year_obj['months'][month]
            
            # Create or get day
            if day not in month_obj['days']:
                month_obj['days'][day] = {
                    'day': day,
                    'color': day_color,
                    'items': []
                }
            
            day_obj = month_obj['days'][day]
            
            # Add item to day with both id and item_id
            day_obj['items'].append({
                'id': id_,          # This is the database primary key
                'item_id': item_id, # This is the operation ID
                'status': status,
                'created_at': created_at,
                'updated_at': updated_at
            })
        
        # Convert the structured dictionaries to arrays as expected by explorer_widget
        # Sort years in descending order (newest first)
        sorted_years = sorted(years_dict.keys(), reverse=True)
        
        for year_key in sorted_years:
            year_obj = years_dict[year_key]
            
            # Convert months dict to list - sort in descending order
            months_list = []
            sorted_months = sorted(year_obj['months'].keys(), key=_month_to_number, reverse=True)
            
            for month_key in sorted_months:
                month_obj = year_obj['months'][month_key]
                
                # Convert days dict to list - sort in descending order
                days_list = []
                sorted_days = sorted(month_obj['days'].keys(), key=int, reverse=True)
                
                for day_key in sorted_days:
                    days_list.append(month_obj['days'][day_key])
                
                month_obj['days'] = days_list  # Replace dict with list
                months_list.append(month_obj)
            
            year_obj['months'] = months_list  # Replace dict with list
            project_structure['items'].append(year_obj)
        
        # Calculate and log summary statistics
        total_years = len(project_structure['items'])
        total_months = sum(len(year_obj['months']) for year_obj in project_structure['items'])
        total_days = sum(sum(len(month_obj['days']) for month_obj in year_obj['months']) 
                        for year_obj in project_structure['items'])
        
        # log(f"Loaded project data: {total_years} years, {total_months} months, {total_days} days")
        return project_structure
        
    except sqlite3.Error as e:
        error(f"Database error getting project structure: {e}")
        return None
        
    except Exception as e:
        exception(e, "Error retrieving project structure")
        return None
        
    finally:
        # Close the connection
        if conn:
            db_config.close_database_connection(conn)

def _month_to_number(month_name):
    """Helper function to convert month names to numbers for sorting."""
    months = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    return months.get(month_name, 0)

def get_item_details(item_id):
    """
    Get details for a specific item by ID.
    
    Args:
        item_id (str): The ID of the item to retrieve
        
    Returns:
        dict: Item details or None if not found
    """
    conn = None
    try:
        # Get database connection
        conn = db_config.connect_to_database()
        if not conn:
            warning("Could not connect to database")
            return None
            
        cursor = conn.cursor()
        cursor.execute(
            "SELECT year, month, day, status, year_color, month_color, day_color FROM project_data WHERE item_id = ?", 
            (item_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
            
        year, month, day, status, year_color_str, month_color_str, day_color_str = row
        
        # Parse colors
        try:
            year_color = eval(year_color_str)
            month_color = eval(month_color_str)
            day_color = eval(day_color_str)
        except:
            year_color = [60, 120, 216]
            month_color = [100, 100, 100]
            day_color = [80, 80, 80]
            
        return {
            'id': item_id,
            'year': year,
            'month': month,
            'day': day,
            'status': status,
            'year_color': year_color,
            'month_color': month_color,
            'day_color': day_color
        }
                            
    except Exception as e:
        exception(e, f"Error getting details for item {item_id}")
        return None
        
    finally:
        if conn:
            db_config.close_database_connection(conn)

def update_item_status(item_id, new_status):
    """
    Update the status of an item in the database.
    
    Args:
        item_id (str): The ID of the item to update
        new_status (str): The new status value
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        # Get database connection
        conn = db_config.connect_to_database()
        if not conn:
            warning("Could not connect to database")
            return False
            
        cursor = conn.cursor()
        
        # Update the item status
        cursor.execute(
            "UPDATE project_data SET status = ? WHERE item_id = ?",
            (new_status, item_id)
        )
        
        if cursor.rowcount == 0:
            warning(f"Item {item_id} not found in database")
            return False
            
        conn.commit()
        log(f"Updated status of item {item_id} to '{new_status}'")
        return True
        
    except Exception as e:
        exception(e, f"Error updating status for item {item_id}")
        return False
        
    finally:
        if conn:
            db_config.close_database_connection(conn)
            
def add_project_item(year, month, day, item_id, status="draft", year_color=None, month_color=None, day_color=None):
    """
    Add a new item to the project structure.
    
    Args:
        year (str): Year string (e.g., "2023")
        month (str): Month name (e.g., "January")
        day (str): Day string (e.g., "15")
        item_id (str): Item identifier
        status (str): Item status (default: "draft")
        year_color (list): RGB color for year [r,g,b]
        month_color (list): RGB color for month [r,g,b]
        day_color (list): RGB color for day [r,g,b]
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        # Set default colors if not provided
        if year_color is None:
            year_color = [60, 120, 216]  # Default blue
        if month_color is None:
            month_color = [100, 149, 237]  # Default cornflower blue
        if day_color is None:
            day_color = [80, 80, 80]  # Default gray
            
        # Convert colors to string representation
        year_color_str = str(year_color)
        month_color_str = str(month_color)
        day_color_str = str(day_color)
            
        # Get database connection
        conn = db_config.connect_to_database()
        if not conn:
            warning("Could not connect to database")
            return False
            
        cursor = conn.cursor()
        
        # Check if item already exists
        cursor.execute("SELECT COUNT(*) FROM project_data WHERE item_id = ?", (item_id,))
        if cursor.fetchone()[0] > 0:
            warning(f"Item {item_id} already exists in the database")
            return False
        
        # Get a new ID for the item (max + 1)
        cursor.execute("SELECT MAX(id) FROM project_data")
        result = cursor.fetchone()
        new_id = "1"
        if result[0]:
            new_id = str(int(result[0]) + 1)
        
        # Insert the new item
        cursor.execute(
            "INSERT INTO project_data (id, year, month, day, item_id, status, year_color, month_color, day_color) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (new_id, year, month, day, item_id, status, year_color_str, month_color_str, day_color_str)
        )
            
        conn.commit()
        log(f"Added new item {item_id} to {year}-{month}-{day} with status '{status}'")
        return True
        
    except Exception as e:
        exception(e, f"Error adding project item {item_id}")
        return False
        
    finally:
        if conn:
            db_config.close_database_connection(conn)

def update_previous_years_colors():
    """
    Update the colors of all records from previous years to gray.
    This function checks if the current year differs from the last processed year
    and only performs updates when necessary.

    Returns:
        bool: True if the update was performed, False if not needed or failed
    """
    conn = None
    try:
        # Get current year
        current_year = str(datetime.datetime.now().year)
        
        # Check if we already processed this year by checking the marker file
        marker_path = os.path.join(db_config.get_database_dir(), f"year_processed_{current_year}.marker")
        
        # If marker exists, we already processed this year
        if os.path.exists(marker_path):
            debug(f"Previous years already processed for year {current_year}")
            return False
            
        # Get database connection
        conn = db_config.connect_to_database()
        if not conn:
            warning("Could not connect to database")
            return False
            
        cursor = conn.cursor()
        
        # Define gray colors
        gray_color = "[120,120,120]"  # Medium gray
        dark_gray_color = "[100,100,100]"  # Darker gray
        light_gray_color = "[140,140,140]"  # Lighter gray
        
        # Update all records from previous years
        cursor.execute(
            """
            UPDATE project_data 
            SET year_color = ?, month_color = ?, day_color = ? 
            WHERE year != ?
            """,
            (dark_gray_color, gray_color, light_gray_color, current_year)
        )
        
        updated_rows = cursor.rowcount
        conn.commit()
        
        # Create marker file to indicate we've processed this year
        with open(marker_path, 'w') as f:
            f.write(f"Processed on {datetime.datetime.now().isoformat()}")
        
        log(f"Updated {updated_rows} records from previous years to gray colors")
        return True
        
    except sqlite3.Error as e:
        error(f"Database error while updating previous years colors: {e}")
        return False
    except Exception as e:
        exception(e, "Error updating previous years colors")
        return False
    finally:
        if conn:
            db_config.close_database_connection(conn)

def check_and_update_year_colors():
    """
    Check if the year has changed since last run and update colors if needed.
    This function should be called during application startup.
    
    Returns:
        bool: True if update was performed, False otherwise
    """
    try:
        # Get current year
        current_year = str(datetime.datetime.now().year)
        
        # Check for stored year value in database directory
        year_file_path = os.path.join(db_config.get_database_dir(), "last_year.txt")
        last_processed_year = None
        
        # Read last processed year if file exists
        if os.path.exists(year_file_path):
            with open(year_file_path, 'r') as f:
                last_processed_year = f.read().strip()
        
        # If year changed or file doesn't exist, update colors
        if last_processed_year != current_year:
            result = update_previous_years_colors()
            
            # Store current year for future checks
            with open(year_file_path, 'w') as f:
                f.write(current_year)
            
            return result
        
        return False
    
    except Exception as e:
        exception(e, "Error in check_and_update_year_colors")
        return False

def initialize_explorer():
    """
    Initialize the explorer widget functionality.
    This function should be called once at startup.
    
    Returns:
        bool: True if initialization was successful
    """
    try:
        # Update colors for previous years' records
        check_and_update_year_colors()
        log("Explorer widget initialized")
        return True
    except Exception as e:
        exception(e, "Error initializing explorer widget")
        return False

def refresh_project_structure():
    """
    Refresh the project structure data from the database.
    This function should be called after adding new files.
    
    Returns:
        dict: Updated project structure, or None if there was an error
    """
    return get_project_structure(refresh=True)
