import sys
import os
import datetime
import re

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QLineEdit, QTextEdit, QDateEdit, QGridLayout, QDialog,
    QFrame, QComboBox, QCheckBox, QLayout, QMessageBox, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QDate, QSize, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QPixmap

_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_pages_dir)
if _pages_dir not in sys.path:
    sys.path.insert(0, _pages_dir)

from CRUD.Shared import muat_data, simpan_data, FIELDS
from modul_antarmuka_pengguna import KeyboardScrollArea, show_message, show_question
from Modul.modul_database import catat_aktivitas

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


# --- Job Dialog (Tampilan 2 Kolom) ---
class JobDialog(QDialog):
    def __init__(self, parent=None, job_data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Lowongan Baru" if not job_data else "Edit Lowongan")
        self.resize(750, 750)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.job_data = job_data
        self.inputs = {}
        self.setup_ui()
        if self.job_data:
            self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Main Container
        container = QFrame()
        container.setObjectName("MainContainer")
        container.setStyleSheet("""
            QFrame#MainContainer {
                background-color: white;
                border: 2px solid #2C687B;
                border-radius: 15px;
            }
        """)
        
        # Efek Bayangan (Drop Shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(container)
        
        inner_layout = QVBoxLayout(container)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: white; border-top-left-radius: 13px; border-top-right-radius: 13px; border: none;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        title_label = QLabel(self.windowTitle())
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #333; border: none; background: transparent;")
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("QPushButton { border: 1px solid #ddd; border-radius: 4px; font-size: 18px; color: #666; background-color: white;} QPushButton:hover { background-color: #f0f0f0; }")
        btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #eee; border: none;")
        
        inner_layout.addWidget(header_frame)
        inner_layout.addWidget(line)

        # Form Content
        scroll = KeyboardScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content_widget = QWidget()
        form_layout = QGridLayout(content_widget)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Helper untuk styling label dan input
        def create_field(label_text, widget, row, col, rowspan=1, colspan=1):
            container = QWidget()
            lay = QVBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(6) # Jarak rapat antara label dan input
            
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #111; font-weight: 500;")
            
            lay.addWidget(lbl)
            lay.addWidget(widget)
            form_layout.addWidget(container, row, col, rowspan, colspan)

        input_style = f"""
            QLineEdit, QTextEdit, QDateEdit, QComboBox {{
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: #fff;
                color: #333;
            }}
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {{
                border: 1px solid #2C687B;
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
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border: none;
            }}
        """

        # Baris 1: Judul & Perusahaan
        self.inputs['Judul_Pekerjaan'] = QLineEdit()
        self.inputs['Judul_Pekerjaan'].setPlaceholderText("cth. Frontend Developer")
        create_field("Judul Pekerjaan *", self.inputs['Judul_Pekerjaan'], 0, 0)

        self.inputs['Nama_Perusahaan'] = QLineEdit()
        self.inputs['Nama_Perusahaan'].setPlaceholderText("cth. PT Teknologi Maju")
        create_field("Nama Perusahaan *", self.inputs['Nama_Perusahaan'], 0, 1)

        # Baris 2: Jenis Pekerjaan & Lokasi
        self.inputs['Jenis_Pekerjaan'] = QComboBox()
        self.inputs['Jenis_Pekerjaan'].addItems(["Full-time", "Part-time", "Freelance", "Internship", "Contract"])
        create_field("Jenis Pekerjaan", self.inputs['Jenis_Pekerjaan'], 1, 0)

        self.inputs['Lokasi'] = QLineEdit()
        self.inputs['Lokasi'].setPlaceholderText("cth. Jakarta, Indonesia")
        create_field("Lokasi", self.inputs['Lokasi'], 1, 1)

        # Baris 3: Gaji & Tanggal Kadaluarsa
        self.inputs['Rentang_Gaji'] = QLineEdit()
        self.inputs['Rentang_Gaji'].setPlaceholderText("cth. 8.000.000")
        self.inputs['Rentang_Gaji'].textChanged.connect(self.format_salary)
        create_field("Gaji", self.inputs['Rentang_Gaji'], 2, 0)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setDate(QDate.currentDate().addDays(30))
        create_field("Tanggal Kadaluarsa", self.date_edit, 2, 1)

        # Baris 4: Skills (Full Width)
        self.inputs['Skills'] = QLineEdit()
        self.inputs['Skills'].setPlaceholderText("cth. React, Node.js, SQL")
        create_field("Skills (pisah koma)", self.inputs['Skills'], 3, 0, 1, 2)

        # Baris 5: Link Lowongan (Full Width)
        self.inputs['Link_Lowongan'] = QLineEdit()
        self.inputs['Link_Lowongan'].setPlaceholderText("https://...")
        create_field("Link Lowongan", self.inputs['Link_Lowongan'], 4, 0, 1, 2)

        # Baris 6: Deskripsi Pekerjaan (Full Width)
        self.inputs['Deskripsi_Pekerjaan'] = QTextEdit()
        self.inputs['Deskripsi_Pekerjaan'].setPlaceholderText("Deskripsi singkat...")
        self.inputs['Deskripsi_Pekerjaan'].setFixedHeight(100)
        create_field("Deskripsi Pekerjaan", self.inputs['Deskripsi_Pekerjaan'], 5, 0, 1, 2)

        # (Hidden Fields untuk kesesuaian dengan backend)
        self.inputs['Benefit_Pekerjaan'] = QLineEdit()
        self.inputs['Kualifikasi_Persyaratan'] = QLineEdit()
        self.inputs['Benefit_Pekerjaan'].hide()
        self.inputs['Kualifikasi_Persyaratan'].hide()

        content_widget.setStyleSheet(input_style)
        scroll.setWidget(content_widget)
        inner_layout.addWidget(scroll)

        # Footer Actions
        footer_line = QFrame()
        footer_line.setFrameShape(QFrame.HLine)
        footer_line.setStyleSheet("background-color: #eee;")
        inner_layout.addWidget(footer_line)

        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #F9FAFB; border-bottom-left-radius: 13px; border-bottom-right-radius: 13px; border: none;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        btn_cancel = QPushButton("Batal")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton { border: 1px solid #dcdcdc; border-radius: 6px; padding: 10px 25px; font-size: 15px; background-color: white; color: #555; }
            QPushButton:hover { background-color: #f8f8f8; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Simpan")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #2C687B; border-radius: 6px; padding: 10px 25px; font-size: 15px; color: white; font-weight: 500; border: none; }
            QPushButton:hover { background-color: #408699; }
        """)
        btn_save.clicked.connect(self.validate_and_accept)

        footer_layout.addStretch()
        footer_layout.addWidget(btn_cancel)
        footer_layout.addWidget(btn_save)
        inner_layout.addWidget(footer_frame)

    def format_salary(self, text):
        # Hapus semua karakter selain angka dan strip (-)
        clean_text = ''.join(c for c in text if c.isdigit() or c == '-')
        
        if not clean_text:
            self.inputs['Rentang_Gaji'].blockSignals(True)
            self.inputs['Rentang_Gaji'].setText("")
            self.inputs['Rentang_Gaji'].blockSignals(False)
            return

        # Format dengan pemisah ribuan (titik), pertahankan rentang (-)
        parts = clean_text.split('-')
        formatted_parts = []
        for part in parts:
            if part.isdigit():
                formatted_parts.append("{:,}".format(int(part)).replace(',', '.'))
            else:
                formatted_parts.append(part)
        
        formatted = '-'.join(formatted_parts)
        
        self.inputs['Rentang_Gaji'].blockSignals(True)
        self.inputs['Rentang_Gaji'].setText(formatted)
        self.inputs['Rentang_Gaji'].blockSignals(False)

    def load_data(self):
        for key, widget in self.inputs.items():
            val = self.job_data.get(key, "")
            if isinstance(widget, QLineEdit):
                widget.setText(val)
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(val)
            elif isinstance(widget, QComboBox):
                idx = widget.findText(val)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
                    
        date_str = self.job_data.get("Tanggal_Kadaluarsa", "")
        try:
            date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
        except (ValueError, TypeError):
            pass

    def validate_and_accept(self):
        if not self.inputs['Judul_Pekerjaan'].text().strip():
            show_message(self, "Validasi Gagal", "Judul Pekerjaan wajib diisi!")
            return
        if not self.inputs['Nama_Perusahaan'].text().strip():
            show_message(self, "Validasi Gagal", "Nama Perusahaan wajib diisi!")
            return
            
        # Validasi tanggal kadaluarsa (cegah tanggal lampau)
        if self.date_edit.date() < QDate.currentDate():
            show_message(
                self, 
                "Tanggal Tidak Valid", 
                f"Tanggal kadaluarsa tidak boleh kurang dari tanggal hari ini ({QDate.currentDate().toString('dd/MM/yyyy')}).\n"
                "Silakan perbaiki tanggal sebelum menyimpan."
            )
            return
            
        # Validasi Rentang Gaji (Harus mengandung angka)
        gaji = self.inputs['Rentang_Gaji'].text().strip()
        if gaji:
            if not re.search(r'\d', gaji):
                show_message(self, "Validasi Gagal", "Gaji harus berupa angka.")
                return
            if len(gaji.replace(".", "").replace("-", "")) < 3:
                show_message(self, "Validasi Gagal", "Gaji terlalu pendek.")
                return

        self.accept()

    def get_data(self):
        data = {}
        if self.job_data and "id" in self.job_data:
            data["id"] = self.job_data["id"]
        else:
            data["id"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                data[key] = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()
                
        dt = self.date_edit.date()
        data["Tanggal_Kadaluarsa"] = f"{dt.day():02d}/{dt.month():02d}/{dt.year()}"
        return data


# --- Job Detail Dialog (Tampilan Read-Only) ---
class JobDetailDialog(QDialog):
    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.job_data = job_data
        self.setWindowTitle("Detail Lowongan Pekerjaan")
        self.resize(600, 750)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Main Container
        container = QFrame()
        container.setObjectName("DetailContainer")
        container.setStyleSheet("""
            QFrame#DetailContainer {
                background-color: white;
                border: 2px solid #2C687B;
                border-radius: 15px;
            }
        """)
        
        # Efek Bayangan (Drop Shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(container)
        
        inner_layout = QVBoxLayout(container)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #F8FAFC; border-bottom: 1px solid #E2E8F0; border-top-left-radius: 13px; border-top-right-radius: 13px; border: none;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        title_label = QLabel("Rincian Pekerjaan")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1E293B; border: none; background: transparent;")
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { 
                border: 1px solid #E2E8F0; border-radius: 6px; 
                font-size: 20px; color: #64748B; background-color: white;
            } 
            QPushButton:hover { background-color: #F1F5F9; color: #0F172A; }
        """)
        btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        inner_layout.addWidget(header_frame)

        # Content with Scroll Area
        scroll = KeyboardScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 25, 30, 35)
        content_layout.setSpacing(20)
        
        scroll.setWidget(content_widget)
        inner_layout.addWidget(scroll)

        def add_detail_section(title, value):
            if not value or value == "-":
                return
            lbl_title = QLabel(title)
            lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl_title.setStyleSheet("color: #777; margin-bottom: 2px;")
            
            lbl_value = QLabel(value)
            lbl_value.setFont(QFont("Segoe UI", 12))
            lbl_value.setStyleSheet("color: #222;")
            lbl_value.setWordWrap(True)
            lbl_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            content_layout.addWidget(lbl_title)
            content_layout.addWidget(lbl_value)

        # Basic Info
        info_layout = QGridLayout()
        info_layout.setSpacing(15)
        
        def create_grid_item(title, value, row, col):
            container = QWidget()
            lay = QVBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(6)
            t = QLabel(title)
            t.setStyleSheet("color: #666; font-size: 13px; font-weight: bold;")
            v = QLabel(value if value else "-")
            v.setStyleSheet("color: #111; font-size: 16px;")
            v.setWordWrap(True)
            v.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lay.addWidget(t)
            lay.addWidget(v)
            info_layout.addWidget(container, row, col)

        create_grid_item("PERUSAHAAN", self.job_data.get("Nama_Perusahaan", "-"), 0, 0)
        create_grid_item("JENIS PEKERJAAN", self.job_data.get("Jenis_Pekerjaan", "-"), 0, 1)
        create_grid_item("LOKASI", self.job_data.get("Lokasi", "-"), 1, 0)
        create_grid_item("RENTANG GAJI", self.job_data.get("Rentang_Gaji", "-"), 1, 1)
        create_grid_item("KADALUARSA", self.job_data.get("Tanggal_Kadaluarsa", "-"), 2, 0)
        create_grid_item("SKILLS", self.job_data.get("Skills", "-"), 2, 1)

        # Judul Besar
        lbl_judul = QLabel(self.job_data.get("Judul_Pekerjaan", "-"))
        lbl_judul.setFont(QFont("Segoe UI", 20, QFont.Bold))
        lbl_judul.setStyleSheet("color: #111;")
        lbl_judul.setWordWrap(True)
        lbl_judul.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content_layout.addWidget(lbl_judul)
        
        content_layout.addLayout(info_layout)
        
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setStyleSheet("background-color: #eee; margin: 10px 0;")
        content_layout.addWidget(divider1)
        
        add_detail_section("Link Lowongan", self.job_data.get("Link_Lowongan", "-"))
        
        desc = self.job_data.get("Deskripsi_Pekerjaan", "").strip()
        if desc and desc != "-":
            lbl_desc_title = QLabel("Deskripsi Pekerjaan")
            lbl_desc_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl_desc_title.setStyleSheet("color: #333; margin-top: 10px;")
            
            text_desc = QTextEdit()
            text_desc.setReadOnly(True)
            text_desc.setPlainText(desc)
            text_desc.setStyleSheet("QTextEdit { border: 1px solid #ddd; border-radius: 8px; padding: 12px; background-color: #fafafa; color: #444; font-size: 13px; line-height: 1.5; }")
            text_desc.setMinimumHeight(150)
            
            content_layout.addWidget(lbl_desc_title)
            content_layout.addWidget(text_desc)
            
        benefits = self.job_data.get("Benefit_Pekerjaan", "").strip()
        if benefits and benefits != "-":
            add_detail_section("Benefit Pekerjaan", benefits)
            
        reqs = self.job_data.get("Kualifikasi_Persyaratan", "").strip()
        if reqs and reqs != "-":
            add_detail_section("Kualifikasi & Persyaratan", reqs)

        content_layout.addStretch()

