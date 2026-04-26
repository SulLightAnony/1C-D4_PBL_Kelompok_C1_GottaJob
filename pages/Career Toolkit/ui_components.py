import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu, QAction, QLineEdit, 
                             QTextEdit, QToolButton, QSizePolicy, QTextBrowser)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap

# ==========================================
# 1. KOMPONEN KARTU CV (DASHBOARD)
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
            QFrame#CVCard { background-color: #ffffff; border-radius: 10px; border: 1px solid #e0e0e0; }
            QFrame#CVCard:hover { border: 2px solid #2C687B; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.btn_menu = QToolButton()
        self.btn_menu.setText("⋮")
        self.btn_menu.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_menu.setStyleSheet("border: none; color: #555555;")
        self.btn_menu.setPopupMode(QToolButton.InstantPopup)
        
        self.kebab_menu = QMenu(self)
        self.kebab_menu.setStyleSheet("QMenu { background-color: white; border: 1px solid #ccc; }")
        
        action_dup = QAction("Duplikasi", self)
        action_dup.triggered.connect(lambda: self.duplicate_clicked.emit(self.cv_id))
        action_del = QAction("Hapus", self)
        action_del.triggered.connect(lambda: self.delete_clicked.emit(self.cv_id))
        
        self.kebab_menu.addAction(action_dup)
        self.kebab_menu.addAction(action_del)
        self.btn_menu.setMenu(self.kebab_menu)
        header_layout.addWidget(self.btn_menu)
        layout.addLayout(header_layout)

        self.lbl_thumbnail = QLabel("[Pratinjau CV]")
        self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
        self.lbl_thumbnail.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; color: #888;")
        self.lbl_thumbnail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.lbl_thumbnail)

        self.lbl_title = QLabel(self.cv_name)
        self.lbl_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #333333; border: none;")
        self.lbl_title.setWordWrap(True)
        layout.addWidget(self.lbl_title)

        self.lbl_date = QLabel(f"Diperbarui: {self.last_updated}")
        self.lbl_date.setFont(QFont("Segoe UI", 9))
        self.lbl_date.setStyleSheet("color: #777777; border: none;")
        layout.addWidget(self.lbl_date)

        action_layout = QHBoxLayout()
        self.btn_edit = QPushButton("Edit"); self.btn_edit.setStyleSheet("background-color: #2C687B; color: white; border-radius: 5px; padding: 5px;")
        self.btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.cv_id))
        
        self.btn_print = QPushButton("Cetak"); self.btn_print.setStyleSheet("background-color: #E28F41; color: white; border-radius: 5px; padding: 5px;")
        self.btn_print.clicked.connect(lambda: self.print_clicked.emit(self.cv_id))

        action_layout.addWidget(self.btn_edit)
        action_layout.addWidget(self.btn_print)
        layout.addLayout(action_layout)

# ==========================================
# 2. KOMPONEN FORM PENGALAMAN & PENDIDIKAN
# ==========================================
class ExperienceInputWidget(QFrame):
    delete_requested = pyqtSignal(object)

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #dcdcdc; border-radius: 8px; margin-bottom: 10px;")
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Pengalaman Kerja"); lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_delete = QPushButton("✖ Hapus"); btn_delete.setStyleSheet("color: #cc0000; border: none;")
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self))
        header_layout.addWidget(lbl_title); header_layout.addStretch(); header_layout.addWidget(btn_delete)
        layout.addLayout(header_layout)

        self.input_company = QLineEdit(); self.input_company.setPlaceholderText("Nama Perusahaan")
        self.input_role = QLineEdit(); self.input_role.setPlaceholderText("Jabatan")
        date_layout = QHBoxLayout()
        self.input_start = QLineEdit(); self.input_start.setPlaceholderText("Mulai (Bulan Tahun)")
        self.input_end = QLineEdit(); self.input_end.setPlaceholderText("Selesai")
        date_layout.addWidget(self.input_start); date_layout.addWidget(self.input_end)
        self.input_desc = QTextEdit(); self.input_desc.setPlaceholderText("Deskripsi pekerjaan"); self.input_desc.setFixedHeight(80)

        layout.addWidget(self.input_company); layout.addWidget(self.input_role)
        layout.addLayout(date_layout); layout.addWidget(self.input_desc)

        if data:
            self.input_company.setText(data.get("company", ""))
            self.input_role.setText(data.get("role", ""))
            self.input_start.setText(data.get("start_date", ""))
            self.input_end.setText(data.get("end_date", ""))
            self.input_desc.setPlainText("\n".join(data.get("description", [])))

    def get_data(self):
        desc = [line.strip() for line in self.input_desc.toPlainText().split('\n') if line.strip()]
        return {"company": self.input_company.text(), "role": self.input_role.text(), "start_date": self.input_start.text(), "end_date": self.input_end.text(), "description": desc}

class EducationInputWidget(QFrame):
    delete_requested = pyqtSignal(object)

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #f0f7fb; border: 1px solid #b3d4e6; border-radius: 8px; margin-bottom: 10px;")
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Riwayat Pendidikan"); lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_delete = QPushButton("✖ Hapus"); btn_delete.setStyleSheet("color: #cc0000; border: none;")
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self))
        header_layout.addWidget(lbl_title); header_layout.addStretch(); header_layout.addWidget(btn_delete)
        layout.addLayout(header_layout)

        self.input_institution = QLineEdit(); self.input_institution.setPlaceholderText("Nama Institusi")
        self.input_degree = QLineEdit(); self.input_degree.setPlaceholderText("Gelar / Jurusan")
        row_layout = QHBoxLayout()
        self.input_year = QLineEdit(); self.input_year.setPlaceholderText("Tahun Lulus")
        self.input_gpa = QLineEdit(); self.input_gpa.setPlaceholderText("IPK (opsional)")
        row_layout.addWidget(self.input_year); row_layout.addWidget(self.input_gpa)

        layout.addWidget(self.input_institution); layout.addWidget(self.input_degree); layout.addLayout(row_layout)

        if data:
            self.input_institution.setText(data.get("institution", ""))
            self.input_degree.setText(data.get("degree", ""))
            self.input_year.setText(data.get("year", ""))
            self.input_gpa.setText(data.get("gpa", ""))

    def get_data(self):
        return {"institution": self.input_institution.text(), "degree": self.input_degree.text(), "year": self.input_year.text(), "gpa": self.input_gpa.text()}

