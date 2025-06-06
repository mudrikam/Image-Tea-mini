import os
import datetime
from PySide6.QtWidgets import QFileDialog
from core.utils.logger import log, debug, warning, error, exception
from database.db_project_files import ProjectFilesModel

# Global operation ID - will be regenerated for each new file operation
# This ensures all files opened in one operation get the same ID
_current_operation_id = None

def get_new_operation_id():
    """
    Generate a sequential 4-digit operation ID from the database.
    
    Returns:
        str: A 4-digit sequential operation ID
    """
    global _current_operation_id
    try:
        # Get the next available ID from the database
        project_model = ProjectFilesModel()
        _current_operation_id = project_model.get_next_item_id()
        return _current_operation_id
    except Exception as e:
        # Fallback to simple incrementing if database fails
        warning(f"Failed to get sequential ID from database: {str(e)}")
        _current_operation_id = "0001"  # Default to "0001" if no previous ID exists
        return _current_operation_id

def get_image_dimensions(filepath):
    """
    Get image dimensions from file.
    
    Args:
        filepath (str): Path to the image file
        
    Returns:
        tuple: (width, height, dimensions_string) or (None, None, None) if not an image
    """
    try:
        from PIL import Image
        if filepath and os.path.exists(filepath):
            with Image.open(filepath) as img:
                width, height = img.size
                dimensions_str = f"{width} x {height}"
                return width, height, dimensions_str
    except Exception as e:
        debug(f"Could not get image dimensions for {filepath}: {str(e)}")
    return None, None, None

def get_file_type_category(extension):
    """
    Determine file type category based on extension.
    
    Args:
        extension (str): File extension without dot
        
    Returns:
        tuple: (file_type, category, sub_category)
    """
    extension = extension.lower()
    
    # Image files
    image_extensions = {
        'jpg': 'JPEG Image',
        'jpeg': 'JPEG Image', 
        'png': 'PNG Image',
        'gif': 'GIF Image',
        'bmp': 'Bitmap Image',
        'tiff': 'TIFF Image',
        'tif': 'TIFF Image',
        'webp': 'WebP Image',
        'svg': 'SVG Image',
        'ico': 'Icon File',
        'raw': 'RAW Image',
        'cr2': 'Canon RAW',
        'nef': 'Nikon RAW',
        'arw': 'Sony RAW'
    }    # Video files
    video_extensions = {
        'mp4': 'MP4 Video',
        'avi': 'AVI Video',
        'mov': 'QuickTime Video',
        'mkv': 'Matroska Video',
        'wmv': 'Windows Media Video',
        'flv': 'Flash Video',
        'webm': 'WebM Video',
        'm4v': 'M4V Video',
        '3gp': '3GP Video',
        'mpg': 'MPEG Video',
        'mpeg': 'MPEG Video',
        'ts': 'Transport Stream',
        'mts': 'AVCHD Video'
    }
    
    if extension in image_extensions:
        return image_extensions[extension], 'Image', 'Photo'
    elif extension in video_extensions:
        return video_extensions[extension], 'Video', 'Movie'
    else:
        return extension.upper() + ' File', 'Other', 'Unknown'

def calculate_title_length(title):
    """Calculate the length of title text."""
    if not title or title == '-':
        return 0
    return len(str(title))

def calculate_tags_count(tags):
    """Calculate the number of tags."""
    if not tags or tags == '-':
        return 0
    # Count tags by splitting on common separators
    tags_list = [tag.strip() for tag in str(tags).replace(',', ' ').split() if tag.strip()]
    return len(tags_list)

def get_current_operation_id():
    """
    Get the current operation ID or generate a new sequential one if none exists.
    
    Returns:
        str: The current 4-digit operation ID
    """
    global _current_operation_id
    if _current_operation_id is None:
        return get_new_operation_id()
    return _current_operation_id

