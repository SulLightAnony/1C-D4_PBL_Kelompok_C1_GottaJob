# pages/live_discovery.py
import sys
import os
import json
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QProgressBar, QMessageBox,
    QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

# Tambahkan path untuk modul pengolahan, visualisasi data, dan database
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(base_dir)

# Path untuk folder pages/Modul
process_dir = os.path.join(base_dir, "Modul")
if process_dir not in sys.path:
    sys.path.insert(0, process_dir)

# Path untuk folder database (di root)
db_mod_dir = os.path.join(root_dir, "database")
if db_mod_dir not in sys.path:
    sys.path.insert(0, db_mod_dir)

from modul_visualisasi_data import PieChartWidget
from modul_antarmuka_pengguna import JobMatchResultContainer, JobDetailPanel, JobDashboardWidget
from modul_database import (simpan_ke_database_sementara, simpan_ke_database_permanen, 
                            bersihkan_database_sementara, set_favorit, get_favorit)

# ─────────────────────────────────────────────────────────────
# Worker: jalankan scraper di thread terpisah agar UI tidak freeze
# ─────────────────────────────────────────────────────────────
class ScraperWorker(QObject):
    log_signal    = pyqtSignal(str)   # kirim teks log ke UI
    result_signal = pyqtSignal(str)   # kirim PATH FILE setelah selesai
    done_signal   = pyqtSignal()      # sinyal selesai

    def __init__(self, keywords: list, pages: list):
        super().__init__()
        self.keywords = keywords
        self.pages = pages
        self._stopped = False

    def run(self):
        # Import scraper dari subfolder pages/Modul/Scraper/
        # base_dir di sini adalah folder 'pages'
        base_pages_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scraper_dir = os.path.join(base_pages_dir, "Modul", "Scraper")
        
        if scraper_dir not in sys.path:
            sys.path.insert(0, scraper_dir)

        try:
            import random
            from scrapper_main import filter_relevan, ambil_nama_dominan
            from scraper_glints import GlintsScraper
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Gagal import scraper: {e}")
            self.done_signal.emit()
            return

        ROOT_DIR = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        )
        DB_DIR = os.path.join(ROOT_DIR, "database")
        os.makedirs(DB_DIR, exist_ok=True)

        global_seen_links  = set()
        data_bersih_unik   = []
        total_tidak_relevan = 0
        total_duplikat      = 0

        self.log_signal.emit(" Memulai pencarian...")
        mesin = GlintsScraper()

        try:
            for idx, kw in enumerate(self.keywords):
                page_num = self.pages[idx]
                self.log_signal.emit(f"\n🔍 Keyword [{idx+1}/{len(self.keywords)}]: {kw.upper()} (Page {page_num})")
                hasil = mesin.scrape_keyword(kw, page=page_num)

                relevan, jml_buang = filter_relevan(hasil, kw)
                total_tidak_relevan += jml_buang
                self.log_signal.emit(
                    f"  ✅ {len(relevan)}/{len(hasil)} job lolos filter relevansi."
                )

                duplikat_lokal = 0
                for job in relevan:
                    link = job.get("Link_Lowongan", "-")
                    if link != "-" and link in global_seen_links:
                        duplikat_lokal += 1
                        total_duplikat += 1
                        continue
                    if link != "-":
                        global_seen_links.add(link)
                    data_bersih_unik.append(job)

                if duplikat_lokal:
                    self.log_signal.emit(f"  ℹ️  {duplikat_lokal} duplikat dibuang.")

                if idx < len(self.keywords) - 1:
                    jeda = random.uniform(10.0, 20.0)
                    self.log_signal.emit(f"  ⏳ Jeda {jeda:.1f} detik...")
                    time.sleep(jeda)

            # Simpan ke JSON menggunakan modul_database
            if data_bersih_unik:
                semua_judul  = [j.get("Judul_Pekerjaan", "-") for j in data_bersih_unik]
                nama_dominan = ambil_nama_dominan(semua_judul)
                
                # Gunakan modul database
                path_hasil = simpan_ke_database_sementara(data_bersih_unik, nama_dominan)
                
                if path_hasil:
                    self.log_signal.emit(f"\n💾 Tersimpan ke Database Sementara: {path_hasil}")
                    self.result_signal.emit(path_hasil)
                else:
                    self.log_signal.emit("\n❌ Gagal menyimpan data.")
            else:
                self.log_signal.emit("\n⚠️  Tidak ada data yang berhasil dikumpulkan.")
                self.result_signal.emit("EMPTY")

        except Exception as e:
            self.log_signal.emit(f"\n[ERROR] {e}")
        finally:
            self.log_signal.emit("🔒 Menutup mesin scraper...")
            mesin.close()
            self.done_signal.emit()


