import os
import sqlite3
import random
from datetime import datetime
from core.utils.logger import log, debug, warning, error, exception
from database.db_config import connect_to_database, close_database_connection
from core.utils.event_system import EventSystem

def generate_random_color(max_value=170):
    """
    Generate a truly random RGB color with one component always at max_value (170) and one at 0.
    For readability on dark themes:
    - When blue=170, green must be >105 or red must be >90
    
    Args:
        max_value (int): Maximum RGB value (default 170 instead of 255 for softer colors)
        
    Returns:
        list: RGB color as [r, g, b] where one component is max_value, one is 0, and one is random
    """
    # Determine which channel gets which value
    # 0: Red is max (170), Blue is 0, Green is random
    # 1: Green is max (170), Red is 0, Blue is random
    # 2: Blue is max (170), Green is 0, Red must be at least 91
    # 3: Blue is max (170), Red is 0, Green must be at least 106
    # 4: Red is max (170), Green is 0, Blue is random
    # 5: Green is max (170), Blue is 0, Red is random
    channel_assignment = random.randint(0, 5)
    
    if channel_assignment == 0:
        # Red is max, Blue is 0, Green is at least 50
        return [max_value, random.randint(50, max_value), 0]
    elif channel_assignment == 1:
        # Green is max, Red is 0, Blue is random
        return [0, max_value, random.randint(0, max_value)]
    elif channel_assignment == 2:
        # Blue is max, Green is 0, Red must be at least 170
        return [random.randint(170, max_value), 0, max_value]
    elif channel_assignment == 3:
        # Blue is max, Red is 0, Green must be at least 70
        return [0, random.randint(70, max_value), max_value]
    elif channel_assignment == 4:
        # Red is max, Green is 0, Blue is random
        return [max_value, 0, random.randint(0, max_value)]
    else:  # channel_assignment == 5
        # Green is max, Blue is 0, Red is random
        return [random.randint(0, max_value), max_value, 0]

def generate_year_color():
    """
    Generate a random color for a year.
    Each color has one component at 170, one at 0, and one random component.
    Colors are completely random and not thematically linked.
    
    Returns:
        list: RGB color values as [r, g, b]
    """
    return generate_random_color(max_value=170)

def generate_month_color():
    """
    Generate a completely random color for a month.
    Each color has one component at 170, one at 0, and one random component.
    Not based on the year color at all - completely random.
    
    Returns:
        list: RGB color values as [r, g, b]
    """
    return generate_random_color(max_value=170)

def generate_day_color():
    """
    Generate a completely random color for a day.
    Each color has one component at 170, one at 0, and one random component.
    Not based on the month color at all - completely random.
    
    Returns:
        list: RGB color values as [r, g, b]
    """
    return generate_random_color(max_value=170)

