import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu, QAction, QLineEdit, 
                             QTextEdit, QToolButton, QSizePolicy, QTextBrowser,
                             QFileDialog, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor

# ==========================================
# 1. KARTU CV (DASHBOARD)
# ==========================================
class CVCard(QFrame):
    edit_clicked = pyqtSignal(str)
    print_clicked = pyqtSignal(str)
    duplicate_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(self, cv_data, parent=None):
        super().__init__(parent)
        self.cv_data = cv_data
        self.cv_id = cv_data.get("cv_id", "")
        self.cv_name = cv_data.get("cv_name", "Untitled CV")
        self.last_updated = cv_data.get("last_updated", "")
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(220, 280)
        self.setObjectName("CVCard")
        # UI ENHANCEMENT: Rounded corners, soft border, hover effect
        self.setStyleSheet("""
            QFrame#CVCard { 
                background-color: #ffffff; 
                border-radius: 12px; 
                border: 1px solid #e2e8f0; 
            }
            QFrame#CVCard:hover { 
                border: 2px solid #2C687B; 
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.btn_menu = QToolButton()
        self.btn_menu.setText("⋮")
        self.btn_menu.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_menu.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_menu.setStyleSheet("border: none; color: #64748b; background: transparent;")
        self.btn_menu.setPopupMode(QToolButton.InstantPopup)
        
        self.kebab_menu = QMenu(self)
        self.kebab_menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #cbd5e1; border-radius: 5px; }
            QMenu::item { padding: 5px 20px; }
            QMenu::item:selected { background-color: #f1f5f9; color: #0f172a; }
        """)
        
        action_dup = QAction("Duplikasi", self)
        action_dup.triggered.connect(lambda: self.duplicate_clicked.emit(self.cv_id))
        action_del = QAction("Hapus", self)
        action_del.triggered.connect(lambda: self.delete_clicked.emit(self.cv_id))
        
        self.kebab_menu.addAction(action_dup)
        self.kebab_menu.addAction(action_del)
        self.btn_menu.setMenu(self.kebab_menu)
        header_layout.addWidget(self.btn_menu)
        layout.addLayout(header_layout)

        self.lbl_thumbnail = QLabel("[Data CV]")
        self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
        self.lbl_thumbnail.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; color: #64748b;")
        self.lbl_thumbnail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.lbl_thumbnail)

        self.lbl_title = QLabel(self.cv_name)
        self.lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #1e293b; border: none; background: transparent;")
        self.lbl_title.setWordWrap(True)
        layout.addWidget(self.lbl_title)

        self.lbl_date = QLabel(f"Diperbarui: {self.last_updated}")
        self.lbl_date.setFont(QFont("Segoe UI", 8))
        self.lbl_date.setStyleSheet("color: #94a3b8; border: none; background: transparent;")
        layout.addWidget(self.lbl_date)

        action_layout = QHBoxLayout()
        # Tombol dengan Hover CSS
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_edit.setStyleSheet("""
            QPushButton { background-color: #2C687B; color: white; border-radius: 6px; padding: 6px; }
            QPushButton:hover { background-color: #235362; }
        """)
        self.btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.cv_id))
        
        self.btn_print = QPushButton("Cetak")
        self.btn_print.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_print.setStyleSheet("""
            QPushButton { background-color: #E28F41; color: white; border-radius: 6px; padding: 6px; }
            QPushButton:hover { background-color: #c97a34; }
        """)
        self.btn_print.clicked.connect(lambda: self.print_clicked.emit(self.cv_id))

        action_layout.addWidget(self.btn_edit)
        action_layout.addWidget(self.btn_print)
        layout.addLayout(action_layout)