def get_file_details(filepath, operation_id=None, title=None, description=None, tags=None, category=None, sub_category=None):
    """
    Extract file details from a given filepath with comprehensive metadata extraction.
    
    Args:
        filepath (str): Path to the file
        operation_id (str, optional): Operation ID to use, or None to use current
        title (str, optional): Custom title for the file
        description (str, optional): Custom description for the file
        tags (str, optional): Custom tags for the file
        category (str, optional): Custom category override
        sub_category (str, optional): Custom sub-category override
        
    Returns:
        dict: Dictionary containing comprehensive file details
    """
    try:
        filename_with_ext = os.path.basename(filepath)
        filename = os.path.splitext(filename_with_ext)[0]
        extension = os.path.splitext(filename_with_ext)[1].lower().lstrip('.')
        
        stat_info = os.stat(filepath)
        filesize = stat_info.st_size
        created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        
        # Create datetime objects for project data
        now = datetime.datetime.now()
        year = str(now.year)
        month = now.strftime('%B')  # Full month name
        day = str(now.day).zfill(2)  # Day with leading zero
        
        # Use the provided operation ID or get the current one
        item_id = operation_id or get_current_operation_id()
        
        # Get file type and category information
        file_type, auto_category, auto_sub_category = get_file_type_category(extension)
        
        # Use provided category/sub_category or auto-detected ones
        final_category = category or auto_category
        final_sub_category = sub_category or auto_sub_category
        
        # Get image dimensions if it's an image file
        image_width, image_height, dimensions = get_image_dimensions(filepath)
        
        # Use provided title or default to filename
        final_title = title or filename
        
        # Calculate title length and tags count
        title_length = calculate_title_length(final_title)
        tags_count = calculate_tags_count(tags)
        
        return {
            "year": year,
            "month": month,
            "day": day,
            "item_id": item_id,
            "status": "draft",  # Default status
            "title": final_title,
            "description": description,
            "tags": tags,
            "filename": filename,
            "extension": extension,
            "filepath": filepath,
            "filesize": filesize,
            "file_type": file_type,
            "image_width": image_width,
            "image_height": image_height,
            "dimensions": dimensions,
            "category": final_category,
            "sub_category": final_sub_category,
            "title_length": title_length,
            "tags_count": tags_count,
            "created_at": created_time,
            "updated_at": modified_time,
            "deleted_at": None
        }
    except Exception as e:
        exception(e, f"Error getting file details for {filepath}")
        return None

def select_image_file(parent=None, start_dir=None):
    """
    Open file dialog to select a single image file.
    
    Args:
        parent: Parent widget for the dialog
        start_dir: Starting directory for the dialog (defaults to user's home dir)
        
    Returns:
        dict: File details if selected, None if canceled
    """
    # Generate a new operation ID for this file selection
    operation_id = get_new_operation_id()
    
    if start_dir is None:
        start_dir = os.path.expanduser('~')
        
    file_filter = "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;All Files (*.*)"
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Image File",
        start_dir,
        file_filter
    )
    
    if filepath:
        log(f"Selected image file: {filepath} (Operation ID: {operation_id})")
        return get_file_details(filepath, operation_id)
    return None

def select_multiple_image_files(parent=None, start_dir=None):
    """
    Open file dialog to select multiple image files.
    
    Args:
        parent: Parent widget for the dialog
        start_dir: Starting directory for the dialog (defaults to user's home dir)
        
    Returns:
        list: List of file details dictionaries
    """
    # Generate a new operation ID for this file selection operation
    # All files selected in this operation will share the same ID
    operation_id = get_new_operation_id()
    
    if start_dir is None:
        start_dir = os.path.expanduser('~')
        
    file_filter = "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;All Files (*.*)"
    filepaths, _ = QFileDialog.getOpenFileNames(
        parent,
        "Select Image Files",
        start_dir,
        file_filter
    )
    
    results = []
    for filepath in filepaths:
        details = get_file_details(filepath, operation_id)
        if details:
            results.append(details)
    
    log(f"Selected {len(results)} image files (Operation ID: {operation_id})")
    return results

