import os
import re
import time
import json
import shutil
import zipfile
import tempfile
import threading
import subprocess
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtCore import Qt, QMetaObject, Signal, QObject, QUrl
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QDesktopServices


class UpdateSignals(QObject):
    """Signals for update process thread communication."""
    progress = Signal(int, str)  # Progress value and status message
    complete = Signal(bool, str)  # Success status and message
    error = Signal(str)  # Error message


def launch_app_updater(parent, config, base_dir):
    """Launch the application updater window.
    
    Args:
        parent: The parent window
        config: The application configuration
        base_dir: The base directory of the application
    """
    # Load the UI file for the app updater dialog
    ui_path = os.path.join(base_dir, "gui", "app_updater_window.ui")
    
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    dialog = loader.load(ui_file, parent)
    ui_file.close()
      # Set window title
    app_name = config.get("app_name", "Image Tea Mini")
    app_version = config.get("app_remote_version", "")
    app_hash = config.get("app_remote_commit_hash", "")
    dialog.setWindowTitle(f"{app_name} Updater - v{app_version}")
      # Display appropriate title and explanation
    dialog.lblTitle.setText(f"Updating {app_name} to v{app_version}")
    
    # Replace placeholders in the explanation text
    explanation_text = dialog.label.text()
    explanation_text = explanation_text.replace("%version%", app_version)
    explanation_text = explanation_text.replace("%hash%", app_hash[:7] if app_hash else "unknown")
    dialog.label.setText(explanation_text)
    
    # Add status label for progress updates if not already in UI
    if not hasattr(dialog, 'lblStatus'):
        dialog.lblStatus = QtWidgets.QLabel(dialog)
        dialog.lblStatus.setText("Ready to update...")
        dialog.lblStatus.setAlignment(Qt.AlignCenter)
        dialog.verticalLayout.insertWidget(dialog.verticalLayout.indexOf(dialog.progressBar), dialog.lblStatus)
    
    # Initialize the progress bar
    dialog.progressBar.setValue(0)
      # Connect the Cancel button
    dialog.btnCancel.clicked.connect(dialog.reject)
    
    # Connect the Proceed button
    dialog.pushButton.clicked.connect(lambda: start_update_process(dialog, config, base_dir))
    dialog.pushButton.setEnabled(False)
    
    # Connect the checkbox to enable/disable the Proceed button
    dialog.checkBox.stateChanged.connect(lambda state: dialog.pushButton.setEnabled(state == Qt.CheckState.Checked.value))
      
    # Make the dialog modal (blocks interaction with parent window)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    # Center the dialog on the screen
    center_on_screen(dialog)
    
    # Show the dialog as modal
    dialog.exec()
    return dialog


def center_on_screen(window):
    """Center a window on the screen."""
    screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
    window_size = window.frameGeometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)


def start_update_process(dialog, config, base_dir):
    """Start the update process.
    
    Args:
        dialog: The updater dialog
        config: The application configuration
        base_dir: The base directory of the application
    """
    # Disable the buttons to prevent multiple clicks
    dialog.pushButton.setEnabled(False)
    dialog.btnCancel.setEnabled(False)
    
    # Create signals for thread communication
    signals = UpdateSignals()
    
    # Connect signals to update the UI
    signals.progress.connect(lambda value, message: update_progress(dialog, value, message))
    signals.complete.connect(lambda success, message: update_complete(dialog, success, message, base_dir))
    signals.error.connect(lambda message: update_error(dialog, message))
    
    # Start update process in a separate thread
    update_thread = threading.Thread(
        target=perform_update,
        args=(config, base_dir, signals)
    )
    update_thread.daemon = True
    update_thread.start()


def update_progress(dialog, value, message):
    """Update the progress bar and message in the UI.
    
    Args:
        dialog: The updater dialog
        value: Progress percentage (0-100)
        message: Status message to display
    """
    QMetaObject.invokeMethod(
        dialog.progressBar,
        "setValue",
        Qt.ConnectionType.QueuedConnection,
        QtCore.Q_ARG(int, value)
    )
    
    # If dialog has a status label, update it
    if hasattr(dialog, 'lblStatus'):
        QMetaObject.invokeMethod(
            dialog.lblStatus,
            "setText",
            Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, message)
        )
    