# ==========================================
# 3. KARTU PEMILIHAN TEMPLATE
# ==========================================
class TemplateCard(QFrame):
    template_selected = pyqtSignal(str)

    def __init__(self, template_id, template_name, desc, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.template_name = template_name
        self.desc = desc
        
        self.setFixedSize(220, 300)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame { background-color: #ffffff; border-radius: 10px; border: 2px solid #e0e0e0; }
            QFrame:hover { border: 2px solid #2C687B; background-color: #f4f9f9; }
        """)

        layout = QVBoxLayout(self)
        self.lbl_preview = QLabel("Preview Visual")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: #e9ecef; border-radius: 5px; color: #6c757d;")
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.lbl_preview)

        lbl_title = QLabel(self.template_name)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_title.setStyleSheet("border: none; color: #333333;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(self.desc)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setFont(QFont("Segoe UI", 8))
        lbl_desc.setStyleSheet("border: none; color: #777;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.template_selected.emit(self.template_id)

# ==========================================
# 4. KOMPONEN SIMULASI PRATINJAU (PREVIEW WIDGET)
# ==========================================
class CVPreviewWidget(QFrame):
    """Widget untuk menampilkan HTML Preview dari CV sebelum dicetak."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QTextBrowser()
        self.browser.setStyleSheet("border: none; padding: 20px;")
        layout.addWidget(self.browser)

    def render_preview(self, data, template_id):
        """Men-generate HTML string berdasarkan data dan template_id"""
        name = data.get("full_name", "NAMA LENGKAP").upper()
        contacts = " | ".join([data.get(k) for k in ["email", "phone", "linkedin"] if data.get(k)])
        
        # Pengaturan gaya (CSS dasar) berdasarkan Template
        font_family = "Arial, sans-serif"
        color_primary = "#2C687B"
        align_header = "center"
        hr_style = f"border: 1px solid {color_primary};"

        if template_id == "ats_modern":
            font_family = "'Times New Roman', serif"
            color_primary = "#000000"
            hr_style = "border: 1px solid black;"
        elif template_id == "ats_minimalist":
            font_family = "Helvetica, sans-serif"
            color_primary = "#333333"
            align_header = "left"
            hr_style = "border: 0; border-top: 1px solid #e0e0e0;"

        # Merakit HTML
        html = f"<div style=\"font-family: {font_family}; color: #333;\">"
        
        # Header
        html += f"<h1 style=\"color: {color_primary}; text-align: {align_header}; margin-bottom: 2px;\">{name}</h1>"
        html += f"<p style=\"text-align: {align_header}; color: #555; font-size: 12px; margin-top: 0;\">{contacts}</p>"
        
        # Fungsi Helper untuk merender bagian
        def render_section(title, content):
            if not content: return ""
            sec = f"<br><h3 style=\"color: {color_primary}; margin-bottom: 2px;\">{title}</h3>"
            sec += f"<hr style=\"{hr_style}\">"
            sec += content
            return sec

        # Summary
        if data.get("summary"):
            html += render_section("RINGKASAN PROFESIONAL", f"<p style=\"font-size: 13px;\">{data.get('summary')}</p>")
            
        # Education
        edu_html = ""
        for edu in data.get("education", []):
            gpa_text = f" (IPK: {edu.get('gpa')})" if edu.get("gpa") else ""
            edu_html += f"""
            <table width="100%" style="font-size: 13px; margin-bottom: 5px;">
                <tr>
                    <td align="left"><b>{edu.get('institution')}</b></td>
                    <td align="right">{edu.get('year')}</td>
                </tr>
                <tr>
                    <td align="left" colspan="2"><i>{edu.get('degree')}{gpa_text}</i></td>
                </tr>
            </table>
            """
        html += render_section("RIWAYAT PENDIDIKAN", edu_html)

        # Experience
        exp_html = ""
        for exp in data.get("experience", []):
            desc_items = "".join([f"<li>{item}</li>" for item in exp.get("description", [])])
            exp_html += f"""
            <table width="100%" style="font-size: 13px; margin-top: 5px;">
                <tr>
                    <td align="left"><b>{exp.get('role')}</b></td>
                    <td align="right">{exp.get('start_date')} - {exp.get('end_date')}</td>
                </tr>
                <tr>
                    <td align="left" colspan="2"><i>{exp.get('company')}</i></td>
                </tr>
            </table>
            <ul style="font-size: 13px; margin-top: 0;">{desc_items}</ul>
            """
        html += render_section("PENGALAMAN KERJA", exp_html)

        # Skills
        if data.get("skills"):
            skills_joined = ", ".join(data.get("skills", []))
            html += render_section("KEAHLIAN", f"<p style=\"font-size: 13px;\">{skills_joined}</p>")

        html += "</div>"
        
        # Set HTML ke dalam QTextBrowser
        self.browser.setHtml(html)