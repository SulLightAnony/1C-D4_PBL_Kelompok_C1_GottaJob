"""
SkillTagInput — Widget input skill dengan desain baru.
Tags ditampilkan di atas box input menggunakan FlowLayout.
Tombol + berada di sebelah kanan box input.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from constants import plus_icon_path
from flow_layout import FlowLayout


class SkillTagInput(QWidget):
    """Widget input skill dengan tags di atas dan input box di bawah."""

    def __init__(self, parent=None, placeholder="Ketik skill lalu tekan Enter...", btn_text=""):
        super().__init__(parent)
        self._skills = []
        self._placeholder = placeholder
        self._btn_text = btn_text
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(12)

        # ── Row 1: Container untuk Tags (Pills) ──
        self.tags_widget = QWidget()
        self.tags_layout = FlowLayout(self.tags_widget, margin=0, spacing=8)
        self.main_layout.addWidget(self.tags_widget)
        self.tags_widget.hide()

        # ── Row 2: Input Box + Tombol Tambah ──
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        # Container untuk LineEdit agar ada border khusus
        self.edit_frame = QFrame()
        self.edit_frame.setObjectName("EditFrame")
        self.edit_frame.setStyleSheet("""
            QFrame#EditFrame {
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                background-color: white;
            }
            QFrame#EditFrame:focus-within {
                border: 1px solid #2C687B;
                background-color: #fff;
            }
        """)
        self.edit_frame.setFixedHeight(40)
        
        edit_layout = QHBoxLayout(self.edit_frame)
        edit_layout.setContentsMargins(12, 0, 12, 0)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(self._placeholder)
        self._edit.setStyleSheet("border: none; background: transparent; font-size: 14px; color: #333;")
        self._edit.returnPressed.connect(self._add_from_input)
        edit_layout.addWidget(self._edit)
        
        input_row.addWidget(self.edit_frame, 1)

        # Tombol + di luar box input
        self._btn_add = QPushButton(self._btn_text)
        self._btn_add.setIcon(QIcon(plus_icon_path))
        self._btn_add.setIconSize(QSize(18, 18))
        if self._btn_text:
            self._btn_add.setFixedHeight(40)
            self._btn_add.setMinimumWidth(100)
            self._btn_add.setStyleSheet("""
                QPushButton {
                    background-color: #2C687B;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    background-color: #408699;
                }
            """)
        else:
            self._btn_add.setFixedSize(40, 40)
            self._btn_add.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #dcdcdc;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                    border-color: #bbb;
                }
                QPushButton:pressed {
                    background-color: #ddd;
                }
            """)
        self._btn_add.setCursor(Qt.PointingHandCursor)
        self._btn_add.clicked.connect(self._add_from_input)
        input_row.addWidget(self._btn_add)

        self.main_layout.addLayout(input_row)

    def _add_from_input(self):
        text = self._edit.text().strip()
        if not text:
            return
        
        # Split berdasarkan koma atau spasi jika perlu
        # Kita pisahkan berdasarkan koma terlebih dahulu, jika tidak ada koma, pisahkan berdasar spasi
        if ',' in text:
            parts = [p.strip() for p in text.split(',')]
        else:
            parts = [p.strip() for p in text.split()]
        
        for word in parts:
            # Kapitalisasi huruf pertama
            if len(word) > 0:
                word = word[0].upper() + word[1:]
                if word not in self._skills:
                    self._insert_tag(word)
        
        self._edit.clear()

    def _insert_tag(self, text):
        """Buat tag pill dengan desain baru: nama skill (bold) + tombol x (rounded border)."""
        tag = QFrame()
        tag.setObjectName("SkillTag")
        tag.setStyleSheet("""
            QFrame#SkillTag {
                background-color: #2C687B;
                border-radius: 15px;
                padding: 0;
            }
        """)
        # Menetapkan tinggi yang konsisten untuk tag
        tag.setFixedHeight(30)
        
        tag_lay = QHBoxLayout(tag)
        tag_lay.setContentsMargins(12, 0, 4, 0)
        tag_lay.setSpacing(6)

        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: white; border: none; background: transparent;")
        tag_lay.addWidget(lbl)

        # Tombol x dengan border bulat kecil di dalamnya
        btn_x = QPushButton("×")
        btn_x.setFixedSize(20, 20)
        btn_x.setCursor(Qt.PointingHandCursor)
        btn_x.setStyleSheet("""
            QPushButton {
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 10px;
                background: transparent;
                font-size: 16px;
                font-weight: normal;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-color: white;
            }
        """)

        def _remove(t=text, w=tag):
            if t in self._skills:
                self._skills.remove(t)
            self.tags_layout.removeWidget(w)
            w.deleteLater()
            if not self._skills:
                self.tags_widget.hide()

        btn_x.clicked.connect(_remove)
        tag_lay.addWidget(btn_x)

        self.tags_layout.addWidget(tag)
        self._skills.append(text)
        self.tags_widget.show()

    # ── Public API ──
    def get_skills(self):
        return list(self._skills)

    def clear_all(self):
        """Hapus semua tag dan kosongkan input."""
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._skills.clear()
        self._edit.clear()
        self.tags_widget.hide()

    def load_skills(self, skills_list):
        """Muat daftar skill ke dalam widget."""
        self.clear_all()
        for s in skills_list:
            if s:
                self._insert_tag(s)