def select_folder(parent=None, start_dir=None):
    """
    Open dialog to select a folder.
    
    Args:
        parent: Parent widget for the dialog
        start_dir: Starting directory for the dialog (defaults to user's home dir)
        
    Returns:
        str: Selected folder path or None if canceled
    """
    if start_dir is None:
        start_dir = os.path.expanduser('~')
        
    folder_path = QFileDialog.getExistingDirectory(
        parent,
        "Select Folder",
        start_dir
    )
    
    if folder_path:
        log(f"Selected folder: {folder_path}")
        return folder_path
    return None

def select_multiple_folders(parent=None, start_dir=None):
    """
    Open dialog to select multiple folders (using a workaround since Qt doesn't support this natively).
    
    Args:
        parent: Parent widget for the dialog
        start_dir: Starting directory for the dialog (defaults to user's home dir)
        
    Returns:
        list: List of selected folder paths
    """
    results = []
    keep_selecting = True
    
    while keep_selecting:
        folder_path = select_folder(parent, start_dir)
        if folder_path:
            results.append(folder_path)
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                parent, 
                "Select Another Folder?",
                "Do you want to select another folder?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            keep_selecting = (reply == QMessageBox.Yes)
            
            # Update the start dir to the parent of the selected folder for convenience
            if keep_selecting:
                start_dir = os.path.dirname(folder_path)
        else:
            keep_selecting = False
    
    log(f"Selected {len(results)} folders")
    return results

def select_video_file(parent=None, start_dir=None):
    """
    Open file dialog to select a video file.
    
    Args:
        parent: Parent widget for the dialog
        start_dir: Starting directory for the dialog (defaults to user's home dir)
        
    Returns:
        dict: File details if selected, None if canceled
    """
    # Generate a new operation ID for this file selection
    operation_id = get_new_operation_id()
    
    if start_dir is None:
        start_dir = os.path.expanduser('~')
        
    file_filter = "Video Files (*.mp4 *.mov *.avi *.mkv *.wmv);;All Files (*.*)"
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Video File",
        start_dir,
        file_filter
    )
    
    if filepath:
        log(f"Selected video file: {filepath} (Operation ID: {operation_id})")
        return get_file_details(filepath, operation_id)
    return None

def select_multiple_video_files(parent=None, start_dir=None):
    """
    Open file dialog to select multiple video files.
    
    Args:
        parent: Parent widget for the dialog
        start_dir: Starting directory for the dialog (defaults to user's home dir)
        
    Returns:
        list: List of file details dictionaries
    """
    # Generate a new operation ID for this file selection operation
    # All files selected in this operation will share the same ID
    operation_id = get_new_operation_id()
    
    if start_dir is None:
        start_dir = os.path.expanduser('~')
        
    file_filter = "Video Files (*.mp4 *.mov *.avi *.mkv *.wmv);;All Files (*.*)"
    filepaths, _ = QFileDialog.getOpenFileNames(
        parent,
        "Select Video Files",
        start_dir,
        file_filter
    )
    
    results = []
    for filepath in filepaths:
        details = get_file_details(filepath, operation_id)
        if details:
            results.append(details)
    
    log(f"Selected {len(results)} video files (Operation ID: {operation_id})")
    return results

def get_image_extensions():
    """
    Get a list of supported image file extensions.
    
    Returns:
        list: List of image file extensions including the dot (e.g., ['.jpg', '.png'])
    """
    return [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.tiff', '.tif', '.webp', '.svg', '.raw',
        '.heif', '.heic', '.ico', '.psd'
    ]


def get_video_extensions():
    """
    Get a list of supported video file extensions.
    
    Returns:
        list: List of video file extensions including the dot (e.g., ['.mp4', '.avi'])
    """
    return [
        '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.webm', '.mkv', '.m4v', '.3gp', '.mpg',
        '.mpeg', '.ts', '.mts'
    ]
