import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QFrame, QStyle)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon

def create_admin_manager_page(router_self):
    page = QWidget()
    page.setStyleSheet("background-color: #F3F4F6;") 
    
    main_layout = QVBoxLayout(page)
    main_layout.setContentsMargins(40, 40, 40, 40)
    main_layout.setSpacing(30)

    # ==========================================
    # HEADER HALAMAN 
    # ==========================================
    header_container = QWidget()
    header_layout = QVBoxLayout(header_container)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(6)

    title = QLabel("Admin Manager")
    title.setFont(QFont("Segoe UI", 26, QFont.Bold))
    title.setStyleSheet("color: #1E3A5F; font-weight: bold; letter-spacing: -0.5px;")
    
    subtitle = QLabel("Kelola hak akses, tambah, edit, atau hapus pengguna dalam sistem GottaJob.")
    subtitle.setFont(QFont("Segoe UI", 11))
    subtitle.setStyleSheet("color: #6B7280;")
    
    header_layout.addWidget(title)
    header_layout.addWidget(subtitle)
    main_layout.addWidget(header_container)

    # Layout Konten Utama
    content_layout = QHBoxLayout()
    content_layout.setSpacing(35)

    # ==========================================
    # KARTU FORM INPUT
    # ==========================================
    form_card = QFrame()
    form_card.setFixedWidth(360)
    form_card.setObjectName("FormCard")
    form_card.setStyleSheet("""
        QFrame#FormCard {
            background-color: white;
            border-radius: 24px;
            border: 1px solid #E5E7EB;
        }
    """)
    
    form_layout = QVBoxLayout(form_card)
    form_layout.setContentsMargins(30, 35, 30, 35)
    form_layout.setSpacing(14)

    router_self.lbl_form_status = QLabel("Tambah User Baru")
    router_self.lbl_form_status.setFont(QFont("Segoe UI", 15, QFont.Bold))
    router_self.lbl_form_status.setStyleSheet("color: #1E3A5F; margin-bottom: 11px; background: transparent; border: none;")
    form_layout.addWidget(router_self.lbl_form_status)

    # Tokenizing Input Style
    label_style = "font-weight: 600; color: #4B5563; font-size: 14px; font-family: 'Segoe UI';"
    input_style = """
        QLineEdit, QComboBox {
            background-color: #F9FAFB;
            border: 1.5px solid #E5E7EB;
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 14px;
            color: #1F2937;
            font-family: 'Segoe UI';
        }
        QLineEdit:focus, QComboBox:focus { 
            border: 2px solid #2C687B; 
            background-color: white; 
        }
        
        /* Stylizasi Khusus QComboBox */
        QComboBox {
            combobox-popup: 0; 
            padding-right: 30px; 
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left-width: 0px; 
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
        }
        QComboBox::down-arrow {
            image: none;
            color: #4B5563;
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: bold;
        }
        QComboBox::down-arrow:on {
            color: #2C687B; 
        }
        
        /* Styling Menu Pop-up Pilihan */
        QComboBox QAbstractItemView {
            background-color: white;
            border: 1.5px solid #E5E7EB;
            border-radius: 12px;
            padding: 6px;
            font-family: 'Segoe UI';
            font-size: 14px;
            color: #1F2937;
            selection-background-color: #F3F4F6; 
            selection-color: #2C687B;
            outline: 0px; 
        }
    """

    # Username
    lbl_username = QLabel("Username")
    lbl_username.setStyleSheet(label_style)
    router_self.txt_username = QLineEdit()
    router_self.txt_username.setPlaceholderText("Masukkan username...")
    router_self.txt_username.setStyleSheet(input_style)
    form_layout.addWidget(lbl_username)
    form_layout.addWidget(router_self.txt_username)

    # Password
    lbl_password = QLabel("Password")
    lbl_password.setStyleSheet(label_style)
    router_self.txt_password = QLineEdit()
    router_self.txt_password.setEchoMode(QLineEdit.Password)
    router_self.txt_password.setPlaceholderText("Masukkan password...")
    router_self.txt_password.setStyleSheet(input_style)
    router_self.password_visible = False
    router_self.icon_hidden = QIcon('assets/hidden.png')
    router_self.icon_shown = QIcon('assets/eye.png')
    router_self.toggle_password_action = router_self.txt_password.addAction(
        router_self.icon_hidden, 
        QLineEdit.TrailingPosition
    )

    router_self.toggle_password_action.triggered.connect(lambda: toggle_password_visibility(router_self))

    form_layout.addWidget(lbl_password)
    form_layout.addWidget(router_self.txt_password)

    # Role
    lbl_role = QLabel("Role")
    lbl_role.setStyleSheet(label_style)
    router_self.cmb_role = QComboBox()
    router_self.cmb_role.addItems(["user", "admin"])
    router_self.cmb_role.setStyleSheet(input_style)
    form_layout.addWidget(lbl_role)
    form_layout.addWidget(router_self.cmb_role)

    router_self.editing_username_target = None 

    # Tombol Utama
    router_self.btn_save_user = QPushButton("Tambah User")
    router_self.btn_save_user.setFont(QFont("Segoe UI", 12, QFont.Bold))
    router_self.btn_save_user.setCursor(Qt.PointingHandCursor)
    router_self.btn_save_user.setStyleSheet("""
        QPushButton {
            background-color: #2C687B;
            color: white;
            padding: 14px;
            border-radius: 12px;
            border: none;
            margin-top: 15px;
        }
        QPushButton:hover { background-color: #225160; }
    """)
    router_self.btn_save_user.clicked.connect(lambda: simpan_user_baru(router_self))
    form_layout.addWidget(router_self.btn_save_user)

    # Tombol Batal
    router_self.btn_cancel_edit = QPushButton("Batal Edit")
    router_self.btn_cancel_edit.setFont(QFont("Segoe UI", 12, QFont.Bold))
    router_self.btn_cancel_edit.setCursor(Qt.PointingHandCursor)
    router_self.btn_cancel_edit.setStyleSheet("""
        QPushButton {
            background-color: #9CA3AF;
            color: white;
            padding: 10px;
            border-radius: 12px;
            border: none;
        }
        QPushButton:hover { background-color: #6B7280; }
    """)
    router_self.btn_cancel_edit.hide()
    router_self.btn_cancel_edit.clicked.connect(lambda: reset_form_state(router_self))
    form_layout.addWidget(router_self.btn_cancel_edit)

    form_layout.addStretch()

    # ==========================================
    # KARTU DATA TABEL USER 
    # ==========================================
    table_card = QFrame()
    table_card.setObjectName("TableCard")
    table_card.setStyleSheet("""
        QFrame#TableCard {
            background-color: white;
            border-radius: 24px;
            border: 1px solid #E5E7EB;
        }
    """)
    
    table_layout = QVBoxLayout(table_card)
    table_layout.setContentsMargins(30, 30, 30, 30)
    table_layout.setSpacing(20)

    table_title = QLabel("Daftar User")
    table_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
    table_title.setStyleSheet("color: #1E3A5F; background: transparent; border: none;")
    table_layout.addWidget(table_title)

    router_self.table_user = QTableWidget()
    router_self.table_user.setColumnCount(3)
    router_self.table_user.setHorizontalHeaderLabels(["Username", "Role", "Aksi"])
    router_self.table_user.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    router_self.table_user.setFocusPolicy(Qt.NoFocus)
    
    router_self.table_user.verticalHeader().setVisible(False) 
    router_self.table_user.setShowGrid(False) 
    router_self.table_user.verticalHeader().setDefaultSectionSize(54) 
    
    router_self.table_user.setStyleSheet("""
        QTableWidget {
            background-color: white;
            color: #374151;
            border: none;
            font-family: 'Segoe UI';
            font-size: 14px;
        }
        QTableWidget::item {
            border-bottom: 1px solid #F3F4F6;
            padding-left: 10px;
        }
        QTableWidget::item:selected {
            background-color: #F3F4F6;
            color: #374151;
        }
        QHeaderView::section {
            background-color: #F9FAFB;
            color: #4B5563;
            padding: 12px;
            font-weight: bold;
            font-size: 15px;
            border: none;
            border-bottom: 2px solid #E5E7EB;
            text-align: left;
        }
    """)
    table_layout.addWidget(router_self.table_user)

    load_data_user_ke_tabel(router_self)
    content_layout.addWidget(form_card)
    content_layout.addWidget(table_card, 1) 
    main_layout.addLayout(content_layout)

    return page


