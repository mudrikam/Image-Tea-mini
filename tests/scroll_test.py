import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QScrollArea, QLabel, QFrame
)
from PySide6.QtCore import Qt

class ScrollTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Scroll Test")
        self.resize(400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create a QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # No styling - use native PySide6 scrollbars
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for content
        container = QFrame()
        container_layout = QVBoxLayout(container)
        
        # Add lorem ipsum paragraphs
        for i in range(20):
            paragraph = QLabel(
                f"Paragraph {i+1}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                f"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                f"Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi "
                f"ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit "
                f"in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
            )
            paragraph.setWordWrap(True)
            container_layout.addWidget(paragraph)
        
        # Set container as scroll area widget
        scroll_area.setWidget(container)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

def main():
    app = QApplication(sys.argv)
    
    # Set application style to the most native-looking style
    # This ensures we get the platform's default scrollbar appearance
    app.setStyle('fusion')  # Fusion style is generally good across platforms
    
    window = ScrollTest()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
