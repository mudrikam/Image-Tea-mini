import os
import re
import json
import time
import threading
import datetime
import webbrowser
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtCore import Qt

# Import the app updater module
from core.helper._app_updater import launch_app_updater


def get_current_datetime_iso():
    """Return the current date and time in ISO 8601 format."""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def get_formatted_datetime(iso_datetime=None):
    """Return a human-readable date and time format from ISO format."""
    try:
        if iso_datetime:
            dt = datetime.datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M:%SZ")
        else:
            dt = datetime.datetime.now()
        return dt.strftime("%d %B %Y, %H:%M:%S")
    except:
        # If parsing fails, return the original or current datetime
        return iso_datetime or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def reload_config(base_dir):
    """Reload the configuration from the config.json file."""
    try:
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error reloading config: {e}")
        return None


def open_update_url(url):
    """Open the update URL in the default web browser."""
    if url:
        webbrowser.open(url)


def launch_app_updater_dialog(parent, config, base_dir):
    """Launch the application updater dialog."""
    # Close the updater check dialog first
    parent.accept()
    
    # Launch the app updater
    launch_app_updater(parent.parentWidget(), config, base_dir)


def save_auto_update_setting(state, config, base_dir):
    """Save the automatic update setting to the config file."""
    # Convert the checkbox state to a boolean
    is_checked = bool(state == Qt.CheckState.Checked.value)
    
    # Update the config
    updated_config = config.copy()
    updated_config['app_automatic_update'] = is_checked
    
    # Save the updated config
    save_config(updated_config, base_dir)
    
    # Update the original config object for the dialog session
    config['app_automatic_update'] = is_checked
    
    # Ensure the main_controller's config is updated as well
    # This makes sure the updated setting is available to the entire application
    updated_config = reload_config(base_dir)
    if updated_config:
        config.update(updated_config)


