import os
import requests
from google import genai
from google.genai import types
from PySide6.QtCore import QThread, Signal
from core.utils.logger import log, debug, warning, error, exception


class GeminiAIProcessor(QThread):
    """
    Thread class for processing images with Gemini AI.
    Processes files from database based on item_id and updates UI during processing.
    """
    
    # Signals for UI updates
    processing_started = Signal()
    processing_finished = Signal()
    item_processing_started = Signal(int)  # row index
    item_processing_finished = Signal(int, str)  # row index, result
    error_occurred = Signal(str)
    
    def __init__(self, config, item_id, files_data):
        super().__init__()
        self.config = config
        self.item_id = item_id
        self.files_data = files_data
        self.client = None
        self.should_stop = False
        
    def setup_gemini_client(self):
        """Setup Gemini client with API key from config."""
        try:
            # Get API keys from config
            api_keys = self.config.get('prompting', {}).get('api_keys', {}).get('gemini', [])
            
            if not api_keys:
                raise Exception("No Gemini API keys found in config")
            
            # Use the first available API key
            api_key = api_keys[0] if api_keys else None
            if not api_key:
                raise Exception("No valid Gemini API key available")
            
            # Configure Gemini client - using the new google-genai approach
            os.environ['GOOGLE_API_KEY'] = api_key
            self.client = genai.Client(api_key=api_key)
            
            debug("Gemini client initialized successfully")
            return True
            
        except Exception as e:
            error(f"Failed to setup Gemini client: {e}")
            self.error_occurred.emit(f"Failed to setup Gemini client: {e}")
            return False
    
    def get_model_and_prompt(self):
        """Get model and prompt configuration from config."""
        try:
            prompting_config = self.config.get('prompting', {})
            
            # Get model
            model = prompting_config.get('current_model', 'gemini-1.5-flash')
            
            # Get prompts
            prompts = prompting_config.get('prompts', {})
            base_prompt = prompts.get('base_prompt', '')
            default_prompt = prompts.get('default_prompt', '')
            custom_prompt = prompts.get('custom_prompt', '')
            negative_prompt = prompts.get('negative_prompt', '')
            exclude_prompt = prompts.get('exclude_prompt', '')
            mandatory_prompt = prompts.get('mandatory_prompt', '')
            
            # Combine all prompts in the correct order
            prompt_parts = []
            
            if base_prompt.strip():
                prompt_parts.append(base_prompt)
            
            if default_prompt.strip():
                prompt_parts.append(default_prompt)
                
            if custom_prompt.strip():
                prompt_parts.append(custom_prompt)
                
            if negative_prompt.strip():
                prompt_parts.append(negative_prompt)
                
            if exclude_prompt.strip():
                prompt_parts.append(exclude_prompt)
                
            # Mandatory prompt (JSON format) should be at the end
            if mandatory_prompt.strip():
                prompt_parts.append(mandatory_prompt)
            
            # Combine all prompts
            combined_prompt = "\n\n".join(prompt_parts)
            
            if not combined_prompt.strip():
                combined_prompt = "Analyze this image and provide a detailed description in JSON format."
            
            debug(f"Using model: {model}")
            debug(f"Using prompt length: {len(combined_prompt)} characters")
            debug(f"Prompt includes mandatory JSON format: {'mandatory_prompt' in prompts}")
            
            return model, combined_prompt
            
        except Exception as e:
            error(f"Error getting model and prompt: {e}")
            return 'gemini-1.5-flash', "Analyze this image and provide a detailed description in JSON format."
    
    def process_image_file(self, file_path, prompt, model):
        """Process a single image file with Gemini AI."""
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Check if it's an image file
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in image_extensions:
                return f"Skipped: Not an image file ({file_ext})"
            
            # Read image file
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            
            # Determine MIME type based on extension
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_type_map.get(file_ext, 'image/jpeg')
            
            # Create image part for Gemini
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
            
            # Generate content with Gemini
            response = self.client.models.generate_content(
                model=model,
                contents=[prompt, image_part],
            )
            
            return response.text
            
        except Exception as e:
            error(f"Error processing image {file_path}: {e}")
            return f"Error: {str(e)}"
    
    def stop_processing(self):
        """Stop the processing thread."""
        self.should_stop = True
        debug("Stop processing requested")
    
    def run(self):
        """Main thread execution."""
        try:
            debug(f"Starting Gemini AI processing for item_id: {self.item_id}")
            self.processing_started.emit()
            
            # Setup Gemini client
            if not self.setup_gemini_client():
                return
            
            # Get model and prompt
            model, prompt = self.get_model_and_prompt()
            
            # Process each file
            for row_index, file_data in enumerate(self.files_data):
                if self.should_stop:
                    debug("Processing stopped by user")
                    break
                
                # Get file ID for database updates
                file_id = file_data.get('id')
                if not file_id:
                    warning(f"No file ID found for row {row_index}")
                    continue
                
                # Signal that we're starting to process this item
                self.item_processing_started.emit(row_index)
                
                # Update status to 'generating' in database
                self.update_file_status(file_id, 'generating')
                
                # Get file path
                file_path = file_data.get('filepath', '')
                filename = file_data.get('filename', 'Unknown')
                
                debug(f"Processing file {row_index + 1}/{len(self.files_data)}: {filename}")
                
                # Process the image
                result = self.process_image_file(file_path, prompt, model)
                
                # Print result to console as requested
                print(f"\n{'='*50}")
                print(f"File: {filename}")
                print(f"Path: {file_path}")
                print(f"Result:")
                print(result)
                print('='*50)
                
                # Update status and database with AI results
                if "Error:" in result:
                    self.update_file_status(file_id, 'failed')
                else:
                    # Parse JSON result and update database
                    ai_metadata = self.parse_ai_result(result)
                    if ai_metadata:
                        self.update_file_with_ai_metadata(file_id, ai_metadata, file_path)
                    
                    self.update_file_status(file_id, 'finished')
                
                # Signal that we're done processing this item
                self.item_processing_finished.emit(row_index, result)
                
                # Small delay to allow UI updates
                self.msleep(100)
            
            debug("Gemini AI processing completed")
            
        except Exception as e:
            exception(e, "Error in Gemini AI processing thread")
            self.error_occurred.emit(str(e))
        finally:
            self.processing_finished.emit()
    
    def update_file_status(self, file_id, status):
        """Update file status in database."""
        try:
            from database.db_project_files import ProjectFilesModel
            model = ProjectFilesModel()
            
            update_data = {
                'status': status,
                'updated_at': self.get_current_timestamp()
            }
            
            success = model.update_file(file_id, update_data)
            if success:
                debug(f"Updated file ID {file_id} status to '{status}'")
            else:
                warning(f"Failed to update file ID {file_id} status to '{status}'")
                
        except Exception as e:
            exception(e, f"Error updating file status for ID {file_id}")
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def parse_ai_result(self, result):
        """
        Parse AI result to extract JSON metadata.
        
        Args:
            result (str): The raw AI response
            
        Returns:
            dict: Parsed metadata or None if parsing fails
        """
        try:
            import json
            import re
            
            # Try to find JSON in the result
            # Look for content between ```json and ``` or just raw JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without markdown formatting
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = result.strip()
            
            # Parse the JSON
            metadata = json.loads(json_str)
            
            debug(f"Successfully parsed AI metadata: {metadata}")
            return metadata
            
        except json.JSONDecodeError as e:
            warning(f"Failed to parse AI result as JSON: {e}")
            debug(f"Raw AI result: {result}")
            return None
        except Exception as e:
            warning(f"Error parsing AI result: {e}")
            return None
    
    def update_file_with_ai_metadata(self, file_id, ai_metadata, file_path):
        """
        Update database and file with AI-generated metadata.
        
        Args:
            file_id (int): Database file ID
            ai_metadata (dict): Parsed AI metadata
            file_path (str): Path to the image file
        """
        try:
            from database.db_project_files import ProjectFilesModel
            
            # Prepare database update data
            update_data = {}
            
            # Map AI metadata to database fields with safe string conversion
            if 'title' in ai_metadata and ai_metadata['title']:
                try:
                    update_data['title'] = str(ai_metadata['title']).strip()
                except Exception as e:
                    warning(f"Error converting title to string: {e}")
            
            if 'description' in ai_metadata and ai_metadata['description']:
                try:
                    update_data['description'] = str(ai_metadata['description']).strip()
                except Exception as e:
                    warning(f"Error converting description to string: {e}")
            
            # Handle keywords/tags (can be list or string) with safe conversion
            if 'keywords' in ai_metadata and ai_metadata['keywords']:
                try:
                    keywords = ai_metadata['keywords']
                    if isinstance(keywords, list):
                        # Filter out None/empty values and convert to strings
                        valid_keywords = [str(k).strip() for k in keywords if k and str(k).strip()]
                        update_data['tags'] = ', '.join(valid_keywords)
                    else:
                        update_data['tags'] = str(keywords).strip()
                except Exception as e:
                    warning(f"Error processing keywords: {e}")
            
            # Calculate new title length and tags count safely
            if 'title' in update_data:
                try:
                    from core.global_operations.file_operations import calculate_title_length
                    update_data['title_length'] = calculate_title_length(update_data['title'])
                except Exception as e:
                    warning(f"Error calculating title length: {e}")
            
            if 'tags' in update_data:
                try:
                    from core.global_operations.file_operations import calculate_tags_count
                    update_data['tags_count'] = calculate_tags_count(update_data['tags'])
                except Exception as e:
                    warning(f"Error calculating tags count: {e}")
            
            # Update timestamp
            update_data['updated_at'] = self.get_current_timestamp()
            
            # Only proceed if we have something to update
            if not update_data or len(update_data) <= 1:  # Only timestamp
                debug(f"No meaningful metadata to update for file ID {file_id}")
                return
            
            # Update database with error handling
            try:
                model = ProjectFilesModel()
                success = model.update_file(file_id, update_data)
                
                if success:
                    debug(f"Updated database for file ID {file_id} with AI metadata")
                    
                    # Also write metadata back to the image file
                    try:
                        self.write_metadata_to_file(file_path, ai_metadata)
                    except Exception as e:
                        warning(f"Failed to write metadata to file {file_path}: {e}")
                    
                else:
                    warning(f"Failed to update database for file ID {file_id}")
                    
            except Exception as e:
                warning(f"Database update failed for file ID {file_id}: {e}")
                
        except Exception as e:
            exception(e, f"Error updating file {file_id} with AI metadata")
    
    def write_metadata_to_file(self, file_path, metadata):
        """
        Write metadata back to the image file.
        
        Args:
            file_path (str): Path to the image file
            metadata (dict): Metadata to write
        """
        try:
            # Write metadata using the file operations module
            from core.global_operations.file_operations import write_metadata_to_file
            success = write_metadata_to_file(file_path, metadata)
            
            if success:
                debug(f"Successfully wrote metadata to file: {file_path}")
            else:
                warning(f"Failed to write metadata to file: {file_path}")
                
        except Exception as e:
            exception(e, f"Error writing metadata to file {file_path}")


