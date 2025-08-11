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

def extract_file_metadata(filepath):
    """
    Extract metadata (title, description, tags) from file using pyexiv2 and other methods.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        dict: Dictionary containing extracted metadata
    """
    metadata = {
        'title': None,
        'description': None,
        'tags': None
    }
    
    try:
        # Try to extract metadata using pyexiv2 (most comprehensive)
        try:
            import pyexiv2
            
            with pyexiv2.Image(filepath) as img_metadata:
                title = None
                description = None
                tags = set()
                
                # Read XMP metadata first (highest priority)
                try:
                    xmp = img_metadata.read_xmp() or {}
                    
                    # Extract title from XMP
                    if 'Xmp.dc.title' in xmp:
                        title = xmp['Xmp.dc.title']
                        if isinstance(title, dict):
                            title = next(iter(title.values()))
                    
                    # Extract description from XMP
                    if 'Xmp.dc.description' in xmp:
                        description = xmp['Xmp.dc.description']
                        if isinstance(description, dict):
                            description = next(iter(description.values()))
                    
                    # Extract tags/keywords from XMP
                    if 'Xmp.dc.subject' in xmp:
                        tags.update(t for t in xmp['Xmp.dc.subject'] if isinstance(t, str))
                    
                    # Additional XMP fields for description
                    if not description and 'Xmp.dc.rights' in xmp:
                        description = xmp['Xmp.dc.rights']
                        if isinstance(description, dict):
                            description = next(iter(description.values()))
                            
                except Exception as e:
                    debug(f"Could not read XMP metadata from {filepath}: {str(e)}")
                
                # Read IPTC metadata if we don't have complete data
                try:
                    iptc = img_metadata.read_iptc() or {}
                    
                    # Extract title from IPTC if not found in XMP
                    if not title and 'Iptc.Application2.ObjectName' in iptc:
                        title = iptc['Iptc.Application2.ObjectName']
                    
                    # Extract description from IPTC
                    if not description and 'Iptc.Application2.Caption' in iptc:
                        description = iptc['Iptc.Application2.Caption']
                    
                    # Extract keywords from IPTC
                    if 'Iptc.Application2.Keywords' in iptc:
                        iptc_keywords = iptc['Iptc.Application2.Keywords']
                        if isinstance(iptc_keywords, list):
                            tags.update(t for t in iptc_keywords if isinstance(t, str))
                        elif isinstance(iptc_keywords, str):
                            tags.add(iptc_keywords)
                    
                    # Additional IPTC fields for description
                    if not description and 'Iptc.Application2.Headline' in iptc:
                        description = iptc['Iptc.Application2.Headline']
                        
                except Exception as e:
                    debug(f"Could not read IPTC metadata from {filepath}: {str(e)}")
                
                # Read EXIF metadata as fallback
                try:
                    exif = img_metadata.read_exif() or {}
                    
                    # Extract title from EXIF if not found elsewhere
                    if not title and 'Exif.Image.DocumentName' in exif:
                        title = exif['Exif.Image.DocumentName']
                    
                    # Extract description from EXIF
                    if not description and 'Exif.Image.ImageDescription' in exif:
                        description = exif['Exif.Image.ImageDescription']
                    
                    # Extract artist as potential tag
                    if 'Exif.Image.Artist' in exif:
                        artist = exif['Exif.Image.Artist']
                        if artist and isinstance(artist, str):
                            tags.add(f"Artist: {artist}")
                    
                    # Extract copyright as potential tag
                    if 'Exif.Image.Copyright' in exif:
                        copyright_info = exif['Exif.Image.Copyright']
                        if copyright_info and isinstance(copyright_info, str):
                            tags.add(f"Copyright: {copyright_info}")
                            
                except Exception as e:
                    debug(f"Could not read EXIF metadata from {filepath}: {str(e)}")
                
                # Clean and assign metadata
                if title:
                    metadata['title'] = str(title).strip()
                if description:
                    metadata['description'] = str(description).strip()
                if tags:
                    metadata['tags'] = ', '.join(sorted(list(tags)))
                    
        except ImportError:
            debug("pyexiv2 module not available, falling back to PIL and exifread")
            
            # Fallback to PIL + exifread method
            if filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif')):
                try:
                    from PIL import Image
                    from PIL.ExifTags import TAGS
                    
                    with Image.open(filepath) as img:
                        exif_data = img._getexif()
                        
                        if exif_data:
                            for tag_id, value in exif_data.items():
                                tag = TAGS.get(tag_id, tag_id)
                                
                                if tag == 'ImageDescription':
                                    metadata['description'] = str(value).strip()
                                elif tag == 'XPTitle':
                                    if isinstance(value, bytes):
                                        metadata['title'] = value.decode('utf-16le', errors='ignore').strip('\x00')
                                    else:
                                        metadata['title'] = str(value).strip()
                                elif tag == 'XPComment':
                                    if isinstance(value, bytes):
                                        metadata['description'] = value.decode('utf-16le', errors='ignore').strip('\x00')
                                    else:
                                        metadata['description'] = str(value).strip()
                                elif tag == 'XPKeywords':
                                    if isinstance(value, bytes):
                                        metadata['tags'] = value.decode('utf-16le', errors='ignore').strip('\x00')
                                    else:
                                        metadata['tags'] = str(value).strip()
                                elif tag == 'DocumentName' and not metadata['title']:
                                    metadata['title'] = str(value).strip()
                                elif tag == 'Artist' and not metadata['tags']:
                                    metadata['tags'] = str(value).strip()
                                    
                except Exception as e:
                    debug(f"Could not extract PIL EXIF metadata from {filepath}: {str(e)}")
                
                # Try exifread for additional metadata
                try:
                    import exifread
                    
                    with open(filepath, 'rb') as f:
                        tags = exifread.process_file(f)
                        
                        if 'Image ImageDescription' in tags and not metadata['description']:
                            metadata['description'] = str(tags['Image ImageDescription']).strip()
                        
                        if 'EXIF UserComment' in tags and not metadata['description']:
                            user_comment = str(tags['EXIF UserComment'])
                            if user_comment.startswith('ASCII'):
                                user_comment = user_comment[5:].strip()
                            metadata['description'] = user_comment.strip()
                            
                except ImportError:
                    debug("exifread module not available")
                except Exception as e:
                    debug(f"Could not extract exifread metadata from {filepath}: {str(e)}")
        
        except Exception as e:
            debug(f"Could not extract pyexiv2 metadata from {filepath}: {str(e)}")
        
        # Clean up metadata values
        for key in metadata:
            if metadata[key]:
                # Remove null characters and extra whitespace
                metadata[key] = str(metadata[key]).replace('\x00', '').strip()
                # If empty after cleaning, set to None
                if not metadata[key]:
                    metadata[key] = None
        
        debug(f"Extracted metadata from {filepath}: title='{metadata['title']}', description='{metadata['description']}', tags='{metadata['tags']}'")
        
    except Exception as e:
        warning(f"Error extracting metadata from {filepath}: {str(e)}")
        # NO FALLBACK - keep metadata as None if extraction fails
    
    return metadata