def load_data_user_ke_tabel(router_self):
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(base_path, 'database', 'user.json'))
    
    if not os.path.exists(json_path):
        return

    with open(json_path, 'r') as file:
        users = json.load(file)

    router_self.table_user.setRowCount(0)
    for row_idx, user_data in enumerate(users):
        router_self.table_user.insertRow(row_idx)
        
        # Format Text Item 
        item_user = QTableWidgetItem(f"  {user_data['username']}")
        item_role = QTableWidgetItem(user_data['role'].upper())
        item_user.setTextAlignment(Qt.AlignCenter)
        item_role.setTextAlignment(Qt.AlignCenter)
        item_user.setFont(QFont("Segoe UI", 11, QFont.Medium))
        item_role.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        # Warna teks role agar tidak kaku
        if user_data['role'] == 'admin':
            item_role.setForeground(QColor("#E74C3C")) 
        else:
            item_role.setForeground(QColor("#2C687B")) 
            
        item_user.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_role.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        router_self.table_user.setItem(row_idx, 0, item_user)
        router_self.table_user.setItem(row_idx, 1, item_role)
        
        # Container Tombol Aksi
        action_widget = QWidget()
        action_widget.setStyleSheet("background-color: white; border: none;")
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(10, 0, 10, 0)
        action_layout.setSpacing(10)
        
        btn_edit = QPushButton("Edit")
        btn_edit.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #2C687B; 
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QPushButton:hover { background-color: #225160; }
        """)
        
        btn_delete = QPushButton("Hapus")
        btn_delete.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: #FFFFFF !important;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        
        username_target = user_data['username']
        btn_edit.clicked.connect(lambda checked, u=user_data: aktifkan_mode_edit(router_self, u))
        btn_delete.clicked.connect(lambda checked, u=username_target: hapus_user(router_self, u))
        
        action_layout.addStretch(1)
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addStretch(1)
        action_layout.setAlignment(Qt.AlignCenter) 
        
        router_self.table_user.setCellWidget(row_idx, 2, action_widget)


def aktifkan_mode_edit(router_self, user_data):
    router_self.lbl_form_status.setText("Edit Data User")
    router_self.lbl_form_status.setStyleSheet("color: #D35400; font-weight: bold;") 
    
    router_self.txt_username.setText(user_data['username'])
    router_self.txt_password.setText(user_data['password'])
    
    index_role = router_self.cmb_role.findText(user_data['role'])
    if index_role >= 0:
        router_self.cmb_role.setCurrentIndex(index_role)
        
    router_self.editing_username_target = user_data['username']
    router_self.btn_save_user.setText("Update Data")
    router_self.btn_save_user.setStyleSheet("""
        QPushButton {
            background-color: #D35400;
            color: white;
            padding: 14px;
            border-radius: 12px;
            border: none;
            margin-top: 15px;
        }
        QPushButton:hover { background-color: #A04000; }
    """)
    router_self.btn_cancel_edit.show()


def reset_form_state(router_self):
    router_self.lbl_form_status.setText("Tambah User Baru")
    router_self.lbl_form_status.setStyleSheet("color: #1E3A5F; font-weight: bold;")
    
    router_self.txt_username.clear()
    router_self.txt_password.clear()
    router_self.cmb_role.setCurrentIndex(0)
    
    router_self.editing_username_target = None
    router_self.btn_save_user.setText("Tambah User")
    router_self.btn_save_user.setStyleSheet("""
        QPushButton {
            background-color: #2C687B;
            color: white;
            padding: 14px;
            border-radius: 12px;
            border: none;
            margin-top: 15px;
        }
        QPushButton:hover { background-color: #225160; }
    """)
    router_self.btn_cancel_edit.hide()


def simpan_user_baru(router_self):
    username = router_self.txt_username.text().strip()
    password = router_self.txt_password.text().strip()
    role = router_self.cmb_role.currentText()

    if not username or not password:
        QMessageBox.warning(router_self, "Peringatan", "Username dan Password tidak boleh kosong!")
        return

    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(base_path, 'database', 'user.json'))

    with open(json_path, 'r+') as file:
        users = json.load(file)
        
        if router_self.editing_username_target is not None:
            if username.lower() != router_self.editing_username_target.lower():
                if any(u['username'].lower() == username.lower() for u in users):
                    QMessageBox.warning(router_self, "Gagal", f"Username '{username}' sudah dipakai user lain!")
                    return
            
            for u in users:
                if u['username'].lower() == router_self.editing_username_target.lower():
                    u['username'] = username
                    u['password'] = password
                    u['role'] = role
                    break
                    
            if hasattr(router_self, 'current_logged_in_user') and router_self.current_logged_in_user == router_self.editing_username_target:
                router_self.current_logged_in_user = username

            QMessageBox.information(router_self, "Sukses", "Data pengguna berhasil diperbarui!")

        else:
            if any(u['username'].lower() == username.lower() for u in users):
                QMessageBox.warning(router_self, "Gagal", f"Username '{username}' sudah terdaftar!")
                return

            users.append({"username": username, "password": password, "role": role})
            QMessageBox.information(router_self, "Sukses", f"User '{username}' berhasil ditambahkan!")

        file.seek(0)
        json.dump(users, file, indent=4)
        file.truncate()

    reset_form_state(router_self)
    load_data_user_ke_tabel(router_self)


def hapus_user(router_self, username):
    if hasattr(router_self, 'current_logged_in_user') and username == router_self.current_logged_in_user:
        QMessageBox.critical(router_self, "Gagal", "Anda tidak bisa menghapus akun Anda sendiri yang sedang aktif!")
        return

    reply = QMessageBox.question(router_self, "Konfirmasi", f"Apakah Anda yakin ingin menghapus user '{username}'?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    
    if reply == QMessageBox.Yes:
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.normpath(os.path.join(base_path, 'database', 'user.json'))

        with open(json_path, 'r') as file:
            users = json.load(file)

        users = [u for u in users if u['username'] != username]

        with open(json_path, 'w') as file:
            json.dump(users, file, indent=4)

        QMessageBox.information(router_self, "Sukses", "User berhasil dihapus!")
        
        if router_self.editing_username_target == username:
            reset_form_state(router_self)
            
        load_data_user_ke_tabel(router_self)

def toggle_password_visibility(router_self):
    if router_self.password_visible:
        router_self.txt_password.setEchoMode(QLineEdit.Password)
        router_self.password_visible = False
        router_self.toggle_password_action.setIcon(router_self.icon_hidden)
    else:
        router_self.txt_password.setEchoMode(QLineEdit.Normal)
        router_self.password_visible = True
        router_self.toggle_password_action.setIcon(router_self.icon_shown)

    router_self.txt_password.setFocus()