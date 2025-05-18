"""
Module for handling application startup tasks.
This provides a centralized place to run initialization code that should be executed
once at application launch.
"""

from core.utils.logger import log, debug, warning, error, exception

def run_startup_tasks():
    """
    Run all application startup tasks.
    This should be called once during application initialization.
    """
    log("Running application startup tasks...")
    
    # Initialize database explorer
    try:
        from database.db_explorer_widget import initialize_explorer
        initialize_explorer()
    except Exception as e:
        exception(e, "Failed to initialize database explorer")
    
    # Add more startup tasks here as needed
    
    log("Application startup tasks completed")
