import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QPushButton, QListWidget, QStackedWidget, QDialog, QMessageBox,
    QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPixmap, QIcon, QFont

class SkillTag(QLabel):
    """Tag skill yang terstandarisasi dengan kategori warna dan ukuran font yang fleksibel."""
    def __init__(self, text, color_or_category="#2C687B", font_size=13, parent=None):
        super().__init__(str(text).strip().title(), parent)
        
        # Mapping kategori ke warna hex
        categories = {
            "hard_skills": "#27AE60",   # Hijau
            "soft_skills": "#8E44AD",   # Ungu
            "positions": "#2980B9",     # Biru
            "matched": "#27AE60",       # Hijau (untuk kecocokan)
            "missing": "#C0392B",       # Merah (untuk gap)
            "salary": "#F39C12",        # Orange
            "benefit": "#2C687B"        # Teal
        }
        
        color = categories.get(color_or_category, color_or_category)
        
        self.setObjectName("SkillTag")
        self.setStyleSheet(f"""
            #SkillTag {{
                background: transparent;
                color: {color};
                border: 2px solid {color};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: {font_size}px;
                font-weight: bold;
            }}
        """)

# --- CENTRALIZED STYLESHEETS ---
MODERN_SCROLLBAR_STYLE = """
QScrollBar:vertical {
    border: none;
    background: #F3F4F6;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #B2D2D9;
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #7A9EB0;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: #F3F4F6;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #B2D2D9;
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover {
    background: #7A9EB0;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

MODERN_BUTTON_STYLE = """
QPushButton {
    background-color: #2C687B;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 14px;
    min-height: 32px;
}
QPushButton:hover {
    background-color: #408699;
}
QPushButton:pressed {
    background-color: #1E3A4A;
}
"""

MODERN_COMBO_STYLE = """
QComboBox {
    border: 2px solid #B2D2D9;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 16px;
    color: #1E3A4A;
    background-color: #F7FBFC;
}
QComboBox:hover {
    border: 2px solid #2C687B;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 40px;
    border: none;
}
QComboBox::down-arrow {
    image: url(__ICON_PATH__);
    width: 24px;
    height: 24px;
}
QComboBox QAbstractItemView {
    border: 1px solid #B2D2D9;
    border-radius: 8px;
    background-color: white;
    selection-background-color: #E2EFF1;
    selection-color: #2C687B;
    outline: none;
    padding: 5px;
}
"""

class ModernComboBox(QComboBox):
    """Dropdown dengan gaya modern yang terstandarisasi."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Lokasi icon panah (menggunakan path relatif ke root)
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(curr_dir))
        icon_path = os.path.join(root_dir, "assets", "Job Archive", "down.png").replace("\\", "/")
        
        self.setStyleSheet(MODERN_COMBO_STYLE.replace("__ICON_PATH__", icon_path))
        self.setCursor(Qt.PointingHandCursor)

MODERN_TABLE_STYLE = """
QTableWidget {
    border: none;
    background-color: white;
    font-size: 16px;
    color: #1E3A4A;
}
QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #F0F5F7;
}
QTableWidget::item:selected {
    background-color: #F7FBFC;
    color: #2C687B;
}
QHeaderView::section {
    background-color: white;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #E0E7EF;
    font-weight: bold;
    font-size: 16px;
    color: #2C687B;
    text-align: left;
}
QScrollBar:vertical {
    border: none;
    background: #F3F4F6;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #B2D2D9;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #7A9EB0;
}
QScrollBar:horizontal {
    border: none;
    background: #F3F4F6;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #B2D2D9;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #7A9EB0;
}
"""