def show_updater_dialog(parent, config, base_dir):
    """Show the updater dialog to check for updates."""
    # Refresh config from file to get the latest values
    refreshed_config = reload_config(base_dir)
    if refreshed_config:
        # Use the refreshed config but update the original config object as well
        # This ensures other parts of the app see the changes
        config.update(refreshed_config)
    
    # Load the UI file for the updater dialog
    updater_ui_path = os.path.join(base_dir, "gui", "dialogs", "updater_window.ui")
    
    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(updater_ui_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    dialog = loader.load(ui_file, parent)
    ui_file.close()
    
    # Set up the dialog with current version information
    current_version = config.get("app_version", "Unknown")
    version_hash = config.get("app_version_hash", "")
    version_date = config.get("app_version_date", "")
    version_detail = f"{current_version}"
    if version_hash:
        version_detail += f" ({version_hash[:7]})"
    if version_date:
        version_detail += f" - {version_date}"
    
    dialog.lblCurrentVersion.setText(f"Current Version: {version_detail}")
    
    # Set initial message
    remote_version = config.get("app_remote_version", "")
    if remote_version:
        remote_hash = config.get("app_remote_commit_hash", "")
        remote_date = config.get("app_remote_version_date", "")
        remote_detail = f"{remote_version}"
        if remote_hash:
            remote_detail += f" ({remote_hash[:7]})"
        if remote_date:
            remote_detail += f" - {remote_date}"
        dialog.lblUpdateVersion.setText(f"Latest Version: {remote_detail}")
    else:
        dialog.lblUpdateVersion.setText(f"Latest Version: Click 'Check' to verify")
      # Show when last update check was performed
    last_check = config.get("app_last_update_check", "")
    if last_check:
        formatted_last_check = get_formatted_datetime(last_check)
        dialog.lblUpdateMessage.setText(f"Last checked: {formatted_last_check}. Click 'Check' button to check for updates.")
    else:
        dialog.lblUpdateMessage.setText("Click 'Check' button to check for updates.")
    
    # Connect button signals to slots
    dialog.pushButton.clicked.connect(dialog.accept)  # Close button
    dialog.btnCheck.clicked.connect(lambda: check_for_updates(dialog, config, base_dir))
    
    # Connect the Update Now button to launch the app updater
    dialog.btnUpdate.clicked.connect(lambda: launch_app_updater_dialog(dialog, config, base_dir))
    dialog.btnUpdate.setEnabled(bool(remote_version and compare_versions(current_version, remote_version)))
    
    # Set up automatic update checkbox
    auto_update = config.get("app_automatic_update", False)
    dialog.checkBox.setChecked(auto_update)
    
    # Connect the checkbox to save its state when changed
    dialog.checkBox.stateChanged.connect(lambda state: save_auto_update_setting(state, config, base_dir))
    
    # Initialize the progress bar
    dialog.progressUpdate.setValue(0)
    
    # Auto-check for updates if the setting is enabled
    if auto_update:
        # Short delay to allow the dialog to show up first
        QtCore.QTimer.singleShot(500, lambda: check_for_updates(dialog, config, base_dir))
    
    # Show the dialog
    dialog.exec()


def check_for_updates(dialog, config, base_dir):
    """Check for updates in a separate thread."""
    # Disable the check button while checking
    dialog.btnCheck.setEnabled(False)
    dialog.lblUpdateMessage.setText("Checking for updates...")
    dialog.progressUpdate.setValue(0)
    
    # Reset the latest version label
    dialog.lblUpdateVersion.setText("Latest Version: Checking...")
    
    # Create and start a thread for checking updates
    update_thread = threading.Thread(
        target=update_check_worker,
        args=(dialog, config, base_dir)
    )
    update_thread.daemon = True
    update_thread.start()


def update_check_worker(dialog, config, base_dir):
    """Worker function to check for updates."""
    try:
        # Step 1: Check internet connection (10%)
        update_progress(dialog, 10, "Checking internet connection...")
        if not check_internet_connection():
            show_update_result(dialog, config, False, 
                              config.get("app_update_message_no_internet", 
                                        "No internet connection. Please check your connection and try again."))
            return
        
        time.sleep(0.5)  # Small delay for UI update
        
        # Step 2: Check if update URL is accessible (30%)
        update_progress(dialog, 30, "Checking update source...")
        update_url = config.get("app_update_url", "")
        if not update_url or not check_url_accessible(update_url):
            show_update_result(dialog, config, False, 
                              config.get("app_update_message_error", 
                                        "Error checking for updates. Please try again later."))
            return
        
        time.sleep(0.5)  # Small delay for UI update
        
        # Step 3: Get latest version from GitHub (60%)
        update_progress(dialog, 60, "Retrieving latest version...")
        latest_version_info = get_latest_github_release(update_url)
        if not latest_version_info or not latest_version_info.get('version'):
            show_update_result(dialog, config, False, 
                              config.get("app_update_message_error", 
                                        "Error checking for updates. Please try again later."))
            return
        
        latest_version = latest_version_info.get('version')
        latest_hash = latest_version_info.get('hash', '')
        latest_date = latest_version_info.get('date', '')
        
        time.sleep(0.5)  # Small delay for UI update
        
        # Step 4: Compare versions (90%)
        update_progress(dialog, 90, "Comparing versions...")
        current_version = config.get("app_version", "0.0.0")
        
        is_update_available = compare_versions(current_version, latest_version)
        
        # Complete the progress bar
        update_progress(dialog, 100, "Check completed")
        
        # Format version details for display
        latest_version_detail = f"{latest_version}"
        if latest_hash:
            latest_version_detail += f" ({latest_hash[:7]})"
        if latest_date:
            latest_version_detail += f" - {latest_date}"
            
        # Update the latest version label
        QtCore.QMetaObject.invokeMethod(
            dialog.lblUpdateVersion,
            "setText",
            Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, f"Latest Version: {latest_version_detail}")
        )
          # Update the config file with the latest remote version information
        updated_config = config.copy()
        updated_config['app_remote_version'] = latest_version
        updated_config['app_remote_commit_hash'] = latest_hash
        updated_config['app_remote_version_date'] = latest_date
        updated_config['app_last_update_check'] = get_current_datetime_iso()
        
        # Save the updated config
        save_config(updated_config, base_dir)
        
        # Update the original config object to reflect changes
        config.update(updated_config)
        
        # Show the result
        if is_update_available:
            update_message = config.get("app_update_message", 
                                       "New version available! Please update to the latest version for new features and bug fixes.")
            show_update_result(dialog, config, True, update_message)
        else:
            update_message = config.get("app_update_message_no_update", 
                                       "You are using the latest version of Image Tea Mini.")
            show_update_result(dialog, config, False, update_message)
            
    except Exception as e:
        # Handle any unexpected errors
        error_message = config.get("app_update_message_error", 
                                  "Error checking for updates. Please try again later.")
        show_update_result(dialog, config, False, f"{error_message} (Error: {str(e)})")


