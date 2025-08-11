from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QTimer
from core.utils.logger import log, debug, warning, error, exception

class TableManager:
    """Helper class for managing table data and visualization."""
    
    def __init__(self):
        """Initialize the table manager."""
        pass
        
    def update_table_data(self, table_widget, item_id):
        """Update the table data for a specific item tab."""
        debug(f"TableManager update_table_data called for item_id: {item_id}")
        
        if not table_widget:
            warning(f"Table widget not provided for item {item_id}")
            return 0
        
        try:
            # Get the actual ID part from the item_id
            parts = item_id.split('_')
            debug(f"Item ID parts: {parts}")
            
            if len(parts) < 2:
                warning(f"Invalid item ID format: {item_id}")
                return 0
                
            actual_id = parts[1]
            debug(f"Using actual_id: {actual_id} for database lookup")
            
            # Get data from the database
            try:
                from database.db_project_files import ProjectFilesModel
                debug(f"Fetching files from database for item_id: {actual_id}")
                model = ProjectFilesModel()
                files_data = model.get_files_by_item_id(actual_id)
                debug(f"Found {len(files_data) if files_data else 0} files from database")
            except Exception as e:
                exception(e, "Error getting data from database")
                files_data = []
                # Return early to prevent further issues
                return 0
            
            # Make sure vertical header (row numbers) is visible
            table_widget.verticalHeader().setVisible(True)
            
            # Configure table selection behavior for full row selection
            table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            
            # Enable clicking on row headers to select entire rows
            table_widget.verticalHeader().setSectionsClickable(True)
            table_widget.verticalHeader().setHighlightSections(True)
            
            # Clear existing table data
            table_widget.setRowCount(0)
            
            # Get the number of files
            file_count = len(files_data) if files_data else 0
            
            # Add data to the table
            if files_data and len(files_data) > 0:
                # Set row count for the data we have
                table_widget.setRowCount(len(files_data))
                
                # Add each row of data
                for row_idx, file_info in enumerate(files_data):                    # Get data from file info
                    filename = str(file_info.get('filename', ''))
                    extension = str(file_info.get('extension', ''))
                    file_id = file_info.get('id')
                    item_id = str(file_info.get('item_id', ''))
                    status = str(file_info.get('status', ''))
                    title = str(file_info.get('title', ''))
                    description = str(file_info.get('description', ''))
                    tags = str(file_info.get('tags', ''))
                    filepath = str(file_info.get('filepath', ''))
                    file_type = str(file_info.get('file_type', ''))
                    category = str(file_info.get('category', ''))
                    sub_category = str(file_info.get('sub_category', ''))
                    dimensions = str(file_info.get('dimensions', ''))
                    
                    # Truncate long filenames and filepaths for display
                    MAX_FILENAME_LENGTH = 25
                    MAX_FILEPATH_LENGTH = 30
                    MAX_DESCRIPTION_LENGTH = 40
                    
                    # Truncate filename if needed
                    if len(filename) > MAX_FILENAME_LENGTH:
                        truncated_filename = f"{filename[:MAX_FILENAME_LENGTH-3]}..."
                    else:
                        truncated_filename = filename
                        
                    # Truncate filepath if needed
                    if len(filepath) > MAX_FILEPATH_LENGTH:
                        truncated_filepath = f"{filepath[:15]}...{filepath[-15:]}"
                    else:
                        truncated_filepath = filepath
                    
                    # Truncate description if needed
                    if len(description) > MAX_DESCRIPTION_LENGTH:
                        truncated_description = f"{description[:MAX_DESCRIPTION_LENGTH-3]}..."
                    else:
                        truncated_description = description
                        # Get pre-calculated metadata values from database
                    title_length = file_info.get('title_length', 0)
                    tags_count = file_info.get('tags_count', 0)
                    filesize = file_info.get('filesize', 0)
                    description_length = len(description)  # Calculate description length here
                    
                    # Create table items
                    filename_item = QtWidgets.QTableWidgetItem(truncated_filename)
                    extension_item = QtWidgets.QTableWidgetItem(extension)
                    id_item = QtWidgets.QTableWidgetItem(str(file_id)) if file_id is not None else QtWidgets.QTableWidgetItem("")
                    item_id_item = QtWidgets.QTableWidgetItem(item_id)
                    status_item = QtWidgets.QTableWidgetItem(status)
                    title_item = QtWidgets.QTableWidgetItem(title)
                    description_item = QtWidgets.QTableWidgetItem(truncated_description)
                    tags_item = QtWidgets.QTableWidgetItem(tags)
                    title_length_item = QtWidgets.QTableWidgetItem(str(title_length))
                    description_length_item = QtWidgets.QTableWidgetItem(str(description_length))
                    tags_count_item = QtWidgets.QTableWidgetItem(str(tags_count))
                    filepath_item = QtWidgets.QTableWidgetItem(truncated_filepath)
                    
                    # Set tooltip to show full content when hovering
                    filename_item.setToolTip(filename)
                    filepath_item.setToolTip(filepath)
                    description_item.setToolTip(description)
                    tags_item.setToolTip(tags)
                    
                    # Store the full file_info in the user data of the filename item
                    # This allows us to retrieve it later when an item is clicked
                    filename_item.setData(QtCore.Qt.UserRole, file_info)
                      # Set items in the table
                    table_widget.setItem(row_idx, 0, filename_item)
                    table_widget.setItem(row_idx, 1, extension_item)
                    table_widget.setItem(row_idx, 2, id_item)
                    table_widget.setItem(row_idx, 3, item_id_item)
                    table_widget.setItem(row_idx, 4, status_item)
                    table_widget.setItem(row_idx, 5, title_item)
                    table_widget.setItem(row_idx, 6, description_item)
                    table_widget.setItem(row_idx, 7, tags_item)
                    table_widget.setItem(row_idx, 8, title_length_item)
                    table_widget.setItem(row_idx, 9, description_length_item)
                    table_widget.setItem(row_idx, 10, tags_count_item)
                    table_widget.setItem(row_idx, 11, filepath_item)
                    
                    # Apply row color based on status - this ensures initial colors are set
                    try:
                        self.apply_status_color_to_row(table_widget, row_idx, status)
                        debug(f"Applied initial {status} color to row {row_idx}")
                    except Exception as color_error:
                        warning(f"Failed to apply color to row {row_idx}: {color_error}")
            else:                # No data found - add a single row with a message
                table_widget.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No files found")
                table_widget.setItem(0, 0, no_data_item)
                table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 2, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 3, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 4, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 5, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 6, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 7, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 8, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 9, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 10, QtWidgets.QTableWidgetItem(""))
                table_widget.setItem(0, 11, QtWidgets.QTableWidgetItem(""))
            
            # Resize columns to content
            table_widget.resizeColumnsToContents()
            
            # Final color refresh to ensure all status colors are properly applied
            if files_data and len(files_data) > 0:
                debug("Performing final color refresh after table population")
                try:
                    for row_idx, file_info in enumerate(files_data):
                        status = file_info.get('status', 'draft')
                        self.apply_status_color_to_row(table_widget, row_idx, status)
                    table_widget.viewport().update()
                    debug("Final color refresh completed successfully")
                except Exception as final_color_error:
                    warning(f"Error in final color refresh: {final_color_error}")
            
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
                    data = {                        'row': row,
                        'filename': table_widget.item(row, 0).text() if table_widget.item(row, 0) else '',
                        'extension': table_widget.item(row, 1).text() if table_widget.item(row, 1) else '',
                        'id': table_widget.item(row, 2).text() if table_widget.item(row, 2) else '',
                        'item_id': table_widget.item(row, 3).text() if table_widget.item(row, 3) else '',
                        'status': table_widget.item(row, 4).text() if table_widget.item(row, 4) else '',
                        'title': table_widget.item(row, 5).text() if table_widget.item(row, 5) else '',
                        'description': table_widget.item(row, 6).text() if table_widget.item(row, 6) else '',
                        'tags': table_widget.item(row, 7).text() if table_widget.item(row, 7) else '',
                        'title_length': table_widget.item(row, 8).text() if table_widget.item(row, 8) else '',
                        'description_length': table_widget.item(row, 9).text() if table_widget.item(row, 9) else '',
                        'tags_count': table_widget.item(row, 10).text() if table_widget.item(row, 10) else '',
                        'filepath': table_widget.item(row, 11).text() if table_widget.item(row, 11) else '',
                    }
                
                # Call the callback function with the row, column, and data
                callback_function(row, column, data)
        except Exception as e:
            exception(e, "Error handling table item click")
    
    def apply_status_color_to_row(self, table_widget, row_index, status):
        """
        Apply color to a table row based on file status.
        
        Args:
            table_widget: The table widget to modify
            row_index: The row index to color
            status: The status to determine color ('draft', 'generating', 'finished', 'failed')
        """
        try:
            # Validate inputs to prevent crashes
            if not table_widget:
                warning("Table widget is None, cannot apply color")
                return
            
            if row_index < 0 or row_index >= table_widget.rowCount():
                warning(f"Row index {row_index} out of bounds (table has {table_widget.rowCount()} rows)")
                return
            
            if not status:
                debug(f"Empty status for row {row_index}, using default")
                status = 'draft'
            
            # Define status colors
            status_colors = {
                'draft': QtGui.QColor(240, 240, 240, 100),      # Light gray
                'generating': QtGui.QColor(255, 255, 0, 150),   # Yellow
                'finished': QtGui.QColor(144, 238, 144, 150),   # Light green
                'failed': QtGui.QColor(255, 182, 193, 150),     # Light red
            }
            
            # Get color for status (default to transparent if status not found)
            color = status_colors.get(status.lower(), QtGui.QColor(255, 255, 255, 0))
            
            # Apply color to all columns in the row with error handling
            columns_updated = 0
            for column in range(table_widget.columnCount()):
                try:
                    item = table_widget.item(row_index, column)
                    if item:
                        brush = QtGui.QBrush(color)
                        item.setBackground(brush)
                        
                        # Set text color for contrast
                        if status.lower() == 'failed':
                            item.setForeground(QtGui.QBrush(QtGui.QColor(139, 0, 0)))  # Dark red text
                        elif status.lower() == 'finished':
                            item.setForeground(QtGui.QBrush(QtGui.QColor(0, 100, 0)))  # Dark green text
                        elif status.lower() == 'generating':
                            item.setForeground(QtGui.QBrush(QtGui.QColor(255, 215, 0)))  # Gold/yellow text for yellow background
                        else:
                            item.setForeground(QtGui.QBrush())  # Default color for draft
                        
                        columns_updated += 1
                except Exception as item_error:
                    warning(f"Error setting color for row {row_index}, column {column}: {item_error}")
                    continue
            
            debug(f"Applied {status} color to row {row_index} ({columns_updated} columns updated)")
            
        except Exception as e:
            warning(f"Error applying status color to row {row_index}: {e}")
            exception(e, f"Full error in apply_status_color_to_row")
    
    def refresh_table_colors(self, table_widget, item_id):
        """
        Refresh all row colors in the table based on current database status.
        
        Args:
            table_widget: The table widget to refresh
            item_id: The item_id to get fresh data from database
        """
        try:
            debug(f"Starting refresh_table_colors for item_id: {item_id}")
            
            # Validate inputs
            if not table_widget:
                warning("Table widget is None, cannot refresh colors")
                return
            
            if not item_id:
                warning("Item ID is None, cannot refresh colors")
                return
            
            # Get fresh data from database with error handling
            parts = item_id.split('_')
            if len(parts) < 2:
                warning(f"Invalid item_id format for refresh: {item_id}")
                return
            
            actual_id = parts[1]
            debug(f"Refreshing colors for actual_id: {actual_id}")
            
            # Get fresh database data with better error handling
            try:
                from database.db_project_files import ProjectFilesModel
                model = ProjectFilesModel()
                files_data = model.get_files_by_item_id(actual_id)
                debug(f"Retrieved {len(files_data) if files_data else 0} files for color refresh")
            except Exception as db_error:
                warning(f"Database error during color refresh: {db_error}")
                return
            
            if not files_data:
                debug("No files data retrieved, skipping color refresh")
                return
            
            # Update colors for each row with bounds checking
            current_row_count = table_widget.rowCount()
            debug(f"Table has {current_row_count} rows, data has {len(files_data)} items")
            
            for row_idx, file_info in enumerate(files_data):
                # Check bounds to prevent index errors
                if row_idx >= current_row_count:
                    warning(f"Row index {row_idx} exceeds table row count {current_row_count}")
                    break
                
                try:
                    status = file_info.get('status', 'draft')
                    debug(f"Applying color refresh for row {row_idx} with status: {status}")
                    self.apply_status_color_to_row(table_widget, row_idx, status)
                except Exception as color_error:
                    warning(f"Error applying color to row {row_idx}: {color_error}")
                    continue
            
            # Force table refresh with error handling - avoid recursive repaint
            try:
                table_widget.viewport().update()
                debug(f"Successfully refreshed table colors for item_id: {item_id}")
            except Exception as refresh_error:
                warning(f"Error during table viewport update: {refresh_error}")
                
        except Exception as e:
            warning(f"Error refreshing table colors: {e}")
            exception(e, f"Full error during refresh_table_colors for item_id: {item_id}")
