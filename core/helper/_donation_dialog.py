"""
Helper module for managing the donation dialog.

This module handles populating the donation dialog with content from the config file.
"""

import os
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QApplication, QToolTip
from PySide6.QtGui import QPixmap, QCursor  # Import QCursor from QtGui
from PySide6 import QtCore, QtWidgets
import qtawesome as qta

def populate_donation_dialog(dialog, config, base_dir):
    """
    Populate the donation dialog with content from the config file.
    
    Args:
        dialog: The donation dialog to populate
        config: The application configuration dictionary
        base_dir: The application base directory
    """
    donation_config = config.get("donation_dialog", {})
    
    # Set the dialog title
    title = donation_config.get("title", "Support Image Tea Mini")
    dialog.setWindowTitle(title)
    
    # Set the title and message labels
    if hasattr(dialog, 'label'):
        dialog.label.setText(donation_config.get("title", "Support Image Tea Mini"))
    
    if hasattr(dialog, 'label_2'):
        dialog.label_2.setText(donation_config.get("message", "If you like this app, please consider supporting its development."))
    
    # Populate e-wallet tab
    if hasattr(dialog, 'tab') and "ewallet" in donation_config:
        _populate_payment_tab(dialog.tab, donation_config["ewallet"])
    
    # Populate bank tab
    if hasattr(dialog, 'tab_2') and "bank" in donation_config:
        _populate_payment_tab(dialog.tab_2, donation_config["bank"])
    
    # Populate QRIS tab
    if hasattr(dialog, 'tab_3') and "QRIS" in donation_config:
        _populate_qris_tab(dialog.tab_3, donation_config["QRIS"], base_dir)
    
    # Populate thank you tab with a simple message
    if hasattr(dialog, 'scrollAreaWidgetContents'):
        _populate_thank_you_tab(dialog.scrollAreaWidgetContents)

def _copy_to_clipboard(text):
    """Copy text to clipboard and show a tooltip."""
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    # Fix the parameter order for showText
    QToolTip.showText(QCursor.pos(), "Copied to clipboard!", None)  # Remove the timeout parameter

