import os
import datetime
from PySide6.QtWidgets import QFileDialog
from core.utils.logger import log, debug, warning, error, exception

def get_file_details(filepath):
    """
    Extract file details from a given filepath.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        dict: Dictionary containing file details
    """
    try:
        filename = os.path.basename(filepath)
        extension = os.path.splitext(filename)[1].lower().lstrip('.')
        
        stat_info = os.stat(filepath)
        filesize = stat_info.st_size
        created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        
        # Create datetime objects for project data
        now = datetime.datetime.now()
        year = str(now.year)
        month = now.strftime('%B')  # Full month name
        day = str(now.day).zfill(2)  # Day with leading zero
        
        # Generate item_id based on timestamp
        item_id = now.strftime('%y%m%d%H%M%S')
        
        return {
            "year": year,
            "month": month,
            "day": day,
            "item_id": item_id,
            "status": "draft",  # Default status
            "filename": filename,
            "extension": extension,
            "filepath": filepath,
            "filesize": filesize,
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
        log(f"Selected image file: {filepath}")
        return get_file_details(filepath)
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
        details = get_file_details(filepath)
        if details:
            results.append(details)
    
    log(f"Selected {len(results)} image files")
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
        log(f"Selected video file: {filepath}")
        return get_file_details(filepath)
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
        details = get_file_details(filepath)
        if details:
            results.append(details)
    
    log(f"Selected {len(results)} video files")
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
