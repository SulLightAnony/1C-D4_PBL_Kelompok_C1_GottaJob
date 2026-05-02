from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QGraphicsBlurEffect, 
                             QFrame, QProgressBar, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

#import file json 
import json
import os

#import modul pengolahan data
from Modul.modul_pengolahan_data import hitung_persentase_skill, ambil_insight_pasar, ambil_top_skills
from Modul.modul_database import get_database_permanen_dir, get_favorit, get_aktivitas

class Card(QFrame):
    def __init__(self, parent=None, border_color="#AAD9B7"):
        super().__init__(parent)
        self.setObjectName("CustomCard") 
        self.setStyleSheet(f"""
            #CustomCard {{
                background-color: white;
                border-radius: 20px;
                border: 5px solid {border_color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

class SkillProgress(QWidget):
    def __init__(self, name, value, color="#52B788"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        lbl = QLabel(name)
        lbl.setMinimumWidth(115) 
        lbl.setStyleSheet("font-weight: 500; color: #333; border: none;")
        
        pbar = QProgressBar()
        pbar.setValue(value)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(8)
        pbar.setStyleSheet(f"""
            QProgressBar {{ background-color: #000000; border-radius: 4px; border: none; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}
        """)
        
        perc = QLabel(f"{value}%")
        perc.setFixedWidth(55)
        perc.setStyleSheet(f"color: {color}; font-weight: bold; border: none;")
        
        layout.addWidget(lbl)
        layout.addWidget(pbar)
        layout.addWidget(perc)

class InsightBox(QLabel):
    def __init__(self, text, bg, border, txt_color):
        super().__init__(text)
        self.setWordWrap(True)
        self.setContentsMargins(15, 12, 15, 12)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMinimumHeight(60)

        self.setStyleSheet(f"""
            background-color: {bg};
            color: {txt_color};
            border-left: 5px solid {border};
            border-top: none; border-right: none; border-bottom: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 500;
            line-height:1.2;
        """)

class ModalGapSkill(QFrame):
    def __init__(self, parent, gap_skills):
        super().__init__(parent)
        # Overlay gelap transparan menutupi seluruh dashboard
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.4); border: none;")
        
        # Kontainer Modal (Kotak Putih di Tengah)
        self.modal_content = Card(self, border_color="#2C687B")
        self.modal_content.setFixedSize(500, 400)
        
        # Posisikan ke tengah
        self.posisi_tengah()

        layout = QVBoxLayout(self.modal_content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Judul Modal
        title = QLabel("Gap Skill Terdeteksi")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2C687B;")
        layout.addWidget(title)

        desc = QLabel("Berikut adalah skill yang perlu kamu pelajari untuk meningkatkan kecocokan:")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; font-size: 20px;")
        layout.addWidget(desc)

        # Scroll Area untuk Skill yang Belum Dikuasai
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignTop)

        if gap_skills:
            for skill in gap_skills:
                item = QLabel(f"• {skill}")
                item.setStyleSheet("font-size: 18px; color: #333; padding: 5px;")
                container_layout.addWidget(item)
        else:
            container_layout.addWidget(QLabel("Selamat! Semua skill sudah kamu kuasai."))

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Tombol Exit / Kembali
        btn_exit = QPushButton("Kembali ke Dashboard")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #2C687B; color: white;
                border-radius: 10px; padding: 12px;
                font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #3d8ba5; }
        """)
        btn_exit.clicked.connect(self.tutup_modal)
        layout.addWidget(btn_exit)

    def posisi_tengah(self):
        qr = self.modal_content.frameGeometry()
        cp = self.parent().rect().center()
        qr.moveCenter(cp)
        self.modal_content.move(qr.topLeft())

    def tutup_modal(self):
        # Hapus efek blur pada dashboard
        self.parent().content_area.setGraphicsEffect(None)
        self.deleteLater()


def load_favorite_job(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Gagal membaca file JSON: {e}")
        return None
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- HEADER AREA ---
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 30, 40, 10)
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2D2D2D; border: none;")
        header_layout.addWidget(title)
        self.main_layout.addWidget(header_widget)

        # --- CONTENT AREA ---
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #E2E4E4;")
        self.main_layout.addWidget(self.content_area)

        body_outer_layout = QVBoxLayout(self.content_area)
        body_outer_layout.setContentsMargins(40, 20, 40, 40)
        
        body_layout = QHBoxLayout()
        body_layout.setSpacing(25)
        body_outer_layout.addLayout(body_layout)

        # --- KOLOM KIRI ---
        left_col = QVBoxLayout()
        left_col.setSpacing(20)

        # 1. KARTU LOWONGAN FAVORIT
        self.dev_card = Card(border_color="#AAD9B7")
        self.dev_layout = QVBoxLayout(self.dev_card)
        self.dev_layout.setContentsMargins(25, 25, 25, 25)
        
        left_col.addWidget(self.dev_card)

        # 2. TREN SKILL MINGGU INI
        self.trend_card = Card(border_color="transparent")
        self.trend_layout = QVBoxLayout(self.trend_card)
        self.trend_layout.setContentsMargins(25, 25, 25, 25)
        
        left_col.addWidget(self.trend_card)
        body_layout.addLayout(left_col, 3)

        # --- KOLOM KANAN (Insight & Aktivitas) ---
        right_col_widget = QWidget()
        right_col_layout = QVBoxLayout(right_col_widget)
        right_col_layout.setContentsMargins(0, 0, 0, 0)
        right_col_layout.setSpacing(20)

        # Set lebar minimum di sini (misal 350 atau 400 pixel)
        right_col_widget.setMinimumWidth(380)

        self.insight_card = Card(border_color="transparent")
        self.ins_card_layout = QVBoxLayout(self.insight_card)
        self.ins_card_layout.setContentsMargins(20, 20, 20, 20)
        self.ins_card_layout.setSpacing(15)
        
        self.act_card = Card(border_color="transparent")
        self.act_lay = QVBoxLayout(self.act_card)
        self.act_lay.setContentsMargins(25, 25, 25, 25)
        
        right_col_layout.addWidget(self.insight_card)
        right_col_layout.addWidget(self.act_card)

        # Aktivitas Terkini
        

        body_layout.addWidget(right_col_widget, 2)

        # Load data pertama kali
        self.load_data()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def load_data(self):
        # 1. Pembersihan Layout
        self.clear_layout(self.dev_layout)
        self.clear_layout(self.trend_layout)
        self.clear_layout(self.ins_card_layout)
        self.clear_layout(self.act_lay)

        # 2. Penentuan Path Dasar
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_json_favorit = os.path.normpath(os.path.join(current_dir, "..", "..", "database", "Database Permanen", "Favorit", "favorit.json"))
        folder_archive = os.path.normpath(os.path.join(current_dir, "..", "..", "database", "Database Permanen", "Job Archive"))
        
        job_data = load_favorite_job(path_json_favorit)
        archive_json = None 

        if job_data:
            # --- RENDER KARTU LOWONGAN FAVORIT ---
            judul = job_data.get("Judul_Pekerjaan", "Lowongan")
            perusahaan = job_data.get("Nama_Perusahaan", "Perusahaan")
            jenis = job_data.get("Jenis_Pekerjaan", "-")
            gaji = job_data.get("Rentang_Gaji", "-")
            match_val = int(job_data.get("match_percentage", 0))

            header_fav = QLabel("Lowongan Favorit")
            header_fav.setStyleSheet("font-weight: bold; color: #888; font-size: 24px;")
            self.dev_layout.addWidget(header_fav)

            top_info = QHBoxLayout()
            name_info = QLabel(f"<b>{judul.upper()}</b><br><font color='#777'>{perusahaan} | {jenis}</font>")
            salary = QLabel(gaji)
            salary.setStyleSheet("font-weight: bold; color: #333; font-size: 15px;")
            top_info.addWidget(name_info)
            top_info.addStretch()
            top_info.addWidget(salary)
            self.dev_layout.addLayout(top_info)

            # --- LOGIKA FUZZY SEARCH UNTUK MENCARI FILE ARCHIVE ---
            import glob
            if os.path.exists(folder_archive):
                semua_file = glob.glob(os.path.join(folder_archive, "*.json"))
                # Ambil keywords dari judul (minimal 3 karakter agar tidak ambigu)
                keywords = [k.lower() for k in judul.split() if len(k) > 2]
                
                for file_path in semua_file:
                    nama_file_kecil = os.path.basename(file_path).lower()
                    # Jika ada keyword yang cocok di nama file, pilih file ini
                    if any(key in nama_file_kecil for key in keywords):
                        archive_json = file_path
                        break
            
            # Debugging (Opsional: Hapus jika sudah jalan)
            print(f"File Archive yang ditemukan: {archive_json}")

            # Render Matched Skills Tags
            tags_layout = QHBoxLayout()
            owned_skills = job_data.get("matched_skills", [])
            for s in owned_skills:
                tag = QLabel(str(s).strip().title())
                tag.setStyleSheet("background-color: #1A1A1A; color: white; padding: 6px 15px; border-radius: 10px; font-size: 13px; font-weight: bold;")
                tags_layout.addWidget(tag)
            tags_layout.addStretch()
            self.dev_layout.addLayout(tags_layout)

            # Match Progress & Button
            match_btn_layout = QHBoxLayout()
            match_btn_layout.addWidget(SkillProgress("Kecocokan skill", match_val), 4)
            btn_gap = QPushButton("Lihat Gap Skill")
            btn_gap.setStyleSheet("background-color: #52B788; color: white; border-radius: 8px; padding: 8px 15px; font-weight: bold;")
            btn_gap.clicked.connect(self.buka_gap_skill)
            match_btn_layout.addWidget(btn_gap, 1)
            self.dev_layout.addLayout(match_btn_layout)

        # 3. RENDER TREN SKILL MINGGU INI (Gunakan modul kamu)
        trend_title = QLabel("TREN SKILL MINGGU INI")
        trend_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        self.trend_layout.addWidget(trend_title)

        top_skills = ambil_top_skills(archive_json, limit=5) if archive_json else []
        if top_skills:
            for skill_name, persentase in top_skills:
                self.trend_layout.addWidget(SkillProgress(skill_name, persentase))
        else:
            self.trend_layout.addWidget(QLabel("Data pendukung tidak ditemukan."))

        # 4. RENDER INSIGHT PASAR (Gunakan modul kamu)
        ins_title = QLabel("INSIGHT PASAR")
        ins_title.setStyleSheet("font-weight: bold; color: #555; margin-top: 5px;")
        self.ins_card_layout.addWidget(ins_title)

        insight_data = ambil_insight_pasar(archive_json) if archive_json else None
        if insight_data:
            self.ins_card_layout.addWidget(InsightBox(insight_data.get("skill", "-"), "#D8F3DC", "#52B788", "#1B4332"))
            self.ins_card_layout.addWidget(InsightBox(insight_data.get("kontrak", "-"), "#FFE5D9", "#FB8B24", "#5F0F40"))
            self.ins_card_layout.addWidget(InsightBox(insight_data.get("gaji", "-"), "#CAF0F8", "#00B4D8", "#03045E"))
        else:
            self.ins_card_layout.addWidget(QLabel("Pilih lowongan untuk melihat insight."))

        # 5. RENDER AKTIVITAS TERKINI (Clean & Modern UI)
        act_lbl = QLabel("AKTIVITAS TERKINI")
        act_lbl.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 15px; font-size: 13px; letter-spacing: 1px;")
        self.act_lay.addWidget(act_lbl)

        path_log = os.path.normpath(os.path.join(current_dir, "..", "..", "database", "Database Permanen", "aktivitas.json"))
        
        if os.path.exists(path_log):
            try:
                with open(path_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                if isinstance(logs, list) and logs:
                    for log in logs[::-1][:4]:
                        pesan_teks = log.get("pesan", "")
                        parts = pesan_teks.split("\n")
                        header = parts[0] if len(parts) > 0 else "Aktivitas"
                        body = parts[1] if len(parts) > 1 else ""
                        
                        # Container Utama per Item
                        item_widget = QWidget()
                        # Hilangkan background abu-abu dengan setStyleSheet transparan
                        item_widget.setStyleSheet("background: transparent; border: none;")
                        
                        item_layout = QVBoxLayout(item_widget)
                        item_layout.setContentsMargins(0, 5, 0, 12) # Jarak atas-bawah diperlebar
                        item_layout.setSpacing(3) # Jarak antara judul dan detail

                        # Label Judul (Hitam Pekat, Sedikit Bold)
                        header_label = QLabel(header)
                        header_label.setStyleSheet("""
                            font-weight: 700; 
                            color: #2D3436; 
                            font-size: 13px; 
                            background: transparent;
                        """)
                        header_label.setWordWrap(True)
                        
                        # Label Detail (Abu-abu, Lebih Kecil)
                        detail_label = QLabel(body if body else pesan_teks)
                        detail_label.setStyleSheet("""
                            color: #636E72; 
                            font-size: 12px; 
                            background: transparent;
                            margin-top: 2px;
                        """)
                        detail_label.setWordWrap(True)

                        if not body:
                            item_layout.addWidget(header_label)
                        else:
                            item_layout.addWidget(header_label)
                            item_layout.addWidget(detail_label)

                        self.act_lay.addWidget(item_widget)
            except Exception as e:
                self.act_lay.addWidget(QLabel("Gagal memuat riwayat."))
        else:
            self.act_lay.addWidget(QLabel("Belum ada aktivitas."))

    #gap_skill
    def buka_gap_skill(self):
        # 1. Tambahkan Efek Blur pada area konten
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)
        self.content_area.setGraphicsEffect(self.blur_effect)
        
        # 2. Ambil data skill dari JSON (Logika Gap Skill)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_json = os.path.join(current_dir, "..", "..", "database", "Database Permanen", "Favorit", "favorit.json")
        job_data = get_favorit()
        
        gap_list = []
        if job_data:
            #ambil semua skill yang ada di lowongan favorit
            semua_skill = [s.strip().lower() for s in job_data.get("Skills", "").split("|") if s.strip()]

            #ambil matched skill
            skill_dimiliki = [s.strip().lower() for s in job_data.get("matched_skills", [])]

            #filter : agar yang masuk tidak ada di skill_dimiliki
            gap_list = [s.title() for s in semua_skill if s not in skill_dimiliki]

        # 3. Tampilkan Modal
        self.modal = ModalGapSkill(self, gap_list)
        self.modal.show()