def update_progress(dialog, value, message):
    """Update the progress bar and message in the UI thread."""
    QtCore.QMetaObject.invokeMethod(
        dialog.progressUpdate,
        "setValue",
        Qt.ConnectionType.QueuedConnection,
        QtCore.Q_ARG(int, value)
    )
    QtCore.QMetaObject.invokeMethod(
        dialog.lblUpdateMessage,
        "setText",
        Qt.ConnectionType.QueuedConnection,
        QtCore.Q_ARG(str, message)
    )


def show_update_result(dialog, config, update_available, message):
    """Show the update result message and enable/disable the update button."""
    # Enable the check button again
    QtCore.QMetaObject.invokeMethod(
        dialog.btnCheck,
        "setEnabled",
        Qt.ConnectionType.QueuedConnection,
        QtCore.Q_ARG(bool, True)
    )
    
    # Set the update message
    QtCore.QMetaObject.invokeMethod(
        dialog.lblUpdateMessage,
        "setText",
        Qt.ConnectionType.QueuedConnection,
        QtCore.Q_ARG(str, message)
    )
    
    # Enable or disable the Update button based on whether an update is available
    QtCore.QMetaObject.invokeMethod(
        dialog.btnUpdate,
        "setEnabled",
        Qt.ConnectionType.QueuedConnection,
        QtCore.Q_ARG(bool, update_available)
    )


def check_internet_connection():
    """Check if there's an active internet connection."""
    try:
        # Try to reach a reliable server
        urlopen("https://www.google.com", timeout=3)
        return True
    except URLError:
        return False


