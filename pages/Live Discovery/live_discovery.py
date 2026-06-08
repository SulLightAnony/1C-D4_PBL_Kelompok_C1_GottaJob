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


def _get_base_path():
    """
    Mengembalikan path root proyek secara benar baik dalam
    mode development maupun setelah di-freeze oleh PyInstaller.
    - Frozen (dist/GottaJob/GottaJob.exe) -> dist/GottaJob/
    - Development (pages/Live Discovery/live_discovery.py) -> project root
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Naik 3 level: live_discovery.py -> Live Discovery -> pages -> root
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_asset_path(*parts):
    """Mengembalikan path absolut ke file di dalam folder assets/."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = _get_base_path()
    return os.path.normpath(os.path.join(base, 'assets', *parts))


def _ensure_modul_in_path():
    """Pastikan folder pages/Modul ada di sys.path (hanya mode dev)."""
    if getattr(sys, 'frozen', False):
        return  # Dalam mode frozen, semua modul sudah di-bundle
    base = _get_base_path()
    for d in [
        os.path.join(base, 'pages', 'Modul'),
        os.path.join(base, 'database'),
    ]:
        if d not in sys.path:
            sys.path.insert(0, d)


_ensure_modul_in_path()

from modul_visualisasi_data import PieChartWidget
from modul_antarmuka_pengguna import (
    JobMatchResultContainer, JobDetailPanel, JobDashboardWidget, 
    show_message, show_question, ActionButton, buat_tombol_kembali
)
from modul_database import (simpan_ke_database_sementara, simpan_ke_database_permanen, 
                            bersihkan_database_sementara, set_favorit, get_favorit, catat_aktivitas, get_all_saved_links)

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
        if getattr(sys, 'frozen', False):
            # Dalam mode frozen, semua modul sudah di-bundle oleh PyInstaller
            scraper_dir = None
        else:
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

        ROOT_DIR = _get_base_path()
        DB_DIR = os.path.join(ROOT_DIR, "database")
        os.makedirs(DB_DIR, exist_ok=True)
        search_icon_path = _get_asset_path('live discovery', 'search.png').replace('\\', '/')

        global_seen_links  = set()
        data_bersih_unik   = []
        total_tidak_relevan = 0
        total_duplikat      = 0

        self.log_signal.emit(" Memulai pencarian...")
        mesin = GlintsScraper()

        try:
            for idx, kw in enumerate(self.keywords):
                page_num = self.pages[idx]
                self.log_signal.emit(f"<img src='{search_icon_path}' width='14' height='14'> Keyword [{idx+1}/{len(self.keywords)}]: {kw.upper()} (Page {page_num})")
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
    background-color: transparent;
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
    favorite_changed = pyqtSignal()

    def update_theme_mode(self, is_admin):
        """Memperbarui warna tombol di Live Discovery dan komponen dashboard anaknya."""
        self.is_admin = is_admin
        theme = "admin" if is_admin else "user"
        if hasattr(self, 'btn_scrape'):
            self.btn_scrape.set_theme(theme)
        if hasattr(self, 'dashboard_view'):
            self.dashboard_view.update_theme_mode(theme)

    def reset_state(self):
        """Reset all inputs, variables, stats, lists, and stacked widget views to initial state."""
        # 1. Stop scraping thread if running
        if self._running:
            try:
                if self._worker:
                    self._worker.log_signal.disconnect()
                    self._worker.result_signal.disconnect()
                    self._worker.done_signal.disconnect()
                if self._thread:
                    self._thread.quit()
                    self._thread.wait()
            except Exception:
                pass
            self._running = False
            self.btn_scrape.setEnabled(True)
            self.progress.setVisible(False)
            icon_path = _get_asset_path('live discovery', 'refresh.png')
            self.btn_scrape.setIcon(QIcon(icon_path))
            self.btn_scrape.setText("▶  Cari Pekerjaan")

        # 2. Reset state variables
        self.last_scraped_file = None
        self.user_selected_skills = []
        self.keyword_pages = {}
        self.last_search_raw = ""
        if hasattr(self, 'current_matches'):
            self.current_matches = []

        # 3. Clear inputs & labels
        self.keyword_input.clear()
        self.status_lbl.setText("")
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)

        # 4. Clear dashboard lists and stats
        self.skill_list.clear()
        self.dashboard_view.job_type_list.clear()
        self.dashboard_view.update_stats(0, 0, "-")
        self.chart.set_data({})

        # 5. Clear table results
        self.match_results.table.setRowCount(0)
        
        # Clear best match card sections
        for lay in [self.match_results.best_match_card.hard_skill_container, 
                    self.match_results.best_match_card.soft_skill_container, 
                    self.match_results.best_match_card.pos_skill_container]:
            self.match_results.best_match_card._clear_layout(lay)
        self.match_results.best_match_card.lbl_perc.setText("0%")
        self.match_results.best_match_card.lbl_title.setText("Nama Pekerjaan")
        self.match_results.best_match_card.lbl_company.setText("Nama Perusahaan")
        self.match_results.best_match_card.lbl_location.setText("📍 Lokasi")
        self.match_results.best_match_card.lbl_perc.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: white; background-color: #27AE60; border-radius: 12px; padding: 10px;"
        )
        self.match_results.best_match_card.setStyleSheet(
            "QFrame#PanelCard { background-color: white; border: 2px solid #27AE60; border-radius: 16px; }"
        )

        # 6. Reset views to default
        self.main_stack.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.right_stack.setCurrentIndex(0)

    def __init__(self):
        super().__init__()
        self.is_admin = False
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

        self.search_card = self._build_search_card()
        root.addWidget(self.search_card)
        
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
        
        self.btn_save_all = QPushButton(" 📥 Simpan Semua")
        self.btn_save_all.setStyleSheet("""
            QPushButton {
                background-color: #059669; color: white; border: none;
                border-radius: 6px; padding: 5px 15px; font-weight: bold;
                font-size: 14px; min-height: 25px;
            }
            QPushButton:hover { background-color: #047857; }
        """)
        self.btn_save_all.setCursor(Qt.PointingHandCursor)
        self.btn_save_all.clicked.connect(self._on_save_all_clicked)
        header_lay.addWidget(self.btn_save_all)
        
        self.btn_back = buat_tombol_kembali("← Kembali")
        self.btn_back.clicked.connect(self._back_to_dashboard)
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

        # Sembunyikan search card saat user berpindah halaman (mirip job_archive)
        self.main_stack.currentChanged.connect(self._update_search_card_visibility)
        self.dashboard_view.right_stack.currentChanged.connect(self._update_search_card_visibility)

    def _update_search_card_visibility(self):
        """
        Tampilkan search card HANYA saat dashboard utama aktif dan
        right_stack ada di index 0 (tampilan Pilih Skill).
        Sembunyikan di semua kondisi lain untuk mencegah aksi tidak sengaja.
        """
        on_dashboard = self.main_stack.currentWidget() == self.dashboard_view
        on_skill_page = self.dashboard_view.right_stack.currentIndex() == 0
        visible = on_dashboard and on_skill_page
        self.search_card.setVisible(visible)
        self.status_lbl.setVisible(visible)

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

        self.btn_scrape = ActionButton("▶  Cari Pekerjaan", color_theme="user")
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
            show_message(self, "Keyword Kosong", "Masukkan keyword pekerjaan terlebih dahulu.")
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

        icon_path = _get_asset_path('live discovery', 'refresh.png')
        self.btn_scrape.setIcon(QIcon(icon_path))
        self.btn_scrape.setText(" Sedang mencari pekerjaan...")
        self._thread.start()

    def _handle_result(self, file_path):
        if file_path == "EMPTY":
            show_message(self, "Informasi", "Tidak ada lowongan pekerjaan lagi yang relevan.")
            return
            
        try:
            from modul_pengolahan_data import hitung_persentase_skill, ambil_jenis_pekerjaan_unik
            self.last_scraped_file = file_path
            
            hasil = hitung_persentase_skill(file_path)
            if hasil:
                total_jobs = 0
                with open(file_path, "r", encoding="utf-8") as f:
                    total_jobs = len(json.load(f))
                
                role = "admin" if getattr(self, 'is_admin', False) else "user"
                catat_aktivitas(f"<b>Live Discovery Selesai</b><br>{os.path.basename(file_path).replace('.json', '')} · {total_jobs} hasil", role=role)

                unique_types = ambil_jenis_pekerjaan_unik(file_path)
                
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
                
                self.dashboard_view.job_type_list.clear()
                for jt in unique_types:
                    item = QListWidgetItem(jt)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    self.dashboard_view.job_type_list.addItem(item)
                
                self.main_stack.setCurrentWidget(self.dashboard_view)
        except Exception as e:
            show_message(self, "Error", f"Gagal mengolah data: {e}")

    def _show_matches(self):
        if not self.last_scraped_file:
            show_message(self, "Peringatan", "Lakukan pencarian pekerjaan terlebih dahulu.")
            return

        selected_skills = []
        for i in range(self.skill_list.count()):
            item = self.skill_list.item(i)
            if item.checkState() == Qt.Checked:
                skill_name = item.text().split(" (")[0]
                selected_skills.append(skill_name)

        if not selected_skills:
            show_message(self, "Peringatan", "Pilih minimal satu skill.")
            return

        selected_job_types = []
        for i in range(self.dashboard_view.job_type_list.count()):
            item = self.dashboard_view.job_type_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_job_types.append(item.text())

        self.user_selected_skills = [s.lower() for s in selected_skills]
        try:
            from modul_pengolahan_data import cari_pekerjaan_cocok
            hasil = cari_pekerjaan_cocok(self.last_scraped_file, selected_skills, selected_job_types)
            if not hasil:
                show_message(self, "Informasi", "Tidak ada pekerjaan yang cocok.")
                return
            
            self.current_matches = hasil
            fav = get_favorit()
            fav_link = fav.get("Link_Lowongan") if fav else None
            
            # Ambil semua link yang sudah tersimpan untuk update status tombol Simpan
            saved_links = get_all_saved_links()
            
            show_fav = not getattr(self, 'is_admin', False)
            self.match_results.set_data(hasil, selected_skills, show_favorite=show_fav, fav_link=fav_link, saved_links=saved_links)
            self.main_stack.setCurrentWidget(self.table_panel)
        except Exception as e:
            show_message(self, "Error", f"Gagal mencari kecocokan: {e}")

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
            show_message(
                self, "Informasi", 
                f"Lowongan '{job_data.get('Judul_Pekerjaan')}' sudah ada di Job Archive."
            )
        elif path:
            show_message(
                self, "Berhasil", 
                f"Lowongan '{job_data.get('Judul_Pekerjaan')}' berhasil disimpan secara permanen ke Job Archive!"
            )
            # Refresh tabel agar tombol Simpan berubah jadi Tersimpan
            fav = get_favorit()
            fav_link = fav.get("Link_Lowongan") if fav else None
            saved_links = get_all_saved_links()
            show_fav = not getattr(self, 'is_admin', False)
            self.match_results.set_data(self.current_matches, self.user_selected_skills, show_favorite=show_fav, fav_link=fav_link, saved_links=saved_links)
            role = "admin" if getattr(self, 'is_admin', False) else "user"
            catat_aktivitas(f"<b>Lowongan disimpan</b><br>{job_data.get('Nama_Perusahaan')}", role=role)
            self.favorite_changed.emit()
        else:
            show_message(self, "Gagal", "Gagal menyimpan lowongan secara permanen.")

    def _on_save_all_clicked(self):
        """Menyimpan seluruh lowongan pekerjaan yang tampil ke Job Archive."""
        if not self.last_scraped_file or not hasattr(self, 'current_matches') or not self.current_matches:
            show_message(self, "Informasi", "Tidak ada data untuk disimpan.")
            return

        res = show_question(self, "Konfirmasi", f"Apakah Anda yakin ingin menyimpan {len(self.current_matches)} pekerjaan ini ke Job Archive?")
        if res == QMessageBox.No:
            return

        berhasil = 0
        duplikat = 0
        gagal = 0
        
        for job_data in self.current_matches:
            path = simpan_ke_database_permanen(job_data, self.last_scraped_file)
            if path == "DUPLICATE":
                duplikat += 1
            elif path:
                berhasil += 1
            else:
                gagal += 1
                
        # Tampilkan ringkasan
        msg = []
        if berhasil > 0: msg.append(f"{berhasil} pekerjaan berhasil disimpan.")
        if duplikat > 0: msg.append(f"{duplikat} pekerjaan sudah ada (duplikat).")
        if gagal > 0: msg.append(f"{gagal} pekerjaan gagal disimpan.")
        
        show_message(self, "Hasil Simpan Semua", "\\n".join(msg) if msg else "Tidak ada yang diproses.")
        
        if berhasil > 0:
            role = "admin" if getattr(self, 'is_admin', False) else "user"
            catat_aktivitas(f"<b>{berhasil} Lowongan disimpan massal</b>", role=role)
            self.favorite_changed.emit()
            
            # Refresh tabel
            fav = get_favorit()
            fav_link = fav.get("Link_Lowongan") if fav else None
            saved_links = get_all_saved_links()
            show_fav = not getattr(self, 'is_admin', False)
            self.match_results.set_data(self.current_matches, self.user_selected_skills, show_favorite=show_fav, fav_link=fav_link, saved_links=saved_links)

    def _on_favorite_clicked(self, job_data):
        """Menangani klik tombol favorit."""
        # 1. Cek apakah sudah ada favorit sebelumnya
        existing_fav = get_favorit()
        if existing_fav:
            res = show_question(
                self, "Konfirmasi Favorit",
                "Pekerjaan sebelumnya yang ditandai favorit akan hilang dari dashboard, apakah kamu yakin?"
            )
            if res == QMessageBox.No:
                return

        # 2. Simpan ke database permanen (Otomatis)
        if self.last_scraped_file:
            path_saved = simpan_ke_database_permanen(job_data, self.last_scraped_file)
            job_data["source_file"] = path_saved if isinstance(path_saved, str) and path_saved != "DUPLICATE" else None

        # 3. Set sebagai favorit utama
        if set_favorit(job_data):
            show_message(self, "Berhasil", f"'{job_data.get('Judul_Pekerjaan')}' sekarang menjadi favorit utama Anda!")
            
            role = "admin" if getattr(self, 'is_admin', False) else "user"
            catat_aktivitas(f"<b>Pekerjaan Favorit Diganti</b><br>{job_data.get('Judul_Pekerjaan')}", role=role)
            self.favorite_changed.emit()

            # 4. Refresh tabel untuk mengubah warna tombol
            show_fav = not getattr(self, 'is_admin', False)
            saved_links = get_all_saved_links()
            self.match_results.set_data(
                self.current_matches, 
                self.user_selected_skills, 
                show_favorite=show_fav,
                fav_link=job_data.get("Link_Lowongan"),
                saved_links=saved_links
            )
        else:
            show_message(self, "Gagal", "Gagal menetapkan favorit.")

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
