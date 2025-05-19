from PySide6 import QtWidgets
from core.utils.logger import log, debug, warning, error, exception

class TableManager:
    """Helper class for managing table data and visualization."""
    
    def __init__(self):
        """Initialize the table manager."""
        pass
    
    def update_table_data(self, table_widget, item_id):
        """Update the table data for a specific item tab."""
        if not table_widget:
            warning(f"Table widget not provided for item {item_id}")
            return 0
        
        try:
            # Get the actual ID part from the item_id
            parts = item_id.split('_')
            if len(parts) < 2:
                warning(f"Invalid item ID format: {item_id}")
                return 0
                
            actual_id = parts[1]
            
            # Get data from the database
            try:
                from database.db_project_files import ProjectFilesModel
                files_data = ProjectFilesModel().get_files_by_item_id(actual_id)
            except Exception as e:
                exception(e, "Error getting data from database")
                files_data = []
            
            # Make sure vertical header (row numbers) is visible
            table_widget.verticalHeader().setVisible(True)
            
            # Clear existing table data
            table_widget.setRowCount(0)
            
            # Get the number of files
            file_count = len(files_data) if files_data else 0
            
            # Add data to the table
            if files_data and len(files_data) > 0:
                # Set row count for the data we have
                table_widget.setRowCount(len(files_data))
                
                # Add each row of data
                for row_idx, file_info in enumerate(files_data):
                    # Get data from file info
                    filename = str(file_info.get('filename', ''))
                    extension = str(file_info.get('extension', ''))
                    
                    # Truncate long filenames for display
                    MAX_FILENAME_LENGTH = 25
                    if len(filename) > MAX_FILENAME_LENGTH:
                        # Truncate and add ellipsis
                        truncated_filename = f"{filename[:MAX_FILENAME_LENGTH-3]}..."
                    else:
                        truncated_filename = filename
                    
                    # Create table items
                    filename_item = QtWidgets.QTableWidgetItem(truncated_filename)
                    extension_item = QtWidgets.QTableWidgetItem(extension)
                    
                    # Set tooltip to show full filename when hovering
                    filename_item.setToolTip(filename)
                    
                    # Set items in the table
                    table_widget.setItem(row_idx, 0, filename_item)
                    table_widget.setItem(row_idx, 1, extension_item)
                
            else:
                # No data found - add a single row with a message
                table_widget.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No files found")
                table_widget.setItem(0, 0, no_data_item)
                table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
            
            # Resize columns to content
            table_widget.resizeColumnsToContents()
            
            return file_count
            
        except Exception as e:
            exception(e, f"Error updating table data for item {item_id}")
            return 0
    
    def format_size(self, size):
        """Format file size to human readable format."""
        if not size:
            return ""
            
        if size > 1024*1024:
            return f"{size/(1024*1024):.2f} MB"
        elif size > 1024:
            return f"{size/1024:.2f} KB"
        else:
            return f"{size} bytes"