def _populate_payment_tab(tab, payment_methods):
    """Create a layout with modern payment method cards."""

    
    layout = QVBoxLayout()
    layout.setSpacing(10)
    layout.setContentsMargins(20, 20, 20, 20)
    
    for method in payment_methods:
        name = method.get("name", "")
        number = method.get("number", "")
        color = method.get("color", "")
        account_name = method.get("account_name", "")
        image_path = method.get("image", "")
        max_width = method.get("max_width", 30)
        
        # Create a container for each payment method with modern card styling
        method_widget = QWidget()
        
        # Modern card styling with subtle shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QtCore.Qt.gray)
        shadow.setOffset(0, 2)
        method_widget.setGraphicsEffect(shadow)
        
        # Clean, modern card style
        style = """
            background-color: white;
            border-radius: 8px;
            padding: 0px;
            margin: 0px;
        """
        
        method_widget.setStyleSheet(style)
        
        # Main layout for the card
        card_layout = QVBoxLayout(method_widget)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Create a colored header
        header_widget = QWidget()
        if color:
            header_widget.setStyleSheet(f"background-color: {color}; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        else:
            header_widget.setStyleSheet("background-color: #f5f5f5; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Add logo if available
        if image_path:
            # Try to find the image
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            possible_paths = [
                os.path.join(base_dir, image_path),
                os.path.join(base_dir, "res", os.path.basename(image_path)),
                os.path.join(base_dir, "assets", os.path.basename(image_path)),
                os.path.join(base_dir, "images", os.path.basename(image_path)),
            ]
            
            # Find the first path that exists
            full_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    full_path = path
                    break
            
            if full_path:
                pixmap = QPixmap(full_path)
                if not pixmap.isNull():
                    logo_label = QLabel()
                    # Scale the pixmap while maintaining aspect ratio
                    if pixmap.width() > max_width:
                        pixmap_scaled = pixmap.scaledToWidth(max_width, QtCore.Qt.SmoothTransformation)
                        logo_label.setPixmap(pixmap_scaled)
                    else:
                        logo_label.setPixmap(pixmap)
                    
                    header_layout.addWidget(logo_label)
                    header_layout.addSpacing(10)
        
        # Add name to header
        name_label = QLabel(f"<b>{name}</b>")
        name_label.setStyleSheet("font-size: 14pt; color: white;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        # Add header to card
        card_layout.addWidget(header_widget)
        
        # Create content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Add account name if provided
        if account_name:
            account_label = QLabel(f"{account_name}")
            account_label.setStyleSheet("font-size: 11pt; color: #555555;")
            content_layout.addWidget(account_label)
        
        # Create a horizontal layout for the number and copy button
        number_container = QWidget()
        number_container.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 5px;
        """)
        
        number_layout = QHBoxLayout(number_container)
        number_layout.setContentsMargins(10, 5, 10, 5)
        number_layout.setSpacing(8)
        
        # Add method number with monospace font for better readability
        number_label = QLabel(f"<span style='font-family: monospace;'>{number}</span>")
        number_label.setStyleSheet("font-size: 12pt; color: #333333; font-weight: 500;")
        number_label.setCursor(QtCore.Qt.IBeamCursor)  # Show text cursor on hover
        
        # Make the number selectable
        number_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        number_layout.addWidget(number_label)
        
        # Add a modern copy button
        copy_button = QPushButton("")
        copy_button.setIcon(qta.icon('fa5s.copy', color="#555555"))
        copy_button.setToolTip("Copy to clipboard")
        copy_button.setFixedSize(28, 28)
        copy_button.setCursor(QtCore.Qt.PointingHandCursor)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # Connect copy button to clipboard function
        copy_button.clicked.connect(lambda checked=False, text=number: _copy_to_clipboard(text))
        
        number_layout.addWidget(copy_button)
        
        # Add the number container to the content layout
        content_layout.addWidget(number_container)
        
        # Add content to card
        card_layout.addWidget(content_widget)
        
        # Add the card to the main layout
        layout.addWidget(method_widget)
    
    # Add stretch to push all items to the top
    layout.addStretch()
    
    # Set the layout on the tab
    if tab.layout():
        # Clear existing layout if there is one
        while tab.layout().count():
            item = tab.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Delete the old layout
        old_layout = tab.layout()
        tab.setLayout(layout)
        old_layout.deleteLater()
    else:
        # Set new layout if there isn't one
        tab.setLayout(layout)

def _populate_qris_tab(tab, qris_data, base_dir):
    """Create a layout with QRIS image."""
    layout = QVBoxLayout()
    
    for qris in qris_data:
        image_path = qris.get("image", "")
        
        # Construct full path to image
        # Try multiple possible locations for the image
        possible_paths = [
            os.path.join(base_dir, image_path),                 # Direct path from config
            os.path.join(base_dir, "res", os.path.basename(image_path)),  # In res folder
            os.path.join(base_dir, "assets", os.path.basename(image_path)),  # In assets folder
            os.path.join(base_dir, "images", os.path.basename(image_path)),  # In images folder
        ]
        
        # Find the first path that exists
        full_path = None
        for path in possible_paths:
            if os.path.exists(path):
                full_path = path
                break
        
        # If image exists, add it to the layout
        if full_path:
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                # Get the max width from config or use default
                max_width = qris.get("max_width", 300)
                
                # Create a QLabel for the image
                image_label = QLabel()
                
                # Scale the pixmap while maintaining aspect ratio
                if pixmap.width() > max_width:
                    pixmap_scaled = pixmap.scaledToWidth(max_width, QtCore.Qt.SmoothTransformation)
                    image_label.setPixmap(pixmap_scaled)
                else:
                    image_label.setPixmap(pixmap)
                
                # Don't scale the contents (prevents squishing)
                image_label.setScaledContents(False)
                # Use aspect ratio preserving scaling
                image_label.setAlignment(QtCore.Qt.AlignCenter)
                # Set size policy to expand horizontally but fixed vertically
                image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                
                # Center the image horizontally
                image_container = QWidget()
                h_layout = QHBoxLayout(image_container)
                h_layout.addStretch()
                h_layout.addWidget(image_label)
                h_layout.addStretch()
                
                layout.addWidget(image_container)
            else:
                # Add a label indicating the image couldn't be loaded
                error_label = QLabel(f"Error loading QRIS image: {os.path.basename(image_path)}")
                layout.addWidget(error_label)
        else:
            # Add a label indicating the image couldn't be found
            not_found_label = QLabel(f"QRIS image not found: {os.path.basename(image_path)}")
            layout.addWidget(not_found_label)
    
    # Add stretch to push everything to the top
    layout.addStretch()
    
    # Set the layout on the tab
    if tab.layout():
        # Clear existing layout if there is one
        while tab.layout().count():
            item = tab.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Delete the old layout
        old_layout = tab.layout()
        tab.setLayout(layout)
        old_layout.deleteLater()
    else:
        # Set new layout if there isn't one
        tab.setLayout(layout)

def _populate_thank_you_tab(content_widget):
    """Populate the thank you tab with a message and supporters list."""
    layout = QVBoxLayout()
    
    # Add a thank you message
    thank_you_label = QLabel(
        "<h2>Thank You!</h2>"
        "<p>Your support helps us continue developing and improving Image Tea Mini.</p>"
        "<p>Every contribution, no matter how small, makes a difference and is greatly appreciated.</p>"
    )
    thank_you_label.setWordWrap(True)
    layout.addWidget(thank_you_label)
    
    # Add supporters list from supporters.txt
    supporters_label = QLabel("<h3>Our Awesome Supporters:</h3>")
    layout.addWidget(supporters_label)
    
    # Get the application's base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    supporters_file = os.path.join(base_dir, "supporters.txt")
    
    supporters_text = ""
    if os.path.exists(supporters_file):
        try:
            with open(supporters_file, 'r', encoding='utf-8') as file:
                supporters = file.read().strip().split('\n')
                # Filter out empty lines and comments
                supporters = [s for s in supporters if s and not s.startswith('//')]
                if supporters:
                    supporters_text = "<ul>"
                    for supporter in supporters:
                        supporters_text += f"<li>{supporter}</li>"
                    supporters_text += "</ul>"
                else:
                    supporters_text = "<p><i>Be the first to support us!</i></p>"
        except Exception as e:
            supporters_text = f"<p><i>Error loading supporters list: {str(e)}</i></p>"
    else:
        supporters_text = "<p><i>Be the first to support us!</i></p>"
    
    # Create and add the supporters list
    supporters_list = QLabel(supporters_text)
    supporters_list.setWordWrap(True)
    supporters_list.setTextFormat(QtCore.Qt.RichText)
    layout.addWidget(supporters_list)
    
    # Add stretch to push content to the top
    layout.addStretch()
    
    # Set the layout on the content widget
    if content_widget.layout():
        # Clear existing layout if there is one
        while content_widget.layout().count():
            item = content_widget.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Delete the old layout
        old_layout = content_widget.layout()
        content_widget.setLayout(layout)
        old_layout.deleteLater()
    else:
        # Set new layout if there isn't one
        content_widget.setLayout(layout)