def update_complete(dialog, success, message, base_dir):
    """Handle the completion of the update process.
    
    Args:
        dialog: The updater dialog
        success: Whether the update was successful
        message: Message to display
        base_dir: Base directory of the application
    """
    if success:
        # Complete the progress bar immediately
        dialog.progressBar.setValue(100)
        
        # Force immediate UI update
        QtCore.QCoreApplication.processEvents()
        
        # Ask user if they want to restart the application
        reply = QMessageBox.question(
            dialog,
            "Update Complete",
            f"{message}\n\nDo you want to restart the application now?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Close the dialog
            dialog.accept()
            
            # Get the path to Launcher.bat
            launcher_path = os.path.join(base_dir, "Launcher.bat")
            
            # Check if Launcher.bat exists
            if os.path.exists(launcher_path):
                # Start a new process to launch the application after a short delay
                # Use subprocess.Popen to avoid blocking
                subprocess.Popen(
                    f'cmd /c "timeout /t 1 && start "" "{launcher_path}""',
                    shell=True
                )
                
                # Get the main application window and close it
                main_window = dialog.parent()
                if main_window:
                    main_window.close()
            else:
                QMessageBox.warning(
                    dialog,
                    "Restart Failed",
                    f"Could not find launcher at: {launcher_path}\n"
                    "Please manually restart the application.",
                    QMessageBox.Ok
                )
        else:
            # Just close the dialog
            dialog.accept()
    else:
        # Show an error message
        QMessageBox.warning(
            dialog,
            "Update Failed",
            message,
            QMessageBox.Ok
        )
        
        # Re-enable the cancel button
        dialog.btnCancel.setEnabled(True)


def update_error(dialog, message):
    """Handle errors during the update process.
    
    Args:
        dialog: The updater dialog
        message: Error message to display
    """
    QMessageBox.critical(
        dialog,
        "Update Error",
        f"An error occurred during the update process:\n\n{message}",
        QMessageBox.Ok
    )
    
    # Re-enable the cancel button
    dialog.btnCancel.setEnabled(True)


def perform_update(config, base_dir, signals):
    """Perform the actual update process in a background thread.
    
    Args:
        config: The application configuration
        base_dir: Base directory of the application
        signals: UpdateSignals instance for thread communication
    """
    try:
        # Step 1: Check internet connection (10%)
        signals.progress.emit(5, "Checking internet connection...")
        if not check_internet_connection():
            signals.error.emit("No internet connection. Please check your connection and try again.")
            return
        
        # Step 2: Check if GitHub is accessible (15%)
        signals.progress.emit(10, "Checking GitHub accessibility...")
        if not check_github_accessible():
            signals.error.emit("Cannot access GitHub. Please check your internet connection and try again.")
            return
          # Step 3: Get latest release info (20%)
        signals.progress.emit(15, "Getting latest release information...")
        github_url = config.get("app_update_url", "")
        repo_info = extract_repo_info(github_url)
        if not repo_info:
            signals.error.emit("Failed to parse GitHub repository information.")
            return
        
        username, repo_name = repo_info
        latest_release = get_latest_release_info(username, repo_name)
        if not latest_release:
            signals.error.emit("Failed to retrieve release information from GitHub.")
            return
        
        # Step 4: Setup the download for source code ZIP from GitHub (25%)
        signals.progress.emit(20, "Finding download package...")
        tag_name = latest_release.get('tag_name')
        if not tag_name:
            signals.error.emit("No tag name found in the latest release.")
            return
            
        # GitHub automatically provides source code archives for each release
        # Format: https://github.com/{username}/{repo}/archive/refs/tags/{tag_name}.zip
        download_url = f"https://github.com/{username}/{repo_name}/archive/refs/tags/{tag_name}.zip"
        zip_filename = f"{repo_name}-{tag_name}.zip"
          # Step 5: Download the ZIP file (50%)
        signals.progress.emit(25, f"Downloading {zip_filename}...")
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, zip_filename)
        
        try:
            download_file(download_url, zip_path, signals)
        except Exception as e:
            signals.error.emit(f"Failed to download update package: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        
        # Step 6: Extract the ZIP file (75%)
        signals.progress.emit(60, "Extracting update package...")
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            signals.error.emit(f"Failed to extract update package: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        
        # Step 7: Find the root folder in the extracted content
        root_folder = None
        for item in os.listdir(extract_dir):
            item_path = os.path.join(extract_dir, item)
            if os.path.isdir(item_path):
                root_folder = item_path
                break
        
        if not root_folder:
            # If no root folder, use the extract directory itself
            root_folder = extract_dir
        
        # Step 8: Replace application files (90%)
        signals.progress.emit(75, "Updating application files...")
        try:
            replace_application_files(root_folder, base_dir, signals)
        except Exception as e:
            signals.error.emit(f"Failed to update application files: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        
        # Step 9: Clean up temporary files
        signals.progress.emit(95, "Cleaning up...")
        shutil.rmtree(temp_dir, ignore_errors=True)
          # Step 10: Update complete (100%)
        signals.progress.emit(100, "Update completed successfully!")
        
        # Update the config with the new version information
        updated_config = config.copy()
        updated_config['app_version'] = latest_release.get('tag_name', '').lstrip('v')
        updated_config['app_version_hash'] = latest_release.get('target_commitish', '')
        
        # Also update app_commit_hash and app_commit_date to match the new version
        updated_config['app_commit_hash'] = latest_release.get('target_commitish', '')
        
        # Format the date
        if 'published_at' in latest_release:
            published_at = latest_release.get('published_at', '')
            if published_at:
                try:
                    # Convert to a more readable format (YYYY-MM-DD)
                    import datetime
                    dt = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    formatted_date = dt.strftime("%Y-%m-%d")
                    updated_config['app_version_date'] = formatted_date
                    updated_config['app_commit_date'] = formatted_date  # Also update app_commit_date
                except:
                    updated_config['app_version_date'] = published_at.split('T')[0]
                    updated_config['app_commit_date'] = published_at.split('T')[0]  # Also update app_commit_date
        
        # Save the updated config
        save_config(updated_config, base_dir)
        
        # Notify completion
        signals.complete.emit(True, "Update completed successfully!")
        
    except Exception as e:
        # Handle any unexpected errors
        signals.error.emit(f"An unexpected error occurred: {str(e)}")


def check_internet_connection():
    """Check if there's an active internet connection."""
    try:
        # Try to reach a reliable server
        req = Request("https://www.google.com")
        req.add_header('User-Agent', 'Mozilla/5.0')
        urlopen(req, timeout=5)
        return True
    except (URLError, HTTPError):
        return False


def check_github_accessible():
    """Check if GitHub is accessible."""
    try:
        req = Request("https://api.github.com")
        req.add_header('User-Agent', 'Mozilla/5.0')
        urlopen(req, timeout=5)
        return True
    except (URLError, HTTPError):
        return False


def extract_repo_info(github_url):
    """Extract the username and repository name from a GitHub URL."""
    github_patterns = [
        r'github\.com/([^/]+)/([^/]+)',  # Standard GitHub URL
        r'github\.com/([^/]+)/([^/]+)/?$',  # GitHub URL with optional trailing slash
        r'github\.com/([^/]+)/([^/]+)/(?:releases|tags)',  # GitHub releases or tags page
    ]
    
    for pattern in github_patterns:
        match = re.search(pattern, github_url)
        if match:
            username, repo = match.groups()
            # Remove any potential .git suffix
            repo = repo.replace('.git', '')
            return username, repo
    
    return None


def get_latest_release_info(username, repo_name):
    """Get the latest release information from GitHub."""
    try:
        api_url = f"https://api.github.com/repos/{username}/{repo_name}/releases/latest"
        req = Request(api_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urlopen(req, timeout=10)
        data = json.loads(response.read().decode())
        return data
    except Exception as e:
        print(f"Error getting latest release: {e}")
        return None


def download_file(url, destination, signals):
    """Download a file with progress updates.
    
    Args:
        url: URL to download from
        destination: Path to save the file
        signals: UpdateSignals instance for thread communication
    """
    try:
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urlopen(req, timeout=30)
        
        # Get file size if available
        file_size = int(response.info().get('Content-Length', 0))
        downloaded = 0
        chunk_size = 8192
        
        with open(destination, 'wb') as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                
                f.write(chunk)
                downloaded += len(chunk)
                
                # Update progress
                if file_size > 0:
                    progress = min(60, 25 + int(35 * downloaded / file_size))
                    progress_msg = f"Downloading... ({downloaded / (1024*1024):.1f} MB / {file_size / (1024*1024):.1f} MB)"
                    signals.progress.emit(progress, progress_msg)
                
        return True
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")


def replace_application_files(source_dir, dest_dir, signals):
    """Replace application files with the new version.
    
    Args:
        source_dir: Directory containing the new version files
        dest_dir: Base directory of the application
        signals: UpdateSignals instance for thread communication
    """
    # Get total number of files to copy for progress tracking
    total_files = 0
    for root, _, files in os.walk(source_dir):
        total_files += len(files)
    
    if total_files == 0:
        raise Exception("No files found in the update package.")
    
    # Copy files with progress updates
    copied_files = 0
    
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path from source_dir
        rel_path = os.path.relpath(root, source_dir)
        
        # Skip if this is the source root directory
        if rel_path == ".":
            rel_path = ""
        
        # Create the destination directory if it doesn't exist
        dest_path = os.path.join(dest_dir, rel_path)
        os.makedirs(dest_path, exist_ok=True)
        
        # Copy each file
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            
            # Skip .git files and directories
            if ".git" in source_file:
                continue
                
            try:
                # Copy the file, overwriting if it exists
                shutil.copy2(source_file, dest_file)
                
                # Update progress
                copied_files += 1
                progress = min(95, 75 + int(20 * copied_files / total_files))
                signals.progress.emit(
                    progress, 
                    f"Updating files... ({copied_files}/{total_files})"
                )
            except Exception as e:
                print(f"Error copying {source_file} to {dest_file}: {e}")
                # Continue with other files even if one fails
    
    return True


def save_config(config, base_dir):
    """Save the updated configuration to the config.json file."""
    try:
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False