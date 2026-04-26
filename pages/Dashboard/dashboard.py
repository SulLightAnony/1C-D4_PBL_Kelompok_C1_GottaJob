from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class StatCard(QFrame):
    """Komponen statistik card"""
    def __init__(self, title, value, subtitle, color="#2C687B"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #E5E7EB;
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #374151; font-size: 14px; font-weight: bold;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #6B7280; font-size: 12px;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_sub)

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # --- BARIS 1: HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: black;")
        
        update_info = QLabel("Update Terakhir: Today, 10:45 AM")
        update_info.setStyleSheet("color: #4B5563; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(update_info, alignment=Qt.AlignBottom)
        main_layout.addLayout(header_layout)

        # --- BARIS 2: STAT CARDS ---
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(StatCard("Active Job Monitoring", "50", "Lowongan terbuka", "#10B981"))
        stats_layout.addWidget(StatCard("Database Metrics", "12", "Perusahaan", "#2563EB"))
        stats_layout.addWidget(StatCard("Applied Ratio", "35%", "Progres Lamaran", "#EF4444"))
        stats_layout.addWidget(StatCard("Total Archive", "50", "Lowongan tersimpan", "#6B7280"))
        main_layout.addLayout(stats_layout)

        # --- BARIS 3: CHART & ACTIVITY ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Bagian Kiri: Placeholder Chart
        # (Nanti bisa pakai Matplotlib atau cukup QFrame dengan gambar dulu)
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet("background-color: white; border-radius: 20px;")
        # Dummy content untuk Chart
        chart_dummy = QLabel("Pie Chart Area\n(Gunakan Matplotlib)")
        chart_dummy.setAlignment(Qt.AlignCenter)
        chart_vbox = QVBoxLayout(self.chart_frame)
        chart_vbox.addWidget(chart_dummy)
        
        # Bagian Kanan: Recent Activity
        self.activity_frame = QFrame()
        self.activity_frame.setStyleSheet("background-color: #E5E7EB; border-radius: 20px; padding: 20px;")
        self.activity_frame.setFixedWidth(400)
        
        activity_layout = QVBoxLayout(self.activity_frame)
        act_title = QLabel("Recent Activity")
        act_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        activity_layout.addWidget(act_title)
        
        # Contoh list activity
        for _ in range(5):
            item = QLabel("• • •  Scraped 5 jobs from Indeed")
            item.setStyleSheet("font-size: 16px; margin: 5px 0;")
            activity_layout.addWidget(item)
        activity_layout.addStretch()

        bottom_layout.addWidget(self.chart_frame, stretch=2)
        bottom_layout.addWidget(self.activity_frame, stretch=1)
        
        main_layout.addLayout(bottom_layout)