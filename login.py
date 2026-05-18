import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStyle,
                             QLineEdit, QPushButton, QFrame, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon

class LoginPage(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window 
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Pastikan mengembang penuh
        self.init_ui()

    def init_ui(self):
        # Background utama
        self.setStyleSheet("background-color: #F3F4F6;") 
        
        layout_utama = QVBoxLayout(self)
        layout_utama.setAlignment(Qt.AlignCenter)

        # Kartu Login
        self.card = QFrame()
        self.card.setFixedSize(450, 500)
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 25px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(8)

        # Logo GottaJob
        lbl_logo_img = QLabel()
        pix = QPixmap('assets/logo.png')
        if not pix.isNull():
            lbl_logo_img.setPixmap(pix.scaled(65, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_logo_img.setAlignment(Qt.AlignCenter)
        lbl_logo_img.setStyleSheet("border: none; margin-bottom: 5px;")

        # Title 
        lbl_title = QLabel("Welcome Back")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C687B; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_subtitle = QLabel("Please enter your details")
        lbl_subtitle.setStyleSheet("color: #7F8C8D; font-size: 13px; border: none; margin-bottom: 10px;")
        lbl_subtitle.setAlignment(Qt.AlignCenter)

        # Input Fields Styling
        label_style = "font-weight: bold; color: #34495E; border: none; margin-top: 10px; font-size:14px;"
        
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet(label_style)
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Enter your username")
        self.apply_input_style(self.input_user)

        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet(label_style)
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Enter your password")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.apply_input_style(self.input_pass)
        self.input_pass.returnPressed.connect(self.handle_login)
        self.input_user.returnPressed.connect(self.input_pass.setFocus)

        self.password_visible = False
        self.icon_hidden = QIcon('assets/hidden.png') 
        self.icon_shown = QIcon('assets/eye.png')
        
        self.toggle_login_password_action = self.input_pass.addAction(
            self.icon_hidden, 
            QLineEdit.TrailingPosition
        )
        self.toggle_login_password_action.triggered.connect(self.toggle_login_password)

        # Login Button (Gunakan warna aksen sidebar yang cerah)
        btn_login = QPushButton("LOGIN")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #2C687B; 
                color: white; 
                font-weight: bold; 
                font-size: 16px;
                border-radius: 12px; 
                padding: 10px;
                margin-top: 20px;
                border: none;
            }
            QPushButton:hover { background-color: #408699; }
        """)
        btn_login.clicked.connect(self.handle_login)

        # Susun komponen
        card_layout.addWidget(lbl_logo_img)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_subtitle)
        card_layout.addWidget(lbl_user)
        card_layout.addWidget(self.input_user)
        card_layout.addWidget(lbl_pass)
        card_layout.addWidget(self.input_pass)
        card_layout.addStretch()
        card_layout.addWidget(btn_login)

        # Memaksa ke tengah secara vertikal
        layout_utama.addStretch(1)
        layout_utama.addWidget(self.card)
        layout_utama.addStretch(1)

    def apply_input_style(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                background-color: #F9FAFB;
                border: 2px solid #ECF0F1;
                border-radius: 10px;
                padding: 12px;
                padding-right: 35px;
                font-size: 16px;
                color: #2C3E50;
            }
            QLineEdit:focus { border: 2px solid #2C687B; background-color: white; }
        """)

    def handle_login(self):
        user = self.input_user.text().strip()
        pw = self.input_pass.text().strip()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_dir) if os.path.basename(current_dir).lower() == 'login' else current_dir
        json_path = os.path.normpath(os.path.join(base_path, 'database', 'user.json'))

        user_find = False
        user_role = ""

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as file:
                    users = json.load(file)

                    # cari username dan password yang cocok
                    for u in users:
                        if u['username'].lower() == user.lower() and u['password'] == pw:
                            user_find = True
                            user_role = u['role']
                            break
            except Exception as e:
                print(f"Error membaca database user: {e}")

        # Logika login 
        if user_find:
            self.parent_window.current_logged_in_user = user

            if user_role == "admin":
                self.parent_window.show_admin_dashboard()
            else:
                self.parent_window.show_user_dashboard()
        else:
            try:
                from pages.Modul.modul_antarmuka_pengguna import show_message
                show_message(self, "Login Failed", "Username atau password salah!")
            except Exception:
                QMessageBox.warning(self, "Login Failed", "Username atau password salah!")
            
            self.input_user.clear()
            self.input_pass.clear()
            self.input_user.setFocus()

    def toggle_login_password(self):
        if self.password_visible:
            self.input_pass.setEchoMode(QLineEdit.Password)
            self.password_visible = False
            self.toggle_login_password_action.setIcon(self.icon_hidden)
        else:
            self.input_pass.setEchoMode(QLineEdit.Normal)
            self.password_visible = True
            self.toggle_login_password_action.setIcon(self.icon_shown)
            
        self.input_pass.setFocus()