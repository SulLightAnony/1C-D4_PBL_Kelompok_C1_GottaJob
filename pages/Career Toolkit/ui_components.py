import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu, QAction, QLineEdit, 
                             QTextEdit, QToolButton, QSizePolicy, QTextBrowser,
                             QFileDialog, QComboBox, QDateEdit, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor

# ==========================================
# KOMPONEN KECIL & HELPER
# ==========================================
class ClickableLabel(QLabel):
    """Label yang bisa diklik (berperan seperti tombol)."""
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class DateRangeWidget(QWidget):
    """Komponen khusus untuk kalender Mulai - Selesai dengan Kalender Popup."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Menerapkan JDate experience dengan setCalendarPopup(True)
        self.start_date = QDateEdit()
        self.start_date.setDisplayFormat("MM/yyyy")
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True) 
        self.start_date.setMinimumWidth(110) # Agar teks tidak terpotong
        self.start_date.setStyleSheet("background: white; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px;")
        
        self.end_date = QDateEdit()
        self.end_date.setDisplayFormat("MM/yyyy")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumWidth(110) # Agar teks tidak terpotong
        self.end_date.setStyleSheet("background: white; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px;")
        
        self.chk_present = QCheckBox("Sekarang")
        self.chk_present.stateChanged.connect(self.toggle_end_date)
        
        layout.addWidget(QLabel("Mulai:"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("Selesai:"))
        layout.addWidget(self.end_date)
        layout.addWidget(self.chk_present)
        layout.addStretch()
        
    def toggle_end_date(self, state):
        self.end_date.setDisabled(state == Qt.Checked)
        
    def get_start_date(self):
        return self.start_date.date().toString("MM/yyyy")
        
    def get_end_date(self):
        if self.chk_present.isChecked():
            return "Sekarang"
        return self.end_date.date().toString("MM/yyyy")
        
    def set_dates(self, start_str, end_str):
        if start_str:
            d = QDate.fromString(start_str, "MM/yyyy")
            if d.isValid(): self.start_date.setDate(d)
        if end_str == "Sekarang":
            self.chk_present.setChecked(True)
        elif end_str:
            d = QDate.fromString(end_str, "MM/yyyy")
            if d.isValid(): self.end_date.setDate(d)

class CompactInputWidget(QFrame):
    """Widget kecil dinamis untuk Skill dan Bahasa (1 Baris)."""
    delete_requested = pyqtSignal(object)
    def __init__(self, placeholder, data=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background: white; border: 1px solid #cbd5e1; border-radius: 6px; margin-bottom: 5px; } QLineEdit { border: none; padding: 5px; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        
        self.btn_delete = QPushButton()
        self.btn_delete.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_delete.setStyleSheet("border: none; background: transparent;")
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_path, "assets", "Career Toolkit", "icon-delete.png")
        if os.path.exists(icon_path):
            self.btn_delete.setIcon(QIcon(icon_path))
        else:
            self.btn_delete.setText("✖")
            self.btn_delete.setStyleSheet("color: red; border: none;")
            
        self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self))
        
        layout.addWidget(self.input_field)
        layout.addWidget(self.btn_delete)
        if data: self.input_field.setText(data)
            
    def get_data(self):
        return self.input_field.text()


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
        self.setStyleSheet("""
            QFrame#CVCard { background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }
            QFrame#CVCard:hover { border: 2px solid #2C687B; background-color: #f8fafc; }
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
        self.kebab_menu.setStyleSheet("QMenu { background-color: white; border: 1px solid #cbd5e1; border-radius: 5px; } QMenu::item { padding: 5px 20px; } QMenu::item:selected { background-color: #f1f5f9; }")
        
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
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_edit.setStyleSheet("QPushButton { background-color: #2C687B; color: white; border-radius: 6px; padding: 6px; } QPushButton:hover { background-color: #235362; }")
        self.btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.cv_id))
        
        self.btn_print = QPushButton("Cetak")
        self.btn_print.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_print.setStyleSheet("QPushButton { background-color: #E28F41; color: white; border-radius: 6px; padding: 6px; } QPushButton:hover { background-color: #c97a34; }")
        self.btn_print.clicked.connect(lambda: self.print_clicked.emit(self.cv_id))

        action_layout.addWidget(self.btn_edit)
        action_layout.addWidget(self.btn_print)
        layout.addLayout(action_layout)

