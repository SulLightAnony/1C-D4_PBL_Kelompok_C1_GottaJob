import sys
import os
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QLineEdit, QTextEdit, QGridLayout, QDialog,
    QFrame, QComboBox, QCheckBox, QLayout, QMessageBox, QSpacerItem, QSizePolicy,
    QStackedWidget, QSpinBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QSize, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QPixmap
import calendar

_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_pages_dir)
if _pages_dir not in sys.path:
    sys.path.insert(0, _pages_dir)

from CRUD.Shared import muat_data, simpan_data, FIELDS
from CRUD.Create import gui_tambah_data
from CRUD.Read import gui_muat_data
from CRUD.Update import gui_perbarui_data
from CRUD.Delete import gui_hapus_data_single, gui_hapus_data_massal

from CRUD.Create import JobDialog
from CRUD.Read import JobCardWidget, JobDetailDialog

# Path assets
down_icon_path = os.path.join(_root_dir, "assets", "Job Archive", "down.png").replace("\\", "/")
refresh_icon_path = os.path.join(_root_dir, "assets", "Job Archive", "refresh.png")

post_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "post.png")
trash_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "trash-can.png")
currency_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "save-money.png")
edit_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "edit.png")
location_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "gps.png")
check_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "check.png")
search_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "search.png")
plus_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "plus.png")


