import os
import sys
import copy
import threading
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QScrollArea, QFrame, QMessageBox, QComboBox, QStyledItemDelegate, QStackedWidget, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pages_dir not in sys.path:
    sys.path.insert(0, _pages_dir)

from CRUD.Shared import muat_data, simpan_data
from modul_antarmuka_pengguna import KeyboardScrollArea, show_message, show_question, ActionButton
from Modul.modul_database import catat_aktivitas
from constants import (
    refresh_icon_path, plus_icon_path, trash_icon_path, 
    search_icon_path, down_icon_path, post_icon_path
)

from CRUD.Read import JobDetailPage, SelectCVDialog
from CRUD.Create import JobFormPage
from flow_layout import FlowLayout
from job_card_widget import JobCardWidget

class JobPostingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ids = set()
        self.data = []
        self._init_stack()
        self.load_data()

    def update_theme_mode(self, is_admin):
        """Memperbarui gaya tombol mengikuti peran user yang sedang login."""
        theme = "admin" if is_admin else "user"
        if hasattr(self, 'btn_refresh'):
            self.btn_refresh.set_theme(theme)
        if hasattr(self, 'btn_add'):
            self.btn_add.set_theme(theme)

    def showEvent(self, event):
        if hasattr(self, 'page_stack'):
            self.page_stack.setCurrentIndex(0)
        super().showEvent(event)

    def _init_stack(self):
        """Membungkus halaman daftar, halaman form, dan halaman detail ke dalam QStackedWidget."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.page_stack = QStackedWidget()
        
        self.list_page = QWidget()
        self.setup_ui() # mengisi self.list_page
        
        self.form_page = JobFormPage(self)
        self.detail_page = JobDetailPage(self)

        self.page_stack.addWidget(self.list_page)
        self.page_stack.addWidget(self.form_page)
        self.page_stack.addWidget(self.detail_page)

        # Connect Detail Page signals
        self.detail_page.back_clicked.connect(lambda: self.page_stack.setCurrentIndex(0))
        self.detail_page.edit_requested.connect(self.edit_data)
        self.detail_page.delete_requested.connect(self.delete_single_data)
        self.detail_page.lamar_requested.connect(self.proses_lamar)

        # Connect Form Page signals
        self.form_page.back_clicked.connect(lambda: self.page_stack.setCurrentIndex(0))
        self.form_page.save_requested.connect(self._save_job_from_form)

        outer_layout.addWidget(self.page_stack)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self.list_page)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Header Row
        header_layout = QHBoxLayout()
        
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
        self.btn_refresh = ActionButton(" Refresh", icon_path=refresh_icon_path, color_theme="user")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_delete_multi = ActionButton(" Hapus ", icon_path=trash_icon_path, color_theme="danger")
        self.btn_delete_multi.clicked.connect(self.delete_selected)
        self.btn_delete_multi.hide() # Hidden by default
        
        self.btn_add = ActionButton(" Tambah Data ", icon_path=plus_icon_path, color_theme="user")
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
            card.lamar_clicked.connect(self.proses_lamar)
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
        """Beralih ke halaman form tambah."""
        self.form_page.set_mode_add()
        self.page_stack.setCurrentIndex(1)

    def edit_data(self, job_data):
        """Beralih ke halaman form untuk mengedit data yang sudah ada."""
        self.form_page.set_mode_edit(job_data)
        self.page_stack.setCurrentIndex(1)

    def _save_job_from_form(self, form_data, editing_job_id):
        if editing_job_id:
            from CRUD.Update import proses_update_job
            success, msg, new_data = proses_update_job(editing_job_id, form_data, self.data)
        else:
            from CRUD.Create import proses_create_job
            success, msg, new_data = proses_create_job(form_data, self.data)

        if not success:
            show_message(self, "Validasi Gagal", msg)
            return

        self.data = new_data
        action_msg = "Diperbarui" if editing_job_id else "Ditambah"
        catat_aktivitas(f"<b>Lowongan {action_msg}</b><br>{form_data['judul']}", role="admin")
        self.simpan_data_async()

        self.page_stack.setCurrentIndex(0)
        self.refresh_ui_only()
        show_message(self, "Berhasil", msg)

    def delete_single_data(self, job_data):
        reply = show_question(self, 'Konfirmasi Hapus', "Yakin ingin menghapus lowongan ini?")
        if reply == QMessageBox.Yes:
            from CRUD.Delete import proses_delete_job
            success, msg, new_data = proses_delete_job(job_data.get("id"), self.data)
            if success:
                self.data = new_data
                self.simpan_data_async()
                catat_aktivitas(msg, role="admin")
                self.refresh_ui_only()
                if self.page_stack.currentIndex() == 2:
                    self.page_stack.setCurrentIndex(0)

    def delete_selected(self):
        from CRUD.Delete import proses_delete_massal
        reply = show_question(self, 'Konfirmasi Hapus Massal', f"Yakin ingin menghapus {len(self.selected_ids)} lowongan terpilih?")
        if reply == QMessageBox.Yes:
            success, msg, new_data = proses_delete_massal(self.selected_ids, self.data)
            if success:
                self.data = new_data
                self.simpan_data_async()
                catat_aktivitas(msg, role="admin")
                self.selected_ids = set()
                self.refresh_ui_only()

    def proses_lamar(self, job_data):
        if job_data.get("Is_lamar", False):
            show_message(self, "Informasi", "Anda sudah melamar pekerjaan ini.")
            return

        dialog = SelectCVDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
            
        cv_data = dialog.selected_cv
        cv_name = cv_data.get("cv_name", "CV Terpilih")

        res = show_question(
            self, "Konfirmasi Pengiriman",
            f"Ingin mengirim {cv_name} untuk melamar posisi {job_data.get('Judul_Pekerjaan')} di {job_data.get('Nama_Perusahaan')}?"
        )
        
        if res == QMessageBox.Yes:
            for job in self.data:
                if job.get("id") == job_data.get("id"):
                    job["Is_lamar"] = True
                    break
            
            self.simpan_data_async()
            self.refresh_ui_only()
            
            show_message(
                self, "Berhasil",
                f"CV '{cv_name}' telah berhasil dikirim!\nStatus lamaran telah diperbarui."
            )
            
            if self.page_stack.currentIndex() == 2:
                self.detail_page.setData(job_data)

    def show_job_details(self, job_data):
        self.detail_page.setData(job_data)
        self.page_stack.setCurrentIndex(2)
