from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PySide6 import QtUiTools, QtCore
from PySide6.QtGui import QColor, QBrush, QFont
import qtawesome as qta  # Import qtawesome for icons

class ExplorerWidget:
    def __init__(self, base_dir=None):
        """Initialize the explorer widget."""
        self.BASE_DIR = base_dir
        self.widget = None
        self.tree = None
        
        # Store references to hierarchical data for future implementation
        self.years = {}      # Dictionary to store year nodes: {year_str: year_item}
        self.months = {}     # Nested dictionary: {year_str: {month_str: month_item}}
        self.days = {}       # Nested dict: {year_str: {month_str: {day_str: day_item}}}
        self.ids = {}        # For storing ID items: {year: {month: {day: {id: id_item}}}}
        
        # Color palettes for individual items - can be customized per item
        self.year_colors = {}    # {year_str: QColor}
        self.month_colors = {}   # {year_str: {month_str: QColor}}
        self.day_colors = {}     # {year_str: {month_str: {day_str: QColor}}

    def load_ui(self):
        """Load the dock widget from UI file."""
        # Load UI file
        ui_path = f"{self.BASE_DIR}/gui/widgets/explorer/explorer_widget.ui"
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Access the dock widget content
        content_widget = self.widget.findChild(QWidget, "dockWidgetContents")
        
        # Create a vertical layout if not already present
        if content_widget.layout() is None:
            layout = QVBoxLayout(content_widget)
        else:
            layout = content_widget.layout()
            
        # Remove all margins to make the widget fill the entire dock
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Clear the layout (remove any existing widgets)
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create the tree widget without a header
        self.tree = QTreeWidget(content_widget)
        self.tree.setHeaderHidden(True)  # Hide the header
        
        # Important: Simply set this property to show branch lines
        self.tree.setRootIsDecorated(True)  # This controls whether branch indicators are shown
        
        # Add item padding to prevent crowding
        self.tree.setStyleSheet("""
            QTreeWidget::item {
                padding: 3px 0px;
            }
        """)
        
        # Create sample hierarchical data structure
        self.create_sample_data()
        
        # Expand the top levels by default
        for year_item in self.years.values():
            self.tree.expandItem(year_item)
        
        # Add tree to the layout
        layout.addWidget(self.tree)
        
        return self.widget

    def create_sample_data(self):
        """Create sample hierarchical data and store references."""
        # Define the bold font for years
        bold_font = QFont()
        bold_font.setBold(True)
        
        # === Year 2025 ===
        # Create year-specific color - use alpha=20 for background
        year_2025_color_bg = QColor(60, 120, 216, 20)  # Blue with alpha=20
        year_2025_color_fg = QColor(60, 120, 216)     # Same blue with full opacity for text
        
        year_2025 = QTreeWidgetItem(self.tree, ["2025"])
        year_2025.setFont(0, bold_font)
        
        # Add calendar icon for year
        year_icon = qta.icon('fa6s.calendar-days', color=year_2025_color_fg.name())
        year_2025.setIcon(0, year_icon)
        
        # Set both background and text color
        year_2025.setBackground(0, QBrush(year_2025_color_bg))
        year_2025.setForeground(0, QBrush(year_2025_color_fg))
        
        self.years["2025"] = year_2025
        self.year_colors["2025"] = year_2025_color_bg
        self.months["2025"] = {}
        self.month_colors["2025"] = {}
        self.days["2025"] = {}
        self.day_colors["2025"] = {}
        self.ids["2025"] = {}
        
        # === September 2025 ===
        # Create month-specific color with higher opacity
        sep_color_bg = QColor(46, 139, 87, 20)  # Green with alpha=20
        sep_color_fg = QColor(46, 139, 87)      # Same green with full opacity for text
        
        month_sep = QTreeWidgetItem(year_2025, ["September"])
        
        # Add month icon
        month_icon = qta.icon('fa6s.calendar-week', color=sep_color_fg.name())
        month_sep.setIcon(0, month_icon)
        
        # Set both background and text colors
        month_sep.setBackground(0, QBrush(sep_color_bg))
        month_sep.setForeground(0, QBrush(sep_color_fg))
        
        self.months["2025"]["September"] = month_sep
        self.month_colors["2025"]["September"] = sep_color_bg
        self.days["2025"]["September"] = {}
        self.day_colors["2025"]["September"] = {}
        self.ids["2025"]["September"] = {}
        
        # Days in September with specific background/text colors
        sep_15_color_bg = QColor(255, 140, 0, 20)    # Orange with alpha=20
        sep_15_color_fg = QColor(255, 140, 0)        # Same orange with full opacity
        
        sep_23_color_bg = QColor(255, 100, 100, 20)  # Light red with alpha=20
        sep_23_color_fg = QColor(255, 100, 100)      # Same light red with full opacity
        
        sep_30_color_bg = QColor(200, 200, 100, 20)  # Yellow-ish with alpha=20
        sep_30_color_fg = QColor(200, 200, 100)      # Same yellow-ish with full opacity
        
        day_date_colors = [
            ("15", sep_15_color_bg, sep_15_color_fg),
            ("23", sep_23_color_bg, sep_23_color_fg),
            ("30", sep_30_color_bg, sep_30_color_fg)
        ]
        
        for day, bg_color, fg_color in day_date_colors:
            day_item = QTreeWidgetItem(month_sep, [day])
            
            # Add day icon
            day_icon = qta.icon('fa6s.calendar-day', color=fg_color.name())
            day_item.setIcon(0, day_icon)
            
            # Set both background and text colors
            day_item.setBackground(0, QBrush(bg_color))
            day_item.setForeground(0, QBrush(fg_color))
            
            self.days["2025"]["September"][day] = day_item
            self.day_colors["2025"]["September"][day] = bg_color
            self.ids["2025"]["September"][day] = {}
        
        # IDs for September 15
        sep_15_ids = ["451654", "451655"]
        for id_value in sep_15_ids:
            id_item = QTreeWidgetItem(self.days["2025"]["September"]["15"], [id_value])
            # Use table icon and inherit color from parent date
            table_icon = qta.icon('fa6s.table', color=sep_15_color_fg.name())
            id_item.setIcon(0, table_icon)
            id_item.setForeground(0, QBrush(sep_15_color_fg))  # Use parent date color (no background)
            self.ids["2025"]["September"]["15"][id_value] = id_item
        
        # IDs for September 23
        sep_23_ids = ["462789", "462790", "462791"]
        for id_value in sep_23_ids:
            id_item = QTreeWidgetItem(self.days["2025"]["September"]["23"], [id_value])
            # Use table icon and inherit color from parent date
            table_icon = qta.icon('fa6s.table', color=sep_23_color_fg.name())
            id_item.setIcon(0, table_icon)
            id_item.setForeground(0, QBrush(sep_23_color_fg))  # Use parent date color (no background)
            self.ids["2025"]["September"]["23"][id_value] = id_item
        
        # IDs for September 30
        id_sep_30_1 = QTreeWidgetItem(self.days["2025"]["September"]["30"], ["475123"])
        table_icon = qta.icon('fa6s.table', color=sep_30_color_fg.name())
        id_sep_30_1.setIcon(0, table_icon)
        id_sep_30_1.setForeground(0, QBrush(sep_30_color_fg))  # Use parent date color (no background)
        self.ids["2025"]["September"]["30"]["475123"] = id_sep_30_1
        
        # === October 2025 ===
        # Create month-specific color with higher opacity
        oct_color_bg = QColor(100, 149, 237, 20)  # Cornflower blue with alpha=20
        oct_color_fg = QColor(100, 149, 237)      # Same cornflower blue with full opacity
        
        month_oct = QTreeWidgetItem(year_2025, ["October"])
        
        # Add month icon for October
        month_icon = qta.icon('fa6s.calendar-week', color=oct_color_fg.name())
        month_oct.setIcon(0, month_icon)
        
        # Set both background and text colors
        month_oct.setBackground(0, QBrush(oct_color_bg))
        month_oct.setForeground(0, QBrush(oct_color_fg))
        
        self.months["2025"]["October"] = month_oct
        self.month_colors["2025"]["October"] = oct_color_bg
        self.days["2025"]["October"] = {}
        self.day_colors["2025"]["October"] = {}
        self.ids["2025"]["October"] = {}
        
        # Days in October with specific colors
        oct_05_color_bg = QColor(180, 120, 240, 20)  # Purple-ish with alpha=20
        oct_05_color_fg = QColor(180, 120, 240)      # Same purple-ish with full opacity
        
        oct_12_color_bg = QColor(100, 200, 200, 20)  # Teal-ish with alpha=20
        oct_12_color_fg = QColor(100, 200, 200)      # Same teal-ish with full opacity
        
        day_date_colors = [
            ("05", oct_05_color_bg, oct_05_color_fg),
            ("12", oct_12_color_bg, oct_12_color_fg)
        ]
        
        for day, bg_color, fg_color in day_date_colors:
            day_item = QTreeWidgetItem(month_oct, [day])
            
            # Add day icon
            day_icon = qta.icon('fa6s.calendar-day', color=fg_color.name())
            day_item.setIcon(0, day_icon)
            
            # Set both background and text colors
            day_item.setBackground(0, QBrush(bg_color))
            day_item.setForeground(0, QBrush(fg_color))
            
            self.days["2025"]["October"][day] = day_item
            self.day_colors["2025"]["October"][day] = bg_color
            self.ids["2025"]["October"][day] = {}
        
        # IDs for October 05
        oct_05_ids = ["481234", "481235"]
        for id_value in oct_05_ids:
            id_item = QTreeWidgetItem(self.days["2025"]["October"]["05"], [id_value])
            table_icon = qta.icon('fa6s.table', color=oct_05_color_fg.name())
            id_item.setIcon(0, table_icon)
            id_item.setForeground(0, QBrush(oct_05_color_fg))  # Use parent date color (no background)
            self.ids["2025"]["October"]["05"][id_value] = id_item
        
        # IDs for October 12
        oct_12_ids = ["492001", "492002", "492003", "492004"]
        for id_value in oct_12_ids:
            id_item = QTreeWidgetItem(self.days["2025"]["October"]["12"], [id_value])
            table_icon = qta.icon('fa6s.table', color=oct_12_color_fg.name())
            id_item.setIcon(0, table_icon)
            id_item.setForeground(0, QBrush(oct_12_color_fg))  # Use parent date color (no background)
            self.ids["2025"]["October"]["12"][id_value] = id_item
