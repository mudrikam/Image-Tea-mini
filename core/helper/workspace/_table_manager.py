from PySide6 import QtWidgets, QtCore
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
                    file_id = file_info.get('id')
                    
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
                    
                    # Store the full file_info in the user data of the filename item
                    # This allows us to retrieve it later when an item is clicked
                    filename_item.setData(QtCore.Qt.UserRole, file_info)
                    
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

    def setup_table_click_handler(self, table_widget, callback_function):
        """
        Set up a click handler for a table widget.
        
        Args:
            table_widget: The table widget to set up the click handler for
            callback_function: The function to call when an item is clicked
                               Should accept parameters: row, column, data_dict
        """
        if not table_widget:
            warning("Table widget not provided, can't set up click handler")
            return
            
        # Connect the itemClicked signal to our handler
        table_widget.itemClicked.connect(
            lambda item: self._handle_table_item_clicked(table_widget, item, callback_function)
        )
        
    def _handle_table_item_clicked(self, table_widget, item, callback_function):
        """
        Handle a table item being clicked.
        
        Args:
            table_widget: The table widget that was clicked
            item: The item that was clicked
            callback_function: The function to call with the data
        """
        if not item or not callback_function:
            return
            
        # Get the row and column of the clicked item
        row = item.row()
        column = item.column()
        
        try:
            # Get data from the row - assuming ID or numerical identifier in hidden data
            id_item = table_widget.item(row, 0)  # Assuming ID is stored in first column or its data
            if id_item:
                # Get the item data (could be stored in Qt.UserRole)
                data = id_item.data(QtCore.Qt.UserRole)
                if not data:
                    # If no specific data stored, create a dictionary with the visible data
                    data = {
                        'row': row,
                        'filename': table_widget.item(row, 0).text() if table_widget.item(row, 0) else '',
                        'extension': table_widget.item(row, 1).text() if table_widget.item(row, 1) else '',
                        # Add more fields as needed
                    }
                
                # Call the callback function with the row, column, and data
                callback_function(row, column, data)
        except Exception as e:
            exception(e, "Error handling table item click")
