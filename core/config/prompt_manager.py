from PySide6.QtWidgets import (QDialog, QMessageBox, QVBoxLayout, QTextEdit, QLabel, QPushButton, 
                             QHBoxLayout, QFrame, QSpinBox, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pathlib import Path
from core.config.ai_config_manager import config_manager
from core.helper._window_utils import center_window
import qtawesome as qta
import json

class PromptManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.original_prompts = {}  # Store original values for cancel
        self.presets = self.load_presets()
        self.current_preset = None  # Track current active preset
        self.loading_preset = False  # Flag to prevent auto-save during preset loading
        self.create_ui()
        self.setup_icons()
        self.setup_connections()
        self.load_prompts()
        
        # Set window properties
        self.setModal(True)
        self.resize(1000, 700)
        self.setMinimumSize(950, 650)
        center_window(self)

    def load_presets(self):
        """Load preset prompts from JSON file"""
        try:
            presets_path = Path(__file__).parent / "prompt_presets.json"
            print(f"[DEBUG] Loading presets from: {presets_path}")
            with open(presets_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_preset = data.get('active_preset', 'preset_1')
                presets = data.get('presets', {})
                
                # Debug preset content
                for key, preset in presets.items():
                    print(f"[DEBUG] Preset {key} base_prompt: {preset.get('base_prompt', '')[:50]}...")
                    print(f"[DEBUG] Preset {key} default_prompt: {preset.get('default_prompt', '')[:50]}...")
                
                return presets
        except Exception as e:
            print(f"[WARNING] Failed to load prompt presets: {e}")
            return {}

    def save_presets(self):
        """Save presets back to JSON file"""
        try:
            presets_path = Path(__file__).parent / "prompt_presets.json"
            data = {
                "active_preset": self.current_preset,
                "presets": self.presets
            }
            with open(presets_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to save presets: {e}")

    def create_ui(self):
        """Create UI elements programmatically"""
        # Set window title and icon
        self.setWindowTitle("Kelola Prompt")
        self.setWindowIcon(qta.icon('fa6s.message'))
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Header frame
        self.headerFrame = QFrame()
        self.headerFrame.setStyleSheet("""
            QFrame#headerFrame {
                background-color: rgba(96, 125, 139, 0.1);
                border: 1px solid rgba(96, 125, 139, 0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.headerFrame.setObjectName("headerFrame")
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        self.titleLabel = QLabel("🤖 Kelola Prompt AI")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        header_layout.addWidget(self.titleLabel)
        
        # Description label
        self.descLabel = QLabel("Atur prompt AI untuk analisis gambar yang lebih akurat dan personal")
        desc_font = QFont()
        desc_font.setPointSize(10)
        desc_font.setItalic(True)
        self.descLabel.setFont(desc_font)
        self.descLabel.setStyleSheet("color: rgba(128, 128, 128, 0.8);")
        header_layout.addWidget(self.descLabel)
        
        self.headerFrame.setLayout(header_layout)
        main_layout.addWidget(self.headerFrame)
        
        # Preset buttons layout
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)
        
        self.presetMetadataButton = QPushButton("Preset 1")
        self.presetDescriptionButton = QPushButton("Preset 2")
        self.presetTagsButton = QPushButton("Preset 3")
        self.presetAdvancedButton = QPushButton("Preset 4")
        self.presetMicrostockButton = QPushButton("Preset 5")
        
        # Add preset buttons to layout
        preset_layout.addWidget(self.presetMetadataButton)
        preset_layout.addWidget(self.presetDescriptionButton)
        preset_layout.addWidget(self.presetTagsButton)
        preset_layout.addWidget(self.presetAdvancedButton)
        preset_layout.addWidget(self.presetMicrostockButton)
        preset_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.resetButton = QPushButton("Reset")
        self.resetButton.setToolTip("Reset semua prompt ke default")
        preset_layout.addWidget(self.resetButton)
        
        main_layout.addLayout(preset_layout)
        
        # Settings frame
        self.settingsFrame = QFrame()
        self.settingsFrame.setStyleSheet("""
            QFrame#settingsFrame {
                background-color: rgba(96, 125, 139, 0.1);
                border: 1px solid rgba(96, 125, 139, 0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.settingsFrame.setObjectName("settingsFrame")
        
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(8)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        # Settings label
        self.settingsLabel = QLabel("⚙️ Pengaturan Prompt")
        settings_font = QFont()
        settings_font.setBold(True)
        self.settingsLabel.setFont(settings_font)
        settings_layout.addWidget(self.settingsLabel)
        
        # Settings controls layout
        settings_controls_layout = QHBoxLayout()
        
        # Title length settings
        title_layout = QHBoxLayout()
        self.titleMinLabel = QLabel("Title:")
        title_layout.addWidget(self.titleMinLabel)
        
        self.titleMinSpinBox = QSpinBox()
        self.titleMinSpinBox.setMinimum(0)
        self.titleMinSpinBox.setMaximum(1000)
        self.titleMinSpinBox.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px;
                border: 1px solid rgba(128, 128, 128, 0.1);
                border-radius: 4px;
                background-color: rgba(128, 128, 128, 0.02);
                font-size: 9pt;
            }
            QSpinBox:hover {
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
            QSpinBox:focus {
                border: 2px solid rgba(96, 125, 139, 0.6);
            }
        """)
        title_layout.addWidget(self.titleMinSpinBox)
        
        self.titleToLabel = QLabel("-")
        title_layout.addWidget(self.titleToLabel)
        
        self.titleMaxSpinBox = QSpinBox()
        self.titleMaxSpinBox.setMinimum(0)
        self.titleMaxSpinBox.setMaximum(1000)
        self.titleMaxSpinBox.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px;
                border: 1px solid rgba(128, 128, 128, 0.1);
                border-radius: 4px;
                background-color: rgba(128, 128, 128, 0.02);
                font-size: 9pt;
            }
            QSpinBox:hover {
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
            QSpinBox:focus {
                border: 2px solid rgba(96, 125, 139, 0.6);
            }
        """)
        title_layout.addWidget(self.titleMaxSpinBox)
        
        settings_controls_layout.addLayout(title_layout)
        
        # Tags count settings
        tags_layout = QHBoxLayout()
        self.tagsCountLabel = QLabel("Keywords:")
        tags_layout.addWidget(self.tagsCountLabel)
        
        self.tagsCountSpinBox = QSpinBox()
        self.tagsCountSpinBox.setMinimum(0)
        self.tagsCountSpinBox.setMaximum(100)
        self.tagsCountSpinBox.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px;
                border: 1px solid rgba(128, 128, 128, 0.1);
                border-radius: 4px;
                background-color: rgba(128, 128, 128, 0.02);
                font-size: 9pt;
            }
            QSpinBox:hover {
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
            QSpinBox:focus {
                border: 2px solid rgba(96, 125, 139, 0.6);
            }
        """)
        tags_layout.addWidget(self.tagsCountSpinBox)
        
        settings_controls_layout.addLayout(tags_layout)
        
        # Description length settings
        desc_layout = QHBoxLayout()
        self.descriptionMaxLabel = QLabel("Description Max:")
        desc_layout.addWidget(self.descriptionMaxLabel)
        
        self.descriptionMaxSpinBox = QSpinBox()
        self.descriptionMaxSpinBox.setMinimum(0)
        self.descriptionMaxSpinBox.setMaximum(10000)
        self.descriptionMaxSpinBox.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px;
                border: 1px solid rgba(128, 128, 128, 0.1);
                border-radius: 4px;
                background-color: rgba(128, 128, 128, 0.02);
                font-size: 9pt;
            }
            QSpinBox:hover {
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
            QSpinBox:focus {
                border: 2px solid rgba(96, 125, 139, 0.6);
            }
        """)
        desc_layout.addWidget(self.descriptionMaxSpinBox)
        
        settings_controls_layout.addLayout(desc_layout)
        
        settings_controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        settings_layout.addLayout(settings_controls_layout)
        
        self.settingsFrame.setLayout(settings_layout)
        main_layout.addWidget(self.settingsFrame)
        
        # Main content layout
        main_content_layout = QHBoxLayout()
        
        # Left column
        left_column_frame = QFrame()
        left_column_layout = QVBoxLayout()
        left_column_layout.setSpacing(8)
        left_column_layout.setContentsMargins(0, 0, 0, 0)
        
        # Base prompt frame
        self.basePromptFrame = QFrame()
        self.basePromptFrame.setStyleSheet("""
            QFrame#basePromptFrame {
                background-color: rgba(33, 150, 243, 0.05);
                border: 1px solid rgba(33, 150, 243, 0.2);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.basePromptFrame.setObjectName("basePromptFrame")
        
        base_prompt_layout = QVBoxLayout()
        base_prompt_layout.setSpacing(4)
        base_prompt_layout.setContentsMargins(0, 0, 0, 0)
        
        self.basePromptLabel = QLabel("⚙️ Base Prompt")
        base_prompt_font = QFont()
        base_prompt_font.setBold(True)
        self.basePromptLabel.setFont(base_prompt_font)
        base_prompt_layout.addWidget(self.basePromptLabel)
        
        self.basePromptEdit = QTextEdit()
        self.basePromptEdit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
        """)
        self.basePromptEdit.setFrameShape(QFrame.NoFrame)
        base_prompt_layout.addWidget(self.basePromptEdit)
        
        self.basePromptFrame.setLayout(base_prompt_layout)
        left_column_layout.addWidget(self.basePromptFrame)
        
        # Default prompt frame
        self.defaultPromptFrame = QFrame()
        self.defaultPromptFrame.setStyleSheet("""
            QFrame#defaultPromptFrame {
                background-color: rgba(76, 175, 80, 0.05);
                border: 1px solid rgba(76, 175, 80, 0.2);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.defaultPromptFrame.setObjectName("defaultPromptFrame")
        
        default_prompt_layout = QVBoxLayout()
        default_prompt_layout.setSpacing(4)
        default_prompt_layout.setContentsMargins(0, 0, 0, 0)
        
        self.defaultPromptLabel = QLabel("📄 Default Prompt")
        default_prompt_font = QFont()
        default_prompt_font.setBold(True)
        self.defaultPromptLabel.setFont(default_prompt_font)
        default_prompt_layout.addWidget(self.defaultPromptLabel)
        
        self.defaultPromptEdit = QTextEdit()
        self.defaultPromptEdit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
        """)
        self.defaultPromptEdit.setFrameShape(QFrame.NoFrame)
        default_prompt_layout.addWidget(self.defaultPromptEdit)
        
        self.defaultPromptFrame.setLayout(default_prompt_layout)
        left_column_layout.addWidget(self.defaultPromptFrame)
        
        left_column_frame.setLayout(left_column_layout)
        main_content_layout.addWidget(left_column_frame)
        
        # Right column
        right_column_frame = QFrame()
        right_column_layout = QVBoxLayout()
        right_column_layout.setSpacing(8)
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        
        # Custom prompt frame
        self.customPromptFrame = QFrame()
        self.customPromptFrame.setStyleSheet("""
            QFrame#customPromptFrame {
                background-color: rgba(156, 39, 176, 0.05);
                border: 1px solid rgba(156, 39, 176, 0.2);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.customPromptFrame.setObjectName("customPromptFrame")
        
        custom_prompt_layout = QVBoxLayout()
        custom_prompt_layout.setSpacing(4)
        custom_prompt_layout.setContentsMargins(0, 0, 0, 0)
        
        self.customPromptLabel = QLabel("🔧 Custom Prompt")
        custom_prompt_font = QFont()
        custom_prompt_font.setBold(True)
        self.customPromptLabel.setFont(custom_prompt_font)
        custom_prompt_layout.addWidget(self.customPromptLabel)
        
        self.customPromptEdit = QTextEdit()
        self.customPromptEdit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
        """)
        self.customPromptEdit.setFrameShape(QFrame.NoFrame)
        custom_prompt_layout.addWidget(self.customPromptEdit)
        
        self.customPromptFrame.setLayout(custom_prompt_layout)
        right_column_layout.addWidget(self.customPromptFrame)
        
        # Bottom row for negative/exclude/mandatory prompts
        bottom_row_layout = QHBoxLayout()
        
        # Negative prompt frame
        self.negativePromptFrame = QFrame()
        self.negativePromptFrame.setStyleSheet("""
            QFrame#negativePromptFrame {
                background-color: rgba(255, 152, 0, 0.05);
                border: 1px solid rgba(255, 152, 0, 0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.negativePromptFrame.setObjectName("negativePromptFrame")
        
        negative_prompt_layout = QVBoxLayout()
        negative_prompt_layout.setSpacing(4)
        negative_prompt_layout.setContentsMargins(0, 0, 0, 0)
        
        self.negativePromptLabel = QLabel("⚠️ Negative Prompt")
        negative_prompt_font = QFont()
        negative_prompt_font.setBold(True)
        self.negativePromptLabel.setFont(negative_prompt_font)
        negative_prompt_layout.addWidget(self.negativePromptLabel)
        
        self.negativePromptEdit = QTextEdit()
        self.negativePromptEdit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                padding: 6px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 8pt;
            }
        """)
        self.negativePromptEdit.setFrameShape(QFrame.NoFrame)
        negative_prompt_layout.addWidget(self.negativePromptEdit)
        
        self.negativePromptFrame.setLayout(negative_prompt_layout)
        bottom_row_layout.addWidget(self.negativePromptFrame)
        
        # Exclude prompt frame
        self.excludePromptFrame = QFrame()
        self.excludePromptFrame.setStyleSheet("""
            QFrame#excludePromptFrame {
                background-color: rgba(244, 67, 54, 0.05);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.excludePromptFrame.setObjectName("excludePromptFrame")
        
        exclude_prompt_layout = QVBoxLayout()
        exclude_prompt_layout.setSpacing(4)
        exclude_prompt_layout.setContentsMargins(0, 0, 0, 0)
        
        self.excludePromptLabel = QLabel("🚫 Exclude Prompt")
        exclude_prompt_font = QFont()
        exclude_prompt_font.setBold(True)
        self.excludePromptLabel.setFont(exclude_prompt_font)
        exclude_prompt_layout.addWidget(self.excludePromptLabel)
        
        self.excludePromptEdit = QTextEdit()
        self.excludePromptEdit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                padding: 6px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 8pt;
            }
        """)
        self.excludePromptEdit.setFrameShape(QFrame.NoFrame)
        exclude_prompt_layout.addWidget(self.excludePromptEdit)
        
        self.excludePromptFrame.setLayout(exclude_prompt_layout)
        bottom_row_layout.addWidget(self.excludePromptFrame)
        
        right_column_layout.addLayout(bottom_row_layout)
        
        # Mandatory prompt frame
        self.mandatoryPromptFrame = QFrame()
        self.mandatoryPromptFrame.setStyleSheet("""
            QFrame#mandatoryPromptFrame {
                background-color: rgba(244, 67, 54, 0.05);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.mandatoryPromptFrame.setObjectName("mandatoryPromptFrame")
        
        mandatory_prompt_layout = QVBoxLayout()
        mandatory_prompt_layout.setSpacing(4)
        mandatory_prompt_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mandatoryPromptLabel = QLabel("🔒 Mandatory Prompt")
        mandatory_prompt_font = QFont()
        mandatory_prompt_font.setBold(True)
        self.mandatoryPromptLabel.setFont(mandatory_prompt_font)
        mandatory_prompt_layout.addWidget(self.mandatoryPromptLabel)
        
        self.mandatoryPromptEdit = QTextEdit()
        self.mandatoryPromptEdit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: rgba(244, 67, 54, 0.02);
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 8pt;
                color: rgba(128, 128, 128, 0.8);
            }
            QTextEdit:disabled {
                background-color: rgba(244, 67, 54, 0.02);
                color: rgba(128, 128, 128, 0.7);
            }
        """)
        self.mandatoryPromptEdit.setFrameShape(QFrame.NoFrame)
        self.mandatoryPromptEdit.setReadOnly(True)
        self.mandatoryPromptEdit.setToolTip("Prompt wajib yang diperlukan agar aplikasi dapat memproses respons AI dengan benar. Tidak dapat diedit secara manual.")
        mandatory_prompt_layout.addWidget(self.mandatoryPromptEdit)
        
        self.mandatoryPromptFrame.setLayout(mandatory_prompt_layout)
        right_column_layout.addWidget(self.mandatoryPromptFrame)
        
        right_column_frame.setLayout(right_column_layout)
        main_content_layout.addWidget(right_column_frame)
        
        main_layout.addLayout(main_content_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.previewButton = QPushButton("Preview")
        self.previewButton.setToolTip("Preview prompt final")
        self.previewButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(156, 39, 176, 0.1);
                border: 1px solid rgba(156, 39, 176, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(156, 39, 176, 0.2);
                border: 1px solid rgba(156, 39, 176, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(156, 39, 176, 0.3);
                border: 1px solid rgba(156, 39, 176, 0.7);
            }
        """)
        button_layout.addWidget(self.previewButton)
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.saveButton = QPushButton("Simpan")
        self.saveButton.setToolTip("Simpan semua perubahan")
        save_font = QFont()
        save_font.setBold(True)
        self.saveButton.setFont(save_font)
        self.saveButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(76, 175, 80, 0.15);
                border: 1px solid rgba(76, 175, 80, 0.4);
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.25);
                border: 1px solid rgba(76, 175, 80, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.35);
                border: 1px solid rgba(76, 175, 80, 0.8);
            }
        """)
        button_layout.addWidget(self.saveButton)
        
        self.cancelButton = QPushButton("Batal")
        self.cancelButton.setToolTip("Batal tanpa menyimpan")
        self.cancelButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(158, 158, 158, 0.1);
                border: 1px solid rgba(158, 158, 158, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(158, 158, 158, 0.2);
                border: 1px solid rgba(158, 158, 158, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(158, 158, 158, 0.3);
                border: 1px solid rgba(158, 158, 158, 0.7);
            }
        """)
        button_layout.addWidget(self.cancelButton)
        
        main_layout.addLayout(button_layout)
        
        # Set the main layout
        self.setLayout(main_layout)
    
    def setup_icons(self):
        """Setup QtAwesome icons for buttons and labels"""
        # Header title with emoji is already set in create_ui
        
        # Add QtAwesome icons as separate labels next to section labels
        self._add_icon_to_label(self.basePromptLabel, 'fa6s.gear', '#666')
        self._add_icon_to_label(self.defaultPromptLabel, 'fa6s.file', '#666')
        self._add_icon_to_label(self.customPromptLabel, 'fa6s.wrench', '#666')
        self._add_icon_to_label(self.negativePromptLabel, 'fa6s.triangle-exclamation', '#FF9800')
        self._add_icon_to_label(self.excludePromptLabel, 'fa6s.ban', '#F44336')
        self._add_icon_to_label(self.mandatoryPromptLabel, 'fa6s.lock', '#F44336')
        self._add_icon_to_label(self.settingsLabel, 'fa6s.sliders', '#2196F3')
        
        # Update button labels and icons for numbered presets
        self.presetMetadataButton.setText("Preset 1")
        self.presetMetadataButton.setIcon(qta.icon('fa6s.bookmark', color='#2196F3'))
        
        self.presetDescriptionButton.setText("Preset 2")
        self.presetDescriptionButton.setIcon(qta.icon('fa6s.bookmark', color='#4CAF50'))
        
        self.presetTagsButton.setText("Preset 3")
        self.presetTagsButton.setIcon(qta.icon('fa6s.bookmark', color='#FF9800'))
        
        self.presetAdvancedButton.setText("Preset 4")
        self.presetAdvancedButton.setIcon(qta.icon('fa6s.bookmark', color='#9C27B0'))
        
        self.presetMicrostockButton.setText("Preset 5")
        self.presetMicrostockButton.setIcon(qta.icon('fa6s.bookmark', color='#FF5722'))
        
        # Other buttons
        self.resetButton.setIcon(qta.icon('fa6s.eraser', color='#F44336'))
        self.previewButton.setIcon(qta.icon('fa6s.file-lines', color='#9C27B0'))
        self.saveButton.setIcon(qta.icon('fa6s.check', color='#4CAF50'))
        self.cancelButton.setIcon(qta.icon('fa6s.xmark', color='#666'))
        
        # Set window icon
        self.setWindowIcon(qta.icon('fa6s.message', color='#25D366'))
        
        # Update button styles to show active state
        self.update_preset_button_styles()

    def update_preset_button_styles(self):
        """Update button styles to show which preset is active"""
        buttons = {
            'preset_1': self.presetMetadataButton,
            'preset_2': self.presetDescriptionButton,
            'preset_3': self.presetTagsButton,
            'preset_4': self.presetAdvancedButton,
            'preset_5': self.presetMicrostockButton
        }
        
        for preset_key, button in buttons.items():
            if preset_key == self.current_preset:
                # Active preset style
                button.setStyleSheet("""
                    QPushButton {
                        padding: 8px 16px;
                        border-radius: 6px;
                        background-color: rgba(33, 150, 243, 0.3);
                        border: 2px solid rgba(33, 150, 243, 0.8);
                        font-weight: bold;
                        color: #1976D2;
                    }
                    QPushButton:hover {
                        background-color: rgba(33, 150, 243, 0.4);
                        border: 2px solid rgba(33, 150, 243, 1.0);
                    }
                """)
                # Update tooltip with preset name
                preset_data = self.presets.get(preset_key, {})
                button.setToolTip(f"✓ AKTIF: {preset_data.get('name', 'Preset')} - {preset_data.get('description', '')}")
            else:
                # Inactive preset style
                base_color = {
                    'preset_1': '33, 150, 243',
                    'preset_2': '76, 175, 80', 
                    'preset_3': '255, 152, 0',
                    'preset_4': '156, 39, 176',
                    'preset_5': '255, 87, 34'
                }.get(preset_key, '128, 128, 128')
                
                button.setStyleSheet(f"""
                    QPushButton {{
                        padding: 8px 16px;
                        border-radius: 6px;
                        background-color: rgba({base_color}, 0.1);
                        border: 1px solid rgba({base_color}, 0.3);
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: rgba({base_color}, 0.2);
                        border: 1px solid rgba({base_color}, 0.5);
                    }}
                    QPushButton:pressed {{
                        background-color: rgba({base_color}, 0.3);
                        border: 1px solid rgba({base_color}, 0.7);
                    }}
                """)
                preset_data = self.presets.get(preset_key, {})
                button.setToolTip(f"{preset_data.get('name', 'Preset')} - {preset_data.get('description', '')}")

    def _add_icon_to_label(self, label, icon_name, color):
        """Add QtAwesome icon as separate label before the text label"""
        try:
            # Create icon label
            icon_label = QLabel()
            icon = qta.icon(icon_name, color=color)
            icon_label.setPixmap(icon.pixmap(16, 16))
            icon_label.setFixedSize(20, 20)
            icon_label.setAlignment(Qt.AlignCenter)
            
            # Get parent layout
            parent_layout = label.parent().layout()
            if parent_layout:
                # Find label index in layout
                for i in range(parent_layout.count()):
                    item = parent_layout.itemAt(i)
                    if item.widget() == label:
                        # Insert icon label before text label
                        icon_layout = QHBoxLayout()
                        icon_layout.setContentsMargins(0, 0, 0, 0)
                        icon_layout.setSpacing(6)
                        icon_layout.addWidget(icon_label)
                        icon_layout.addWidget(label)
                        icon_layout.addStretch()
                        
                        # Replace the single label with icon+text layout
                        parent_layout.removeWidget(label)
                        parent_layout.insertLayout(i, icon_layout)
                        break
        except Exception as e:
            print(f"[WARNING] Failed to add icon to label: {e}")
            # Fallback: just keep the original label

    def setup_connections(self):
        """Setup signal connections"""
        # Change preset buttons to radio button style
        self.presetMetadataButton.clicked.connect(lambda: self.select_preset('preset_1'))
        self.presetDescriptionButton.clicked.connect(lambda: self.select_preset('preset_2'))
        self.presetTagsButton.clicked.connect(lambda: self.select_preset('preset_3'))
        self.presetAdvancedButton.clicked.connect(lambda: self.select_preset('preset_4'))
        self.presetMicrostockButton.clicked.connect(lambda: self.select_preset('preset_5'))
        
        self.resetButton.clicked.connect(self.reset_to_default)
        self.previewButton.clicked.connect(self.preview_prompt)
        self.saveButton.clicked.connect(self.save_changes)
        self.cancelButton.clicked.connect(self.cancel_changes)
        
        # Settings controls connections
        self.titleMinSpinBox.valueChanged.connect(self.on_settings_changed)
        self.titleMaxSpinBox.valueChanged.connect(self.on_settings_changed)
        self.tagsCountSpinBox.valueChanged.connect(self.on_settings_changed)
        self.descriptionMaxSpinBox.valueChanged.connect(self.on_settings_changed)
        
        # Auto-save ONLY to config.json when text changes (not to preset)
        self.basePromptEdit.textChanged.connect(self.on_prompt_text_changed_config_only)
        self.defaultPromptEdit.textChanged.connect(self.on_prompt_text_changed_config_only)
        self.customPromptEdit.textChanged.connect(self.on_prompt_text_changed_config_only)
        self.negativePromptEdit.textChanged.connect(self.on_prompt_text_changed_config_only)
        self.excludePromptEdit.textChanged.connect(self.on_prompt_text_changed_config_only)

    def on_settings_changed(self):
        """Handle settings changes and auto-save to current preset"""
        # Skip if we're loading a preset
        if self.loading_preset:
            return
            
        # Auto-save settings when changed
        settings = {
            'title_min_length': self.titleMinSpinBox.value(),
            'title_max_length': self.titleMaxSpinBox.value(),
            'tags_count': self.tagsCountSpinBox.value(),
            'description_max_length': self.descriptionMaxSpinBox.value()
        }
        
        # Validate that min <= max for title length
        if settings['title_min_length'] > settings['title_max_length']:
            settings['title_max_length'] = settings['title_min_length']
            self.titleMaxSpinBox.setValue(settings['title_max_length'])
        
        # Auto-save settings to current preset
        if self.current_preset and self.current_preset in self.presets:
            self.presets[self.current_preset]['settings'] = settings
            self.save_presets()  # Auto-save presets file when settings change
        
        # Auto-save to config.json (config follows preset)
        self.auto_save_to_config()
        
        # Reload prompts with new settings applied FROM PRESET (not config)
        self.reload_prompts_from_preset()

    def on_prompt_text_changed_config_only(self):
        """Auto-save ONLY to config.json when prompt text changes - DO NOT save to preset"""
        # Skip if we're loading a preset to avoid overwriting placeholders
        if self.loading_preset:
            return
            
        # Only auto-save to config.json with current UI values (processed)
        # DO NOT save back to preset - preserve placeholders in preset
        self.auto_save_to_config_from_ui()

    def auto_save_to_config_from_ui(self):
        """Auto-save current UI values directly to config.json (processed values, not placeholders)"""
        # Get current processed values from UI
        current_ui_values = {
            'base_prompt': self.basePromptEdit.toPlainText().strip(),
            'default_prompt': self.defaultPromptEdit.toPlainText().strip(),
            'custom_prompt': self.customPromptEdit.toPlainText().strip(),
            'negative_prompt': self.negativePromptEdit.toPlainText().strip(),
            'exclude_prompt': self.excludePromptEdit.toPlainText().strip(),
            'mandatory_prompt': self.mandatoryPromptEdit.toPlainText().strip()
        }
        
        print(f"[DEBUG] Auto-saving UI values to config.json (processed values)")
        
        # Update main config with current UI values (already processed)
        if 'prompts' not in self.config_manager._config['prompting']:
            self.config_manager._config['prompting']['prompts'] = {}
        
        # Update config with processed UI values
        for key, value in current_ui_values.items():
            self.config_manager._config['prompting']['prompts'][key] = value
        
        # Update settings from current preset
        if self.current_preset and self.current_preset in self.presets:
            settings = self.presets[self.current_preset].get('settings', {})
            self.config_manager.update_prompt_settings(settings)
        
        # Save config
        self.config_manager.save_config()
        print(f"[DEBUG] Config.json updated with current UI values (auto-save)")

    def reload_prompts_from_preset(self):
        """Reload prompts FROM CURRENT PRESET and apply current settings placeholders"""
        if not self.current_preset or self.current_preset not in self.presets:
            return
        
        # Get current settings values
        title_min = self.titleMinSpinBox.value()
        title_max = self.titleMaxSpinBox.value()
        tags_count = self.tagsCountSpinBox.value()
        description_max = self.descriptionMaxSpinBox.value()

        # Get fresh prompts from CURRENT PRESET ONLY - never from config
        preset = self.presets[self.current_preset]
        raw_prompts = {
            'base_prompt': preset.get('base_prompt', ''),
            'default_prompt': preset.get('default_prompt', ''),
            'custom_prompt': preset.get('custom_prompt', ''),
            'negative_prompt': preset.get('negative_prompt', ''),
            'exclude_prompt': preset.get('exclude_prompt', ''),
            'mandatory_prompt': preset.get('mandatory_prompt', '')
        }

        # Process prompts with current settings
        def process_prompt_with_settings(prompt_text):
            if not prompt_text:
                return prompt_text
            processed = prompt_text
            
            # Replace placeholders with current settings
            processed = processed.replace("TITLE_LENGTH_PLACEHOLDER", f"{title_min}-{title_max}")
            processed = processed.replace("KEYWORDS_COUNT_PLACEHOLDER", str(tags_count))
            processed = processed.replace("DESCRIPTION_MAX_PLACEHOLDER", str(description_max))
            
            return processed

        # Temporarily disconnect signals to avoid recursion
        self.titleMinSpinBox.valueChanged.disconnect()
        self.titleMaxSpinBox.valueChanged.disconnect()
        self.tagsCountSpinBox.valueChanged.disconnect()
        self.descriptionMaxSpinBox.valueChanged.disconnect()

        try:
            # Load fresh prompts from preset and apply current settings
            self.basePromptEdit.setPlainText(process_prompt_with_settings(raw_prompts['base_prompt']))
            self.defaultPromptEdit.setPlainText(process_prompt_with_settings(raw_prompts['default_prompt']))
            self.customPromptEdit.setPlainText(process_prompt_with_settings(raw_prompts['custom_prompt']))
            self.negativePromptEdit.setPlainText(process_prompt_with_settings(raw_prompts['negative_prompt']))
            self.excludePromptEdit.setPlainText(process_prompt_with_settings(raw_prompts['exclude_prompt']))
            # Process mandatory prompt with settings too
            self.mandatoryPromptEdit.setPlainText(process_prompt_with_settings(raw_prompts['mandatory_prompt']))
            
        finally:
            # Reconnect signals
            self.titleMinSpinBox.valueChanged.connect(self.on_settings_changed)
            self.titleMaxSpinBox.valueChanged.connect(self.on_settings_changed)
            self.tagsCountSpinBox.valueChanged.connect(self.on_settings_changed)
            self.descriptionMaxSpinBox.valueChanged.connect(self.on_settings_changed)

    def on_prompt_text_changed(self):
        """Auto-save when any prompt text changes - SAVE TO PRESET, then update config"""
        # Save current UI values back to preset immediately (but only the raw text without placeholders)
        if self.current_preset and self.current_preset in self.presets:
            # Get current raw text from UI and save back to preset
            current_prompts = {
                'base_prompt': self.basePromptEdit.toPlainText().strip(),
                'default_prompt': self.defaultPromptEdit.toPlainText().strip(),
                'custom_prompt': self.customPromptEdit.toPlainText().strip(),
                'negative_prompt': self.negativePromptEdit.toPlainText().strip(),
                'exclude_prompt': self.excludePromptEdit.toPlainText().strip()
            }
            
            # Convert back to placeholder format before saving to preset
            title_min = self.titleMinSpinBox.value()
            title_max = self.titleMaxSpinBox.value()
            tags_count = self.tagsCountSpinBox.value()
            description_max = self.descriptionMaxSpinBox.value()
            
            def convert_to_placeholder_format(prompt_text):
                """Convert processed text back to placeholder format for storage"""
                if not prompt_text:
                    return prompt_text
                
                converted = prompt_text
                # Replace current values back to placeholders
                converted = converted.replace(f"{title_min}-{title_max}", "TITLE_LENGTH_PLACEHOLDER")
                converted = converted.replace(str(tags_count), "KEYWORDS_COUNT_PLACEHOLDER")
                converted = converted.replace(str(description_max), "DESCRIPTION_MAX_PLACEHOLDER")
                
                return converted
            
            # Save to preset in placeholder format
            for key, value in current_prompts.items():
                self.presets[self.current_preset][key] = convert_to_placeholder_format(value)
            
            self.save_presets()  # Auto-save presets file
            self.auto_save_to_config()  # Auto-save to main config (config follows preset)

    def load_prompts(self):
        """Load current prompts from PRESET ONLY - never from config"""
        print(f"[DEBUG] Loading prompts for preset: {self.current_preset}")
        
        # DO NOT reload config - preset is the source of truth
        # self.config_manager.load_config()  # REMOVED - this was causing the issue
        
        # Load the active preset - PRESET IS THE ONLY SOURCE
        if self.current_preset and self.current_preset in self.presets:
            print(f"[DEBUG] Loading preset data for: {self.current_preset}")
            self.load_preset_data(self.current_preset)
        else:
            # Fallback to preset_1 if no active preset
            print(f"[DEBUG] Fallback to preset_1, current was: {self.current_preset}")
            self.current_preset = 'preset_1'
            if 'preset_1' in self.presets:
                self.load_preset_data(self.current_preset)
            else:
                print(f"[ERROR] preset_1 not found in presets!")
                return
        
        # Force update config.json with preset data immediately (preset -> config)
        self.auto_save_to_config()
        
        # Store original prompts for cancel functionality FROM UI (after preset load)
        self.original_prompts = {
            'base_prompt': self.basePromptEdit.toPlainText().strip(),
            'default_prompt': self.defaultPromptEdit.toPlainText().strip(),
            'custom_prompt': self.customPromptEdit.toPlainText().strip(),
            'negative_prompt': self.negativePromptEdit.toPlainText().strip(),
            'exclude_prompt': self.excludePromptEdit.toPlainText().strip(),
            'mandatory_prompt': self.mandatoryPromptEdit.toPlainText().strip()
        }
        
        print(f"[DEBUG] Loaded prompts - base_prompt length: {len(self.original_prompts['base_prompt'])}")
        print(f"[DEBUG] Loaded prompts - default_prompt length: {len(self.original_prompts['default_prompt'])}")
        
        # Update button styles to show active preset
        self.update_preset_button_styles()

    def load_preset_data(self, preset_key: str):
        """Load preset data into UI - PRESET IS THE ONLY SOURCE"""
        if preset_key not in self.presets:
            print(f"[ERROR] Preset {preset_key} not found in presets")
            return
        
        preset = self.presets[preset_key]
        print(f"[DEBUG] Loading preset {preset_key}")
        print(f"[DEBUG] Preset base_prompt: {preset.get('base_prompt', '')[:100]}...")
        print(f"[DEBUG] Preset default_prompt: {preset.get('default_prompt', '')[:100]}...")
        
        # Set loading flag to prevent auto-save during preset loading
        self.loading_preset = True
        
        # Temporarily disconnect signals
        self.titleMinSpinBox.valueChanged.disconnect()
        self.titleMaxSpinBox.valueChanged.disconnect()
        self.tagsCountSpinBox.valueChanged.disconnect()
        self.descriptionMaxSpinBox.valueChanged.disconnect()
        
        try:
            # Load settings from preset
            settings = preset.get('settings', {})
            print(f"[DEBUG] Loading settings: {settings}")
            self.titleMinSpinBox.setValue(settings.get('title_min_length', 0))
            self.titleMaxSpinBox.setValue(settings.get('title_max_length', 0))
            self.tagsCountSpinBox.setValue(settings.get('tags_count', 0))
            self.descriptionMaxSpinBox.setValue(settings.get('description_max_length', 0))
            
            # Load prompts and process placeholders
            title_min = settings.get('title_min_length', 0)
            title_max = settings.get('title_max_length', 0)
            tags_count = settings.get('tags_count', 0)
            description_max = settings.get('description_max_length', 0)
            
            def process_prompt_with_settings(prompt_text):
                if not prompt_text:
                    return prompt_text
                processed = prompt_text
                processed = processed.replace("TITLE_LENGTH_PLACEHOLDER", f"{title_min}-{title_max}")
                processed = processed.replace("KEYWORDS_COUNT_PLACEHOLDER", str(tags_count))
                processed = processed.replace("DESCRIPTION_MAX_PLACEHOLDER", str(description_max))
                return processed
            
            # Load ALL prompts from preset (including negative, custom, exclude)
            base_prompt_processed = process_prompt_with_settings(preset.get('base_prompt', ''))
            default_prompt_processed = process_prompt_with_settings(preset.get('default_prompt', ''))
            custom_prompt_processed = process_prompt_with_settings(preset.get('custom_prompt', ''))
            negative_prompt_processed = process_prompt_with_settings(preset.get('negative_prompt', ''))
            exclude_prompt_processed = process_prompt_with_settings(preset.get('exclude_prompt', ''))
            
            # Mandatory prompt from preset ONLY - PRESET IS THE ONLY SOURCE
            mandatory_prompt = preset.get('mandatory_prompt', '')
            
            # Process mandatory prompt with settings too
            mandatory_prompt_processed = process_prompt_with_settings(mandatory_prompt)
            
            print(f"[DEBUG] Setting base_prompt to UI: {base_prompt_processed[:100]}...")
            print(f"[DEBUG] Setting default_prompt to UI: {default_prompt_processed[:100]}...")
            print(f"[DEBUG] Setting custom_prompt to UI: {custom_prompt_processed[:50]}...")
            print(f"[DEBUG] Setting negative_prompt to UI: {negative_prompt_processed[:50]}...")
            print(f"[DEBUG] Setting exclude_prompt to UI: {exclude_prompt_processed[:50]}...")
            print(f"[DEBUG] Setting mandatory_prompt to UI: {mandatory_prompt_processed[:100]}...")
            
            # Set all prompts from preset
            self.basePromptEdit.setPlainText(base_prompt_processed)
            self.defaultPromptEdit.setPlainText(default_prompt_processed)
            self.customPromptEdit.setPlainText(custom_prompt_processed)
            self.negativePromptEdit.setPlainText(negative_prompt_processed)
            self.excludePromptEdit.setPlainText(exclude_prompt_processed)
            
            # Set processed mandatory prompt
            self.mandatoryPromptEdit.setPlainText(mandatory_prompt_processed)
            
        finally:
            # Reconnect signals
            self.titleMinSpinBox.valueChanged.connect(self.on_settings_changed)
            self.titleMaxSpinBox.valueChanged.connect(self.on_settings_changed)
            self.tagsCountSpinBox.valueChanged.connect(self.on_settings_changed)
            self.descriptionMaxSpinBox.valueChanged.connect(self.on_settings_changed)
            
            # Clear loading flag
            self.loading_preset = False

    def select_preset(self, preset_key: str):
        """Select and load a preset"""
        if preset_key not in self.presets:
            return
        
        # Save current UI prompts back to current preset BEFORE switching (with placeholder conversion)
        if self.current_preset and self.current_preset in self.presets:
            self.save_current_ui_to_preset(self.current_preset)
            self.save_presets()  # Save presets file when switching
        
        # Switch to new preset
        self.current_preset = preset_key
        self.load_preset_data(preset_key)
        self.update_preset_button_styles()
        
        # Auto-save current preset to config.json immediately
        self.auto_save_to_config()

    def save_current_ui_to_preset(self, preset_key: str):
        """Save current UI values back to preset with placeholder conversion"""
        if preset_key not in self.presets:
            return
        
        # Get current values from UI
        current_ui_values = {
            'base_prompt': self.basePromptEdit.toPlainText().strip(),
            'default_prompt': self.defaultPromptEdit.toPlainText().strip(),
            'custom_prompt': self.customPromptEdit.toPlainText().strip(),
            'negative_prompt': self.negativePromptEdit.toPlainText().strip(),
            'exclude_prompt': self.excludePromptEdit.toPlainText().strip()
            # DON'T save mandatory_prompt - it should remain read-only
        }
        
        current_settings = {
            'title_min_length': self.titleMinSpinBox.value(),
            'title_max_length': self.titleMaxSpinBox.value(),
            'tags_count': self.tagsCountSpinBox.value(),
            'description_max_length': self.descriptionMaxSpinBox.value()
        }
        
        # Convert processed UI values back to placeholder format for preset storage
        def convert_to_placeholder_format(prompt_text):
            """Convert processed text back to placeholder format for storage"""
            if not prompt_text:
                return prompt_text
            
            title_min = current_settings['title_min_length']
            title_max = current_settings['title_max_length']
            tags_count = current_settings['tags_count']
            description_max = current_settings['description_max_length']
            
            converted = prompt_text
            # Replace current values back to placeholders
            converted = converted.replace(f"{title_min}-{title_max}", "TITLE_LENGTH_PLACEHOLDER")
            converted = converted.replace(str(tags_count), "KEYWORDS_COUNT_PLACEHOLDER")
            converted = converted.replace(str(description_max), "DESCRIPTION_MAX_PLACEHOLDER")
            
            return converted
        
        # Convert and save to preset in placeholder format
        for key, value in current_ui_values.items():
            self.presets[preset_key][key] = convert_to_placeholder_format(value)
        
        # Update preset settings
        self.presets[preset_key]['settings'] = current_settings
        
        print(f"[DEBUG] Saved UI values to preset {preset_key} with placeholders preserved")

    def reset_to_default(self):
        """Clear all prompts and reset settings to 0 in current preset"""
        reply = QMessageBox.question(
            self,
            "Clear Preset",
            f"Yakin mau hapus semua prompt dan reset settings di {self.presets.get(self.current_preset, {}).get('name', 'preset ini')}?\n\nSemua prompt akan dikosongkan dan settings direset ke 0 (kecuali mandatory prompt).",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all editable prompt fields
            self.basePromptEdit.clear()
            self.defaultPromptEdit.clear()
            self.customPromptEdit.clear()
            self.negativePromptEdit.clear()
            self.excludePromptEdit.clear()
            # Don't clear mandatory prompt as it's read-only and essential
            
            # Reset all settings to 0
            self.titleMinSpinBox.setValue(0)
            self.titleMaxSpinBox.setValue(0)
            self.tagsCountSpinBox.setValue(0)
            self.descriptionMaxSpinBox.setValue(0)

    def preview_prompt(self):
        """Show preview of final prompt that will be sent with dynamic settings"""
        base_prompt = self.basePromptEdit.toPlainText().strip()
        default_prompt = self.defaultPromptEdit.toPlainText().strip()
        custom_prompt = self.customPromptEdit.toPlainText().strip()
        negative_prompt = self.negativePromptEdit.toPlainText().strip()
        exclude_prompt = self.excludePromptEdit.toPlainText().strip()
        mandatory_prompt = self.mandatoryPromptEdit.toPlainText().strip()
        
        # Get current settings values
        title_min = self.titleMinSpinBox.value()
        title_max = self.titleMaxSpinBox.value()
        tags_count = self.tagsCountSpinBox.value()
        description_max = self.descriptionMaxSpinBox.value()
        
        # Function to replace dynamic placeholders in prompts
        def process_prompt(prompt_text):
            """Replace dynamic placeholders with current settings"""
            processed = prompt_text
            
            # Replace placeholders with current settings
            processed = processed.replace("TITLE_LENGTH_PLACEHOLDER", f"{title_min}-{title_max}")
            processed = processed.replace("KEYWORDS_COUNT_PLACEHOLDER", str(tags_count))
            processed = processed.replace("DESCRIPTION_MAX_PLACEHOLDER", str(description_max))
            
            return processed
        
        # Build final prompt with processed content
        final_prompt_parts = []
        
        if base_prompt:
            final_prompt_parts.append(f"SYSTEM: {process_prompt(base_prompt)}")
        
        if default_prompt:
            final_prompt_parts.append(f"MAIN: {process_prompt(default_prompt)}")
        
        if custom_prompt:
            final_prompt_parts.append(f"CUSTOM: {process_prompt(custom_prompt)}")
        
        if negative_prompt:
            final_prompt_parts.append(f"AVOID: {process_prompt(negative_prompt)}")
        
        if exclude_prompt:
            final_prompt_parts.append(f"EXCLUDE: {process_prompt(exclude_prompt)}")
        
        if mandatory_prompt:
            final_prompt_parts.append(f"FORMAT: {process_prompt(mandatory_prompt)}")
        
        final_prompt = "\n\n".join(final_prompt_parts)
        
        # Add settings summary at the top
        settings_summary = f"CURRENT SETTINGS:\n- Title Length: {title_min}-{title_max} characters\n- Keywords Count: {tags_count} keywords\n- Description Max: {description_max} characters\n\n{'='*50}\n\n"
        final_prompt = settings_summary + final_prompt
        
        # Show preview dialog
        try:
            preview_dialog = PromptPreviewWindow(self, final_prompt)
            preview_dialog.exec()
            
        except Exception as e:
            print(f"[ERROR] Failed to show preview dialog: {e}")
            # Fallback to simple message box
            QMessageBox.information(
                self, 
                "Preview Prompt", 
                f"Final Prompt:\n\n{final_prompt}"
            )

    def save_changes(self):
        """Save all changes without closing the window - now just for user satisfaction"""
        try:
            # Save current UI to current preset with placeholder conversion
            if self.current_preset:
                self.save_current_ui_to_preset(self.current_preset)
            
            self.save_presets()
            self.auto_save_to_config()
            
            # Show brief success message for user satisfaction
            QMessageBox.information(
                self,
                "Tersimpan",
                "Semua perubahan telah disimpan!"
            )
            
        except Exception as e:
            print(f"[ERROR] Failed to save: {e}")
            QMessageBox.critical(self, "Error", f"Gagal simpan perubahan:\n{str(e)}")

    def cancel_changes(self):
        """Close the dialog"""
        self.reject()

    def get_current_prompts(self):
        """Get current prompt values"""
        return {
            'base_prompt': self.basePromptEdit.toPlainText().strip(),
            'default_prompt': self.defaultPromptEdit.toPlainText().strip(),
            'custom_prompt': self.customPromptEdit.toPlainText().strip(),
            'negative_prompt': self.negativePromptEdit.toPlainText().strip(),
            'exclude_prompt': self.excludePromptEdit.toPlainText().strip()
        }
    
    def auto_save_to_config(self):
        """Auto-save current preset data to main config.json - PRESET is the source of truth"""
        if self.current_preset and self.current_preset in self.presets:
            preset = self.presets[self.current_preset]
            
            print(f"[DEBUG] Auto-saving preset {self.current_preset} to config.json")
            
            # Get current settings to process placeholders
            settings = preset.get('settings', {})
            title_min = settings.get('title_min_length', 0)
            title_max = settings.get('title_max_length', 0)
            tags_count = settings.get('tags_count', 0)
            description_max = settings.get('description_max_length', 0)
            
            def process_preset_prompt_for_config(prompt_text):
                """Process preset prompt with placeholders into final config values"""
                if not prompt_text:
                    return prompt_text
                processed = prompt_text
                # Replace placeholders with actual settings values for config
                processed = processed.replace("TITLE_LENGTH_PLACEHOLDER", f"{title_min}-{title_max}")
                processed = processed.replace("KEYWORDS_COUNT_PLACEHOLDER", str(tags_count))
                processed = processed.replace("DESCRIPTION_MAX_PLACEHOLDER", str(description_max))
                return processed
            
            # Update main config with PROCESSED preset data (placeholders replaced with actual values)
            # Include ALL prompts from preset
            new_prompts = {
                'base_prompt': process_preset_prompt_for_config(preset.get('base_prompt', '')),
                'default_prompt': process_preset_prompt_for_config(preset.get('default_prompt', '')),
                'custom_prompt': process_preset_prompt_for_config(preset.get('custom_prompt', '')),
                'negative_prompt': process_preset_prompt_for_config(preset.get('negative_prompt', '')),
                'exclude_prompt': process_preset_prompt_for_config(preset.get('exclude_prompt', '')),
                'mandatory_prompt': process_preset_prompt_for_config(preset.get('mandatory_prompt', ''))
            }
            
            print(f"[DEBUG] Updating config prompts with PROCESSED values: {[(k, len(v)) for k, v in new_prompts.items()]}")
            
            if 'prompts' not in self.config_manager._config['prompting']:
                self.config_manager._config['prompting']['prompts'] = {}
            
            # Update ALL prompts with PROCESSED values from preset - preset is the only source
            for key, value in new_prompts.items():
                self.config_manager._config['prompting']['prompts'][key] = value
            
            # Update settings - PRESET data is the source of truth
            print(f"[DEBUG] Updating config settings with: {settings}")
            self.config_manager.update_prompt_settings(settings)
            
            # Save config
            self.config_manager.save_config()
            print(f"[DEBUG] Config.json updated with PROCESSED preset {self.current_preset} data")


class PromptPreviewWindow(QDialog):
    """Preview window for final prompt with programmatic UI"""
    
    def __init__(self, parent=None, prompt_text=""):
        super().__init__(parent)
        self.prompt_text = prompt_text
        self.create_ui()
        self.setup_connections()
        
        # Set window properties
        self.setModal(True)
        self.resize(700, 500)
        center_window(self)
    
    def create_ui(self):
        """Create UI elements programmatically"""
        # Set window title and icon
        self.setWindowTitle("Preview Prompt")
        self.setWindowIcon(qta.icon('fa6s.file-lines'))
        self.setStyleSheet("QDialog { border-radius: 8px; }")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Title layout
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        # Title icon
        self.titleIconLabel = QLabel()
        self.titleIconLabel.setMinimumSize(22, 22)
        self.titleIconLabel.setMaximumSize(22, 22)
        self.titleIconLabel.setAlignment(Qt.AlignCenter)
        doc_icon = qta.icon('fa6s.file-lines', color='#2E7D32')
        self.titleIconLabel.setPixmap(doc_icon.pixmap(18, 18))
        title_layout.addWidget(self.titleIconLabel)
        
        # Title label
        self.titleLabel = QLabel("Preview Prompt Final")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        title_layout.addWidget(self.titleLabel)
        
        title_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        main_layout.addLayout(title_layout)
        
        # Preview text edit
        self.previewTextEdit = QTextEdit()
        self.previewTextEdit.setReadOnly(True)
        self.previewTextEdit.setFrameShape(QFrame.NoFrame)
        self.previewTextEdit.setStyleSheet("""
            QTextEdit#previewTextEdit {
                font-family: 'Consolas', 'Courier New', 'Monaco', monospace;
                font-size: 10pt;
                line-height: 1.4;
                border: 1px solid rgba(37, 211, 102, 0.4);
                border-radius: 6px;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }

            QTextEdit#previewTextEdit:focus {
                border: 1px solid rgba(37, 211, 102, 0.7);
                outline: none;
            }

            QTextEdit#previewTextEdit QScrollBar:vertical {
                background-color: rgba(0, 0, 0, 0.1);
                border: none;
                width: 12px;
                margin: 0;
                border-radius: 6px;
            }

            QTextEdit#previewTextEdit QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }

            QTextEdit#previewTextEdit QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }

            QTextEdit#previewTextEdit QScrollBar::handle:vertical:pressed {
                background-color: rgba(0, 0, 0, 0.7);
            }

            QTextEdit#previewTextEdit QScrollBar::add-line:vertical,
            QTextEdit#previewTextEdit QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: none;
            }

            QTextEdit#previewTextEdit QScrollBar::add-page:vertical,
            QTextEdit#previewTextEdit QScrollBar::sub-page:vertical {
                background: none;
            }

            QTextEdit#previewTextEdit QScrollBar:horizontal {
                background-color: rgba(0, 0, 0, 0.1);
                border: none;
                height: 12px;
                margin: 0;
                border-radius: 6px;
            }

            QTextEdit#previewTextEdit QScrollBar::handle:horizontal {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }

            QTextEdit#previewTextEdit QScrollBar::handle:horizontal:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }

            QTextEdit#previewTextEdit QScrollBar::handle:horizontal:pressed {
                background-color: rgba(0, 0, 0, 0.7);
            }

            QTextEdit#previewTextEdit QScrollBar::add-line:horizontal,
            QTextEdit#previewTextEdit QScrollBar::sub-line:horizontal {
                width: 0px;
                border: none;
                background: none;
            }

            QTextEdit#previewTextEdit QScrollBar::add-page:horizontal,
            QTextEdit#previewTextEdit QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.previewTextEdit.setObjectName("previewTextEdit")
        self.previewTextEdit.setPlainText(self.prompt_text)
        main_layout.addWidget(self.previewTextEdit)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.closeButton = QPushButton("Tutup")
        self.closeButton.setIcon(qta.icon('fa6s.xmark', color='#666'))
        self.closeButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(158, 158, 158, 0.1);
                border: 1px solid rgba(158, 158, 158, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(158, 158, 158, 0.2);
                border: 1px solid rgba(158, 158, 158, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(158, 158, 158, 0.3);
                border: 1px solid rgba(158, 158, 158, 0.7);
            }
        """)
        button_layout.addWidget(self.closeButton)
        
        main_layout.addLayout(button_layout)
        
        # Set the main layout
        self.setLayout(main_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.closeButton.clicked.connect(self.accept)