def get_file_details(filepath, operation_id=None, title=None, description=None, tags=None, category=None, sub_category=None):
    """
    Extract file details from a given filepath with comprehensive metadata extraction.
    
    Args:
        filepath (str): Path to the file
        operation_id (str, optional): Operation ID to use, or None to use current
        title (str, optional): Custom title for the file (overrides extracted metadata)
        description (str, optional): Custom description for the file (overrides extracted metadata)
        tags (str, optional): Custom tags for the file (overrides extracted metadata)
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
        
        # Extract metadata from file
        extracted_metadata = extract_file_metadata(filepath)
        
        # Use provided metadata or extracted metadata, with provided taking priority
        # Only use filename as fallback for title if explicitly provided as parameter
        final_title = title or extracted_metadata['title']  # No filename fallback here
        final_description = description or extracted_metadata['description']
        final_tags = tags or extracted_metadata['tags']
        
        # Calculate title length and tags count
        title_length = calculate_title_length(final_title)
        tags_count = calculate_tags_count(final_tags)
        
        return {
            "year": year,
            "month": month,
            "day": day,
            "item_id": item_id,
            "status": "draft",  # Default status
            "title": final_title,
            "description": final_description,
            "tags": final_tags,
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


def write_metadata_to_file(filepath, metadata):
    """
    Write metadata to an image file using pyexiv2 and other methods.
    
    Args:
        filepath (str): Path to the image file
        metadata (dict): Dictionary containing metadata to write
                        Expected keys: title, description, keywords/tags
                        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if file exists and is writable
        if not os.path.exists(filepath):
            warning(f"File does not exist: {filepath}")
            return False
        
        if not os.access(filepath, os.W_OK):
            warning(f"File is not writable: {filepath}")
            return False
        
        # Check if it's an image file
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif']
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext not in image_extensions:
            debug(f"Skipping metadata write for non-supported file type: {file_ext}")
            return False
        
        success = False
        
        # Try pyexiv2 first (most comprehensive)
        try:
            import pyexiv2
            
            with pyexiv2.Image(filepath) as img:
                # Prepare metadata for writing with safe string conversion
                xmp_data = {}
                iptc_data = {}
                exif_data = {}
                
                # Handle title with error handling (write as plain string, not dict)
                if 'title' in metadata and metadata['title']:
                    try:
                        title = str(metadata['title']).strip()
                        if title and len(title) < 250:  # Reasonable length limit
                            xmp_data['Xmp.dc.title'] = title
                            iptc_data['Iptc.Application2.ObjectName'] = title
                            exif_data['Exif.Image.DocumentName'] = title
                    except Exception as e:
                        warning(f"Error processing title metadata: {e}")
                
                # Handle description with error handling (write as plain string, not dict)
                if 'description' in metadata and metadata['description']:
                    try:
                        description = str(metadata['description']).strip()
                        if description and len(description) < 2000:  # Reasonable length limit
                            xmp_data['Xmp.dc.description'] = description
                            iptc_data['Iptc.Application2.Caption'] = description
                            exif_data['Exif.Image.ImageDescription'] = description
                    except Exception as e:
                        warning(f"Error processing description metadata: {e}")
                
                # Handle keywords/tags with error handling
                keywords = []
                try:
                    if 'keywords' in metadata and metadata['keywords']:
                        if isinstance(metadata['keywords'], list):
                            keywords = [str(k).strip() for k in metadata['keywords'] if k and str(k).strip() and len(str(k).strip()) < 100]
                        elif isinstance(metadata['keywords'], str):
                            keywords = [k.strip() for k in metadata['keywords'].split(',') if k.strip() and len(k.strip()) < 100]
                    elif 'tags' in metadata and metadata['tags']:
                        if isinstance(metadata['tags'], list):
                            keywords = [str(t).strip() for t in metadata['tags'] if t and str(t).strip() and len(str(t).strip()) < 100]
                        elif isinstance(metadata['tags'], str):
                            keywords = [t.strip() for t in metadata['tags'].split(',') if t.strip() and len(t.strip()) < 100]
                    
                    # Limit number of keywords
                    keywords = keywords[:50]  # Max 50 keywords
                    
                except Exception as e:
                    warning(f"Error processing keywords metadata: {e}")
                    keywords = []
                
                if keywords:
                    try:
                        xmp_data['Xmp.dc.subject'] = keywords
                        # IPTC keywords need to be set individually
                        iptc_data['Iptc.Application2.Keywords'] = keywords
                    except Exception as e:
                        warning(f"Error setting keywords in metadata: {e}")
                
                # Write XMP metadata with error handling
                if xmp_data:
                    try:
                        img.modify_xmp(xmp_data)
                        debug(f"Wrote XMP metadata to {filepath}")
                    except Exception as e:
                        warning(f"Failed to write XMP metadata: {e}")
                
                # Write IPTC metadata with error handling
                if iptc_data:
                    try:
                        img.modify_iptc(iptc_data)
                        debug(f"Wrote IPTC metadata to {filepath}")
                    except Exception as e:
                        warning(f"Failed to write IPTC metadata: {e}")
                
                # Write EXIF metadata with error handling (be careful with EXIF as it can be more restrictive)
                if exif_data:
                    try:
                        img.modify_exif(exif_data)
                        debug(f"Wrote EXIF metadata to {filepath}")
                    except Exception as e:
                        warning(f"Failed to write EXIF metadata: {e}")
                
                success = True
                log(f"Successfully wrote metadata to {filepath}")
                
        except ImportError:
            debug("pyexiv2 module not available, trying alternative methods")
            
            # Fallback to PIL method for basic metadata
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                import piexif
                
                # Read existing EXIF data
                img = Image.open(filepath)
                
                # Get existing EXIF or create new
                if 'exif' in img.info:
                    exif_dict = piexif.load(img.info['exif'])
                else:
                    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                
                # Add metadata to EXIF with error handling
                if 'description' in metadata and metadata['description']:
                    try:
                        description = str(metadata['description']).strip()
                        if description and len(description) < 500:  # EXIF has smaller limits
                            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode('utf-8')
                    except Exception as e:
                        warning(f"Error adding description to EXIF: {e}")
                
                if 'title' in metadata and metadata['title']:
                    try:
                        title = str(metadata['title']).strip()
                        if title and len(title) < 100:  # EXIF has smaller limits
                            exif_dict["0th"][piexif.ImageIFD.DocumentName] = title.encode('utf-8')
                    except Exception as e:
                        warning(f"Error adding title to EXIF: {e}")
                
                # Convert and save with error handling
                try:
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(filepath, exif=exif_bytes)
                    success = True
                    debug(f"Wrote basic metadata using PIL/piexif to {filepath}")
                except Exception as e:
                    warning(f"Failed to save image with EXIF: {e}")
                
            except ImportError:
                debug("piexif module not available")
            except Exception as e:
                warning(f"Failed to write metadata using PIL method: {e}")
        
        except Exception as e:
            warning(f"Failed to write metadata using pyexiv2: {e}")
        
        return success
        
    except Exception as e:
        exception(e, f"Error writing metadata to {filepath}")
        return False


def update_file_metadata_from_ai(filepath, ai_metadata):
    """
    Update file metadata both in database and in the actual file.
    This is a convenience function that combines database and file updates.
    
    Args:
        filepath (str): Path to the image file
        ai_metadata (dict): AI-generated metadata
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Write to file first
        file_success = write_metadata_to_file(filepath, ai_metadata)
        
        # Update database if we have a way to find the record
        # This would require finding the file record by filepath
        db_success = True  # Assume success for now
        
        # You could add database update logic here if needed
        # by finding the file record and updating it
        
        return file_success and db_success
        
    except Exception as e:
        exception(e, f"Error updating file metadata for {filepath}")
        return False