def check_url_accessible(url):
    """Check if the given URL is accessible."""
    try:
        # Extract the base URL (domain) in case the URL includes paths
        if "github.com" in url:
            # For GitHub URLs, we want to make sure we can access the API
            api_url = "https://api.github.com"
            req = Request(api_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            urlopen(req, timeout=5)
            return True
        else:
            # For other URLs, just check if we can access the given URL
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            urlopen(req, timeout=5)
            return True
    except (URLError, HTTPError):
        return False


def get_latest_github_release(github_url):
    """Get the latest release version and details from GitHub."""
    try:
        # Extract the username and repository name from the GitHub URL
        # The URL format is typically: https://github.com/username/repository
        match = re.search(r'github.com/([^/]+)/([^/]+)', github_url)
        if match:
            username, repo = match.groups()
            
            # Remove any potential .git suffix
            repo = repo.replace('.git', '')
            
            # If the URL points to the releases page, extract the repo name
            if 'releases' in repo:
                repo = repo.split('/releases')[0]
                
            # Construct the API URL for the latest release
            api_url = f"https://api.github.com/repos/{username}/{repo}/releases/latest"
            
            # Send the request
            req = Request(api_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            response = urlopen(req, timeout=5)
            
            # Parse the JSON response
            data = json.loads(response.read().decode())
            
            # Get the tag name (version)
            tag_name = data.get('tag_name', '')
            version = tag_name
            
            # Some projects prefix their tags with 'v', remove it if present
            if version.startswith('v'):
                version = version[1:]
            
            # Get the commit information if available
            commit_hash = ''
            commit_date = ''
            
            # First, try to get commit details from the release API response
            # Use target_commitish if it looks like a commit hash (not "main" or "master")
            target_commitish = data.get('target_commitish', '')
            if target_commitish and not target_commitish.lower() in ['main', 'master', 'develop', 'trunk']:
                commit_hash = target_commitish
            
            # If we don't have a proper commit hash, try to get it from the tag itself
            if not commit_hash or len(commit_hash) < 7:
                try:
                    # Get the commit SHA from the tag reference
                    tag_url = f"https://api.github.com/repos/{username}/{repo}/git/refs/tags/{tag_name}"
                    tag_req = Request(tag_url)
                    tag_req.add_header('User-Agent', 'Mozilla/5.0')
                    tag_response = urlopen(tag_req, timeout=5)
                    tag_data = json.loads(tag_response.read().decode())
                    
                    # If it's an annotated tag, we need to get the tagged object
                    if tag_data.get('object', {}).get('type') == 'tag':
                        tag_sha = tag_data.get('object', {}).get('sha', '')
                        if tag_sha:
                            # Get the tag object
                            tag_obj_url = f"https://api.github.com/repos/{username}/{repo}/git/tags/{tag_sha}"
                            tag_obj_req = Request(tag_obj_url)
                            tag_obj_req.add_header('User-Agent', 'Mozilla/5.0')
                            tag_obj_response = urlopen(tag_obj_req, timeout=5)
                            tag_obj_data = json.loads(tag_obj_response.read().decode())
                            commit_hash = tag_obj_data.get('object', {}).get('sha', '')
                    else:
                        # Lightweight tag points directly to the commit
                        commit_hash = tag_data.get('object', {}).get('sha', '')
                except:
                    # If we can't get the commit hash from the tag, fall back to the target_commitish
                    if not commit_hash:
                        commit_hash = target_commitish
            
            # Get the published date
            published_at = data.get('published_at', '')
            if published_at:
                # Convert to a more readable format (YYYY-MM-DD)
                try:
                    dt = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    commit_date = dt.strftime("%Y-%m-%d")
                except:
                    commit_date = published_at.split('T')[0]  # Just take the date part
            
            return {
                'version': version,
                'hash': commit_hash,
                'date': commit_date,
                'full_data': data  # Include full data for potential future use
            }
            
    except Exception as e:
        print(f"Error getting latest release: {e}")
        
    return None


def compare_versions(current, latest):
    """Compare version strings to determine if an update is available."""
    try:
        # Strip any 'v' prefix if present
        if current.startswith('v'):
            current = current[1:]
        if latest.startswith('v'):
            latest = latest[1:]
        
        # Split versions into components
        current_parts = [int(x) for x in current.split('.')]
        latest_parts = [int(x) for x in latest.split('.')]
        
        # Pad with zeros if needed
        while len(current_parts) < 3:
            current_parts.append(0)
        while len(latest_parts) < 3:
            latest_parts.append(0)
        
        # Compare version components
        for i in range(max(len(current_parts), len(latest_parts))):
            if i >= len(current_parts):
                return True  # Latest has more components, so it's newer
            if i >= len(latest_parts):
                return False  # Current has more components, latest can't be newer
            
            if latest_parts[i] > current_parts[i]:
                return True  # Latest component is higher, so it's newer
            if latest_parts[i] < current_parts[i]:
                return False  # Latest component is lower, so it's not newer
        
        # If we get here, versions are identical
        return False
        
    except Exception as e:
        print(f"Error comparing versions: {e}")
        # If there's an error, assume no update to be safe
        return False