# ==========================================
# 2. KOMPONEN FOTO (FIXED LAYOUT)
# ==========================================
class PhotoUploaderWidget(QFrame):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.photo_path = ""
        self.setStyleSheet("QFrame { background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; }")
        self.init_ui(data)

    def init_ui(self, data):
        # Menggunakan layout horizontal rata kiri agar semuanya rapi
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 1. Label Pratinjau Foto
        self.lbl_preview = ClickableLabel("Tidak ada\nfoto")
        self.lbl_preview.setFont(QFont("Segoe UI", 8))
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setFixedSize(90, 120) # Default 3x4
        self.lbl_preview.setCursor(QCursor(Qt.PointingHandCursor))
        self.lbl_preview.setStyleSheet("background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 4px; color: #64748b;")
        self.lbl_preview.clicked.connect(self.browse_image)
        layout.addWidget(self.lbl_preview)
        
        # 2. Icon Tong Sampah (Di sebelah kanan foto)
        self.btn_remove = QPushButton()
        self.btn_remove.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_remove.setStyleSheet("border: none; background: transparent;")
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_path, "assets", "Career Toolkit", "icon-delete.png")
        if os.path.exists(icon_path):
            self.btn_remove.setIcon(QIcon(icon_path))
        else:
            self.btn_remove.setText("✖")
            self.btn_remove.setStyleSheet("color: red; border: none;")
        self.btn_remove.clicked.connect(self.remove_image)
        layout.addWidget(self.btn_remove, alignment=Qt.AlignBottom) # Sejajar di bawah
        
        layout.addSpacing(20) # Jarak antara foto+icon dengan kontrol info
        
        # 3. Kontrol Informasi (Tetap di kiri, sebelah icon sampah)
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignTop)
        
        lbl_info = QLabel("<b>Unggah Pas Foto Resmi</b><br><span style='font-size: 11px; color: #666;'>Klik kotak abu-abu di samping untuk memilih foto.</span>")
        lbl_info.setStyleSheet("border: none; background: transparent; color: #333;")
        
        self.combo_ratio = QComboBox()
        self.combo_ratio.addItems(["Rasio 3x4", "Rasio 2x3"])
        self.combo_ratio.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 5px; padding: 4px; background: white; max-width: 150px;")
        self.combo_ratio.currentIndexChanged.connect(self.change_ratio)
        
        info_layout.addWidget(lbl_info)
        info_layout.addWidget(self.combo_ratio)
        layout.addLayout(info_layout)

        if data and data.get("path"):
            self.photo_path = data["path"]
            if data.get("ratio") == "2x3":
                self.combo_ratio.setCurrentIndex(1)
            self.update_preview()

    def change_ratio(self):
        if self.combo_ratio.currentIndex() == 1: # 2x3
            self.lbl_preview.setFixedSize(80, 120)
        else: # 3x4
            self.lbl_preview.setFixedSize(90, 120)
        self.update_preview() # Wajib dipanggil agar gambar melakukan re-scale

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Pas Foto", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.photo_path = path
            self.update_preview()

    def update_preview(self):
        if self.photo_path and os.path.exists(self.photo_path):
            pixmap = QPixmap(self.photo_path)
            self.lbl_preview.setPixmap(pixmap.scaled(self.lbl_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            self.remove_image()

    def remove_image(self):
        self.photo_path = ""
        self.lbl_preview.clear()
        self.lbl_preview.setText("Tidak ada\nfoto")

    def get_data(self):
        return {"path": self.photo_path, "ratio": "2x3" if self.combo_ratio.currentIndex() == 1 else "3x4"}


# ==========================================
# 3. BLOK INPUT DINAMIS PENGALAMAN DLL
# ==========================================
class BaseInputWidget(QFrame):
    delete_requested = pyqtSignal(object)
    def __init__(self, title, bg_color, border_color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; margin-bottom: 10px; }} QLineEdit, QTextEdit {{ background: white; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; }}")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 15)
        
        header = QHBoxLayout()
        lbl_title = QLabel(title); lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold)); lbl_title.setStyleSheet("border: none; background: transparent;")
        
        self.btn_delete = QPushButton()
        self.btn_delete.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_delete.setStyleSheet("border: none; background: transparent;")
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_path, "assets", "Career Toolkit", "icon-delete.png")
        if os.path.exists(icon_path):
            self.btn_delete.setIcon(QIcon(icon_path))
        else:
            self.btn_delete.setText("✖")
            self.btn_delete.setStyleSheet("color: red; border: none;")
            
        self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self))
        
        header.addWidget(lbl_title); header.addStretch(); header.addWidget(self.btn_delete)
        self.layout.addLayout(header)

class ExperienceInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Pengalaman Kerja", "#f8fafc", "#e2e8f0", parent)
        self.input_company = QLineEdit(); self.input_company.setPlaceholderText("Nama Perusahaan / Target Tempat")
        self.input_role = QLineEdit(); self.input_role.setPlaceholderText("Jabatan / Peran")
        self.date_picker = DateRangeWidget()
        self.input_desc = QTextEdit(); self.input_desc.setPlaceholderText("Deskripsi pekerjaan & pencapaian"); self.input_desc.setFixedHeight(80)

        self.layout.addWidget(self.input_company); self.layout.addWidget(self.input_role)
        self.layout.addWidget(self.date_picker); self.layout.addWidget(self.input_desc)

        if data:
            self.input_company.setText(data.get("company", "")); self.input_role.setText(data.get("role", ""))
            self.date_picker.set_dates(data.get("start_date", ""), data.get("end_date", ""))
            self.input_desc.setPlainText("\n".join(data.get("description", [])))

    def get_data(self):
        desc = [line.strip() for line in self.input_desc.toPlainText().split('\n') if line.strip()]
        return {"company": self.input_company.text(), "role": self.input_role.text(), "start_date": self.date_picker.get_start_date(), "end_date": self.date_picker.get_end_date(), "description": desc}

class OrganizationInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Pengalaman Organisasi", "#f0fdf4", "#bbf7d0", parent)
        self.input_org = QLineEdit(); self.input_org.setPlaceholderText("Nama Organisasi")
        self.input_role = QLineEdit(); self.input_role.setPlaceholderText("Peran (misal: Ketua Himpunan)")
        self.date_picker = DateRangeWidget()
        self.input_desc = QTextEdit(); self.input_desc.setPlaceholderText("Tugas / Pencapaian"); self.input_desc.setFixedHeight(60)

        self.layout.addWidget(self.input_org); self.layout.addWidget(self.input_role)
        self.layout.addWidget(self.date_picker); self.layout.addWidget(self.input_desc)

        if data:
            self.input_org.setText(data.get("organization", "")); self.input_role.setText(data.get("role", ""))
            self.date_picker.set_dates(data.get("start_date", ""), data.get("end_date", ""))
            self.input_desc.setPlainText("\n".join(data.get("description", [])))

    def get_data(self):
        desc = [line.strip() for line in self.input_desc.toPlainText().split('\n') if line.strip()]
        return {"organization": self.input_org.text(), "role": self.input_role.text(), "start_date": self.date_picker.get_start_date(), "end_date": self.date_picker.get_end_date(), "description": desc}

class EducationInputWidget(BaseInputWidget):
    def __init__(self, data=None, parent=None):
        super().__init__("Riwayat Pendidikan", "#eff6ff", "#bfdbfe", parent)
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
        super().__init__("Sertifikasi & Penghargaan", "#fef3c7", "#fde68a", parent)
        self.input_name = QLineEdit(); self.input_name.setPlaceholderText("Nama Sertifikasi")
        self.input_issuer = QLineEdit(); self.input_issuer.setPlaceholderText("Penerbit")
        self.input_year = QLineEdit(); self.input_year.setPlaceholderText("Tahun")
        self.input_desc = QTextEdit(); self.input_desc.setPlaceholderText("Deskripsi (Opsional)"); self.input_desc.setFixedHeight(50)
        
        self.layout.addWidget(self.input_name); self.layout.addWidget(self.input_issuer)
        self.layout.addWidget(self.input_year); self.layout.addWidget(self.input_desc)

        if data:
            self.input_name.setText(data.get("name", "")); self.input_issuer.setText(data.get("issuer", ""))
            self.input_year.setText(data.get("year", ""))
            self.input_desc.setPlainText(data.get("description", ""))

    def get_data(self):
        return {"name": self.input_name.text(), "issuer": self.input_issuer.text(), "year": self.input_year.text(), "description": self.input_desc.toPlainText()}

