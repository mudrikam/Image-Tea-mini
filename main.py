import os
import sys

# Get the absolute path of the directory containing this script
# This ensures our app can find all its resources no matter where it's run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add our app's root directory to the Python path
# This allows us to import modules using simple names like "core.main_controller"
# instead of having to use full absolute paths
sys.path.insert(0, BASE_DIR)

try:
    # Import our main controller class
    # This class handles the application's core logic and UI management
    from core.main_controller import MainController
except ImportError:
    # If the import fails, provide helpful debugging information
    # This makes it much easier to diagnose path or installation problems
    print(f"Current path: {sys.path}")
    print(f"Looking for module in: {os.path.join(BASE_DIR, 'core')}")
    raise  # Re-raise the exception after showing the helpful info

def main():
    """
    Main application entry point.
    
    This function:
    1. Creates the main controller
    2. Initializes the application
    3. Runs the main event loop
    4. Performs cleanup on exit
    """
    # Create our main controller and pass it our base directory
    # This way the controller doesn't need to recalculate the path
    controller = MainController(base_dir=BASE_DIR)
    
    # Initialize sets everything up before showing the UI
    # This is where connections to databases or other resources would happen
    controller.initialize()
    
    # Run starts the application's main event loop
    # The app will stay in this function until the user closes it
    controller.run()
    
    # Shutdown cleans up resources before exiting
    # This ensures we don't leave files open or connections active
    controller.shutdown()

if __name__ == "__main__":
    # This conditional checks if this file is being run directly (not imported)
    # It's a standard Python pattern that allows a file to be both
    # a runnable script and an importable module
    main()