# ==========================================
# 2. KOMPONEN FOTO (BARU)
# ==========================================
class PhotoUploaderWidget(QFrame):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.photo_path = ""
        self.setStyleSheet("""
            QFrame { background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; }
        """)
        self.init_ui(data)

    def init_ui(self, data):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Kotak Preview
        self.lbl_preview = QLabel("Tidak ada\nFoto")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setFixedSize(80, 100) # Ukuran standar portrait
        self.lbl_preview.setStyleSheet("background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 4px; color: #64748b;")
        layout.addWidget(self.lbl_preview)

        # Kontrol Kanan
        control_layout = QVBoxLayout()
        
        lbl_info = QLabel("<b>Unggah Pas Foto Resmi</b>")
        lbl_info.setStyleSheet("border: none; background: transparent; color: #333;")
        control_layout.addWidget(lbl_info)

        row_btn = QHBoxLayout()
        self.btn_upload = QPushButton("Pilih Foto")
        self.btn_upload.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_upload.setStyleSheet("""
            QPushButton { background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px; padding: 5px; }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_upload.clicked.connect(self.browse_image)
        
        self.combo_ratio = QComboBox()
        self.combo_ratio.addItems(["Rasio 3x4", "Rasio 2x3"])
        self.combo_ratio.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 5px; padding: 4px; background: white;")
        
        row_btn.addWidget(self.btn_upload)
        row_btn.addWidget(self.combo_ratio)
        row_btn.addStretch()
        
        self.btn_remove = QPushButton("Hapus")
        self.btn_remove.setStyleSheet("color: #ef4444; border: none; background: transparent;")
        self.btn_remove.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_remove.clicked.connect(self.remove_image)
        
        control_layout.addLayout(row_btn)
        control_layout.addWidget(self.btn_remove)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)

        # Load data if edit mode
        if data and data.get("path"):
            self.photo_path = data["path"]
            if data.get("ratio") == "2x3":
                self.combo_ratio.setCurrentIndex(1)
            self.update_preview()

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Pas Foto", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.photo_path = path
            self.update_preview()

    def update_preview(self):
        if self.photo_path and os.path.exists(self.photo_path):
            pixmap = QPixmap(self.photo_path)
            # Resize pixmap fit to label
            self.lbl_preview.setPixmap(pixmap.scaled(self.lbl_preview.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.remove_image()

    def remove_image(self):
        self.photo_path = ""
        self.lbl_preview.clear()
        self.lbl_preview.setText("Tidak ada\nFoto")

    def get_data(self):
        return {
            "path": self.photo_path,
            "ratio": "2x3" if self.combo_ratio.currentIndex() == 1 else "3x4"
        }

# ==========================================
# 3. BLOK INPUT DINAMIS (EXPERIENCE, EDUCATION, DLL)
# ==========================================
class BaseInputWidget(QFrame):
    """Kelas dasar agar tidak menulis ulang style rounded corner & tombol hapus."""
    delete_requested = pyqtSignal(object)
    def __init__(self, title, bg_color, border_color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; margin-bottom: 10px; }} QLineEdit, QTextEdit {{ background: white; border: 1px solid #ccc; border-radius: 4px; padding: 5px; }}")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 15)
        
        header = QHBoxLayout()
        lbl_title = QLabel(title); lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold)); lbl_title.setStyleSheet("border: none; background: transparent;")
        btn_delete = QPushButton("✖ Hapus"); btn_delete.setStyleSheet("color: #ef4444; border: none; background: transparent; font-weight: bold;")
        btn_delete.setCursor(QCursor(Qt.PointingHandCursor))
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self))
        header.addWidget(lbl_title); header.addStretch(); header.addWidget(btn_delete)
        self.layout.addLayout(header)

class ExperienceInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Pengalaman Kerja", "#f8fafc", "#e2e8f0", parent)
        self.input_company = QLineEdit(); self.input_company.setPlaceholderText("Nama Perusahaan / Target Tempat")
        self.input_role = QLineEdit(); self.input_role.setPlaceholderText("Jabatan / Peran")
        date_layout = QHBoxLayout()
        self.input_start = QLineEdit(); self.input_start.setPlaceholderText("Mulai (Bulan Tahun)")
        self.input_end = QLineEdit(); self.input_end.setPlaceholderText("Selesai")
        date_layout.addWidget(self.input_start); date_layout.addWidget(self.input_end)
        self.input_desc = QTextEdit(); self.input_desc.setPlaceholderText("Deskripsi pekerjaan & pencapaian"); self.input_desc.setFixedHeight(80)

        self.layout.addWidget(self.input_company); self.layout.addWidget(self.input_role)
        self.layout.addLayout(date_layout); self.layout.addWidget(self.input_desc)

        if data:
            self.input_company.setText(data.get("company", "")); self.input_role.setText(data.get("role", ""))
            self.input_start.setText(data.get("start_date", "")); self.input_end.setText(data.get("end_date", ""))
            self.input_desc.setPlainText("\n".join(data.get("description", [])))

    def get_data(self):
        desc = [line.strip() for line in self.input_desc.toPlainText().split('\n') if line.strip()]
        return {"company": self.input_company.text(), "role": self.input_role.text(), "start_date": self.input_start.text(), "end_date": self.input_end.text(), "description": desc}

class OrganizationInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Pengalaman Organisasi", "#f0fdf4", "#bbf7d0", parent) # Nuansa hijau
        self.input_org = QLineEdit(); self.input_org.setPlaceholderText("Nama Organisasi")
        self.input_role = QLineEdit(); self.input_role.setPlaceholderText("Peran (misal: Ketua Himpunan)")
        date_layout = QHBoxLayout()
        self.input_start = QLineEdit(); self.input_start.setPlaceholderText("Mulai")
        self.input_end = QLineEdit(); self.input_end.setPlaceholderText("Selesai")
        date_layout.addWidget(self.input_start); date_layout.addWidget(self.input_end)
        self.input_desc = QTextEdit(); self.input_desc.setPlaceholderText("Tugas / Pencapaian"); self.input_desc.setFixedHeight(60)

        self.layout.addWidget(self.input_org); self.layout.addWidget(self.input_role)
        self.layout.addLayout(date_layout); self.layout.addWidget(self.input_desc)

        if data:
            self.input_org.setText(data.get("organization", "")); self.input_role.setText(data.get("role", ""))
            self.input_start.setText(data.get("start_date", "")); self.input_end.setText(data.get("end_date", ""))
            self.input_desc.setPlainText("\n".join(data.get("description", [])))

    def get_data(self):
        desc = [line.strip() for line in self.input_desc.toPlainText().split('\n') if line.strip()]
        return {"organization": self.input_org.text(), "role": self.input_role.text(), "start_date": self.input_start.text(), "end_date": self.input_end.text(), "description": desc}

class EducationInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Riwayat Pendidikan", "#eff6ff", "#bfdbfe", parent) # Nuansa biru
        self.input_institution = QLineEdit(); self.input_institution.setPlaceholderText("Nama Institusi")
        self.input_degree = QLineEdit(); self.input_degree.setPlaceholderText("Gelar / Jurusan")
        row_layout = QHBoxLayout()
        self.input_year = QLineEdit(); self.input_year.setPlaceholderText("Tahun Lulus")
        self.input_gpa = QLineEdit(); self.input_gpa.setPlaceholderText("IPK")
        row_layout.addWidget(self.input_year); row_layout.addWidget(self.input_gpa)

        self.layout.addWidget(self.input_institution); self.layout.addWidget(self.input_degree); self.layout.addLayout(row_layout)

        if data:
            self.input_institution.setText(data.get("institution", "")); self.input_degree.setText(data.get("degree", ""))
            self.input_year.setText(data.get("year", "")); self.input_gpa.setText(data.get("gpa", ""))

    def get_data(self):
        return {"institution": self.input_institution.text(), "degree": self.input_degree.text(), "year": self.input_year.text(), "gpa": self.input_gpa.text()}

class CertificationInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Sertifikasi & Penghargaan", "#fef3c7", "#fde68a", parent) # Nuansa kuning/emas
        self.input_name = QLineEdit(); self.input_name.setPlaceholderText("Nama Sertifikasi (misal: AWS Cloud Practitioner)")
        self.input_issuer = QLineEdit(); self.input_issuer.setPlaceholderText("Penerbit (misal: Amazon)")
        self.input_year = QLineEdit(); self.input_year.setPlaceholderText("Tahun")
        
        self.layout.addWidget(self.input_name); self.layout.addWidget(self.input_issuer); self.layout.addWidget(self.input_year)

        if data:
            self.input_name.setText(data.get("name", "")); self.input_issuer.setText(data.get("issuer", ""))
            self.input_year.setText(data.get("year", ""))

    def get_data(self):
        return {"name": self.input_name.text(), "issuer": self.input_issuer.text(), "year": self.input_year.text()}

# ==========================================
# 4. KARTU TEMPLATE & PREVIEW
# ==========================================
class TemplateCard(QFrame):
    template_selected = pyqtSignal(str)

    def __init__(self, template_id, template_name, desc, image_file, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.template_name = template_name
        self.desc = desc
        self.image_file = image_file
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(220, 320)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("""
            QFrame { background-color: #ffffff; border-radius: 12px; border: 2px solid #e2e8f0; }
            QFrame:hover { border: 2px solid #2C687B; background-color: #f8fafc; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Load image from assets/Career Toolkit/
        self.lbl_preview = QLabel("Preview Tidak Ditemukan")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; color: #94a3b8;")
        
        # Cari gambar relatif terhadap file main.py (asumsi running dari root)
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_path = os.path.join(base_path, "assets", "Career Toolkit", self.image_file)
        
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.lbl_preview.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.lbl_preview)

        lbl_title = QLabel(self.template_name)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_title.setStyleSheet("border: none; background: transparent; color: #1e293b;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(self.desc)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setFont(QFont("Segoe UI", 8))
        lbl_desc.setStyleSheet("border: none; background: transparent; color: #64748b;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.template_selected.emit(self.template_id)

class CVPreviewWidget(QFrame):
    """Widget untuk menampilkan HTML Preview (TIDAK BERUBAH)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.browser = QTextBrowser()
        self.browser.setStyleSheet("border: none; padding: 20px;")
        layout.addWidget(self.browser)

    def render_preview(self, data, template_id):
        # [KODE RENDER HTML LAMA TETAP SAMA]
        # (Kita akan perbarui render preview ini nanti untuk memuat foto dan section baru)
        self.browser.setHtml(f"<h3>Memuat pratinjau data untuk {data.get('full_name', '')}...</h3><p>Template: {template_id}</p>")