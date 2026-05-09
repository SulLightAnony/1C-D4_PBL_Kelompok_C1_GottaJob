"""
SkillTagInput — widget PyQt5 yang menampilkan tag pills
skill langsung di dalam satu box input (inline).
Mendukung Enter / tombol + untuk menambah skill,
dan klik x untuk menghapus tag.
"""
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QScrollArea, QWidget, QLineEdit,
    QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt


class SkillTagInput(QFrame):
    """Widget input skill yang menampilkan tag pills langsung di dalam box input."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._skills = []
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("SkillTagInput")
        self.setMinimumHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet("""
            QFrame#SkillTagInput {
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                background-color: #fafafa;
            }
            QFrame#SkillTagInput:focus-within {
                border: 1px solid #2C687B;
                background-color: #fff;
            }
        """)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(6, 5, 0, 5)
        outer.setSpacing(0)

        # Scroll area horizontal untuk tag + input
        self._scroll = QScrollArea()
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFixedHeight(34)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._inner = QWidget()
        self._inner.setStyleSheet("background: transparent;")
        self._inner_layout = QHBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(5)
        self._inner_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # QLineEdit selalu di ujung kanan tags
        self._edit = QLineEdit()
        self._edit.setPlaceholderText("Tambah skill...")
        self._edit.setMinimumWidth(120)
        self._edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._edit.setFixedHeight(28)
        self._edit.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #333;
                font-size: 13px;
                padding: 0 4px;
            }
        """)
        self._edit.returnPressed.connect(self._add_from_input)
        self._inner_layout.addWidget(self._edit)
        self._inner_layout.addStretch()

        self._scroll.setWidget(self._inner)
        outer.addWidget(self._scroll, 1)

        # Tombol +
        self._btn_add = QPushButton("+")
        self._btn_add.setFixedSize(44, 44)
        self._btn_add.setCursor(Qt.PointingHandCursor)
        self._btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2C687B;
                border: none;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #408699; }
        """)
        self._btn_add.clicked.connect(self._add_from_input)
        outer.addWidget(self._btn_add)

    def _add_from_input(self):
        text = self._edit.text().strip()
        if not text:
            return
        for word in text.split():
            word = word.strip()
            if word:
                word = word[0].upper() + word[1:]
                if word not in self._skills:
                    self._insert_tag(word)
        self._edit.clear()
        # Scroll ke kanan setelah tag ditambah
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        self._scroll.horizontalScrollBar().setValue(
            self._scroll.horizontalScrollBar().maximum()
        )

    def _insert_tag(self, text):
        """Masukkan tag pill tepat sebelum QLineEdit."""
        tag = QFrame()
        tag.setStyleSheet("""
            QFrame {
                background-color: #1e4f5e;
                border-radius: 5px;
            }
        """)
        tag_lay = QHBoxLayout(tag)
        tag_lay.setContentsMargins(8, 3, 4, 3)
        tag_lay.setSpacing(4)

        lbl = QLabel(text)
        lbl.setStyleSheet("color: white; font-size: 12px; font-weight: 500; border: none; background: transparent;")

        btn_x = QPushButton("x")
        btn_x.setFixedSize(16, 16)
        btn_x.setCursor(Qt.PointingHandCursor)
        btn_x.setStyleSheet("""
            QPushButton {
                color: rgba(255,255,255,0.75);
                border: none;
                background: transparent;
                font-size: 11px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover { color: white; }
        """)

        def _remove(t=text, w=tag):
            if t in self._skills:
                self._skills.remove(t)
            idx = self._inner_layout.indexOf(w)
            if idx >= 0:
                self._inner_layout.takeAt(idx)
            w.deleteLater()

        btn_x.clicked.connect(_remove)
        tag_lay.addWidget(lbl)
        tag_lay.addWidget(btn_x)

        # Sisipkan sebelum QLineEdit (selalu di posisi count-2)
        count = self._inner_layout.count()
        insert_pos = max(0, count - 2)
        self._inner_layout.insertWidget(insert_pos, tag)
        self._skills.append(text)

    # ── Public API ──
    def get_skills(self):
        return list(self._skills)

    def clear_all(self):
        """Hapus semua tag dan kosongkan input."""
        to_remove = []
        for i in range(self._inner_layout.count()):
            item = self._inner_layout.itemAt(i)
            if item and item.widget() and item.widget() is not self._edit:
                to_remove.append(item.widget())
        for w in to_remove:
            self._inner_layout.removeWidget(w)
            w.deleteLater()
        self._skills.clear()
        self._edit.clear()

    def load_skills(self, skills_list):
        """Muat daftar skill ke dalam widget."""
        self.clear_all()
        for s in skills_list:
            if s:
                self._insert_tag(s)
