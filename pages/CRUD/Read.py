import os
import sys
import json
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QGridLayout, QFrame, QDialog, QComboBox, 
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QIcon, QPixmap, QDesktopServices

_crud_dir = os.path.dirname(os.path.abspath(__file__))
_pages_dir = os.path.dirname(_crud_dir)
_job_posting_dir = os.path.join(_pages_dir, "Job Posting")
_modul_dir = os.path.join(_pages_dir, "Modul")

for _p in [_pages_dir, _job_posting_dir, _modul_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from constants import (
    company_icon_path, location_detail_icon_path, edit_icon_path, 
    trash_icon_path, send_icon_path, checked_icon_path, 
    currency_icon_path, calendar_icon_path, suitcase_icon_path, 
    link_icon_path, green_check_icon_path
)
from modul_antarmuka_pengguna import ActionButton, SkillTag, MODERN_BUTTON_STYLE
from flow_layout import FlowLayout

class JobDetailPage(QWidget):
    back_clicked = pyqtSignal()
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(dict)
    lamar_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.job_data = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet("background-color: white;")

        # ── Header Section (#1D4E5F) ──
        self.header = QFrame()
        self.header.setFixedHeight(200)
        self.header.setStyleSheet("background-color: #1D4E5F; border: none;")
        h_layout = QVBoxLayout(self.header)
        h_layout.setContentsMargins(30, 20, 30, 25)

        # Tombol Kembali
        back_row = QHBoxLayout()
        self.btn_back = QPushButton("← Kembali")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("color: #9FE1CB; border: none; font-size: 14px; font-weight: bold; background: transparent;")
        self.btn_back.clicked.connect(lambda: self.back_clicked.emit())
        back_row.addWidget(self.btn_back)
        back_row.addStretch()
        h_layout.addLayout(back_row)
        h_layout.addStretch()

        # Judul & Meta
        self.lbl_title = QLabel("Job Title")
        self.lbl_title.setFont(QFont("Segoe UI", 20, QFont.Medium))
        self.lbl_title.setStyleSheet("color: white; border: none; background: transparent;")
        self.lbl_title.setWordWrap(True)
        h_layout.addWidget(self.lbl_title)

        self.meta_info_layout = QHBoxLayout()
        self.meta_info_layout.setSpacing(20)
        
        def create_meta_label(icon_path):
            container = QWidget()
            container.setStyleSheet("background: transparent; border: none;")
            lay = QHBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(8)
            
            icon_lbl = QLabel()
            pix = QPixmap(icon_path)
            if not pix.isNull():
                icon_lbl.setPixmap(pix.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            text_lbl = QLabel("-")
            text_lbl.setStyleSheet("color: #9FE1CB; font-size: 14px; font-weight: 500; border: none; background: transparent;")
            
            lay.addWidget(icon_lbl)
            lay.addWidget(text_lbl)
            return container, text_lbl

        self.widget_perusahaan, self.lbl_perusahaan = create_meta_label(company_icon_path)
        self.widget_lokasi, self.lbl_lokasi = create_meta_label(location_detail_icon_path)
        
        self.meta_info_layout.addWidget(self.widget_perusahaan)
        self.meta_info_layout.addWidget(self.widget_lokasi)
        self.meta_info_layout.addStretch()
        h_layout.addLayout(self.meta_info_layout)

        # Badges
        self.badge_layout = QHBoxLayout()
        self.badge_layout.setSpacing(8)
        h_layout.addLayout(self.badge_layout)

        layout.addWidget(self.header)

        # ── Content Area ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: white;")
        
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(30, 30, 30, 30)
        c_lay.setSpacing(25)

        # Meta Grid (2x2)
        self.meta_grid = QGridLayout()
        self.meta_grid.setSpacing(15)
        c_lay.addLayout(self.meta_grid)

        def add_divider():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("background-color: #f0f0f0; border: none; height: 1px;")
            c_lay.addWidget(line)

        add_divider()

        # Deskripsi
        c_lay.addWidget(self._create_section_lbl("DESKRIPSI PEKERJAAN"))
        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #4A5568; font-size: 16px; line-height: 160%; border: none;")
        c_lay.addWidget(self.lbl_desc)

        add_divider()

        # Hard Skills
        c_lay.addWidget(self._create_section_lbl("HARD SKILLS"))
        self.h_skills_container = QWidget()
        self.h_skills_flow = FlowLayout(self.h_skills_container, margin=0, spacing=8, uniform_width=False)
        c_lay.addWidget(self.h_skills_container)

        c_lay.addSpacing(10)

        # Soft Skills
        c_lay.addWidget(self._create_section_lbl("SOFT SKILLS"))
        self.s_skills_container = QWidget()
        self.s_skills_flow = FlowLayout(self.s_skills_container, margin=0, spacing=8, uniform_width=False)
        c_lay.addWidget(self.s_skills_container)

        add_divider()

        # Benefit & Kualifikasi
        bk_row = QHBoxLayout()
        bk_row.setSpacing(40)
        bk_row.setAlignment(Qt.AlignTop)
        
        self.lay_benefit = QVBoxLayout()
        self.lay_benefit.setSpacing(12)
        self.lay_benefit.addWidget(self._create_section_lbl("BENEFIT PEKERJAAN"))
        bk_row.addLayout(self.lay_benefit, 1)
        bk_row.setAlignment(self.lay_benefit, Qt.AlignTop)

        self.lay_kual = QVBoxLayout()
        self.lay_kual.setSpacing(12)
        self.lay_kual.addWidget(self._create_section_lbl("KUALIFIKASI & PERSYARATAN"))
        bk_row.addLayout(self.lay_kual, 1)
        bk_row.setAlignment(self.lay_kual, Qt.AlignTop)

        c_lay.addLayout(bk_row)
        c_lay.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # ── Footer Bar ──
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("background-color: white; border-top: 1px solid #eee;")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(30, 0, 30, 0)

        self.btn_edit = QPushButton(" Edit")
        self.btn_edit.setIcon(QIcon(edit_icon_path))
        self.btn_edit.setIconSize(QSize(18, 18))
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setFixedSize(100, 40)
        self.btn_edit.setStyleSheet("""
            QPushButton { border: 1px solid #D1D5DB; border-radius: 8px; color: #4A5568; font-weight: 500; }
            QPushButton:hover { background-color: #F9FAFB; border-color: #9CA3AF; }
        """)
        
        self.btn_delete = ActionButton(" Hapus", icon_path=trash_icon_path, color_theme="danger")
        self.btn_delete.setFixedSize(100, 40)
        
        self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.job_data))
        self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.job_data))
        
        f_lay.addWidget(self.btn_edit)
        f_lay.addWidget(self.btn_delete)
        f_lay.addStretch()

        self.btn_lamar = QPushButton("Lamar Sekarang")
        self.btn_lamar.setIcon(QIcon(send_icon_path))
        self.btn_lamar.setIconSize(QSize(18, 18))
        self.btn_lamar.setFixedSize(220, 46)
        self.btn_lamar.setCursor(Qt.PointingHandCursor)
        self.btn_lamar.setStyleSheet("""
            QPushButton { background-color: #1D4E5F; color: white; border-radius: 10px; font-weight: bold; font-size: 14px; border: none; }
            QPushButton:hover { background-color: #2C687B; }
            QPushButton:disabled { background-color: #E2EFF1; color: #2C687B; border: 1px solid #B2D2D9; }
        """)
        self.btn_lamar.clicked.connect(lambda: self.lamar_requested.emit(self.job_data))
        f_lay.addWidget(self.btn_lamar)
        f_lay.addStretch()

        layout.addWidget(footer)

    def _create_section_lbl(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #718096; font-size: 11px; font-weight: 600; text-transform: uppercase; border: none;")
        return lbl

    def _create_meta_item(self, label, value, icon_path=None, is_link=False):
        box = QFrame()
        box.setStyleSheet("background-color: #F8FAFC; border-radius: 10px; border: 1px solid #F1F5F9;")
        box.setFixedHeight(65)
        lay = QHBoxLayout(box)
        lay.setContentsMargins(15, 0, 15, 0)
        lay.setSpacing(12)

        if icon_path:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(QPixmap(icon_path).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            lay.addWidget(icon_lbl)

        v = QVBoxLayout()
        v.setSpacing(2)
        v.setAlignment(Qt.AlignCenter)
        
        l_lbl = QLabel(label)
        l_lbl.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 600; text-transform: uppercase; border: none; background: transparent;")
        v.addWidget(l_lbl)

        v_lbl = QLabel(str(value))
        color = "#F39C12" if "Gaji" in label else "#1E293B"
        v_lbl.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700; border: none; background: transparent;")
        
        if is_link and value != "-":
            v_lbl.setCursor(Qt.PointingHandCursor)
            v_lbl.setStyleSheet("color: #1D4E5F; font-size: 16px; font-weight: 700; text-decoration: underline; border: none; background: transparent;")
            v_lbl.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl(value))
            
        v.addWidget(v_lbl)
        lay.addLayout(v)
        lay.addStretch()
        return box

    def _populate_list(self, layout, items_str):
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        
        items = [i.strip() for i in items_str.split("|") if i.strip()]
        if not items:
            l = QLabel("Tidak ada data")
            l.setStyleSheet("color: #94A3B8; font-style: italic; font-size: 16px; border: none;")
            layout.addWidget(l)
            return

        for text in items:
            row = QHBoxLayout()
            row.setSpacing(10)
            check = QLabel()
            pix = QPixmap(green_check_icon_path)
            if not pix.isNull():
                check.setPixmap(pix.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            check.setStyleSheet("border: none; background: transparent; margin-top: 2px;")
            row.addWidget(check, 0, Qt.AlignTop)
            
            t_lbl = QLabel(text)
            t_lbl.setWordWrap(True)
            t_lbl.setStyleSheet("color: #334155; font-size: 16px; line-height: 120%; border: none; padding: 0px;")
            row.addWidget(t_lbl, 1)
            layout.addLayout(row)
        
        layout.addStretch()
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def setData(self, data):
        self.job_data = data
        self.lbl_title.setText(data.get("Judul_Pekerjaan", "Detail Lowongan"))
        self.lbl_perusahaan.setText(data.get("Nama_Perusahaan", "-"))
        self.lbl_lokasi.setText(data.get("Lokasi", "-"))

        while self.badge_layout.count():
            item = self.badge_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        badge_style = "border: 1px solid rgba(255,255,255,0.4); background-color: transparent; color: white; border-radius: 20px; padding: 4px 16px; font-size: 11px; font-weight: 600;"
        
        for b in [data.get("Jenis_Pekerjaan"), data.get("Kategori")]:
            if b:
                lbl = QLabel(b)
                lbl.setStyleSheet(badge_style)
                self.badge_layout.addWidget(lbl)

        try:
            d_str = data.get("Tanggal_Kadaluarsa", "")
            d = datetime.datetime.strptime(d_str, "%d/%m/%Y").date()
            diff = (d - datetime.date.today()).days
            sisa_text = f"Sisa {max(0, diff)} hari" if diff >= 0 else "Berakhir"
        except:
            sisa_text = "Sisa - hari"
            
        self.lbl_sisa_badge = QLabel(sisa_text)
        self.lbl_sisa_badge.setStyleSheet(badge_style)
        self.badge_layout.addWidget(self.lbl_sisa_badge)
        
        self.badge_layout.addStretch()

        while self.meta_grid.count():
            item = self.meta_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        self.meta_grid.addWidget(self._create_meta_item("Rentang Gaji", data.get("Rentang_Gaji", "-"), currency_icon_path), 0, 0)
        self.meta_grid.addWidget(self._create_meta_item("Tanggal Kadaluarsa", data.get("Tanggal_Kadaluarsa", "-"), calendar_icon_path), 0, 1)
        self.meta_grid.addWidget(self._create_meta_item("Jenis Pekerjaan", data.get("Jenis_Pekerjaan", "-"), suitcase_icon_path), 1, 0)
        self.meta_grid.addWidget(self._create_meta_item("Link Lowongan", data.get("Link_Lowongan", "-") or "-", icon_path=link_icon_path, is_link=True), 1, 1)

        desc = data.get("Deskripsi_Pekerjaan", "").strip()
        self.lbl_desc.setText(desc if desc else "Tidak ada deskripsi tersedia untuk lowongan ini.")

        while self.h_skills_flow.count():
            it = self.h_skills_flow.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        
        h_skills_raw = data.get("Hard_Skills", "")
        if not h_skills_raw and data.get("Skills"):
            parts = data.get("Skills", "").split("||")
            h_skills_raw = parts[0] if len(parts) > 0 else ""
            
        h_skills = [s.strip() for s in h_skills_raw.replace(",", "|").replace(";", "|").split("|") if s.strip()]
        for s in h_skills:
            pill = SkillTag(s, "hard_skills", font_size=14)
            self.h_skills_flow.addWidget(pill)

        while self.s_skills_flow.count():
            it = self.s_skills_flow.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            
        s_skills_raw = data.get("Soft_Skills", "")
        if not s_skills_raw and data.get("Skills"):
            parts = data.get("Skills", "").split("||")
            s_skills_raw = parts[1] if len(parts) > 1 else ""

        s_skills = [s.strip() for s in s_skills_raw.replace(",", "|").replace(";", "|").split("|") if s.strip()]
        for s in s_skills:
            pill = SkillTag(s, "soft_skills", font_size=14)
            self.s_skills_flow.addWidget(pill)

        self._populate_list(self.lay_benefit, data.get("Benefit_Pekerjaan", ""))
        self._populate_list(self.lay_kual, data.get("Kualifikasi_Persyaratan", ""))

        is_applied = data.get("Is_lamar", False)
        self.btn_lamar.setText("Sudah Melamar" if is_applied else "Lamar Sekarang")
        self.btn_lamar.setEnabled(not is_applied)
        self.btn_lamar.setIcon(QIcon(checked_icon_path if is_applied else send_icon_path))


class SelectCVDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pilih CV")
        self.setFixedWidth(420)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.selected_cv = None
        self.setup_ui()

    def setup_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #2C687B;
                border-radius: 15px;
            }
            QLabel { border: none; background: transparent; }
        """)
        main_lay.addWidget(self.container)

        inner_lay = QVBoxLayout(self.container)
        inner_lay.setContentsMargins(25, 25, 25, 25)
        inner_lay.setSpacing(20)

        title = QLabel("Pilih CV untuk Dikirim")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2C687B;")
        inner_lay.addWidget(title)

        cvs = []
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(root_dir, "database", "Database Permanen", "Career Toolkit", "curiculum-vitae.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    cvs = json.load(f)
        except Exception as e:
            print(f"Error loading CVs: {e}")

        if not cvs:
            lbl_empty = QLabel("Tidak ada CV tersedia. Silakan buat CV di Career Toolkit.")
            lbl_empty.setWordWrap(True)
            lbl_empty.setStyleSheet("color: #718096; font-size: 14px; font-style: italic;")
            inner_lay.addWidget(lbl_empty)
            
            btn_close = QPushButton("Tutup")
            btn_close.setCursor(Qt.PointingHandCursor)
            btn_close.setFixedHeight(38)
            btn_close.setStyleSheet(MODERN_BUTTON_STYLE)
            btn_close.clicked.connect(self.reject)
            inner_lay.addWidget(btn_close)
            return

        hint = QLabel("Pilih salah satu CV di bawah ini:")
        hint.setStyleSheet("color: #4A5568; font-size: 14px;")
        inner_lay.addWidget(hint)

        self.combo_cv = QComboBox()
        for cv in cvs:
            self.combo_cv.addItem(cv.get("cv_name", "CV Tanpa Nama"), cv)
        
        self.combo_cv.setItemDelegate(QStyledItemDelegate())
        self.combo_cv.setFixedHeight(40)
        self.combo_cv.setStyleSheet("""
            QComboBox { 
                border: 1px solid #D1D5DB; border-radius: 8px; padding: 8px 12px; font-size: 14px; background: #F9FAFB; color: #1E3A4A;
            }
            QComboBox:focus { border: 2px solid #2C687B; }
            QComboBox QAbstractItemView { background: white; border: 1px solid #D1D5DB; selection-background-color: #E2EFF1; selection-color: #2C687B; outline: none; }
        """)
        inner_lay.addWidget(self.combo_cv)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        btn_cancel = QPushButton("Batal")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6; color: #4A5568;
                border: 1px solid #D1D5DB; border-radius: 8px;
                padding: 8px 18px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #E5E7EB; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_confirm = QPushButton("Kirim CV Ini")
        btn_confirm.setCursor(Qt.PointingHandCursor)
        btn_confirm.setFixedHeight(38)
        btn_confirm.setStyleSheet(MODERN_BUTTON_STYLE)
        btn_confirm.clicked.connect(self.on_confirm)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        inner_lay.addLayout(btn_layout)

    def on_confirm(self):
        self.selected_cv = self.combo_cv.currentData()
        self.accept()