# --- Job Card Widget ---
class JobCardWidget(QFrame):
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)
    checkbox_toggled = pyqtSignal(dict, bool)
    card_clicked = pyqtSignal(dict)

    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.job_data = job_data
        self.setFixedHeight(240)
        self.setMinimumWidth(320)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            if not isinstance(child, (QPushButton, QCheckBox)):
                self.card_clicked.emit(self.job_data)
        super().mousePressEvent(event)

    def setup_ui(self):
        self.setObjectName("JobCard")
        self.setStyleSheet("""
            QFrame#JobCard {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 10px;
            }
            QFrame#JobCard:hover {
                border: 1px solid #2C687B;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 12)
        main_layout.setSpacing(8)

        # Header Row: Initial Logo, Title & Company, Checkbox
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        # Initial Logo
        initial = self.job_data.get("Nama_Perusahaan", "X")[:2].upper()
        lbl_logo = QLabel(initial)
        lbl_logo.setFixedSize(48, 48)
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        # Determine color based on initial
        colors = ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff3e0", "#f3e5f5"]
        text_colors = ["#880e4f", "#0d47a1", "#1b5e20", "#e65100", "#4a148c"]
        idx = sum(ord(c) for c in initial) % len(colors)
        lbl_logo.setStyleSheet(f"background-color: {colors[idx]}; color: {text_colors[idx]}; border-radius: 12px; border: none;")
        header_layout.addWidget(lbl_logo)

        # Title & Company
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        judul = self.job_data.get("Judul_Pekerjaan", "Tanpa Judul")
        if len(judul) > 23: judul = judul[:21] + "..."
        lbl_title = QLabel(judul)
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_title.setStyleSheet("color: #111; border: none;")
        
        lbl_company = QLabel(self.job_data.get("Nama_Perusahaan", "-"))
        lbl_company.setFont(QFont("Segoe UI", 11))
        lbl_company.setStyleSheet("color: #777; border: none;")
        
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_company)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator { width: 16px; height: 16px; border: 1.5px solid #ccc; border-radius: 4px; }
            QCheckBox::indicator:checked { background-color: #2C687B; border-color: #2C687B; image: url('✓'); }
        """)
        self.checkbox.toggled.connect(lambda checked: self.checkbox_toggled.emit(self.job_data, checked))
        header_layout.addWidget(self.checkbox, alignment=Qt.AlignTop)
        
        main_layout.addLayout(header_layout)

        # Badges Row (Type, Remote, Status)
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(6)
        
        def create_badge(text, bg_color, text_color):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: 10px; padding: 3px 10px; font-size: 11px; font-weight: bold; border: none;")
            return lbl

        # Jenis Pekerjaan
        jenis = self.job_data.get("Jenis_Pekerjaan", "Full-time")
        if jenis == "Internship":
            badges_layout.addWidget(create_badge(jenis, "#fce4ec", "#c2185b"))
        else:
            badges_layout.addWidget(create_badge(jenis, "#e8f0fe", "#1a73e8"))

        # Remote Badge
        lokasi = self.job_data.get("Lokasi", "")
        if "remote" in lokasi.lower() or "remote" in jenis.lower():
            badges_layout.addWidget(create_badge("Remote", "#e8f5e9", "#2e7d32"))

        # Kadaluarsa Badge check
        date_str = self.job_data.get("Tanggal_Kadaluarsa", "")
        kadaluarsa_date = None
        is_warn = False
        try:
            d = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            kadaluarsa_date = d
            if (d - datetime.date.today()).days <= 7:
                badges_layout.addWidget(create_badge("Segera Berakhir", "#ffebee", "#c62828"))
                is_warn = True
        except: pass
        
        badges_layout.addStretch()
        main_layout.addLayout(badges_layout)

        main_layout.addSpacing(4) # extra spacing before location

        # Info Row (Location & Salary)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        lbl_loc = QLabel(f"📍  {self.job_data.get('Lokasi', '-')}")
        lbl_loc.setStyleSheet("color: #666; font-size: 12px; border: none;")
        info_layout.addWidget(lbl_loc)

        raw_sal = self.job_data.get('Rentang_Gaji', '-')
        
        def shorten_number(num_str):
            try:
                num = int(num_str.replace('.', ''))
                if num >= 1_000_000_000:
                    val = f"{num / 1_000_000_000:.1f}".replace('.0', '')
                    return f"{val}M"
                elif num >= 1_000_000:
                    val = f"{num / 1_000_000:.1f}".replace('.0', '')
                    return f"{val}jt"
                elif num >= 1_000:
                    val = f"{num / 1_000:.1f}".replace('.0', '')
                    return f"{val}k"
                return str(num)
            except:
                return num_str

        formatted_sal = "-"
        if raw_sal and raw_sal != "-":
            parts = [p.strip() for p in raw_sal.split('-')]
            formatted_parts = [shorten_number(p) for p in parts]
            formatted_sal = " - ".join(formatted_parts)

        lbl_sal = QLabel(f"💲  {formatted_sal}")
        lbl_sal.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_sal.setStyleSheet("color: #20a082; border: none;")
        info_layout.addWidget(lbl_sal)
        main_layout.addLayout(info_layout)

        main_layout.addSpacing(4)

        # Skills Row (Max 3 items)
        skills = [s.strip() for s in self.job_data.get('Skills', '').split(',') if s.strip()]
        if skills:
            skills_layout = QHBoxLayout()
            skills_layout.setSpacing(6)
            for s in skills[:3]:
                lbl_s = QLabel(s)
                lbl_s.setStyleSheet("background-color: #f4f4f4; color: #444; border-radius: 8px; padding: 4px 10px; font-size: 11px; border: none;")
                skills_layout.addWidget(lbl_s)
            if len(skills) > 3:
                lbl_more = QLabel(f"+{len(skills)-3}")
                lbl_more.setStyleSheet("background-color: #e8e8e8; color: #555; border-radius: 8px; padding: 4px 10px; font-size: 11px; border: none;")
                skills_layout.addWidget(lbl_more)
            skills_layout.addStretch()
            main_layout.addLayout(skills_layout)
        else:
            main_layout.addSpacing(25) # Spacer if no skills

        main_layout.addStretch()

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #f0f0f0; border: none; height: 1px;")
        main_layout.addWidget(divider)

        # Footer Row (Kadaluarsa + Action Buttons)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 4, 0, 0)
        
        kad_layout = QVBoxLayout()
        kad_layout.setSpacing(0)
        lbl_k_lbl = QLabel("Kadaluarsa")
        lbl_k_lbl.setStyleSheet("color: #888; font-size: 11px; border: none;")
        
        formatted_date = "-"
        if kadaluarsa_date:
            formatted_date = kadaluarsa_date.strftime("%d/%m/%Y")
            
        lbl_k_val = QLabel(formatted_date)
        lbl_k_val.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_k_val.setStyleSheet(f"color: {'#c62828' if is_warn else '#333'}; border: none;")
        
        kad_layout.addWidget(lbl_k_lbl)
        kad_layout.addWidget(lbl_k_val)
        footer_layout.addLayout(kad_layout)
        
        footer_layout.addStretch()
        
        btn_style = "QPushButton { border: 1px solid #ddd; border-radius: 6px; background: white; font-size: 14px; padding: 0px;} QPushButton:hover { background: #f5f5f5; }"
        
        btn_edit = QPushButton()
        btn_edit.setIcon(QIcon(edit_icon_path))
        btn_edit.setIconSize(QSize(18, 18))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.job_data))
        
        btn_del = QPushButton()
        btn_del.setIcon(QIcon(trash_icon_path))
        btn_del.setIconSize(QSize(18, 18))
        btn_del.setFixedSize(32, 32)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet("QPushButton { border: 1px solid #ddd; border-radius: 6px; background: white; font-size: 14px; padding: 0px;} QPushButton:hover { background: #fee; border-color: #ffcdd2; color: red; }")
        btn_del.clicked.connect(lambda: self.delete_clicked.emit(self.job_data))

        footer_layout.addWidget(btn_edit, alignment=Qt.AlignBottom)
        footer_layout.addWidget(btn_del, alignment=Qt.AlignBottom)
        
        main_layout.addLayout(footer_layout)


