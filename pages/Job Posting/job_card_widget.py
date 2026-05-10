"""
JobCardWidget — widget kartu untuk satu lowongan pekerjaan.
Menampilkan info singkat (judul, perusahaan, lokasi, gaji,
skills, badge, checkbox) dengan sinyal edit/delete/card_clicked.
"""
import datetime

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QCheckBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

from constants import (
    check_icon_path, location_icon_path, currency_icon_path,
    edit_icon_path, trash_icon_card_path, send_icon_path, checked_icon_path
)


class JobCardWidget(QFrame):
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)
    checkbox_toggled = pyqtSignal(dict, bool)
    card_clicked = pyqtSignal(dict)
    lamar_clicked = pyqtSignal(dict)

    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.job_data = job_data
        self.setFixedHeight(290)
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
            QFrame#JobCard[selected="true"] {
                background-color: #f0f9ff;
                border: 2px solid #2C687B;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 12)
        main_layout.setSpacing(8)

        # ── Header: Logo, Judul & Perusahaan, Checkbox ──
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        initial = self.job_data.get("Nama_Perusahaan", "X")[:2].upper()
        lbl_logo = QLabel(initial)
        lbl_logo.setFixedSize(48, 48)
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        colors = ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff3e0", "#f3e5f5"]
        text_colors = ["#880e4f", "#0d47a1", "#1b5e20", "#e65100", "#4a148c"]
        idx = sum(ord(c) for c in initial) % len(colors)
        lbl_logo.setStyleSheet(
            f"background-color: {colors[idx]}; color: {text_colors[idx]}; "
            "border-radius: 12px; border: none;"
        )
        header_layout.addWidget(lbl_logo)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        judul = self.job_data.get("Judul_Pekerjaan", "Tanpa Judul")
        if len(judul) > 23:
            judul = judul[:21] + "..."
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

        self.checkbox = QCheckBox()
        check_url = check_icon_path.replace("\\", "/")
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border: 2px solid #dcdcdc;
                border-radius: 4px;
                background-color: #f1f5f9;
            }}
            QCheckBox::indicator:hover {{ border-color: #2C687B; }}
            QCheckBox::indicator:checked {{
                background-color: #2C687B;
                border-color: #2C687B;
                image: url("{check_url}");
            }}
        """)

        def on_checked(checked):
            self.setProperty("selected", checked)
            self.style().unpolish(self)
            self.style().polish(self)
            self.checkbox_toggled.emit(self.job_data, checked)

        self.checkbox.toggled.connect(on_checked)
        header_layout.addWidget(self.checkbox, alignment=Qt.AlignTop)
        main_layout.addLayout(header_layout)

        # ── Badges: Jenis, Remote, Segera Berakhir ──
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(6)

        def create_badge(text, bg_color, text_color):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"background-color: {bg_color}; color: {text_color}; "
                "border-radius: 10px; padding: 3px 10px; font-size: 11px; "
                "font-weight: bold; border: none;"
            )
            return lbl

        jenis = self.job_data.get("Jenis_Pekerjaan", "Penuh Waktu")
        if jenis == "Internship":
            badges_layout.addWidget(create_badge(jenis, "#fce4ec", "#c2185b"))
        else:
            badges_layout.addWidget(create_badge(jenis, "#e8f0fe", "#1a73e8"))

        lokasi = self.job_data.get("Lokasi", "")
        if "remote" in lokasi.lower() or "remote" in jenis.lower():
            badges_layout.addWidget(create_badge("Remote", "#e8f5e9", "#2e7d32"))

        date_str = self.job_data.get("Tanggal_Kadaluarsa", "")
        kadaluarsa_date = None
        is_warn = False
        try:
            d = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            kadaluarsa_date = d
            if (d - datetime.date.today()).days <= 7:
                badges_layout.addWidget(create_badge("Segera Berakhir", "#ffebee", "#c62828"))
                is_warn = True
        except Exception:
            pass

        badges_layout.addStretch()
        main_layout.addLayout(badges_layout)
        main_layout.addSpacing(4)

        # ── Info: Lokasi & Gaji ──
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        pix_loc = QPixmap(location_icon_path).scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        loc_row = QHBoxLayout()
        loc_row.setSpacing(6)
        lbl_loc_icon = QLabel()
        lbl_loc_icon.setPixmap(pix_loc)
        lbl_loc_icon.setStyleSheet("border: none;")
        lbl_loc_text = QLabel(self.job_data.get("Lokasi", "-"))
        lbl_loc_text.setStyleSheet("color: #666; font-size: 12px; border: none;")
        loc_row.addWidget(lbl_loc_icon)
        loc_row.addWidget(lbl_loc_text)
        loc_row.addStretch()
        info_layout.addLayout(loc_row)

        raw_sal = self.job_data.get("Rentang_Gaji", "-")

        def shorten_number(num_str):
            try:
                num = int(num_str.replace(".", ""))
                if num >= 1_000_000_000:
                    return f"{num / 1_000_000_000:.1f}".replace(".0", "") + "M"
                elif num >= 1_000_000:
                    return f"{num / 1_000_000:.1f}".replace(".0", "") + "jt"
                elif num >= 1_000:
                    return f"{num / 1_000:.1f}".replace(".0", "") + "k"
                return str(num)
            except Exception:
                return num_str

        formatted_sal = "-"
        if raw_sal and raw_sal != "-":
            parts = [p.strip() for p in raw_sal.split("-")]
            formatted_sal = " - ".join(shorten_number(p) for p in parts)

        sal_row = QHBoxLayout()
        sal_row.setSpacing(6)
        pix_sal = QPixmap(currency_icon_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl_sal_icon = QLabel()
        lbl_sal_icon.setPixmap(pix_sal)
        lbl_sal_icon.setStyleSheet("border: none;")
        lbl_sal_text = QLabel(formatted_sal)
        lbl_sal_text.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_sal_text.setStyleSheet("color: #20a082; border: none;")
        sal_row.addWidget(lbl_sal_icon)
        sal_row.addWidget(lbl_sal_text)
        sal_row.addStretch()
        info_layout.addLayout(sal_row)
        main_layout.addLayout(info_layout)
        main_layout.addSpacing(4)

        # ── Skills (maks 3 tag) ──
        skills = [s.strip() for s in self.job_data.get("Skills", "").split("|") if s.strip()]
        if skills:
            skills_layout = QHBoxLayout()
            skills_layout.setSpacing(6)
            for s in skills[:3]:
                lbl_s = QLabel(s)
                lbl_s.setStyleSheet(
                    "background-color: #f4f4f4; color: #444; border-radius: 8px; "
                    "padding: 4px 10px; font-size: 11px; border: none;"
                )
                skills_layout.addWidget(lbl_s)
            if len(skills) > 3:
                lbl_more = QLabel(f"+{len(skills) - 3}")
                lbl_more.setStyleSheet(
                    "background-color: #e8e8e8; color: #555; border-radius: 8px; "
                    "padding: 4px 10px; font-size: 11px; border: none;"
                )
                skills_layout.addWidget(lbl_more)
            skills_layout.addStretch()
            main_layout.addLayout(skills_layout)
        else:
            main_layout.addSpacing(25)

        main_layout.addStretch()

        # ── Divider ──
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #f0f0f0; border: none; height: 1px;")
        main_layout.addWidget(divider)

        # ── Footer: Kadaluarsa + Tombol Edit/Hapus ──
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 4, 0, 0)

        kad_layout = QVBoxLayout()
        kad_layout.setSpacing(0)
        lbl_k_lbl = QLabel("Kadaluarsa")
        lbl_k_lbl.setStyleSheet("color: #888; font-size: 11px; border: none;")
        formatted_date = kadaluarsa_date.strftime("%d/%m/%Y") if kadaluarsa_date else "-"
        lbl_k_val = QLabel(formatted_date)
        lbl_k_val.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_k_val.setStyleSheet(f"color: {'#c62828' if is_warn else '#333'}; border: none;")
        kad_layout.addWidget(lbl_k_lbl)
        kad_layout.addWidget(lbl_k_val)
        footer_layout.addLayout(kad_layout)
        footer_layout.addStretch()

        btn_style = (
            "QPushButton { border: 1px solid #ddd; border-radius: 6px; background: white; "
            "font-size: 14px; padding: 0px;} QPushButton:hover { background: #f5f5f5; }"
        )

        btn_edit = QPushButton()
        btn_edit.setIcon(QIcon(edit_icon_path))
        btn_edit.setIconSize(QSize(18, 18))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.job_data))

        btn_del = QPushButton()
        btn_del.setIcon(QIcon(trash_icon_card_path))
        btn_del.setIconSize(QSize(18, 18))
        btn_del.setFixedSize(32, 32)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet(
            "QPushButton { border: 1px solid #ddd; border-radius: 6px; background: white; "
            "font-size: 14px; padding: 0px;} "
            "QPushButton:hover { background: #fee; border-color: #ffcdd2; color: red; }"
        )
        btn_del.clicked.connect(lambda: self.delete_clicked.emit(self.job_data))

        footer_layout.addWidget(btn_edit, alignment=Qt.AlignBottom)
        footer_layout.addWidget(btn_del, alignment=Qt.AlignBottom)
        main_layout.addLayout(footer_layout)

        # ── Action: Lamar Sekarang ──
        main_layout.addSpacing(6)
        is_applied = self.job_data.get("Is_lamar", False)
        btn_lamar = QPushButton("Terlamar" if is_applied else "Lamar Sekarang")
        btn_lamar.setIcon(QIcon(checked_icon_path if is_applied else send_icon_path))
        btn_lamar.setIconSize(QSize(16, 16))
        btn_lamar.setFixedHeight(40)
        btn_lamar.setCursor(Qt.PointingHandCursor)
        
        if is_applied:
            btn_lamar.setEnabled(False)
            btn_lamar.setStyleSheet("""
                QPushButton {
                    background-color: #E2EFF1;
                    color: #2C687B;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 13px;
                    border: 1px solid #B2D2D9;
                }
            """)
        else:
            btn_lamar.setStyleSheet("""
                QPushButton {
                    background-color: #408699;
                    color: white;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2C687B;
                }
                QPushButton:pressed {
                    background-color: #1E4A58;
                }
            """)
        
        btn_lamar.clicked.connect(lambda: self.lamar_clicked.emit(self.job_data))
        main_layout.addWidget(btn_lamar)
