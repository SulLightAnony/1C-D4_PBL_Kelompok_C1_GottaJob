from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QGraphicsBlurEffect, 
                             QFrame, QProgressBar, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

#import file json 
import json
import os

file_path = "../../database/Database Permanen/Favorit/favorit.json"

def load_favorite_job(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Gagal membaca file JSON: {e}")
        return None

#import modul pengolahan data
from Modul.modul_pengolahan_data import hitung_persentase_skill

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
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {txt_color};
            border-left: 5px solid {border};
            border-top: none; border-right: none; border-bottom: none;
            border-radius: 10px;
            font-size: 17px;
            font-weight: 500;
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
        desc.setStyleSheet("color: #666; font-size: 14px;")
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
                item.setStyleSheet("font-size: 16px; color: #333; padding: 5px;")
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

        # 1. KARTU LOWONGAN FAVORIT (Buat objeknya dulu)
        dev_card = Card(border_color="#AAD9B7")
        dev_layout = QVBoxLayout(dev_card)
        dev_layout.setContentsMargins(25, 25, 25, 25)

        header_fav = QLabel("Lowongan Favorit")
        header_fav.setStyleSheet("font-weight: bold; color: #888; font-size: 24px;")
        dev_layout.addWidget(header_fav)

        top_info = QHBoxLayout()
        name_info = QLabel() # Kosongkan dulu
        salary = QLabel() # Kosongkan dulu
        salary.setStyleSheet("font-weight: bold; color: #333; font-size: 15px;")
        top_info.addWidget(name_info)
        top_info.addStretch()
        top_info.addWidget(salary)
        dev_layout.addLayout(top_info)

        tags_layout = QHBoxLayout() # Layout untuk tags hitam
        dev_layout.addLayout(tags_layout)
        
        # LOGIKA PENGISIAN DATA DARI JSON
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_json = os.path.join(current_dir, "..", "..", "database", "Database Permanen", "Favorit", "favorit.json")
        
        job_data = load_favorite_job(path_json)
        
        if job_data:
            judul = job_data.get("Judul_Pekerjaan", "Lowongan")
            perusahaan = job_data.get("Nama_Perusahaan", "Perusahaan")
            jenis = job_data.get("Jenis_Pekerjaan", "-")
            gaji = job_data.get("Rentang_Gaji", "-")
            match_val = int(job_data.get("match_percentage", 0))

            name_info.setText(f"<b>{judul.upper()}</b><br><font color='#777'>{perusahaan} | {jenis}</font>")
            salary.setText(gaji)


            skill_list = job_data.get("Skills", "").split(" | ")
            for s in skill_list:
                tag = QLabel(s.strip())
                tag.setStyleSheet("background-color: #1A1A1A; color: white; padding: 6px 15px; border-radius: 10px; font-size: 11px; font-weight: bold;")
                self.tags_layout.addWidget(tag)
            self.tags_layout.addStretch()

            self.dev_layout.addSpacing(20)
            self.dev_layout.addWidget(SkillProgress("Kecocokan skill", match_val))
        else:
            self.name_info.setText("<b>Belum ada pekerjaan favorit</b><br><font color='#777'>Pilih dari Job Archive</font>")
            import glob
            all_archives = glob.glob(os.path.join(db_dir, "*.json"))
            if all_archives:
                archive_json = all_archives[0]

            #scroll area untuk tag skill
            scroll_tags = QScrollArea()
            scroll_tags.setWidgetResizable(True)
            scroll_tags.setFixedHeight(50) 
            scroll_tags.setFrameShape(QFrame.NoFrame)
            scroll_tags.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Scroll halus tanpa bar kaku
            scroll_tags.setStyleSheet("background: transparent;")

            container_tags = QWidget()
            container_tags.setStyleSheet("background: transparent;")
            tags_h = QHBoxLayout(container_tags)
            tags_h.setContentsMargins(0, 0, 0, 0)

            # Tags Skills
            owned_skills = job_data.get("matched_skills", [])

            if not owned_skills:
                owned_skills = job_data.get("Skills", "").split(" | ")
            
            for s in owned_skills:
                skill_text = s.strip().title()
                if skill_text:
                    tag = QLabel(skill_text)
                    tag.setStyleSheet("""
                        background-color: #1A1A1A; 
                        color: white; 
                        padding: 6px 15px; 
                        border-radius: 10px; 
                        font-size: 11px; 
                        font-weight: bold;
                    """)
                    tags_layout.addWidget(tag)
            tags_layout.addStretch()

            dev_layout.addSpacing(20)
            
            #layout untuk nampung bar dan button
            match_btn_layout = QHBoxLayout()
            match_btn_layout.setSpacing(15)

            match_btn_layout.addWidget(SkillProgress("Kecocokan skill", match_val), 4)

            #button lihat gap skill
            btn_gap = QPushButton("Lihat Gap Skill")
            btn_gap.setCursor(Qt.PointingHandCursor)
            btn_gap.setStyleSheet("""
                QPushButton {
                    background-color: #D1D5DB; 
                    color: #374151;
                    border-radius: 8px; 
                    padding: 8px 15px;
                    font-weight: bold; 
                    font-size: 12px; 
                    border: 1px solid #9CA3AF;
                }
                QPushButton:hover { background-color: #BEC3CC; }
            """)

            btn_gap.clicked.connect(self.buka_gap_skill)

            match_btn_layout.addWidget(btn_gap, 1)

            dev_layout.addLayout(match_btn_layout)
        
        left_col.addWidget(dev_card)


        # 2. TREN SKILL MINGGU INI
        trend_card = Card(border_color="transparent")
        trend_layout = QVBoxLayout(trend_card)
        trend_layout.setContentsMargins(25, 25, 25, 25)
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

        trend_layout.addWidget(trend_title)

        #pembersihan data lama
        while trend_layout.count() > 1:
            item = trend_layout.takeAt(1)
            if item.widget():
                item.widget.deleteLater()
        
        try:
            #logika scanning folder archive
            job_title = job_data.get("Judul_Pekerjaan", "").lower().replace(" ", "_")
            file_target = f"{job_title}.json"
            folder_archive = os.path.join(current_dir,"..","..","database", "Database Permanen", "Job Archive", file_target)
            # List semua file json di folder Job Archive
            if os.path.exists(folder_archive):
                hasil_stats = hitung_persentase_skill(folder_archive)

                if isinstance(hasil_stats, dict) and hasil_stats:
                    count = 0
                    for persentase in sorted(hasil_stats.keys(), reverse=True, key=float):
                        for skill_name in hasil_stats[persentase]:
                            if count < 5:
                                trend_layout.addWidget(SkillProgress(skill_name, int(float(persentase))))
                                count += 1
                else:
                    trend_layout.addWidget(QLabel("Belum ada statistik untuk kategori ini."))

            else:
                trend_layout.addWidget(QLabel(f"File {file_target} belum tersedia di Archive."))

        except Exception as e:
            print(f"Error Tren Skill: {e}")
            trend_layout.addWidget(QLabel("Gagal memuat tren skill."))
        left_col.addWidget(trend_card)
        body_layout.addLayout(left_col,2)

        # --- KOLOM KANAN (Insight & Aktivitas) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(20)

        insight_card = Card(border_color="transparent") # Gunakan transparent agar senada dengan Tren Skill
        ins_card_layout = QVBoxLayout(insight_card)
        ins_card_layout.setContentsMargins(20, 20, 20, 20)
        ins_card_layout.setSpacing(15)
        
        # Insight Pasar
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

        ins_card_layout.addWidget(ins_title)

        #bersihkan data sebelumnya
        while ins_card_layout.count() > 1:
            item = ins_card_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        try:
            job_title = job_data.get("Judul_Pekerjaan", "").lower().replace(" ", "_")
            file_target = f"{job_title}.json"
            archive_json = os.path.join(current_dir,"..","..","database", "Database Permanen", "Job Archive", file_target)

            # Default teks jika data tidak lengkap
            teks_insight = "Belum ada tren skill yang terdeteksi."
            teks_kontrak = "Data status pekerjaan belum tersedia."
            teks_gaji = "Informasi gaji belum tersedia."
            
            if os.path.exists(archive_json):
                with open(archive_json, 'r', encoding='utf-8') as f:
                    all_jobs = json.load(f)

                if all_jobs:
                    hasil_stats = hitung_persentase_skill(archive_json)
                    if hasil_stats:
                        persentase_top = list(hasil_stats.keys()) [0]
                        skill_top = " & ".join(hasil_stats[persentase_top][:2])
                        teks_insight = f"fokus kuasai {skill_top}."

                    status_list = [j.get("Jenis_Pekerjaan", "Full-time") for j in all_jobs]
                    from collections import Counter
                    most_common_status = Counter(status_list).most_common(1)[0][0]
                    teks_kontrak = f"Didominasi posisi {most_common_status}."

                    import re
                    gaji_list = []
                    for j in all_jobs:
                        gaji_str = j.get("Rentang_Gaji", "")
                        angka = re.findall(r'\d+', gaji_str.replace('.', ''))
                        if angka:
                            # Ambil rata-rata dari batas bawah dan atas jika ada
                            rata_rata_job = sum(map(int, angka)) / len(angka)
                            gaji_list.append(rata_rata_job)
                    
                    if gaji_list:
                        avg_gaji = sum(gaji_list) / len(gaji_list)
                        teks_gaji = f"Gaji rata-rata sekitar Rp {avg_gaji/1_000_000:.1f} jt/bulan"
                    
                    ins_card_layout.addWidget(InsightBox(teks_insight, "#D8F3DC", "#52B788", "#1B4332"))
                    ins_card_layout.addWidget(InsightBox(teks_kontrak, "#FFE5D9", "#FB8B24", "#5F0F40"))
                    ins_card_layout.addWidget(InsightBox(teks_gaji, "#CAF0F8", "#00B4D8", "#03045E"))
            else:
                ins_card_layout.addWidget(QLabel(f"File {file_target} belum ada di archive."))

        except Exception as e:
            ins_card_layout.addWidget(QLabel(f"Gagal memuat insight: {e}"))

        right_col.addWidget(insight_card)

        # Aktivitas Terkini
        act_card = Card(border_color="transparent")
        act_lay = QVBoxLayout(act_card)
        act_lay.setContentsMargins(25, 25, 25, 25)
        act_lbl = QLabel("AKTIVITAS TERKINI")
        act_lbl.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        self.act_lay.addWidget(act_lbl)
        
        list_aktivitas = get_aktivitas()
        if list_aktivitas:
            for act in list_aktivitas:
                msg_lbl = QLabel(f"• {act.get('pesan')}")
                msg_lbl.setWordWrap(True)
                msg_lbl.setStyleSheet("font-size: 13px; color: #333; margin-bottom: 5px;")
                self.act_lay.addWidget(msg_lbl)
        else:
            self.act_lay.addWidget(QLabel("Belum ada aktivitas tercatat."))



        body_layout.addLayout(right_col, 1)
        body_outer_layout.addStretch()

        #gap_skill
    def buka_gap_skill(self):
        # 1. Tambahkan Efek Blur pada area konten
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)
        self.content_area.setGraphicsEffect(self.blur_effect)

        # 2. Ambil data skill dari JSON (Logika Gap Skill)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_json = os.path.join(current_dir, "..", "..", "database", "Database Permanen", "Favorit", "favorit.json")
        job_data = load_favorite_job(path_json)
        
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

