import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QFrame, QLabel, 
                             QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon

# IMPORT file menu
base_dir = os.path.dirname(os.path.abspath(__file__))
pages_path = os.path.join(base_dir, "pages")

if pages_path not in sys.path:
    sys.path.insert(0, pages_path)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Login"))
from login import LoginPage
try:
    from login import LoginPage
except ImportError:
    # Jika file login_page.py:
    from login_page import LoginPage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Dashboard"))
from dashboard import DashboardPage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Dashboard Admin"))
from dashboard_admin import AdminDashboardPage

# Live Discovery ada di folder dengan spasi → gunakan sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Live Discovery"))
from live_discovery import LiveDiscoveryPage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Job Archive"))
from job_archive import JobArchivePage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Career Toolkit"))
from toolkit_main import CareerToolkitPage

# Tambahkan path untuk modul database agar bisa dibersihkan saat tutup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Modul"))
from modul_database import bersihkan_database_sementara

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Job Posting"))
from job_posting import JobPostingPage

#Path untuk modul pengolahan_data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Modul"))
from modul_pengolahan_data import hitung_persentase_skill


from dashboard import DashboardPage
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gottajob")
        self.resize(1280, 800)

        # Set window icon dari assets/logo.png
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Kerangka Utama
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout_utama = QHBoxLayout(self.main_widget)
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setObjectName("Sidebar")
        #styling
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar { background-color: #2C687B; border: none; }
            QPushButton {
                color: #B2D2D9;
                background-color: transparent;
                padding: 18px 25px;
                text-align: left;
                font-size: 21px;
                border: none;
                border-radius: 12px;
                margin: 8px 15px;
            }
            QPushButton:hover { background-color: #408699; color: white; }
            QPushButton#ActiveMenu {
                background-color: #8CC7C4;
                color: white;
                font-weight: bold;
            }
        """)

        self.layout_sidebar = QVBoxLayout(self.sidebar)
        self.layout_sidebar.setAlignment(Qt.AlignTop)

        self.setup_logo()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #4A8799; margin: 0 15px;")
        self.layout_sidebar.addWidget(line)
        self.layout_sidebar.addSpacing(20)

        # TOMBOL MENU
        self.menu_buttons = []
        
        self.btn_dashboard = self.create_menu_btn("  Dashboard", 0, "Dashboard", "dashboard.png")
        self.btn_admin     = self.create_menu_btn("Dashboard admin", 5, "Dashboard Admin", "dahboard.png")
        self.btn_discovery = self.create_menu_btn("  Live Discovery", 1, "Live Discovery", "search.png")
        self.btn_archive   = self.create_menu_btn("  Job Archive", 2, "Job Archive", "folder.png")
        self.btn_directory = self.create_menu_btn("  Job Posting", 3, "Job Posting", "post.png")
        self.btn_toolkit   = self.create_menu_btn("  Career Toolkit", 4, "Career Toolkit", "toolbox.png")

        self.btn_dashboard.setObjectName("ActiveMenu")

        # AREA KONTEN (KANAN)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F3F4F6;")

        # MENU
        self.halaman_dashboard = DashboardPage() # <--- PENTING: Membuat objek halaman
        self.halaman_dashboard_admin = AdminDashboardPage()

        self.halaman_discovery = LiveDiscoveryPage()
        # Koneksi signal refresh dashboard dari Live Discovery
        self.halaman_discovery.favorite_changed.connect(self.halaman_dashboard.load_data)
        self.halaman_discovery.favorite_changed.connect(self.halaman_dashboard_admin.load_data)
        
        self.halaman_archive = JobArchivePage()
        # Koneksi signal refresh dashboard
        self.halaman_archive.favorite_changed.connect(self.halaman_dashboard.load_data)
        
        self.toolkit_page = CareerToolkitPage()
        
        self.job_posting_page = JobPostingPage()

        self.content_stack.addWidget(self.halaman_dashboard)         # Index 0
        self.content_stack.addWidget(self.halaman_discovery)         # Index 1
        self.content_stack.addWidget(self.halaman_archive)           # Index 2 (Sudah dibuat)
        self.content_stack.addWidget(self.job_posting_page)          # Index 3 (Job Posting)
        self.content_stack.addWidget(self.toolkit_page)              # Index 4
        self.content_stack.addWidget(self.halaman_dashboard_admin)   # Index 5

        self.halaman_login = LoginPage(self)
        self.content_stack.addWidget(self.halaman_login)

        # hide sidebar
        self.sidebar.hide()
        self.content_stack.setCurrentWidget(self.halaman_login)

        self.layout_utama.addWidget(self.sidebar)
        self.layout_utama.addWidget(self.content_stack)

    def show_admin_dashboard(self):
        self.sidebar.show() # Munculkan lagi sidebar
        self.btn_dashboard.hide() # Sembunyikan menu user jika perlu
        self.pindah_halaman(self.btn_admin, 5) # Paksa pindah ke halaman admin (index 5)

    def show_user_dashboard(self):
        self.sidebar.show() # Munculkan lagi sidebarnya
        self.btn_admin.hide() # Sembunyikan menu admin untuk user biasa
        self.pindah_halaman(self.btn_dashboard, 0) # Paksa pindah ke dashboard user (index 0)

    def setup_logo(self):
        container = QWidget()
        container.setFixedHeight(100)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 10, 10, 10)
        label_img = QLabel()
        pix = QPixmap('assets/logo.png')
        if not pix.isNull():
            label_img.setFixedWidth(60)
            label_img.setPixmap(pix.scaledToHeight(60, Qt.SmoothTransformation))
        label_txt = QLabel("GOTTAJOB")
        label_txt.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        layout.addWidget(label_img)
        layout.addWidget(label_txt)
        layout.addStretch()
        self.layout_sidebar.addWidget(container)

    def create_menu_btn(self, text, index, folder_name, icon_name=None):
        btn = QPushButton(text)
        font = QFont("Segoe UI", 18) 
        btn.setFont(font)

        if icon_name:
            base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, 'assets', folder_name, icon_name)
            
            icon = QIcon(icon_path)
            if not icon.isNull():
                btn.setIcon(icon)
                btn.setIconSize(QSize(32, 32)) 
        
        btn.clicked.connect(lambda: self.pindah_halaman(btn, index))
        self.layout_sidebar.addWidget(btn)
        self.menu_buttons.append(btn)
        return btn

    def pindah_halaman(self, clicked_btn, index):
        self.content_stack.setCurrentIndex(index)
        for btn in self.menu_buttons:
            btn.setObjectName("")
        clicked_btn.setObjectName("ActiveMenu")
        self.sidebar.setStyleSheet(self.sidebar.styleSheet())

    def create_page(self, text):
        """Halaman dummy sementara sebelum kamu buat file .py nya"""
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(f"Halaman {text} (Belum dibuat filenya)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def closeEvent(self, event):
        """Dijalankan saat user menutup aplikasi."""
        try:
            bersihkan_database_sementara()
        except:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Terapkan Tema Global (Tombol Dialog & Scrollbar)
    from modul_antarmuka_pengguna import GLOBAL_DIALOG_STYLE
    app.setStyleSheet(GLOBAL_DIALOG_STYLE)
    
    app.setFont(QFont("Segoe UI", 10))
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())