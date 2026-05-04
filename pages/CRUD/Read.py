import os
import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QGridLayout, QFrame, QTextEdit, QCheckBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

from CRUD.Shared import muat_data

_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_pages_dir)
trash_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "trash-can.png")
trash_icon2_path = os.path.join(_root_dir, "assets", "Job Posting", "trash-can2.png")
currency_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "save-money.png")
edit_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "edit.png")
location_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "gps.png")
check_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "check.png")

# --- Job Detail Dialog (Tampilan Read-Only) ---
class JobDetailDialog(QDialog):
    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.job_data = job_data
        self.setWindowTitle("Detail Lowongan Pekerjaan")
        self.resize(600, 700)
        self.setStyleSheet("background-color: white;")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        title_label = QLabel("Rincian Pekerjaan")
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

        # Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(15)

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
            lay.setSpacing(4)
            t = QLabel(title)
            t.setStyleSheet("color: #777; font-size: 11px; font-weight: bold;")
            v = QLabel(value if value else "-")
            v.setStyleSheet("color: #222; font-size: 13px;")
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
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)


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
        self.setFocusPolicy(Qt.StrongFocus)
        self.setup_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.job_data)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.card_clicked.emit(self.job_data)
        super().keyPressEvent(event)

    def setup_ui(self):
        self.setObjectName("JobCard")
        self.setStyleSheet("""
            QFrame#JobCard {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 10px;
            }
            QFrame#JobCard:hover, QFrame#JobCard:focus {
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
        safe_check_path = check_icon_path.replace("\\", "/")
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{ width: 16px; height: 16px; border: 1.5px solid #ccc; border-radius: 4px; }}
            QCheckBox::indicator:checked {{ background-color: #2C687B; border-color: #2C687B; image: url('{safe_check_path}'); }}
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
        
        loc_layout = QHBoxLayout()
        loc_layout.setContentsMargins(0, 0, 0, 0)
        loc_layout.setSpacing(6)
        loc_icon = QLabel()
        loc_icon.setPixmap(QPixmap(location_icon_path).scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_loc = QLabel(self.job_data.get('Lokasi', '-'))
        lbl_loc.setStyleSheet("color: #666; font-size: 12px; border: none;")
        loc_layout.addWidget(loc_icon)
        loc_layout.addWidget(lbl_loc)
        loc_layout.addStretch()
        info_layout.addLayout(loc_layout)

        sal_layout = QHBoxLayout()
        sal_layout.setContentsMargins(0, 0, 0, 0)
        sal_layout.setSpacing(6)
        sal_icon = QLabel()
        sal_icon.setPixmap(QPixmap(currency_icon_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_sal = QLabel(self.job_data.get('Rentang_Gaji', '-'))
        lbl_sal.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_sal.setStyleSheet("color: #20a082; border: none;")
        sal_layout.addWidget(sal_icon)
        sal_layout.addWidget(lbl_sal)
        sal_layout.addStretch()
        info_layout.addLayout(sal_layout)
        
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
            formatted_date = kadaluarsa_date.strftime("%Y-%m-%d")
            
        lbl_k_val = QLabel(formatted_date)
        lbl_k_val.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_k_val.setStyleSheet(f"color: {'#c62828' if is_warn else '#333'}; border: none;")
        
        kad_layout.addWidget(lbl_k_lbl)
        kad_layout.addWidget(lbl_k_val)
        footer_layout.addLayout(kad_layout)
        
        footer_layout.addStretch()
        
        btn_style = "QPushButton { border: 1px solid #ddd; border-radius: 6px; background: white; font-size: 14px;} QPushButton:hover { background: #f5f5f5; }"
        
        btn_edit = QPushButton()
        btn_edit.setIcon(QIcon(edit_icon_path))
        btn_edit.setIconSize(QSize(18, 18))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.job_data))
        
        btn_del = QPushButton()
        btn_del.setIcon(QIcon(trash_icon2_path))
        btn_del.setIconSize(QSize(18, 18))
        btn_del.setFixedSize(32, 32)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet("QPushButton { border: 1px solid #ddd; border-radius: 6px; background: white; font-size: 14px;} QPushButton:hover { background: #fee; border-color: #ffcdd2; color: red; }")
        btn_del.clicked.connect(lambda: self.delete_clicked.emit(self.job_data))

        footer_layout.addWidget(btn_edit)
        footer_layout.addWidget(btn_del)
        
        main_layout.addLayout(footer_layout)


# --- Main Page ---


def gui_muat_data(page):
    page.data = muat_data()
    page.selected_ids.clear()
    page.btn_delete_multi.hide()
    page.render_cards()
    page.update_statistics()
