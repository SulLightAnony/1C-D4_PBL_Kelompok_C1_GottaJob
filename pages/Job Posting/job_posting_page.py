import datetime
import os
import sys
import copy
import threading
import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QLineEdit, QTextEdit, QDateEdit, QGridLayout, QFrame, QComboBox, 
    QMessageBox, QStackedWidget, QApplication, QStyledItemDelegate, QDialog
)
from PyQt5.QtCore import Qt, QDate, QSize, pyqtSignal, QUrl, QRegExp
from PyQt5.QtGui import QFont, QIcon, QPixmap, QRegExpValidator, QDesktopServices

# Import local components
from constants import (
    post_icon_path, refresh_icon_path, trash_icon_path, 
    plus_icon_path, search_icon_path, down_icon_path,
    send_icon_path, checked_icon_path, currency_icon_path,
    edit_icon_path, location_icon_path, calendar_icon_path,
    link_icon_path, suitcase_icon_path
)
from flow_layout import FlowLayout
from skill_tag_input import SkillTagInput
from job_card_widget import JobCardWidget

# Import from other directories (using existing logic)
_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pages_dir not in sys.path:
    sys.path.insert(0, _pages_dir)

from CRUD.Shared import muat_data, simpan_data
from modul_antarmuka_pengguna import KeyboardScrollArea, show_message, show_question, MODERN_BUTTON_STYLE, ActionButton, SkillTag
from Modul.modul_database import catat_aktivitas
from CRUD.Read import JobDetailDialog