# --- Main Page ---
class JobPostingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ids = set()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
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
        
        self.btn_add = QPushButton(" ➕ Tambah Data ")
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
        
        # Tambahkan search icon di sisi kiri
        self.search_action = self.search_bar.addAction(QIcon(search_icon_path), QLineEdit.LeadingPosition)
        
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
        self.scroll_area = KeyboardScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Sembunyikan border scrollarea tapi biarkan background transparan
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
        import copy
        import threading
        data_copy = copy.deepcopy(self.data)
        threading.Thread(target=simpan_data, args=(data_copy,), daemon=True).start()

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

    def add_data(self):
        dialog = JobDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            self.data.append(new_data)
            self.simpan_data_async()
            catat_aktivitas(f"<b>Lowongan Ditambah</b><br>{new_data.get('Judul_Pekerjaan')}")
            self.refresh_ui_only()

    def edit_data(self, job_data):
        dialog = JobDialog(self, job_data=job_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_data()
            for i, j in enumerate(self.data):
                if j.get("id") == job_data.get("id"):
                    self.data[i] = updated_data
                    break
            self.simpan_data_async()
            catat_aktivitas(f"<b>Lowongan Diperbarui</b><br>{updated_data.get('Judul_Pekerjaan')}")
            self.refresh_ui_only()

    def delete_single_data(self, job_data):
        reply = show_question(self, 'Konfirmasi Hapus', "Yakin ingin menghapus lowongan ini?")
        if reply == QMessageBox.Yes:
            self.data = [j for j in self.data if j.get("id") != job_data.get("id")]
            self.simpan_data_async()
            catat_aktivitas(f"<b>Lowongan Dihapus</b><br>{job_data.get('Judul_Pekerjaan')}")
            self.refresh_ui_only()

    def delete_selected(self):
        reply = show_question(self, 'Konfirmasi Hapus Massal', f"Yakin ingin menghapus {len(self.selected_ids)} lowongan terpilih?")
        if reply == QMessageBox.Yes:
            jumlah = len(self.selected_ids)
            self.data = [j for j in self.data if j.get("id") not in self.selected_ids]
            self.simpan_data_async()
            catat_aktivitas(f"<b>Lowongan Dihapus</b><br>{jumlah} data lowongan")
            self.refresh_ui_only()

    def show_job_details(self, job_data):
        dialog = JobDetailDialog(job_data, self)
        dialog.exec_()

