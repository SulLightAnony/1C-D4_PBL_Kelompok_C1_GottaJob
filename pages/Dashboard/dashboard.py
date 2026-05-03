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
        body_layout.addLayout(left_col, 2)

        # --- KOLOM KANAN (Insight & Aktivitas) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(20)

        self.insight_card = Card(border_color="transparent")
        self.ins_card_layout = QVBoxLayout(self.insight_card)
        self.ins_card_layout.setContentsMargins(20, 20, 20, 20)
        self.ins_card_layout.setSpacing(15)
        
        right_col.addWidget(self.insight_card)

        # Aktivitas Terkini
        self.act_card = Card(border_color="transparent")
        self.act_lay = QVBoxLayout(self.act_card)
        self.act_lay.setContentsMargins(25, 25, 25, 25)
        
        right_col.addWidget(self.act_card)

        body_layout.addLayout(right_col, 1)
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
        # Bersihkan layout lama
        self.clear_layout(self.dev_layout)
        self.clear_layout(self.trend_layout)
        self.clear_layout(self.ins_card_layout)
        self.clear_layout(self.act_lay)
        
        # 1. Populating Favorit
        header_fav = QLabel("Lowongan Favorit")
        header_fav.setStyleSheet("font-weight: bold; color: #888; font-size: 24px;")
        self.dev_layout.addWidget(header_fav)
        
        self.name_info = QLabel()
        self.salary = QLabel()
        self.salary.setStyleSheet("font-weight: bold; color: #333; font-size: 15px;")
        
        top_info = QHBoxLayout()
        top_info.addWidget(self.name_info)
        top_info.addStretch()
        top_info.addWidget(self.salary)
        self.dev_layout.addLayout(top_info)
        
        self.tags_layout = QHBoxLayout()
        self.dev_layout.addLayout(self.tags_layout)

        # Ambil favorit dari modul_database
        job_data = get_favorit()
        
        # Tentukan file arsip mana yang akan dibaca untuk tren
        # Prioritas: 1. source_file dari favorit, 2. File pertama di folder archive
        db_dir = get_database_permanen_dir()
        archive_json = None
        
        if job_data:
            archive_json = job_data.get("source_file")
            
            # Jika source_file tidak ada atau tidak valid, coba tebak dari judul/folder
            if not archive_json or not os.path.exists(archive_json):
                import glob
                all_archives = glob.glob(os.path.join(db_dir, "*.json"))
                if all_archives:
                    archive_json = all_archives[0]

            judul = job_data.get("Judul_Pekerjaan", "Lowongan")
            perusahaan = job_data.get("Nama_Perusahaan", "Perusahaan")
            jenis = job_data.get("Jenis_Pekerjaan", "-")
            gaji = job_data.get("Rentang_Gaji", "-")
            match_val = int(job_data.get("match_percentage", 0))

            self.name_info.setText(f"<b>{judul.upper()}</b><br><font color='#777'>{perusahaan} | {jenis}</font>")
            self.salary.setText(gaji)

            #logika filter skill
            matched_skills = job_data.get("matched_skills", [])
            self.clear_layout(self.tags_layout)

            for s in matched_skills:
                tag = QLabel(str(s).strip().title())
                tag.setStyleSheet("background-color: #1A1A1A; color: white; padding: 6px 15px; border-radius: 10px; font-size: 11px; font-weight: bold;")
                self.tags_layout.addWidget(tag)
            self.tags_layout.addStretch()

            match_btn_layout = QHBoxLayout()

            #progress bar
            self.progress_widget = SkillProgress("Kecocokan skill", match_val)
            match_btn_layout.addWidget(self.progress_widget, 4)

            #tombol lihat gap skill
            self.btn_gap = QPushButton("Lihat Gap Skill")
            self.btn_gap.setCursor(Qt.PointingHandCursor)
            self.btn_gap.setStyleSheet("""
                    QPushButton {
                        background-color: #52B788;
                        color: white;
                        border-radius: 8px;
                        padding: 8px 15px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #40916C; }
            """)
            self.btn_gap.clicked.connect(self.buka_gap_skill)
            match_btn_layout.addWidget(self.btn_gap, 1) # Stretch 1
            
            self.dev_layout.addSpacing(10)
            self.dev_layout.addLayout(match_btn_layout)


        else:
            self.name_info.setText("<b>Belum ada pekerjaan favorit</b><br><font color='#777'>Pilih dari Job Archive</font>")
            import glob
            all_archives = glob.glob(os.path.join(db_dir, "*.json"))
            if all_archives:
                archive_json = all_archives[0]

        # 2. Populating Tren Skill
        trend_title = QLabel("TREN SKILL MINGGU INI")
        trend_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        self.trend_layout.addWidget(trend_title)
        
        try:
            if archive_json and os.path.exists(archive_json):
                top_skills = ambil_top_skills(archive_json, limit=5)
                
                if top_skills:
                    for skill_name, persentase in top_skills:
                        self.trend_layout.addWidget(SkillProgress(skill_name, persentase))
                else:
                    self.trend_layout.addWidget(QLabel("Belum ada data skill di arsip terpilih."))
            else:
                self.trend_layout.addWidget(QLabel("Silakan cari pekerjaan di Live Discovery terlebih dahulu."))
        except Exception as e:
            print(f"Error Tren Skill: {e}")
            self.trend_layout.addWidget(QLabel("Gagal memuat tren skill."))

        # 3. Populating Insight Pasar
        ins_title = QLabel("INSIGHT PASAR")
        ins_title.setStyleSheet("font-weight: bold; color: #555; margin-top: 5px;")
        self.ins_card_layout.addWidget(ins_title)

        try:
            if archive_json and os.path.exists(archive_json):
                insight_data = ambil_insight_pasar(archive_json)
                
                if insight_data:
                    self.ins_card_layout.addWidget(InsightBox(insight_data["skill"], "#D8F3DC", "#52B788", "#1B4332"))
                    self.ins_card_layout.addWidget(InsightBox(insight_data["kontrak"], "#FFE5D9", "#FB8B24", "#5F0F40"))
                    self.ins_card_layout.addWidget(InsightBox(insight_data["gaji"], "#CAF0F8", "#00B4D8", "#03045E"))
                else:
                    self.ins_card_layout.addWidget(QLabel("Belum ada data untuk insight."))
            else:
                self.ins_card_layout.addWidget(QLabel("Insight akan muncul setelah Anda mencari pekerjaan."))
        except Exception as e:
            self.ins_card_layout.addWidget(QLabel(f"Gagal memuat insight: {e}"))

        # 4. Populating Aktivitas Terkini
        act_lbl = QLabel("AKTIVITAS TERKINI")
        act_lbl.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px; font-size:13px;")
        self.act_lay.addWidget(act_lbl)
        
        list_aktivitas = get_aktivitas()
        if list_aktivitas:
            for act in list_aktivitas:
                pesan_teks = act.get('pesan', "")

                # 1. Ambil teks murni (buang tag HTML)
                import re
                clean_text = re.sub('<[^<]+?>', ' ', pesan_teks) # ganti tag dengan spasi
                parts = [p.strip() for p in clean_text.split("  ") if p.strip()]
                
                header = parts[0] if len(parts) > 0 else "Aktivitas"
                body = parts[1] if len(parts) > 1 else ""

                # 2. Buat Widget Container
                item_container = QWidget()
                item_container.setStyleSheet("background: transparent;")
                v_lay = QVBoxLayout(item_container)
                v_lay.setContentsMargins(0, 0, 0, 10) # Jarak antar grup aktivitas
                v_lay.setSpacing(0) # Kita kontrol jarak manual lewat margin label

                # 3. Label Header (Pekerjaan Favorit)
                h_lbl = QLabel(header)
                h_lbl.setStyleSheet("""
                    font-weight: bold; 
                    color: #2D3436; 
                    font-size: 13px; 
                    margin-bottom: 2px; /* JARAK KE CONTENT */
                """)
                # Mencegah teks turun ke bawah/wrap yang bikin berantakan
                h_lbl.setWordWrap(False) 

                # 4. Label Content (Detail Pekerjaan)
                b_lbl = QLabel(body)
                b_lbl.setStyleSheet("""
                    color: #636E72; 
                    font-size: 12px;
                    padding-bottom: 5px; /* JARAK KE HEADER BERIKUTNYA */
                """)
                b_lbl.setWordWrap(False)

                v_lay.addWidget(h_lbl)
                if body:
                    v_lay.addWidget(b_lbl)
                    
                self.act_lay.addWidget(item_container)          
        else:
            self.act_lay.addWidget(QLabel("Belum ada aktivitas tercatat."))
        self.act_lay.addStretch()
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