# ==========================================
# 4. KARTU TEMPLATE & PREVIEW
# ==========================================
class TemplateCard(QFrame):
    template_selected = pyqtSignal(str)
    def __init__(self, template_id, template_name, desc, image_file, parent=None):
        super().__init__(parent)
        self.template_id = template_id; self.template_name = template_name; self.desc = desc; self.image_file = image_file
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(220, 320)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 12px; border: 2px solid #e2e8f0; } QFrame:hover { border: 2px solid #2C687B; background-color: #f8fafc; }")
        layout = QVBoxLayout(self); layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_preview = QLabel("Preview Tidak Ditemukan")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; color: #94a3b8;")
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_path = os.path.join(base_path, "assets", "Career Toolkit", self.image_file)
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.lbl_preview.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.lbl_preview)

        lbl_title = QLabel(self.template_name); lbl_title.setAlignment(Qt.AlignCenter); lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold)); lbl_title.setStyleSheet("border: none; background: transparent; color: #1e293b;")
        layout.addWidget(lbl_title)
        lbl_desc = QLabel(self.desc); lbl_desc.setAlignment(Qt.AlignCenter); lbl_desc.setFont(QFont("Segoe UI", 8)); lbl_desc.setStyleSheet("border: none; background: transparent; color: #64748b;"); lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.template_selected.emit(self.template_id)

class CVPreviewWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar Zoom
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(10, 10, 10, 10)
        lbl_info = QLabel("Gunakan <b>Ctrl + Scroll Mouse</b> untuk memperbesar/memperkecil kanvas A4.")
        lbl_info.setStyleSheet("color: #475569; font-size: 13px; border: none;")
        toolbar.addWidget(lbl_info)
        toolbar.addStretch()
        
        self.btn_zoom_out = QPushButton("Zoom -")
        self.btn_zoom_in = QPushButton("Zoom +")
        for btn in [self.btn_zoom_in, self.btn_zoom_out]:
            btn.setStyleSheet("background: white; border: 1px solid #cbd5e1; padding: 5px 10px; border-radius: 4px;")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            toolbar.addWidget(btn)
            
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)

        self.browser = QTextBrowser()
        # Matikan Interaksi Teks (Non-Selectable)
        self.browser.setTextInteractionFlags(Qt.NoTextInteraction)
        self.browser.setStyleSheet("background-color: transparent; border: none;")
        
        layout.addLayout(toolbar)
        layout.addWidget(self.browser)

    def zoom_in(self): self.browser.zoomIn(1)
    def zoom_out(self): self.browser.zoomOut(1)

    def render_preview(self, data, template_id):
        name = data.get("full_name", "NAMA LENGKAP").upper()
        contacts = " | ".join([data.get(k) for k in ["email", "phone", "linkedin"] if data.get(k)])
        
        font_family = "Arial, sans-serif"; color_primary = "#2C687B"; align_header = "center"
        if template_id == "ats_modern": font_family = "'Times New Roman', serif"; color_primary = "#000000"
        elif template_id == "ats_minimalist": font_family = "Helvetica, sans-serif"; color_primary = "#333333"; align_header = "left"

        photo_html = ""
        photo_data = data.get("photo", {})
        photo_path = photo_data.get("path", "")
        if photo_path and os.path.exists(photo_path):
            img_uri = photo_path.replace('\\', '/')
            # Dimensi absolut untuk foto, mengunci proporsinya!
            img_w = "113px"
            img_h = "151px" if photo_data.get("ratio") == "3x4" else "170px"
            
            photo_html = f'<img src="file:///{img_uri}" width="{img_w}" height="{img_h}" style="position: absolute; right: 40px; top: 40px; border: 1px solid #ccc;">'

        # KANVAS A4 (Terkunci pada 794px x 1123px, Mencegah elemen berantakan)
        html = f'''
        <div style="width: 794px; min-height: 1123px; margin: 0 auto; background-color: white; padding: 40px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); box-sizing: border-box; position: relative; pointer-events: none; user-select: none;">
            <div style="font-family: {font_family}; color: #333;">
                {photo_html}
                <div style="margin-right: 130px;">
                    <h1 style="color: {color_primary}; text-align: {align_header}; margin-bottom: 2px;">{name}</h1>
                    <p style="text-align: {align_header}; color: #555; font-size: 13px; margin-top: 0;">{contacts}</p>
                </div>
        '''
        
        def render_section(title, content):
            if not content: return ""
            style_hr = f"border: 0; border-top: 2px solid {color_primary}; margin-bottom: 5px;" if template_id != "ats_minimalist" else "border: 0; border-top: 1px solid #ccc;"
            return f'<br><h3 style="color: {color_primary}; margin-bottom: 2px;">{title}</h3><hr style="{style_hr}">{content}'

        if data.get("summary"): html += render_section("RINGKASAN PROFESIONAL", f'<p style="font-size: 14px;">{data.get("summary")}</p>')
            
        edu_html = ""
        for edu in data.get("education", []):
            gpa_text = f" (IPK: {edu.get('gpa')})" if edu.get("gpa") else ""
            edu_html += f'<table width="100%" style="font-size: 14px; margin-bottom: 5px;"><tr><td align="left"><b>{edu.get("institution")}</b></td><td align="right">{edu.get("year")}</td></tr><tr><td align="left" colspan="2"><i>{edu.get("degree")}{gpa_text}</i></td></tr></table>'
        html += render_section("RIWAYAT PENDIDIKAN", edu_html)

        exp_html = ""
        for exp in data.get("experience", []):
            desc_items = "".join([f"<li>{item}</li>" for item in exp.get("description", [])])
            exp_html += f'<table width="100%" style="font-size: 14px; margin-top: 5px;"><tr><td align="left"><b>{exp.get("role")}</b></td><td align="right">{exp.get("start_date")} - {exp.get("end_date")}</td></tr><tr><td align="left" colspan="2"><i>{exp.get("company")}</i></td></tr></table><ul style="font-size: 14px; margin-top: 0;">{desc_items}</ul>'
        html += render_section("PENGALAMAN KERJA", exp_html)

        org_html = ""
        for org in data.get("organizations", []):
            desc_items = "".join([f"<li>{item}</li>" for item in org.get("description", [])])
            org_html += f'<table width="100%" style="font-size: 14px; margin-top: 5px;"><tr><td align="left"><b>{org.get("role")}</b></td><td align="right">{org.get("start_date")} - {org.get("end_date")}</td></tr><tr><td align="left" colspan="2"><i>{org.get("organization")}</i></td></tr></table><ul style="font-size: 14px; margin-top: 0;">{desc_items}</ul>'
        html += render_section("PENGALAMAN ORGANISASI", org_html)

        cert_html = ""
        for cert in data.get("certifications", []):
            desc = f'<br><span style="font-size: 13px;">{cert.get("description")}</span>' if cert.get("description") else ""
            cert_html += f'<table width="100%" style="font-size: 14px; margin-bottom: 5px;"><tr><td align="left"><b>{cert.get("name")}</b></td><td align="right">{cert.get("year")}</td></tr><tr><td align="left" colspan="2"><i>Penerbit: {cert.get("issuer")}</i>{desc}</td></tr></table>'
        html += render_section("SERTIFIKASI & PENGHARGAAN", cert_html)

        if data.get("skills"):
            html += render_section("KEAHLIAN / ALAT", f'<p style="font-size: 14px;">{", ".join(data.get("skills", []))}</p>')
        if data.get("languages"):
            html += render_section("BAHASA", f'<p style="font-size: 14px;">{", ".join(data.get("languages", []))}</p>')

        html += "</div></div>"
        self.browser.setHtml(html)