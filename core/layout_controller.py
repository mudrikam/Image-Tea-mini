from PySide6 import QtWidgets, QtUiTools, QtCore
import os
from core.widgets.explorer_widget import ExplorerWidget
from core.widgets.output_logs import OutputLogsWidget
from core.helper._window_utils import center_window

class LayoutController:
    def __init__(self, parent_window, base_dir):
        """Initialize the layout controller.
        
        Args:
            parent_window: The main application window
            base_dir: The base directory of the application
        """
        self.parent = parent_window
        self.BASE_DIR = base_dir
        self.widgets = {}
        
        # Use QSettings directly instead of manual file handling
        self.settings = QtCore.QSettings("ImageTeaMini", "Layout")
    
    def load_explorer_widget(self):
        """Load the explorer dock widget and add it to the main window."""
        # Create the explorer widget
        explorer = ExplorerWidget(self.BASE_DIR)
        dock_widget = explorer.load_ui()
        
        # Store reference to the widget
        self.widgets['explorer'] = dock_widget
        
        # Add the dock widget to the main window
        self.parent.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_widget)
        
        # Ensure the widget is visible
        dock_widget.setVisible(True)
        dock_widget.show()
        
        return dock_widget

    def load_output_logs_widget(self):
        """Load the output logs dock widget and add it to the main window."""
        # Create the output logs widget
        logs = OutputLogsWidget(self.BASE_DIR)
        dock_widget = logs.load_ui()
        
        # Store reference to the widget
        self.widgets['output_logs'] = dock_widget
        
        # Add the dock widget to the main window at the bottom
        self.parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        
        # Ensure the widget is visible
        dock_widget.setVisible(True)
        dock_widget.show()
        
        return dock_widget
    
    def setup_ui(self):
        """Set up all UI components."""
        # Load the explorer widget
        self.load_explorer_widget()
        
        # Load the output logs widget
        self.load_output_logs_widget()
        
        # Restore previous layout if available, otherwise ensure default layout is shown
        if not self.restore_layout():
            # If no saved layout exists, make sure all widgets are visible
            self.ensure_widgets_visible()
        
        return self
    
    def ensure_widgets_visible(self):
        """Make sure all dock widgets are visible and properly positioned."""
        # Make sure all dock widgets are visible
        for widget_name, widget in self.widgets.items():
            widget.setVisible(True)
            
            # Ensure the widget is not floating unless explicitly set
            if widget.isFloating():
                widget.setFloating(False)
        
        # Process events to make sure UI updates
        QtWidgets.QApplication.processEvents()
        
    def save_layout(self):
        """Save the current layout configuration."""
        # Use QSettings to save window geometry and state
        self.settings.setValue("geometry", self.parent.saveGeometry())
        self.settings.setValue("windowState", self.parent.saveState())
        
    def restore_layout(self):
        """Restore the previously saved layout configuration."""
        # Restore geometry and state from QSettings
        geometry = self.settings.value("geometry")
        state = self.settings.value("windowState")
        
        if geometry and state:
            self.parent.restoreGeometry(geometry)
            self.parent.restoreState(state)
            
            # Even if we restore layout, ensure our critical widgets are visible
            # This ensures core functionality is never hidden
            for widget_name, widget in self.widgets.items():
                if not widget.isVisible():
                    widget.setVisible(True)
            
            return True
        else:
            return False
    
    def reset_widgets_to_default(self):
        """Reset all dock widgets to their original default state as defined in UI files."""
        # First, clear all saved layout settings
        self.settings.clear()
        
        # Temporarily store references to existing widgets
        existing_widgets = self.widgets.copy()
        
        # Clear our widgets dictionary
        self.widgets.clear()
        
        # Remove all existing dock widgets from main window
        for widget_name, widget in existing_widgets.items():
            self.parent.removeDockWidget(widget)
            widget.setParent(None)  # Fully detach from parent
        
        # Create and load fresh widgets from UI files
        self.load_explorer_widget()
        self.load_output_logs_widget()
        
        # Process events to ensure all UI changes are applied
        QtWidgets.QApplication.processEvents()
        
        # Save this clean state as the new default
        self.save_layout()
        
        # Show a status message if the parent has a status bar
        status_bar = getattr(self.parent, 'statusBar', None)
        if status_bar and callable(status_bar):
            status_bar().showMessage("Layout reset to default", 2000)
        
        return True