# --- FlowLayout Implementation ---
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        if not self.itemList:
            return 0
            
        # Gunakan ukuran minimum item pertama sebagai referensi
        ref_min_w = self.itemList[0].minimumSize().width()
        if ref_min_w <= 0:
            ref_min_w = 320
            
        spaceX = self.spacing()
        spaceY = self.spacing()
        
        available_width = rect.width()
        
        # Hitung jumlah kolom maksimal yang muat
        if available_width < ref_min_w:
            cols = 1
        else:
            cols = max(1, (available_width + spaceX) // (ref_min_w + spaceX))
            
        # Hitung lebar per item agar stretch sampai mentok
        item_w = (available_width - (cols - 1) * spaceX) // cols
        
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        
        for i, item in enumerate(self.itemList):
            item_h = item.sizeHint().height()
            
            if not testOnly:
                item.setGeometry(QRect(x, y, item_w, item_h))
                
            x += item_w + spaceX
            lineHeight = max(lineHeight, item_h)
            
            # Pindah ke baris baru jika kolom sudah terpenuhi
            if (i + 1) % cols == 0:
                x = rect.x()
                y += lineHeight + spaceY
                lineHeight = 0

        # Kembalikan tinggi total
        if len(self.itemList) % cols != 0:
            return y + lineHeight - rect.y()
        else:
            return y - rect.y() - spaceY if y > rect.y() else 0


class JobPostingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ids = set()
        self.data = []
        self._init_stack()
        self.load_data()

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

        self.btn_refresh = QPushButton(" Segarkan")
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
        
        def create_stat_card(title, count_ref, badge_text, badge_color, badge_bg):
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

        self.card_total, self.lbl_count_total = create_stat_card("TOTAL POSTING", "0", "Aktif", "#2e7d32", "#e8f5e9")
        self.card_ft, self.lbl_count_ft = create_stat_card("FULL-TIME", "0", "Terbuka", "#1a73e8", "#e8f0fe")
        self.card_rm, self.lbl_count_rm = create_stat_card("REMOTE", "0", "Aktif", "#2e7d32", "#e8f5e9")
        self.card_warn, self.lbl_count_warn = create_stat_card("SEGERA KADALUARSA", "0", "⚠️ Perhatian", "#f57c00", "#fff3e0")
        
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
        self.combo_filter.addItems(["Semua Jenis", "Full-time", "Part-time", "Freelance", "Internship", "Contract"])
        self.combo_filter.setFixedSize(150, 36)
        
        combo_style = f"""
            QComboBox {{
                border: 1px solid #ddd;
                border-radius: 18px;
                padding: 0 15px;
                font-size: 13px;
                background-color: white;
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
        """
        self.combo_filter.setStyleSheet(combo_style)
        self.combo_filter.currentTextChanged.connect(self.filter_cards)
        
        filter_layout.addWidget(self.search_bar)
        filter_layout.addWidget(self.combo_filter)
        
        self.main_layout.addLayout(filter_layout)

        # Cards Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.flow_layout = FlowLayout(self.cards_container, margin=0, spacing=20)
        
        self.scroll_area.setWidget(self.cards_container)
        self.main_layout.addWidget(self.scroll_area)

    def load_data(self):
        gui_muat_data(self)

    def update_statistics(self):
        total = len(self.data)
        ft = sum(1 for j in self.data if j.get('Jenis_Pekerjaan', '').lower() == 'full-time')
        rm = sum(1 for j in self.data if 'remote' in j.get('Lokasi', '').lower() or 'remote' in j.get('Jenis_Pekerjaan', '').lower())
        
        warn = 0
        for j in self.data:
            try:
                d = datetime.datetime.strptime(j.get("Tanggal_Kadaluarsa", ""), "%d/%m/%Y").date()
                if (d - datetime.date.today()).days <= 7:
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
        import datetime as dt_mod

        page = QWidget()
        page.setStyleSheet("background-color: #F3F4F6;")
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

        lbl_title = QLabel("Tambah Lowongan Baru")
        lbl_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        lbl_title.setStyleSheet("color: #222;")

        header.addWidget(btn_back)
        header.addSpacing(16)
        header.addWidget(lbl_title)
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
            container.setStyleSheet("background: transparent; border: none;")
            v = QVBoxLayout(container)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #555; font-weight: 600; border: none;")
            v.addWidget(lbl)
            v.addWidget(widget)
            return container

        field_style = """
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                border: 1px solid #dcdcdc; border-radius: 8px;
                padding: 10px 14px; font-size: 14px;
                background-color: #fafafa; color: #333;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #2C687B; background-color: #fff;
            }
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
        self.f_jenis.addItems(["Full-time", "Part-time", "Freelance", "Internship", "Contract"])
        self.f_lokasi = QLineEdit(); self.f_lokasi.setPlaceholderText("cth. Jakarta, Indonesia")
        grid.addWidget(make_field("Jenis Pekerjaan", self.f_jenis), 1, 0)
        grid.addWidget(make_field("Lokasi", self.f_lokasi), 1, 1)

        # Baris 2: Gaji & Tanggal (Kalender)
        self.f_gaji = QLineEdit(); self.f_gaji.setPlaceholderText("cth. Rp 8jt - 15jt")

        self.f_date = QDateEdit()
        self.f_date.setCalendarPopup(True)
        self.f_date.setDisplayFormat("dd/MM/yyyy")
        self.f_date.setDate(QDate.currentDate().addDays(30))
        self.f_date.setMinimumDate(QDate.currentDate().addDays(1))

        grid.addWidget(make_field("Rentang Gaji", self.f_gaji), 2, 0)
        grid.addWidget(make_field("Tanggal Kadaluarsa", self.f_date), 2, 1)

        # Baris 3: Skills (full width)
        self.f_skills = QLineEdit(); self.f_skills.setPlaceholderText("cth. React, Node.js, SQL (pisah koma)")
        grid.addWidget(make_field("Skills", self.f_skills), 3, 0, 1, 2)

        # Baris 4: Link (full width)
        self.f_link = QLineEdit(); self.f_link.setPlaceholderText("https://...")
        grid.addWidget(make_field("Link Lowongan", self.f_link), 4, 0, 1, 2)

        # Baris 5: Deskripsi (full width)
        self.f_desc = QTextEdit(); self.f_desc.setPlaceholderText("Deskripsi singkat...")
        self.f_desc.setFixedHeight(100)
        grid.addWidget(make_field("Deskripsi Pekerjaan", self.f_desc), 5, 0, 1, 2)

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

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _save_new_job(self):
        """Validasi dan simpan data dari halaman form tambah."""
        import datetime as dt_mod
        if not self.f_judul.text().strip():
            QMessageBox.warning(self, "Validasi Gagal", "Judul Pekerjaan wajib diisi!")
            return
        if not self.f_perusahaan.text().strip():
            QMessageBox.warning(self, "Validasi Gagal", "Nama Perusahaan wajib diisi!")
            return

        # Validasi Tanggal Kadaluarsa (Preventif)
        selected_qdate = self.f_date.date()
        if selected_qdate <= QDate.currentDate():
            QMessageBox.warning(self, "Validasi Gagal", "Tanggal Kadaluarsa tidak boleh hari ini atau di masa lalu!")
            return

        new_data = {
            "id": dt_mod.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Judul_Pekerjaan": self.f_judul.text().strip(),
            "Nama_Perusahaan": self.f_perusahaan.text().strip(),
            "Jenis_Pekerjaan": self.f_jenis.currentText(),
            "Lokasi": self.f_lokasi.text().strip(),
            "Rentang_Gaji": self.f_gaji.text().strip(),
            "Skills": self.f_skills.text().strip(),
            "Link_Lowongan": self.f_link.text().strip(),
            "Deskripsi_Pekerjaan": self.f_desc.toPlainText().strip(),
            "Benefit_Pekerjaan": "",
            "Kualifikasi_Persyaratan": "",
            "Tanggal_Kadaluarsa": f"{selected_qdate.day():02d}/{selected_qdate.month():02d}/{selected_qdate.year()}",
        }

        self.data.append(new_data)
        simpan_data(self.data)

        # Reset form
        for w in [self.f_judul, self.f_perusahaan, self.f_lokasi, self.f_gaji, self.f_skills, self.f_link]:
            w.clear()
        self.f_desc.clear()
        self.f_jenis.setCurrentIndex(0)

        self.page_stack.setCurrentIndex(0)
        self.load_data()
        QMessageBox.information(self, "Berhasil", "Lowongan berhasil ditambahkan!")

    def add_data(self):
        """Beralih ke halaman form tambah."""
        self.page_stack.setCurrentIndex(1)

    def edit_data(self, job_data):
        gui_perbarui_data(self, JobDialog, job_data)

    def delete_single_data(self, job_data):
        gui_hapus_data_single(self, job_data)

    def delete_selected(self):
        gui_hapus_data_massal(self)

    def show_job_details(self, job_data):
        dialog = JobDetailDialog(job_data, self)
        dialog.exec_()

