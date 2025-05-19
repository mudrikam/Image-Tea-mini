"""
Helper module for handling menu actions.

This module centralizes menu action handlers, making them reusable across the application
while maintaining separation of concerns.
"""

from PySide6.QtWidgets import QMainWindow, QStatusBar
from PySide6 import QtWidgets  # Import QtWidgets as a module, not a class
from PySide6.QtCore import QObject
import sys
import os

# Import necessary helper modules
from core.helper._about_dialog import show_about_dialog
from core.helper._license_dialog import show_license_dialog
from core.helper._contributors_dialog import show_contributors_dialog
from core.helper._updater_dialog import show_updater_dialog
from core.helper._url_handler import open_url
from core.helper._donation_dialog import show_donation_dialog
from core.helper._window_utils import center_window
from core.utils.logger import log, debug, warning, error, exception

# Import the new modules we created
from core.global_operations.file_operations import (
    select_image_file, select_multiple_image_files,
    select_folder, select_multiple_folders,
    select_video_file, select_multiple_video_files,
    get_image_extensions, get_video_extensions
)
from database.db_project_files import ProjectFilesModel

class MenuActionHandler(QObject):
    """Class that handles menu actions for the main window."""
    
    def __init__(self, main_window, config, base_dir, layout_controller=None):
        """Initialize the menu action handler.
        
        Args:
            main_window: The main application window
            config: The application configuration
            base_dir: The base directory of the application
            layout_controller: Optional layout controller for layout-related actions
        """
        super().__init__()
        self.window = main_window
        self.config = config
        self.BASE_DIR = base_dir
        self.layout_controller = layout_controller
        self.project_files_model = ProjectFilesModel()
    
    def connect_all_actions(self):
        """Connect all menu actions to their respective handlers."""
        self.connect_file_menu_actions()
        self.connect_edit_menu_actions()
        self.connect_view_menu_actions()
        self.connect_settings_menu_actions()
        self.connect_prompt_menu_actions()
        self.connect_help_menu_actions()
        
    def connect_file_menu_actions(self):
        """Connect File menu actions to their handlers."""
        # Connect File menu actions
        self.window.actionNew.triggered.connect(self.handle_new)
        self.window.actionOpen_Image.triggered.connect(self.handle_open_image)
        self.window.actionOpen_Multiple_Images.triggered.connect(self.handle_open_multiple_images)
        self.window.actionOpen_Folder.triggered.connect(self.handle_open_folder)
        self.window.actionOpen_Multiple_Folders.triggered.connect(self.handle_open_multiple_folders)
        self.window.actionOpen_Video.triggered.connect(self.handle_open_video)
        self.window.actionOpen_Multiple_Videos.triggered.connect(self.handle_open_multiple_videos)
        
        # Connect logs action
        self.window.actionSave_Logs.triggered.connect(self.handle_save_logs)
        
        # Connect export actions
        self.window.actionExport_CSV_Freepik.triggered.connect(self.handle_export_csv_freepik)
        self.window.actionExport_CSV_Shutterstock.triggered.connect(self.handle_export_csv_shutterstock)
        self.window.actionExport_CSV_Adobe_Stock.triggered.connect(self.handle_export_csv_adobe_stock)
        self.window.actionExport_CSV_iStock.triggered.connect(self.handle_export_csv_istock)
        
        # Connect Quit action
        self.window.actionQuit.triggered.connect(self.handle_quit)
        
    def connect_edit_menu_actions(self):
        """Connect Edit menu actions to their handlers."""
        # Connect basic edit actions
        self.window.actionCut.triggered.connect(self.handle_cut)
        self.window.actionCopy.triggered.connect(self.handle_copy)
        self.window.actionPaste.triggered.connect(self.handle_paste)
        self.window.actionDelete.triggered.connect(self.handle_delete)
        
        # Connect selection actions
        self.window.actionSelect_All.triggered.connect(self.handle_select_all)
        self.window.actionDeselect_All.triggered.connect(self.handle_deselect_all)
        
        # Connect other edit actions
        self.window.actionRefresh.triggered.connect(self.handle_refresh)
        self.window.actionClear.triggered.connect(self.handle_clear)
        self.window.actionRename.triggered.connect(self.handle_rename)
        self.window.actionRename_All.triggered.connect(self.handle_rename_all)
        
    def connect_view_menu_actions(self):
        """Connect View menu actions to their handlers."""
        # Connect appearance actions
        self.window.actionFull_Screen.triggered.connect(self.handle_full_screen)
        self.window.actionWindowed.triggered.connect(self.handle_windowed)
        self.window.actionCenter.triggered.connect(self.handle_center)
        
        # Connect layout actions
        self.window.actionDefault.triggered.connect(self.handle_default_layout)
        if hasattr(self.window, 'actionBatch_Processing'):
            self.window.actionBatch_Processing.triggered.connect(self.handle_batch_processing_layout)
        if hasattr(self.window, 'actionMetadata_Editing'):
            self.window.actionMetadata_Editing.triggered.connect(self.handle_metadata_editing_layout)
        if hasattr(self.window, 'actionMetadata_Analysis'):
            self.window.actionMetadata_Analysis.triggered.connect(self.handle_metadata_analysis_layout)
    
    def connect_settings_menu_actions(self):
        """Connect Settings menu actions to their handlers.""" 
        # Connect preferences action
        self.window.actionPreferences.triggered.connect(self.handle_preferences)
        
        # Connect AI settings actions
        if hasattr(self.window, 'actionGoogle_Gemini'):
            self.window.actionGoogle_Gemini.triggered.connect(self.handle_google_gemini_settings)
        if hasattr(self.window, 'actionOpen_AI'):
            self.window.actionOpen_AI.triggered.connect(self.handle_open_ai_settings)
    
    def connect_prompt_menu_actions(self):
        """Connect Prompt menu actions to their handlers."""
        # These are application-specific and might require custom handlers
        if hasattr(self.window, 'actionDefault_Prompt'):
            self.window.actionDefault_Prompt.triggered.connect(self.handle_default_prompt)
        if hasattr(self.window, 'actionCustom_Prompt'):
            self.window.actionCustom_Prompt.triggered.connect(self.handle_custom_prompt)
        if hasattr(self.window, 'actionNegative_Prompt'):
            self.window.actionNegative_Prompt.triggered.connect(self.handle_negative_prompt)
        if hasattr(self.window, 'actionMetadata_Prompt_2'):
            self.window.actionMetadata_Prompt_2.triggered.connect(self.handle_metadata_prompt)
        if hasattr(self.window, 'actionPrompt_Preferences'):
            self.window.actionPrompt_Preferences.triggered.connect(self.handle_prompt_preferences)
    
    def connect_help_menu_actions(self):
        """Connect Help menu actions to their handlers."""
        # Connect Help menu actions
        self.window.actionAbout_2.triggered.connect(self.handle_about)
        self.window.actionLicense.triggered.connect(self.handle_license)
        self.window.actionContributors.triggered.connect(self.handle_contributors)
        self.window.actionWhatsApp_Group.triggered.connect(self.handle_whatsapp_group)
        self.window.actionGithub_Repository.triggered.connect(self.handle_github_repository)
        self.window.actionReport_Issue.triggered.connect(self.handle_report_issue)
        self.window.actionCheck_for_Updates.triggered.connect(self.handle_check_for_updates)
        self.window.actionDonate.triggered.connect(self.handle_donate)

    # Updated File menu handlers
    def handle_new(self):
        """Handle New action."""
        log("Creating new project")
        # Implement specific New functionality
        self.show_status_message("Creating new project...")
    
    def handle_open_image(self):
        """Handle Open Image action."""
        log("Opening image file dialog")
        self.show_status_message("Select an image file...")
        
        # Get the user's home directory for dialog starting location
        start_dir = self._get_user_home_directory()
        
        # Open file dialog to select an image, starting from the home directory
        file_details = select_image_file(self.window, start_dir)
        
        if file_details:
            # Add the file to the database
            result = self.project_files_model.add_file(file_details)
            if result:  # result will be the record ID if successful
                self.show_status_message(f"Opened image: {file_details['filename']} (ID: {result})")
                log(f"Added image file '{file_details['filename']}' to project with ID: {result}")
                
                # Manually trigger refresh on explorer widget
                if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
                    self.window.explorer_widget.refresh_data()
            else:
                self.show_status_message("Failed to add image to project")
        else:
            self.show_status_message("No image selected")
    
    def handle_open_multiple_images(self):
        """Handle Open Multiple Images action."""
        log("Opening multiple images file dialog")
        self.show_status_message("Select image files...")
        
        # Get the user's home directory for dialog starting location
        start_dir = self._get_user_home_directory()
        
        # Open file dialog to select multiple images, starting from the home directory
        file_details_list = select_multiple_image_files(self.window, start_dir)
        
        if file_details_list:
            # Add the files to the database
            success_ids = self.project_files_model.add_multiple_files(file_details_list)
            self.show_status_message(f"Added {len(success_ids)} of {len(file_details_list)} images to project")
            log(f"Added {len(success_ids)} of {len(file_details_list)} image files to project")
            
            # Manually trigger refresh on explorer widget
            if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
                self.window.explorer_widget.refresh_data()
        else:
            self.show_status_message("No images selected")
    
    def _process_files_in_folder(self, folder_path):
        """
        Process all image and video files in a folder and add them to the database.
        This method has been deprecated. Use project_files_model.process_folder instead.
        """
        warning("Using deprecated _process_files_in_folder method")
        _, processed_count = self.project_files_model.process_folder(folder_path)
        return processed_count
    
    def _get_user_home_directory(self):
        """
        Get the user's home directory in a cross-platform way.
        
        Returns:
            str: Path to the user's home directory
        """
        # os.path.expanduser('~') works on Windows, macOS, and Linux
        return os.path.expanduser('~')
    
    def handle_open_folder(self):
        """Handle Open Folder action."""
        log("Opening folder dialog")
        self.show_status_message("Select a folder...")
        
        # Get the user's home directory for dialog starting location
        start_dir = self._get_user_home_directory()
        
        # Open dialog to select a folder
        folder_path = select_folder(self.window, start_dir)
        
        if folder_path and os.path.isdir(folder_path):
            # Process the folder using the database model (no folder details needed)
            _, processed_files = self.project_files_model.process_folder(folder_path)
            
            if processed_files > 0:
                self.show_status_message(f"Processed folder: {os.path.basename(folder_path)} - Added {processed_files} files to project")
                log(f"Added {processed_files} files from folder '{os.path.basename(folder_path)}' to project")
                
                # Manually trigger refresh on explorer widget
                if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
                    self.window.explorer_widget.refresh_data()
            else:
                self.show_status_message(f"No compatible files found in folder: {os.path.basename(folder_path)}")
        else:
            self.show_status_message("No folder selected")
    
    def handle_open_multiple_folders(self):
        """Handle Open Multiple Folders action."""
        log("Opening multiple folders dialog")
        self.show_status_message("Select folders...")
        
        # Get the user's home directory for dialog starting location
        start_dir = self._get_user_home_directory()
        
        # Open dialog to select multiple folders
        folder_paths = select_multiple_folders(self.window, start_dir)
        
        if folder_paths:
            # Process all folders using the database model
            results = self.project_files_model.process_multiple_folders(folder_paths)
            
            if results['total_files'] > 0:
                self.show_status_message(f"Processed {results['total_folders']} folders - Added {results['total_files']} files to project")
                log(f"Added {results['total_files']} files from {results['total_folders']} folders to project")
                
                # Manually trigger refresh on explorer widget
                if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
                    self.window.explorer_widget.refresh_data()
            else:
                self.show_status_message(f"No compatible files found in selected folders")
        else:
            self.show_status_message("No folders selected")
    
    def handle_open_video(self):
        """Handle Open Video action."""
        log("Opening video file dialog")
        self.show_status_message("Select a video file...")
        
        # Get the user's home directory for dialog starting location
        start_dir = self._get_user_home_directory()
        
        # Open file dialog to select a video, starting from the home directory
        file_details = select_video_file(self.window, start_dir)
        
        if file_details:
            # Add the file to the database
            result = self.project_files_model.add_file(file_details)
            if result:  # result will be the record ID if successful
                self.show_status_message(f"Opened video: {file_details['filename']} (ID: {result})")
                log(f"Added video file '{file_details['filename']}' to project with ID: {result}")
                
                # Manually trigger refresh on explorer widget
                if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
                    self.window.explorer_widget.refresh_data()
            else:
                self.show_status_message("Failed to add video to project")
        else:
            self.show_status_message("No video selected")
    
    def handle_open_multiple_videos(self):
        """Handle Open Multiple Videos action."""
        log("Opening multiple videos file dialog")
        self.show_status_message("Select video files...")
        
        # Get the user's home directory for dialog starting location
        start_dir = self._get_user_home_directory()
        
        # Open file dialog to select multiple videos, starting from the home directory
        file_details_list = select_multiple_video_files(self.window, start_dir)
        
        if file_details_list:
            # Add the files to the database
            success_ids = self.project_files_model.add_multiple_files(file_details_list)
            self.show_status_message(f"Added {len(success_ids)} of {len(file_details_list)} videos to project")
            log(f"Added {len(success_ids)} of {len(file_details_list)} video files to project")
            
            # Manually trigger refresh on explorer widget
            if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
                self.window.explorer_widget.refresh_data()
        else:
            self.show_status_message("No videos selected")
    
    def handle_save_logs(self):
        """Handle Save Logs action."""
        log("Saving application logs")
        self.show_status_message("Saving application logs...")
        
        # Find the output_logs instance - this is where the bug is
        output_logs = None
        
        # Check if we can access it from layout_controller
        if self.layout_controller and hasattr(self.layout_controller, 'output_logs') and self.layout_controller.output_logs:
            output_logs = self.layout_controller.output_logs
            
        # If we found it, call its save_logs method
        if output_logs:
            output_logs.save_logs()
        else:
            warning("Could not find output logs widget")
            self.show_status_message("Could not find output logs widget")
    
    def handle_export_csv_freepik(self):
        """Handle Export CSV Freepik action."""
        log("Exporting CSV for Freepik")
        # Implement specific Export CSV Freepik functionality
        self.show_status_message("Exporting CSV for Freepik...")
    
    def handle_export_csv_shutterstock(self):
        """Handle Export CSV Shutterstock action."""
        log("Exporting CSV for Shutterstock")
        # Implement specific Export CSV Shutterstock functionality
        self.show_status_message("Exporting CSV for Shutterstock...")
    
    def handle_export_csv_adobe_stock(self):
        """Handle Export CSV Adobe Stock action."""
        log("Exporting CSV for Adobe Stock")
        # Implement specific Export CSV Adobe Stock functionality
        self.show_status_message("Exporting CSV for Adobe Stock...")
    
    def handle_export_csv_istock(self):
        """Handle Export CSV iStock action."""
        log("Exporting CSV for iStock")
        # Implement specific Export CSV iStock functionality
        self.show_status_message("Exporting CSV for iStock...")
    
    def handle_quit(self):
        """Handle Quit action."""
        debug("Shutting down application...")
        # Implementation of quit handled by main controller
        self.window.close()

    # Edit menu handlers
    def handle_cut(self):
        """Handle Cut action.""" 
        # This needs to be connected to the currently focused widget
        try:
            focused_widget = self.window.focusWidget()
            if hasattr(focused_widget, "cut"):
                focused_widget.cut()
        except Exception as e:
            warning(f"Clipboard operation failed: {e}")
    
    def handle_copy(self):
        """Handle Copy action."""
        # This needs to be connected to the currently focused widget
        try:
            focused_widget = self.window.focusWidget()
            if hasattr(focused_widget, "copy"):
                focused_widget.copy()
        except Exception as e:
            # Handle clipboard errors gracefully
            warning(f"Clipboard operation failed: {e}")
    
    def handle_paste(self):
        """Handle Paste action."""
        # This needs to be connected to the currently focused widget
        try:
            focused_widget = self.window.focusWidget()
            if hasattr(focused_widget, "paste"):
                focused_widget.paste()
        except Exception as e:
            warning(f"Clipboard operation failed: {e}")
    
    def handle_delete(self):
        """Handle Delete action."""
        # This needs to be connected to the currently focused widget
        focused_widget = self.window.focusWidget()
        if hasattr(focused_widget, "delete"):
            focused_widget.delete()
    
    def handle_select_all(self):
        """Handle Select All action."""
        # This needs to be connected to the currently focused widget
        focused_widget = self.window.focusWidget()
        if hasattr(focused_widget, "selectAll"):
            focused_widget.selectAll()
    
    def handle_deselect_all(self):
        """Handle Deselect All action."""
        # This needs specific implementation depending on widget
        log("Deselecting all items")
        self.show_status_message("Deselected all items")
    
    def handle_refresh(self):
        """Handle Refresh action."""
        log("Refreshing view")
        self.show_status_message("Refreshing view...")
        
        # Refresh explorer widget if it exists
        if hasattr(self.window, 'explorer_widget') and self.window.explorer_widget:
            self.window.explorer_widget.refresh_data()
    
    def handle_clear(self):
        """Handle Clear action."""
        focused_widget = self.window.focusWidget()
        if hasattr(focused_widget, "clear"):
            focused_widget.clear()
        self.show_status_message("Cleared content")
    
    def handle_rename(self):
        """Handle Rename action."""
        log("Renaming selected item")
        self.show_status_message("Renaming selected item...")
    
    def handle_rename_all(self):
        """Handle Rename All action."""
        log("Renaming all items")
        self.show_status_message("Renaming all items...")

    # View menu handlers
    def handle_full_screen(self):
        """Handle Full Screen action."""
        if self.window:
            self.window.showFullScreen()
            self.show_status_message("Switched to fullscreen mode")
    
    def handle_windowed(self):
        """Handle Windowed action."""
        if self.window:
            self.window.showNormal()
            self.show_status_message("Switched to windowed mode")
    
    def handle_center(self):
        """Handle Center action."""
        if self.window:
            center_window(self.window)
            self.show_status_message("Window centered")
    
    def handle_default_layout(self):
        """Handle Default Layout action."""
        if self.layout_controller:
            self.layout_controller.reset_widgets_to_default()
        else:
            warning("Layout controller not available")
    
    def handle_batch_processing_layout(self):
        """Handle Batch Processing Layout action."""
        log("Switching to batch processing layout")
        self.show_status_message("Switched to batch processing layout")
        # Implement layout switching logic
    
    def handle_metadata_editing_layout(self):
        """Handle Metadata Editing Layout action."""
        log("Switching to metadata editing layout")
        self.show_status_message("Switched to metadata editing layout")
        # Implement layout switching logic
    
    def handle_metadata_analysis_layout(self):
        """Handle Metadata Analysis Layout action."""
        log("Switching to metadata analysis layout")
        self.show_status_message("Switched to metadata analysis layout")
        # Implement layout switching logic

    # Settings menu handlers
    def handle_preferences(self):
        """Handle Preferences action."""
        from core.helper._global_preferences import show_global_preferences
        show_global_preferences(self.window, self.config, self.BASE_DIR)
    
    def handle_google_gemini_settings(self):
        """Handle Google Gemini Settings action."""
        log("Opening Google Gemini settings")
        self.show_status_message("Opening Google Gemini settings...")
        # Implement Gemini settings dialog
    
    def handle_open_ai_settings(self):
        """Handle Open AI Settings action."""
        log("Opening OpenAI settings")
        self.show_status_message("Opening OpenAI settings...")
        # Implement OpenAI settings dialog

    # Prompt menu handlers
    def handle_default_prompt(self):
        """Handle Default Prompt action."""
        log("Using default prompt")
        self.show_status_message("Using default prompt")
    
    def handle_custom_prompt(self):
        """Handle Custom Prompt action."""
        log("Using custom prompt")
        self.show_status_message("Using custom prompt")
    
    def handle_negative_prompt(self):
        """Handle Negative Prompt action."""
        log("Using negative prompt")
        self.show_status_message("Using negative prompt")
    
    def handle_metadata_prompt(self):
        """Handle Metadata Prompt action."""
        log("Using metadata prompt")
        self.show_status_message("Using metadata prompt")
    
    def handle_prompt_preferences(self):
        """Handle Prompt Preferences action."""
        log("Opening prompt preferences")
        self.show_status_message("Opening prompt preferences...")

    # Help menu handlers  
    def handle_about(self):
        """Handle About action."""
        show_about_dialog(self.window, self.config, self.BASE_DIR)
    
    def handle_license(self):
        """Handle License action."""
        show_license_dialog(self.window, self.config, self.BASE_DIR)
    
    def handle_contributors(self):
        """Handle Contributors action."""
        show_contributors_dialog(self.window, self.config, self.BASE_DIR)
    
    def handle_whatsapp_group(self):
        """Handle WhatsApp Group action."""
        whatsapp_url = self.config.get("app_whatsapp", "")
        if whatsapp_url:
            log("Opening WhatsApp support group")
            open_url(whatsapp_url)
        else:
            warning("WhatsApp group URL not configured")
    
    def handle_github_repository(self):
        """Handle GitHub Repository action."""
        repo_url = self.config.get("app_repository", "")
        if repo_url:
            log("Opening GitHub repository")
            open_url(repo_url)
        else:
            warning("GitHub repository URL not configured")
    
    def handle_report_issue(self):
        """Handle Report Issue action."""
        issue_url = self.config.get("app_report_issue", "")
        if issue_url:
            log("Opening issue reporting page")
            open_url(issue_url)
        else:
            warning("Issue reporting URL not configured")
    
    def handle_check_for_updates(self):
        """Handle Check for Updates action."""
        log("Checking for updates...")
        show_updater_dialog(self.window, self.config, self.BASE_DIR)
    
    def handle_donate(self):
        """Handle Donate action."""
        show_donation_dialog(self.window, self.config, self.BASE_DIR)
    
    # Utility methods
    def show_status_message(self, message, timeout=3000):
        """Show a message in the status bar.
        
        Args:
            message: The message to show
            timeout: The timeout in milliseconds (default: 3000)
        """
        status_bar = getattr(self.window, 'statusBar', None)
        if status_bar and callable(status_bar):
            status_bar().showMessage(message, timeout)