class GeminiAISystem:
    """
    Main class for managing Gemini AI operations.
    Handles integration with UI components and database.
    """
    
    def __init__(self, config):
        self.config = config
        self.processor_thread = None
        self.is_processing = False
        
        # UI components (will be set by controller)
        self.generate_button = None
        self.stop_button = None
        self.table_widget = None
        
        # TableManager for row highlighting
        self.table_manager = None
        
    def set_ui_components(self, generate_button, stop_button, table_widget):
        """Set UI components for status updates."""
        self.generate_button = generate_button
        self.stop_button = stop_button
        self.table_widget = table_widget
        
        # Initialize table manager for highlighting
        if table_widget:
            from core.helper.workspace._table_manager import TableManager
            self.table_manager = TableManager()
        
        # Connect button signals
        if self.generate_button:
            self.generate_button.clicked.connect(self.start_processing)
        if self.stop_button:
            self.stop_button.clicked.connect(self.stop_processing)
    
    def update_button_states(self, processing=False):
        """Update button enabled/disabled states."""
        if self.generate_button:
            self.generate_button.setEnabled(not processing)
        if self.stop_button:
            self.stop_button.setEnabled(processing)
    
    def start_processing(self, item_id=None, files_data=None):
        """Start Gemini AI processing for the specified item."""
        if self.is_processing:
            warning("Processing already in progress")
            return
        
        if not item_id or not files_data:
            warning("No item_id or files_data provided for processing")
            return
        
        try:
            debug(f"Starting Gemini AI processing for item_id: {item_id}")
            
            # Store current item_id for table refresh
            self.current_item_id = item_id
            
            # Create and setup processor thread
            self.processor_thread = GeminiAIProcessor(self.config, item_id, files_data)
            
            # Connect signals
            self.processor_thread.processing_started.connect(self._on_processing_started)
            self.processor_thread.processing_finished.connect(self._on_processing_finished)
            self.processor_thread.item_processing_started.connect(self._on_item_processing_started)
            self.processor_thread.item_processing_finished.connect(self._on_item_processing_finished)
            self.processor_thread.error_occurred.connect(self._on_error_occurred)
            
            # Start processing
            self.processor_thread.start()
            
        except Exception as e:
            exception(e, "Error starting Gemini AI processing")
    
    def stop_processing(self):
        """Stop current processing."""
        if self.processor_thread and self.processor_thread.isRunning():
            debug("Stopping Gemini AI processing")
            self.processor_thread.stop_processing()
            self.processor_thread.quit()
            self.processor_thread.wait()
    
    def _on_processing_started(self):
        """Handle processing started signal."""
        self.is_processing = True
        self.update_button_states(processing=True)
        log("Gemini AI processing started")
    
    def _on_processing_finished(self):
        """Handle processing finished signal."""
        self.is_processing = False
        self.update_button_states(processing=False)
        
        # Final refresh of table colors to show all completed statuses
        self.refresh_table_colors()
        
        log("Gemini AI processing finished")
    
    def _on_item_processing_started(self, row_index):
        """Handle item processing started signal."""
        debug(f"Signal received: item_processing_started for row {row_index}")
        # Refresh table colors to show updated status
        self.refresh_table_colors()
        debug(f"Started processing item at row {row_index}")
    
    def _on_item_processing_finished(self, row_index, result):
        """Handle item processing finished signal."""
        debug(f"Finished processing item at row {row_index}")
        # Refresh table colors to show updated status
        self.refresh_table_colors()
    
    def refresh_table_colors(self):
        """Refresh table colors based on current database status."""
        if self.table_widget and self.table_manager:
            try:
                # Get current item_id
                if hasattr(self, 'current_item_id'):
                    self.table_manager.refresh_table_colors(self.table_widget, self.current_item_id)
            except Exception as e:
                warning(f"Error refreshing table colors: {e}")
    
    def _on_error_occurred(self, error_message):
        """Handle error signal."""
        error(f"Gemini AI processing error: {error_message}")
        print(f"Error: {error_message}")
    
    def cleanup(self):
        """Cleanup resources."""
        if self.processor_thread and self.processor_thread.isRunning():
            self.stop_processing()