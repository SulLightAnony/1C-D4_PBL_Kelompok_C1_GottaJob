import sys
import os
import json
import glob

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QMessageBox, QStackedWidget, QListWidget, QListWidgetItem,
    QProgressDialog, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QSize
from PyQt5.QtGui import QPixmap, QIcon

class DeadLinkReviewDialog(QDialog):
    """Dialog untuk menampilkan daftar link mati dan meminta konfirmasi hapus."""
    def __init__(self, dead_jobs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review Lowongan Kadaluarsa")
        self.setMinimumSize(700, 450)
        
        lay = QVBoxLayout(self)
        
        lbl = QLabel(f"Ditemukan {len(dead_jobs)} lowongan yang link-nya sudah tidak aktif.\nCentang yang ingin Anda hapus:")
        lbl.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        lay.addWidget(lbl)
        
        self.table = QTableWidget(len(dead_jobs), 4)
        self.table.setHorizontalHeaderLabels(["Hapus?", "Pekerjaan", "Perusahaan", "Sumber File"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.rows_data = []
        for i, item in enumerate(dead_jobs):
            job = item['job']
            file_name = os.path.basename(item['file'])
            
            cb_item = QTableWidgetItem()
            cb_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            cb_item.setCheckState(Qt.Checked)
            self.table.setItem(i, 0, cb_item)
            
            self.table.setItem(i, 1, QTableWidgetItem(job.get("Judul_Pekerjaan", "-")))
            self.table.setItem(i, 2, QTableWidgetItem(job.get("Nama_Perusahaan", "-")))
            self.table.setItem(i, 3, QTableWidgetItem(file_name))
            
            self.rows_data.append(item)
            
        lay.addWidget(self.table)
        
        btn_lay = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Hapus yang Terpilih")
        btn_ok.setStyleSheet("background-color: #C0392B; color: white; font-weight: bold;")
        btn_ok.clicked.connect(self.accept)
        
        btn_lay.addStretch()
        btn_lay.addWidget(btn_cancel)
        btn_lay.addWidget(btn_ok)
        lay.addLayout(btn_lay)

    def get_selected_to_delete(self):
        to_delete = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).checkState() == Qt.Checked:
                to_delete.append(self.rows_data[i])
        return to_delete

class LinkValidatorWorker(QObject):
    """Worker untuk mengecek validitas link di semua file JSON secara background."""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list) # Mengembalikan list of {'file': path, 'job': job_dict}

    def __init__(self, db_dir):
        super().__init__()
        self.db_dir = db_dir

    def run(self):
        try:
            dead_links = []
            file_paths = glob.glob(os.path.join(self.db_dir, "*.json"))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            }
            import urllib.request
            import urllib.error

            for fp in file_paths:
                file_name = os.path.basename(fp)
                self.progress_signal.emit(f"Memeriksa: {file_name}")
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    continue
                
                for job in data:
                    url = job.get("Link_Lowongan", "")
                    if not url or url == "#": continue
                    
                    is_dead = False
                    try:
                        # Tahap 1: Coba HEAD
                        req = urllib.request.Request(url, headers=headers, method='HEAD')
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            if resp.status not in [200, 301, 302]:
                                is_dead = True
                    except urllib.error.HTTPError as e:
                        # 403/500/503 dianggap masih ada (mungkin bot diblokir)
                        if e.code in [403, 500, 503]:
                            is_dead = False
                        elif e.code in [404, 410]:
                            is_dead = True
                        else:
                            # Coba Tahap 2: GET
                            try:
                                req_get = urllib.request.Request(url, headers=headers, method='GET')
                                with urllib.request.urlopen(req_get, timeout=5) as resp_get:
                                    is_dead = resp_get.status not in [200, 301, 302]
                            except:
                                is_dead = True
                    except:
                        # Timeout/Connection error: Anggap masih aktif agar tidak sembarangan menghapus
                        is_dead = False

                    if is_dead:
                        dead_links.append({'file': fp, 'job': job})
            
            self.finished_signal.emit(dead_links)
        except Exception as e:
            print(f"Error in LinkValidatorWorker: {e}")
            self.finished_signal.emit([])

# Path dasar proyek
current_dir = os.path.dirname(os.path.abspath(__file__)) # pages/Job Archive
pages_dir = os.path.dirname(current_dir)                # pages
root_dir = os.path.dirname(pages_dir)                  # root

# Path asset spesifik
icon_path = os.path.join(root_dir, "assets", "Job Archive", "down.png").replace("\\", "/")

# Path untuk modul pengolahan dan visualisasi data
process_dir = os.path.join(pages_dir, "Modul")
if process_dir not in sys.path:
    sys.path.insert(0, process_dir)

