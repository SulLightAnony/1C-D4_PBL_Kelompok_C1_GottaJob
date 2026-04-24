import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QFrame, QLabel, 
                             QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from pages.career_toolkit.toolkit_main import CareerToolkitPage

# IMPORT file menu
from pages.dashboard import DashboardPage

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GottaJob Dashboard")
        self.resize(1280, 800)

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
                font-size: 22px;
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
        
        self.btn_dashboard = self.create_menu_btn("  Dashboard", 0, "dashboard.png")
        self.btn_discovery = self.create_menu_btn("  Live Discovery", 1, "search.png")
        self.btn_archive   = self.create_menu_btn("  Job Archive", 2, "folder.png")
        self.btn_directory = self.create_menu_btn("  Job Posting", 3, "post.png")
        self.btn_toolkit   = self.create_menu_btn("  Career Toolkit", 4, "toolbox.png")

        self.btn_dashboard.setObjectName("ActiveMenu")

        # AREA KONTEN (KANAN)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F3F4F6;")

        # MENU
        self.halaman_dashboard = DashboardPage() # <--- PENTING: Membuat objek halaman
        self.toolkit_page = CareerToolkitPage()
        
        self.content_stack.addWidget(self.halaman_dashboard)         # Index 0
        self.content_stack.addWidget(self.create_page("Discovery"))  # Index 1 (Sementara)
        self.content_stack.addWidget(self.create_page("Archive"))    # Index 2 (Sementara)
        self.content_stack.addWidget(self.create_page("Directory"))  # Index 3 (Sementara)
        self.content_stack.addWidget(self.toolkit_page)             # Index 4

        self.layout_utama.addWidget(self.sidebar)
        self.layout_utama.addWidget(self.content_stack)

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

    def create_menu_btn(self, text, index, icon_name=None):
        btn = QPushButton(text)
        font = QFont("Segoe UI", 18) 
        btn.setFont(font)

        if icon_name:
            base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, 'assets', icon_name)
            
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())