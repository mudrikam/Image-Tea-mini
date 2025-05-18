import os
import sqlite3
from datetime import datetime
from core.utils.logger import log, debug, warning, error, exception
from database.db_config import connect_to_database, close_database_connection
from core.utils.event_system import EventSystem

class ProjectFilesModel:
    """
    Model class to handle project files database operations.
    """
    
    def __init__(self):
        """Initialize the model."""
        self.table_name = "project_data"
    
    def add_file(self, file_details):
        """
        Add a file to the project database.
        
        Args:
            file_details (dict): Dictionary containing file details
            
        Returns:
            bool or int: Record ID if successful, False otherwise
        """
        try:
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
            
            # Publish event to notify listeners that data has changed
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
            result = self.add_file(file_details)
            if result:  # If add_file returns the ID (not False)
                success_ids.append(result)
        
        log(f"Added {len(success_ids)}/{len(file_details_list)} files to database")
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
            tuple: (None, processed_count) - ID is always None, and count of processed files
        """
        # We're not adding the folder itself to the database, just processing its contents
        folder_id = None
        processed_count = 0
        
        try:
            from core.global_operations.file_operations import get_image_extensions, get_video_extensions, get_file_details
            
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
                            # Reuse the get_file_details function to get consistent file details
                            file_details = get_file_details(file_path)
                            if file_details:
                                # Add file individually using add_file
                                file_id = self.add_file(file_details)
                                if file_id:
                                    processed_count += 1
                        except Exception as e:
                            warning(f"Error processing file {file_path}: {str(e)}")
        
        except Exception as e:
            exception(e, f"Error processing folder {folder_path}")
        
        return folder_id, processed_count
    
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
            'processed_folders': []
        }
        
        if not folder_paths:
            return results
            
        for folder_path in folder_paths:
            # Handle both string paths and dictionary folder details
            if isinstance(folder_path, dict):
                folder_path = folder_path.get('filepath', '')
                
            if not folder_path or not os.path.isdir(folder_path):
                continue
                
            # Process the folder without passing folder details
            _, processed_count = self.process_folder(folder_path)
            
            # Add to results
            results['total_folders'] += 1
            results['total_files'] += processed_count
            results['processed_folders'].append({
                'folder_path': folder_path,
                'processed_files': processed_count
            })
            
            # Log each folder processing
            log(f"Processed folder: {os.path.basename(folder_path)} - Added {processed_count} files")
        
        return results
