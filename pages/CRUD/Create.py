import os
import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QGridLayout, QFrame, QLineEdit, QTextEdit, QComboBox, QDateEdit, QMessageBox
from PyQt5.QtCore import Qt, QDate
import calendar
from PyQt5.QtGui import QFont

from CRUD.Shared import simpan_data

_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_pages_dir)
down_icon_path = os.path.join(_root_dir, "assets", "Job Archive", "down.png").replace("\\", "/")

# --- Job Dialog (Tampilan 2 Kolom) ---
class JobDialog(QDialog):
    def __init__(self, parent=None, job_data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Lowongan Baru" if not job_data else "Edit Lowongan")
        self.resize(700, 600)
        self.setStyleSheet("background-color: white;")
        self.job_data = job_data
        self.inputs = {}
        self.setup_ui()
        if self.job_data:
            self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        title_label = QLabel(self.windowTitle())
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #333;")
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet("QPushButton { border: 1px solid #ddd; border-radius: 4px; font-size: 18px; color: #666; background-color: white;} QPushButton:hover { background-color: #f0f0f0; }")
        btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #eee;")
        
        main_layout.addWidget(header_frame)
        main_layout.addWidget(line)

        # Form Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
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

        # Baris 3: Rentang Gaji & Tanggal Kadaluarsa
        self.inputs['Rentang_Gaji'] = QLineEdit()
        self.inputs['Rentang_Gaji'].setPlaceholderText("cth. Rp 8jt - 15jt")
        create_field("Rentang Gaji", self.inputs['Rentang_Gaji'], 2, 0)

        # Input Tanggal: Kalender
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate().addDays(30))
        # Validasi Preventif: Minimal besok
        self.date_edit.setMinimumDate(QDate.currentDate().addDays(1))
        # Styling popup kalender agar tidak hitam
        _cal = self.date_edit.calendarWidget()
        _cal.setStyleSheet("""
            QCalendarWidget { background-color: white; border: 1px solid #B2D2D9; border-radius: 8px; }
            QCalendarWidget QAbstractItemView { background-color: white; color: #1E3A4A; selection-background-color: #1D4E5F; selection-color: white; outline: none; font-size: 13px; }
            QCalendarWidget QAbstractItemView:disabled { color: #B2D2D9; }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #1D4E5F; padding: 4px; }
            QCalendarWidget QToolButton { color: white; background-color: transparent; border: none; font-weight: bold; font-size: 14px; padding: 4px 8px; }
            QCalendarWidget QToolButton:hover { background-color: rgba(255,255,255,0.15); border-radius: 4px; }
            QCalendarWidget QToolButton::menu-indicator { image: none; }
            QCalendarWidget QSpinBox { color: white; background-color: transparent; border: none; font-weight: bold; font-size: 14px; }
            QCalendarWidget QMenu { background-color: white; color: #1E3A4A; border: 1px solid #B2D2D9; font-size: 13px; }
            QCalendarWidget QMenu::item:selected { background-color: #E2EFF1; color: #1D4E5F; }
            QCalendarWidget QHeaderView::section { background-color: #F0F7F9; color: #2C687B; font-weight: bold; font-size: 12px; border: none; padding: 4px; }
        """)

        create_field("Tanggal Kadaluarsa", self.date_edit, 2, 1)

        # Baris 4: Hard Skills & Soft Skills
        self.inputs['Hard_Skills'] = QLineEdit()
        self.inputs['Hard_Skills'].setPlaceholderText("cth. Python, SQL, Project Management")
        create_field("Hard Skills", self.inputs['Hard_Skills'], 3, 0)

        self.inputs['Soft_Skills'] = QLineEdit()
        self.inputs['Soft_Skills'].setPlaceholderText("cth. Komunikasi, Kerjasama Tim")
        create_field("Soft Skills", self.inputs['Soft_Skills'], 3, 1)

        # Field 'Skills' tetap ada namun disembunyikan untuk kompatibilitas data lama
        self.inputs['Skills'] = QLineEdit()
        self.inputs['Skills'].hide()

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
        main_layout.addWidget(scroll)

        # Footer Actions
        footer_line = QFrame()
        footer_line.setFrameShape(QFrame.HLine)
        footer_line.setStyleSheet("background-color: #eee;")
        main_layout.addWidget(footer_line)

        footer_frame = QFrame()
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
        main_layout.addWidget(footer_frame)

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
            target_date = QDate(date_obj.year, date_obj.month, date_obj.day)
            
            # Jika tanggal lama sudah expired, turunkan minimum date sementara agar bisa dimuat
            if target_date <= QDate.currentDate():
                self.date_edit.setMinimumDate(target_date)
                QMessageBox.warning(
                    self,
                    "Tanggal Kadaluarsa Sudah Lewat",
                    f"Peringatan: Tanggal kadaluarsa data ini ({date_str}) sudah lewat!\n"
                    "Silakan pilih tanggal baru di kalender sebelum menyimpan."
                )
            
            self.date_edit.setDate(target_date)
        except (ValueError, TypeError):
            pass

    def validate_and_accept(self):
        if not self.inputs['Judul_Pekerjaan'].text().strip():
            QMessageBox.warning(self, "Validasi Gagal", "Judul Pekerjaan wajib diisi!")
            return
        if not self.inputs['Nama_Perusahaan'].text().strip():
            QMessageBox.warning(self, "Validasi Gagal", "Nama Perusahaan wajib diisi!")
            return
            
        # Validasi Tanggal Kadaluarsa (Preventif)
        selected_date = self.date_edit.date()
        if selected_date <= QDate.currentDate():
            QMessageBox.warning(self, "Validasi Gagal", "Tanggal Kadaluarsa tidak boleh hari ini atau di masa lalu!")
            return
            
        self.accept()

    def get_data(self):
        data = {}
        if self.job_data and "id" in self.job_data:
            data["id"] = self.job_data["id"]
        else:
            data["id"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["Is_lamar"] = False
            
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                data[key] = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()

        # Gabungkan Hard Skills dan Soft Skills ke field 'Skills' utama untuk kompatibilitas
        h_skills = data.get("Hard_Skills", "")
        s_skills = data.get("Soft_Skills", "")
        data["Skills"] = f"{h_skills}||{s_skills}"
                
        dt = self.date_edit.date()
        data["Tanggal_Kadaluarsa"] = f"{dt.day():02d}/{dt.month():02d}/{dt.year()}"
        return data




def gui_tambah_data(page, dialog_class):
    dialog = dialog_class(page)
    if dialog.exec_() == QDialog.Accepted:
        new_data = dialog.get_data()
        page.data.append(new_data)
        simpan_data(page.data)
        page.load_data()

def proses_create_job(form_data, current_data):
    import datetime as dt_mod
    from PyQt5.QtCore import QDate

    judul = form_data.get('judul', '').strip()
    perusahaan = form_data.get('perusahaan', '').strip()
    
    if not judul:
        return False, "Judul Pekerjaan wajib diisi!", current_data
    if not perusahaan:
        return False, "Nama Perusahaan wajib diisi!", current_data

    # Validasi Tanggal Kadaluarsa
    selected_date = form_data.get('date', QDate.currentDate())
    if selected_date <= QDate.currentDate():
        return False, "Tanggal Kadaluarsa tidak boleh hari ini atau di masa lalu!", current_data

    g_min = form_data.get('gaji_min', '').strip()
    g_max = form_data.get('gaji_max', '').strip()
    rentang_final = f"{g_min}-{g_max}" if g_min and g_max else (g_min or g_max or "-")

    skills_list = form_data.get('skills', [])
    skills_str = "|".join(skills_list)

    new_data = {
        "id": dt_mod.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Judul_Pekerjaan": judul,
        "Nama_Perusahaan": perusahaan,
        "Jenis_Pekerjaan": form_data.get('jenis', ''),
        "Lokasi": form_data.get('lokasi', '').strip(),
        "Rentang_Gaji": rentang_final,
        "Skills": skills_str,
        "Link_Lowongan": form_data.get('link', '').strip(),
        "Deskripsi_Pekerjaan": form_data.get('desc', '').strip(),
        "Benefit_Pekerjaan": form_data.get('benefit', '').strip(),
        "Kualifikasi_Persyaratan": form_data.get('kualifikasi', '').strip(),
        "Kategori": form_data.get('kategori', '').strip(),
        "Tanggal_Kadaluarsa": f"{selected_date.day():02d}/{selected_date.month():02d}/{selected_date.year()}",
        "Is_lamar": False
    }

    current_data.append(new_data)
    return True, "Lowongan berhasil ditambahkan!", current_data
