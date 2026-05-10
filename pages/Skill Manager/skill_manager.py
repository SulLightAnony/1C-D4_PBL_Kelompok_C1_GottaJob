# pages/Skill Manager/skill_manager.py
import os
import json
import glob
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QFrame, QHeaderView, 
    QComboBox, QLineEdit, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Tambahkan path modul
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from Modul.modul_kategorisasi import categorizer, HasilKlasifikasi, _get_dictionary_dir
from Modul.modul_database import get_database_permanen_dir

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
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C687B;")
        sub = QLabel("Kelola klasifikasi skill (Hard Skill, Soft Skill, Position) untuk meningkatkan akurasi matching.")
        sub.setStyleSheet("color: #64748B;")
        
        h_lay.addWidget(title)
        h_lay.addWidget(sub)
        layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.btn_scan = QPushButton("🔍 Scan")
        self.btn_scan.setFixedWidth(100)
        self.btn_scan.setStyleSheet("background-color: #2C687B; color: white; padding: 10px; font-weight: bold; border-radius: 6px;")
        self.btn_scan.clicked.connect(self.start_scan)
        
        self.combo_scan_cat = QComboBox()
        self.combo_scan_cat.setPlaceholderText("Pilih Kategori Archive")
        self.combo_scan_cat.setMinimumWidth(200)
        self.combo_scan_cat.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")
        self.load_scan_categories()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari skill...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")

        self.filter_conf = QComboBox()
        self.filter_conf.addItems(["Semua Confidence", "Hanya Low Confidence"])
        self.filter_conf.currentIndexChanged.connect(self.filter_table)
        self.filter_conf.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px;")

        toolbar.addWidget(self.btn_scan)
        toolbar.addWidget(self.combo_scan_cat)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Filter:"))
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.filter_conf)
        layout.addLayout(toolbar)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar { border: none; height: 6px; background: #E2E8F0; } QProgressBar::chunk { background: #2C687B; }")
        layout.addWidget(self.progress)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Skill", "Muncul", "Deteksi Awal", "Conf", "Kategori Baru", "Alias Ke"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: white; border-radius: 8px; border: 1px solid #E2E8F0; }")
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
        target_path = self.combo_scan_cat.currentData()
        if not target_path:
            target_path = self.db_dir

        self.btn_scan.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.worker = SkillScannerWorker(target_path)
        self.worker.progress_signal.connect(lambda cur, tot: self.progress.setValue(int(cur/tot * 100)))
        self.worker.finished_signal.connect(self.on_scan_finished)
        self.worker.start()

    def on_scan_finished(self, results):
        self.all_data = results
        self.btn_scan.setEnabled(True)
        self.progress.setVisible(False)
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
            self.table.setItem(i, 0, QTableWidgetItem(skill))
            
            # Count
            count_item = QTableWidgetItem(str(info["count"]))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, count_item)
            
            # Detected
            self.table.setItem(i, 2, QTableWidgetItem(info["class"].kategori))
            
            # Confidence
            conf = info["class"].confidence
            conf_item = QTableWidgetItem(conf.upper())
            if conf == "low": conf_item.setForeground(Qt.red)
            elif conf == "medium": conf_item.setForeground(Qt.blue)
            else: conf_item.setForeground(Qt.darkGreen)
            conf_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, conf_item)
            
            # New Category Dropdown
            combo = QComboBox()
            combo.addItems(["(Tetap)", "Hard Skill", "Soft Skill", "Position", "Hapus (Spam)"])
            self.table.setCellWidget(i, 4, combo)
            
            # Alias Input
            alias_edit = QLineEdit()
            alias_edit.setPlaceholderText("Contoh: python")
            self.table.setCellWidget(i, 5, alias_edit)

    def filter_table(self):
        if self.all_data:
            self.display_data(self.all_data)

    def save_to_dictionary(self):
        res = QMessageBox.question(self, "Konfirmasi", "Apakah Anda yakin ingin memperbarui kamus skill berdasarkan perubahan di tabel?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.No:
            return

        # Load current dictionary
        try:
            with open(os.path.join(self.dict_dir, "universal.json"), "r", encoding="utf-8") as f:
                univ = json.load(f)
            with open(os.path.join(self.dict_dir, "alias.json"), "r", encoding="utf-8") as f:
                alias = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membaca kamus: {e}")
            return

        count_changes = 0
        for i in range(self.table.rowCount()):
            skill_raw = self.table.item(i, 0).text()
            new_cat = self.table.cellWidget(i, 4).currentText()
            alias_target = self.table.cellWidget(i, 5).text().strip().lower()

            # 1. Alias
            if alias_target:
                alias["alias"][skill_raw.lower()] = alias_target
                count_changes += 1

            # 2. Category
            if new_cat != "(Tetap)":
                if new_cat == "Soft Skill":
                    if skill_raw.lower() not in univ["soft_skills"]:
                        univ["soft_skills"].append(skill_raw.lower())
                elif new_cat == "Position":
                    # Menambahkan pola regex sederhana
                    pattern = f"\\b{skill_raw.lower()}\\b"
                    if pattern not in univ["position_patterns"]:
                        univ["position_patterns"].append(pattern)
                count_changes += 1

        if count_changes > 0:
            try:
                with open(os.path.join(self.dict_dir, "universal.json"), "w", encoding="utf-8") as f:
                    json.dump(univ, f, ensure_ascii=False, indent=4)
                with open(os.path.join(self.dict_dir, "alias.json"), "w", encoding="utf-8") as f:
                    json.dump(alias, f, ensure_ascii=False, indent=4)
                
                QMessageBox.information(self, "Berhasil", f"Berhasil memperbarui {count_changes} entri di Kamus Skill.")
                # Reload global categorizer
                categorizer.__init__()
                self.start_scan() # Refresh table
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan perubahan: {e}")
        else:
            QMessageBox.information(self, "Info", "Tidak ada perubahan yang dideteksi.")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    win = SkillManagerPage()
    win.show()
    sys.exit(app.exec_())
