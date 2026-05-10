from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QGraphicsBlurEffect, 
                             QFrame, QProgressBar, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

#import file json 
import json
import os
import re

#import modul pengolahan data
from Modul.modul_pengolahan_data import hitung_persentase_skill, ambil_insight_pasar, ambil_top_skills, hitung_gap_skill, cari_archive_terdekat
from Modul.modul_kategorisasi import pisahkan_skill
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
            font-size: 16px;
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
        
        # Container untuk kolom kiri agar bisa dibatasi lebarnya
        left_col_widget = QWidget()
        left_col_widget.setLayout(left_col)
        left_col_widget.setMinimumWidth(600)
        left_col.setContentsMargins(0, 0, 0, 0)

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
        left_col.addStretch()
        body_layout.addWidget(left_col_widget, 3)

        # --- KOLOM KANAN (Insight & Aktivitas) ---
        right_col_widget = QWidget()
        right_col_layout = QVBoxLayout(right_col_widget)
        right_col_layout.setContentsMargins(0, 0, 0, 0)
        right_col_layout.setSpacing(20)

        # Set lebar minimum di sini (misal 350 atau 400 pixel)
        # Set lebar minimum dan maksimum di sini
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
        right_col_layout.addStretch()

        # Aktivitas Terkini
        body_layout.addWidget(right_col_widget, 2)
        body_outer_layout.addStretch()

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
            salary_text = gaji
            bonus = job_data.get("Bonus", "-")
            if bonus != "-" and bonus.lower() != "bonus":
                # Pembersihan instan untuk data lama agar tidak "+ Bonus: Bonus" dan ganti "month"
                bonus_clean = re.sub(r'^bonus\s*:?\s*', '', bonus, flags=re.IGNORECASE).strip()
                bonus_clean = bonus_clean.replace("/month", "/Bulan").replace("month", "Bulan")
                salary_text += f"<br><font color='#27AE60' size='3'>+ Bonus: {bonus_clean}</font>"
                
            salary = QLabel(salary_text)
            salary.setStyleSheet("font-weight: bold; color: #333; font-size: 16px;")
            salary.setAlignment(Qt.AlignRight | Qt.AlignTop)
            
            top_info.addWidget(name_info)
            top_info.addStretch()
            top_info.addWidget(salary)
            self.dev_layout.addLayout(top_info)

            # --- CARI FILE ARCHIVE TERDEKAT ---
            archive_json = cari_archive_terdekat(judul, folder_archive)
            
            # Debugging
            print(f"File Archive yang ditemukan: {archive_json}")

            # Render Matched Skills Tags
            # --- RENDER TAG SKILL (Dikelompokkan) ---
            # container utama
            owned_tags_container = QWidget()
            owned_tags_container.setStyleSheet("background: transparent; border: none;")
            owned_tags_layout = QVBoxLayout(owned_tags_container)
            owned_tags_layout.setContentsMargins(0, 5, 0, 5)
            owned_tags_layout.setSpacing(10)

            owned_cat = job_data.get("matched_categorized")
            if not owned_cat:
                owned_skills = job_data.get("matched_skills", [])
                owned_cat = pisahkan_skill(owned_skills)
            
            # Gabungkan semua untuk ditampilkan (atau bisa dipisah per baris jika mau)
            # Untuk dashboard, kita tampilkan dalam satu baris tapi teratur
            from modul_antarmuka_pengguna import SkillTag

            current_row_owned = QHBoxLayout()
            current_row_owned.setSpacing(8)
            line_width_owned = 0
            max_width_owned = 550

            for category in ["hard_skills", "soft_skills", "positions"]:
                for s in owned_cat.get(category, []):
                    tag = SkillTag(s, category, font_size=16)
                    tag_w = tag.fontMetrics().boundingRect(s).width() + 45
            
            # Cek jika baris sudah penuh
                    if line_width_owned + tag_w > max_width_owned:
                        current_row_owned.addStretch()
                        owned_tags_layout.addLayout(current_row_owned)
                        current_row_owned = QHBoxLayout()
                        current_row_owned.setSpacing(8)
                        line_width_owned = 0
                    
                    current_row_owned.addWidget(tag)
                    line_width_owned += tag_w

            # Tambahkan baris terakhir
            current_row_owned.addStretch()
            owned_tags_layout.addLayout(current_row_owned)
            
            # Masukkan ke layout utama kartu (dev_layout)
            self.dev_layout.addWidget(owned_tags_container)

            # Match Progress & Button
            match_btn_layout = QHBoxLayout()
            match_btn_layout.addWidget(SkillProgress("Kecocokan skill", match_val), 4)
            btn_gap = QPushButton("Lihat Gap Skill")
            btn_gap.setStyleSheet("""
                QPushButton {
                    background-color: #2C687B; 
                    color: white; 
                    border-radius: 8px; 
                    padding: 8px 15px; 
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e4653;
                }
            """)
            btn_gap.clicked.connect(self.toggle_gap_skill)
            match_btn_layout.addWidget(btn_gap, 1)
            self.dev_layout.addLayout(match_btn_layout)

            #buat container gap skill
            self.container_gap_skill = QFrame()
            self.container_gap_skill.setStyleSheet("""
                QFrame {
                    background-color: #FFF5F5; 
                    border-radius: 12px; 
                    margin-top: 10px;
                }
            """)
            self.container_gap_skill.hide()

            #layout dalam container
            layout_expand = QVBoxLayout(self.container_gap_skill)
            layout_expand.setContentsMargins(15, 15, 15, 15)
            layout_expand.setSpacing(10)

            # Header Label di dalam box expand
            label_judul_gap = QLabel("Skill yang Perlu Kamu Pelajari:")
            label_judul_gap.setStyleSheet("color: #C0392B; font-weight: bold; font-size: 15px; border: none; background: transparent;")
            layout_expand.addWidget(label_judul_gap)

            tags_widget = QWidget()
            tags_widget.setStyleSheet("background: transparent; border: none;")

            tags_flow_layout = QHBoxLayout(tags_widget)
            tags_flow_layout.setContentsMargins(0, 0, 0, 0)
            tags_flow_layout.setSpacing(8)

            gap_list = hitung_gap_skill(job_data) # Mengambil list skill yang belum dimiliki

            from modul_antarmuka_pengguna import SkillTag

            if gap_list:
                container_tags = QWidget()
                container_tags.setStyleSheet("background: transparent; border: none;")
                layout_tags = QVBoxLayout(container_tags)
                layout_tags.setContentsMargins(0, 0, 0, 0)
                layout_tags.setSpacing(10)

                current_row = QHBoxLayout()
                current_row.setSpacing(8)
                line_width = 0
                max_width = 450

                for s in gap_list:
                    tag = SkillTag(s, "missing", font_size=16)

                    tag.setStyleSheet("""
                        background-color: white; 
                        color: #C0392B; 
                        border: 1px solid #E6B0AA; 
                        border-radius: 15px; 
                        padding: 5px 12px;
                        font-weight: 600;
                    """)

                    # Hitung lebar tag secara otomatis
                    tag_width = tag.fontMetrics().boundingRect(s).width() + 40
                    
                    # Jika sudah mentok ke kanan, buat baris baru
                    if line_width + tag_width > max_width:
                        current_row.addStretch() # Geser ke kiri
                        layout_tags.addLayout(current_row)
                        current_row = QHBoxLayout()
                        current_row.setSpacing(8)
                        line_width = 0
                    
                    current_row.addWidget(tag)
                    line_width += tag_width
                
                # Tambahkan baris terakhir
                current_row.addStretch()
                layout_tags.addLayout(current_row)
                
                layout_expand.addWidget(container_tags)
            else:
                layout_expand.addWidget(QLabel("Semua skill sudah terpenuhi!"))

            self.dev_layout.addWidget(self.container_gap_skill)

        # 3. RENDER TREN SKILL MINGGU INI 
        trend_title = QLabel("TREN SKILL MINGGU INI")
        trend_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        self.trend_layout.addWidget(trend_title)

        top_skills = ambil_top_skills(archive_json, limit=5) if archive_json else []
        if top_skills:
            for skill_name, persentase in top_skills:
                self.trend_layout.addWidget(SkillProgress(skill_name, persentase))
        else:
            self.trend_layout.addWidget(QLabel("Data pendukung tidak ditemukan."))

        # 4. RENDER INSIGHT PASAR 
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

        logs = get_aktivitas()
        if logs:
            try:
                for log in logs[:4]:
                    pesan_teks = log.get("pesan", "")
                    parts = pesan_teks.split("\n")
                    header = parts[0] if len(parts) > 0 else "Aktivitas"
                    body = parts[1] if len(parts) > 1 else ""
                    
                    # Container Utama per Item
                    item_widget = QWidget()
                    item_widget.setStyleSheet("background: transparent; border: none;")
                    
                    item_layout = QVBoxLayout(item_widget)
                    item_layout.setContentsMargins(0, 5, 0, 12)
                    item_layout.setSpacing(3)

                    # Label Judul
                    header_label = QLabel(header)
                    header_label.setStyleSheet("""
                            font-weight: 700; 
                            color: #2D3436; 
                            font-size: 16px; 
                            background: transparent;
                    """)
                    header_label.setWordWrap(True)
                    
                    # Label Detail
                    detail_label = QLabel(body if body else pesan_teks)
                    detail_label.setStyleSheet("""
                            color: #636E72; 
                            font-size: 14px; 
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
        
        # 2. Ambil data skill dari JSON lewat Modul Pengolahan Data
        job_data = get_favorit()
        gap_list = hitung_gap_skill(job_data)

        # 3. Tampilkan Modal
        self.modal = ModalGapSkill(self, gap_list)
        self.modal.show()

    def toggle_gap_skill(self):
        if self.container_gap_skill:
            if self.container_gap_skill.isVisible():
                self.container_gap_skill.hide()
            else:
                self.container_gap_skill.show()