from modul_visualisasi_data import PieChartWidget
from modul_pengolahan_data import hitung_persentase_skill, cari_pekerjaan_cocok, ambil_jenis_pekerjaan_unik
from modul_database import get_database_permanen_dir, set_favorit, get_favorit
from modul_antarmuka_pengguna import JobMatchResultContainer, JobDetailPanel, JobDashboardWidget

# ─────────────────────────────────────────────────────────────
# Style Sheet
# ─────────────────────────────────────────────────────────────
STYLE = """
QWidget#JobArchivePage {
    background-color: #F3F4F6;
}

QFrame#PanelCard {
    background-color: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #E0E7EF;
}

QLabel#JudulLabel, QWidget#JudulContainer {
    font-size: 18px;
    font-weight: bold;
    color: #2C687B;
    background-color: transparent;
}

QLabel#SubLabel {
    font-size: 13px;
    color: #7A9EB0;
    background-color: transparent;
}

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
QPushButton {
    background-color: #2C687B;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #408699;
}
""".replace("__ICON_PATH__", icon_path)

class JobArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("JobArchivePage")
        self.setStyleSheet(STYLE)
        
        # Gunakan direktori database permanen dari modul database
        self.db_dir = get_database_permanen_dir()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(28, 22, 28, 22)
        self.main_layout.setSpacing(18)

        # ── Panel Atas (Pemilihan Data) ──
        box = QFrame()
        box.setObjectName("PanelCard")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(16, 16, 16, 16)

        # Judul dengan Icon
        judul_container = QWidget()
        judul_container.setObjectName("JudulContainer")
        judul_layout = QHBoxLayout(judul_container)
        judul_layout.setContentsMargins(0, 0, 0, 0)
        judul_layout.setSpacing(10)

        icon_label = QLabel()
        archive_icon_path = os.path.join(root_dir, "assets", "Job Archive", "archives.png")
        pixmap = QPixmap(archive_icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        judul = QLabel("Job Archive")
        judul.setObjectName("JudulLabel")
        
        judul_layout.addWidget(icon_label)
        judul_layout.addWidget(judul)
        judul_layout.addStretch()

        sub = QLabel("Pilih data lowongan yang telah tersimpan untuk melihat visualisasinya.")
        sub.setObjectName("SubLabel")

        # Kontrol pemilihan file
        ctrl_layout = QHBoxLayout()
        self.combo_file = QComboBox()
        self.combo_file.currentIndexChanged.connect(self._on_file_selected)
        
        btn_refresh = QPushButton(" Perbarui Daftar")
        refresh_icon_path = os.path.join(root_dir, "assets", "Job Archive", "refresh.png")
        btn_refresh.setIcon(QIcon(refresh_icon_path))
        btn_refresh.setIconSize(QSize(18, 18))
        btn_refresh.setToolTip("Muat ulang daftar file data dari database")
        btn_refresh.clicked.connect(self.load_file_list)
        
        ctrl_layout.addWidget(self.combo_file, stretch=1)
        ctrl_layout.addWidget(btn_refresh)

        box_layout.addWidget(judul_container)
        box_layout.addWidget(sub)
        box_layout.addSpacing(10)
        box_layout.addLayout(ctrl_layout)

        self.main_layout.addWidget(box)

        self.main_stack = QStackedWidget()
        self.main_layout.addWidget(self.main_stack, stretch=1)

        # 1. VIEW DASHBOARD
        self.chart = PieChartWidget(size_ratio=0.8)
        self.dashboard_view = JobDashboardWidget(self.chart)
        self.dashboard_view.find_match_clicked.connect(self._show_matches)
        
        # Skill list reference for backward compatibility
        self.skill_list = self.dashboard_view.skill_list

        # 2. VIEW TABEL HASIL

        # 2. VIEW TABEL HASIL
        self.table_view = QFrame()
        self.table_view.setObjectName("PanelCard")
        table_lay = QVBoxLayout(self.table_view)
        table_lay.setContentsMargins(30, 25, 30, 25)
        
        t_header = QHBoxLayout()
        t_header.addWidget(QLabel("Rekomendasi Lowongan Pekerjaan", objectName="JudulLabel"))
        t_header.addStretch()
        btn_back = QPushButton("← Kembali")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.main_stack.setCurrentWidget(self.dashboard_view))
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2C687B;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2C687B;
                border-radius: 6px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #E2EFF1;
            }
        """)
        t_header.addWidget(btn_back)
        table_lay.addLayout(t_header)
        
        self.match_results = JobMatchResultContainer()
        self.match_results.itemDoubleClicked.connect(self._show_job_detail)
        self.match_results.favorite_clicked.connect(self._on_favorite_clicked)
        self.match_results.delete_clicked.connect(self._on_delete_clicked)
        table_lay.addWidget(self.match_results)

        # 3. VIEW DETAIL
        self.detail_view = JobDetailPanel(on_back_callback=lambda: self.main_stack.setCurrentWidget(self.table_view))

        # Add to stack
        self.main_stack.addWidget(self.dashboard_view)
        self.main_stack.addWidget(self.table_view)
        self.main_stack.addWidget(self.detail_view)
        
        # Load daftar file pertama kali (tanpa auto-check link agar tidak mengganggu start-up)
        self.load_file_list(auto_check=True)


    def load_file_list(self, auto_check=False):
        """Memuat daftar file JSON dan opsional melakukan validasi link."""
        self.combo_file.clear()
        self.combo_file.addItem("-- Pilih File Data --", "")
        
        if not os.path.exists(self.db_dir):
            return
            
        file_paths = glob.glob(os.path.join(self.db_dir, "*.json"))
        for fp in file_paths:
            file_name = os.path.basename(fp)
            self.combo_file.addItem(file_name, fp)

        # Jika dipanggil via tombol (manual refresh), tanya apakah mau bersih-bersih data
        if not auto_check:
            res = QMessageBox.question(
                self, "Validasi Link", 
                "Apakah Anda ingin sekaligus mengecek dan menghapus lowongan yang sudah kadaluarsa?\n"
                "(Proses ini mungkin memerlukan waktu beberapa saat)",
                QMessageBox.Yes | QMessageBox.No
            )
            if res == QMessageBox.Yes:
                self._start_link_validation()

    def _start_link_validation(self):
        self.progress_dialog = QProgressDialog("Memulai validasi link...", "Batal", 0, 0, self)
        self.progress_dialog.setWindowTitle("Membersihkan Data Kadaluarsa")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        self.val_thread = QThread()
        self.val_worker = LinkValidatorWorker(self.db_dir)
        self.val_worker.moveToThread(self.val_thread)

        self.val_thread.started.connect(self.val_worker.run)
        self.val_worker.progress_signal.connect(self.progress_dialog.setLabelText)
        self.val_worker.finished_signal.connect(self._on_validation_finished)
        self.val_worker.finished_signal.connect(self.val_thread.quit)
        
        self.val_thread.start()

    def _on_validation_finished(self, dead_links):
        self.progress_dialog.close()
        
        if not dead_links:
            QMessageBox.information(self, "Selesai", "Semua lowongan dalam arsip masih aktif.")
            return
            
        # Tampilkan dialog review
        dialog = DeadLinkReviewDialog(dead_links, self)
        if dialog.exec_() == QDialog.Accepted:
            to_delete = dialog.get_selected_to_delete()
            if not to_delete:
                return
                
            # Kelompokkan berdasarkan file agar tidak bolak-balik buka file
            by_file = {}
            for item in to_delete:
                fp = item['file']
                if fp not in by_file: by_file[fp] = []
                by_file[fp].append(item['job'])
                
            total_deleted = 0
            for fp, jobs_to_remove in by_file.items():
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Filter data
                new_data = [j for j in data if j not in jobs_to_remove]
                total_deleted += (len(data) - len(new_data))
                
                if not new_data:
                    os.remove(fp)
                else:
                    with open(fp, "w", encoding="utf-8") as f:
                        json.dump(new_data, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "Berhasil", f"Berhasil menghapus {total_deleted} lowongan kadaluarsa.")
            self.load_file_list(auto_check=True)

    def _on_file_selected(self, index):
        file_path = self.combo_file.itemData(index)
        if not file_path or not os.path.exists(file_path):
            self.chart.set_data({})
            if hasattr(self, 'skill_list'):
                self.skill_list.clear()
            if hasattr(self, 'dashboard_view'):
                self.dashboard_view.update_stats(0, 0, "-")
            self.current_file = None
            return
            
        try:
            hasil_olah = hitung_persentase_skill(file_path)
            self.main_stack.setCurrentWidget(self.dashboard_view)
            self.skill_list.clear()
            self.current_file = file_path

            if hasil_olah:
                with open(file_path, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                
                total_jobs = len(data_json)
                total_skills = sum(len(s) for s in hasil_olah.values())
                
                unique_types = ambil_jenis_pekerjaan_unik(file_path)
                        
                max_p = max(hasil_olah.keys())
                dominant_skill = hasil_olah[max_p][0]
                
                self.dashboard_view.update_stats(total_jobs, total_skills, dominant_skill)
                self.chart.set_data(hasil_olah)
                
                all_s = []
                for p, ss in hasil_olah.items():
                    for s in ss: all_s.append((s, p))
                all_s.sort(key=lambda x: (-x[1], x[0]))
                
                for s_name, p in all_s:
                    item = QListWidgetItem(f"{s_name} ({p}%)")
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    self.skill_list.addItem(item)
                    
                self.dashboard_view.job_type_list.clear()
                for jt in unique_types:
                    item = QListWidgetItem(jt)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    self.dashboard_view.job_type_list.addItem(item)
            else:
                self.chart.set_data({})
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {e}")

    def _show_matches(self):
        selected = []
        for i in range(self.skill_list.count()):
            item = self.skill_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text().split(" (")[0])
        
        if not selected:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu skill.")
            return

        selected_job_types = []
        for i in range(self.dashboard_view.job_type_list.count()):
            item = self.dashboard_view.job_type_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_job_types.append(item.text())

        self.user_skills = [s.lower() for s in selected]
        hasil = cari_pekerjaan_cocok(self.current_file, selected, selected_job_types)
        
        if not hasil:
            QMessageBox.information(self, "Info", "Tidak ada kecocokan.")
            return
            
        self.current_matches = hasil
        fav = get_favorit()
        fav_link = fav.get("Link_Lowongan") if fav else None
        
        # Tampilkan Favorit & Hapus (show_save=False)
        self.match_results.set_data(hasil, selected, show_save=False, show_favorite=True, show_delete=True, fav_link=fav_link)
        self.main_stack.setCurrentWidget(self.table_view)

    def _show_job_detail(self, item):
        data = self.current_matches[item.row()]
        self.detail_view.update_data(data, self.user_skills)
        self.main_stack.setCurrentWidget(self.detail_view)

    def _on_favorite_clicked(self, job_data):
        """Menangani klik tombol favorit di Archive."""
        existing_fav = get_favorit()
        if existing_fav:
            res = QMessageBox.question(
                self, "Konfirmasi Favorit",
                "Pekerjaan sebelumnya yang ditandai favorit akan hilang dari dashboard, apakah kamu yakin?",
                QMessageBox.Yes | QMessageBox.No
            )
            if res == QMessageBox.No:
                return

        if set_favorit(job_data):
            QMessageBox.information(self, "Berhasil", f"'{job_data.get('Judul_Pekerjaan')}' sekarang menjadi favorit utama Anda!")
            
            # Refresh tabel
            self.match_results.set_data(
                self.current_matches, 
                self.user_skills, 
                show_save=False, 
                show_favorite=True, 
                show_delete=True,
                fav_link=job_data.get("Link_Lowongan")
            )
        else:
            QMessageBox.warning(self, "Gagal", "Gagal menetapkan favorit.")

    def _on_delete_clicked(self, job_data):
        """Menangani penghapusan item pekerjaan dari arsip."""
        res = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus '{job_data.get('Judul_Pekerjaan')}' dari arsip ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if res == QMessageBox.No:
            return

        try:
            # 1. Baca file saat ini
            with open(self.current_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 2. Filter data (hapus yang cocok)
            # Karena job_data mungkin punya field tambahan dari pengolahan (seperti match_percentage),
            # kita bandingkan link lowongannya yang unik.
            target_link = job_data.get("Link_Lowongan")
            new_data = [j for j in data if j.get("Link_Lowongan") != target_link]
            
            if len(new_data) == len(data):
                QMessageBox.warning(self, "Gagal", "Data tidak ditemukan di file asli.")
                return

            # 3. Tulis kembali atau hapus file jika kosong
            if not new_data:
                os.remove(self.current_file)
                QMessageBox.information(self, "Berhasil", "Data terakhir dihapus, file arsip dibersihkan.")
                self.load_file_list(auto_check=True)
                self.main_stack.setCurrentWidget(self.dashboard_view)
            else:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=4)
                
                QMessageBox.information(self, "Berhasil", "Pekerjaan berhasil dihapus dari arsip.")
                
                # 4. Refresh tampilan tabel
                # Update current_matches list
                self.current_matches = [m for m in self.current_matches if m.get("Link_Lowongan") != target_link]
                
                if not self.current_matches:
                    self.main_stack.setCurrentWidget(self.dashboard_view)
                else:
                    fav = get_favorit()
                    fav_link = fav.get("Link_Lowongan") if fav else None
                    self.match_results.set_data(
                        self.current_matches, 
                        self.user_skills, 
                        show_save=False, 
                        show_favorite=True, 
                        show_delete=True,
                        fav_link=fav_link
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menghapus data: {e}")