# --- Page: Detail Lowongan ---
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

        self.lbl_meta = QLabel("Company • Location")
        self.lbl_meta.setStyleSheet("color: #9FE1CB; font-size: 14px; border: none; background: transparent;")
        h_layout.addWidget(self.lbl_meta)

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
        
        self.lay_benefit = QVBoxLayout()
        self.lay_benefit.addWidget(self._create_section_lbl("BENEFIT PEKERJAAN"))
        bk_row.addLayout(self.lay_benefit, 1)

        self.lay_kual = QVBoxLayout()
        self.lay_kual.addWidget(self._create_section_lbl("KUALIFIKASI & PERSYARATAN"))
        bk_row.addLayout(self.lay_kual, 1)

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
        self.lbl_sisa = QLabel("Sisa - hari")
        self.lbl_sisa.setStyleSheet("color: #718096; font-size: 13px; font-weight: 500;")
        f_lay.addWidget(self.lbl_sisa)

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
            # Mouse press logic to open link
            v_lbl.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl(value))
            
        v.addWidget(v_lbl)
        lay.addLayout(v)
        lay.addStretch()
        return box

    def _populate_list(self, layout, items_str):
        # Clear previous items except label
        while layout.count() > 1:
            it = layout.takeAt(1)
            if it.widget(): it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    w = it.layout().takeAt(0).widget()
                    if w: w.deleteLater()
        
        items = [i.strip() for i in items_str.split("|") if i.strip()]
        if not items:
            l = QLabel("Tidak ada data")
            l.setStyleSheet("color: #94A3B8; font-style: italic; font-size: 16px; border: none;")
            layout.addWidget(l)
            return

        for text in items:
            row = QHBoxLayout()
            row.setSpacing(10)
            check = QLabel("✓")
            check.setStyleSheet("color: #2C687B; font-weight: bold; font-size: 16px; border: none;")
            row.addWidget(check, 0, Qt.AlignTop)
            
            t_lbl = QLabel(text)
            t_lbl.setWordWrap(True)
            t_lbl.setStyleSheet("color: #334155; font-size: 16px; line-height: 140%; border: none;")
            row.addWidget(t_lbl, 1)
            layout.addLayout(row)

    def setData(self, data):
        self.job_data = data
        self.lbl_title.setText(data.get("Judul_Pekerjaan", "Detail Lowongan"))
        self.lbl_meta.setText(f"{data.get('Nama_Perusahaan', '-')}  •  {data.get('Lokasi', '-')}")

        # Refresh Badges
        while self.badge_layout.count():
            item = self.badge_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        for b in [data.get("Jenis_Pekerjaan"), data.get("Kategori")]:
            if b:
                lbl = QLabel(b)
                lbl.setStyleSheet("background-color: rgba(255,255,255,0.15); color: white; border-radius: 12px; padding: 4px 14px; font-size: 11px; font-weight: 600; border: none;")
                self.badge_layout.addWidget(lbl)
        self.badge_layout.addStretch()

        # Refresh Meta Grid
        while self.meta_grid.count():
            item = self.meta_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        self.meta_grid.addWidget(self._create_meta_item("Rentang Gaji", data.get("Rentang_Gaji", "-"), currency_icon_path), 0, 0)
        self.meta_grid.addWidget(self._create_meta_item("Tanggal Kadaluarsa", data.get("Tanggal_Kadaluarsa", "-"), calendar_icon_path), 0, 1)
        self.meta_grid.addWidget(self._create_meta_item("Jenis Pekerjaan", data.get("Jenis_Pekerjaan", "-"), suitcase_icon_path), 1, 0)
        self.meta_grid.addWidget(self._create_meta_item("Link Lowongan", data.get("Link_Lowongan", "-") or "-", icon_path=link_icon_path, is_link=True), 1, 1)

        # Description
        desc = data.get("Deskripsi_Pekerjaan", "").strip()
        self.lbl_desc.setText(desc if desc else "Tidak ada deskripsi tersedia untuk lowongan ini.")

        # Hard Skills
        while self.h_skills_flow.count():
            it = self.h_skills_flow.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        
        h_skills_raw = data.get("Hard_Skills", "")
        # Fallback untuk data lama
        if not h_skills_raw and data.get("Skills"):
            parts = data.get("Skills", "").split("||")
            h_skills_raw = parts[0] if len(parts) > 0 else ""
            
        h_skills = [s.strip() for s in h_skills_raw.replace(",", "|").replace(";", "|").split("|") if s.strip()]
        for s in h_skills:
            pill = SkillTag(s, "hard_skills", font_size=14)
            self.h_skills_flow.addWidget(pill)

        # Soft Skills
        while self.s_skills_flow.count():
            it = self.s_skills_flow.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            
        s_skills_raw = data.get("Soft_Skills", "")
        # Fallback untuk data lama
        if not s_skills_raw and data.get("Skills"):
            parts = data.get("Skills", "").split("||")
            s_skills_raw = parts[1] if len(parts) > 1 else ""

        s_skills = [s.strip() for s in s_skills_raw.replace(",", "|").replace(";", "|").split("|") if s.strip()]
        for s in s_skills:
            pill = SkillTag(s, "soft_skills", font_size=14)
            self.s_skills_flow.addWidget(pill)

        # Populate Checklist
        self._populate_list(self.lay_benefit, data.get("Benefit_Pekerjaan", ""))
        self._populate_list(self.lay_kual, data.get("Kualifikasi_Persyaratan", ""))

        # Lamar status
        is_applied = data.get("Is_lamar", False)
        self.btn_lamar.setText("Sudah Melamar" if is_applied else "Lamar Sekarang")
        self.btn_lamar.setEnabled(not is_applied)
        self.btn_lamar.setIcon(QIcon(checked_icon_path if is_applied else send_icon_path))

        # Remaining days
        try:
            d_str = data.get("Tanggal_Kadaluarsa", "")
            d = datetime.datetime.strptime(d_str, "%d/%m/%Y").date()
            diff = (d - datetime.date.today()).days
            self.lbl_sisa.setText(f"Sisa {max(0, diff)} hari" if diff >= 0 else "Lowongan Berakhir")
        except:
            self.lbl_sisa.setText("Sisa - hari")

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
        # Main Layout (Transparan)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)

        # Container dengan styling ModernMessageBox
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

        # Load CV data
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



class JobPostingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ids = set()
        self.data = []
        self.editing_job_id = None
        self._init_stack()
        self.load_data()

    def update_theme_mode(self, is_admin):
        """Memperbarui gaya tombol mengikuti peran user yang sedang login."""
        theme = "admin" if is_admin else "user"
        if hasattr(self, 'btn_refresh'):
            self.btn_refresh.set_theme(theme)
        if hasattr(self, 'btn_add'):
            self.btn_add.set_theme(theme)

    def showEvent(self, event):
        if hasattr(self, 'page_stack'):
            self.page_stack.setCurrentIndex(0)
        super().showEvent(event)

    def _init_stack(self):
        """Membungkus halaman daftar, halaman form, dan halaman detail ke dalam QStackedWidget."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.page_stack = QStackedWidget()
        
        self.list_page = QWidget()
        self.setup_ui() # mengisi self.list_page
        self.form_page = self._build_form_page()
        self.detail_page = JobDetailPage(self)

        self.page_stack.addWidget(self.list_page)
        self.page_stack.addWidget(self.form_page)
        self.page_stack.addWidget(self.detail_page)

        # Connect Detail Page signals
        self.detail_page.back_clicked.connect(lambda: self.page_stack.setCurrentIndex(0))
        self.detail_page.edit_requested.connect(self.edit_data)
        self.detail_page.delete_requested.connect(self.delete_single_data)
        self.detail_page.lamar_requested.connect(self.proses_lamar)

        outer_layout.addWidget(self.page_stack)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self.list_page)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Header Row
        header_layout = QHBoxLayout()
        
        # Icon Label
        icon_label = QLabel()
        pixmap = QPixmap(post_icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_label, alignment=Qt.AlignTop | Qt.AlignLeft)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        lbl_title = QLabel("Manajemen Job Posting")
        lbl_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_title.setStyleSheet("color: #222;")
        lbl_sub = QLabel("Kelola semua lowongan pekerjaan")
        lbl_sub.setFont(QFont("Segoe UI", 12))
        lbl_sub.setStyleSheet("color: #777;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_sub)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        # Action Buttons
        self.btn_refresh = ActionButton(" Refresh", icon_path=refresh_icon_path, color_theme="user")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_delete_multi = ActionButton(" Hapus ", icon_path=trash_icon_path, color_theme="danger")
        self.btn_delete_multi.clicked.connect(self.delete_selected)
        self.btn_delete_multi.hide() # Hidden by default
        
        self.btn_add = ActionButton(" Tambah Data ", icon_path=plus_icon_path, color_theme="user")
        self.btn_add.clicked.connect(self.add_data)
        
        header_layout.addWidget(self.btn_refresh)
        header_layout.addWidget(self.btn_delete_multi)
        header_layout.addWidget(self.btn_add)
        
        self.main_layout.addLayout(header_layout)

        # Statistics Cards Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        def create_stat_card(title, badge_text, badge_color, badge_bg):
            frame = QFrame()
            frame.setFixedHeight(110)
            frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #eee; border-radius: 10px; }")
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(20, 15, 20, 15)
            
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("color: #777; font-size: 11px; font-weight: bold; border: none;")
            
            lbl_c = QLabel("0")
            lbl_c.setFont(QFont("Segoe UI", 24, QFont.Bold))
            lbl_c.setStyleSheet("color: #222; border: none;")
            
            lbl_b = QLabel(badge_text)
            lbl_b.setStyleSheet(f"background-color: {badge_bg}; color: {badge_color}; border-radius: 10px; padding: 2px 8px; font-size: 10px; border: none;")
            lbl_b.setFixedSize(lbl_b.sizeHint())
            
            lay.addWidget(lbl_t)
            lay.addWidget(lbl_c)
            lay.addWidget(lbl_b)
            return frame, lbl_c

        self.card_total, self.lbl_count_total = create_stat_card("TOTAL POSTING", "Aktif", "#2e7d32", "#e8f5e9")
        self.card_ft, self.lbl_count_ft = create_stat_card("Penuh Waktu", "Terbuka", "#1a73e8", "#e8f0fe")
        self.card_rm, self.lbl_count_rm = create_stat_card("REMOTE", "Aktif", "#2e7d32", "#e8f5e9")
        self.card_warn, self.lbl_count_warn = create_stat_card("SEGERA KADALUARSA", "⚠️ Perhatian", "#f57c00", "#fff3e0")
        
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_ft)
        stats_layout.addWidget(self.card_rm)
        stats_layout.addWidget(self.card_warn)
        
        self.main_layout.addLayout(stats_layout)

        # Filter & Search Row
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 10, 0, 10)
        
        lbl_list = QLabel("Daftar Lowongan")
        lbl_list.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_list.setStyleSheet("color: #222;")
        
        self.lbl_list_count = QLabel("0 lowongan")
        self.lbl_list_count.setStyleSheet("color: #888; font-size: 12px;")
        
        filter_layout.addWidget(lbl_list)
        filter_layout.addWidget(self.lbl_list_count)
        filter_layout.addStretch()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cari lowongan...")
        self.search_bar.setFixedSize(250, 36)
        self.search_bar.setStyleSheet("QLineEdit { border: 1px solid #ddd; border-radius: 18px; padding: 0 15px; font-size: 13px; background-color: white;}")
        self.search_bar.addAction(QIcon(search_icon_path), QLineEdit.LeadingPosition)
        self.search_bar.textChanged.connect(self.filter_cards)
        
        self.combo_filter = QComboBox()
        self.combo_filter.setItemDelegate(QStyledItemDelegate())
        self.combo_filter.addItems(["Semua Jenis", "Penuh Waktu", "Paruh Waktu", "Freelance", "Magang", "Kontrak"])
        self.combo_filter.setFixedSize(150, 36)
        
        combo_style = f"""
            QComboBox {{
                border: 1px solid #ddd;
                border-radius: 18px;
                padding: 0 15px;
                font-size: 13px;
                background-color: white;
                color: black;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url({down_icon_path});
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView, QListView {{
                background-color: white;
                background: white;
                color: black;
                selection-background-color: #2C687B;
                selection-color: white;
                border: 1px solid #ddd;
                outline: none;
            }}
            QComboBox QAbstractItemView::item, QListView::item {{
                background-color: white;
                color: black;
                padding: 4px 8px;
            }}
        """
        self.combo_filter.setStyleSheet(combo_style)
        self.combo_filter.currentTextChanged.connect(self.filter_cards)
        
        filter_layout.addWidget(self.search_bar)
        filter_layout.addWidget(self.combo_filter)
        
        self.main_layout.addLayout(filter_layout)

        # Cards Scroll Area
        self.scroll_area = KeyboardScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.flow_layout = FlowLayout(self.cards_container, margin=0, spacing=20)
        
        self.scroll_area.setWidget(self.cards_container)
        self.main_layout.addWidget(self.scroll_area)

    def load_data(self):
        self.data = muat_data()
        self.refresh_ui_only()

    def refresh_ui_only(self):
        self.selected_ids.clear()
        self.btn_delete_multi.hide()
        self.render_cards(self.search_bar.text(), self.combo_filter.currentText())
        self.update_statistics()

    def simpan_data_async(self):
        data_copy = copy.deepcopy(self.data)
        threading.Thread(target=simpan_data, args=(data_copy,), daemon=True).start()

    def update_statistics(self):
        total = len(self.data)
        ft = sum(1 for j in self.data if j.get('Jenis_Pekerjaan', '') == 'Penuh Waktu')
        rm = sum(1 for j in self.data if 'remote' in j.get('Lokasi', '').lower() or 'remote' in j.get('Jenis_Pekerjaan', '').lower())
        
        warn = 0
        today = datetime.date.today()
        for j in self.data:
            try:
                d = datetime.datetime.strptime(j.get("Tanggal_Kadaluarsa", ""), "%d/%m/%Y").date()
                if (d - today).days <= 7:
                    warn += 1
            except: pass
            
        self.lbl_count_total.setText(str(total))
        self.lbl_count_ft.setText(str(ft))
        self.lbl_count_rm.setText(str(rm))
        self.lbl_count_warn.setText(str(warn))
        self.lbl_list_count.setText(f"{total} lowongan")

    def render_cards(self, filter_text="", type_filter="Semua Jenis"):
        # Clear layout
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        filter_text = filter_text.lower()
        count = 0
        for job in self.data:
            j_title = job.get("Judul_Pekerjaan", "").lower()
            j_comp = job.get("Nama_Perusahaan", "").lower()
            j_type = job.get("Jenis_Pekerjaan", "")
            
            if filter_text and filter_text not in j_title and filter_text not in j_comp:
                continue
            if type_filter != "Semua Jenis" and type_filter.lower() != j_type.lower():
                continue
                
            card = JobCardWidget(job)
            card.edit_clicked.connect(self.edit_data)
            card.delete_clicked.connect(self.delete_single_data)
            card.checkbox_toggled.connect(self.handle_checkbox)
            card.card_clicked.connect(self.show_job_details)
            card.lamar_clicked.connect(self.proses_lamar)
            self.flow_layout.addWidget(card)
            count += 1
            
        self.lbl_list_count.setText(f"{count} lowongan")

    def filter_cards(self):
        self.render_cards(self.search_bar.text(), self.combo_filter.currentText())

    def handle_checkbox(self, job_data, is_checked):
        job_id = job_data.get("id")
        if is_checked:
            self.selected_ids.add(job_id)
        else:
            self.selected_ids.discard(job_id)
            
        if self.selected_ids:
            self.btn_delete_multi.show()
            self.btn_delete_multi.setText(f" Hapus ({len(self.selected_ids)}) ")
        else:
            self.btn_delete_multi.hide()

    def _build_form_page(self):
        """Membangun halaman form tambah data sebagai QWidget penuh (bukan dialog)."""
        page = QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setFixedHeight(38)
        btn_back.setStyleSheet("""
            QPushButton { border: 1px solid #ccc; border-radius: 8px; padding: 0 20px;
                          background-color: white; color: #444; font-size: 14px; }
            QPushButton:hover { background-color: #f0f0f0; }
        """)
        btn_back.clicked.connect(lambda: self.page_stack.setCurrentIndex(0))

        self.lbl_form_title = QLabel("Tambah Lowongan Baru")
        self.lbl_form_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.lbl_form_title.setStyleSheet("color: #222;")

        header.addWidget(btn_back)
        header.addSpacing(16)
        header.addWidget(self.lbl_form_title)
        header.addStretch()
        layout.addLayout(header)

        # Card putih pembungkus form
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 1px solid #e8e8e8; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(18)

        # ── helper pembangun field ──
        def make_field(label_text, widget):
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            v = QVBoxLayout(container)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #555; font-weight: 600; border: none;")
            v.addWidget(lbl)
            v.addWidget(widget)
            return container

        field_style = f"""
            QLineEdit, QTextEdit, QSpinBox {{
                border: 1px solid #dcdcdc; border-radius: 8px;
                padding: 10px 14px; font-size: 14px;
                background-color: white; color: #333;
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
                border: 1px solid #2C687B;
            }}

            QComboBox, QDateEdit {{
                border: 2px solid #B2D2D9;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1E3A4A;
                background-color: #F7FBFC;
            }}
            QComboBox:hover, QDateEdit:hover {{
                border: 2px solid #2C687B;
            }}
            QComboBox::drop-down, QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 35px;
                border: none;
            }}
            QComboBox::down-arrow, QDateEdit::down-arrow {{
                image: url({down_icon_path});
                width: 20px;
                height: 20px;
            }}
            QComboBox QAbstractItemView, QListView {{
                background-color: white;
                background: white;
                color: black;
                selection-background-color: #E2EFF1;
                selection-color: #2C687B;
                border: 1px solid #B2D2D9;
                outline: none;
            }}
            QComboBox QAbstractItemView::item, QListView::item {{
                background-color: white;
                color: black;
                padding: 4px 8px;
            }}
            QComboBox QAbstractItemView::item:hover, QListView::item:hover {{
                background-color: #E2EFF1;
                color: #2C687B;
            }}
            QCalendarWidget QWidget {{ background-color: white; color: #333; }}
            QCalendarWidget QAbstractItemView:enabled {{ color: #333; selection-background-color: #E2EFF1; selection-color: #2C687B; }}
            QCalendarWidget QToolButton {{ color: #1E3A4A; background-color: transparent; border: none; font-weight: bold; }}
            QCalendarWidget QMenu {{ background-color: white; color: #333; border: 1px solid #B2D2D9; }}
        """
        card.setStyleSheet(card.styleSheet() + field_style)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Inisialisasi Field
        self.f_judul = QLineEdit(); self.f_judul.setPlaceholderText("cth. Frontend Developer")
        self.f_perusahaan = QLineEdit(); self.f_perusahaan.setPlaceholderText("cth. PT Teknologi Maju")
        
        self.f_jenis = QComboBox()
        self.f_jenis.setItemDelegate(QStyledItemDelegate())
        self.f_jenis.addItems(["Penuh Waktu","Kontrak","Paruh Waktu","Magang","Freelance"])
        
        self.f_lokasi = QLineEdit(); self.f_lokasi.setPlaceholderText("cth. Jakarta, Indonesia")
        
        self.f_gaji_min = QLineEdit(); self.f_gaji_min.setPlaceholderText("Gaji Min (cth. 5.000.000)")
        self.f_gaji_max = QLineEdit(); self.f_gaji_max.setPlaceholderText("Gaji Max (cth. 8.000.000)")
        salary_val = QRegExpValidator(QRegExp(r"[0-9.]+"))
        self.f_gaji_min.setValidator(salary_val)
        self.f_gaji_max.setValidator(salary_val)

        def format_salary_input(edit_widget):
            text = edit_widget.text().replace('.', '')
            if not text: return
            try:
                formatted = "{:,}".format(int(text)).replace(',', '.')
                edit_widget.blockSignals(True)
                cursor_pos = edit_widget.cursorPosition()
                old_len = len(edit_widget.text())
                edit_widget.setText(formatted)
                new_pos = cursor_pos + (len(formatted) - old_len)
                edit_widget.setCursorPosition(max(0, new_pos))
                edit_widget.blockSignals(False)
            except: pass

        self.f_gaji_min.textChanged.connect(lambda: format_salary_input(self.f_gaji_min))
        self.f_gaji_max.textChanged.connect(lambda: format_salary_input(self.f_gaji_max))

        gaji_container = QWidget()
        gaji_container.setStyleSheet("background: transparent;")
        gaji_lay = QHBoxLayout(gaji_container)
        gaji_lay.setContentsMargins(0,0,0,0)
        gaji_lay.addWidget(self.f_gaji_min)
        lbl_dash = QLabel("-"); lbl_dash.setStyleSheet("color: #888; font-weight: bold; border: none;")
        gaji_lay.addWidget(lbl_dash)
        gaji_lay.addWidget(self.f_gaji_max)

        self.f_date = QDateEdit()
        self.f_date.setCalendarPopup(True)
        self.f_date.setDisplayFormat("dd/MM/yyyy")
        self.f_date.setDate(QDate.currentDate().addDays(30))
        self.f_date.setMinimumDate(QDate.currentDate().addDays(1))

        # Terapkan style langsung ke popup kalender agar tidak hitam
        cal = self.f_date.calendarWidget()
        cal.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #B2D2D9;
                border-radius: 8px;
            }
            QCalendarWidget QAbstractItemView {
                background-color: white;
                color: #1E3A4A;
                selection-background-color: #1D4E5F;
                selection-color: white;
                outline: none;
                font-size: 13px;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #B2D2D9;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1D4E5F;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 4px;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 14px;
                padding: 4px 8px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: rgba(255,255,255,0.15);
                border-radius: 4px;
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }
            QCalendarWidget QSpinBox {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #1E3A4A;
                border: 1px solid #B2D2D9;
                font-size: 13px;
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #E2EFF1;
                color: #1D4E5F;
            }
            QCalendarWidget QHeaderView::section {
                background-color: #F0F7F9;
                color: #2C687B;
                font-weight: bold;
                font-size: 12px;
                border: none;
                padding: 4px;
            }
        """)

        self.skill_input = SkillTagInput(btn_text="Tambah")
        lbl_skill_hint = QLabel('Ketik skill lalu tekan Enter atau klik Tambah')
        lbl_skill_hint.setStyleSheet("color: #777; font-size: 11px; margin-top: 2px; margin-left: 2px; border: none; background: transparent;")
        skills_group = QWidget()
        skills_group_layout = QVBoxLayout(skills_group)
        skills_group_layout.setContentsMargins(0, 0, 0, 0); skills_group_layout.setSpacing(4)
        skills_group_layout.addWidget(self.skill_input); skills_group_layout.addWidget(lbl_skill_hint)

        self.f_kategori = QComboBox()
        self.f_kategori.setEditable(True)
        self.f_kategori.setItemDelegate(QStyledItemDelegate())
        self.f_kategori.addItems([
            "", "Akuntansi", "Administrasi & HRD", "Seni, Media, & Komunikasi",
            "Konstruksi & Real Estate", "Business Development & Sales",
            "Komputer & Perangkat Lunak", "Konsultan", "Desain",
            "Pendidikan & Pelatihan", "Keuangan", "Perangkat Keras & Elektronik",
            "Kesehatan", "Hotel & Travel", "Manajemen Leadership & Senior",
            "Legal", "Manufaktur", "Marketing", "Operasional & Pelayanan Pelanggan",
            "Lainnya", "Product Management & Project Management",
            "Sains & Penelitian", "Industri Jasa", "Supply Chain, Logistik & Transportasi"
        ])
        self.f_kategori.lineEdit().setPlaceholderText("Pilih atau ketik kategori...")

        self.f_link = QLineEdit(); self.f_link.setPlaceholderText("https://...")
        self.f_desc = QTextEdit(); self.f_desc.setPlaceholderText("Deskripsi singkat..."); self.f_desc.setFixedHeight(100)
        self.f_benefit = SkillTagInput(placeholder="cth. BPJS, Makan siang...", btn_text="Tambah")
        self.f_kualifikasi = SkillTagInput(placeholder="cth. Minimal S1, 2 tahun peng...", btn_text="Tambah")

        # Simpan fields untuk relayout responsif
        self.form_field_containers = [
            (make_field("Judul Pekerjaan *", self.f_judul), False),
            (make_field("Nama Perusahaan *", self.f_perusahaan), False),
            (make_field("Jenis Pekerjaan", self.f_jenis), False),
            (make_field("Lokasi", self.f_lokasi), False),
            (make_field("Rentang Gaji (Angka Saja)", gaji_container), False),
            (make_field("Tanggal Kadaluarsa", self.f_date), False),
            (make_field("Skills", skills_group), True),
            (make_field("Kategori Pekerjaan", self.f_kategori), True),
            (make_field("Link Lowongan", self.f_link), True),
            (make_field("Deskripsi Pekerjaan", self.f_desc), True),
            (make_field("Benefit Pekerjaan", self.f_benefit), False),
            (make_field("Kualifikasi Persyaratan", self.f_kualifikasi), False)
        ]

        self.form_grid = grid
        self._refresh_form_layout() 

        card_layout.addLayout(grid)

        # Tombol Simpan
        btn_save = QPushButton("Simpan Lowongan")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(44)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #2C687B; border-radius: 8px; color: white;
                          font-size: 15px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #408699; }
        """)
        btn_save.clicked.connect(self._save_new_job)
        card_layout.addWidget(btn_save)

        # Bisa disubmit menggunakan Enter
        for field in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            field.returnPressed.connect(self._save_new_job)

        # Bungkus form ke dalam Scroll Area agar tidak merusak ukuran jendela
        scroll = KeyboardScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        # Masukkan card ke dalam scroll
        scroll.setWidget(card)
        
        layout.addWidget(scroll)
        return page

    def _refresh_form_layout(self):
        """Mengatur ulang layout form agar responsif (1 atau 2 kolom)."""
        if not hasattr(self, 'form_grid') or not hasattr(self, 'form_field_containers'):
            return

        # Ambil semua widget dari grid tanpa menghapusnya (hanya hapus dari layout)
        while self.form_grid.count():
            item = self.form_grid.takeAt(0)
            # Jangan setParent(None) agar widget tidak terhapus
            # Cukup biarkan layout melepaskannya

        width = self.width()
        cols = 1 if width < 800 else 2
        
        curr_row = 0
        curr_col = 0

        for container, is_full in self.form_field_containers:
            if cols == 1 or is_full:
                self.form_grid.addWidget(container, curr_row, 0, 1, cols)
                curr_row += 1
                curr_col = 0
            else:
                self.form_grid.addWidget(container, curr_row, curr_col)
                curr_col += 1
                if curr_col >= cols:
                    curr_row += 1
                    curr_col = 0

    def resizeEvent(self, event):
        """Update layout saat window di-resize."""
        super().resizeEvent(event)
        if hasattr(self, 'page_stack') and self.page_stack.currentIndex() == 1:
            self._refresh_form_layout()

    def _save_new_job(self):
        """Validasi dan simpan data dari halaman form tambah dengan mendelegasikan ke logika CRUD."""
        form_data = {
            "judul": self.f_judul.text().strip(),
            "perusahaan": self.f_perusahaan.text().strip(),
            "jenis": self.f_jenis.currentText(),
            "lokasi": self.f_lokasi.text().strip(),
            "gaji_min": self.f_gaji_min.text().strip(),
            "gaji_max": self.f_gaji_max.text().strip(),
            "skills": self.skill_input.get_skills(),
            "link": self.f_link.text().strip(),
            "desc": self.f_desc.toPlainText().strip(),
            "benefit": "|".join(self.f_benefit.get_skills()),
            "kualifikasi": "|".join(self.f_kualifikasi.get_skills()),
            "kategori": self.f_kategori.currentText().strip(),
            "date": self.f_date.date()
        }

        if self.editing_job_id:
            from CRUD.Update import proses_update_job
            success, msg, new_data = proses_update_job(self.editing_job_id, form_data, self.data)
        else:
            from CRUD.Create import proses_create_job
            success, msg, new_data = proses_create_job(form_data, self.data)

        if not success:
            show_message(self, "Validasi Gagal", msg)
            return

        self.data = new_data
        action_msg = "Diperbarui" if self.editing_job_id else "Ditambah"
        catat_aktivitas(f"<b>Lowongan {action_msg}</b><br>{form_data['judul']}", role="admin")
        self.simpan_data_async()

        self.editing_job_id = None

        # Reset form
        for w in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            w.clear()
        self.f_kategori.setCurrentIndex(0)
        self.f_kategori.lineEdit().clear()
        self.skill_input.clear_all()
        self.f_desc.clear()
        self.f_benefit.clear_all()
        self.f_kualifikasi.clear_all()
        self.f_jenis.setCurrentIndex(0)

        self.page_stack.setCurrentIndex(0)
        self.refresh_ui_only()
        show_message(self, "Berhasil", msg)

    def add_data(self):
        """Beralih ke halaman form tambah."""
        self.editing_job_id = None
        self.lbl_form_title.setText("Tambah Lowongan Baru")
        for w in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            w.clear()
        self.f_kategori.setCurrentIndex(0)
        self.f_kategori.lineEdit().clear()
        self.skill_input.clear_all()
        self.f_desc.clear()
        self.f_benefit.clear_all()
        self.f_kualifikasi.clear_all()
        self.f_jenis.setCurrentIndex(0)
        self.f_date.setDate(QDate.currentDate().addDays(30))
        self.page_stack.setCurrentIndex(1)

    def edit_data(self, job_data):
        """Beralih ke halaman form untuk mengedit data yang sudah ada."""
        self.editing_job_id = job_data.get("id")
        self.lbl_form_title.setText("Edit Lowongan")
        
        self.f_judul.setText(job_data.get("Judul_Pekerjaan", ""))
        self.f_perusahaan.setText(job_data.get("Nama_Perusahaan", ""))
        
        jenis = job_data.get("Jenis_Pekerjaan", "")
        idx = self.f_jenis.findText(jenis)
        if idx >= 0:
            self.f_jenis.setCurrentIndex(idx)
            
        self.f_lokasi.setText(job_data.get("Lokasi", ""))
        
        raw_sal = job_data.get("Rentang_Gaji", "")
        if "-" in raw_sal:
            parts = raw_sal.split("-")
            if len(parts) >= 2:
                self.f_gaji_min.setText(parts[0].strip())
                self.f_gaji_max.setText(parts[1].strip())
        else:
            self.f_gaji_min.setText(raw_sal)
            self.f_gaji_max.clear()
            
        # Muat ulang skills
        raw_skills = job_data.get("Skills", "")
        skills_list = [s.strip() for s in raw_skills.split('|') if s.strip()] if raw_skills else []
        self.skill_input.load_skills(skills_list)
        self.f_link.setText(job_data.get("Link_Lowongan", ""))
        self.f_desc.setPlainText(job_data.get("Deskripsi_Pekerjaan", ""))
        
        raw_benefit = job_data.get("Benefit_Pekerjaan", "")
        self.f_benefit.load_skills([s.strip() for s in raw_benefit.split('|') if s.strip()] if raw_benefit else [])
        
        raw_kualifikasi = job_data.get("Kualifikasi_Persyaratan", "")
        self.f_kualifikasi.load_skills([s.strip() for s in raw_kualifikasi.split('|') if s.strip()] if raw_kualifikasi else [])
        
        kat = job_data.get("Kategori", "")
        self.f_kategori.setEditText(kat)
        
        date_str = job_data.get("Tanggal_Kadaluarsa", "")
        try:
            d = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            self.f_date.setDate(QDate(d.year, d.month, d.day))
        except:
            self.f_date.setDate(QDate.currentDate().addDays(30))
            
        self.page_stack.setCurrentIndex(1)

    def delete_single_data(self, job_data):
        reply = show_question(self, 'Konfirmasi Hapus', "Yakin ingin menghapus lowongan ini?")
        if reply == QMessageBox.Yes:
            from CRUD.Delete import proses_delete_job
            success, msg, new_data = proses_delete_job(job_data.get("id"), self.data)
            if success:
                self.data = new_data
                self.simpan_data_async()
                catat_aktivitas(msg, role="admin")
                self.refresh_ui_only()
                if self.page_stack.currentIndex() == 2:
                    self.page_stack.setCurrentIndex(0)

    def delete_selected(self):
        from CRUD.Delete import proses_delete_massal
        reply = show_question(self, 'Konfirmasi Hapus Massal', f"Yakin ingin menghapus {len(self.selected_ids)} lowongan terpilih?")
        if reply == QMessageBox.Yes:
            success, msg, new_data = proses_delete_massal(self.selected_ids, self.data)
            if success:
                self.data = new_data
                self.simpan_data_async()
                catat_aktivitas(msg, role="admin")
                self.selected_ids = set()
                self.refresh_ui_only()

    def proses_lamar(self, job_data):
        """Menampilkan alur pemilihan CV dan update status Is_lamar."""
        if job_data.get("Is_lamar", False):
            show_message(self, "Informasi", "Anda sudah melamar pekerjaan ini.")
            return

        # 1. Pilih CV
        dialog = SelectCVDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
            
        cv_data = dialog.selected_cv
        cv_name = cv_data.get("cv_name", "CV Terpilih")

        # 2. Konfirmasi Kirim
        res = show_question(
            self, "Konfirmasi Pengiriman",
            f"Ingin mengirim {cv_name} untuk melamar posisi {job_data.get('Judul_Pekerjaan')} di {job_data.get('Nama_Perusahaan')}?"
        )
        
        if res == QMessageBox.Yes:
            # Update status di data lokal
            for job in self.data:
                if job.get("id") == job_data.get("id"):
                    job["Is_lamar"] = True
                    break
            
            # Simpan dan Refresh
            self.simpan_data_async()
            self.refresh_ui_only()
            
            show_message(
                self, "Berhasil",
                f"CV '{cv_name}' telah berhasil dikirim!\nStatus lamaran telah diperbarui."
            )
            
            # Refresh detail page if active
            if self.page_stack.currentIndex() == 2:
                self.detail_page.setData(job_data)

    def show_job_details(self, job_data):
        """Berpindah ke halaman detail lowongan dengan data yang dipilih."""
        self.detail_page.setData(job_data)
        self.page_stack.setCurrentIndex(2)
