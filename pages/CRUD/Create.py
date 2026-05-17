import os
import sys
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QFrame, QGridLayout, 
    QStyledItemDelegate, QCalendarWidget, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator, QIcon

_crud_dir = os.path.dirname(os.path.abspath(__file__))
_pages_dir = os.path.dirname(_crud_dir)
_job_posting_dir = os.path.join(_pages_dir, "Job Posting")
_modul_dir = os.path.join(_pages_dir, "Modul")

for _p in [_pages_dir, _job_posting_dir, _modul_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from constants import down_icon_path
from modul_antarmuka_pengguna import KeyboardScrollArea
from skill_tag_input import SkillTagInput

class JobFormPage(QWidget):
    back_clicked = pyqtSignal()
    save_requested = pyqtSignal(dict, str) # form_data dict, editing_job_id (None if new)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editing_job_id = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self)
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
        btn_back.clicked.connect(lambda: self.back_clicked.emit())

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

        cal = self.f_date.calendarWidget()
        cal.setStyleSheet("""
            QCalendarWidget { background-color: white; border: 1px solid #B2D2D9; border-radius: 8px; }
            QCalendarWidget QAbstractItemView { background-color: white; color: #1E3A4A; selection-background-color: #1D4E5F; selection-color: white; outline: none; font-size: 13px; }
            QCalendarWidget QAbstractItemView:disabled { color: #B2D2D9; }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #1D4E5F; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 4px; }
            QCalendarWidget QToolButton { color: white; background-color: transparent; border: none; font-weight: bold; font-size: 14px; padding: 4px 8px; }
            QCalendarWidget QToolButton:hover { background-color: rgba(255,255,255,0.15); border-radius: 4px; }
            QCalendarWidget QToolButton::menu-indicator { image: none; }
            QCalendarWidget QSpinBox { color: white; background-color: transparent; border: none; font-weight: bold; font-size: 14px; }
            QCalendarWidget QMenu { background-color: white; color: #1E3A4A; border: 1px solid #B2D2D9; font-size: 13px; }
            QCalendarWidget QMenu::item:selected { background-color: #E2EFF1; color: #1D4E5F; }
            QCalendarWidget QHeaderView::section { background-color: #F0F7F9; color: #2C687B; font-weight: bold; font-size: 12px; border: none; padding: 4px; }
        """)

        self.f_hard_skills = SkillTagInput(placeholder="Ketik hard skill & Enter...", btn_text="Tambah")
        self.f_soft_skills = SkillTagInput(placeholder="Ketik soft skill & Enter...", btn_text="Tambah")

        hard_group = QWidget(); hard_group.setStyleSheet("background: transparent;")
        hard_lay = QVBoxLayout(hard_group); hard_lay.setContentsMargins(0,0,0,0); hard_lay.setSpacing(4)
        hard_lay.addWidget(self.f_hard_skills)
        hard_lay.addWidget(QLabel("<font color='#777' size='1'>Ketik hard skill lalu tekan Enter atau klik Tambah</font>"))

        soft_group = QWidget(); soft_group.setStyleSheet("background: transparent;")
        soft_lay = QVBoxLayout(soft_group); soft_lay.setContentsMargins(0,0,0,0); soft_lay.setSpacing(4)
        soft_lay.addWidget(self.f_soft_skills)
        soft_lay.addWidget(QLabel("<font color='#777' size='1'>Ketik soft skill lalu tekan Enter atau klik Tambah</font>"))

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

        self.form_field_containers = [
            (make_field("Judul Pekerjaan *", self.f_judul), False),
            (make_field("Nama Perusahaan *", self.f_perusahaan), False),
            (make_field("Jenis Pekerjaan", self.f_jenis), False),
            (make_field("Lokasi", self.f_lokasi), False),
            (make_field("Rentang Gaji (Angka Saja)", gaji_container), False),
            (make_field("Tanggal Kadaluarsa", self.f_date), False),
            (make_field("Hard Skills", hard_group), False),
            (make_field("Soft Skills", soft_group), False),
            (make_field("Kategori Pekerjaan", self.f_kategori), True),
            (make_field("Link Lowongan", self.f_link), True),
            (make_field("Deskripsi Pekerjaan", self.f_desc), True),
            (make_field("Benefit Pekerjaan", self.f_benefit), False),
            (make_field("Kualifikasi Persyaratan", self.f_kualifikasi), False)
        ]

        self.form_grid = grid
        self.refresh_form_layout() 

        card_layout.addLayout(grid)

        btn_save = QPushButton("Simpan Lowongan")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(44)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #2C687B; border-radius: 8px; color: white;
                          font-size: 15px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #408699; }
        """)
        btn_save.clicked.connect(self._on_save_clicked)
        card_layout.addWidget(btn_save)

        for field in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            field.returnPressed.connect(self._on_save_clicked)

        scroll = KeyboardScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        scroll.setWidget(card)
        
        layout.addWidget(scroll)

    def refresh_form_layout(self):
        if not hasattr(self, 'form_grid') or not hasattr(self, 'form_field_containers'):
            return
        while self.form_grid.count():
            item = self.form_grid.takeAt(0)
            
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
        super().resizeEvent(event)
        self.refresh_form_layout()

    def set_mode_add(self):
        self.editing_job_id = None
        self.lbl_form_title.setText("Tambah Lowongan Baru")
        self._clear_fields()
        self.f_date.setDate(QDate.currentDate().addDays(30))

    def set_mode_edit(self, job_data):
        self.editing_job_id = job_data.get("id")
        self.lbl_form_title.setText("Edit Lowongan")
        self._clear_fields()
        
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
            
        h_raw = job_data.get("Hard_Skills", "")
        s_raw = job_data.get("Soft_Skills", "")
        if not h_raw and not s_raw and job_data.get("Skills"):
            parts = job_data.get("Skills", "").split("||")
            h_raw = parts[0] if len(parts) > 0 else ""
            s_raw = parts[1] if len(parts) > 1 else ""
            
        self.f_hard_skills.load_skills([s.strip() for s in h_raw.replace(",", "|").split("|") if s.strip()])
        self.f_soft_skills.load_skills([s.strip() for s in s_raw.replace(",", "|").split("|") if s.strip()])
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

    def _clear_fields(self):
        for w in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji_min, self.f_gaji_max, self.f_link]:
            w.clear()
        self.f_kategori.setCurrentIndex(0)
        self.f_kategori.lineEdit().clear()
        self.f_hard_skills.clear_all()
        self.f_soft_skills.clear_all()
        self.f_desc.clear()
        self.f_benefit.clear_all()
        self.f_kualifikasi.clear_all()
        self.f_jenis.setCurrentIndex(0)

    def _on_save_clicked(self):
        form_data = {
            "judul": self.f_judul.text().strip(),
            "perusahaan": self.f_perusahaan.text().strip(),
            "jenis": self.f_jenis.currentText(),
            "lokasi": self.f_lokasi.text().strip(),
            "gaji_min": self.f_gaji_min.text().strip(),
            "gaji_max": self.f_gaji_max.text().strip(),
            "hard_skills": self.f_hard_skills.get_skills(),
            "soft_skills": self.f_soft_skills.get_skills(),
            "link": self.f_link.text().strip(),
            "desc": self.f_desc.toPlainText().strip(),
            "benefit": "|".join(self.f_benefit.get_skills()),
            "kualifikasi": "|".join(self.f_kualifikasi.get_skills()),
            "kategori": self.f_kategori.currentText().strip(),
            "date": self.f_date.date()
        }
        self.save_requested.emit(form_data, self.editing_job_id)


def proses_create_job(form_data, current_data):
    from PyQt5.QtCore import QDate

    judul = form_data.get('judul', '').strip()
    perusahaan = form_data.get('perusahaan', '').strip()

    if not judul:
        return False, "Judul Pekerjaan wajib diisi!", current_data
    if not perusahaan:
        return False, "Nama Perusahaan wajib diisi!", current_data

    selected_date = form_data.get('date', QDate.currentDate())
    g_min = form_data.get('gaji_min', '').strip()
    g_max = form_data.get('gaji_max', '').strip()

    gaji = ""
    if g_min and g_max:
        gaji = f"{g_min} - {g_max}"
    elif g_min:
        gaji = g_min

    baru = {
        "id": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Judul_Pekerjaan": judul,
        "Nama_Perusahaan": perusahaan,
        "Jenis_Pekerjaan": form_data.get('jenis', ''),
        "Lokasi": form_data.get('lokasi', '').strip(),
        "Rentang_Gaji": gaji,
        "Hard_Skills": ", ".join(form_data.get('hard_skills', [])),
        "Soft_Skills": ", ".join(form_data.get('soft_skills', [])),
        "Skills": ", ".join(form_data.get('hard_skills', [])) + "||" + ", ".join(form_data.get('soft_skills', [])),
        "Link_Lowongan": form_data.get('link', '').strip(),
        "Deskripsi_Pekerjaan": form_data.get('desc', ''),
        "Benefit_Pekerjaan": form_data.get('benefit', ''),
        "Kualifikasi_Persyaratan": form_data.get('kualifikasi', ''),
        "Kategori": form_data.get('kategori', ''),
        "Tanggal_Kadaluarsa": selected_date.toString("dd/MM/yyyy"),
        "Is_lamar": False,
        "source": "job_posting"
    }

    current_data.append(baru)
    return True, "Lowongan berhasil ditambahkan!", current_data
