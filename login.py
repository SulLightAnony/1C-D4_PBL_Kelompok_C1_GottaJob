from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

class LoginPage(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window 
        self.init_ui()

    def init_ui(self):
        # Background utama
        self.setStyleSheet("background-color: #F3F4F6;") 
        
        layout_utama = QVBoxLayout(self)
        layout_utama.setAlignment(Qt.AlignCenter)

        # Kartu Login
        self.card = QFrame()
        self.card.setFixedSize(450, 550)
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 25px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(50, 40, 50, 50)
        card_layout.setSpacing(10)

        # Logo GottaJob
        lbl_logo_img = QLabel()
        pix = QPixmap('assets/logo.png')
        if not pix.isNull():
            lbl_logo_img.setPixmap(pix.scaled(65, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_logo_img.setAlignment(Qt.AlignCenter)
        lbl_logo_img.setStyleSheet("border: none; margin-bottom: 5px;")

        # Title 
        lbl_title = QLabel("Welcome Back")
        lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C687B; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_subtitle = QLabel("Please enter your details")
        lbl_subtitle.setStyleSheet("color: #7F8C8D; font-size: 14px; border: none; margin-bottom: 20px;")
        lbl_subtitle.setAlignment(Qt.AlignCenter)

        # Input Fields Styling
        label_style = "font-weight: bold; color: #34495E; border: none; margin-top: 10px; font-size:14px;"
        
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet(label_style)
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Enter your username")
        self.apply_input_style(self.input_user)
        self.input_user.returnPressed.connect(self.handle_login)

        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet(label_style)
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Enter your password")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.apply_input_style(self.input_pass)
        self.input_pass.returnPressed.connect(self.handle_login)

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

        layout_utama.addWidget(self.card)

    def apply_input_style(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                background-color: #F9FAFB;
                border: 2px solid #ECF0F1;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                color: #2C3E50;
            }
            QLineEdit:focus { border: 2px solid #2C687B; background-color: white; }
        """)

    def handle_login(self):
        user = self.input_user.text().strip()
        pw = self.input_pass.text().strip()

        # Logika login sederhana
        if user == "admin" and pw == "admin123":
            self.parent_window.show_admin_dashboard()
        elif user == "user" and pw == "user123":
            self.parent_window.show_user_dashboard()
        else:
            QMessageBox.warning(self, "Login Failed", "Username atau password salah!")
            self.input_user.clear()
            self.input_pass.clear()
            self.input_user.setFocus()