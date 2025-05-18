import os
import sys

# Get the absolute path of the directory containing this script
# This ensures our app can find all its resources no matter where it's run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add our app's root directory to the Python path
# This allows us to import modules using simple names like "core.main_controller"
# instead of having to use full absolute paths
sys.path.insert(0, BASE_DIR)

# Now we can safely import our modules after the path is set
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

try:
    # Import our main controller class
    # This class handles the application's core logic and UI management
    from core.main_controller import MainController
    from database.db_explorer_widget import initialize_explorer
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
    # Set the attribute to ensure application quits when last window is closed
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Initialize the application
    app = QApplication(sys.argv)
    
    # Ensure application exits when all windows are closed
    app.setQuitOnLastWindowClosed(True)
    
    # Run year color update at startup
    initialize_explorer()
    
    # Create our main controller and pass it our base directory
    # This way the controller doesn't need to recalculate the path
    controller = MainController(base_dir=BASE_DIR)
    
    # Register a clean shutdown function to be called when app is about to quit
    app.aboutToQuit.connect(controller.shutdown)
    
    # Initialize sets everything up before showing the UI
    # This is where connections to databases or other resources would happen
    controller.initialize()
    
    # Run starts the application's main event loop
    # The app will stay in this function until the user closes it
    controller.run()
    
    # Force the process to exit with a success code after the event loop finishes
    # This ensures the terminal/cmd will close as well
    os._exit(0)  # Use os._exit to forcibly terminate the process
    
    # This line will never be reached due to os._exit, but keeping it for clarity
    return 0

if __name__ == "__main__":
    main()  # Using os._exit() directly
