# pages/Skill Manager/skill_manager.py
import os
import json
import glob
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QFrame, QHeaderView, 
    QLineEdit, QMessageBox, QProgressBar
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
    progress_signal = pyqtSignal(int, int) # current, total
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
            self.progress_signal.emit(i + 1, total_files)

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
        self.combo_scan_cat.addItem("-- Semua Kategori --", self.db_dir)
        
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
        
        # Jika bukan "Semua Kategori", siapkan path file skills.json di folder kategori tersebut
        if hasattr(self, 'last_scan_category') and self.last_scan_category != "-- Semua Kategori --":
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
                        # Fallback ke universal jika scan semua kategori
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
                
                show_message(self, "Berhasil", f"Kamus skill berhasil diperbarui! {count_changes} perubahan disimpan.")
                # Reload global categorizer agar Confidence jadi HIGH
                categorizer.__init__()
                self.start_scan() # Refresh tabel agar warna berubah
            except Exception as e:
                show_message(self, "Error", f"Gagal menyimpan perubahan: {e}")
        else:
            show_message(self, "Info", "Tidak ada perubahan yang dideteksi.")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    win = SkillManagerPage()
    win.show()
    sys.exit(app.exec_())
