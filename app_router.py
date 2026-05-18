import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QFrame, QLabel, 
                             QStackedWidget, QShortcut)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
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

# Account Manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "create_user"))
from create_user import create_account_manager_page

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
        self.menu_texts = {
            "Dashboard": "  Dashboard",
            "Dashboard Admin": "  Dashboard Admin",
            "Skill Manager": "  Skill Manager",
            "Live Discovery": "  Live Discovery",
            "Job Archive": "  Job Archive",
            "Job Posting": "  Job Posting",
            "Career Toolkit": "  Career Toolkit",
            "Account Manager": "  Account Manager",
            "Logout": "  Logout"
        }
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
        # COLLAPSE SIDEBAR
        self.sidebar_expanded_width = 280
        self.sidebar_collapsed_width = 85
        self.sidebar_expanded = True

        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(self.sidebar_expanded_width)
        self.sidebar.setMaximumWidth(self.sidebar_expanded_width)
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
                outline: none;
            }
            QPushButton:hover, QPushButton:focus { background-color: #408699; color: white; outline: none; }
            QPushButton#ActiveMenu {
                background-color: #8CC7C4;
                color: white;
                font-weight: bold;
            }
            QPushButton#ActiveMenu:hover, QPushButton#ActiveMenu:focus {
                background-color: #8CC7C4;
                color: white;
            }
        """)

        self.layout_sidebar = QVBoxLayout(self.sidebar)
        self.layout_sidebar.setContentsMargins(0, 0, 0, 0)
        self.layout_sidebar.setSpacing(0)
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
        self.btn_admin     = self.create_menu_btn("  Dashboard", 5, "Dashboard Admin", "dahboard.png")
        self.btn_discovery = self.create_menu_btn("  Live Discovery", 1, "Live Discovery", "search.png")
        self.btn_archive   = self.create_menu_btn("  Job Archive", 2, "Job Archive", "folder.png")
        self.btn_skill_manager = self.create_menu_btn("  Skill Manager", 6, "Skill Manager", "settings.png")
        self.btn_account_manager   = self.create_menu_btn("  Account Manager", 8, "Account Manager", "settings.png")
        self.btn_directory = self.create_menu_btn("  Job Posting", 3, "Job Posting", "post.png")
        self.btn_toolkit   = self.create_menu_btn("  Career Toolkit", 4, "Career Toolkit", "toolbox.png")
        
        # Sembunyikan Dashboard Admin & Skill Manager dari menu default (user biasa)
        self.btn_admin.hide()
        self.btn_skill_manager.hide()
        self.btn_account_manager.hide()

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
            self.btn_admin,
            self.btn_discovery,
            self.btn_archive,
            self.btn_skill_manager,
            self.btn_account_manager,
            self.btn_directory,
            self.btn_toolkit
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
        self.halaman_account_manager = create_account_manager_page(self)

        # Koneksi Signal
        self.halaman_discovery.favorite_changed.connect(self.halaman_dashboard.load_data)
        self.halaman_discovery.favorite_changed.connect(self.halaman_dashboard_admin.load_data)
        self.halaman_archive.favorite_changed.connect(self.halaman_dashboard.load_data)
        self.halaman_archive.favorite_changed.connect(self.halaman_dashboard_admin.load_data)
        self.halaman_archive.build_cv_requested.connect(self.go_to_toolkit_for_ai)
        self.halaman_dashboard_admin.manage_skill_requested.connect(self.go_to_skill_manager_with_filter)
        
        # Tambahkan ke Stack
        self.content_stack.addWidget(self.halaman_dashboard)         # Index 0
        self.content_stack.addWidget(self.halaman_discovery)         # Index 1
        self.content_stack.addWidget(self.halaman_archive)           # Index 2
        self.content_stack.addWidget(self.job_posting_page)          # Index 3
        self.content_stack.addWidget(self.toolkit_page)              # Index 4
        self.content_stack.addWidget(self.halaman_dashboard_admin)   # Index 5
        self.content_stack.addWidget(self.skill_manager_page)        # Index 6
        self.content_stack.addWidget(self.halaman_login)             # Index 7
        self.content_stack.addWidget(self.halaman_account_manager)   # Index 8

        # Tampilan Awal: Login
        self.sidebar.hide()
        self.content_stack.setCurrentWidget(self.halaman_login)

        self.layout_utama.addWidget(self.sidebar)
        self.layout_utama.addWidget(self.content_stack)

        # Sinkronisasi folder kategori
        import threading
        threading.Thread(target=sinkronisasi_folder_kategori, daemon=True).start()

    def show_admin_dashboard(self):
        """Dijalankan setelah login admin berhasil."""
        self.update_theme(is_admin=True)
        self.job_posting_page.update_theme_mode(is_admin=True)
        self.halaman_discovery.update_theme_mode(is_admin=True)
        self.halaman_archive.update_theme_mode(is_admin=True)
        self.sidebar.show()
        # Admin melihat menu khusus admin dan manager
        self.btn_dashboard.hide()
        self.btn_toolkit.hide() # Tutup akses career toolkit

        self.btn_admin.show()
        self.btn_skill_manager.show()
        self.btn_account_manager.show()
        self.lbl_admin_badge.show()
        
        # Batasi navigasi tombol hanya untuk admin sesuai urutan baru
        self.nav_buttons = [
            self.btn_admin,
            self.btn_discovery,
            self.btn_archive,
            self.btn_skill_manager,
            self.btn_account_manager,
            self.btn_directory
        ]
        
        self.pindah_halaman(self.btn_admin, 5)

    def show_user_dashboard(self):
        """Dijalankan setelah login user biasa berhasil."""
        self.update_theme(is_admin=False)
        self.job_posting_page.update_theme_mode(is_admin=False)
        self.halaman_discovery.update_theme_mode(is_admin=False)
        self.halaman_archive.update_theme_mode(is_admin=False)
        self.sidebar.show()
        self.btn_admin.hide()
        self.btn_skill_manager.hide()
        self.btn_account_manager.hide()
        self.lbl_admin_badge.hide()
        self.btn_dashboard.show()
        self.btn_toolkit.show() # Tampilkan jika sebelumnya disembunyikan oleh admin
        
        # Batasi navigasi tombol hanya untuk user
        self.nav_buttons = [
            self.btn_dashboard,
            self.btn_discovery,
            self.btn_archive,
            self.btn_directory,
            self.btn_toolkit
        ]
        
        self.pindah_halaman(self.btn_dashboard, 0)

    def proses_logout(self):
        """Kembali ke halaman login dan sembunyikan sidebar."""
        self.sidebar.hide()
        self.halaman_login.input_user.clear()
        self.halaman_login.input_pass.clear()
        self.update_theme(is_admin=False) # Reset background to clean gray (#F3F4F6)
        self.content_stack.setCurrentWidget(self.halaman_login)

    def update_theme(self, is_admin):
        """Mengatur tema umum aplikasi (background window, sidebar, dan halaman) tergantung sisi user/admin."""
        # 1. Tentukan warna background dasar aplikasi
        bg_app = "#F0FFFF" if is_admin else "#F3F4F6"
        
        # Terapkan background ke QMainWindow, main_widget, dan content_stack
        self.setStyleSheet(f"QMainWindow {{ background-color: {bg_app}; }}")
        self.main_widget.setStyleSheet(f"background-color: {bg_app};")
        self.content_stack.setStyleSheet(f"background-color: {bg_app};")
        
        # 2. Logika Sidebar Theme
        bg_color = "#1E3A5F" if is_admin else "#2C687B"
        hover_color = "#295180" if is_admin else "#408699"
        active_color = "#386D9E" if is_admin else "#8CC7C4"
        line_color = "#295180" if is_admin else "#4A8799"
        
        self.sidebar_hover_color = hover_color
        self.sidebar_active_color = active_color
        
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
                outline: none;
            }}
            QPushButton:hover, QPushButton:focus {{ background-color: {hover_color}; color: white; outline: none; }}
            QPushButton#ActiveMenu {{
                background-color: {active_color};
                color: white;
                font-weight: bold;
            }}
            QPushButton#ActiveMenu:hover, QPushButton#ActiveMenu:focus {{
                background-color: {active_color};
                color: white;
            }}
        """)
        
        self.update_btn_toggle_style()

    def update_btn_toggle_style(self):
        """Update style of btn_toggle to match page buttons dynamically"""
        hover_color = getattr(self, "sidebar_hover_color", "#408699")
        active_color = getattr(self, "sidebar_active_color", "#8CC7C4")
        
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
                padding: 0px;
                margin: 0px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {active_color};
            }}
        """)

    def setup_logo(self):
        container = QWidget()
        container.setObjectName("LogoContainer")
        container.setFixedHeight(80)
        container.setStyleSheet("""
            QWidget#LogoContainer {
                background-color: transparent;
                border: none;
            }
        """)

        self.logo_layout = QHBoxLayout(container)
        self.logo_layout.setContentsMargins(15, 10, 20, 10)
        self.logo_layout.setSpacing(10)

        # =========================
        # LOGO IMAGE
        # =========================
        self.label_img = QLabel()
        self.label_img.setStyleSheet("background: transparent; border: none;")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Pastikan path ke assets selalu dihitung dari root proyek (naik satu tingkat)
        base_path = os.path.dirname(current_dir)
        logo_path = os.path.join(base_path, 'assets', 'logo.png')
        pix = QPixmap(logo_path)

        if not pix.isNull():
            self.label_img.setPixmap(
                pix.scaled(
                    38,
                    38,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        # =========================
        # TEXT LOGO
        # =========================
        self.container_text_logo = QWidget()
        self.container_text_logo.setStyleSheet("background: transparent; border: none;")
        text_layout = QVBoxLayout(self.container_text_logo)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        self.label_txt = QLabel("GOTTAJOB")
        self.label_txt.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)

        self.lbl_admin_badge = QLabel("admin")
        self.lbl_admin_badge.setStyleSheet("""
            color: #E74C3C;
            font-size: 13px;
            font-weight: bold;
            font-style: italic;
        """)
        self.lbl_admin_badge.hide()

        text_layout.addWidget(self.label_txt)
        text_layout.addWidget(self.lbl_admin_badge)

        # =========================
        # TOGGLE BUTTON (Pindah ke Kanan)
        # =========================
        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedSize(55, 55)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)

        icon_path = os.path.join(base_path, 'assets', 'burger-bar.png')

        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.btn_toggle.setIcon(icon)
            self.btn_toggle.setIconSize(QSize(30, 30))
            self.btn_toggle.setText("")
        else:
            self.btn_toggle.setText("☰")

        self.update_btn_toggle_style()
        self.btn_toggle.clicked.connect(self.toggle_sidebar)

        # =========================
        # ADD WIDGET (Urutan diubah agar Burger di Kanan)
        # =========================
        self.logo_layout.addWidget(self.label_img)
        self.logo_layout.addWidget(self.container_text_logo)
        
        # Dorong tombol burger ke ujung kanan menggunakan Stretch
        self.logo_layout.addStretch() 
        self.logo_layout.addWidget(self.btn_toggle)

        self.layout_sidebar.addWidget(container)

    #TOOGLE SIDEBAR
    def toggle_sidebar(self):
        # Tentukan width tujuan
        if self.sidebar_expanded:
            new_width = self.sidebar_collapsed_width
        else:
            new_width = self.sidebar_expanded_width

        # Animasi minimum width
        self.anim_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim_min.setDuration(250)
        self.anim_min.setStartValue(self.sidebar.width())
        self.anim_min.setEndValue(new_width)
        self.anim_min.setEasingCurve(QEasingCurve.InOutQuart)

        # Animasi maximum width
        self.anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim_max.setDuration(250)
        self.anim_max.setStartValue(self.sidebar.width())
        self.anim_max.setEndValue(new_width)
        self.anim_max.setEasingCurve(QEasingCurve.InOutQuart)

        self.anim_min.start()
        self.anim_max.start()

        # =========================
        # COLLAPSE STATE
        # =========================
        if self.sidebar_expanded:
            self.container_text_logo.hide()
            self.label_img.hide() # Sembunyikan logo utama agar tersisa tombol burger saja di atas

            # Set size and margins of toggle button to match collapsed page buttons exactly!
            self.btn_toggle.setFixedSize(73, 55)
            self.logo_layout.setContentsMargins(6, 12, 6, 12)

            self.btn_logout.setText("")

            for btn in self.menu_buttons:
                btn.setText("")
                # Pastikan icon tetap muncul di tengah (Center) saat teks kosong
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 14px;
                        margin: 6px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        border-radius: 10px;
                    }
                """)

        # =========================
        # EXPAND STATE
        # =========================
        else:
            self.container_text_logo.show()
            self.label_img.show() # Munculkan kembali logo utama

            # Reset size and margins to expanded state
            self.btn_toggle.setFixedSize(55, 55)
            self.logo_layout.setContentsMargins(15, 12, 20, 12)

            self.btn_dashboard.setText(self.menu_texts["Dashboard"])
            self.btn_admin.setText(self.menu_texts["Dashboard Admin"])
            self.btn_skill_manager.setText(self.menu_texts["Skill Manager"])
            self.btn_discovery.setText(self.menu_texts["Live Discovery"])
            self.btn_archive.setText(self.menu_texts["Job Archive"])
            self.btn_directory.setText(self.menu_texts["Job Posting"])
            self.btn_toolkit.setText(self.menu_texts["Career Toolkit"])
            self.btn_account_manager.setText(self.menu_texts["Account Manager"])
            self.btn_logout.setText(self.menu_texts["Logout"])

            for btn in self.menu_buttons:
                btn.setStyleSheet("") # Kembalikan ke style asal (text-align: left biasanya)

        # FIX: Pindahkan toggle state ke luar if-else agar selalu dieksekusi tiap kali diklik
        self.sidebar_expanded = not self.sidebar_expanded

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
        
        # Auto-reload dashboards on transition
        if index == 0 and hasattr(self, 'halaman_dashboard'):
            self.halaman_dashboard.load_data()
        elif index == 5 and hasattr(self, 'halaman_dashboard_admin'):
            self.halaman_dashboard_admin.load_data()

    def go_to_toolkit_for_ai(self, job_data):
        toolkit_index = 4 
        self.content_stack.setCurrentIndex(toolkit_index)
        if hasattr(self, 'btn_toolkit'):
            self.pindah_halaman(self.btn_toolkit, toolkit_index)
        if hasattr(self, 'toolkit_page'):
            self.toolkit_page.apply_ai_enhancement(job_data)
            
    def go_to_skill_manager_with_filter(self, skill_name, category_name):
        skill_manager_index = 6
        self.content_stack.setCurrentIndex(skill_manager_index)
        if hasattr(self, 'btn_skill_manager'):
            self.pindah_halaman(self.btn_skill_manager, skill_manager_index)
        if hasattr(self, 'skill_manager_page'):
            self.skill_manager_page.set_search_filter(skill_name, category_name)
            
    def get_current_nav_index(self):
        """Mencari indeks tombol navigasi aktif dalam daftar self.nav_buttons"""
        for i, btn in enumerate(self.nav_buttons):
            if btn.objectName() == "ActiveMenu":
                return i
        return -1

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Up, Qt.Key_Down):
            # 1. Tentukan arah navigasi
            is_up = (key == Qt.Key_Up)
            
            # 2. Cegah navigasi jika berada di sub-halaman tabel hasil atau detail di Job Archive
            # (Pada halaman dalam ini, arrow key didedikasikan sepenuhnya untuk menggerakkan scroll)
            current_page = self.content_stack.currentWidget()
            if current_page == self.halaman_archive:
                sub_page = self.halaman_archive.main_stack.currentWidget()
                if sub_page in (self.halaman_archive.table_view, self.halaman_archive.detail_view):
                    # Redireksi event secara langsung ke tabel atau scroll detail
                    if sub_page == self.halaman_archive.table_view:
                        self.halaman_archive.match_results.table.setFocus()
                        QApplication.sendEvent(self.halaman_archive.match_results.table, event)
                    else:
                        self.halaman_archive.detail_view.scroll.setFocus()
                        QApplication.sendEvent(self.halaman_archive.detail_view.scroll, event)
                    event.accept()
                    return

            # 3. Cegah navigasi jika fokus sedang di dalam input, combobox, atau scroll area
            # (Menjamin navigasi keyboard widget tidak terinterupsi jika widget sedang aktif)
            focused = QApplication.focusWidget()
            if focused:
                from PyQt5.QtWidgets import QLineEdit, QComboBox, QAbstractScrollArea
                if isinstance(focused, (QLineEdit, QComboBox, QAbstractScrollArea)):
                    super().keyPressEvent(event)
                    return
                parent = focused.parent()
                while parent:
                    if isinstance(parent, QAbstractScrollArea):
                        super().keyPressEvent(event)
                        return
                    parent = parent.parent()

            # 4. Jika sidebar tidak aktif, biarkan penekanan tombol normal
            if not self.sidebar.isVisible():
                super().keyPressEvent(event)
                return

            # 5. Jalankan navigasi pemindahan fokus/highlight sidebar
            focused = QApplication.focusWidget()
            curr_idx = -1
            for i, btn in enumerate(self.nav_buttons):
                if btn == focused:
                    curr_idx = i
                    break
            
            if curr_idx == -1:
                # Jika belum ada yang fokus, mulai dari tombol halaman aktif saat ini
                curr_idx = self.get_current_nav_index()
            
            if is_up:
                target_idx = curr_idx - 1
            else:
                target_idx = curr_idx + 1
                
            if 0 <= target_idx < len(self.nav_buttons):
                self.nav_buttons[target_idx].setFocus()
            event.accept()
        elif key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            focused = QApplication.focusWidget()
            if focused in self.nav_buttons:
                focused.click()
                event.accept()
                return
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        try:
            bersihkan_database_sementara()
        except:
            pass
        event.accept()

    