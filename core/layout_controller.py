from PySide6 import QtWidgets, QtUiTools, QtCore
import os
from core.widgets.explorer_widget import ExplorerWidget
from core.widgets.output_logs import OutputLogsWidget
from core.widgets._default_layout import reset_widget_to_default
from core.utils.logger import log, debug, warning, error, exception, set_output_logs

class LayoutController:
    def __init__(self, parent_window, base_dir):
        """Initialize the layout controller."""
        self.parent = parent_window
        self.BASE_DIR = base_dir
        self.widgets = {}
        self.output_logs = None
        self.settings = QtCore.QSettings("ImageTeaMini", "Layout")
    
    def load_explorer_widget(self):
        """Load the explorer dock widget and add it to the main window."""
        try:
            # Create and load the explorer widget
            explorer = ExplorerWidget(self.BASE_DIR)
            dock_widget = explorer.load_ui()
            self.widgets['explorer'] = dock_widget
            self.parent.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_widget)
            dock_widget.setVisible(True)
            dock_widget.show()
            return dock_widget
        except Exception as e:
            exception(e, "Failed to load file explorer")
            return None

    def load_output_logs_widget(self):
        """Load the output logs dock widget and add it to the main window."""
        try:
            # Create and load the output logs widget
            logs = OutputLogsWidget(self.BASE_DIR)
            dock_widget = logs.load_ui()
            self.widgets['output_logs'] = dock_widget
            self.output_logs = logs
            set_output_logs(logs)
            
            # Connect output logs to main menu actions
            if hasattr(logs, 'connect_to_main_menu') and callable(logs.connect_to_main_menu):
                logs.connect_to_main_menu(self.parent)
            
            # Add the dock widget to the main window at the bottom
            self.parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
            dock_widget.setVisible(True)
            dock_widget.show()
            
            return dock_widget
        except Exception as e:
            exception(e, "Failed to load logs panel")
            return None

    def load_main_workspace(self):
        """Load the main workspace into the central widget."""
        try:
            # Load UI file
            ui_path = f"{self.BASE_DIR}/gui/layout/main_workspace.ui"
            loader = QtUiTools.QUiLoader()
            ui_file = QtCore.QFile(ui_path)
            
            if not ui_file.exists():
                error(f"Main workspace UI file not found")
                # Create a fallback widget
                workspace_widget = QtWidgets.QWidget()
                layout = QtWidgets.QVBoxLayout(workspace_widget)
                label = QtWidgets.QLabel("No workspace template found. Please check your installation.")
                label.setAlignment(QtCore.Qt.AlignCenter)
                layout.addWidget(label)
                self.parent.setCentralWidget(workspace_widget)
                return workspace_widget
                
            ui_file.open(QtCore.QFile.ReadOnly)
            workspace_widget = loader.load(ui_file)
            ui_file.close()
            
            # Set the workspace as the central widget
            self.parent.setCentralWidget(workspace_widget)
            return workspace_widget
        except Exception as e:
            exception(e, "Error loading main workspace")
            
            # Create a fallback widget
            workspace_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(workspace_widget)
            label = QtWidgets.QLabel(f"Workspace loading error: {str(e)}")
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)
            self.parent.setCentralWidget(workspace_widget)
            return workspace_widget
    
    def setup_ui(self):
        """Set up all UI components."""
        # This message is useful to show that the app is starting up
        self.load_output_logs_widget()
        
        self.load_main_workspace()
        self.load_explorer_widget()
        
        # Restore previous layout if available
        if not self.restore_layout():
            # If no saved layout exists, make sure all widgets are visible
            self.ensure_widgets_visible()
        
        # This message is useful to confirm the app is ready for use
        log("Ready")
        return self
    
    def ensure_widgets_visible(self):
        """Make sure all dock widgets are visible."""
        # Make sure all dock widgets are visible
        for widget_name, widget in self.widgets.items():
            widget.setVisible(True)
            if widget.isFloating():
                widget.setFloating(False)
        
        # Process events to update UI
        QtWidgets.QApplication.processEvents()
        
    def save_layout(self):
        """Save the current layout configuration."""
        self.settings.setValue("geometry", self.parent.saveGeometry())
        self.settings.setValue("windowState", self.parent.saveState())
        
    def restore_layout(self):
        """Restore the previously saved layout configuration."""
        geometry = self.settings.value("geometry")
        state = self.settings.value("windowState")
        
        if geometry and state:
            self.parent.restoreGeometry(geometry)
            self.parent.restoreState(state)
            
            # Ensure critical widgets are always visible
            for widget_name, widget in self.widgets.items():
                if not widget.isVisible():
                    widget.setVisible(True)
            
            # Removed redundant "restored layout" message
            return True
        else:
            # This is actually useful information
            debug("No saved layout found, using defaults")
            return False
    
    def reset_widgets_to_default(self):
        """Reset all dock widgets to their original default state."""
        # This message is useful to show a major UI change is happening
        log("Resetting to default layout...")
        
        # Clear saved layout settings
        self.settings.clear()
        
        # Define mappings for widget types to their UI files
        ui_paths = {
            'explorer': f"{self.BASE_DIR}/gui/widgets/explorer/explorer_widget.ui",
            'output_logs': f"{self.BASE_DIR}/gui/widgets/logs/output_logs.ui",
        }
        
        # Define widget positions
        widget_positions = {
            'explorer': QtCore.Qt.LeftDockWidgetArea,
            'output_logs': QtCore.Qt.BottomDockWidgetArea,
        }
        
        # Remove all dock widgets first
        for widget_name, widget in self.widgets.items():
            self.parent.removeDockWidget(widget)
            widget.resize(10, 10)  # Reset to small size first

        # Process events to ensure removals take effect
        QtWidgets.QApplication.processEvents()
        
        # Re-add each widget and reset its size to default
        for widget_name, widget in self.widgets.items():
            # Reset widget size from UI file
            if widget_name in ui_paths:
                reset_widget_to_default(widget, ui_paths[widget_name])
                
            # Add widget back to its correct position
            if widget_name in widget_positions:
                area = widget_positions[widget_name]
                self.parent.addDockWidget(area, widget)
                widget.setVisible(True)
                widget.raise_()
        
        # Refresh the main workspace
        self.load_main_workspace()
        
        # Process events to ensure all UI changes are applied
        QtWidgets.QApplication.processEvents()
        
        # Save this clean state as the new default
        self.save_layout()
        
        # Show a status message if the parent has a status bar
        status_bar = getattr(self.parent, 'statusBar', None)
        if status_bar and callable(status_bar):
            status_bar().showMessage("Layout reset to default", 2000)
        
        # Removed redundant "layout reset complete" message
        return True