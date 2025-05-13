import os
from PySide6 import QtWidgets, QtUiTools, QtCore
from PySide6.QtCore import Qt


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
    dialog.label.setText(explanation_text)    # Initialize the progress bar
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
    
    # Update the progress
    dialog.progressBar.setValue(10)
    
    # TODO: Implement the actual update process here
    # This would include:
    # 1. Downloading the latest version
    # 2. Creating a backup of important files (optional)
    # 3. Replacing the application files
    # 4. Restarting the application if needed
    
    # For now, just simulate progress
    import time
    for i in range(10, 100, 10):
        dialog.progressBar.setValue(i)
        time.sleep(0.5)
    
    dialog.progressBar.setValue(100)
    
    # Re-enable the cancel button
    dialog.btnCancel.setEnabled(True)