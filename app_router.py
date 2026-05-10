import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QFrame, QLabel, 
                             QStackedWidget, QShortcut)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QKeySequence

# IMPORT file menu
base_dir = os.path.dirname(os.path.abspath(__file__))
pages_path = os.path.join(base_dir, "pages")

if pages_path not in sys.path:
    sys.path.insert(0, pages_path)

# Login
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Login"))
try:
    from login import LoginPage
except ImportError:
    from login_page import LoginPage

# Dashboard
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Dashboard"))
from dashboard import DashboardPage

# Admin Dashboard
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Dashboard Admin"))
from dashboard_admin import AdminDashboardPage

# Live Discovery
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Live Discovery"))
from live_discovery import LiveDiscoveryPage

# Job Archive
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Job Archive"))
from job_archive import JobArchivePage

# Career Toolkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Career Toolkit"))
from toolkit_main import CareerToolkitPage

# Modul
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Modul"))
from modul_database import bersihkan_database_sementara, sinkronisasi_folder_kategori

# Job Posting
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Job Posting"))
from job_posting import JobPostingPage

# Skill Manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pages", "Skill Manager"))
from skill_manager import SkillManagerPage


class AppRouter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gottajob")
        self.setStyleSheet("QMainWindow { background-color: #F3F4F6; }") # Background dasar QMainWindow

        # Set window icon
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Kerangka Utama
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: #F3F4F6;")
        self.setCentralWidget(self.main_widget)
        self.layout_utama = QHBoxLayout(self.main_widget)
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setObjectName("Sidebar")
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

        self.sidebar_line = QFrame()
        self.sidebar_line.setFrameShape(QFrame.HLine)
        self.sidebar_line.setStyleSheet("background-color: #4A8799; margin: 0 15px;")
        self.layout_sidebar.addWidget(self.sidebar_line)
        self.layout_sidebar.addSpacing(20)

        # TOMBOL MENU
        self.menu_buttons = []
        
        self.btn_dashboard = self.create_menu_btn("  Dashboard", 0, "Dashboard", "dashboard.png")
        self.btn_admin     = self.create_menu_btn("  Dashboard Admin", 5, "Dashboard Admin", "dahboard.png")
        self.btn_skill_manager = self.create_menu_btn("  Skill Manager", 6, "Skill Manager", "settings.png")
        self.btn_discovery = self.create_menu_btn("  Live Discovery", 1, "Live Discovery", "search.png")
        self.btn_archive   = self.create_menu_btn("  Job Archive", 2, "Job Archive", "folder.png")
        self.btn_directory = self.create_menu_btn("  Job Posting", 3, "Job Posting", "post.png")
        self.btn_toolkit   = self.create_menu_btn("  Career Toolkit", 4, "Career Toolkit", "toolbox.png")
        
        # Sembunyikan Dashboard Admin & Skill Manager dari menu default (user biasa)
        self.btn_admin.hide()
        self.btn_skill_manager.hide()

        # Tambahkan Spacer agar tombol Logout selalu di bawah
        self.layout_sidebar.addStretch()

        # Tombol Logout
        self.btn_logout = QPushButton("  Logout")
        self.btn_logout.setFont(QFont("Segoe UI", 18))
        
        # Tambahkan Ikon Log-Out
        icon_path_logout = os.path.join(base_dir, 'assets', 'log-out.png')
        icon_logout = QIcon(icon_path_logout)
        if not icon_logout.isNull():
            self.btn_logout.setIcon(icon_logout)
            self.btn_logout.setIconSize(QSize(24, 24))

        self.btn_logout.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #C0392B;
                padding: 15px;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
                margin: 8px 15px;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.proses_logout)
        self.layout_sidebar.addWidget(self.btn_logout)


        self.nav_buttons = [
            self.btn_dashboard,
            self.btn_discovery,
            self.btn_archive,
            self.btn_directory,
            self.btn_toolkit,
            self.btn_admin,
            self.btn_skill_manager
        ]

        self.btn_dashboard.setObjectName("ActiveMenu")

        # AREA KONTEN (KANAN)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F3F4F6;")

        # HALAMAN-HALAMAN
        self.halaman_dashboard = DashboardPage()
        self.halaman_dashboard_admin = AdminDashboardPage()
        self.halaman_discovery = LiveDiscoveryPage()
        self.halaman_archive = JobArchivePage()
        self.toolkit_page = CareerToolkitPage()
        self.job_posting_page = JobPostingPage()
        self.skill_manager_page = SkillManagerPage()
        self.halaman_login = LoginPage(self)

        # Koneksi Signal
        self.halaman_discovery.favorite_changed.connect(self.halaman_dashboard.load_data)
        self.halaman_discovery.favorite_changed.connect(self.halaman_dashboard_admin.load_data)
        self.halaman_archive.favorite_changed.connect(self.halaman_dashboard.load_data)
        self.halaman_archive.build_cv_requested.connect(self.go_to_toolkit_for_ai)
        
        # Tambahkan ke Stack
        self.content_stack.addWidget(self.halaman_dashboard)         # Index 0
        self.content_stack.addWidget(self.halaman_discovery)         # Index 1
        self.content_stack.addWidget(self.halaman_archive)           # Index 2
        self.content_stack.addWidget(self.job_posting_page)          # Index 3
        self.content_stack.addWidget(self.toolkit_page)              # Index 4
        self.content_stack.addWidget(self.halaman_dashboard_admin)   # Index 5
        self.content_stack.addWidget(self.skill_manager_page)        # Index 6
        self.content_stack.addWidget(self.halaman_login)             # Index 7

        # Tampilan Awal: Login
        self.sidebar.hide()
        self.content_stack.setCurrentWidget(self.halaman_login)

        self.layout_utama.addWidget(self.sidebar)
        self.layout_utama.addWidget(self.content_stack)

        # Sinkronisasi folder kategori
        import threading
        threading.Thread(target=sinkronisasi_folder_kategori, daemon=True).start()
        
        # Shortcut Navigasi
        self.shortcut_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut_up.activated.connect(self.navigasi_ke_atas)
        self.shortcut_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut_down.activated.connect(self.navigasi_ke_bawah)

    def show_admin_dashboard(self):
        """Dijalankan setelah login admin berhasil."""
        self.update_sidebar_theme(is_admin=True)
        self.job_posting_page.update_theme_mode(is_admin=True)
        self.halaman_discovery.update_theme_mode(is_admin=True)
        self.halaman_archive.update_theme_mode(is_admin=True)
        self.sidebar.show()
        # Admin melihat menu khusus admin dan manager
        self.btn_dashboard.hide()
        self.btn_toolkit.hide() # Tutup akses career toolkit
        self.btn_admin.show()
        self.btn_skill_manager.show()
        self.lbl_admin_badge.show()
        self.pindah_halaman(self.btn_admin, 5)

    def show_user_dashboard(self):
        """Dijalankan setelah login user biasa berhasil."""
        self.update_sidebar_theme(is_admin=False)
        self.job_posting_page.update_theme_mode(is_admin=False)
        self.halaman_discovery.update_theme_mode(is_admin=False)
        self.halaman_archive.update_theme_mode(is_admin=False)
        self.sidebar.show()
        self.btn_admin.hide()
        self.btn_skill_manager.hide()
        self.lbl_admin_badge.hide()
        self.btn_dashboard.show()
        self.btn_toolkit.show() # Tampilkan jika sebelumnya disembunyikan oleh admin
        self.pindah_halaman(self.btn_dashboard, 0)

    def proses_logout(self):
        """Kembali ke halaman login dan sembunyikan sidebar."""
        self.sidebar.hide()
        self.halaman_login.input_user.clear()
        self.halaman_login.input_pass.clear()
        self.content_stack.setCurrentWidget(self.halaman_login)

    def update_sidebar_theme(self, is_admin):
        bg_color = "#1E3A5F" if is_admin else "#2C687B"
        hover_color = "#295180" if is_admin else "#408699"
        active_color = "#386D9E" if is_admin else "#8CC7C4"
        line_color = "#295180" if is_admin else "#4A8799"
        
        if hasattr(self, 'sidebar_line'):
            self.sidebar_line.setStyleSheet(f"background-color: {line_color}; margin: 0 15px;")

        self.sidebar.setStyleSheet(f"""
            QFrame#Sidebar {{ background-color: {bg_color}; border: none; }}
            QPushButton {{
                color: #B2D2D9;
                background-color: transparent;
                padding: 18px 25px;
                text-align: left;
                font-size: 21px;
                border: none;
                border-radius: 12px;
                margin: 8px 15px;
            }}
            QPushButton:hover {{ background-color: {hover_color}; color: white; }}
            QPushButton#ActiveMenu {{
                background-color: {active_color};
                color: white;
                font-weight: bold;
            }}
        """)

    def setup_logo(self):
        container = QWidget()
        container.setFixedHeight(100)
        container.setStyleSheet("background-color: transparent;") # Mencegah pewarisan background dari main_widget
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 10, 10, 10)
        label_img = QLabel()
        pix = QPixmap('assets/logo.png')
        if not pix.isNull():
            label_img.setFixedWidth(60)
            label_img.setPixmap(pix.scaledToHeight(60, Qt.SmoothTransformation))
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        label_txt = QLabel("GOTTAJOB")
        label_txt.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        
        self.lbl_admin_badge = QLabel("admin")
        self.lbl_admin_badge.setStyleSheet("color: #E74C3C; font-size: 20px; font-style: italic; font-weight: bold;")
        self.lbl_admin_badge.setAlignment(Qt.AlignRight)
        self.lbl_admin_badge.hide()
        
        text_layout.addWidget(label_txt)
        text_layout.addWidget(self.lbl_admin_badge)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        layout.addWidget(label_img)
        layout.addLayout(text_layout)
        layout.addStretch()
        self.layout_sidebar.addWidget(container)

    def create_menu_btn(self, text, index, folder_name, icon_name=None):
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 18))
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

    def go_to_toolkit_for_ai(self, job_data):
        toolkit_index = 4 
        self.content_stack.setCurrentIndex(toolkit_index)
        if hasattr(self, 'btn_toolkit'):
            self.pindah_halaman(self.btn_toolkit, toolkit_index)
        if hasattr(self, 'toolkit_page'):
            self.toolkit_page.apply_ai_enhancement(job_data)
            
    def navigasi_ke_atas(self):
        curr = self.content_stack.currentIndex()
        if 0 < curr < 5: # Navigasi hanya di menu utama user
            self.nav_buttons[curr-1].click()

    def navigasi_ke_bawah(self):
        curr = self.content_stack.currentIndex()
        if 0 <= curr < 4:
            self.nav_buttons[curr+1].click()

    def closeEvent(self, event):
        try:
            bersihkan_database_sementara()
        except:
            pass
        event.accept()