class ProjectFilesModel:
    """
    Model class to handle project files database operations.
    """
    
    def __init__(self):
        """Initialize the model."""
        self.table_name = "project_data"
    
    def get_last_item_id(self):
        """
        Get the last used item_id from the database and convert to int.
        
        Returns:
            int: The last used item_id as an integer, or 0 if no items found
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Query for the maximum numeric item_id from the database
            query = """
                SELECT item_id FROM project_data 
                WHERE deleted_at IS NULL
            """
            
            cursor.execute(query)
            
            # Fetch all item_ids
            rows = cursor.fetchall()
            close_database_connection(conn)
            
            # If no records found, start with 0
            if not rows:
                return 0
            
            # Extract numeric value from each item_id
            # Expected format: four digits like "0001", "0023", etc.
            max_id = 0
            for row in rows:
                item_id = row[0]
                if item_id and isinstance(item_id, str):
                    try:
                        # Try to convert the string to an integer
                        id_value = int(item_id)
                        if id_value > max_id:
                            max_id = id_value
                    except ValueError:
                        # If conversion fails, ignore this item_id
                        continue
            
            return max_id
            
        except sqlite3.Error as e:
            error(f"Database error when retrieving last item_id: {e}")
            return 0
        except Exception as e:
            exception(e, "Error retrieving last item_id")
            return 0
            
    def get_next_item_id(self):
        """
        Get the next available item_id as a zero-padded 4-digit string.
        
        Returns:
            str: The next available item_id (e.g., "0001", "0002", etc.)
        """
        last_id = self.get_last_item_id()
        next_id = last_id + 1
        
        # Format as 4-digit string with leading zeros
        return f"{next_id:04d}"

    def add_file(self, file_details, publish_event=True):
        """
        Add a file to the project database.
        
        Args:
            file_details (dict): Dictionary containing file details
            publish_event (bool): Whether to publish a data changed event (default: True)
            
        Returns:
            bool or int: Record ID if successful, False otherwise
        """
        try:
            # Generate random colors for year, month, and day if not provided
            if 'year_color' not in file_details:
                file_details['year_color'] = str(generate_year_color())
                
            if 'month_color' not in file_details:
                # Completely independent from year color
                file_details['month_color'] = str(generate_month_color())
                
            if 'day_color' not in file_details:
                # Completely independent from month color
                file_details['day_color'] = str(generate_day_color())
            
            # Generate the next item_id if not provided
            if 'item_id' not in file_details:
                file_details['item_id'] = self.get_next_item_id()
            
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Remove id from file_details if present (it will be auto-generated)
            if 'id' in file_details:
                del file_details['id']
            
            # Extract all fields from file_details
            fields = list(file_details.keys())
            placeholders = ["?" for _ in fields]
            values = [file_details.get(field) for field in fields]
            
            # Construct query
            query = f"INSERT INTO {self.table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            
            # Execute and commit
            cursor.execute(query, values)
            conn.commit()
            
            # Get the ID of the last inserted row
            last_id = cursor.lastrowid
            
            log(f"Added file to database: {file_details.get('filename', 'Unknown')} with ID {last_id}")
            close_database_connection(conn)
            
            # Only publish event if explicitly requested
            # This allows batch operations to control when to refresh the UI
            if publish_event:
                EventSystem.publish('project_data_changed')
            
            return last_id
            
        except sqlite3.Error as e:
            error(f"Database error while adding file: {e}")
            if 'conn' in locals() and conn:
                close_database_connection(conn)
            return False
        except Exception as e:
            exception(e, "Error adding file to database")
            if 'conn' in locals() and conn:
                close_database_connection(conn)
            return False
    
    def add_multiple_files(self, file_details_list):
        """
        Add multiple files to the project database.
        
        Args:
            file_details_list (list): List of dictionaries containing file details
            
        Returns:
            list: List of IDs for successfully added files
        """
        success_ids = []
        for file_details in file_details_list:
            # Don't publish event for individual file additions - only at the end
            result = self.add_file(file_details, publish_event=False)
            if result:  # If add_file returns the ID (not False)
                success_ids.append(result)
        
        log(f"Added {len(success_ids)}/{len(file_details_list)} files to database")
        
        # Publish event only after all files have been added
        if success_ids:
            EventSystem.publish('project_data_changed')
            
        return success_ids
    def get_all_files(self, status=None):
        """
        Get all files from the database, optionally filtered by status.
        
        Args:
            status (str, optional): Filter by status
            
        Returns:
            list: List of dictionaries containing file details
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Get all column names
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Construct query
            if status:
                query = f"SELECT * FROM {self.table_name} WHERE status = ? AND deleted_at IS NULL"
                cursor.execute(query, (status,))
            else:
                query = f"SELECT * FROM {self.table_name} WHERE deleted_at IS NULL"
                cursor.execute(query)
                
            # Fetch results and convert to list of dictionaries
            rows = cursor.fetchall()
            results = []
            for row in rows:
                file_dict = {columns[i]: row[i] for i in range(len(columns))}
                results.append(file_dict)
                
            close_database_connection(conn)
            return results
            
        except sqlite3.Error as e:
            error(f"Database error while retrieving files: {e}")
            if conn:
                close_database_connection(conn)
            return []
        except Exception as e:
            exception(e, "Error retrieving files from database")
            if conn:
                close_database_connection(conn)
            return []
    def get_files_by_item_id(self, item_id):
        """
        Get all files for a specific item_id.
        
        Args:
            item_id: The item_id to search for
            
        Returns:
            list: List of dictionaries with file information
        """
        debug(f"ProjectFilesModel get_files_by_item_id called with item_id: {item_id}")
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
              # Query for files with the specified item_id
            query = """
                SELECT id, year, month, day, item_id, status, year_color, month_color, day_color,
                       title, description, tags, filename, extension, filepath, filesize,
                       file_type, image_width, image_height, dimensions, category, sub_category,
                       title_length, tags_count, created_at, updated_at
                FROM project_data 
                WHERE item_id = ? AND deleted_at IS NULL
                ORDER BY filename
            """
            
            debug(f"Executing SQL query with item_id: {item_id}")
            cursor.execute(query, (item_id,))
            
            # Fetch all rows as dictionaries
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            debug(f"Found {len(rows)} rows in database for item_id: {item_id}")
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
                
            close_database_connection(conn)
            return result
            
        except Exception as e:
            exception(e, f"Error getting files by item_id: {item_id}")
            return []
    
    def get_files_by_id(self, id):
        """
        Get file information for a specific id.
        
        Args:
            id: The primary key id to search for
            
        Returns:
            list: List containing a dictionary with file information if found
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
              # Query for the file with the specified id
            query = """
                SELECT id, year, month, day, item_id, status, year_color, month_color, day_color,
                       title, description, tags, filename, extension, filepath, filesize,
                       file_type, image_width, image_height, dimensions, category, sub_category,
                       title_length, tags_count, created_at, updated_at
                FROM project_data 
                WHERE id = ? AND deleted_at IS NULL
            """
            
            cursor.execute(query, (id,))
            
            # Fetch the row as a dictionary
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            
            close_database_connection(conn)
            
            if row:
                return [dict(zip(columns, row))]
            else:
                return []
                
        except Exception as e:
            exception(e, f"Error getting file by id: {id}")
            return []
    
    def update_file(self, file_id, update_data):
        """
        Update file information in the database.
        
        Args:
            file_id (str): ID of the file to update
            update_data (dict): Dictionary containing fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Always update the updated_at field
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Construct SET part of query
            set_clause = ", ".join([f"{field} = ?" for field in update_data.keys()])
            values = list(update_data.values())
            
            # Add ID to values list
            values.append(file_id)
            
            # Construct and execute query
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            affected_rows = cursor.rowcount
            close_database_connection(conn)
            
            if affected_rows > 0:
                debug(f"Updated file with ID {file_id}")
                # Publish event to notify listeners that data has changed
                EventSystem.publish('project_data_changed')
                return True
            else:
                warning(f"No file found with ID {file_id}")
                return False
                
        except sqlite3.Error as e:
            error(f"Database error while updating file: {e}")
            if conn:
                close_database_connection(conn)
            return False
        except Exception as e:
            exception(e, f"Error updating file with ID {file_id}")
            if conn:
                close_database_connection(conn)
            return False
    
    def delete_file(self, file_id, soft_delete=True):
        """
        Delete a file from the database.
        
        Args:
            file_id (str): ID of the file to delete
            soft_delete (bool): If True, just mark as deleted; if False, remove from DB
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            if soft_delete:
                # Soft delete - just mark the deleted_at field
                query = f"UPDATE {self.table_name} SET deleted_at = ? WHERE id = ?"
                cursor.execute(query, (datetime.now().isoformat(), file_id))
            else:
                # Hard delete - remove from database
                query = f"DELETE FROM {self.table_name} WHERE id = ?"
                cursor.execute(query, (file_id,))
                
            conn.commit()
            affected_rows = cursor.rowcount
            close_database_connection(conn)
            
            if affected_rows > 0:
                debug(f"{'Soft' if soft_delete else 'Hard'} deleted file with ID {file_id}")
                # Publish event to notify listeners that data has changed
                EventSystem.publish('project_data_changed')
                return True
            else:
                warning(f"No file found with ID {file_id}")
                return False
                
        except sqlite3.Error as e:
            error(f"Database error while deleting file: {e}")
            if conn:
                close_database_connection(conn)
            return False
        except Exception as e:
            exception(e, f"Error deleting file with ID {file_id}")
            if conn:
                close_database_connection(conn)
            return False    
    def process_folder(self, folder_path, folder_details=None):
        """
        Process a folder and add all supported files to the database.
        
        Args:
            folder_path (str): Path to the folder
            folder_details (dict, optional): Dictionary with folder metadata (not used)
            
        Returns:
            tuple: (dict, processed_count) - dict contains folder metadata including item_id, and count of processed files
        """
        # We're not adding the folder itself to the database, just processing its contents
        folder_data = {}
        processed_count = 0
        
        try:
            from core.global_operations.file_operations import (
                get_image_extensions, get_video_extensions, 
                get_file_details, get_new_operation_id
            )
            
            # Generate a new operation ID for all files in this folder
            # This ensures all files from this folder share the same ID
            operation_id = get_new_operation_id()
            
            # Generate completely random colors for all files in this folder
            year_color = generate_year_color()
            month_color = generate_month_color()  # Not based on year_color
            day_color = generate_day_color()      # Not based on month_color
            
            # Get supported extensions
            image_extensions = get_image_extensions()
            video_extensions = get_video_extensions()
            supported_extensions = image_extensions + video_extensions
            
            # Walk through the folder and its subfolders
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    
                    # Only process files with supported extensions
                    if ext in supported_extensions:
                        try:
                            # Use get_file_details which now extracts metadata from files
                            file_details = get_file_details(file_path, operation_id)
                            if file_details:
                                # Add colors to the file details
                                file_details['year_color'] = str(year_color)
                                file_details['month_color'] = str(month_color)
                                file_details['day_color'] = str(day_color)
                                
                                # Add file individually using add_file but don't publish events for each one
                                file_id = self.add_file(file_details, publish_event=False)
                                if file_id:
                                    processed_count += 1
                                    log(f"Added file with extracted metadata: {file_details.get('title', 'Unknown')} from {file_path}")
                        except Exception as e:
                            warning(f"Error processing file {file_path}: {str(e)}")
            
            # Publish event only after processing all files in the folder
            if processed_count > 0:
                EventSystem.publish('project_data_changed')
        except Exception as e:
            exception(e, f"Error processing folder {folder_path}")
        
        # Return folder data including the operation_id
        folder_data = {'item_id': operation_id} if processed_count > 0 else {}
        return folder_data, processed_count
        
    def process_multiple_folders(self, folder_paths):
        """
        Process multiple folders and add their files to the database.
        
        Args:
            folder_paths (list): List of folder paths to process
            
        Returns:
            dict: Summary of processed folders with counts
        """        
        results = {
            'total_folders': 0,
            'total_files': 0,
            'processed_folders': [],
            'item_ids': []
        }
        
        if not folder_paths:
            return results
            
        # For multiple folders, we still generate just one operation ID
        # to group all files from this multi-folder operation
        from core.global_operations.file_operations import get_new_operation_id
        multi_folder_operation_id = get_new_operation_id()
        
        # Generate completely random colors for this whole multi-folder operation
        year_color = generate_year_color()
        month_color = generate_month_color()  # Not based on year_color
        day_color = generate_day_color()      # Not based on month_color
        
        total_processed_files = 0
        
        for folder_path in folder_paths:
            if not folder_path or not os.path.isdir(folder_path):
                continue
                
            try:
                from core.global_operations.file_operations import (
                    get_image_extensions, get_video_extensions,
                    get_file_details
                )
                
                # Get supported extensions
                image_extensions = get_image_extensions()
                video_extensions = get_video_extensions()
                supported_extensions = image_extensions + video_extensions
                
                folder_processed_count = 0
                
                # Walk through the folder and its subfolders
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        ext = os.path.splitext(file)[1].lower()
                        
                        # Only process files with supported extensions
                        if ext in supported_extensions:
                            try:
                                # Use the multi-folder operation ID for all files
                                file_details = get_file_details(file_path, multi_folder_operation_id)
                                if file_details:
                                    # Add colors to the file details
                                    file_details['year_color'] = str(year_color)
                                    file_details['month_color'] = str(month_color)
                                    file_details['day_color'] = str(day_color)
                                    
                                    # Add file individually using add_file but don't publish events for each one
                                    file_id = self.add_file(file_details, publish_event=False)
                                    if file_id:
                                        folder_processed_count += 1
                                        total_processed_files += 1
                            except Exception as e:
                                warning(f"Error processing file {file_path}: {str(e)}")
                  # Add to results
                results['total_folders'] += 1
                results['total_files'] += folder_processed_count
                results['processed_folders'].append({
                    'folder_path': folder_path,
                    'processed_files': folder_processed_count
                })
                
                # Add operation ID to results if files were processed
                if folder_processed_count > 0 and multi_folder_operation_id not in results['item_ids']:
                    results['item_ids'].append(multi_folder_operation_id)
                
                # Log each folder processing
                log(f"Processed folder: {os.path.basename(folder_path)} - Added {folder_processed_count} files")
                
            except Exception as e:
                exception(e, f"Error processing folder {folder_path}")
        
        # Publish event only once after all folders have been processed
        if total_processed_files > 0:
            EventSystem.publish('project_data_changed')
            
        return results