# --- MODERN DIALOGS ---
class ModernMessageBox(QDialog):
    """Kotak pesan kustom dengan desain modern dan tombol terstandarisasi."""
    def __init__(self, title, text, buttons=QMessageBox.Ok, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main Container (untuk shadow/border radius)
        self.container = QFrame(self)
        self.container.setObjectName("MsgBoxContainer")
        self.container.setStyleSheet("""
            QFrame#MsgBoxContainer {
                background-color: white;
                border: 2px solid #2C687B;
                border-radius: 15px;
            }
        """)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)
        main_lay.addWidget(self.container)
        
        inner_lay = QVBoxLayout(self.container)
        inner_lay.setContentsMargins(25, 25, 25, 20)
        inner_lay.setSpacing(20)
        
        # Header/Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C687B; border: none; background-color: transparent;")
        inner_lay.addWidget(title_lbl)
        
        # Message Content
        self.msg_lbl = QLabel(text)
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setStyleSheet("font-size: 15px; color: #1E3A4A; border: none; line-height: 1.4; background-color: transparent;")
        inner_lay.addWidget(self.msg_lbl)
        
        # Buttons Row
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(12)
        btn_lay.addStretch()
        
        self.result = QMessageBox.No # Default
        
        if buttons & QMessageBox.Yes:
            btn_yes = QPushButton("Ya")
            btn_yes.setCursor(Qt.PointingHandCursor)
            btn_yes.setStyleSheet(MODERN_BUTTON_STYLE)
            btn_yes.clicked.connect(self._on_yes)
            btn_lay.addWidget(btn_yes)
            
        if buttons & QMessageBox.No:
            btn_no = QPushButton("Tidak")
            btn_no.setCursor(Qt.PointingHandCursor)
            # Style berbeda untuk tombol 'Tidak' agar lebih subtle
            btn_no.setStyleSheet("""
                QPushButton {
                    background-color: #F3F4F6; color: #4A5568;
                    border: 1px solid #D1D5DB; border-radius: 8px;
                    padding: 8px 18px; font-weight: bold; font-size: 14px; min-height: 32px;
                }
                QPushButton:hover { background-color: #E5E7EB; }
            """)
            btn_no.clicked.connect(self._on_no)
            btn_lay.addWidget(btn_no)
            
        if buttons & QMessageBox.Ok and not (buttons & QMessageBox.Yes):
            btn_ok = QPushButton("Selesai")
            btn_ok.setCursor(Qt.PointingHandCursor)
            btn_ok.setStyleSheet(MODERN_BUTTON_STYLE)
            btn_ok.clicked.connect(self._on_ok)
            btn_lay.addWidget(btn_ok)
            
        inner_lay.addLayout(btn_lay)

    def _on_yes(self): self.result = QMessageBox.Yes; self.accept()
    def _on_no(self): self.result = QMessageBox.No; self.reject()
    def _on_ok(self): self.result = QMessageBox.Ok; self.accept()

def show_message(parent, title, text):
    """Menampilkan pesan informasi modern (OK)."""
    dialog = ModernMessageBox(title, text, QMessageBox.Ok, parent)
    return dialog.exec_()

def show_question(parent, title, text):
    """Menampilkan pertanyaan konfirmasi modern (Yes/No)."""
    dialog = ModernMessageBox(title, text, QMessageBox.Yes | QMessageBox.No, parent)
    dialog.exec_()
    return dialog.result

GLOBAL_DIALOG_STYLE = MODERN_SCROLLBAR_STYLE + """
QDialog { background-color: white; }
"""