# ─────────────────────────────────────────────────────────────
# Halaman Live Discovery
# ─────────────────────────────────────────────────────────────
STYLE = """
QWidget#LiveDiscoveryPage {
    background-color: #F3F4F6;
}

/* ── Header bar ── */
QFrame#HeaderBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2C687B, stop:1 #3A8FA3);
    border-radius: 0px;
}

/* ── Search card ── */
QFrame#SearchCard {
    background-color: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #E0E7EF;
}
QFrame#SearchCard QLabel {
    background-color: transparent;
}

QLineEdit#KeywordInput {
    border: 2px solid #B2D2D9;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 15px;
    color: #1E3A4A;
    background: #F7FBFC;
}
QLineEdit#KeywordInput:focus {
    border: 2px solid #2C687B;
    background: #FFFFFF;
}

QPushButton#BtnScrape {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2C687B, stop:1 #3A8FA3);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 15px;
    font-weight: bold;
}
QPushButton#BtnScrape:hover  { background: #408699; }
QPushButton#BtnScrape:disabled { background: #9BBEC8; }

/* ── Progress bar ── */
QProgressBar {
    border: none;
    border-radius: 6px;
    background: #D9EDF2;
    height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2C687B, stop:1 #5BB8CC);
    border-radius: 6px;
}

QFrame#PanelCard {
    background-color: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #E0E7EF;
}
"""


class LiveDiscoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LiveDiscoveryPage")
        self.setStyleSheet(STYLE)

        self._thread  = None
        self._worker  = None
        self._running = False
        self.last_scraped_file = None
        self.user_selected_skills = []
        self.keyword_pages = {}
        self.last_search_raw = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(18)

        root.addWidget(self._build_search_card())
        
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #7A9EB0; font-style: italic; margin-left: 5px;")
        root.addWidget(self.status_lbl)
        
        root.addWidget(self._build_progress_bar())
        
        self.main_stack = QStackedWidget()
        root.addWidget(self.main_stack, stretch=1)

        # ─── VIEW 1: DASHBOARD ───
        self.chart = PieChartWidget(size_ratio=0.8)
        self.dashboard_view = JobDashboardWidget(self.chart)
        self.dashboard_view.find_match_clicked.connect(self._show_matches)
        self.skill_list = self.dashboard_view.skill_list
        
        # ─── VIEW 2: TABEL HASIL ───
        self.table_panel = QFrame()
        self.table_panel.setObjectName("PanelCard")
        table_lay = QVBoxLayout(self.table_panel)
        table_lay.setContentsMargins(30, 25, 30, 25)
        
        header_lay = QHBoxLayout()
        lbl_table_title = QLabel("Rekomendasi Lowongan Pekerjaan")
        lbl_table_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C687B; background-color: transparent;")
        header_lay.addWidget(lbl_table_title)
        header_lay.addStretch()
        
        self.btn_back = QPushButton("← Kembali")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self._back_to_dashboard)
        self.btn_back.setStyleSheet("""
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
        header_lay.addWidget(self.btn_back)
        table_lay.addLayout(header_lay)
        table_lay.addSpacing(15)
        
        self.match_results = JobMatchResultContainer()
        self.match_results.itemDoubleClicked.connect(self._show_job_detail)
        self.match_results.save_clicked.connect(self._on_save_permanent_clicked)
        self.match_results.favorite_clicked.connect(self._on_favorite_clicked)
        table_lay.addWidget(self.match_results)
        
        # ─── VIEW 3: DETAIL ───
        self.detail_panel = JobDetailPanel(on_back_callback=self._back_to_results)
        
        # Tambahkan ke stack
        self.main_stack.addWidget(self.dashboard_view)
        self.main_stack.addWidget(self.table_panel)
        self.main_stack.addWidget(self.detail_panel)
        
        self.main_stack.setCurrentWidget(self.dashboard_view)

    def _build_search_card(self):
        card = QFrame()
        card.setObjectName("SearchCard")
        card.setFixedHeight(90)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)

        lbl = QLabel("Nama Pekerjaan:")
        lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #2C687B;")
        lbl.setFixedWidth(140)

        self.keyword_input = QLineEdit()
        self.keyword_input.setObjectName("KeywordInput")
        self.keyword_input.setPlaceholderText("Contoh: python developer, data scientist")
        self.keyword_input.returnPressed.connect(self._start_scraping)

        self.btn_scrape = QPushButton("▶  Cari Pekerjaan")
        self.btn_scrape.setObjectName("BtnScrape")
        self.btn_scrape.setFixedWidth(180)
        self.btn_scrape.clicked.connect(self._start_scraping)

        lay.addWidget(lbl)
        lay.addWidget(self.keyword_input, stretch=1)
        lay.addWidget(self.btn_scrape)
        return card

    def _build_progress_bar(self):
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(10)
        self.progress.setVisible(False)
        return self.progress

    def _start_scraping(self):
        raw = self.keyword_input.text().strip()
        if not raw:
            QMessageBox.warning(self, "Keyword Kosong", "Masukkan keyword pekerjaan terlebih dahulu.")
            return
        if self._running:
            return

        if self.last_search_raw != raw:
            # Bersihkan database sementara dan reset paginasi jika keyword berubah
            bersihkan_database_sementara()
            self.keyword_pages = {}
            self.last_search_raw = raw

        keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
        
        pages_to_fetch = []
        for kw in keywords:
            kw_lower = kw.lower()
            current_page = self.keyword_pages.get(kw_lower, 1)
            pages_to_fetch.append(current_page)
            # Increment the page for the next time this keyword is searched
            self.keyword_pages[kw_lower] = current_page + 1
            
        self._running = True
        self.btn_scrape.setEnabled(False)
        self.progress.setVisible(True)

        self._thread = QThread()
        self._worker = ScraperWorker(keywords, pages_to_fetch)
        self._worker.moveToThread(self._thread)

        self._worker.log_signal.connect(print)
        self._worker.log_signal.connect(self.status_lbl.setText)
        self._thread.started.connect(self._worker.run)
        self._worker.result_signal.connect(self._handle_result)
        self._worker.done_signal.connect(self._on_done)
        self._worker.done_signal.connect(self._thread.quit)

        icon_path = os.path.join(root_dir, "assets", "live discovery", "refresh.png")
        self.btn_scrape.setIcon(QIcon(icon_path))
        self.btn_scrape.setText(" Sedang mencari pekerjaan...")
        self._thread.start()

    def _handle_result(self, file_path):
        if file_path == "EMPTY":
            QMessageBox.information(self, "Informasi", "Tidak ada lowongan pekerjaan lagi yang relevan.")
            return
            
        try:
            from modul_pengolahan_data import hitung_persentase_skill
            self.last_scraped_file = file_path
            
            hasil = hitung_persentase_skill(file_path)
            if hasil:
                with open(file_path, "r", encoding="utf-8") as f:
                    total_jobs = len(json.load(f))
                
                total_unique_skills = sum(len(skills) for skills in hasil.values())
                max_perc = max(hasil.keys())
                dominant_text = hasil[max_perc][0] if hasil[max_perc] else "-"
                
                self.dashboard_view.update_stats(total_jobs, total_unique_skills, dominant_text)
                self.chart.set_data(hasil)
                
                self.skill_list.clear()
                all_skills = []
                for perc, skills in hasil.items():
                    for s in skills:
                        all_skills.append((s, perc))
                all_skills.sort(key=lambda x: (-x[1], x[0]))
                
                for name, perc in all_skills:
                    item = QListWidgetItem(f"{name} ({perc}%)")
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    self.skill_list.addItem(item)
                
                self.main_stack.setCurrentWidget(self.dashboard_view)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengolah data: {e}")

    def _show_matches(self):
        if not self.last_scraped_file:
            QMessageBox.warning(self, "Peringatan", "Lakukan pencarian pekerjaan terlebih dahulu.")
            return

        selected_skills = []
        for i in range(self.skill_list.count()):
            item = self.skill_list.item(i)
            if item.checkState() == Qt.Checked:
                skill_name = item.text().split(" (")[0]
                selected_skills.append(skill_name)

        if not selected_skills:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu skill.")
            return

        self.user_selected_skills = [s.lower() for s in selected_skills]
        try:
            from modul_pengolahan_data import cari_pekerjaan_cocok
            hasil = cari_pekerjaan_cocok(self.last_scraped_file, selected_skills)
            if not hasil:
                QMessageBox.information(self, "Informasi", "Tidak ada pekerjaan yang cocok.")
                return
            
            self.current_matches = hasil
            fav = get_favorit()
            fav_link = fav.get("Link_Lowongan") if fav else None
            self.match_results.set_data(hasil, selected_skills, fav_link=fav_link)
            self.main_stack.setCurrentWidget(self.table_panel)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mencari kecocokan: {e}")

    def _show_job_detail(self, item):
        row = item.row()
        if not hasattr(self, 'current_matches') or row >= len(self.current_matches):
            return
        self.detail_panel.update_data(self.current_matches[row], self.user_selected_skills)
        self.main_stack.setCurrentWidget(self.detail_panel)

    def _on_save_permanent_clicked(self, job_data):
        """Menangani klik tombol simpan per baris."""
        if not self.last_scraped_file:
            return
            
        path = simpan_ke_database_permanen(job_data, self.last_scraped_file)
        if path == "DUPLICATE":
            QMessageBox.information(
                self, "Informasi", 
                f"Lowongan '{job_data.get('Judul_Pekerjaan')}' sudah ada di Job Archive."
            )
        elif path:
            QMessageBox.information(
                self, "Berhasil", 
                f"Lowongan '{job_data.get('Judul_Pekerjaan')}' berhasil disimpan secara permanen ke Job Archive!"
            )
        else:
            QMessageBox.warning(self, "Gagal", "Gagal menyimpan lowongan secara permanen.")

    def _on_favorite_clicked(self, job_data):
        """Menangani klik tombol favorit."""
        # 1. Cek apakah sudah ada favorit sebelumnya
        existing_fav = get_favorit()
        if existing_fav:
            res = QMessageBox.question(
                self, "Konfirmasi Favorit",
                "Pekerjaan sebelumnya yang ditandai favorit akan hilang dari dashboard, apakah kamu yakin?",
                QMessageBox.Yes | QMessageBox.No
            )
            if res == QMessageBox.No:
                return

        # 2. Simpan ke database permanen (Otomatis)
        if self.last_scraped_file:
            simpan_ke_database_permanen(job_data, self.last_scraped_file)
        
        # 3. Set sebagai favorit utama
        if set_favorit(job_data):
            QMessageBox.information(self, "Berhasil", f"'{job_data.get('Judul_Pekerjaan')}' sekarang menjadi favorit utama Anda!")
            
            # 4. Refresh tabel untuk mengubah warna tombol
            self.match_results.set_data(
                self.current_matches, 
                self.user_selected_skills, 
                fav_link=job_data.get("Link_Lowongan")
            )
        else:
            QMessageBox.warning(self, "Gagal", "Gagal menetapkan favorit.")

    def _back_to_results(self):
        self.main_stack.setCurrentWidget(self.table_panel)

    def _back_to_dashboard(self):
        self.main_stack.setCurrentWidget(self.dashboard_view)

    def _on_done(self):
        self._running = False
        self.btn_scrape.setEnabled(True)
        self.btn_scrape.setIcon(QIcon())
        self.btn_scrape.setText("▶  Cari Pekerjaan")
        self.progress.setVisible(False)
        self.status_lbl.setText("Proses selesai.")
