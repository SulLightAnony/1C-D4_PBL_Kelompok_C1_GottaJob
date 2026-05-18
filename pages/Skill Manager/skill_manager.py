# pages/Skill Manager/skill_manager.py
import os
import json
import glob
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QFrame, QHeaderView, 
    QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

# Tambahkan path modul
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from Modul.modul_kategorisasi import categorizer, HasilKlasifikasi, _get_dictionary_dir
from Modul.modul_database import get_database_permanen_dir
from Modul.modul_antarmuka_pengguna import ModernComboBox, show_message, show_question, MODERN_TABLE_STYLE, SkillTag

class SkillScannerWorker(QThread):
    finished_signal = pyqtSignal(dict)    # { skill_name: { 'count': int, 'class': HasilKlasifikasi } }

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir

    def run(self):
        # Scan hanya di folder yang dipilih (recursive=True tetap untuk jaga-jaga subfolder di dalamnya)
        all_json = glob.glob(os.path.join(self.target_dir, "**", "*.json"), recursive=True)
        total_files = len(all_json)
        
        skill_counts = {} # { skill_lower: { 'raw': str, 'count': int } }
        
        for i, fp in enumerate(all_json):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for job in data:
                    skills_raw = job.get("Skills", "")
                    if not skills_raw or skills_raw == "-":
                        continue
                    
                    # Glints skills separated by |
                    list_s = [s.strip() for s in skills_raw.split("|") if s.strip()]
                    for s in list_s:
                        s_lower = s.lower()
                        if s_lower not in skill_counts:
                            skill_counts[s_lower] = {"raw": s, "count": 0}
                        skill_counts[s_lower]["count"] += 1
            except:
                continue

        # Klasifikasikan hasil unik
        final_results = {}
        for s_lower, info in skill_counts.items():
            klasifikasi = categorizer._klasifikasi_satu(info["raw"])
            if klasifikasi:
                final_results[info["raw"]] = {
                    "count": info["count"],
                    "class": klasifikasi
                }
        
        self.finished_signal.emit(final_results)

class SkillManagerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db_dir = get_database_permanen_dir()
        self.dict_dir = _get_dictionary_dir()
        self.all_data = {}
        self.is_programmatic_change = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(15)

        # Header Card
        header = QFrame()
        header.setObjectName("PanelCard")
        header.setStyleSheet("#PanelCard { background-color: white; border-radius: 12px; border: 1px solid #E0E7EF; }")
        h_lay = QVBoxLayout(header)
        
        title = QLabel("Skill Dictionary Manager")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C687B; background-color: transparent;")
        sub = QLabel("Kelola klasifikasi skill (Hard Skill, Soft Skill, Position) untuk meningkatkan akurasi matching.")
        sub.setStyleSheet("color: #64748B; background-color: transparent;")
        
        h_lay.addWidget(title)
        h_lay.addWidget(sub)
        layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Icon Path
        # Dropdown Kategori Scan
        self.combo_scan_cat = ModernComboBox()
        self.combo_scan_cat.setPlaceholderText("Pilih Kategori Archive")
        self.combo_scan_cat.setMinimumWidth(200)
        self.load_scan_categories()
        
        # Otomatis scan saat kategori dipilih
        self.combo_scan_cat.currentIndexChanged.connect(self.start_scan)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari skill...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 16px; border: 2px solid #B2D2D9; border-radius: 8px; 
                font-size: 14px; color: #1E3A4A; background: #F7FBFC;
            }
            QLineEdit:focus { border: 2px solid #2C687B; background: white; }
        """)

        self.filter_conf = ModernComboBox()
        self.filter_conf.addItems(["Semua Confidence", "Hanya Low Confidence"])
        self.filter_conf.currentIndexChanged.connect(self.filter_table)

        toolbar.addWidget(self.combo_scan_cat)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Filter:"))
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.filter_conf)
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Skill", "Muncul", "Deteksi Awal", "Conf", "Kategori Baru", "Alias Ke"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(65) # Sedikit lebih rapat dibanding Job Table
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet(MODERN_TABLE_STYLE)
        layout.addWidget(self.table)

        # Footer
        footer = QHBoxLayout()
        self.btn_save = QPushButton("💾 Update Kamus Skill")
        self.btn_save.setStyleSheet("background-color: #059669; color: white; padding: 12px 30px; font-weight: bold; border-radius: 8px;")
        self.btn_save.clicked.connect(self.save_to_dictionary)
        footer.addStretch()
        footer.addWidget(self.btn_save)
        layout.addLayout(footer)

    def load_scan_categories(self):
        self.combo_scan_cat.clear()
        self.combo_scan_cat.addItem("-- Semua Bidang --", self.db_dir)
        
        if not os.path.exists(self.db_dir):
            return

        # Ambil folder kategori
        for entry in os.scandir(self.db_dir):
            if entry.is_dir():
                self.combo_scan_cat.addItem(entry.name, entry.path)

    def start_scan(self):
        # Mencegah scan ganda jika sudah ada yang berjalan
        if hasattr(self, 'worker') and self.worker.isRunning():
            return
            
        # Bersihkan input pencarian jika kategori berubah secara manual dari dropdown user,
        # agar tidak menyaring hasil bidang baru dengan teks pencarian bidang sebelumnya
        if not getattr(self, 'is_programmatic_change', False):
            self.search_input.clear()
            
        target_path = self.combo_scan_cat.currentData()
        self.last_scan_category = self.combo_scan_cat.currentText() # Simpan nama kategori
        
        if not target_path:
            target_path = self.db_dir

        self.worker = SkillScannerWorker(target_path)
        self.worker.finished_signal.connect(self.on_scan_finished)
        self.worker.start()

    def on_scan_finished(self, results):
        self.all_data = results
        self.display_data(results)

    def display_data(self, data):
        self.table.setRowCount(0)
        show_low_only = self.filter_conf.currentIndex() == 1
        search_text = self.search_input.text().lower()

        filtered = []
        for skill, info in data.items():
            if show_low_only and info["class"].confidence != "low":
                continue
            if search_text and search_text not in skill.lower():
                continue
            filtered.append((skill, info))

        # Sort by count
        filtered.sort(key=lambda x: x[1]["count"], reverse=True)

        self.table.setRowCount(len(filtered))
        for i, (skill, info) in enumerate(filtered):
            # Skill Name
            skill_item = QTableWidgetItem(skill)
            skill_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 0, skill_item)
            
            # Count
            count_item = QTableWidgetItem(str(info["count"]))
            count_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, count_item)
            
            # Detected (SkillTag)
            deteksi_raw = info["class"].kategori
            cat_map = {
                "hard_skill": "hard_skills",
                "soft_skill": "soft_skills",
                "position": "positions"
            }
            tag_cat = cat_map.get(deteksi_raw, deteksi_raw)
            
            tag_widget = QWidget()
            tag_widget.setStyleSheet("background: transparent;")
            tag_lay = QHBoxLayout(tag_widget)
            tag_lay.setContentsMargins(5, 5, 5, 5)
            tag_lay.setAlignment(Qt.AlignCenter)
            
            tag = SkillTag(deteksi_raw.replace("_", " "), tag_cat)
            tag_lay.addWidget(tag)
            self.table.setCellWidget(i, 2, tag_widget)
            
            # Confidence (SkillTag)
            conf_raw = info["class"].confidence
            conf_map = {
                "high": "matched",
                "medium": "benefit",
                "low": "missing"
            }
            conf_cat = conf_map.get(conf_raw, "#BDC3C7")
            
            conf_widget = QWidget()
            conf_widget.setStyleSheet("background: transparent;")
            conf_lay = QHBoxLayout(conf_widget)
            conf_lay.setContentsMargins(5, 5, 5, 5)
            conf_lay.setAlignment(Qt.AlignCenter)
            
            conf_tag = SkillTag(conf_raw.upper(), conf_cat)
            conf_lay.addWidget(conf_tag)
            self.table.setCellWidget(i, 3, conf_widget)
            
            # New Category Dropdown
            combo = ModernComboBox()
            combo.addItems(["(Tetap)", "Hard Skill", "Soft Skill", "Position", "Hapus (Spam)"])
            self.table.setCellWidget(i, 4, combo)
            
            # Alias Input
            alias_edit = QLineEdit()
            alias_edit.setPlaceholderText("Contoh: python")
            alias_edit.setStyleSheet("""
                QLineEdit {
                    padding: 4px 8px; border: 1px solid #B2D2D9; border-radius: 4px; 
                    font-size: 13px; color: #1E3A4A; background: #F7FBFC;
                }
                QLineEdit:focus { border: 1px solid #2C687B; background: white; }
            """)
            self.table.setCellWidget(i, 5, alias_edit)

        # Highlight dan gulir otomatis ke baris skill sasaran jika ada
        if hasattr(self, 'pending_highlight_skill') and self.pending_highlight_skill:
            target = self.pending_highlight_skill.lower()
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 0)
                if item and item.text().lower() == target:
                    self.table.setCurrentCell(r, 0)
                    self.table.scrollToItem(item)
                    break
            self.pending_highlight_skill = None

    def filter_table(self):
        if self.all_data:
            self.display_data(self.all_data)

    def save_to_dictionary(self):
        res = show_question(self, "Konfirmasi", "Apakah Anda yakin ingin memperbarui kamus skill berdasarkan perubahan di tabel?")
        if res == QMessageBox.No:
            return

        # Load current dictionary
        try:
            with open(os.path.join(self.dict_dir, "universal.json"), "r", encoding="utf-8") as f:
                univ = json.load(f)
            with open(os.path.join(self.dict_dir, "alias.json"), "r", encoding="utf-8") as f:
                alias = json.load(f)
        except Exception as e:
            show_message(self, "Error", f"Gagal membaca kamus: {e}")
            return

        count_changes = 0
        
        # Penampung data untuk file kategori (Hard Skill & Position)
        category_data = {"hard_skills": [], "positions": []}
        cat_file_path = None
        
        # Jika bukan "Semua Bidang", siapkan path file skills.json di folder kategori tersebut
        if hasattr(self, 'last_scan_category') and self.last_scan_category != "-- Semua Bidang --":
            cat_dir = os.path.join(self.dict_dir, self.last_scan_category)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir, exist_ok=True)
            cat_file_path = os.path.join(cat_dir, "skills.json")
            
            # Muat data kategori yang ada jika file sudah ada
            if os.path.exists(cat_file_path):
                try:
                    with open(cat_file_path, "r", encoding="utf-8") as f:
                        category_data = json.load(f)
                except: pass

        for i in range(self.table.rowCount()):
            skill_raw = self.table.item(i, 0).text()
            new_cat = self.table.cellWidget(i, 4).currentText()
            alias_target = self.table.cellWidget(i, 5).text().strip().lower()

            # 1. Alias (Global)
            if alias_target:
                alias["alias"][skill_raw.lower()] = alias_target
                count_changes += 1

            # 2. Category
            if new_cat != "(Tetap)":
                skill_low = skill_raw.lower()
                
                # --- BERSIHKAN DAHULU DARI KATEGORI LAIN UNTUK MENCEGAH DUPLIKAT ---
                # A. Dari Universal
                if skill_low in univ.get("soft_skills", []):
                    univ["soft_skills"].remove(skill_low)
                    count_changes += 1
                if skill_low in univ.get("hard_skills", []):
                    univ["hard_skills"].remove(skill_low)
                    count_changes += 1
                
                pattern = f"\\b{skill_low}\\b"
                if pattern in univ.get("position_patterns", []):
                    univ["position_patterns"].remove(pattern)
                    count_changes += 1
                
                # B. Dari Seluruh Category-Specific (skills.json di semua subfolder)
                for entry in os.scandir(self.dict_dir):
                    if entry.is_dir():
                        other_cat_file = os.path.join(entry.path, "skills.json")
                        if cat_file_path and other_cat_file == cat_file_path:
                            continue
                        if os.path.exists(other_cat_file):
                            try:
                                with open(other_cat_file, "r", encoding="utf-8") as f:
                                    other_data = json.load(f)
                                
                                other_modified = False
                                if skill_low in other_data.get("hard_skills", []):
                                    other_data["hard_skills"].remove(skill_low)
                                    other_modified = True
                                    count_changes += 1
                                if skill_low in other_data.get("positions", []):
                                    other_data["positions"].remove(skill_low)
                                    other_modified = True
                                    count_changes += 1
                                    
                                if other_modified:
                                    with open(other_cat_file, "w", encoding="utf-8") as f:
                                        json.dump(other_data, f, ensure_ascii=False, indent=4)
                            except:
                                pass
                                
                # C. Dari Category-Specific Target yang sedang aktif di memori
                if skill_low in category_data.get("hard_skills", []):
                    category_data["hard_skills"].remove(skill_low)
                    count_changes += 1
                if skill_low in category_data.get("positions", []):
                    category_data["positions"].remove(skill_low)
                    count_changes += 1

                # --- SEKARANG MASUKKAN KE KATEGORI YANG DIPILIH ---
                if new_cat == "Soft Skill":
                    if skill_low not in univ["soft_skills"]:
                        univ["soft_skills"].append(skill_low)
                        count_changes += 1
                elif new_cat == "Hard Skill":
                    if cat_file_path:
                        if skill_low not in category_data["hard_skills"]:
                            category_data["hard_skills"].append(skill_low)
                            count_changes += 1
                    else:
                        if "hard_skills" not in univ: univ["hard_skills"] = []
                        if skill_low not in univ["hard_skills"]:
                            univ["hard_skills"].append(skill_low)
                            count_changes += 1
                elif new_cat == "Position":
                    if cat_file_path:
                        if skill_low not in category_data["positions"]:
                            category_data["positions"].append(skill_low)
                            count_changes += 1
                    else:
                        pattern = f"\\b{skill_low}\\b"
                        if pattern not in univ["position_patterns"]:
                            univ["position_patterns"].append(pattern)
                            count_changes += 1

        if count_changes > 0:
            try:
                # Simpan Universal & Alias
                with open(os.path.join(self.dict_dir, "universal.json"), "w", encoding="utf-8") as f:
                    json.dump(univ, f, ensure_ascii=False, indent=4)
                with open(os.path.join(self.dict_dir, "alias.json"), "w", encoding="utf-8") as f:
                    json.dump(alias, f, ensure_ascii=False, indent=4)
                
                # Simpan Category-specific Skills
                if cat_file_path and (category_data["hard_skills"] or category_data["positions"]):
                    with open(cat_file_path, "w", encoding="utf-8") as f:
                        json.dump(category_data, f, ensure_ascii=False, indent=4)
                
                # Reload global categorizer agar modul kategorisasi sinkron dengan perubahan terbaru
                categorizer.__init__()
                
                # Sinkronisasikan perubahan kamus langsung ke seluruh file database
                self.sync_changes_to_database()
                
                show_message(self, "Berhasil", f"Kamus skill berhasil diperbarui! {count_changes} perubahan disimpan dan database permanen disinkronkan.")
                self.start_scan() # Refresh tabel agar warna berubah
            except Exception as e:
                show_message(self, "Error", f"Gagal menyimpan perubahan: {e}")
        else:
            show_message(self, "Info", "Tidak ada perubahan yang dideteksi.")

    def sync_changes_to_database(self):
        """
        Menyelaraskan perubahan kamus langsung ke sumber data di Database Permanen/Job Archive.
        Menggabungkan Opsi A (koreksi typo/alias) & Opsi B (re-kategorisasi fisik) ke seluruh berkas JSON.
        """
        db_dir = self.db_dir
        if not os.path.exists(db_dir):
            return
            
        file_paths = glob.glob(os.path.join(db_dir, "**", "*.json"), recursive=True)
        
        for fp in file_paths:
            try:
                modified = False
                with open(fp, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                    
                if not isinstance(jobs, list):
                    continue
                    
                for job in jobs:
                    raw_skills = job.get("Skills", "")
                    if not raw_skills or raw_skills == "-":
                        continue
                        
                    # Split dan bersihkan/normalisasikan skill (Opsi A - Alias & Typo)
                    skill_list = [s.strip() for s in raw_skills.split("|") if s.strip()]
                    cleaned_skills = []
                    has_alias_change = False
                    
                    for skill in skill_list:
                        normalized = categorizer._normalize(skill)
                        if normalized.lower() != skill.lower():
                            cleaned_skills.append(normalized.title())
                            has_alias_change = True
                        else:
                            cleaned_skills.append(skill)
                            
                    if has_alias_change:
                        job["Skills"] = " | ".join(cleaned_skills)
                        modified = True
                        
                    # Re-kategorisasi fisik berdasarkan aturan kamus baru (Opsi B)
                    new_all_categorized = categorizer.kategorikan(cleaned_skills)
                    
                    # Jika ada perubahan kategori, perbarui secara fisik
                    if job.get("all_categorized") != new_all_categorized:
                        job["all_categorized"] = new_all_categorized
                        modified = True
                        
                    # Jika ada matched_categorized, perbarui juga berdasarkan list skill-nya
                    if "matched_categorized" in job:
                        old_matched = job.get("matched_skills", [])
                        if not old_matched and "matched_categorized" in job:
                            mc = job["matched_categorized"]
                            old_matched = mc.get("hard_skills", []) + mc.get("soft_skills", []) + mc.get("positions", [])
                            
                        cleaned_matched = []
                        for ms in old_matched:
                            cleaned_matched.append(categorizer._normalize(ms).title())
                            
                        new_matched_categorized = categorizer.kategorikan(cleaned_matched)
                        if job["matched_categorized"] != new_matched_categorized:
                            job["matched_categorized"] = new_matched_categorized
                            job["matched_skills"] = cleaned_matched
                            modified = True
                            
                if modified:
                    with open(fp, "w", encoding="utf-8") as f:
                        json.dump(jobs, f, ensure_ascii=False, indent=4)
                        
            except Exception as e:
                print(f"Error syncing dictionary to {fp}: {e}")

    def set_search_filter(self, skill_name, category_name=None):
        """Pindah ke kategori bidang, aktifkan filter low confidence, dan highlight skill sasaran"""
        self.is_programmatic_change = True
        try:
            self.pending_highlight_skill = skill_name
            self.search_input.clear()
            self.filter_conf.setCurrentIndex(1) # Pilih "Hanya Low Confidence"
            
            if category_name:
                idx = self.combo_scan_cat.findText(category_name)
                if idx >= 0:
                    self.combo_scan_cat.setCurrentIndex(idx)
                else:
                    self.combo_scan_cat.setCurrentIndex(0) # Fallback ke Semua Bidang
            else:
                self.combo_scan_cat.setCurrentIndex(0)
                
            self.filter_table()
        finally:
            self.is_programmatic_change = False

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    win = SkillManagerPage()
    win.show()
    sys.exit(app.exec_())
