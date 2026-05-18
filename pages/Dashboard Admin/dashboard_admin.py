import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QProgressBar, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal

from Modul.modul_antarmuka_pengguna import AktivitasTerkiniWidget, terapkan_soft_shadow, KeyboardScrollArea
from Modul.modul_pengolahan_data import (hitung_total_lowongan_aktif, 
                                        hitung_persentase_lowongan_per_kategori,
                                        hitung_tren_bidang_aktif,
                                        ambil_skill_tidak_terklasifikasi,
                                        hitung_total_user_terdaftar)
from Modul.modul_visualisasi_data import PieChartWidget

# --- REUSABLE COMPONENTS ---

class Card(QFrame):
    def __init__(self, parent=None, border_color="#E2E8F0"):
        super().__init__(parent)
        if border_color == "transparent":
            border_color = "#E2E8F0"
        self.setObjectName("AdminCard")
        self.setStyleSheet(f"""
            QFrame#AdminCard {{
                background-color: white;
                border-radius: 15px;
                border: 1px solid {border_color};
            }}
        """)
        
        # Tambahkan soft drop shadow modern lewat helper function central
        terapkan_soft_shadow(self)

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
    manage_skill_requested = pyqtSignal(str, str) # Dipancarkan ketika admin ingin mengelola skill tertentu (skill_name, category_name)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")
        self.baseline_counts = {}
        
        self.layout_halaman = QVBoxLayout(self)
        self.layout_halaman.setContentsMargins(0, 0, 0, 0)

        self.bg_container = QFrame()
        self.bg_container.setStyleSheet("background-color: transparent; border: none;")
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
        self.stat_skill = StatCard("SKILL TIDAK TERKLASIFIKASI", 78, "#E74C3C")
        self.stat_user = StatCard("USER TERDAFTAR", 0, "#9B59B6")
        
        stats_layout.addWidget(self.stat_job)
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
        
        # Tambahkan KeyboardScrollArea agar bisa scroll jika jumlah bidang banyak
        self.aktif_scroll = KeyboardScrollArea()
        self.aktif_scroll.setWidgetResizable(True)
        self.aktif_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.aktif_scroll_content = QWidget()
        self.aktif_scroll_content.setStyleSheet("background: transparent;")
        self.aktif_scroll_lay = QVBoxLayout(self.aktif_scroll_content)
        self.aktif_scroll_lay.setContentsMargins(0, 0, 0, 0)
        self.aktif_scroll_lay.setSpacing(0)
        
        self.aktif_scroll.setWidget(self.aktif_scroll_content)
        self.aktif_lay.addWidget(self.aktif_scroll)

        # 3. TERAKHIR: Masukkan card ke dalam layout utama bawah
        lower_layout.addWidget(self.aktif_card, 3)

        # C. DAFTAR SKILL TAK TERKLASIFIKASI
        self.skill_card = Card()
        self.skill_lay = QVBoxLayout(self.skill_card)
        self.skill_lay.setContentsMargins(25, 25, 25, 25)
        lbl_s = QLabel("DAFTAR SKILL TIDAK TERKLASIFIKASI")
        lbl_s.setWordWrap(True)
        lbl_s.setStyleSheet("font-weight: bold; color: #2C3E50; font-size: 16px; margin-bottom: 10px;")
        self.skill_lay.addWidget(lbl_s)
        
        # Placeholder stretch
        self.skill_lay.addStretch()
        lower_layout.addWidget(self.skill_card, 3)

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
            total_user = hitung_total_user_terdaftar()

            # 2. Update Label Angka
            self.stat_job.lbl_value.setText(str(total_lowongan))
            self.stat_user.lbl_value.setText(str(total_user))

            # 3. Refresh widget aktivitas admin
            self.aktivitas_widget.refresh()

            # 4. Update LOWONGAN PER BIDANG secara dinamis
            self.update_lowongan_per_bidang()

            # 5. Update BIDANG AKTIF secara dinamis dengan trend
            self.update_bidang_aktif()

            # 6. Update SKILL TIDAK TERKLASIFIKASI secara dinamis
            self.update_skill_tak_terklasifikasi()

            print(f"Admin Dashboard Updated: {total_lowongan} lowongan ditemukan.")
        except Exception as e:
            print(f"Gagal update dashboard admin: {e}")

    def update_skill_tak_terklasifikasi(self):
        """Mengisi daftar skill tak terklasifikasi secara dinamis"""
        # Hapus semua widget dinamis lama kecuali label judul
        self.clear_layout(self.skill_lay, keep=1)
        
        # Ambil data dinamis
        total_count, top_skills = ambil_skill_tidak_terklasifikasi(limit=4)
        
        # Update StatCard di atas
        self.stat_skill.lbl_value.setText(str(total_count))
        
        if not top_skills:
            lbl_empty = QLabel("Semua skill sudah\nterklasifikasi dengan baik! 🎉")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("color: #7F8C8D; font-size: 14px; margin-top: 20px;")
            self.skill_lay.addWidget(lbl_empty)
            self.skill_lay.addStretch()
            return
            
        for item in top_skills:
            skill_name = item["skill"]
            count = item["count"]
            
            skill_item = QHBoxLayout()
            
            # Label Nama Skill & Kemunculan
            lbl_name = QLabel(f"{skill_name} ({count}x)")
            lbl_name.setStyleSheet("font-size: 13px; color: #34495E; font-weight: 500;")
            skill_item.addWidget(lbl_name)
            
            # Tombol Kelola
            btn_manage = QPushButton("Kelola")
            btn_manage.setStyleSheet("""
                QPushButton {
                    background-color: #EBF5FB; 
                    color: #2980B9; 
                    border-radius: 8px; 
                    font-weight: bold; 
                    padding: 5px 12px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                    color: white;
                }
            """)
            btn_manage.setCursor(Qt.PointingHandCursor)
            
            # Gunakan lambda yang menangkap nilai secara statis
            btn_manage.clicked.connect(lambda checked, s=skill_name: self.handle_manage_skill(s))
            
            skill_item.addWidget(btn_manage)
            self.skill_lay.addLayout(skill_item)
            
        self.skill_lay.addStretch()

    def handle_manage_skill(self, skill_name):
        """Mencari bidang kategori skill lalu memancarkan sinyal ke router utama"""
        from Modul.modul_pengolahan_data import cari_kategori_untuk_skill
        cat_name = cari_kategori_untuk_skill(skill_name) or ""
        self.manage_skill_requested.emit(skill_name, cat_name)

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
            
            if not data_kategori:
                no_data_lbl = QLabel("Tidak ada lowongan aktif.")
                no_data_lbl.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 14px; margin-top: 10px;")
                self.bidang_lay.addWidget(no_data_lbl)
            else:
                # Tampilkan maksimal 5 kategori teratas untuk menjaga estetika layout agar tetap presisi
                top_kategori = dict(list(data_kategori.items())[:5])
                
                chart = PieChartWidget(size_ratio=0.8)
                chart.set_data(top_kategori)
                self.bidang_lay.addWidget(chart)
        except Exception as e:
            print(f"Error update_lowongan_per_bidang: {e}")

    def update_bidang_aktif(self):
        """Mengupdate card BIDANG AKTIF secara dinamis berdasarkan data ril dan baseline trend"""
        try:
            # Hapus data sebelumnya dari dalam layout scroll content
            self.clear_layout(self.aktif_scroll_lay, keep=0)
            
            # Ambil data statistik & trend yang sudah diproses di modul pengolahan data
            trend_data = hitung_tren_bidang_aktif(self.baseline_counts)
            
            if not trend_data:
                no_data_lbl = QLabel("Tidak ada bidang aktif.")
                no_data_lbl.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 14px; margin-top: 10px;")
                self.aktif_scroll_lay.addWidget(no_data_lbl)
            else:
                for item in trend_data: # Tampilkan seluruh bidang aktif dinamis tanpa batasan!
                    # Gambar baris kategori
                    row_widget = QWidget()
                    row = QHBoxLayout(row_widget)
                    row.setContentsMargins(0, 8, 0, 8) 
                    
                    lbl_name = QLabel(item["nama"])
                    lbl_name.setStyleSheet("font-size: 14px; color: #333;")
                    
                    lbl_val = QLabel(str(item["jumlah"]))
                    lbl_val.setFixedWidth(60)
                    lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    lbl_val.setStyleSheet("font-size: 14px; color: #333; font-weight: 500;")
                    
                    lbl_trend = QLabel(item["trend"])
                    lbl_trend.setFixedWidth(50)
                    lbl_trend.setAlignment(Qt.AlignCenter)
                    lbl_trend.setStyleSheet(f"color: {item['warna']}; font-weight: bold; font-size: 16px;")
                    
                    row.addWidget(lbl_name)
                    row.addStretch()
                    row.addWidget(lbl_val)
                    row.addWidget(lbl_trend)
                    self.aktif_scroll_lay.addWidget(row_widget)
            
            self.aktif_scroll_lay.addStretch()
        except Exception as e:
            print(f"Error update_bidang_aktif: {e}")