class KeyboardScrollArea(QScrollArea):
    """
    QScrollArea yang diperluas dengan dukungan navigasi keyboard.
    Tombol ↑ ↓ ← → menggerakkan scroll satu langkah kecil.
    Page Up / Page Down menggerakkan satu halaman.
    Home / End melompat ke awal atau akhir konten.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Fokus keyboard untuk menggunakan scroller
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(MODERN_SCROLLBAR_STYLE)

    def keyPressEvent(self, event):
        vbar = self.verticalScrollBar()
        hbar = self.horizontalScrollBar()
        step = 25          # px per menekan tombol arrow
        page = 150         # px per menekan tombol Page Up/Down

        key = event.key()
        if key == Qt.Key_Up:
            vbar.setValue(vbar.value() - step)
        elif key == Qt.Key_Down:
            vbar.setValue(vbar.value() + step)
        elif key == Qt.Key_Left:
            hbar.setValue(hbar.value() - step)
        elif key == Qt.Key_Right:
            hbar.setValue(hbar.value() + step)
        elif key == Qt.Key_PageUp:
            vbar.setValue(vbar.value() - page)
        elif key == Qt.Key_PageDown:
            vbar.setValue(vbar.value() + page)
        elif key == Qt.Key_Home:
            vbar.setValue(vbar.minimum())
        elif key == Qt.Key_End:
            vbar.setValue(vbar.maximum())
        else:
            # Teruskan event lain ke parent agar tidak terblokir
            super().keyPressEvent(event)

class StatCard(QFrame):
    """Card statistik kecil (Scorecard style) yang terstandarisasi."""
    def __init__(self, title, val="0", parent=None):
        super().__init__(parent)
        self.setObjectName("PanelCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(5)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: normal; color: #4A5568; background-color: transparent;")
        
        self.lbl_val = QLabel(val)
        self.lbl_val.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A4A; background-color: transparent;")
        
        lay.addWidget(self.lbl_title, alignment=Qt.AlignLeft)
        lay.addWidget(self.lbl_val, alignment=Qt.AlignLeft)

    def update_value(self, val, color=None):
        self.lbl_val.setText(str(val))
        if color:
            self.lbl_val.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color}; background-color: transparent;")

class JobDashboardWidget(QWidget):
    """Kontainer utama dashboard yang berisi statistik, chart, dan daftar skill."""
    find_match_clicked = pyqtSignal()
    
    def __init__(self, chart_widget, parent=None):
        super().__init__(parent)
        self.chart = chart_widget
        self._init_ui()

    def _init_ui(self):
        # Layout utama horizontal: Kiri (Stats + Chart) | Kanan (Skill List)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # ── KIRI: Stats di atas, Chart di bawah ──
        left_container = QVBoxLayout()
        left_container.setSpacing(20)

        # Baris Atas Kiri: 3 Card Statistik (Horizontal)
        stat_row = QHBoxLayout()
        stat_row.setSpacing(10)
        
        self.card_total = StatCard("Total pekerjaan")
        self.card_skills = StatCard("Skill teridentifikasi")
        self.card_dominant = StatCard("Skill dominan", "-")
        
        stat_row.addWidget(self.card_total)
        stat_row.addWidget(self.card_skills)
        stat_row.addWidget(self.card_dominant)
        left_container.addLayout(stat_row)

        # Bagian Bawah Kiri: Chart Card
        chart_card = QFrame()
        chart_card.setObjectName("PanelCard")
        chart_card_lay = QVBoxLayout(chart_card)
        chart_card_lay.setContentsMargins(0, 20, 0, 50)
        
        lbl_chart = QLabel("Tren skill minggu ini", alignment=Qt.AlignHCenter)
        lbl_chart.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C687B; background-color: transparent;")
        chart_card_lay.addWidget(lbl_chart)
        chart_card_lay.addSpacing(20)
        chart_card_lay.addWidget(self.chart, stretch=1)
        
        left_container.addWidget(chart_card, stretch=1)
        main_layout.addLayout(left_container, stretch=2)

        # ── KANAN: Daftar Skill & Job Type (Full Height) ──
        right_panel = QFrame()
        right_panel.setObjectName("PanelCard")
        right_lay = QVBoxLayout(right_panel)
        right_lay.setContentsMargins(0, 0, 0, 0)
        
        self.right_stack = QStackedWidget()
        
        # --- PAGE 1: SKILL LIST ---
        page_skill = QWidget()
        page_skill_lay = QVBoxLayout(page_skill)
        page_skill_lay.setContentsMargins(20, 20, 20, 20)
        
        right_title = QLabel("Daftar Skill Pekerjaan", alignment=Qt.AlignCenter)
        right_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C687B; background-color: transparent;")
        page_skill_lay.addWidget(right_title)
        page_skill_lay.addSpacing(15)
        
        self.skill_list = QListWidget()
        list_style = """
            QListWidget { 
                border: none; background-color: #F7FBFC; border-radius: 8px; font-size: 16px; color: #1E3A4A;
            }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #E0E7EF; color: #1E3A4A; }
            QListWidget::item:hover { background-color: #EBF4F6; }
            QListWidget::item:selected { background-color: #E2EFF1; color: #2C687B; border-left: 4px solid #2C687B; }
            QScrollBar:vertical { border: none; background: #F3F4F6; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #B2D2D9; border-radius: 4px; }
            QScrollBar:horizontal { border: none; background: #F3F4F6; height: 8px; border-radius: 4px; }
            QScrollBar::handle:horizontal { background: #B2D2D9; border-radius: 4px; }
            QListWidget::indicator { width: 22px; height: 22px; border: 2px solid #B2D2D9; border-radius: 4px; background-color: white; }
            QListWidget::indicator:checked { background-color: #2C687B; border: 2px solid #2C687B; }
        """
        self.skill_list.setStyleSheet(list_style)
        self.skill_list.itemClicked.connect(self._toggle_item_check)
        page_skill_lay.addWidget(self.skill_list, stretch=1)
        page_skill_lay.addSpacing(15)
        
        self.btn_next_job_type = QPushButton(" Pilih jenis pekerjaan")
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.btn_next_job_type.setCursor(Qt.PointingHandCursor)
        self.btn_next_job_type.setStyleSheet("""
            QPushButton {
                background-color: #2C687B; color: white;
                font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px;
            }
            QPushButton:hover { background-color: #3B7C91; }
        """)
        self.btn_next_job_type.clicked.connect(lambda: self.right_stack.setCurrentIndex(1))
        page_skill_lay.addWidget(self.btn_next_job_type)
        self.right_stack.addWidget(page_skill)
        
        # --- PAGE 2: JOB TYPE LIST ---
        page_type = QWidget()
        page_type_lay = QVBoxLayout(page_type)
        page_type_lay.setContentsMargins(20, 20, 20, 20)
        
        header_type_lay = QHBoxLayout()
        btn_back_skill = QPushButton("← Kembali")
        btn_back_skill.setCursor(Qt.PointingHandCursor)
        btn_back_skill.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #2C687B;
                font-size: 14px; font-weight: bold;
                border: 1px solid #2C687B; border-radius: 6px; padding: 5px 15px;
            }
            QPushButton:hover { background-color: #E2EFF1; }
        """)
        btn_back_skill.clicked.connect(lambda: self.right_stack.setCurrentIndex(0))
        header_type_lay.addWidget(btn_back_skill)
        
        type_title = QLabel("Tipe Pekerjaan")
        type_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C687B; background-color: transparent;")
        header_type_lay.addWidget(type_title, stretch=1, alignment=Qt.AlignCenter)
        header_type_lay.addSpacing(70) # balance for the wider back button
        page_type_lay.addLayout(header_type_lay)
        page_type_lay.addSpacing(15)
        
        self.job_type_list = QListWidget()
        self.job_type_list.setStyleSheet(list_style)
        self.job_type_list.itemClicked.connect(self._toggle_item_check)
        page_type_lay.addWidget(self.job_type_list, stretch=1)
        page_type_lay.addSpacing(15)
        
        self.btn_find_match = QPushButton(" Cari pekerjaan yang cocok")
        search_icon_path = os.path.join(base_path, 'assets', 'Job Archive', 'search.png')
        self.btn_find_match.setIcon(QIcon(search_icon_path))
        self.btn_find_match.setIconSize(QSize(18, 18))
        self.btn_find_match.setCursor(Qt.PointingHandCursor)
        self.btn_find_match.setStyleSheet("""
            QPushButton {
                background-color: #2C687B; color: white;
                font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px;
            }
            QPushButton:hover { background-color: #3B7C91; }
        """)
        self.btn_find_match.clicked.connect(self.find_match_clicked.emit)
        page_type_lay.addWidget(self.btn_find_match)
        self.right_stack.addWidget(page_type)
        
        right_lay.addWidget(self.right_stack)
        main_layout.addWidget(right_panel, stretch=1)

    def update_stats(self, total_jobs, total_skills, dominant_skill):
        self.card_total.update_value(total_jobs)
        self.card_skills.update_value(total_skills)
        self.card_dominant.update_value(dominant_skill, color="#2C687B")

    def _toggle_item_check(self, item):
        last_state = item.data(Qt.UserRole)
        current_state = item.checkState()
        
        if last_state is None:
            # Default state when item is created is usually Unchecked
            last_state = Qt.Unchecked
            
        if current_state != last_state:
            # Checkbox clicked directly (Qt already toggled it)
            item.setData(Qt.UserRole, current_state)
        else:
            # Text clicked (Qt did not toggle it, so we toggle manually)
            new_state = Qt.Checked if current_state == Qt.Unchecked else Qt.Unchecked
            item.setCheckState(new_state)
            item.setData(Qt.UserRole, new_state)


class BestMatchCard(QFrame):
    """Card untuk menampilkan pekerjaan dengan persentase kecocokan tertinggi."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PanelCard")
        self.setStyleSheet("""
            QFrame#PanelCard {
                background-color: white;
                border: 2px solid #27AE60;
                border-radius: 16px;
            }
        """)
        self.setFixedWidth(350)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        # Scroll Area for the entire card content (mendukung navigasi keyboard)
        self.scroll = KeyboardScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #F3F4F6; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #B2D2D9; border-radius: 4px; }
            QScrollBar:horizontal { border: none; background: #F3F4F6; height: 8px; border-radius: 4px; }
            QScrollBar::handle:horizontal { background: #B2D2D9; border-radius: 4px; }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.content_lay = QVBoxLayout(self.scroll_content)
        self.content_lay.setContentsMargins(5, 5, 5, 5)
        self.content_lay.setSpacing(15)

        # 0. Label Judul Persentase
        self.lbl_perc_title = QLabel("Persentase Kecocokan")
        self.lbl_perc_title.setAlignment(Qt.AlignCenter)
        self.lbl_perc_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C687B; background-color: transparent;")
        self.content_lay.addWidget(self.lbl_perc_title)

        # 1. Badge Persentase
        self.lbl_perc = QLabel("0%")
        self.lbl_perc.setAlignment(Qt.AlignCenter)
        self.lbl_perc.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
            background-color: #27AE60;
            border-radius: 12px;
            padding: 10px;
        """)
        self.content_lay.addWidget(self.lbl_perc)

        self.content_lay.addSpacing(5)

        # 2. Judul Pekerjaan
        self.lbl_title = QLabel("Nama Pekerjaan")
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E3A4A; background-color: transparent;")
        self.content_lay.addWidget(self.lbl_title)

        # 3. Nama Perusahaan & Lokasi
        self.lbl_company = QLabel("Nama Perusahaan")
        self.lbl_company.setStyleSheet("font-size: 16px; color: #2C687B; font-weight: bold; background-color: transparent;")
        self.content_lay.addWidget(self.lbl_company)

        self.lbl_location = QLabel("📍 Lokasi")
        self.lbl_location.setWordWrap(True)
        self.lbl_location.setStyleSheet("font-size: 16px; color: #1E3A4A; background-color: transparent;")
        self.content_lay.addWidget(self.lbl_location)

        # 4. SKILL SECTIONS (Hard, Soft, Position)
        self.hard_skill_container = self._setup_skill_section("TECHNICAL / HARD SKILLS", "#2C3E50")
        self.soft_skill_container = self._setup_skill_section("SOFT SKILLS", "#8E44AD")
        self.pos_skill_container = self._setup_skill_section("POSISI / PERAN TERKAIT", "#2980B9")
        
        self.content_lay.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

    def _setup_skill_section(self, title, color):
        """Helper untuk membuat kontainer section skill."""
        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color}; margin-top: 10px; letter-spacing: 1px;")
        self.content_lay.addWidget(lbl)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(6)
        self.content_lay.addWidget(container)
        return layout

    def update_data(self, data, user_skills):
        perc = data.get('match_percentage', 0)
        self.lbl_perc.setText(f"{perc}%")
        
        # Tentukan warna tema kartu
        color = "#27AE60" if perc >= 70 else ("#F39C12" if perc >= 40 else "#C0392B")
            
        self.lbl_perc.setStyleSheet(f"font-size: 36px; font-weight: bold; color: white; background-color: {color}; border-radius: 12px; padding: 10px;")
        self.setStyleSheet(f"QFrame#PanelCard {{ background-color: white; border: 2px solid {color}; border-radius: 16px; }}")

        self.lbl_title.setText(data.get("Judul_Pekerjaan", "-"))
        self.lbl_company.setText(data.get("Nama_Perusahaan", "-"))
        self.lbl_location.setText(f"📍 {data.get('Lokasi', '-')}")

        # Clear all sections
        for lay in [self.hard_skill_container, self.soft_skill_container, self.pos_skill_container]:
            self._clear_layout(lay)

        # Ambil data kategori (sudah dikategorikan di modul_pengolahan_data)
        all_cat = data.get("all_categorized", {"hard_skills": [], "soft_skills": [], "positions": []})
        matched_cat = data.get("matched_categorized", {"hard_skills": [], "soft_skills": [], "positions": []})

        # Render masing-masing kategori
        self._render_category_items(self.hard_skill_container, all_cat["hard_skills"], matched_cat["hard_skills"])
        self._render_category_items(self.soft_skill_container, all_cat["soft_skills"], matched_cat["soft_skills"])
        self._render_category_items(self.pos_skill_container, all_cat["positions"], matched_cat["positions"])

    def _render_category_items(self, layout, all_items, matched_items):
        """Merender item dalam satu kategori dengan warna hijau (punya) atau merah (tidak)."""
        if not all_items:
            layout.addWidget(QLabel("-"), alignment=Qt.AlignLeft)
            return

        matched_set = {s.lower() for s in matched_items}
        for s in all_items:
            is_owned = s.lower() in matched_set
            tag_cat = "matched" if is_owned else "missing"
            layout.addWidget(self._create_tag(s, tag_cat), alignment=Qt.AlignLeft)

    def _create_tag(self, text, color_or_category):
        return SkillTag(text, color_or_category, font_size=16)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

class JobMatchResultContainer(QWidget):
    """Kontainer yang membagi tampilan menjadi Best Match (Kiri) dan Hasil Lainnya (Kanan)."""
    itemDoubleClicked = pyqtSignal(object)
    save_clicked = pyqtSignal(dict)
    favorite_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Kiri: Best Match Card
        self.best_match_card = BestMatchCard()
        layout.addWidget(self.best_match_card)

        # Kanan: Tabel Hasil (Semua)
        self.table = JobMatchTable()
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.table.save_clicked.connect(self.save_clicked.emit)
        self.table.favorite_clicked.connect(self.favorite_clicked.emit)
        self.table.delete_clicked.connect(self.delete_clicked.emit)
        layout.addWidget(self.table, stretch=1)

    def set_data(self, hasil, selected_skills, show_save=True, show_favorite=True, show_delete=False, fav_link=None, saved_links=None):
        if not hasil:
            return
        
        # Urutkan berdasarkan persentase tertinggi (biasanya sudah di modul pengolahan)
        best = hasil[0]
        self.best_match_card.update_data(best, selected_skills)
        
        # Isi tabel dengan semua data (atau sisanya)
        self.table.set_data(hasil, selected_skills, show_save=show_save, show_favorite=show_favorite, show_delete=show_delete, fav_link=fav_link, saved_links=saved_links)
        self.current_data = hasil

    def _on_item_double_clicked(self, item):
        self.itemDoubleClicked.emit(item)

class JobMatchTable(QTableWidget):
    """Komponen tabel hasil pencarian lowongan yang terstandarisasi."""
    save_clicked = pyqtSignal(dict)
    favorite_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Judul Pekerjaan", "Perusahaan", "Kecocokan", "Aksi"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.verticalHeader().setDefaultSectionSize(130)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setStyleSheet(MODERN_TABLE_STYLE)

    def resizeEvent(self, event):
        """Picu pembaruan teks tombol saat ukuran tabel berubah."""
        super().resizeEvent(event)
        self._update_responsive_buttons()

    def _update_responsive_buttons(self):
        """Sembunyikan atau tampilkan teks tombol berdasarkan lebar tabel."""
        # Ambang batas lebar (bisa disesuaikan, misal 1000px)
        is_compact = self.width() < 1000
        
        for row in range(self.rowCount()):
            widget = self.cellWidget(row, 3) # Kolom Aksi
            if widget:
                buttons = widget.findChildren(QPushButton)
                for btn in buttons:
                    original_text = btn.property("original_text")
                    if original_text:
                        if is_compact:
                            btn.setText("") # Hanya ikon
                            btn.setToolTip(original_text.strip()) # Tampilkan teks saat hover saja
                        else:
                            btn.setText(original_text) # Teks + Ikon
                            btn.setToolTip("")

    def set_data(self, hasil, selected_skills, show_save=True, show_favorite=True, show_delete=False, fav_link=None, saved_links=None):
        """Isi tabel dengan data lowongan hasil pencocokan."""
        self.setRowCount(len(hasil))
        
        # Sembunyikan kolom aksi jika tidak ada tombol yang ditampilkan
        if not show_save and not show_favorite and not show_delete:
            self.setColumnHidden(3, True)
        else:
            self.setColumnHidden(3, False)

        # Setup icon paths once
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        save_icon_path = os.path.join(root_dir, "assets", "modul", "save.png")
        star_icon_path = os.path.join(root_dir, "assets", "modul", "star.png")
        delete_icon_path = os.path.join(root_dir, "assets", "modul", "delete.png")

        for row, data in enumerate(hasil):
            # 1. Judul Pekerjaan
            self.setItem(row, 0, QTableWidgetItem(data.get("Judul_Pekerjaan", "-")))
            
            # 2. Nama Perusahaan
            self.setItem(row, 1, QTableWidgetItem(data.get("Nama_Perusahaan", "-")))
            
            # 3. Persentase Kecocokan
            perc = data.get("match_percentage", 0)
            match_item = QTableWidgetItem(f"{perc}%")
            match_item.setTextAlignment(Qt.AlignCenter)
            
            # Warna teks berdasarkan tingkat kecocokan
            if perc >= 70:
                match_item.setForeground(QColor("#27AE60")) # Hijau
            elif perc >= 40:
                match_item.setForeground(QColor("#F39C12")) # Oranye
            else:
                match_item.setForeground(QColor("#C0392B")) # Merah
                
            font = match_item.font()
            font.setBold(True)
            match_item.setFont(font)
            
            self.setItem(row, 2, match_item)
            
            if not show_save and not show_favorite and not show_delete:
                continue
                
            # Container untuk tombol aksi
            btn_widget = QWidget()
            btn_widget.setStyleSheet("background-color: transparent;")
            btn_lay = QHBoxLayout(btn_widget)
            btn_lay.setContentsMargins(10, 0, 10, 0)
            btn_lay.setSpacing(10)
            btn_lay.setAlignment(Qt.AlignCenter)
            
            # 4. Tombol Simpan
            if show_save:
                # Cek apakah sudah tersimpan di archive
                is_saved = False
                if saved_links and data.get("Link_Lowongan") in saved_links:
                    is_saved = True
                
                btn_text = " Tersimpan" if is_saved else " Simpan"
                btn_save = QPushButton(btn_text)
                btn_save.setProperty("original_text", btn_text)
                btn_save.setIcon(QIcon(save_icon_path))
                btn_save.setCursor(Qt.PointingHandCursor)
                
                if is_saved:
                    btn_save.setEnabled(False)
                    btn_save.setStyleSheet("""
                        QPushButton {
                            background-color: #BDC3C7; color: white;
                            border: none; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 13px;
                            min-height: 32px;
                        }
                    """)
                else:
                    btn_save.setStyleSheet("""
                        QPushButton {
                            background-color: #2C687B; color: white;
                            border: none; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 13px;
                            min-height: 32px;
                        }
                        QPushButton:hover { background-color: #3B7C91; }
                    """)
                btn_save.clicked.connect(lambda checked, d=data: self.save_clicked.emit(d))
                btn_lay.addWidget(btn_save)

            # 5. Tombol Favorit
            if show_favorite:
                is_fav = (fav_link == data.get("Link_Lowongan"))
                btn_text = " Terfavorit" if is_fav else " Favorit"
                btn_fav = QPushButton(btn_text)
                btn_fav.setProperty("original_text", btn_text)
                btn_fav.setIcon(QIcon(star_icon_path))
                btn_fav.setCursor(Qt.PointingHandCursor)
                
                if is_fav:
                    btn_fav.setEnabled(False)
                    btn_fav.setStyleSheet("""
                        QPushButton {
                            background-color: #BDC3C7; color: white;
                            border: none; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 13px;
                            min-height: 32px;
                        }
                    """)
                else:
                    btn_fav.setStyleSheet("""
                        QPushButton {
                            background-color: #F1C40F; color: #1E3A4A;
                            border: none; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 13px;
                            min-height: 32px;
                        }
                        QPushButton:hover { background-color: #F39C12; }
                    """)
                
                btn_fav.clicked.connect(lambda checked, d=data: self.favorite_clicked.emit(d))
                btn_lay.addWidget(btn_fav)

            # 6. Tombol Hapus
            if show_delete:
                btn_text = " Hapus"
                btn_del = QPushButton(btn_text)
                btn_del.setProperty("original_text", btn_text)
                btn_del.setIcon(QIcon(delete_icon_path))
                btn_del.setCursor(Qt.PointingHandCursor)
                btn_del.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C; color: white;
                        border: none; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 13px;
                        min-height: 32px;
                    }
                    QPushButton:hover { background-color: #C0392B; }
                """)
                btn_del.clicked.connect(lambda checked, d=data: self.delete_clicked.emit(d))
                btn_lay.addWidget(btn_del)
            
            self.setCellWidget(row, 3, btn_widget)
        
        # Jalankan pengecekan responsif segera setelah data dimuat
        self._update_responsive_buttons()

class JobDetailPanel(QFrame):
    """Komponen detail lowongan pekerjaan yang terstandarisasi."""
    def __init__(self, on_back_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("PanelCard")
        self.on_back_callback = on_back_callback
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        # Header
        header = QHBoxLayout()
        btn_back = self._create_back_button()
        btn_back.clicked.connect(self.on_back_callback)
        header.addWidget(btn_back)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(15)

        # Scroll Area (mendukung navigasi keyboard)
        scroll = KeyboardScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: none; background: #F3F4F6; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical { background: #B2D2D9; min-height: 20px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #7A9EB0; }
            QScrollBar:horizontal {
                border: none; background: #F3F4F6; height: 8px; border-radius: 4px;
            }
            QScrollBar::handle:horizontal { background: #B2D2D9; min-width: 20px; border-radius: 4px; }
            QScrollBar::handle:horizontal:hover { background: #7A9EB0; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { height: 0px; width: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.content_lay = QVBoxLayout(scroll_content)
        self.content_lay.setContentsMargins(0, 0, 20, 0)
        self.content_lay.setSpacing(15)

        # Labels
        self.det_title = QLabel("Judul Pekerjaan")
        self.det_title.setWordWrap(True)
        self.det_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A4A; background-color: transparent;")
        self.content_lay.addWidget(self.det_title)
        
        self.det_company = QLabel("Nama Perusahaan")
        self.det_company.setStyleSheet("font-size: 16px; color: #2C687B; font-weight: bold; background-color: transparent;")
        self.content_lay.addWidget(self.det_company)

        # Sections
        self.det_loc = self._create_section("📍 Lokasi Pekerjaan")
        self.det_type = self._create_section("💼 Jenis Pekerjaan")
        
        # Salary Tags
        self.salary_lay = self._create_tag_container("💰 Rentang Gaji")
        
        # Skill Tags
        self.lbl_match_title = QLabel("✅ Skill yang kamu punya")
        self.lbl_match_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #27AE60; background-color: transparent;")
        self.content_lay.addWidget(self.lbl_match_title)
        self.match_tags_lay = self._create_tag_layout()
        
        self.lbl_missing_title = QLabel("🛠 Skill yang dibutuhkan lainnya")
        self.lbl_missing_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #C0392B; background-color: transparent;")
        self.content_lay.addWidget(self.lbl_missing_title)
        self.missing_tags_lay = self._create_tag_layout()

        # Benefit Tags
        self.benefit_tags_lay = self._create_tag_container("🎁 Benefit Pekerjaan")

        self.det_req = self._create_section("📋 Kualifikasi & Persyaratan")
        self.det_desc = self._create_section("📝 Deskripsi Pekerjaan")
        
        self.det_link = self._create_section("🔗 Link Lowongan")
        self.det_link.setOpenExternalLinks(True)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _create_back_button(self):
        btn = QPushButton("← Kembali")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #2C687B;
                font-size: 14px; font-weight: bold;
                border: 1px solid #2C687B; border-radius: 6px; padding: 5px 15px;
            }
            QPushButton:hover { background-color: #E2EFF1; }
        """)
        return btn

    def _create_section(self, title):
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 5, 0, 15)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C687B; background-color: transparent;")
        lay.addWidget(lbl_t)
        lbl_c = QLabel("-")
        lbl_c.setWordWrap(True)
        lbl_c.setStyleSheet("font-size: 16px; color: #4A5568; line-height: 1.5; background-color: transparent;")
        lay.addWidget(lbl_c)
        self.content_lay.addWidget(container)
        return lbl_c

    def _create_tag_container(self, title):
        """Membuat section yang berisi judul dan kumpulan tag (layout horizontal)."""
        section_widget = QWidget()
        section_lay = QVBoxLayout(section_widget)
        section_lay.setContentsMargins(0, 5, 0, 15)
        
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C687B; background-color: transparent;")
        section_lay.addWidget(lbl_t)
        
        # Widget khusus untuk menampung tag secara horizontal
        tag_container = QWidget()
        tag_lay = QHBoxLayout(tag_container)
        tag_lay.setContentsMargins(0, 5, 0, 0)
        tag_lay.setSpacing(8)
        tag_lay.setAlignment(Qt.AlignLeft)
        
        section_lay.addWidget(tag_container)
        self.content_lay.addWidget(section_widget)
        
        return tag_lay

    def _create_tag_layout(self):
        """Membuat layout horizontal untuk tag yang langsung ditempel ke content_lay."""
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 5, 0, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignLeft)
        self.content_lay.addWidget(container)
        return lay

    def update_data(self, data, user_selected_skills=[]):
        """Populasi data pekerjaan ke UI."""
        self.det_title.setText(data.get("Judul_Pekerjaan", "-"))
        self.det_company.setText(data.get("Nama_Perusahaan", "-"))
        self.det_loc.setText(data.get("Lokasi", "-"))
        self.det_type.setText(data.get("Jenis_Pekerjaan", "-"))
        
        # Salary & Bonus
        self._clear_layout(self.salary_lay)
        sal = data.get("Rentang_Gaji", "-")
        self.salary_lay.addWidget(self._create_tag(sal, "salary"))
        
        bonus = data.get("Bonus", "-")
        if bonus != "-" and bonus.lower() != "bonus":
            self.salary_lay.addWidget(self._create_tag(f"Bonus: {bonus}", "salary"))
            
        self.salary_lay.addStretch()

        # Skills
        self._clear_layout(self.match_tags_lay)
        self._clear_layout(self.missing_tags_lay)
        raw_skills = data.get("Skills", "-")
        if raw_skills != "-":
            job_skills = [s.strip() for s in raw_skills.split("|")]
            user_set = {s.lower() for s in user_selected_skills}
            matched = [s for s in job_skills if s.lower() in user_set]
            missing = [s for s in job_skills if s.lower() not in user_set]
            
            self.lbl_match_title.setVisible(len(matched) > 0)
            for s in matched: self.match_tags_lay.addWidget(self._create_tag(s, "matched"))
            self.match_tags_lay.addStretch()

            self.lbl_missing_title.setVisible(len(missing) > 0)
            for s in missing: self.missing_tags_lay.addWidget(self._create_tag(s, "missing"))
            self.missing_tags_lay.addStretch()

        # Benefits
        self._clear_layout(self.benefit_tags_lay)
        raw_ben = data.get("Benefit_Pekerjaan", "-")
        if raw_ben != "-":
            for b in [x.strip() for x in raw_ben.split("|")]:
                self.benefit_tags_lay.addWidget(self._create_tag(b, "benefit"))
            self.benefit_tags_lay.addStretch()

        # Requirements & Description
        req = data.get("Kualifikasi_Persyaratan", "-")
        self.det_req.setText("• " + req.replace(" | ", "\n• ").replace("\n", "\n• ") if req != "-" else "-")
        self.det_desc.setText(data.get("Deskripsi_Pekerjaan", "-"))
        
        link = data.get("Link_Lowongan", "#")
        self.det_link.setText(f'<a href="{link}" style="color: #2C687B; text-decoration: none;">Buka di browser ↗</a>')

    def _create_tag(self, text, color_or_category):
        return SkillTag(text, color_or_category, font_size=16)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
