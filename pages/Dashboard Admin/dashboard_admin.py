import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QProgressBar, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from Modul.modul_antarmuka_pengguna import AktivitasTerkiniWidget
from Modul.modul_pengolahan_data import hitung_total_lowongan_aktif, hitung_persentase_lowongan_per_kategori

# --- REUSABLE COMPONENTS ---

class Card(QFrame):
    def __init__(self, parent=None, border_color="transparent"):
        super().__init__(parent)
        self.setStyleSheet(f"""
            background-color: white;
            border-radius: 15px;
            border: 1px solid {border_color};
        """)

class StatCard(Card):
    def __init__(self, title, value, color="#2980B9"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #7F8C8D; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 48px; font-weight: bold; margin-top: 5px;")
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)

class SkillProgressAdmin(QWidget):
    def __init__(self, name, value, color="#3498DB"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        lbl = QLabel(name)
        lbl.setMinimumWidth(100)
        lbl.setStyleSheet("font-weight: 500; color: #333;")
        
        self.pbar = QProgressBar()
        self.pbar.setValue(value)
        self.pbar.setTextVisible(False)
        self.pbar.setFixedHeight(10)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{ background-color: #ECF0F1; border-radius: 5px; border: none; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}
        """)
        
        self.perc = QLabel(f"{value}%")
        self.perc.setStyleSheet("font-weight: bold; color: #333;")
        
        layout.addWidget(lbl)
        layout.addWidget(self.pbar)
        layout.addWidget(self.perc)

# --- MAIN ADMIN PAGE ---

class AdminDashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F8F9FA;")
        
        self.layout_halaman = QVBoxLayout(self)
        self.layout_halaman.setContentsMargins(0, 0, 0, 0)

        self.bg_container = QFrame()
        self.bg_container.setStyleSheet("background-color: #EBF5FB; border: none;")
        self.layout_halaman.addWidget(self.bg_container)

        self.main_layout = QVBoxLayout(self.bg_container)
        
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # 1. HEADER
        header = QLabel("Dashboard")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        self.main_layout.addWidget(header)

        # 2. STATISTIC CARDS 
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.stat_job = StatCard("LOWONGAN AKTIF", 0, "#27AE60")
        self.stat_company = StatCard("PERUSAHAAN TERDAFTAR", 124, "#2980B9")
        self.stat_skill = StatCard("SKILL TIDAK TERKLASIFIKASI", 78, "#E74C3C")
        self.stat_user = StatCard("USER TERDAFTAR", 450, "#9B59B6")
        
        stats_layout.addWidget(self.stat_job)
        stats_layout.addWidget(self.stat_company)
        stats_layout.addWidget(self.stat_skill)
        stats_layout.addWidget(self.stat_user)
        
        self.main_layout.addLayout(stats_layout)

        # 3. LOWER CONTENT
        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(20)

        # A. LOWONGAN PER BIDANG
        bidang_card = Card()
        self.bidang_lay = QVBoxLayout(bidang_card)
        self.bidang_lay.setContentsMargins(25, 25, 25, 25)
        
        lbl_b = QLabel("LOWONGAN PER BIDANG")
        lbl_b.setStyleSheet("font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        self.bidang_lay.addWidget(lbl_b)
        
        
        lower_layout.addWidget(bidang_card, 4)

        # --- B. BIDANG AKTIF ---
        self.aktif_card = Card()
        self.aktif_lay = QVBoxLayout(self.aktif_card)
        self.aktif_lay.setContentsMargins(25, 25, 25, 25)
        
        lbl_title = QLabel("BIDANG AKTIF")
        lbl_title.setStyleSheet("font-weight: bold; color: #2C3E50; font-size: 16px; margin-bottom: 10px;")
        self.aktif_lay.addWidget(lbl_title)

        # 1. Fungsi untuk menambah baris (Definisikan dulu)
        def add_aktif_row(name, val, trend, trend_color):
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 8, 0, 8) 
            
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-size: 14px; color: #333;")
            
            lbl_val = QLabel(str(val))
            lbl_val.setFixedWidth(60)
            lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl_val.setStyleSheet("font-size: 14px; color: #333; font-weight: 500;")
            
            lbl_trend = QLabel(trend)
            lbl_trend.setFixedWidth(50)
            lbl_trend.setAlignment(Qt.AlignCenter)
            lbl_trend.setStyleSheet(f"color: {trend_color}; font-weight: bold; font-size: 16px;")
            
            row.addWidget(lbl_name)
            row.addStretch()
            row.addWidget(lbl_val)
            row.addWidget(lbl_trend)
            self.aktif_lay.addWidget(row_widget)

        # 2. Masukkan Data baris demi baris
        add_aktif_row("Teknologi", 120, "↓", "#E74C3C")
        add_aktif_row("Keuangan", 56, "↑", "#27AE60")
        add_aktif_row("Kesehatan", 100, "-", "#95A5A6")
        
        self.aktif_lay.addStretch()

        # 3. TERAKHIR: Masukkan card ke dalam layout utama bawah
        lower_layout.addWidget(self.aktif_card, 3)

        # C. DAFTAR SKILL TAK TERKLASIFIKASI
        skill_card = Card()
        skill_lay = QVBoxLayout(skill_card)
        skill_lay.setContentsMargins(25, 25, 25, 25)
        lbl_s = QLabel("DAFTAR SKILL TIDAK TERKLASIFIKASI")
        lbl_s.setWordWrap(True)
        lbl_s.setStyleSheet("font-weight: bold; color: #2C3E50;")
        skill_lay.addWidget(lbl_s)
        
        skill_item = QHBoxLayout()
        skill_item.addWidget(QLabel("Leadership"))
        btn_acc = QPushButton("Accept")
        btn_acc.setStyleSheet("background-color: #AED6F1; color: #21618C; border-radius: 10px; font-weight: bold; padding: 4px 10px;")
        skill_item.addWidget(btn_acc)
        skill_lay.addLayout(skill_item)
        skill_lay.addStretch()
        lower_layout.addWidget(skill_card, 3)

        self.main_layout.addLayout(lower_layout)

        # 4. AKTIVITAS TERKINI ADMIN
        self.aktivitas_widget = AktivitasTerkiniWidget(role="admin")
        self.main_layout.addWidget(self.aktivitas_widget)

        # PANGGIL LOAD DATA PERTAMA KALI
        self.load_data()

    def load_data(self):
        """Logika utama untuk refresh data Admin"""
        try:
            # 1. Hitung total lowongan dari seluruh kategori di Database Permanen/Job Archive
            total_lowongan = hitung_total_lowongan_aktif()

            # 2. Update Label Angka
            self.stat_job.lbl_value.setText(str(total_lowongan))

            # 3. Refresh widget aktivitas admin
            self.aktivitas_widget.refresh()

            # 4. Update LOWONGAN PER BIDANG secara dinamis
            self.update_lowongan_per_bidang()

            print(f"Admin Dashboard Updated: {total_lowongan} lowongan ditemukan.")
        except Exception as e:
            print(f"Gagal update dashboard admin: {e}")

    def clear_layout(self, layout, keep=1):
        """Menghapus semua widget di dalam layout kecuali beberapa widget awal"""
        if layout is not None:
            while layout.count() > keep:
                item = layout.takeAt(keep)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout(), keep=0)

    def update_lowongan_per_bidang(self):
        """Mengupdate card LOWONGAN PER BIDANG secara dinamis berdasarkan data ril"""
        try:
            # Hapus data sebelumnya (tetapkan judul index 0 tetap ada)
            self.clear_layout(self.bidang_lay, keep=1)
            
            # Ambil data per kategori dari pengolahan data
            data_kategori = hitung_persentase_lowongan_per_kategori()
            
            # Daftar warna premium untuk progress bar
            colors = ["#3498DB", "#2ECC71", "#E67E22", "#9B59B6", "#F1C40F", "#E74C3C", "#1ABC9C", "#34495E"]
            
            if not data_kategori:
                no_data_lbl = QLabel("Tidak ada lowongan aktif.")
                no_data_lbl.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 14px; margin-top: 10px;")
                self.bidang_lay.addWidget(no_data_lbl)
            else:
                # Tampilkan maksimal 5 kategori teratas untuk menjaga estetika layout agar tetap presisi
                for i, (kat, info) in enumerate(list(data_kategori.items())[:5]):
                    color = colors[i % len(colors)]
                    percentage = info["persentase"]
                    jumlah = info["jumlah"]
                    
                    # Tambahkan baris skill progress admin
                    display_name = f"{kat} ({jumlah})"
                    self.bidang_lay.addWidget(SkillProgressAdmin(display_name, percentage, color))
            
            self.bidang_lay.addStretch()
        except Exception as e:
            print(f"Error update_lowongan_per_bidang: {e}")