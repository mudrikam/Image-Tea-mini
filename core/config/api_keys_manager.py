from PySide6.QtWidgets import (QDialog, QMessageBox, QListWidgetItem, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QLineEdit, QListWidget, QGroupBox, 
                             QFrame, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, QThread, Signal, QUrl, QSize
from PySide6.QtGui import QColor, QDesktopServices, QFont
from App.config.config_manager import config_manager
from App.utils.window_utils import center_dialog
import qtawesome as qta

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class ApiTestThread(QThread):
    """Thread for testing API keys without blocking UI"""
    test_completed = Signal(bool, str)  # success, message
    
    def __init__(self, platform, api_key, config_manager):
        super().__init__()
        self.platform = platform
        self.api_key = api_key
        self.config_manager = config_manager
    
    def run(self):
        try:
            if self.platform == "gemini":
                success, message = self.test_gemini_key()
            elif self.platform == "openai":
                success, message = self.test_openai_key()
            else:
                success, message = False, "Platform not supported"
            
            self.test_completed.emit(success, message)
        except Exception as e:
            self.test_completed.emit(False, f"Connection error: {str(e)}")
    
    def test_gemini_key(self):
        """Test Gemini API key"""
        if not GENAI_AVAILABLE:
            return False, "Library Google GenAI belum diinstall.\n\nSilakan install dulu pakai:\npip install google-genai"
        
        try:
            # Get available models from config
            platform_config = self.config_manager.get_platform_config("gemini")
            models = platform_config.get('models', ['gemini-1.5-flash'])
            test_model = models[0]  # Use first available model for testing
            
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=test_model,
                contents=["Test connection"]
            )
            return True, f"API Key kamu berfungsi dengan baik!\n\nTes koneksi berhasil menggunakan model: {test_model}"
        except Exception as e:
            return False, self._parse_gemini_error(str(e))
    
    def test_openai_key(self):
        """Test OpenAI API key"""
        if not OPENAI_AVAILABLE:
            return False, "Library OpenAI belum diinstall.\n\nSilakan install dulu pakai:\npip install openai"
        
        try:
            # Get available models from config
            platform_config = self.config_manager.get_platform_config("openai")
            models = platform_config.get('models', ['gpt-4o-mini'])
            test_model = models[0]  # Use first available model for testing
            
            client = OpenAI(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=test_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Test connection"}
                ]
            )
            return True, f"API Key kamu berfungsi dengan baik!\n\nTes koneksi berhasil menggunakan model: {test_model}"
        except Exception as e:
            return False, self._parse_openai_error(str(e))
    
    def _parse_gemini_error(self, error_msg):
        """Parse Gemini error message into user-friendly format"""
        error_lower = error_msg.lower()
        
        if "invalid api key" in error_lower or "api_key_invalid" in error_lower:
            return "API Key Tidak Valid\n\nAPI Key yang kamu masukkan salah.\nCoba cek lagi dan ulangi."
        elif "quota" in error_lower or "resource_exhausted" in error_lower:
            return "Quota Habis\n\nQuota API kamu sudah habis.\nCoba cek billing atau tunggu reset quota."
        elif "permission" in error_lower or "forbidden" in error_lower:
            return "Akses Ditolak\n\nAPI Key kamu gak punya akses ke layanan ini.\nCoba cek permission API Key kamu."
        elif "not found" in error_lower or "model_not_found" in error_lower:
            return "Model Tidak Ditemukan\n\nModel yang diminta gak tersedia.\nCoba lagi nanti."
        elif "timeout" in error_lower or "deadline" in error_lower:
            return "Koneksi Timeout\n\nPermintaan kamu kelamaan.\nCoba cek koneksi internet dan ulangi."
        elif "network" in error_lower or "connection" in error_lower:
            return "Error Jaringan\n\nGak bisa konek ke API Gemini.\nCoba cek koneksi internet kamu."
        else:
            return f"Tes API Gagal\n\nDetail error:\n{error_msg}"
    
    def _parse_openai_error(self, error_msg):
        """Parse OpenAI error message into user-friendly format"""
        error_lower = error_msg.lower()
        
        if "invalid api key" in error_lower or "unauthorized" in error_lower:
            return "API Key Tidak Valid\n\nAPI Key yang kamu masukkan salah.\nCoba cek lagi dan ulangi."
        elif "quota" in error_lower or "insufficient_quota" in error_lower:
            return "Quota Habis\n\nQuota API kamu sudah habis.\nCoba cek billing atau tambahin kredit ke akun kamu."
        elif "permission" in error_lower or "forbidden" in error_lower:
            return "Akses Ditolak\n\nAPI Key kamu gak punya akses ke layanan ini.\nCoba cek permission API Key kamu."
        elif "rate limit" in error_lower:
            return "Rate Limit Kelebihan\n\nTerlalu banyak request. Tunggu sebentar dulu terus coba lagi."
        elif "model" in error_lower and "not found" in error_lower:
            return "Model Gak Tersedia\n\nModel yang diminta gak tersedia.\nCoba lagi nanti."
        elif "timeout" in error_lower:
            return "Koneksi Timeout\n\nPermintaan kamu kelamaan.\nCoba cek koneksi internet dan ulangi."
        elif "network" in error_lower or "connection" in error_lower:
            return "Error Jaringan\n\nGak bisa konek ke API OpenAI.\nCoba cek koneksi internet kamu."
        else:
            return f"Tes API Gagal\n\nDetail error:\n{error_msg}"

class ApiKeysManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_platform = None
        self.test_thread = None  # Track thread to prevent multiple tests
        self.create_ui()
        self.setup_icons()
        self.setup_connections()
        self.load_platforms()
        
        # Set window properties - ukuran optimal untuk laptop
        self.setModal(True)
        self.resize(750, 650)  # Lebih besar untuk accommodate content
        self.setMinimumSize(700, 600)  # Minimum size untuk laptop kecil
        
        # Center window di layar AFTER all setup is complete
        center_dialog(self)
    
    def create_ui(self):
        """Create UI elements programmatically"""
        # Set window title and icon
        self.setWindowTitle("Kelola API Key")
        self.setWindowIcon(qta.icon('fa6s.key'))
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Title label
        self.titleLabel = QLabel("🔑 Kelola API Key")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        main_layout.addWidget(self.titleLabel)
        
        # Subtitle label
        self.subtitleLabel = QLabel("Atur API Key untuk analisis AI yang lebih powerful dan akurat ✨")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_font.setItalic(True)
        self.subtitleLabel.setFont(subtitle_font)
        self.subtitleLabel.setStyleSheet("""
            QLabel {
                color: rgba(128, 128, 128, 0.8);
                margin-bottom: 5px;
            }
        """)
        self.subtitleLabel.setWordWrap(True)
        main_layout.addWidget(self.subtitleLabel)
        
        # Help section
        help_layout = QHBoxLayout()
        
        self.helpLabel = QLabel("💡 Butuh API Key gratis? Join grup kami untuk dapetin API Key gratis dan tutorial lengkap! Udah 500+ orang yang terbantu.")
        help_font = QFont()
        help_font.setPointSize(9)
        self.helpLabel.setFont(help_font)
        self.helpLabel.setWordWrap(True)
        self.helpLabel.setStyleSheet("""
            QLabel {
                background-color: rgba(37, 211, 102, 0.1);
                border-radius: 6px;
                padding: 8px;
                border-left: 3px solid #25D366;
            }
        """)
        help_layout.addWidget(self.helpLabel)
        
        self.waButton = QPushButton("Join Grup")
        self.waButton.setMinimumSize(120, 40)
        self.waButton.setMaximumSize(120, 40)
        wa_font = QFont()
        wa_font.setBold(True)
        self.waButton.setFont(wa_font)
        self.waButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(37, 211, 102, 0.15);
                border: 1px solid rgba(37, 211, 102, 0.4);
                color: #25D366;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(37, 211, 102, 0.25);
                border: 1px solid rgba(37, 211, 102, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(37, 211, 102, 0.35);
                border: 1px solid rgba(37, 211, 102, 0.8);
            }
        """)
        help_layout.addWidget(self.waButton)
        
        main_layout.addLayout(help_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Platform frame
        self.platformFrame = QFrame()
        self.platformFrame.setStyleSheet("""
            QFrame#platformFrame {
                background-color: rgba(128, 128, 128, 0.05);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.platformFrame.setObjectName("platformFrame")
        platform_layout = QVBoxLayout()
        platform_layout.setContentsMargins(0, 0, 0, 0)
        
        # Platform selection
        platform_select_layout = QHBoxLayout()
        
        self.platformLabel = QLabel("Platform:")
        platform_select_layout.addWidget(self.platformLabel)
        
        self.platformComboBox = QComboBox()
        self.platformComboBox.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid rgba(128, 128, 128, 0.1);
                border-radius: 6px;
                background-color: rgba(128, 128, 128, 0.02);
                font-size: 10pt;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
            QComboBox:focus {
                border: 2px solid rgba(33, 150, 243, 0.6);
                background-color: rgba(128, 128, 128, 0.02);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid rgba(128, 128, 128, 0.1);
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-radius: 6px;
                selection-background-color: rgba(33, 150, 243, 0.2);
            }
        """)
        platform_select_layout.addWidget(self.platformComboBox)
        
        platform_select_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        platform_layout.addLayout(platform_select_layout)
        
        # Key actions layout
        key_actions_layout = QHBoxLayout()
        
        self.keyLineEdit = QLineEdit()
        self.keyLineEdit.setPlaceholderText("Paste API Key kamu di sini...")
        self.keyLineEdit.setEchoMode(QLineEdit.Password)
        self.keyLineEdit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid rgba(128, 128, 128, 0.1);
                border-radius: 6px;
                background-color: rgba(128, 128, 128, 0.02);
                font-size: 10pt;
            }
            QLineEdit:hover {
                border: 1px solid rgba(128, 128, 128, 0.2);
                background-color: rgba(128, 128, 128, 0.02);
            }
            QLineEdit:focus {
                border: 2px solid rgba(76, 175, 80, 0.6);
                background-color: rgba(128, 128, 128, 0.02);
            }
        """)
        key_actions_layout.addWidget(self.keyLineEdit)
        
        self.addKeyButton = QPushButton("Tambah")
        self.addKeyButton.setToolTip("Tambahin API Key baru (otomatis deteksi platform)")
        self.addKeyButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(76, 175, 80, 0.1);
                border: 1px solid rgba(76, 175, 80, 0.3);
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.3);
                border: 1px solid rgba(76, 175, 80, 0.7);
            }
        """)
        key_actions_layout.addWidget(self.addKeyButton)
        
        self.testKeyButton = QPushButton("Tes")
        self.testKeyButton.setToolTip("Tes koneksi API Key yang dipilih")
        self.testKeyButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(156, 39, 176, 0.1);
                border: 1px solid rgba(156, 39, 176, 0.3);
                font-weight: 500;
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
        key_actions_layout.addWidget(self.testKeyButton)
        
        self.removeKeyButton = QPushButton("Hapus")
        self.removeKeyButton.setToolTip("Hapus API Key yang dipilih")
        self.removeKeyButton.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: rgba(244, 67, 54, 0.1);
                border: 1px solid rgba(244, 67, 54, 0.3);
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(244, 67, 54, 0.3);
                border: 1px solid rgba(244, 67, 54, 0.7);
            }
        """)
        key_actions_layout.addWidget(self.removeKeyButton)
        
        platform_layout.addLayout(key_actions_layout)
        
        self.platformFrame.setLayout(platform_layout)
        main_layout.addWidget(self.platformFrame)
        
        # Keys group box
        self.keysGroupBox = QGroupBox("API Keys")
        keys_group_font = QFont()
        keys_group_font.setBold(True)
        self.keysGroupBox.setFont(keys_group_font)
        self.keysGroupBox.setStyleSheet("""
            QGroupBox#keysGroupBox {
                border: none;
                font-weight: bold;
                padding-top: 10px;
                border-radius: 8px;
                background-color: rgba(128, 128, 128, 0.05);
            }
            QGroupBox#keysGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self.keysGroupBox.setObjectName("keysGroupBox")
        
        keys_layout = QVBoxLayout()
        keys_layout.setContentsMargins(0, 0, 0, 0)
        
        self.keysListWidget = QListWidget()
        self.keysListWidget.setMinimumHeight(150)
        self.keysListWidget.setFrameShape(QFrame.NoFrame)
        self.keysListWidget.setStyleSheet("""
            QListWidget {
                border-radius: 6px;
                padding: 5px;
                outline: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0;
                border-radius: 4px;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: rgba(76, 175, 80, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(76, 175, 80, 0.3);
            }
            QListWidget::item:selected:active {
                background-color: rgba(76, 175, 80, 0.4);
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """)
        keys_layout.addWidget(self.keysListWidget)
        
        self.keysGroupBox.setLayout(keys_layout)
        main_layout.addWidget(self.keysGroupBox)
        
        # Platform info label
        self.platformInfoLabel = QLabel("Info platform bakal ditampilkan di sini...")
        self.platformInfoLabel.setWordWrap(True)
        self.platformInfoLabel.setOpenExternalLinks(True)
        self.platformInfoLabel.setFrameShape(QFrame.NoFrame)
        self.platformInfoLabel.setStyleSheet("""
            QLabel#platformInfoLabel {
                background-color: rgba(128, 128, 128, 0.05);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.platformInfoLabel.setObjectName("platformInfoLabel")
        main_layout.addWidget(self.platformInfoLabel)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.saveButton = QPushButton("Simpan")
        self.saveButton.setToolTip("Simpan perubahan dan tutup")
        self.saveButton.setDefault(True)
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
        """Setup QtAwesome icons for buttons and UI elements"""
        # Button icons dengan warna - consistent with PromptManager style
        self.addKeyButton.setIcon(qta.icon('fa6s.plus', color='#4CAF50'))
        self.removeKeyButton.setIcon(qta.icon('fa6s.trash', color='#F44336'))
        self.testKeyButton.setIcon(qta.icon('fa6s.flask', color='#9C27B0'))
        self.saveButton.setIcon(qta.icon('fa6s.check', color='#4CAF50'))
        self.cancelButton.setIcon(qta.icon('fa6s.xmark', color='#F44336'))
        self.waButton.setIcon(qta.icon('fa6b.whatsapp', color="#FFFFFF"))
        
        # Set window icon - consistent with PromptManager
        self.setWindowIcon(qta.icon('fa6s.key', color='#FF9800'))
    
    def setup_connections(self):
        """Setup signal connections"""
        self.platformComboBox.currentIndexChanged.connect(self.on_platform_changed)
        self.addKeyButton.clicked.connect(self.add_api_key)
        self.removeKeyButton.clicked.connect(self.remove_api_key)
        self.testKeyButton.clicked.connect(self.test_api_key)
        self.saveButton.clicked.connect(self.save_changes)
        self.cancelButton.clicked.connect(self.reject)
        self.keyLineEdit.returnPressed.connect(self.add_api_key)
        self.keysListWidget.itemSelectionChanged.connect(self.on_key_selection_changed)
        
        # WhatsApp button connection
        self.waButton.clicked.connect(self.open_whatsapp_group)
    
    def open_whatsapp_group(self):
        """Open WhatsApp group link"""
        try:
            wa_link = self.config_manager.app_config.get('contact', {}).get('whatsapp', '')
            if wa_link:
                QDesktopServices.openUrl(QUrl(wa_link))
            else:
                QMessageBox.information(
                    self, 
                    "Grup WhatsApp", 
                    "Link grup WhatsApp gak tersedia di konfigurasi."
                )
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Error", 
                f"Gagal buka grup WhatsApp:\n{str(e)}"
            )
    
    def update_platform_info(self):
        """Update platform information display"""
        if not self.current_platform:
            return
        
        platform_config = self.config_manager.get_platform_config(self.current_platform)
        api_keys = self.config_manager.get_api_keys(self.current_platform)
        
        # Get platform info from config
        platform_name = platform_config.get('name', 'Unknown Platform')
        models = platform_config.get('models', [])
        default_model = platform_config.get('default_model', models[0] if models else 'N/A')
        supported_formats = platform_config.get('supported_formats', {})
        
        if self.current_platform == "gemini":
            # Build supported formats string
            image_formats = ', '.join(supported_formats.get('images', []))
            video_formats = ', '.join(supported_formats.get('videos', []))
            
            info_text = f"""
            <div style="padding: 4px;">
            <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1976D2;">🤖 {platform_name}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>💎 Model Unggulan:</b> {default_model}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎯 Models Tersedia:</b> {', '.join(models)}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎁 Tier Gratis:</b> 15 request/menit, 1.500 request/hari</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>📸 Format Gambar:</b> {image_formats}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎬 Format Video:</b> {video_formats}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🔑 API Key Aktif:</b> {len(api_keys)} API Key</p>
            <p style="margin: 4px 0; font-size: 10px; color: #666;"><i>💡 Butuh API Key gratis? Grup kami sering share API Key dan tips!</i></p>
            </div>
            """
        elif self.current_platform == "openai":
            # Build supported formats string
            image_formats = ', '.join(supported_formats.get('images', []))
            video_support = "Tidak didukung" if not supported_formats.get('videos') else ', '.join(supported_formats.get('videos', []))
            
            info_text = f"""
            <div style="padding: 4px;">
            <p style="margin: 0; font-size: 13px; font-weight: bold; color: #10A37F;">🧠 {platform_name}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>💎 Model Unggulan:</b> {default_model}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎯 Models Tersedia:</b> {', '.join(models)}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎁 Tier Gratis:</b> Kredit $5 untuk akun baru (3 bulan)</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>📸 Format Gambar:</b> {image_formats}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎬 Format Video:</b> {video_support}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🔑 API Key Aktif:</b> {len(api_keys)} API Key</p>
            <p style="margin: 4px 0; font-size: 10px; color: #666;"><i>💡 Join grup untuk tips mengoptimalkan penggunaan kredit!</i></p>
            </div>
            """
        else:
            # Generic platform info from config
            image_formats = ', '.join(supported_formats.get('images', []))
            video_formats = ', '.join(supported_formats.get('videos', [])) if supported_formats.get('videos') else "Tidak didukung"
            
            info_text = f"""
            <div style="padding: 4px;">
            <p style="margin: 0; font-size: 13px; font-weight: bold; color: #7C4DFF;">⚡ {platform_name}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>💎 Model Default:</b> {default_model}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎯 Models Tersedia:</b> {', '.join(models)}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>📸 Format Gambar:</b> {image_formats}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🎬 Format Video:</b> {video_formats}</p>
            <p style="margin: 4px 0; font-size: 11px;"><b>🔑 API Key Aktif:</b> {len(api_keys)} API Key</p>
            </div>
            """
        
        self.platformInfoLabel.setText(info_text)
    
    def get_status_color(self, status):
        """Get color for API key status"""
        colors = {
            "active": QColor(0, 128, 0),        # Green text
            "busy": QColor(255, 165, 0),        # Orange text
            "quota_exceeded": QColor(128, 128, 128),  # Gray text
            "invalid": QColor(255, 0, 0),       # Red text
            "unknown": None                      # No color (use default theme)
        }
        return colors.get(status, None)
    
    def load_api_keys(self):
        """Load API keys for current platform"""
        if not self.current_platform:
            return
            
        self.keysListWidget.clear()
        api_keys = self.config_manager.get_api_keys(self.current_platform)
        key_status = self.config_manager.get_api_key_status(self.current_platform)
        
        for i, key in enumerate(api_keys):
            # Mask the key for display
            masked_key = self.mask_api_key(key)
            
            # Add status icon based on key status
            status = key_status.get(key, "unknown")
            status_icon = self.get_status_icon(status)
            
            item = QListWidgetItem()
            item.setText(masked_key)
            item.setIcon(status_icon)
            item.setData(Qt.UserRole, key)  # Store full key in user data
            
            # NO FOREGROUND COLOR SETTING - let PySide6 handle it vanilla
            
            self.keysListWidget.addItem(item)
    
    def get_status_icon(self, status):
        """Get QtAwesome icon for API key status dengan warna"""
        icons = {
            "active": qta.icon('fa6s.circle-check', color='#4CAF50'),
            "busy": qta.icon('fa6s.clock', color='#FF9800'),
            "quota_exceeded": qta.icon('fa6s.ban', color='#9E9E9E'),
            "invalid": qta.icon('fa6s.circle-xmark', color='#F44336'),
            "unknown": qta.icon('fa6s.circle-question', color='#607D8B')
        }
        return icons.get(status, qta.icon('fa6s.circle-question', color='#607D8B'))
    
    def on_key_selection_changed(self):
        """Handle API key selection change"""
        current_item = self.keysListWidget.currentItem()
        self.testKeyButton.setEnabled(current_item is not None)
        self.removeKeyButton.setEnabled(current_item is not None)
    
    def mask_api_key(self, key):
        """Mask API key for display"""
        if len(key) <= 12:
            return "*" * len(key)
        return key[:8] + "*" * (len(key) - 12) + key[-4:]
    
    def load_platforms(self):
        """Load available platforms into combo box"""
        platforms = self.config_manager.get_available_platforms()
        self.platformComboBox.clear()
        
        for platform_key, platform_info in platforms.items():
            self.platformComboBox.addItem(platform_info['name'], platform_key)
        
        # Set current platform and load initial data
        current_platform = self.config_manager.current_platform
        for i in range(self.platformComboBox.count()):
            if self.platformComboBox.itemData(i) == current_platform:
                self.platformComboBox.setCurrentIndex(i)
                self.current_platform = current_platform
                self.load_api_keys()
                self.update_platform_info()
                break
    
    def on_platform_changed(self):
        """Handle platform selection change"""
        platform_key = self.platformComboBox.currentData()
        if platform_key:
            self.current_platform = platform_key
            self.load_api_keys()
            self.update_platform_info()
    
    def test_api_key(self):
        """Test selected API key"""
        # Prevent multiple simultaneous tests
        if self.test_thread and self.test_thread.isRunning():
            return
            
        current_item = self.keysListWidget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Gak Ada Yang Dipilih", "Pilih dulu API Key yang mau dites.")
            return
        
        full_key = current_item.data(Qt.UserRole)
        
        # Disable test button during testing
        self.testKeyButton.setEnabled(False)
        self.testKeyButton.setText("Testing...")
        self.testKeyButton.setIcon(qta.icon('fa6s.spinner', color='#FF9800', animation=qta.Spin(self.testKeyButton)))
        
        # Start API test in separate thread with config manager
        self.test_thread = ApiTestThread(self.current_platform, full_key, self.config_manager)
        self.test_thread.test_completed.connect(self.on_test_completed)
        self.test_thread.start()
    
    def on_test_completed(self, success, message):
        """Handle API test completion"""
        # Clean up thread
        if self.test_thread:
            self.test_thread.deleteLater()
            self.test_thread = None
        
        # Re-enable test button
        self.testKeyButton.setEnabled(True)
        self.testKeyButton.setText("Tes")
        self.testKeyButton.setIcon(qta.icon('fa6s.flask', color='#9C27B0'))
        
        # Update API key status
        current_item = self.keysListWidget.currentItem()
        if current_item:
            full_key = current_item.data(Qt.UserRole)
            if success:
                status = "active"
            else:
                if "quota" in message.lower() or "kuota" in message.lower():
                    status = "quota_exceeded"
                elif "invalid" in message.lower() or "tidak valid" in message.lower() or "salah" in message.lower():
                    status = "invalid"
                else:
                    status = "unknown"
            
            # Update status 
            self.config_manager.set_api_key_status(self.current_platform, full_key, status)
            
            # Update the display with new status - ONLY ICON, NO COLOR
            status_icon = self.get_status_icon(status)
            current_item.setIcon(status_icon)
            
            # NEVER SET FOREGROUND COLOR - let PySide6 handle it vanilla
        
        # Show result message
        if success:
            QMessageBox.information(self, "Tes Berhasil", message)
        else:
            QMessageBox.warning(self, "Tes Gagal", message)
    
    def save_changes(self):
        """Save all changes and close dialog"""
        try:
            # Configuration is auto-saved, just close
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal simpan perubahan:\n{str(e)}")
    
    def add_api_key(self):
        """Add new API key"""
        new_key = self.keyLineEdit.text().strip()
        if not new_key:
            QMessageBox.warning(self, "Peringatan", "Masukin dulu API Key nya")
            return
        
        # Auto-detect platform based on API key format
        detected_platform = self.detect_platform_from_key(new_key)
        
        if not detected_platform:
            msg = QMessageBox(self)
            msg.setWindowTitle("Format API Key Tidak Dikenali")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Hmm, format API Key ini belum kami kenali 🤔")
            msg.setDetailedText(
                "Format yang kami dukung saat ini:\n\n"
                "🟢 Gemini: AIzaXXXXXXXX (dimulai dengan 'AIza')\n"
                "🔵 OpenAI: sk-XXXXXXXX (dimulai dengan 'sk-')\n\n"
                "📚 Belum punya API Key atau butuh bantuan?\n"
                "Grup WhatsApp kami siap membantu! Kamu bisa:\n"
                "• Dapat API Key gratis dari member lain\n"
                "• Belajar cara daftar yang benar\n"
                "• Share pengalaman dengan sesama pengguna\n"
                "• Dapat tips mengoptimalkan penggunaan API"
            )
            
            # Add community button to message box
            wa_button = msg.addButton("🚀 Join Grup", QMessageBox.ActionRole)
            skip_button = msg.addButton("Lewati", QMessageBox.RejectRole)
            
            msg.setDefaultButton(wa_button)
            
            result = msg.exec()
            if msg.clickedButton() == wa_button:
                self.open_whatsapp_group()
            return
        
        # Check if key already exists in detected platform
        existing_keys = self.config_manager.get_api_keys(detected_platform)
        if new_key in existing_keys:
            QMessageBox.warning(self, "API Key Sudah Ada", f"API Key ini sudah terdaftar di platform {detected_platform.upper()} 🔄")
            return
        
        # Add key to detected platform
        self.config_manager.add_api_key(detected_platform, new_key)
        
        # Switch to the detected platform if different from current
        if detected_platform != self.current_platform:
            self.switch_to_platform(detected_platform)
        else:
            # Just reload if same platform
            self.load_api_keys()
            self.update_platform_info()
        
        # Clear input
        self.keyLineEdit.clear()

    def detect_platform_from_key(self, api_key):
        """Detect platform based on API key format using config"""
        if not api_key:
            return None
        
        # Get all available platforms from config
        platforms = self.config_manager.get_available_platforms()
        
        for platform_key, platform_config in platforms.items():
            # Check known patterns for each platform
            if platform_key == "gemini":
                # Gemini API keys typically start with 'AIza' and are ~39 characters
                if api_key.startswith("AIza") and len(api_key) >= 35:
                    return platform_key
            elif platform_key == "openai":
                # OpenAI API keys typically start with 'sk-' and are longer
                if api_key.startswith("sk-") and len(api_key) >= 40:
                    return platform_key
            # Add more platform detection patterns here as needed
        
        return None
    
    def switch_to_platform(self, platform):
        """Switch to specified platform"""
        platforms = self.config_manager.get_available_platforms()
        
        for i in range(self.platformComboBox.count()):
            if self.platformComboBox.itemData(i) == platform:
                self.platformComboBox.setCurrentIndex(i)
                self.current_platform = platform
                self.load_api_keys()
                self.update_platform_info()
                break
    
    def remove_api_key(self):
        """Remove selected API key"""
        current_item = self.keysListWidget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Peringatan", "Pilih dulu API Key yang mau dihapus")
            return
        
        full_key = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, 
            "Konfirmasi Hapus", 
            "Yakin mau hapus API Key ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.remove_api_key(self.current_platform, full_key)
            self.load_api_keys()
            self.update_platform_info()
