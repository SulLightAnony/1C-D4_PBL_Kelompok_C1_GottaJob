import datetime
import os
import sys
import copy
import threading

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QLineEdit, QTextEdit, QDateEdit, QGridLayout, QFrame, QComboBox, 
    QMessageBox, QStackedWidget, QApplication, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QDate, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QRegExpValidator
from PyQt5.QtCore import QRegExp

# Import local components
from constants import (
    post_icon_path, refresh_icon_path, trash_icon_path, 
    plus_icon_path, search_icon_path, down_icon_path
)
from flow_layout import FlowLayout
from skill_tag_input import SkillTagInput
from job_card_widget import JobCardWidget

# Import from other directories (using existing logic)
_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pages_dir not in sys.path:
    sys.path.insert(0, _pages_dir)

from CRUD.Shared import muat_data, simpan_data
from modul_antarmuka_pengguna import KeyboardScrollArea, show_message, show_question
from Modul.modul_database import catat_aktivitas
from CRUD.Read import JobDetailDialog

class JobPostingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ids = set()
        self.data = []
        self.editing_job_id = None
        self._init_stack()
        self.load_data()

    def showEvent(self, event):
        if hasattr(self, 'page_stack'):
            self.page_stack.setCurrentIndex(0)
        super().showEvent(event)

    def _init_stack(self):
        """Membungkus halaman daftar dan halaman form ke dalam QStackedWidget."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.page_stack = QStackedWidget()

        # Halaman 0: Daftar Lowongan
        self.list_page = QWidget()
        self.setup_ui()  # mengisi self.list_page

        # Halaman 1: Form Tambah Data
        self.form_page = self._build_form_page()

        self.page_stack.addWidget(self.list_page)   # index 0
        self.page_stack.addWidget(self.form_page)   # index 1

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
        btn_style_primary = "QPushButton { border: none; border-radius: 6px; background-color: #2C687B; color: white; font-size: 14px; font-weight: bold; padding: 0 20px;} QPushButton:hover { background-color: #408699; }"

        self.btn_refresh = QPushButton(" Refresh")
        self.btn_refresh.setIcon(QIcon(refresh_icon_path))
        self.btn_refresh.setIconSize(QSize(18, 18))
        self.btn_refresh.setFixedHeight(40)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet(btn_style_primary)
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_delete_multi = QPushButton(" Hapus ")
        self.btn_delete_multi.setIcon(QIcon(trash_icon_path))
        self.btn_delete_multi.setIconSize(QSize(18, 18))
        self.btn_delete_multi.setFixedHeight(40)
        self.btn_delete_multi.setCursor(Qt.PointingHandCursor)
        self.btn_delete_multi.setStyleSheet(btn_style_primary)
        self.btn_delete_multi.clicked.connect(self.delete_selected)
        self.btn_delete_multi.hide() # Hidden by default
        
        self.btn_add = QPushButton(" Tambah Data ")
        self.btn_add.setIcon(QIcon(plus_icon_path))
        self.btn_add.setIconSize(QSize(18, 18))
        self.btn_add.setFixedHeight(40)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet(btn_style_primary)
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

        # Baris 0: Judul & Perusahaan
        self.f_judul = QLineEdit(); self.f_judul.setPlaceholderText("cth. Frontend Developer")
        self.f_perusahaan = QLineEdit(); self.f_perusahaan.setPlaceholderText("cth. PT Teknologi Maju")
        grid.addWidget(make_field("Judul Pekerjaan *", self.f_judul), 0, 0)
        grid.addWidget(make_field("Nama Perusahaan *", self.f_perusahaan), 0, 1)

        # Baris 1: Jenis & Lokasi
        self.f_jenis = QComboBox()
        self.f_jenis.setItemDelegate(QStyledItemDelegate())
        self.f_jenis.addItems(["Penuh Waktu","Kontrak","Paruh Waktu","Magang","Freelance"])
        self.f_lokasi = QLineEdit(); self.f_lokasi.setPlaceholderText("cth. Jakarta, Indonesia")
        grid.addWidget(make_field("Jenis Pekerjaan", self.f_jenis), 1, 0)
        grid.addWidget(make_field("Lokasi", self.f_lokasi), 1, 1)

        # Baris 2: Gaji & Tanggal (Kalender)
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
            except:
                pass

        self.f_gaji_min.textChanged.connect(lambda: format_salary_input(self.f_gaji_min))
        self.f_gaji_max.textChanged.connect(lambda: format_salary_input(self.f_gaji_max))

        gaji_container = QWidget()
        gaji_container.setStyleSheet("background: transparent;")
        gaji_lay = QHBoxLayout(gaji_container)
        gaji_lay.setContentsMargins(0,0,0,0)
        gaji_lay.addWidget(self.f_gaji_min)
        lbl_dash = QLabel("-")
        lbl_dash.setStyleSheet("color: #888; font-weight: bold; border: none;")
        gaji_lay.addWidget(lbl_dash)
        gaji_lay.addWidget(self.f_gaji_max)

        self.f_date = QDateEdit()
        self.f_date.setCalendarPopup(True)
        self.f_date.setDisplayFormat("dd/MM/yyyy")
        self.f_date.setDate(QDate.currentDate().addDays(30))
        self.f_date.setMinimumDate(QDate.currentDate().addDays(1))

        grid.addWidget(make_field("Rentang Gaji (Angka Saja)", gaji_container), 2, 0)
        grid.addWidget(make_field("Tanggal Kadaluarsa", self.f_date), 2, 1)

        # Baris 3: Skills (Tag Input Style - Inline Box)
        self.skill_input = SkillTagInput(btn_text="Tambah")
        lbl_skill_hint = QLabel('Ketik skill lalu tekan Enter atau klik Tambah')
        lbl_skill_hint.setStyleSheet("color: #777; font-size: 11px; margin-top: 2px; margin-left: 2px; border: none; background: transparent;")

        skills_group = QWidget()
        skills_group_layout = QVBoxLayout(skills_group)
        skills_group_layout.setContentsMargins(0, 0, 0, 0)
        skills_group_layout.setSpacing(4)
        skills_group_layout.addWidget(self.skill_input)
        skills_group_layout.addWidget(lbl_skill_hint)

        grid.addWidget(make_field("Skills", skills_group), 3, 0, 1, 2)

        self.f_link = QLineEdit(); self.f_link.setPlaceholderText("https://...")
        grid.addWidget(make_field("Link Lowongan", self.f_link), 4, 0, 1, 2)

        # Baris 5: Deskripsi (full width)
        self.f_desc = QTextEdit(); self.f_desc.setPlaceholderText("Deskripsi singkat...")
        self.f_desc.setFixedHeight(100)
        grid.addWidget(make_field("Deskripsi Pekerjaan", self.f_desc), 5, 0, 1, 2)

        # Baris 6: Benefit & Kualifikasi
        self.f_benefit = SkillTagInput(placeholder="cth. BPJS, Makan siang...", btn_text="Tambah")
        self.f_kualifikasi = SkillTagInput(placeholder="cth. Minimal S1, 2 tahun peng...", btn_text="Tambah")
        grid.addWidget(make_field("Benefit Pekerjaan", self.f_benefit), 6, 0)
        grid.addWidget(make_field("Kualifikasi Persyaratan", self.f_kualifikasi), 6, 1)

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

        layout.addWidget(card)
        layout.addStretch()
        return page

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
            "date": self.f_date.date()
        }

        if self.editing_job_id:
            from CRUD.Update import proses_update_job
            success, msg, new_data = proses_update_job(self.editing_job_id, form_data, self.data)
        else:
            from CRUD.Create import proses_create_job
            success, msg, new_data = proses_create_job(form_data, self.data)

        if not success:
            QMessageBox.warning(self, "Validasi Gagal", msg)
            return

        self.data = new_data
        action_msg = "Diperbarui" if self.editing_job_id else "Ditambah"
        catat_aktivitas(f"<b>Lowongan {action_msg}</b><br>{form_data['judul']}")
        self.simpan_data_async()

        self.editing_job_id = None

        # Reset form
        for w in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            w.clear()
        self.skill_input.clear_all()
        self.f_desc.clear()
        self.f_benefit.clear_all()
        self.f_kualifikasi.clear_all()
        self.f_jenis.setCurrentIndex(0)

        self.page_stack.setCurrentIndex(0)
        self.refresh_ui_only()
        QMessageBox.information(self, "Berhasil", msg)

    def add_data(self):
        """Beralih ke halaman form tambah."""
        self.editing_job_id = None
        self.lbl_form_title.setText("Tambah Lowongan Baru")
        for w in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            w.clear()
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
                catat_aktivitas(msg)
                self.refresh_ui_only()

    def delete_selected(self):
        from CRUD.Delete import proses_delete_massal
        reply = show_question(self, 'Konfirmasi Hapus Massal', f"Yakin ingin menghapus {len(self.selected_ids)} lowongan terpilih?")
        if reply == QMessageBox.Yes:
            success, msg, new_data = proses_delete_massal(self.selected_ids, self.data)
            if success:
                self.data = new_data
                self.simpan_data_async()
                catat_aktivitas(msg)
                self.selected_ids = set()
                self.refresh_ui_only()

    def show_job_details(self, job_data):
        dialog = JobDetailDialog(job_data, self)
        dialog.exec_()
