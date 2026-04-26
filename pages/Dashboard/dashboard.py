from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
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
            font-size: 13px;
            font-weight: 500;
        """)

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
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #E2E4E4;")
        self.main_layout.addWidget(content_area)

        body_outer_layout = QVBoxLayout(content_area)
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

            # Tags Skills
            skill_list = job_data.get("Skills", "").split(" | ")
            for s in skill_list:
                tag = QLabel(s.strip())
                tag.setStyleSheet("background-color: #1A1A1A; color: white; padding: 6px 15px; border-radius: 10px; font-size: 11px; font-weight: bold;")
                tags_layout.addWidget(tag)
            tags_layout.addStretch()

            dev_layout.addSpacing(20)
            dev_layout.addWidget(SkillProgress("Kecocokan skill", match_val))
        
        left_col.addWidget(dev_card)

        # 2. TREN SKILL MINGGU INI
        trend_card = Card(border_color="transparent")
        trend_layout = QVBoxLayout(trend_card)
        trend_layout.setContentsMargins(25, 25, 25, 25)
        trend_title = QLabel("TREN SKILL MINGGU INI")
        trend_title.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        trend_layout.addWidget(trend_title)
        
        skills = [("Flutter", 60), ("Swift", 60), ("iOS Development", 60), ("Kotlin", 40), ("React Native", 100)]
        for skill, val in skills:
            trend_layout.addWidget(SkillProgress(skill, val))
        
        left_col.addWidget(trend_card)
        body_layout.addLayout(left_col, 2)

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
        ins_card_layout.addWidget(ins_title)

        #ambil data
        archive_json = os.path.join(current_dir, "..", "..", "database", "Database Permanen", "Job Archive", "game_developer.json")

        #default teks gagal
        teks_skill = "Belum ada tren skill yang terdeteksi."
        teks_kontrak = "Data status pekerjaan belum tersedia."
        teks_gaji = "Informasi gaji belum tersedia."

        try:
            with open(archive_json, 'r', encoding='utf-8') as f:
                all_jobs = json.load(f)
            if all_jobs:
                hasil_stats = hitung_persentase_skill(archive_json)
                if hasil_stats:
                    persentase_top = list(hasil_stats.keys()) [0]
                    skill_top = " & ".join(hasil_stats[persentase_top][:2])
                    teks_insight = f"{skill_top} mendominasi {persentase_top}% lowongan — fokus di sini untuk ROI terbesar."

                status_list = [j.get("Jenis_Pekerjaan", "Full-time") for j in all_jobs]
                from collections import Counter
                most_common_status = Counter(status_list).most_common(1)[0][0]
                teks_kontrak = f"Mayoritas posisi berstatus {most_common_status} — cocok untuk bangun portofolio awal."

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
                    teks_gaji = f"Gaji rata-rata sekitar Rp {avg_gaji/1_000_000:.1f} jt/bulan berdasarkan data pasar saat ini."
                
                ins_card_layout.addWidget(InsightBox(teks_insight, "#D8F3DC", "#52B788", "#1B4332"))
                ins_card_layout.addWidget(InsightBox(teks_kontrak, "#FFE5D9", "#FB8B24", "#5F0F40"))
                ins_card_layout.addWidget(InsightBox(teks_gaji, "#CAF0F8", "#00B4D8", "#03045E"))
        except Exception as e:
            ins_card_layout.addWidget(QLabel(f"Gagal memuat insight: {e}"))

        right_col.addWidget(insight_card)

        # Aktivitas Terkini
        act_card = Card(border_color="transparent")
        act_lay = QVBoxLayout(act_card)
        act_lay.setContentsMargins(25, 25, 25, 25)
        act_lbl = QLabel("AKTIVITAS TERKINI")
        act_lbl.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 10px;")
        act_lay.addWidget(act_lbl)
        act_lay.addWidget(QLabel("• <b>Live Discovery Selesai</b><br>ios developer · 12 hasil"))
        act_lay.addWidget(QLabel("• <b>Lowongan disimpan</b><br>PT Sigma Global Teknologi"))
        act_lay.addWidget(QLabel("• <b>Live Discovery Selesai</b><br>mobile developer · 5 hasil"))
        right_col.addWidget(act_card)

        body_layout.addLayout(right_col, 1)
        body_outer_layout.addStretch()