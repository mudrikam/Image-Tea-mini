# filepath: z:\Build\Image-Tea-mini\database\db_workspace.py
import os
import sqlite3
from datetime import datetime
from core.utils.logger import log, debug, warning, error, exception
from database.db_config import connect_to_database, close_database_connection
from database.db_project_files import ProjectFilesModel

class WorkspaceDataModel:
    """
    Model class to handle workspace-related database operations.
    This class is used by the workspace controller and the drag-and-drop handler
    to interact with the database.
    """
    
    def __init__(self):
        """Initialize the model."""
        self.project_model = ProjectFilesModel()
        self.table_name = "project_data"
    
    def add_files_from_drop(self, file_details_list):
        """
        Add files from a drag-and-drop operation to the database.
        
        Args:
            file_details_list (list): List of dictionaries containing file details
            
        Returns:
            str: Item ID used for the operation
        """
        if not file_details_list:
            return None
            
        # All files from the same drop operation share the same item_id
        try:
            # Use existing add_multiple_files method from ProjectFilesModel
            self.project_model.add_multiple_files(file_details_list)
            
            # Return the item_id that was used
            return file_details_list[0]['item_id']
        except Exception as e:
            exception(e, "Error adding files from drop operation")
            return None
    
    def process_dropped_folder(self, folder_path):
        """
        Process a folder that was dropped into the application.
        
        Args:
            folder_path (str): Path to the dropped folder
            
        Returns:
            str: Item ID used for the operation
        """
        try:
            # Use the existing process_folder method from ProjectFilesModel
            result = self.project_model.process_folder(folder_path)
            
            if result and isinstance(result, dict) and 'item_id' in result:
                return result['item_id']
                
            return None
        except Exception as e:
            exception(e, f"Error processing dropped folder: {folder_path}")
            return None
    
    def process_multiple_dropped_folders(self, folder_paths):
        """
        Process multiple folders that were dropped into the application.
        
        Args:
            folder_paths (list): List of paths to dropped folders
            
        Returns:
            list: List of item IDs used for the operations
        """
        item_ids = []
        
        for folder_path in folder_paths:
            item_id = self.process_dropped_folder(folder_path)
            if item_id:
                item_ids.append(item_id)
                
        return item_ids
    
    def get_files_by_item_id(self, item_id):
        """
        Get all files associated with a specific item ID.
        
        Args:
            item_id (str): The item ID to query
            
        Returns:
            list: List of file records
        """
        return self.project_model.get_files_by_item_id(item_id)
        
    def update_status(self, item_id, status):
        """
        Update the status for all files with a specific item ID.
        
        Args:
            item_id (str): The item ID to update
            status (str): The new status
            
        Returns:
            bool: Success or failure
        """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            query = f"""
                UPDATE {self.table_name}
                SET status = ?, updated_at = ?
                WHERE item_id = ?
            """
            
            now = datetime.now().isoformat()
            cursor.execute(query, (status, now, item_id))
            conn.commit()
            
            affected_rows = cursor.rowcount
            close_database_connection(conn)
            
            if affected_rows > 0:
                debug(f"Updated status to '{status}' for {affected_rows} files with item_id {item_id}")
                return True
            else:
                warning(f"No files found with item_id {item_id} to update status")
                return False
                
        except sqlite3.Error as e:
            error(f"Database error when updating status: {e}")
            return False
        except Exception as e:
            exception(e, f"Error updating status for item_id {item_id}")
            return False